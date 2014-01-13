from textlab.data.prefixmap import PrefixMap, prefixes
import unittest

class PrefixesTest(unittest.TestCase):
    
    def test_prefixes_empty(self):
        self.assertEqual(list(prefixes('')), [''])
    
    def test_prefixes(self):
        self.assertEqual(list(prefixes('prefixes')), ['', 'p', 'pr', 'pre', 'pref', 'prefi', 'prefix', 'prefixe', 'prefixes'])


class PrefixMapTest(unittest.TestCase):
    
    def test_exact(self):
        actual = self.actual(u'myvalue1')
        expected = set([1])
        self.assertEqual(actual, expected)
        
    def test_long_prefix(self):
        actual = self.actual(u'myvalue')
        expected = set([1, 2])
        self.assertEqual(actual, expected)
    
    def test_short_prefix(self):
        actual = self.actual(u'my')
        expected = set([1, 2, 3])
        self.assertEqual(actual, expected)
    
    def test_zero_size_prefix(self):
        actual = set(self.map().get(u''))
        expected = set([1, 2, 3, 4])
        self.assertEqual(actual, expected)
    
    def test_get_nonexistent(self):
        actual = set(self.map().get(u'nonexistent'))
        expected = set()
        self.assertEqual(actual, expected)
    
    def test_delete(self):
        m = self.map()
        m.delete(u'myvalue', 1)
        actual = set(m.get(u'myvalue'))
        expected = set([2])
        self.assertEqual(actual, expected)
    
    def test_invalid_add_key(self):
        self.assertRaises(AssertionError, self.map().add, 'asciikey', 1)
    
    def test_invalid_get_key(self):
        self.assertRaises(AssertionError, self.map().get, 'nonexistent')
    
    def test_invalid_delete_key(self):
        self.assertRaises(AssertionError, self.map().delete, 'asciikey', 2)
    
    def actual(self, prefix):
        return set(self.map().get(prefix))
    
    def map(self):
        m = PrefixMap()
        m.add(u'myvalue1', 1)
        m.add(u'myvalue2', 2)
        m.add(u'myothervalue', 3)
        m.add(u'other', 4)
        return m
