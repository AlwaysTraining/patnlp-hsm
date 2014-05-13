'''Module for importing cnll files.'''

import codecs
from copy import deepcopy
from itertools import izip
import logging

from hsm.data.document import Document
from hsm.data.importer.util import compute_starts, compute_ends
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
from hsm.data.segment import Segment


logging.basicConfig()

def get_lemma(morph_lemma):
    if len(morph_lemma) > 1:
        ridx = morph_lemma.rfind("=")
        if ridx == -1: ridx = morph_lemma.rfind("+")
        if ridx == -1: ridx = len(morph_lemma)
        if ridx > 0:
            morph_lemma = morph_lemma[:ridx]
        lemma = morph_lemma.replace("_", "")
    else:
        lemma = morph_lemma 
    return lemma.lower()

def get_word_parts(morph_lemma):
    ridx = morph_lemma.rfind("=")
    if ridx == -1: ridx = morph_lemma.rfind("+")
    if ridx == -1: ridx = len(morph_lemma)
    lemma = morph_lemma[:ridx]
    lemma = lemma.lower()
    chunks = lemma.split("_")
    if len(chunks) > 1:
        prefix, postfix = chunks[0], chunks[-1]
    else:
        prefix, postfix = None, None
    return prefix, postfix

def get_case(morph):
    if morph.startswith("_S_") or morph.startswith("_H_"):
        try:
            case = morph[morph.rindex(" ") + 1: len(morph)]
        except ValueError:
            case = None
    else:
        case = None  
    return case

def get_pos(morph):
    pos = morph.split()[0][1:-1]
    return pos

class Lists(object):
    '''Dictionary for collection lists of tokens.'''
    
    def __init__(self):
        self.word = []
        self.lemma = []
        self.pos = []
        self.case = []
        self.ne_type = []
    
    def append(self, line):
        parts = line.split('\t')
        if len(parts) == 4:
            self.word.append(parts[0].strip())
            self.lemma.append(get_lemma(parts[1]))
            self.pos.append(get_pos(parts[2]))
            self.case.append(get_case(parts[2]))
            self.ne_type.append(parts[3].strip().upper())
    
    @staticmethod
    def concatenate(lists):
        concat = Lists()
        f = lambda x, y: x + y
        concat.word = reduce(f, map(lambda x: x.word, lists))
        concat.lemma = reduce(f, map(lambda x: x.lemma, lists))
        concat.pos = reduce(f, map(lambda x: x.pos, lists))
        concat.case = reduce(f, map(lambda x: x.case, lists))
        concat.ne_type = reduce(f, map(lambda x: x.ne_type, lists))
        assert len(concat.word) == len(concat.lemma) == len(concat.pos) == len(concat.case) == len(concat.ne_type)
        return concat
    
    def __len__(self):
        return len(self.word)
    
    def clear(self):
        self.word[:] = []
        self.lemma[:] = []
        self.pos[:] = []
        self.case[:] = []
        self.ne_type[:] = []

def create_ne_segments(values, starts, ends, document, segstorage):
    segments = []
    segment = None
    for value, start, end in izip(values, starts, ends):
        if value.startswith('B-'):
            ne_value = value[2:]
            if segment is not None:
                segments.append(segment)
                segment = Segment(u'ne_type', ne_value, document, start, end)
            segment = Segment(u'ne_type', ne_value, document, start, end)
        elif value.startswith('I-'):
            segment.end = end 
        elif value.startswith('O') and segment is not None:
            segments.append(segment)
            segment = None
    if segment is not None:
        segment.end = len(document.text)
        segments.append(segment)
    segstorage.save(segments)

def create_segments(name, values, starts, ends, document, segstorage):
    segments = []
    for value, start, end in izip(values, starts, ends):
        if value is not None:
            segments.append(Segment(name, value, document, start, end))
    segstorage.save(segments)

def create_sentences(list_of_lists, document, segstorage):
    plain_sentences = [u' '.join(lists.word) for lists in list_of_lists]
    segments = []
    starts, ends = compute_starts(plain_sentences, u' '), compute_ends(plain_sentences, u' ')
    for sentence, start, end in izip(plain_sentences, starts, ends):
        segments.append(Segment(u'sentence', sentence, document, start, end))
    segstorage.save(segments)

class CnllImporter(object):
    
    logger = logging.getLogger('cnllimporter')
    logger.setLevel(logging.DEBUG)
    
    def __init__(self, **kwargs):
        '''Initialize a new importer.
        Arguments:
        filename - the file containing the corpus.
        name_prefix - the name to prefix the documents with, such as 'etsastat:'
        documentstorage - instance of the document storage to save the documents to.
        segmentstorage - instance of the segment storage to save the segments to.
        '''
        self._fnm = kwargs.get('filename')
        self._name_prefix = kwargs['name_prefix']
        self._documentstorage = kwargs['documentstorage']
        self._segmentstorage = kwargs['segmentstorage']
        self._doc_idx = None
        
        assert isinstance(self._name_prefix, unicode)
        assert len(self._name_prefix) > 0

    def _end_of_sentence(self, sentences, lists):
        if len(lists) > 0:
            sentences.append(deepcopy(lists))
            lists.clear()
    
    def _end_of_document(self, sentences):
        lists = Lists.concatenate(sentences)
        # create document
        doc_text = u' '.join(lists.word)
        document = Document(self._name_prefix + unicode(self._doc_idx), doc_text)
        self._documentstorage.save(document)
        self._doc_idx += 1
        
        # create segments
        starts, ends = compute_starts(lists.word, u' '), compute_ends(lists.word, u' ')
        create_segments(u'word', lists.word, starts, ends, document, self._segmentstorage)
        create_segments(u'lemma', lists.lemma, starts, ends, document, self._segmentstorage)
        create_segments(u'case', lists.case, starts, ends, document, self._segmentstorage)
        create_segments(u'pos', lists.pos, starts, ends, document, self._segmentstorage)
        create_ne_segments(lists.ne_type, starts, ends, document, self._segmentstorage)
        
        # create sentece segments
        create_sentences(sentences, document, self._segmentstorage)
        
        sentences[:] = []

    def import_data(self):
        self._doc_idx = 1
        f = codecs.open(self._fnm, 'r', 'utf-8')
        lists = Lists()
        sentences = []
        line = f.readline()
        while line != '':
            line = line.strip()
            lists.append(line)
            if len(line) == 0 or line == '--':
                self._end_of_sentence(sentences, lists)
            if line == '--':
                self._end_of_document(sentences)
            line = f.readline()
        self._end_of_sentence(sentences, lists)
        self._end_of_document(sentences)
        
if __name__ == '__main__':
    documentstorage = MongoDocumentStorage()
    segmentstorage = MongoSegmentStorage()
    importer = CnllImporter(filename='/home/timo/estner/estner.cnll',
                    name_prefix=u'ner:',
                    documentstorage=documentstorage,
                    segmentstorage=segmentstorage)
    importer.import_data()
