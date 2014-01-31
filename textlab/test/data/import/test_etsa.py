# -*- coding: utf-8 -*-
import inspect
import os
import unittest

from textlab.data.document import Document
from textlab.data.documentstorage import DocumentStorage
from textlab.data.importer.etsa import compute_starts, compute_ends, \
    EtsaDocumentExtractor
from textlab.data.segment import Segment
from textlab.data.segmentstorage import SegmentStorage


class EtsaDocumentExtractorTest(unittest.TestCase):
    '''Test that all segments get extracted from the testing ETSA document.'''
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        path = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), 'etsaimporttest.data')
        extractor = EtsaDocumentExtractor(self.doc_name(), open(path, 'r').read())
        self._documentstorage = DocumentStorage()
        self._segmentstorage = SegmentStorage()
        extractor.process(self._documentstorage, self._segmentstorage)
    
    def test_document_import(self):
        document = self._documentstorage.load(self.doc_name())
        self.assertEqual(document.text, self.doc_text())
    
    def test_sentence_segment_import(self):
        segments = self._segmentstorage.load(doc_name=self.doc_name(), name=u'sentence')
        self.assertEqual(segments, self.sentence_segments())
    
    def test_word_segment_import(self):
        segments = self._segmentstorage.load(doc_name=self.doc_name(), name=u'word')
        self.assertEqual(segments, self.word_segments())
    
    def test_lemma_segment_import(self):
        segments = self._segmentstorage.load(doc_name=self.doc_name(), name=u'lemma')
        self.assertEqual(segments, self.lemma_segments())
    
    def test_pos_segment_import(self):
        segments = self._segmentstorage.load(doc_name=self.doc_name(), name=u'pos')
        self.assertEqual(segments, self.pos_segments())

    def doc_name(self):
        return u'testdoc'

    def doc_text(self):
        return u'Kaebused : Kaebuseks viimasel nädalals süvenenud õhupuudustunne . Operatsioonijärgne kulg iseärasusteta .'
    
    def document(self):
        return Document(self.doc_name(), self.doc_text())
    
    def sentence_segments(self):
        return set([Segment(u'sentence', u'Kaebused : Kaebuseks viimasel nädalals süvenenud õhupuudustunne .', self.document(), 0, 65),
                    Segment(u'sentence', u'Operatsioonijärgne kulg iseärasusteta .', self.document(), 66, 105)])

    def word_segments(self):
        document = self.document()
        return set([Segment(u'word', u'Kaebused', document, 0, 8),
                    Segment(u'word', u':', document, 9, 10),
                    Segment(u'word', u'Kaebuseks', document, 11, 20),
                    Segment(u'word', u'viimasel', document, 21, 29),
                    Segment(u'word', u'nädalals', document, 30, 38),
                    Segment(u'word', u'süvenenud', document, 39, 48),
                    Segment(u'word', u'õhupuudustunne', document, 49, 63),
                    Segment(u'word', u'.', document, 64, 65),
                    Segment(u'word', u'Operatsioonijärgne', document, 66, 84),
                    Segment(u'word', u'kulg', document, 85, 89),
                    Segment(u'word', u'iseärasusteta', document, 90, 103),
                    Segment(u'word', u'.', document, 104, 105)])

    def lemma_segments(self):
        document = self.document()
        return set([Segment(u'lemma', u'kaebus', document, 0, 8),
                    Segment(u'lemma', u':', document, 9, 10),
                    Segment(u'lemma', u'kaebus', document, 11, 20),
                    Segment(u'lemma', u'viimane', document, 21, 29),
                    Segment(u'lemma', u'nädalals', document, 30, 38), # first variant
                    Segment(u'lemma', u'nädal', document, 30, 38),    # second variant
                    Segment(u'lemma', u'süvenema', document, 39, 48), # first variant
                    Segment(u'lemma', u'süvenenud', document, 39, 48), # second variant
                    Segment(u'lemma', u'õhupuudustunne', document, 49, 63),
                    Segment(u'lemma', u'.', document, 64, 65),
                    Segment(u'lemma', u'operatsioonijärgne', document, 66, 84),
                    Segment(u'lemma', u'kulg', document, 85, 89),
                    # missing analyze
                    Segment(u'lemma', u'.', document, 104, 105)])
        
    def pos_segments(self):
        document = self.document()
        return set([Segment(u'pos', u'S', document, 0, 8),
                    Segment(u'pos', u'Z', document, 9, 10),
                    Segment(u'pos', u'H', document, 11, 20),
                    Segment(u'pos', u'A', document, 21, 29),
                    Segment(u'pos', u'S', document, 30, 38),
                    Segment(u'pos', u'V', document, 39, 48), # first variant
                    Segment(u'pos', u'A', document, 39, 48), # second variant
                    Segment(u'pos', u'S', document, 49, 63),
                    Segment(u'pos', u'Z', document, 64, 65),
                    Segment(u'pos', u'A', document, 66, 84),
                    Segment(u'pos', u'S', document, 85, 89),
                    # missing analyze
                    Segment(u'pos', u'Z', document, 104, 105)])

