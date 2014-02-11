'''
Module containing functionality for performing classification using active learning.

- must support iterative training of large number of examples.
- must allow adding training examples with labels
- must be able to provide a confidence score for each classified example
- must be able to add training examples from annotated examples using a confidence cutoff treshold.
- must allow PCA plots for known training examples.
'''
from sklearn.feature_extraction.text import HashingVectorizer
import numpy as np

CLASSIFIER_NAME = 'classifier_name'
SEGMENT_NAME = 'segment_name'
OUTPUT_NAME = 'output_name'

class Classifier(object):
    
    def __init__(self, segment_name, *args, **kwargs):
        self._segment_name = segment_name
    
    def fit(self, documents, y):
        pass



class DocumentBow(object):
    
    def __init__(self):
        self._vectorizer = HashingVectorizer(decode_error='ignore',
                                             n_features=2**18,
                                             non_negative=True,
                                             analyzer='char_wb',
                                             ngram_range=(3,3),
                                             dtype=np.int8)