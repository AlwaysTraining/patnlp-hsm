from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import logging
import os
import sys

from textlab.configuration import DICTIONARY_PATH, LDA_PATH
from textlab.data.mongosegmentstorage import MongoSegmentStorage
from textlab.data.segmentcorpus import SegmentCorpus


class LdaLearner(object):
    
    def __init__(self, corpus, dictionary, num_topics=500):
        self._corpus = corpus
        self._dictionary = dictionary
        self._num_topics = num_topics
        self._lda = None
    
    def fit(self):
        self._lda = LdaModel(corpus=self._corpus, id2word=self._dictionary, num_topics=self._num_topics, distributed=True)
    
    def get(self):
        return self._lda

def usage():
    print 'usage: ldalearner.py [segment_name] [dictionary_name] [resulting_model_name]'
    sys.exit(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    args = sys.argv[1:]
    
    if len(args) != 3:
        usage()
    
    segment_name = unicode(args[0])
    dict_path = os.path.join(DICTIONARY_PATH, args[1])
    dictionary = Dictionary.load(dict_path)
    
    model_path = os.path.join(LDA_PATH, args[2])
    
    corpus = SegmentCorpus(segment_name, dictionary, MongoSegmentStorage())
    learner = LdaLearner(corpus, dictionary)
    learner.fit()
    
    learner.get().save(model_path)

