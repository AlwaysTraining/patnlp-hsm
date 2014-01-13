import unittest

from textlab.data.document import Document
from textlab.data.documentstorage import DocumentNotExistsException, \
    DocumentExistsException, DocumentStorage


class DocumentStorageTest(unittest.TestCase):
    
    def test_load(self):
        self.assertEqual(self.storage().load(u'DOCUMENT A'), self.documentA())
    
    def test_load_document_not_exists(self):
        self.assertRaises(DocumentNotExistsException, self.storage().load, u'DOCUMENT D')
    
    def test_load_invalid_key(self):
        self.assertRaises(AssertionError, self.storage().load, 'asciikey')
    
    def test_load_all(self):
        actual = set(self.storage().load_all(u''))
        self.assertEqual(actual, set(self.documents()))
    
    def test_load_all_invalid_key(self):
        self.assertRaises(AssertionError, self.storage().load_all, 'asciikey')
    
    def test_load_limit(self):
        self.assertEqual(len(self.storage().load_all(u'', 1)), 1)
        
    def test_load_invalid_limit(self):
        self.assertRaises(Exception, self.storage().load_all, u'', 0)
    
    def test_load_regex(self):
        docs = set(self.storage().load_all(u'', regex=u'where'))
        self.assertEqual(docs, set([self.documentB(), self.documentC()]))
    
    def test_load_neg_regex(self):
        docs = set(self.storage().load_all(u'', neg_regex=u'where'))
        self.assertEqual(docs, set([self.documentA()]))
    
    def test_load_both_regex(self):
        docs = set(self.storage().load_all(u'', regex=u'where', neg_regex=u'Mexico'))
        self.assertEqual(docs, set([self.documentC()]))
    
    def test_load_iterator(self):
        iterator = self.storage().load_iterator(u'')
        expected = self.documents()
        self.assertNotEqual(iterator, expected)
        for doc in iterator:
            self.assertTrue(doc in expected)
    
    def test_delete(self):
        storage = self.storage()
        storage.delete(u'DOCUMENT A')
        actual = set(storage.load_all(u''))
        expected = set(self.documents()) - set([self.documentA()])
        self.assertEqual(actual, expected)
    
    def test_delete_document_not_exists(self):
        self.assertRaises(DocumentNotExistsException, self.storage().delete, u'DOCUMENT D')
    
    def test_delete_invalid_key(self):
        self.assertRaises(AssertionError, self.storage().delete, 'asciikey')
    
    def test_delete_all(self):
        storage = self.storage()
        num_deleted = storage.delete_all(u'DOCUMENT')
        actual = set(storage.load_all(u''))
        expected = set()
        self.assertEqual(actual, expected)
        self.assertEqual(num_deleted, 3)
    
    def test_delete_all_invalid_key(self):
        self.assertRaises(AssertionError, self.storage().delete_all, 'asciikey')
    
    def test_save(self):
        storage = self.emptystorage()
        storage.save(self.documentA())
        self.assertEqual(storage.load(u'DOCUMENT A'), self.documentA())
    
    def test_document_exists_and_save_fails(self):
        storage = self.emptystorage()
        storage.save(self.documentA())
        self.assertRaises(DocumentExistsException, storage.save, self.documentA())
    
    def test_save_all(self):
        storage = self.emptystorage()
        storage.save_all(self.documents())
        self.assertEqual(set(storage.load_all(u'')), set(self.documents()))
    
    def test_document_exists_and_save_all_fails(self):
        storage = self.emptystorage()
        storage.save(self.documentC())
        self.assertRaises(DocumentExistsException, storage.save_all, self.documents())
    
    def documentA(self):
        return Document(u'DOCUMENT A', u'These are the contents of the first document')
    
    def documentB(self):
        return Document(u'DOCUMENT B', u'Somewhere in the Mexico.')
    
    def documentC(self):
        return Document(u'DOCUMENT C', u'Somewhere nowhere in whateverland.')
    
    def documents(self):
        return [self.documentA(),
                self.documentB(),
                self.documentC()]
    
    def emptystorage(self):
        return DocumentStorage()
    
    def storage(self):
        storage = self.emptystorage()
        storage.save_all(self.documents())
        return storage
