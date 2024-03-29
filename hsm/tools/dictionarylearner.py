from gensim.corpora import Dictionary
import os
import sys

from hsm.configuration import DICTIONARY_PATH
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.transformer.ngramtransformer import NgramTransformer


class DictionaryLearner(object):
    '''Learn a gensim dictionary from all available documents.'''
    
    def __init__(self, n=4):
        '''Initialize a DictionaryLearner instance using vocabulary of ngrams of size `n`.'''
        self._ngram = NgramTransformer(n)
        self._dictionary = Dictionary()
    
    def fit(self, documentstorage, filter_extremes=True):
        '''Fit a dictonary using documents from given documentstorage.'''
        for document in documentstorage.load_iterator(u''):
            text_document = document.text
            ngrams = self._ngram.transform([text_document])
            self._dictionary.add_documents(ngrams)
        if filter_extremes:
            self._dictionary.filter_extremes()

    def get(self):
        return self._dictionary

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        print 'usage: dictionarylearner.py n [dictionary name]'
        sys.exit(0)
    n = int(args[0])
    fname = args[1]
    documentstorage = MongoDocumentStorage()
    learner = DictionaryLearner(n)
    learner.fit(documentstorage)
    dictionary = learner.get()
    path = os.path.join(DICTIONARY_PATH, fname)
    print 'Saving dictionary to <' + path + '>'
    dictionary.save(path)
    dictionary.save_as_text(path + '.txt')
