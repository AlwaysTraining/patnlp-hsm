import re

import pymongo as pm
from hsm.configuration import config
from hsm.data.mongodocumentstorage import get_mongoclient
from hsm.data.segment import Segment
from hsm.data.segmentstorage import SegmentStorage


class MongoSegmentStorage(SegmentStorage):
    '''Mongodb backed segment storage.'''
    
    def __init__(self, dbkey='db'):
        '''Initialize segment storage.
        Arguments:
        dbkey - the key to load database name from default configuration.'''
        client = get_mongoclient()
        db = client[config.get('mongodb', dbkey)]
        self._segments = db['segments']
        self._segments.ensure_index([('name', pm.ASCENDING)])
        self._segments.ensure_index([('doc_name', pm.ASCENDING)])
        self._segments.ensure_index([('name', pm.ASCENDING), ('doc_name', pm.ASCENDING)])
    
    def _get_query(self, kwargs):
        name, name_prefix, doc_name, doc_prefix, value_regex, neg_regex = self._parse_arguments(kwargs)
        query = {}
        if name_prefix is not None:
            if len(name_prefix) > 0:
                query['name'] = {'$regex': '^' + name_prefix}
        elif name is not None:
            query['name'] = name
        else:
            raise Exception('At least `name` or `name_prefix` should be given!')
        if doc_prefix is not None:
            if len(doc_prefix) > 0:
                query['doc_name'] = {'$regex': '^' + doc_prefix}
        elif doc_name is not None:
            query['doc_name'] = doc_name
        else:
            raise Exception('At least `doc_name` or `doc_prefix` should be given!')
        regex_query = {}
        if value_regex is not None:
            regex_query['$regex'] = re.compile(value_regex, re.UNICODE)
        if neg_regex is not None:
            regex_query['$not'] = re.compile(neg_regex, re.UNICODE)
        if value_regex is not None or neg_regex is not None:
            query['value'] = regex_query
        return query
    
    def load(self, **kwargs):
        '''Load segments from the storage.
        Keyword arguments:
        name - the name of the segment.
        name_prefix - if given, overrides `name` and loads all segments matching prefix.
        doc_name - the name of the document to load segments for.
        doc_prefix - if given, overrides `doc_name` and filters documents by matching their name with the prefix.
        value_regex - if given, then returns only segments, whose value matches given regular expression.
        neg_regex - if given, discards segments, whose value matches given regular expression.
        limit - if given, limits the number of segments to given limit.
        sort - default False, otherwise sorts the segments by document name, segment name, segment start, segment end.
        '''
        return frozenset(self.load_iterator(**kwargs))
    
    def load_iterator(self, **kwargs):
        '''Same as load, but returns the generator for the returned segments
           and sorts the segments by document name, segment name, segment start, segment end.'''
        limit = self._parse_limit(kwargs)
        sort = self._parse_sort(kwargs)
        query = self._get_query(kwargs)
        return self._load_iterator(query, limit, sort)
    
    def _load_iterator(self, query, limit=None, sort=False):
        cursor = self._segments.find(query)
        if sort:
            criteria = [('doc_name', pm.ASCENDING), ('name', pm.ASCENDING),
                         ('start', pm.ASCENDING), ('end', pm.ASCENDING), ('value', pm.ASCENDING)]
            cursor = cursor.sort(criteria)
        if limit is not None:
            cursor = cursor.limit(limit)
        for entry in cursor:
            yield Segment.from_dict(entry)
    
    def save(self, segments):
        '''Save given segments to the storage.'''
        if len(segments) > 0:
            for segment in segments:
                if not isinstance(segment, Segment):
                    print type(segment), Segment
                    raise AssertionError(unicode(segment) + u' is not a segment!')
            self._segments.insert([Segment.to_dict(segment) for segment in segments])
    
    def delete(self, **kwargs):
        '''Delete segments from the storage.
        Keyword arguments:
        name - the name of the segment.
        name_prefix - if given, overrides `name` and loads all segments matching prefix.
        doc_name - the name of the document to load segments for.
        doc_prefix - if given, overrides `doc_name` and filters documents by matching their name with the prefix.
        '''
        query = self._get_query(kwargs)
        self._segments.remove(query)

    def _unpack(self, aggregation):
        result = aggregation['result']
        return dict([(entry['_id'], entry['count']) for entry in result])

    def counts(self, **kwargs):
        query = self._get_query(kwargs)
        counts = self._segments.aggregate([{'$match': query},
                                           {'$group': {'_id': '$name', 'count': {'$sum': 1}}}])
        return self._unpack(counts)
    
    def count(self, key):
        return self._segments.find({'name': key}).count()
    
    def value_counts(self, **kwargs):
        query = self._get_query(kwargs)
        counts = self._segments.aggregate([{'$match': query},
                                           {'$group': {'_id': '$value', 'count': {'$sum': 1}}}])
        return self._unpack(counts)
    