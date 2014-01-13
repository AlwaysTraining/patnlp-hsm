from textlab.data.mongosegmentstorage import MongoSegmentStorage
from textlab.test.data.test_segmentstorage import SegmentStorageTest


class MongoSegmentStorageTest(SegmentStorageTest):
    '''Reuse SegmentStorageTest cases by overriding how
    empty storage instance is created.'''
    
    def test_test(self):
        '''Test that confirms that the test uses correct type of storage.'''
        storage = self.storage()
        self.assertIsInstance(storage, MongoSegmentStorage)
    
    def emptystorage(self):
        storage = MongoSegmentStorage('test_db')
        storage.delete()
        return storage
