'''
Module for importing ETSA databases.
'''
from MySQLdb.cursors import SSCursor, DictCursor
import MySQLdb
import ast
import logging

from hsm.data.document import Document
from hsm.data.documentstorage import DocumentStorage
from hsm.data.importer.util import compute_starts, compute_ends
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
from hsm.data.segment import Segment
from hsm.data.segmentstorage import SegmentStorage


logging.basicConfig()

class OldEtsaImporter(object):
    '''Importer that uses `anamnesis_nlp` table to retrieve everything necessary.
    This is the oldest variant of the importer.'''
    logger = logging.getLogger('etsaimporter')
    logger.setLevel(logging.DEBUG)
    
    def __init__(self, **kwargs):
        '''Initialize a new importer.
        Arguments:
        host - the mysql server host.
        port - mysql port of the server port.
        user - the username to log into database.
        passwd - the password to log into databse.
        db - the database name to select.
        table_name - the table analogous to `anamnesis_nlp`.
        name_prefix - the name to prefix the documents with, such as 'etsastat:'
        documentstorage - instance of the document storage to save the documents to.
        segmentstorage - instance of the segment storage to save the segments to.
        '''
        self._table_name = kwargs['table_name']
        self._name_prefix = kwargs['name_prefix']
        self._documentstorage = kwargs['documentstorage']
        self._segmentstorage = kwargs['segmentstorage']
        
        assert isinstance(self._table_name, unicode)
        assert isinstance(self._name_prefix, unicode)
        assert len(self._name_prefix) > 0
        assert issubclass(type(self._documentstorage), DocumentStorage)
        assert issubclass(type(self._segmentstorage), SegmentStorage)
        
        self.logger.info('Initializing MySQL connection to {0}:{1}'.format(kwargs['host'], kwargs['port']))
        self._conn = MySQLdb.connect(host=kwargs['host'],
                                     port=kwargs['port'],
                                     user=kwargs['user'],
                                     passwd=kwargs['passwd'],
                                     db=kwargs['db'])
        self.logger.info('MySQL connection initiated.')

    def __del__(self):
        if self._conn is not None:
            self._conn.close()

    def _get_query(self, limit):
        query = 'select epiId, anamnesis_mrf from ' + self._table_name
        if limit is not None:
            query += ' limit ' + str(int(limit))
        return query
    
    def _process_single(self, result):
        epiId, mrf = result
        extractor = EtsaDocumentExtractor(self._name_prefix + u':' + unicode(epiId), mrf)
        extractor.process(self._documentstorage, self._segmentstorage)

    def _pre_import_data_hook(self):
        pass

    def import_data(self, limit=None):
        '''Import etsa database to given document and segment storage.
        Keyword arguments:
        limit - if not None, then import only `limit` number of first documents.
        '''
        self.logger.info('Importing ETSA data. Limit is ' + str(limit))
        
        self._pre_import_data_hook()
        
        cur = SSCursor(self._conn)
        cur.execute(self._get_query(limit))
        
        result = cur.fetchone()
        numprocessed = 0
        while result is not None:
            self._process_single(result)
            numprocessed += 1
            if limit is not None and numprocessed >= limit:
                break
            result = cur.fetchone()
            # TODO: add multithreading
        self.logger.info('Processed {0} documents!'.format(numprocessed))


class EtsaImporter(OldEtsaImporter):
    '''Importer for ambulatory data, which has few variations compared to stationary.
       This is current standard importer.'''
    
    def __init__(self, *args, **kwargs):
        OldEtsaImporter.__init__(self, *args, **kwargs)
    
    def _get_query(self, limit):
        query = 'select epiId, anamnesis, anamsum, diagnosis, dcase from ' + self._table_name
        if limit is not None:
            query += ' limit ' + str(int(limit))
        return query
        
    def _process_field(self, name, mrf):
        extractor = EtsaDocumentExtractor(name, mrf)
        extractor.process(self._documentstorage, self._segmentstorage)
    
    def _process_single(self, result):
        epiId, anamnesis, anamsum, diagnosis, dcase = result
        if anamnesis is not None:
            self._process_field(self._name_prefix + u':anamnesis:' + unicode(epiId), anamnesis)
        if anamsum is not None:
            self._process_field(self._name_prefix + u':anamsum:' + unicode(epiId), anamsum)
        if diagnosis is not None:
            self._process_field(self._name_prefix + u':diagnosis:' + unicode(epiId), diagnosis)
        if dcase is not None:
            self._process_field(self._name_prefix + u':dcase:' + unicode(epiId), dcase)


class EtsaVisitImporter(OldEtsaImporter):
    '''This is current standard importer for etsa data that is splitted into visits.'''
    
    def __init__(self, *args, **kwargs):
        OldEtsaImporter.__init__(self, *args, **kwargs)
        
    def _get_query(self, limit):
        query = 'select id, epiId, patId, epiType, fieldName, date, json from ' + self._table_name
        if limit is not None:
            query += ' limit ' + str(int(limit))
        return query
    
    def _pre_import_data_hook(self):
        self.logger.info('Retrieving procedures metadata')
        cursor = DictCursor(self._conn)
        cursor.execute('select epiId, unifiedDisplayName from work.procedure_entries;')
        self._procedures_data = cursor.fetchall()
        self.logger.info('Retrieving procedures metadata done.')
    
    def _process_single(self, result):
        rowId, epiId, patId, epiType, fieldName, date, json = result
        extractor = EtsaDocumentExtractor(self._name_prefix + u':' + fieldName + u':' + unicode(rowId), json)
        meta = {'id': rowId,
                'epiId': epiId,
                'patId': patId,
                'epiType': epiType,
                'fieldName': fieldName}
        # handle date
        if date is not None:
            meta['date'] = u'{0}-{1}-{2}'.format(date.day, date.month, date.year)
        # handle procedures metadata
        if fieldName == 'procedures_text':
            procmeta = self._procedures_data[0]
            if procmeta['epiId'] != epiId:
                raise Exception('EpiIds do not match for event {0} and next procedure metadata with epiId {1}'.format(epiId, procmeta['epiId']))
            meta['procedure'] = procmeta['unifiedDisplayName']
            self._procedures_data = self._procedures_data[1:]
        extractor.process(self._documentstorage, self._segmentstorage, meta)
        

class EtsaDocumentExtractor(object):
    '''Class that encapsulates functionality for extracting everything from a single
    ETSA document.'''
    
    def __init__(self, docName, mrf):
        '''Initialize a new document extractor with given `docName` and morphological information.'''
        self._docname = docName
        self._mrf = mrf
        self._token_sentences = None
        self._word_sentences = None
        self._words = None
        self._word_starts = None
        self._word_ends = None
        self._plain_sentences = None
        self._document = None
    
    def process(self, documentstorage, segmentstorage, metadata=None):
        self._create_token_sentences()
        self._create_word_sentences()
        self._create_plain_sentences()
        
        self._create_document(metadata)
        documentstorage.save(self._document)
        self._create_sentence_segments(segmentstorage)
        #self._create_word_segments(segmentstorage)
        #self._create_morph_segments(segmentstorage, 'lemma')
        #self._create_morph_segments(segmentstorage, 'pos')

    def _create_token_sentences(self):
        '''Parses the encoded data from ETSA base into tokens for further processing.'''
        self._token_sentences = ast.literal_eval(self._mrf)
        self._fix_ne_tokens()
    
    def _fix_ne_tokens(self):
        '''Visits data contains annotated named entities, which are reprsented as empty strings.
           This method maps them to various placeholders as our segments require length.'''
        for sentence in self._token_sentences:
            for word in sentence:
                if 'ne' in word:
                    word['sone'] = u'<<' + unicode(word['ne'].upper()) + u'>>'
        
    def _create_word_sentences(self):
        '''Parse the words from tokens.'''
        self._word_sentences = [[token['sone'].decode('unicode_escape', 'replace') for token in sentence] for sentence in self._token_sentences]
        self._words = reduce(lambda x, y: x + y, self._word_sentences)
        self._word_starts = compute_starts(self._words, u' ')
        self._word_ends = compute_ends(self._words, u' ')
    
    def _create_plain_sentences(self):
        '''Create plain text sentences.'''
        self._plain_sentences = [u' '.join(sentence) for sentence in self._word_sentences]
    
    def _create_document(self, metadata):
        '''Create a plain text document.'''
        self._document = Document(self._docname, u' '.join(self._plain_sentences))
        self._document.metadata = metadata
    
    def _create_sentence_segments(self, segmentstorage):
        '''Create segments that denote the sentences in the document and store them.'''
        starts = compute_starts(self._plain_sentences)
        ends = compute_ends(self._plain_sentences)
        segments = []
        for sentence, start, end in zip(self._plain_sentences, starts, ends):
            segments.append(Segment(u'sentence', sentence, self._document, start, end))
        segmentstorage.save(segments)

    def _create_word_segments(self, segmentstorage):
        segments = []
        for word, start, end in zip(self._words, self._word_starts, self._word_ends):
            segments.append(Segment(u'word', word, self._document, start, end))
        segmentstorage.save(segments)
    
    def _create_morph_segments(self, segmentstorage, morph_key):
        all_values = []
        for sentence in self._token_sentences:
            for token in sentence:
                all_values.append([analyze[morph_key].decode('unicode_escape', 'replace') for analyze in token.get('analyysid', [])])
        segments = []
        for values, start, end in zip(all_values, self._word_starts, self._word_ends):
            for value in values:
                segments.append(Segment(unicode(morph_key), value, self._document, start, end))
        segmentstorage.save(segments)

