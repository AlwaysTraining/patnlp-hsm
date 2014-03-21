import unittest

import hsm
from hsm.data.transformer.ngramtransformer import NgramTransformer


class NgramTransformerTest(unittest.TestCase):
    
    def test_simple(self):
        document = u'Tere'
        expected = [u'te', u'er', 're']
        transformer = NgramTransformer(2)
        self.assertEqual(transformer.transform([document]), [expected])
        
    def test_digit_replacement(self):
        document = u'RR 120/90'
        expected = [u'rr 0', u'r 00', u' 000', u'000/', u'00/0', u'0/00']
        transformer = NgramTransformer(4)
        self.assertEqual(transformer.transform([document]), [expected])
