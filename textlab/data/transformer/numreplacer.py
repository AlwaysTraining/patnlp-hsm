import re

class NumReplacer(object):
    '''Simple preprocessor/transformer that replaces certain characters in text with tahs to make it 
    easier to capture number/punctuation related patterns in plain text.'''
    
    def __init__(self, *args, **kwargs):
        self._patterns = [(re.compile('[0-9]'), '0')] # replace all digits with 0
    
    def fit(self, X):
        return [self._process(x) for x in X]
    
    def fit_transform(self, X):
        return self.fit(X)
    
    def partial_fit(self, X):
        return self.fit(X)
    
    def transform(self, X):
        return self.fit(X)
    
    def _process(self, sentence):
        sentence = sentence.lower()
        for pattern, substitution in self._patterns:
            sentence = pattern.sub(substitution, sentence)
        return sentence
