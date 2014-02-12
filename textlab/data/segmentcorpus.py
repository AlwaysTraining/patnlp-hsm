from gensim.interfaces import CorpusABC
from textlab.data.transformer.ngramtransformer import NgramTransformer

class SegmentCorpus(CorpusABC):
    '''Implementation of gensim corpus interface that
    makes it possible to use segments as a gensim corpora.
    '''
    
    def __init__(self, segment_name, dictionary, segmentstorage):
        self._segment_name = segment_name
        self._dictionary = dictionary
        self._segstorage = segmentstorage
        
        n = len(dictionary[dictionary.keys().__iter__().next()])
        self._transformer = NgramTransformer(n)

    def __iter__(self):
        for segment in self._segstorage.load_iterator(name=self._segment_name):
            yield self._dictionary.doc2bow(self._transformer.transform([segment.value])[0])
    
    def __len__(self):
        return self._segstorage.counts()[self._segment_name]
    
    def save(self, fname):
        raise NotImplementedError('This corpus does not support saving as it is merely a read-only interface to a combined MongoDb-backed database.')
    