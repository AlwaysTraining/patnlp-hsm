import unittest

import hsm
from hsm.data.document import Document
from hsm.data.segment import Segment


class SegmentTest(unittest.TestCase):
    
    def test_construction(self):
        seg = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        self.assertEqual(seg.name, self.name())
        self.assertEqual(seg.value, self.value())
        self.assertEqual(seg.doc_name, self.document().name)
        self.assertEqual(seg.doc_len, len(self.document().text))
        self.assertEqual(seg.start, self.start())
        self.assertEqual(seg.end, self.end())
    
    def test_construction_invalid_name(self):
        self.assertRaises(AssertionError, Segment, 'ascii name', self.value(), self.document(), self.start(), self.end())
        
    def test_construction_invalid_value(self):
        self.assertRaises(AssertionError, Segment, self.name(), 'ascii value', self.document(), self.start(), self.end())
        
    def test_construction_invalid_start(self):
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), self.document(), -1, self.end())
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), self.document(), 10000, self.end()) # greater than doc length
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), self.document(), self.end()+1, self.end())
    
    def test_construction_invalid_end(self):
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), self.document(), self.end(), self.end()-1)
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), self.document(), self.end(), -1)
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), self.document(), self.end(), 100000) # greater than doc length
    
    def test_construction_without_document(self):
        seg = Segment(self.name(), self.value(), None, self.start(), self.end(), self.document().name, len(self.document().text))
        self.assertEqual(seg.name, self.name())
        self.assertEqual(seg.value, self.value())
        self.assertEqual(seg.doc_name, self.document().name)
        self.assertEqual(seg.doc_len, len(self.document().text))
        self.assertEqual(seg.start, self.start())
        self.assertEqual(seg.end, self.end())
        
    def test_construction_without_document_invalid_name(self):
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), None, self.end(), self.end()-1, 'asciiname', len(self.document().text))
        
    def test_construction_without_document_invalid_len(self):
        self.assertRaises(AssertionError, Segment, self.name(), self.value(), None, self.end(), self.end()-1, self.document().name, -1)
    
    def test_equality(self):
        A = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        B = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        self.assertEqual(A, B)
    
    def test_inequality(self):
        A = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        B = Segment(self.name(), u'Some other value', self.document(), self.start(), self.end())
        self.assertNotEqual(A, B)
    
    def test_cmp(self):
        A = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        B = Segment(self.name(), self.value(), self.document(), self.start(), self.end()+1)
        self.assertEqual(cmp(A, B), -1)
    
    def test_hash(self):
        A = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        B = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        self.assertEqual(set([A]), set([B]))
    
    def test_from_dict(self):
        A = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        B = Segment.from_dict(self.dictionary())
        self.assertEqual(A, B)
    
    def test_to_dict(self):
        A = Segment(self.name(), self.value(), self.document(), self.start(), self.end())
        self.assertEqual(Segment.to_dict(A), self.dictionary())
    
    def name(self):
        return u'TEST SEGMENT'
    
    def value(self):
        return u'segment value'
    
    def start(self):
        return 0
    
    def end(self):
        return 3
    
    def document(self):
        return Document(u'DOC_ID', u'Some text', {})
    
    def dictionary(self):
        return {'name': self.name(),
                'value': self.value(),
                'start': self.start(),
                'end': self.end(),
                'doc_name': self.document().name,
                'doc_len': len(self.document().text)}
