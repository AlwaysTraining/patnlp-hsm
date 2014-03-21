import re


class NgramTransformer(object):
    '''Simple preprocessor/transformer that replaces certain characters in text with tahs to make it 
    easier to capture number/punctuation related patterns in plain text.'''
    
    def __init__(self, n=4, *args, **kwargs):
        '''Keyword arguments:
        n - the ngram size.
        '''
        self._n = n
        self._patterns = [(re.compile('[0-9]'), '0')] # replace all digits with 0
    
    def fit(self, documents):
        return [self._process(document) for document in documents]
    
    def fit_transform(self, documents):
        return self.fit(documents)
    
    def partial_fit(self, documents):
        return self.fit(documents)
    
    def transform(self, documents):
        return self.fit(documents)
    
    def _process(self, document):
        document = document.lower()
        for pattern, substitution in self._patterns:
            document = pattern.sub(substitution, document)
        return self._ngrams(document)

    def _ngrams(self, document):
        return [document[i:i+self._n] for i in range(len(document) - self._n + 1)]
