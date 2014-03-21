from copy import deepcopy


class PrefixMap(object):
    '''Map designed to store and query unique objects by prefixes.'''
    
    def __init__(self, othermap=None):
        '''If `othermap` is none, construct a copy. Otherwise
        initialize an empty instance.'''
        if othermap is not None:
            assert isinstance(othermap, PrefixMap)
            self._map = deepcopy(othermap._map)
        self._map = dict()
    
    def add(self, name, value):
        '''Add (name, value) pair to the instance.'''
        assert isinstance(name, unicode)
        for key in prefixes(name):
            if key not in self._map:
                self._map[key] = set()
            self._map[key].add(value)
    
    def get(self, prefix):
        '''Get a generator for all values matching given `prefix` name.'''
        assert isinstance(prefix, unicode)
        values = set()
        if prefix in self._map:
            for value in self._map[prefix]:
                values.add(value)
        return values
        
    
    def delete(self, prefix, value):
        '''Delete a specified value for all elements with name matching given `prefix`.'''
        assert isinstance(prefix, unicode)
        for key in prefixes(prefix):
            if key in self._map:
                self._map[key].remove(value)
                if len(self._map[key]) == 0:
                    del self._map[key]

def prefixes(string):
    for n in range(len(string) + 1):
        yield string[:n]
