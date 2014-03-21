import unittest

from hsm.data.document import Document
from hsm.data.documentstorage import DocumentStorage
from hsm.data.segment import Segment
from hsm.data.segmentstorage import SegmentStorage
from hsm.tools.filter import SegmentDocumentMatcher, ContainerFilter, Filter, \
    FILTER_NAME, SEGMENT_NAME, OUTPUT_NAME, CONTAINER_NAME, CONTAINER_INCLUDES, \
    SEGMENT_VALUE_REGEX, CREATES_SEGMENT, SEGMENT_NEG_REGEX, DOCUMENT_PREFIX, \
    DOCUMENT_REGEX, DOCUMENT_NEG_REGEX, MIXIN_NAME, SPLITTER_REGEX, SPLITTER_LEFT, \
    SPLITTER_RIGHT, SPLITTER_NEG_REGEX, CONTAINER_VALUE_REGEX


def iterator(iterable):
    for elem in iterable:
        yield elem

class SegmentDocumentMatcherTest(unittest.TestCase):
    
    def test_empty(self):
        matcher = SegmentDocumentMatcher(iterator([]), iterator([]))
        self.assertEqual(list(matcher.get()), [])
    
    def test_basic(self):
        matcher = SegmentDocumentMatcher(iterator(self.first_segments()), iterator(self.second_segments()))
        tuples = list(matcher.get())
        self.assertEqual(len(tuples), 1)
        self.assertEqual(set(tuples[0][0]), set([self.first2()]))
        self.assertEqual(set(tuples[0][1]), set([self.second1(), self.second2()]))
    
    def test_end(self):
        matcher = SegmentDocumentMatcher(iterator(self.first_segments()), iterator(self.third_segments()))
        tuples = list(matcher.get())
        self.assertEqual(len(tuples), 1)
        self.assertEqual(set(tuples[0][0]), set([self.first3()]))
        self.assertEqual(set(tuples[0][1]), set([self.third1(), self.third2()]))
    
    def first1(self):
        return Segment(u'first', u'', None, 0, 2, u'DOC A', 100)
    
    def first2(self):
        return Segment(u'first', u'', None, 0, 2, u'DOC B', 100)
    
    def first3(self):
        return Segment(u'first', u'', None, 0, 2, u'DOC D', 100)
    
    def first_segments(self):
        return [self.first1(), self.first2(), self.first3()]
    
    def second1(self):
        return Segment(u'second', u'B', None, 0, 2, u'DOC B', 100)
    
    def second2(self):
        return Segment(u'second', u'B', None, 3, 5, u'DOC B', 100)
    
    def second3(self):
        return Segment(u'second', u'', None, 0, 2, u'DOC C', 100)
        
    def second4(self):
        return Segment(u'second', u'', None, 3, 5, u'DOC C', 100)
    
    def second_segments(self):
        return [self.second1(), self.second2(), self.second3(), self.second4()]
    
    def third1(self):
        return Segment(u'third', u'', None, 3, 5, u'DOC D', 100)
    
    def third2(self):
        return Segment(u'third', u'', None, 7, 10, u'DOC D', 100)
    
    def third_segments(self):
        return [self.third1(), self.third2()]


class ContainerFilterTest(unittest.TestCase):
    
    def test_container_contains_keep_source(self):
        contfilter = ContainerFilter(iterator(self.first_segments()), iterator(self.second_segments()), True, True)
        self.assertEqual(set(contfilter.get()), set([self.first1()]))
    
    def test_container_contains_keep_container(self):
        contfilter = ContainerFilter(iterator(self.first_segments()), iterator(self.second_segments()), True, False)
        self.assertEqual(set(contfilter.get()), set([self.second1()]))
    
    def test_source_contains_keep_source(self):
        contfilter = ContainerFilter(iterator(self.second_segments()), iterator(self.first_segments()), False, True)
        self.assertEqual(set(contfilter.get()), set([self.second1()]))
    
    def test_source_contains_keep_container(self):
        contfilter = ContainerFilter(iterator(self.second_segments()), iterator(self.first_segments()), False, False)
        self.assertEqual(set(contfilter.get()), set([self.first1()]))
    
    def first1(self):
        return Segment(u'first', u'', None, 0, 10, u'DOC A', 100)
    
    def first2(self):
        return Segment(u'first', u'', None, 9, 11, u'DOC A', 100)
    
    def first_segments(self):
        return [self.first1(), self.first2()]
    
    def second1(self):
        return Segment(u'container', u'', None, 0, 10, u'DOC A', 100)
    
    def second2(self):
        return Segment(u'container', u'', None, 10, 15, u'DOC A', 100)
    
    def second_segments(self):
        return [self.second1(), self.second2()]
    

class FilterTest(unittest.TestCase):
    
    def basic_kwargs(self):
        return {FILTER_NAME: u'test_filter',
                SEGMENT_NAME: u'lemma',
                OUTPUT_NAME: u'lemma:copy'}
    
    def test_construction(self):
        filt = Filter(**self.basic_kwargs())
        self.assertEqual(filt[FILTER_NAME], u'test_filter')
        self.assertEqual(filt[SEGMENT_NAME], u'lemma')
        self.assertEqual(filt[OUTPUT_NAME], u'lemma:copy')
    
    def test_invalid_keyword(self):
        kwargs = self.basic_kwargs()
        kwargs['invalid'] = u'invalid'
        self.assertRaises(ValueError, Filter, **kwargs)
    
    def test_missing_mandatory_keyword(self):
        kwargs = self.basic_kwargs()
        del kwargs[FILTER_NAME]
        self.assertRaises(ValueError, Filter, **kwargs)
    
    def test_wrong_type_for_unicode(self):
        kwargs = self.basic_kwargs()
        kwargs[CONTAINER_NAME] = 'non unicode name'
        self.assertRaises(AssertionError, Filter, **kwargs)
    
    def test_wrong_type_for_bool(self):
        kwargs = self.basic_kwargs()
        kwargs[CONTAINER_INCLUDES] = u'non bool'
        self.assertRaises(AssertionError, Filter, **kwargs)
    
    def test_set_value(self):
        filt = Filter(**self.basic_kwargs())
        filt[SEGMENT_NAME] = u'pos'
        self.assertEqual(filt[SEGMENT_NAME], u'pos')
    
    def test_set_invalid_keyword_value(self):
        filt = Filter(**self.basic_kwargs())
        self.assertRaises(ValueError, filt.__setitem__, u'invalid key', u'some value')
    
    def test_set_wrong_type(self):
        filt = Filter(**self.basic_kwargs())
        self.assertRaises(AssertionError, filt.__setitem__, CONTAINER_INCLUDES, u'unicode value')
        self.assertRaises(AssertionError, filt.__setitem__, FILTER_NAME, 0)
    
    def second_keywords(self):
        return {FILTER_NAME: u'second_filter',
                SEGMENT_NAME: u'second:lemma',
                OUTPUT_NAME: u'second:lemma:copy'}
    
    def test_update(self):
        filt = Filter(**self.basic_kwargs())
        filt.update(self.second_keywords())
        self.assertEqual(filt[FILTER_NAME], u'second_filter')
        self.assertEqual(filt[SEGMENT_NAME], u'second:lemma')
        self.assertEqual(filt[OUTPUT_NAME], u'second:lemma:copy')
    
    def test_basic_copy(self):
        filt = Filter(**self.basic_kwargs())
        outs = set(filt.filter(self.segmentstorage(), self.documentstorage()))
        self.assertEqual(outs, set(self.first_copy_lemmas()) | set(self.second_copy_lemmas()))
    
    def test_apply(self):
        filt = Filter(**self.basic_kwargs())
        segmentstorage = self.segmentstorage()
        filt.apply(segmentstorage, self.documentstorage())
        copies = set(segmentstorage.load(name=u'lemma:copy'))
        self.assertEqual(copies, set(self.first_copy_lemmas()) | set(self.second_copy_lemmas()))
    
    def test_second_apply_removes_previous_segments(self):
        filt = Filter(**self.basic_kwargs())
        segmentstorage = self.segmentstorage()
        filt.apply(segmentstorage, self.documentstorage())
        filt.apply(segmentstorage, self.documentstorage()) # second apply
        copies = set(segmentstorage.load(name=u'lemma:copy'))
        self.assertEqual(copies, set(self.first_copy_lemmas()) | set(self.second_copy_lemmas()))
        
    
    def test_basic_creation(self):
        kwargs = self.basic_kwargs()
        kwargs[SEGMENT_VALUE_REGEX] = u'was|sick|\d+'
        kwargs[SEGMENT_NEG_REGEX] = u'was'
        kwargs[OUTPUT_NAME] = u'lemma'
        kwargs[CREATES_SEGMENT] = True
        segmentstorage = SegmentStorage()
        filt = Filter(**kwargs)
        filt.apply(segmentstorage, self.documentstorage())
        segs = segmentstorage.load(name=u'lemma')
        self.assertEqual(set(segs), set([self.lemma3(), self.lemma7()]))
    
    def test_basic_regex(self):
        kwargs = self.basic_kwargs()
        kwargs[SEGMENT_VALUE_REGEX] = u'was|sick|\d+'
        kwargs[SEGMENT_NEG_REGEX] = u'was'
        kwargs[OUTPUT_NAME] = u'lemma'
        kwargs[CREATES_SEGMENT] = False
        filt = Filter(**kwargs)
        outs = filt.filter(self.segmentstorage(), self.documentstorage())
        self.assertEqual(set(outs), set([self.lemma3(), self.lemma7()]))
    
    def test_with_document_prefix(self):
        kwargs = self.basic_kwargs()
        kwargs[DOCUMENT_PREFIX] = u'DOCUMENT B'
        filt = Filter(**kwargs)
        outs = set(filt.filter(self.segmentstorage(), self.documentstorage()))
        self.assertEqual(outs, set(self.second_copy_lemmas()))
    
    def test_with_document_regex(self):
        kwargs = self.basic_kwargs()
        kwargs[DOCUMENT_REGEX] = u's'
        kwargs[DOCUMENT_NEG_REGEX] = u'sic'
        filt = Filter(**kwargs)
        outs = set(filt.filter(self.segmentstorage(), self.documentstorage()))
        self.assertEqual(outs, set(self.second_copy_lemmas()))
    
    def test_with_container(self):
        kwargs = self.basic_kwargs()
        kwargs[CONTAINER_NAME] = u'sentence'
        kwargs[CONTAINER_VALUE_REGEX] = u'length'
        filt = Filter(**kwargs)
        outs = set(filt.filter(self.segmentstorage(), self.documentstorage()))
        self.assertEqual(set(outs), set(self.second_copy_lemmas()))
    
    def test_with_mixin(self):
        kwargs = self.basic_kwargs()
        kwargs[MIXIN_NAME] = u'mixin'
        filt = Filter(**kwargs)
        segmentstorage = self.segmentstorage()
        segmentstorage.save([self.mixin1()])
        outs = set(filt.filter(segmentstorage, self.documentstorage()))
        self.assertEqual(outs, set(self.first_copy_lemmas()) | set(self.second_copy_lemmas()) | set([self.mixin_copy1()]))
    
    def test_splitter_full(self):
        kwargs = self.basic_kwargs()
        kwargs[SPLITTER_LEFT] = u'e'
        kwargs[SPLITTER_REGEX] = u' '
        kwargs[SPLITTER_RIGHT] = u'...'
        kwargs[SPLITTER_NEG_REGEX] = u'was'
        kwargs[SEGMENT_NAME] = u'sentence'
        kwargs[OUTPUT_NAME] = u'fragment'
        filt = Filter(**kwargs)
        segmentstorage = self.segmentstorage()
        segmentstorage.save([self.sentence1(), self.sentence2()])
        outs = set(filt.filter(segmentstorage, self.documentstorage()))
        self.assertEqual(outs, set(self.fragments()))
    
    def documentA(self):
        return Document(u'DOCUMENT A', u'Dude was sick!')
    
    def documentB(self):
        return Document(u'DOCUMENT B', u'The length is 100')
    
    def documentstorage(self):
        storage = DocumentStorage()
        storage.save_all([self.documentA(), self.documentB()])
        return storage
    
    def lemma1(self):
        return Segment(u'lemma', u'dude', self.documentA(), 0, 4)
    
    def lemma2(self):
        return Segment(u'lemma', u'is', self.documentA(), 5, 8)
    
    def lemma3(self):
        return Segment(u'lemma', u'sick', self.documentA(), 9, 13)
    
    def lemma4(self):
        return Segment(u'lemma', u'the', self.documentB(), 0, 3)
    
    def lemma5(self):
        return Segment(u'lemma', u'length', self.documentB(), 4, 10)
    
    def lemma6(self):
        return Segment(u'lemma', u'is', self.documentB(), 11, 13)
    
    def lemma7(self):
        return Segment(u'lemma', u'100', self.documentB(), 14, 17)
    
    def mixin1(self):
        return Segment(u'mixin', u'Dude was', self.documentA(), 0, 8)
    
    def mixin_copy1(self):
        return Segment(u'lemma:copy', u'Dude was', self.documentA(), 0, 8)
    
    def first_copy_lemmas(self):
        res = []
        for seg in [self.lemma1(), self.lemma2(), self.lemma3()]:
            seg.name = u'lemma:copy'
            res.append(seg)
        return res

    def second_copy_lemmas(self):
        res = []
        for seg in [self.lemma4(), self.lemma5(), self.lemma6(), self.lemma7()]:
            seg.name = u'lemma:copy'
            res.append(seg)
        return res
    
    def sentence1(self):
        return Segment(u'sentence', u'Dude was sick!', self.documentA(), 0, 14)
    
    def sentence2(self):
        return Segment(u'sentence', u'The length is 100', self.documentB(), 0, 17)
    
    def fragments(self):
        return [Segment(u'fragment', u'Dude was sick!', self.documentA(), 0, 14),
                Segment(u'fragment', u'The', self.documentB(), 0, 3),
                Segment(u'fragment', u'length is 100', self.documentB(), 4, 17)]
    
    def segmentstorage(self):
        storage = SegmentStorage()
        storage.save([self.lemma1(), self.lemma2(), self.lemma3()])
        storage.save([self.lemma4(), self.lemma5(), self.lemma6(), self.lemma7()])
        storage.save([self.sentence1(), self.sentence2()])
        return storage
