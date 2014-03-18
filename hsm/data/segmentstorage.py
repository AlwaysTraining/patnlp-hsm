import re

from hsm.data.prefixmap import PrefixMap
from hsm.data.segment import Segment


class SegmentStorage(object):
    '''Memory segment storage.'''
    
    def __init__(self):
        self._segmap = dict()
        self._segprefixmap = PrefixMap()
    
    def _parse_arguments(self, kwargs):
        name = None
        name_prefix = None
        doc_name = None
        doc_prefix = None
        value_regex = None
        neg_regex = None
        # parse the arguments
        for key in kwargs:
            if key == 'name':
                name = kwargs[key]
            elif key == 'name_prefix':
                name_prefix = kwargs[key]
            elif key == 'doc_name':
                doc_name = kwargs[key]
            elif key == 'doc_prefix':
                doc_prefix = kwargs[key]
            elif key == 'value_regex':
                value_regex = kwargs[key]
            elif key == 'neg_regex':
                neg_regex = kwargs[key]
            else:
                raise Exception('Unknown keyword argument: `' + key + '`')
        # check if they are correct type
        if name is not None:
            assert isinstance(name, unicode)
        if name_prefix is not None:
            assert isinstance(name_prefix, unicode)
        if doc_name is not None:
            assert isinstance(doc_name, unicode)
        if doc_prefix is not None:
            assert isinstance(doc_prefix, unicode)
        if value_regex is not None:
            
            assert isinstance(value_regex, unicode)
        if neg_regex is not None:
            assert isinstance(neg_regex, unicode)
        # make sure at least prefix argument always exist for both segment and document names
        if name is None and name_prefix is None:
            name_prefix = u''
        if doc_name is None and doc_prefix is None:
            doc_prefix = u''
        return name, name_prefix, doc_name, doc_prefix, value_regex, neg_regex
    
    def _parse_limit(self, kwargs):
        if 'limit' in kwargs:
            limit = int(kwargs['limit'])
            if limit < 1:
                raise Exception('Limit must be greater than zero!')
            del kwargs['limit']
            return limit
    
    def _parse_sort(self, kwargs):
        if 'sort' in kwargs:
            sort = bool(kwargs['sort'])
            del kwargs['sort']
            return sort
        return False
    
    def load(self, **kwargs):
        '''Load segments from the storage.
        Keyword arguments:
        name - the name of the segment.
        name_prefix - if given, overrides `name` and loads all segments matching prefix.
        doc_name - the name of the document to load segments for.
        doc_prefix - if given, overrides `doc_name` and filters documents by matching their name with the prefix.
        value_regex - if given, then returns only segments, whose value matches given regular expression.
        neg_regex - if given, discards segments, whose value matches given regular expression.
        limit - if given, limits the number of documents to given limit.
        '''
        return frozenset(self.load_iterator(**kwargs))
    
    def load_iterator(self, **kwargs):
        '''Same as load, but returns the generator for the returned segments.
        Additional keyword arguments:
        sort - default False, otherwise sorts the segments by document name, segment name, segment start, segment end.
        '''
        limit = self._parse_limit(kwargs)
        sort = self._parse_sort(kwargs)
        name, name_prefix, doc_name, doc_prefix, value_regex, neg_regex = self._parse_arguments(kwargs)
        segments = set()
        if name_prefix is not None:
            for seg_name in self._segprefixmap.get(name_prefix):
                if seg_name in self._segmap:
                    segments |= self._segmap[seg_name]
        elif name is not None:
            if name in self._segmap:
                segments |= self._segmap[name]
        else:
            raise Exception('At least `name` or `name_prefix` should be given!')
        if value_regex is not None:
            segments = self._filter_value_regex(segments, value_regex)
        if neg_regex is not None:
            segments = self._filter_neg_regex(segments, neg_regex)
        if doc_prefix is not None:
            generator = self._limit(self._filter_prefix(segments, doc_prefix), limit)
            if sort:
                return sorted(generator)
            else:
                return generator
        elif doc_name is not None:
            generator = self._limit(self._filter_name(segments, doc_name), limit)
            if sort:
                return sorted(generator)
            else:
                return generator
        else:
            raise Exception('At least `doc_name` or `doc_prefix` should be given!')
    
    def _limit(self, segments, limit):
        if limit is not None:
            return set(list(segments)[:limit])
        return segments
    
    def _filter_name(self, segments, doc_name):
        return set(seg for seg in segments if seg.doc_name == doc_name)
    
    def _filter_prefix(self, segments, doc_prefix):
        return set(seg for seg in segments if seg.doc_name.startswith(doc_prefix))
    
    def _filter_value_regex(self, segments, value_regex):
        pattern = re.compile(value_regex, re.UNICODE)
        return set(seg for seg in segments if pattern.search(seg.value) is not None)
    
    def _filter_neg_regex(self, segments, neg_regex):
        pattern = re.compile(neg_regex, re.UNICODE)
        return set(seg for seg in segments if pattern.search(seg.value) is None)
    
    def save(self, segments):
        '''Save given segments to the storage.'''
        for segment in segments:
            assert isinstance(segment, Segment)
        for segment in segments:
            segset = self._segmap.get(segment.name, set())
            segset.add(segment)
            self._segmap[segment.name] = segset
            self._segprefixmap.add(segment.name, segment.name)
    
    def delete(self, **kwargs):
        '''Delete segments from the storage.
        Keyword arguments:
        name - the name of the segment.
        name_prefix - if given, overrides `name` and loads all segments matching prefix.
        doc_name - the name of the document to load segments for.
        doc_prefix - if given, overrides `doc_name` and filters documents by matching their name with the prefix.
        '''
        for segment in self.load(**kwargs):
            self._segmap[segment.name].remove(segment)

    def counts(self, **kwargs):
        '''Get the total counts of the segments.
           Method will return a dictionary, where
              key: segment name
              value: total number of segments with that name
        '''
        segments = self.load(**kwargs)
        counts = {}
        for seg in segments:
            count = counts.get(seg.name, 0)
            counts[seg.name] = count + 1
        return counts
    
    def count(self, key):
        return self.counts().get(key, 0)
    
    def value_counts(self, **kwargs):
        '''Get the total number of values.
        Method will return a dictionary: where
            key: value
            value: total number of such value.
        '''
        segments = self.load(**kwargs)
        counts = {}
        for seg in segments:
            count = counts.get(seg.value, 0)
            counts[seg.value] = count + 1
        return counts
