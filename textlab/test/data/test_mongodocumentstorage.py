from textlab.data.mongodocumentstorage import MongoDocumentStorage
from textlab.test.data.test_documentstorage import DocumentStorageTest


class MongoDocumentStorageTest(DocumentStorageTest):
    '''Reuse DocumentStorageTest cases by overriding how
    empty storage instance is created.'''
    
    def test_test(self):
        '''Test that confirms that the test uses correct type of storage.'''
        storage = self.storage()
        self.assertIsInstance(storage, MongoDocumentStorage)
    
    def emptystorage(self):
        storage = MongoDocumentStorage('test_db')
        storage.delete_all(u'')
        return storage