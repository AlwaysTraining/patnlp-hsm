import unittest

import hsm
from hsm.data.document import Document


class DocumentTest(unittest.TestCase):
    
    def test_construction(self):
        doc = Document(self.name(), self.text(), self.metadata())
        self.assertEqual(doc.name, self.name())
        self.assertEqual(doc.text, self.text())
        self.assertEqual(doc.metadata, self.metadata())

    def test_construction_empty_metadata(self):
        doc = Document(self.name(), self.text())
        self.assertEqual(doc.metadata, {})

    def test_construction_invalid_name(self):
        self.assertRaises(AssertionError, Document, None, self.text(), {})
        
    def test_construction_invalid_text(self):
        self.assertRaises(AssertionError, Document, self.name(), 0, {})
    
    def test_construction_invalid_metadata(self):
        self.assertRaises(AssertionError, Document, self.name(), self.text(), 1)

    def test_from_dict(self):
        A = Document(self.name(), self.text(), self.metadata())
        B = Document.from_dict(self.dictionary())
        self.assertEqual(A, B)

    def test_to_dict(self):
        A = Document(self.name(), self.text(), self.metadata())
        self.assertEqual(Document.to_dict(A), self.dictionary())

    def test_equality(self):
        A = Document(self.name(), self.text(), self.metadata())
        B = Document(self.name(), self.text(), self.metadata())
        self.assertEqual(A, B)
    
    def test_inequality(self):
        A = Document(self.name(), self.text(), {})
        B = Document(self.name(), self.text(), self.metadata())
        self.assertNotEqual(A, B)

    def test_hash(self):
        A = Document(self.name(), self.text())
        B = Document(self.name(), self.text(), {})
        self.assertEqual(set([A]), set([B]))

    def name(self):
        return u'DOCUMENT_1'

    def text(self):
        return u'This is some text'
    
    def metadata(self):
        return {'meta1': 1, 'meta2': 2}
    
    def dictionary(self):
        return {'name': self.name(), 'text': self.text(), 'metadata': self.metadata()}
