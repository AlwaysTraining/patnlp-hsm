import unittest

from textlab.data.document import Document
from textlab.data.segment import Segment
from textlab.data.segmentstorage import SegmentStorage


class SegmentStorageTest(unittest.TestCase):
    
    def test_load_all_succeeds(self):
        segments = self.storage().load()
        self.assertEqual(segments, self.first_segments() | self.second_segments())
    
    def test_load_name_succeeds(self):
        segments = self.storage().load(name=u'SOME SEGMENT')
        self.assertEqual(segments, self.first_segments())
    
    def test_load_name_fails_invalid_name(self):
        self.assertRaises(AssertionError, self.storage().load, name='asciikey')
    
    def test_load_name_no_results(self):
        segments = self.storage().load(name=u'NONEXISTENT')
        self.assertEqual(segments, set())
    
    def test_load_name_prefix_succeeds(self):
        segments = self.storage().load(name_prefix=u'SOME')
        self.assertEqual(segments, self.first_segments())
    
    def test_load_filter_doc_name(self):
        segments = self.storage().load(doc_name=self.documentB().name)
        self.assertEqual(segments, set([self.segmentA3()]))
    
    def test_load_filter_doc_prefix(self):
        segments = self.storage().load(name=u'SOME SEGMENT', doc_prefix=u'DOCUMENT')
        self.assertEqual(segments, self.first_segments())
    
    def test_load_filter_doc_default_prefix(self):
        segments = self.storage().load(name=u'SOME SEGMENT')
        self.assertEqual(segments, self.first_segments())
        
    def test_load_filter_fails_invalid_filter(self):
        self.assertRaises(AssertionError, self.storage().load, name=u'OTHER SEGMENT', doc_name='asciikey')
        self.assertRaises(AssertionError, self.storage().load, name=u'OTHER SEGMENT', doc_prefix='asciikey')
    
    def test_load_prefix_overrides_name(self):
        segments = self.storage().load(name=u'SOME SEGMENT', name_prefix=u'')
        self.assertEqual(segments, self.first_segments() | self.second_segments())
    
    def test_load_filter_prefix_overrides_doc_name(self):
        segments = self.storage().load(doc_name=self.documentA().name, doc_prefix=u'')
        self.assertEqual(segments, self.first_segments() | self.second_segments())
    
    def test_load_limit(self):
        self.assertEqual(len(self.storage().load(limit=1)), 1)
    
    def test_load_invalid_limit(self):
        self.assertRaises(Exception, self.storage().load, limit=0)
    
    def test_load_iterator(self):
        iterator = self.storage().load_iterator(doc_name=self.documentA().name, doc_prefix=u'', sort=True)
        expected = self.first_segments() | self.second_segments()
        # test that the iterator does not output full set of segments
        self.assertNotEqual(iter, expected)
        # check that each returned segment is expected and collect them in the list
        result = []
        for segment in iterator:
            self.assertTrue(segment in expected)
            result.append(segment)
        # check that the list is sorted
        self.assertEqual(result, list(sorted(result)))
    
    def test_value_regex(self):
        segments = self.storage().load(value_regex=u'OTHER')
        expected = set([self.segmentB1(), self.segmentB2()])
        self.assertEqual(segments, expected)
    
    def test_neg_regex(self):
        segments = self.storage().load(neg_regex=u'SOME')
        expected = set([self.segmentB1(), self.segmentB2()])
        self.assertEqual(segments, expected)
    
    def test_value_neg_regex(self):
        segments = self.storage().load(value_regex=u'VALUE', neg_regex=u'SOME')
        expected = set([self.segmentB1(), self.segmentB2()])
        self.assertEqual(segments, expected)
    
    def test_save(self):
        storage = self.emptystorage()
        storage.save([self.segmentA1()])
        segment = storage.load(name=self.segmentA1().name).__iter__().next()
        self.assertEqual(segment, self.segmentA1())
    
    def test_delete_all(self):
        storage = self.storage()
        storage.delete()
        self.assertEqual(storage.load(), set([]))
    
    def test_delete_some(self):
        storage = self.storage()
        storage.delete(name_prefix=u'SOME')
        self.assertEqual(storage.load(), self.second_segments())
    
    def test_count_all(self):
        storage = self.storage()
        counts = storage.counts()
        expected = {u'SOME SEGMENT': 3, u'OTHER SEGMENT': 2}
        self.assertEqual(counts, expected)
    
    def test_count_docfilter(self):
        storage = self.storage()
        counts = storage.counts(doc_name=u'DOCUMENT A')
        expected = {u'SOME SEGMENT': 2, u'OTHER SEGMENT': 2}
        self.assertEqual(counts, expected)
    
    def test_count_docprefixfilter(self):
        storage = self.storage()
        counts = storage.counts(doc_prefix=u'DOCUMENT')
        expected = {u'SOME SEGMENT': 3, u'OTHER SEGMENT': 2}
        self.assertEqual(counts, expected)
    
    def test_count_segfilter(self):
        storage = self.storage()
        counts = storage.counts(name_prefix=u'')
        expected = {u'SOME SEGMENT': 3, u'OTHER SEGMENT': 2}
        self.assertEqual(counts, expected)
    
    def test_valuecount(self):
        storage = self.storage()
        counts = storage.value_counts()
        expected = {u'SOME VALUE': 3, u'OTHER VALUE': 2}
        self.assertEqual(counts, expected)
    
    def test_valuecount_filtering(self):
        storage = self.storage()
        counts = storage.value_counts(doc_prefix=u'DOCUMENT A', name_prefix=u'SOME')
        expected = {u'SOME VALUE': 2}
        self.assertEqual(counts, expected)
    
    def emptystorage(self):
        return SegmentStorage()
    
    def storage(self):
        storage = self.emptystorage()
        storage.save(self.first_segments())
        storage.save(self.second_segments())
        return storage
    
    def first_segments(self):
        return set([self.segmentA1(), self.segmentA2(), self.segmentA3()])
    
    def second_segments(self):
        return set([self.segmentB1(), self.segmentB2()])
    
    def segmentA1(self):
        return Segment(u'SOME SEGMENT', u'SOME VALUE', self.documentA(), 0, 2)
    
    def segmentA2(self):
        return Segment(u'SOME SEGMENT', u'SOME VALUE', self.documentA(), 2, 4)
    
    def segmentA3(self):
        return Segment(u'SOME SEGMENT', u'SOME VALUE', self.documentB(), 0, 2)
    
    def segmentB1(self):
        return Segment(u'OTHER SEGMENT', u'OTHER VALUE', self.documentA(), 4, 6)
    
    def segmentB2(self):
        return Segment(u'OTHER SEGMENT', u'OTHER VALUE', self.documentA(), 6, 10)
    
    def documentA(self):
        return Document(u'DOCUMENT A', u'These are the contents of the first document')
    
    def documentB(self):
        return Document(u'DOCUMENT B', u'Somewhere in the Mexico.')

