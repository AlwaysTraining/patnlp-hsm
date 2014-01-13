import pymongo as pm
from textlab.configuration import config
from textlab.data.mongodocumentstorage import get_mongoclient
from textlab.data.settingsstorage import SettingsStorage


class MongoSettingsStorage(SettingsStorage):
    
    def __init__(self, dbkey='db'):
        '''Initialize Mongodb backed settings storage.
        Arguments:
        dbkey - the key to load database name from default configuration.'''
        client = get_mongoclient()
        db = client[config.get('mongodb', dbkey)]
        self._settings = db['settings']
        self._settings.ensure_index([('name', pm.ASCENDING)], unique=True)

    def list(self, prefix):
        return [entry['name'] for entry in self._settings.find({'name': {'$regex': u'^' + prefix}})]

    def load(self, key):
        res = self._settings.find_one({'name': key})
        if res is None:
            raise KeyError('Settings with name ' + key + ' do not exist!')
        return res['data']
    
    def save(self, key, settings):
        assert isinstance(settings, dict)
        self.delete(key)
        self._settings.insert({'name': key, 'data': settings})
    
    def delete(self, key):
        self._settings.remove({'name': key})
