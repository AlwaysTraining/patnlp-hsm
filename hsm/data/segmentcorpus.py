from gensim.interfaces import CorpusABC
from hsm.data.transformer.ngramtransformer import NgramTransformer


class SegmentCorpus(CorpusABC):
    '''Implementation of gensim corpus interface that
    makes it possible to use segments as a read-only gensim corpora.
    '''
    
    def __init__(self, segment_name, dictionary, segmentstorage, limit=None):
        self._segment_name = segment_name
        self._dictionary = dictionary
        self._segstorage = segmentstorage
        self._limit = limit
        
        n = len(dictionary[dictionary.keys().__iter__().next()])
        self._transformer = NgramTransformer(n)

    def __iter__(self):
        if self._limit is None:
            for segment in self._segstorage.load_iterator(name=self._segment_name):
                yield self._dictionary.doc2bow(self._transformer.transform([segment.value])[0])
        else:
            for idx, segment in enumerate(self._segstorage.load_iterator(name=self._segment_name)):
                if idx >= self._limit:
                    break
                yield self._dictionary.doc2bow(self._transformer.transform([segment.value])[0])
    
    def __len__(self):
        count = self._segstorage.count(self._segment_name)
        if self._limit is not None:
            return min(count, self._limit)
        return count
    
    def save(self, fname):
        raise NotImplementedError('This corpus does not support saving as it is merely a read-only interface to a combined MongoDb-backed database.')
    