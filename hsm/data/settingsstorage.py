'''Storage for storing tool settings.'''

class SettingsStorage(object):
    
    def __init__(self):
        self._data = dict()
    
    def list(self, keyprefix):
        keys = []
        for key in self._data:
            if key.startswith(keyprefix):
                keys.append(key)
        return list(sorted(keys))
    
    def load(self, key):
        return self._data[key]
    
    def save(self, key, settings):
        self._data[key] = settings
    
    def delete(self, key):
        del self._data[key]
