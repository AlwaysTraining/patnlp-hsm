'''
Module for importing ETSA databases.
'''
import MySQLdb
import ast
import logging

from textlab.data.document import Document
from textlab.data.documentstorage import DocumentStorage
from textlab.data.mongodocumentstorage import MongoDocumentStorage
from textlab.data.mongosegmentstorage import MongoSegmentStorage
from textlab.data.segment import Segment
from textlab.data.segmentstorage import SegmentStorage


logging.basicConfig()

class EtsaImporter(object):
    '''Importer that uses `anamnesis_nlp` table to retrieve everything necessary.'''
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

    def import_data(self):
        '''Import etsa database to given document and segment storage.'''
        self.logger.info('Importing ETSA data.')
        cur = self._conn.cursor()
        cur.execute('select epiId, anamnesis_mrf from ' + self._table_name)
        
        result = cur.fetchone()
        numprocessed = 0
        while result is not None:
            epiId, mrf = result
            extractor = EtsaDocumentExtractor(self._name_prefix + u':' + unicode(epiId), mrf)
            extractor.process(self._documentstorage, self._segmentstorage)
            numprocessed += 1
            result = cur.fetchone()
            # TODO: add multithreading
        self.logger.info('Processed {0} documents!'.format(numprocessed))

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
    
    def process(self, documentstorage, segmentstorage):
        self._create_token_sentences()
        self._create_word_sentences()
        self._create_plain_sentences()
        
        self._create_document()
        documentstorage.save(self._document)
        self._create_sentence_segments(segmentstorage)
        self._create_word_segments(segmentstorage)
        self._create_morph_segments(segmentstorage, 'lemma')
        self._create_morph_segments(segmentstorage, 'pos')

    def _create_token_sentences(self):
        '''Parses the encoded data from ETSA base into tokens for further processing.'''
        self._token_sentences = ast.literal_eval(self._mrf)
        
    def _create_word_sentences(self):
        '''Parse the words from tokens.'''
        self._word_sentences = [[token['sone'].decode('unicode_escape') for token in sentence] for sentence in self._token_sentences]
        self._words = reduce(lambda x, y: x + y, self._word_sentences)
        self._word_starts = compute_starts(self._words, u' ')
        self._word_ends = compute_ends(self._words, u' ')
    
    def _create_plain_sentences(self):
        '''Create plain text sentences.'''
        self._plain_sentences = [u' '.join(sentence) for sentence in self._word_sentences]
    
    def _create_document(self):
        '''Create a plain text document.'''
        self._document = Document(self._docname, u' '.join(self._plain_sentences))
    
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
                all_values.append([analyze[morph_key].decode('unicode_escape') for analyze in token.get('analyysid', [])])
        segments = []
        for values, start, end in zip(all_values, self._word_starts, self._word_ends):
            for value in values:
                segments.append(Segment(unicode(morph_key), value, self._document, start, end))
        segmentstorage.save(segments)

def compute_starts(tokens, sep=u' '):
    '''Compute start positions of tokens, if they were joined by given separator as a single string.'''
    seplen = len(sep)
    starts = []
    next_start = 0
    for token in tokens:
        starts.append(next_start)
        next_start += len(token) + seplen
    return starts
     
def compute_ends(tokens, sep=u' '):
    '''Compute end positions of tokens, if they were joined by given separator as a single string.'''
    ends = []
    if len(tokens) == 0:
        return ends
    else:
        seplen = len(sep)
        next_end = len(tokens[0])
        for token in tokens[1:]:
            ends.append(next_end)
            next_end += seplen + len(token)
        ends.append(next_end)
        return ends

if __name__ == '__main__':
    documentstorage = MongoDocumentStorage()
    segmentstorage = MongoSegmentStorage()
    importer = EtsaImporter(host='127.0.0.1',
                    port=3310,
                    user='etsad',
                    passwd='2KHZjJRNwqScpnvh',
                    db='etsad2',
                    table_name=u'anamnesis_nlp',
                    name_prefix=u'etsastat',
                    documentstorage=documentstorage,
                    segmentstorage=segmentstorage)
    importer.import_data()
