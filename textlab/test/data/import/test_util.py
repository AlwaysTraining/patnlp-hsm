import unittest

from data.importer.util import compute_starts, compute_ends


class ComputeStartsEndsTest(unittest.TestCase):
    '''Tests for various functions in etsa importer module.'''
    
    def test_zero_starts(self):
        self.assertEqual(compute_starts([]), [])
        self.assertEqual(compute_starts([], sep=u'   '), [])
    
    def test_zero_ends(self):
        self.assertEqual(compute_ends([]), [])
        self.assertEqual(compute_ends([], sep=u'   '), [])
        
    def test_starts(self):
        self.assertEqual(compute_starts(self.tokens(), self.sep()), self.starts())
        
    def test_ends(self):
        self.assertEqual(compute_ends(self.tokens(), self.sep()), self.ends())
    
    def tokens(self):
        return ['yks', 'kaks', 'kolm']
    
    def sep(self):
        return 'sep'
    
    def starts(self):
        return [0, 6, 13]
    
    def ends(self):
        return [3, 10, 17]
