from hsm.data.mongosettingsstorage import MongoSettingsStorage
from hsm.test.data.test_settingsstorage import SettingsStorageTest


class MongoSettingsStorageTest(SettingsStorageTest):
    
    def emptystorage(self):
        storage = MongoSettingsStorage('test_db')
        storage._settings.remove()
        return storage
