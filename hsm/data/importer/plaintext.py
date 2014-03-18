''' One document per line importer.'''
import codecs

from hsm.data.document import Document
from hsm.data.documentstorage import DocumentStorage
from hsm.data.importer.util import compute_starts, compute_ends
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
from hsm.data.segment import Segment
from hsm.data.segmentstorage import SegmentStorage


class PlainTextImporter(object):
    
    def __init__(self, input_fnm, doc_prefix, docstorage, segstorage):
        self._input_fnm = input_fnm
        self._doc_prefix = doc_prefix
        self._docstorage = docstorage
        self._segstorage = segstorage

    def _process_line(self, line, doc_idx):
        tokens = line.split()
        starts, ends = compute_starts(tokens, u' '), compute_ends(tokens, u' ')
        document = Document(self._doc_prefix + u":" + str(doc_idx), line, {})
        segments = []
        for tok, start, end in zip(tokens, starts, ends):
            segment = Segment(u'token', tok, document, start, end)
            segments.append(segment)
        self._docstorage.save(document)
        self._segstorage.save(segments)

    def process(self):
        self._docstorage.delete_all(self._doc_prefix)
        self._segstorage.delete(doc_prefix=self._doc_prefix)
        f = codecs.open(self._input_fnm, 'rb', 'utf-8')
        line = f.readline()
        doc_idx = 1
        while line != '':
            self._process_line(line, doc_idx)
            doc_idx += 1
            line = f.readline()
        f.close()
        
if __name__ == '__main__':
    docstorage = MongoDocumentStorage()
    segstorage = MongoSegmentStorage()
    #docstorage = DocumentStorage()
    #segstorage = SegmentStorage()
    importer = PlainTextImporter('/home/timo/korpused/ut tagasiside/tagasiside.txt', u'ut', docstorage, segstorage)
    importer.process()
