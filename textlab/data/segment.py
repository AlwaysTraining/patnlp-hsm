
class Segment(object):
    '''Segment denotes a part of a text.
    
    It references a document given by `doc_name` from characters `start` to `end` (excluded).
    Segment has a `value` that corresponds to the referenced positions in the document.
    
    The `name` can be anything as long as it describes the segment. The preferred method of naming
    segments is hierarchial. For example, in case of named entities, you should name segments
    describing them as ne:per, ne:loc, ne:org etc. So it would be easy to search fo all entities using
    a query ne:* for example.
    '''
    
    def __init__(self, name, value, document, start, end, doc_name=None, doc_len=None):
        '''Construct a new segment.
        Arguments:
        name - the name of the segment, such as `word`.
        value - the value reporesnted by the segment.
        document - the document instance the segment is created on.
        start - the first character in the document where the segment starts.
        end - the last+1 character in the document where the segment is ends.
        
        doc_name - the document name, in case document is `None`.
        doc_len - the document size, in case document is `None`.
        
        Note that `doc_name` and `doc_len` should be used only when a instance to document is not available.
        '''
        self.name = name
        self.value = value
        if document is None:
            self.doc_name = doc_name
            self.doc_len = doc_len
        else:
            self.doc_name = document.name
            self.doc_len = len(document.text)
        self.start = start
        self.end = end

    @staticmethod
    def from_dict(dictionary):
        return Segment(dictionary['name'],
                       dictionary['value'],
                       None,
                       dictionary['start'],
                       dictionary['end'],
                       dictionary['doc_name'],
                       dictionary['doc_len'])

    @staticmethod
    def to_dict(segment):
        return {'name': segment.name,
                'value': segment.value,
                'start': segment.start,
                'end': segment.end,
                'doc_name': segment.doc_name,
                'doc_len': segment.doc_len}

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        assert isinstance(name, unicode)
        self._name = name
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        assert isinstance(value, unicode)
        self._value = value
        
    @property
    def doc_name(self):
        return self._doc_name
    
    @doc_name.setter
    def doc_name(self, doc_name):
        assert isinstance(doc_name, unicode)
        self._doc_name = doc_name
    
    @property
    def doc_len(self):
        return self._doc_len
    
    @doc_len.setter
    def doc_len(self, doc_len):
        assert doc_len >= 0
        self._doc_len = doc_len
    
    @property
    def start(self):
        return self._start
    
    @start.setter
    def start(self, start):
        assert isinstance(start, int)
        assert start >= 0
        assert start <= self.doc_len
        self._start = start
        
    @property
    def end(self):
        return self._end
    
    @end.setter
    def end(self, end):
        assert isinstance(end, int)
        assert self.start < end
        assert end <= self.doc_len
        self._end = end

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __cmp__(self, other):
        first = (self.doc_name, self.name, self.start, self.end, self.value)
        second = (other.doc_name, other.name, other.start, other.end, other.value)
        return cmp(first, second)
    
    def __hash__(self):
        return self.doc_name.__hash__() ^ self.name.__hash__() ^ self.start ^ self.end
    
    def __str__(self):
        return u'{0}:{1}[{2},{3})={4}'.format(self.doc_name, self.name, self.start, self.end, self.value)
    
    def __repr__(self):
        return u'{0}:{1}:[{2},{3})'.format(self.doc_name, self.name, self.start, self.end)
    
