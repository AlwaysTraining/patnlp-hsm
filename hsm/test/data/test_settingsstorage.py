import unittest

import hsm
from hsm.data.settingsstorage import SettingsStorage


class SettingsStorageTest(unittest.TestCase):

    def test_save(self):
        storage = self.storage()
        storage.save('tool number two', self.settings())
        self.assertEqual(storage.load('tool number two'), self.settings())
    
    def test_delete(self):
        storage = self.storage()
        storage.delete('tool number one')
        self.assertRaises(KeyError, storage.load, 'tool number one')
    
    def test_load(self):
        storage = self.storage()
        settings = storage.load('tool number one')
        self.assertEqual(settings, self.settings())
    
    def test_list(self):
        storage = self.storage()
        storage.save('prefix:one', {})
        storage.save('prefix:two', {})
        storage.save('anotherprefix:one', {})
        self.assertEqual(storage.list('prefix:'), ['prefix:one', 'prefix:two'])
    
    def test_load_nonexistent(self):
        self.assertRaises(KeyError, self.storage().load, 'this key does not exist')
    
    def settings(self):
        return {'option1': 'something', 'option2': 'something else'}
    
    def emptystorage(self):
        return SettingsStorage()
    
    def storage(self):
        storage = self.emptystorage()
        storage.save('tool number one', self.settings())
        return storage
