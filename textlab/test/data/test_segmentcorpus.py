import unittest
from textlab.data.segmentstorage import SegmentStorage
from textlab.data.document import Document
from textlab.data.segment import Segment
from textlab.data.documentstorage import DocumentStorage
from textlab.tools.dictionarylearner import DictionaryLearner
from textlab.data.segmentcorpus import SegmentCorpus

class FragmentCorpusTest(unittest.TestCase):
    
    def test_size(self):
        corpus = self.corpus()
        actual = [segment for segment in corpus]
        self.assertEqual(len(actual), len(corpus))
    
    def document(self):
        return Document(u'the document', u'aaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbcccccccccddddddddd')
    
    def segmentA(self):
        return Segment(u'random', u'aaa', self.document(), 0, 4)
    
    def segmentB(self):
        return Segment(u'random', u'bbb', self.document(), 5, 10)
    
    def documentstorage(self):
        storage = DocumentStorage()
        document = self.document()
        storage.save(document)
        return storage
    
    def segmentstorage(self):
        storage = SegmentStorage()
        storage.save([self.segmentA(), self.segmentB()])
        return storage

    def dictionary(self):
        learner = DictionaryLearner(2)
        learner.fit(self.documentstorage())
        print learner.get()
        return learner.get()
    
    def corpus(self):
        return SegmentCorpus(u'random', self.dictionary(), self.segmentstorage())
