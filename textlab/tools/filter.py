'''
Basic segment filtering tool.

Features:
- can filter by regular expressions in segment values
- can filter by matching documents
- can create initial segments directly from documents
- can filter segments containing/contained by other types of segments
- can join or mix in segments of other types as a result.
'''
import re

from textlab.data.segment import Segment


FILTER_NAME = 'filter_name'

SEGMENT_NAME = 'segment_name'
SEGMENT_VALUE_REGEX = 'segment_value_regex'
SEGMENT_NEG_REGEX = 'segment_neg_regex'
CREATES_SEGMENT = 'creates_segment'
OUTPUT_NAME = 'output_name'

DOCUMENT_PREFIX = 'document_prefix'
DOCUMENT_REGEX = 'document_regex'
DOCUMENT_NEG_REGEX = 'document_neg_regex'

CONTAINER_NAME = 'container_name'
CONTAINER_VALUE_REGEX = 'container_value_regex'
CONTAINER_NEG_REGEX = 'container_neg_regex'
CONTAINER_INCLUDES = 'container_includes'
CONTAINER_KEEP_SOURCE = 'container_keep_source'

SPLITTER_LEFT = 'splitter_left'
SPLITTER_REGEX = 'splitter_regex'
SPLITTER_RIGHT = 'splitter_right'
SPLITTER_NEG_REGEX = 'splitter_neg_regex'

MIXIN_NAME = 'mixin_name'
MIXIN_VALUE_REGEX = 'mixin_value_regex'
MIXIN_NEG_REGEX = 'mixin_neg_regex'

class Filter(dict):
    # filter key names and types
    ALLOWED_KEYWORDS = frozenset([FILTER_NAME,
                                  SEGMENT_NAME, SEGMENT_VALUE_REGEX, SEGMENT_NEG_REGEX, CREATES_SEGMENT, OUTPUT_NAME,
                                  DOCUMENT_PREFIX, DOCUMENT_REGEX, DOCUMENT_NEG_REGEX,
                                  CONTAINER_NAME, CONTAINER_VALUE_REGEX, CONTAINER_NEG_REGEX, CONTAINER_INCLUDES, CONTAINER_KEEP_SOURCE,
                                  SPLITTER_LEFT, SPLITTER_REGEX, SPLITTER_RIGHT, SPLITTER_NEG_REGEX,
                                  MIXIN_NAME, MIXIN_VALUE_REGEX, MIXIN_NEG_REGEX])
    MANDATORY_KEYWORDS = frozenset([FILTER_NAME, SEGMENT_NAME, OUTPUT_NAME])
    BOOLEAN_KEYWORDS = frozenset([CREATES_SEGMENT, CONTAINER_INCLUDES, CONTAINER_KEEP_SOURCE])
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._check_everything()

    def _check_everything(self):
        self._check_allowed_keywords()
        self._check_mandatory_keywords()
        self._check_keyword_types()
        if len(self[FILTER_NAME]) == 0:
            raise ValueError('Filter name not specified!')

    def _check_allowed_keywords(self):
        for key in self:
            if key not in Filter.ALLOWED_KEYWORDS:
                raise ValueError(u'Invalid keyword: ' + key)
    
    def _check_mandatory_keywords(self):
        for key in Filter.MANDATORY_KEYWORDS:
            if key not in self:
                raise ValueError(u'Mandatory keyword ' + key + u' missing!')
    
    def _check_keyword_types(self):
        for key in self:
            if key in Filter.BOOLEAN_KEYWORDS and not isinstance(self[key], bool):
                raise AssertionError(key + ' does not have boolean value')
            elif key not in Filter.BOOLEAN_KEYWORDS and not isinstance(self[key], unicode):
                raise AssertionError(key + ' does not have unicode value')
    
    def __setitem__(self, key, value):
        super(Filter, self).__setitem__(key, value)
        self._check_everything()

    def update(self, *args, **kwargs):
        super(Filter, self).update(*args, **kwargs)
        self._check_everything()
    
    def _doc_iterator(self, docstorage):
        return docstorage.load_iterator(self.get(DOCUMENT_PREFIX, u''),
                                        regex=self.get(DOCUMENT_REGEX, None),
                                        neg_regex=self.get(DOCUMENT_NEG_REGEX, None))
        
    def _filtered_doc_names(self, docstorage):
        if DOCUMENT_REGEX in self or DOCUMENT_NEG_REGEX in self:
            return frozenset([doc.name for doc in self._doc_iterator(docstorage)])
    
    def _basic_segment_iterator(self, segstorage, docstorage):
        '''Method that loads the baseic segments of the filter.'''
        iterator = segstorage.load_iterator(name=self.get(SEGMENT_NAME),
                                            value_regex=self.get(SEGMENT_VALUE_REGEX, None),
                                            neg_regex=self.get(SEGMENT_NEG_REGEX, None),
                                            doc_prefix=self.get(DOCUMENT_PREFIX, None))
        docnames = self._filtered_doc_names(docstorage)
        for segment in iterator:
            if docnames is not None and segment.doc_name not in docnames:
                continue
            yield segment
    
    def _basic_segmentcreator_iterator(self, docstorage):
        '''Method that creates basic segments from raw documents.'''
        # compile value and negative regexes as necessary
        value_regex = re.compile(self[SEGMENT_VALUE_REGEX], re.UNICODE)
        neg_regex = None
        if SEGMENT_NEG_REGEX in self:
            neg_regex = re.compile(self[SEGMENT_NEG_REGEX], re.UNICODE)
        # iterate all matching documents to find matching segments
        seg_name = self[SEGMENT_NAME]
        for doc in self._doc_iterator(docstorage):
            text = doc.text
            for mo in value_regex.finditer(text):
                value = mo.group(0)
                # skip this item, if the negative regex matches it
                if neg_regex is not None and neg_regex.search(value) is not None:
                    continue
                yield Segment(seg_name, value, doc, mo.start(0), mo.end(0))

    def _container_segments(self, segstorage):
        return segstorage.load_iterator(name=self.get(CONTAINER_NAME),
                                        value_regex=self.get(CONTAINER_VALUE_REGEX, None),
                                        neg_regex=self.get(CONTAINER_NEG_REGEX, None),
                                        doc_prefix=self.get(DOCUMENT_PREFIX, None))


    def _mixin_segments(self, segstorage):
        return segstorage.load_iterator(name=self.get(MIXIN_NAME),
                                        value_regex=self.get(MIXIN_VALUE_REGEX, None),
                                        neg_regex=self.get(MIXIN_NEG_REGEX, None),
                                        doc_prefix=self.get(DOCUMENT_PREFIX, None))

    def _split(self, segment, pattern, neg_pattern):
        if segment.end - segment.start != len(segment.value):
            raise AssertionError('Splitter requires that the segment value would be same length as referenced document text.')
        # determine the matching split points
        split_points = []
        last_end = None
        for mo in pattern.finditer(segment.value):
            if neg_pattern is not None and neg_pattern.search(mo.group(0)) is not None:
                continue
            if len(split_points) == 0:
                split_points.append((0, mo.start('splitter')))
            else:
                split_points.append((last_end, mo.start('splitter')))
            last_end = mo.end('splitter')
        if last_end is not None:
            split_points.append((last_end, len(segment.value)))
        # generate segments
        for start, end in split_points:
            if end - start == 0:
                continue
            yield Segment(segment.name, segment.value[start:end], None, start, end, segment.doc_name, segment.doc_len)

    def filter_basic(self, segstorage, docstorage):
        creates_segment = self.get(CREATES_SEGMENT, False)
        if creates_segment:
            return self._basic_segmentcreator_iterator(docstorage)
        else:
            return self._basic_segment_iterator(segstorage, docstorage)

    def filter_container(self, basic_segments, segstorage):
        if CONTAINER_NAME in self:
            return ContainerFilter(basic_segments, self._container_segments(segstorage)).get()
        return basic_segments
    
    def filter_splitter(self, container_segments):
        if SPLITTER_REGEX in self:
            regex = self.get(SPLITTER_LEFT, u'') + u'(?P<splitter>' + self.get(SPLITTER_REGEX, u'') + u')' + self.get(SPLITTER_RIGHT, u'')
            pattern = re.compile(regex, re.UNICODE | re.MULTILINE)
            neg_pattern = None
            if SPLITTER_NEG_REGEX in self:
                neg_pattern = re.compile(self[SPLITTER_NEG_REGEX], re.UNICODE | re.MULTILINE)
            for cont_seg in container_segments:
                for seg in self._split(cont_seg, pattern, neg_pattern):
                    yield seg
        for seg in container_segments:
            yield seg
    
    def filter_mixin(self, splitter_segments, segstorage):
        if MIXIN_NAME in self:
            for seg in self._mixin_segments(segstorage):
                yield seg
        for seg in splitter_segments:
            yield seg
    
    def filter(self, segstorage, docstorage):
        basic = self.filter_basic(segstorage, docstorage)
        container = self.filter_container(basic, segstorage)
        splitter = self.filter_splitter(container)
        mixin = self.filter_mixin(splitter, segstorage)
        outname = self[OUTPUT_NAME]
        for seg in mixin:
            seg.name = outname
            yield seg
    
    def apply(self, segstorage, docstorage):
        batch_size = 1000
        segs = []
        for seg in self.filter(segstorage, docstorage):
            segs.append(seg)
            if len(segs) > batch_size:
                segstorage.save(segs)
                segs = []
        segstorage.save(segs)


class ContainerFilter(object):
    
    def __init__(self, basic_segments, container_segments, container_includes=True, keep_source=True):
        self._basic = basic_segments
        self._container = container_segments
        self._includes = container_includes
        self._keep_source = keep_source
    
    def get(self):
        matcher = SegmentDocumentMatcher(self._basic, self._container)
        if self._keep_source and self._includes:
            for first, second in matcher.get():
                for seg in first:
                    if self._is_matched(seg, second):
                        yield seg
        elif not self._keep_source and self._includes:
            for first, second in matcher.get():
                for seg in second:
                    if self._matches(seg, first):
                        yield seg
        elif self._keep_source and not self._includes:
            for first, second in matcher.get():
                for seg in first:
                    if self._matches(seg, second):
                        yield seg
        elif not self._keep_source and not self._includes:
            for first, second in matcher.get():
                for seg in second:
                    if self._is_matched(seg, first):
                        yield seg
    
    def _is_matched(self, segment, collection):
        for col_segment in collection:
            if segment.start >= col_segment.start and segment.end <= col_segment.end:
                return True
        return False
    
    def _matches(self, segment, collection):
        for col_segment in collection:
            if segment.start <= col_segment.start and segment.end >= col_segment.end:
                return True
        return False


class SegmentDocumentMatcher(object):
    '''Class that takes to iterables that return segments
       and yields piece-wise the segments belonging to same document.
       It assumes that the segments are sorted by document names.'''
    
    def __init__(self, first_iterator, second_iterator):
        self._first = first_iterator
        self._second = second_iterator
    
    def _get_single(self, iterator):
        doc_name = None
        segs = []
        for seg in iterator:
            if seg.doc_name != doc_name:
                if doc_name is not None:
                    yield segs
                    segs = []
                doc_name = seg.doc_name
            segs.append(seg)
        if doc_name is not None:
            yield segs
    
    def get(self):
        first_iter = self._get_single(self._first)
        second_iter = self._get_single(self._second)
        first_segs, second_segs = first_iter.next(), second_iter.next()
        while len(first_segs) > 0 and len(second_segs) > 0:
            first_name = first_segs[0].doc_name
            second_name = second_segs[0].doc_name
            res = cmp(first_name, second_name)
            if res < 0:  # skip first segments
                first_segs = first_iter.next()
            elif res > 0:  # skip second segments
                second_segs = second_iter.next()
            else:
                yield (first_segs, second_segs)
                first_segs, second_segs = first_iter.next(), second_iter.next()
