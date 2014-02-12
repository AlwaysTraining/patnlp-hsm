import unittest
from textlab.data.segmentstorage import SegmentStorage
from textlab.data.document import Document
from textlab.data.segment import Segment
from textlab.data.documentstorage import DocumentStorage
from textlab.tools.dictionarylearner import DictionaryLearner
from textlab.data.segmentcorpus import SegmentCorpus

class SegmentCorpusTest(unittest.TestCase):
    
    def test_size(self):
        corpus = self.corpus()
        actual = [segment for segment in corpus]
        self.assertEqual(len(actual), len(corpus))
    
    def documentA(self):
        return Document(u'docA', u'Ahaa, see on esimene korpus')
    
    def documentB(self):
        return Document(u'docB', u'Hmm, see on teine korpus')
    
    def documentC(self):
        return Document(u'docC', u'Ja siin on kolmas korpus')
    
    
    def segmentA(self):
        return Segment(u'random', u'aaa', self.documentA(), 0, 4)
    
    def segmentB(self):
        return Segment(u'random', u'bbb', self.documentB(), 5, 10)
    
    def documentstorage(self):
        storage = DocumentStorage()
        storage.save_all([self.documentA(), self.documentB(), self.documentC()])
        return storage
    
    def segmentstorage(self):
        storage = SegmentStorage()
        storage.save([self.segmentA(), self.segmentB()])
        return storage

    def dictionary(self):
        learner = DictionaryLearner(3)
        learner.fit(self.documentstorage(), filter_extremes=False)
        return learner.get()
    
    def corpus(self):
        return SegmentCorpus(u'random', self.dictionary(), self.segmentstorage())
