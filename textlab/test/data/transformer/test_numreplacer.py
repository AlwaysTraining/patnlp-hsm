import unittest
from textlab.data.transformer.numreplacer import NumReplacer

class NumReplacerTest(unittest.TestCase):
    
    def setUp(self):
        self._replacer = NumReplacer()
    
    def test_digit_replacement(self):
        original = 'is a 0123456789'
        expected = 'is a 0000000000'
        self.assertEqual(self._replacer.transform([original]), [expected])

    def test_lowercase(self):
        original = 'LoWeRcAsE'
        expected = 'lowercase'
        self.assertEqual(self._replacer.transform([original]), [expected])
