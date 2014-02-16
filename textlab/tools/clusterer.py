'''
Module for clusterer tool.
'''
from sklearn.manifold import LocallyLinearEmbedding
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import logging
from sklearn.manifold.isomap import Isomap
from sklearn.decomposition import pca, nmf
from sklearn.decomposition.fastica_ import FastICA

CLUSTERER_NAME = 'clusterer_name'
SEGMENT_NAME = 'segment_name'
DICTIONARY = 'dictionary'
LDA_MODEL = 'lda_model'

logger = logging.getLogger('clusterertool')

class Clusterer(dict):
    REQUIRED_KEYWORDS = [CLUSTERER_NAME, SEGMENT_NAME, DICTIONARY, LDA_MODEL]
       
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._check_keywords(kwargs)
        self._dvec = None
        self._scaler = None
        self._lle = None
    
    def _check_keywords(self, kwargs):
        for key in kwargs:
            if key not in Clusterer.REQUIRED_KEYWORDS:
                raise Exception(u'Illegal keyword {0}'.format(key))
            elif not isinstance(kwargs[key], unicode):
                raise ValueError(u'Keyword {0} value {1} not unicode type'.format(key, kwargs[key]))
            elif len(kwargs[key]) == 0:
                raise ValueError(u'Keyword {0} value with zero length'.format(key, kwargs[key]))
    
    def fit(self, documents, y=None, **kwargs):
        self._dvec = DictVectorizer(dtype=np.float32, sparse=True)
        self._scaler = MinMaxScaler((-1, 1))
        #self._lle = pca.PCA(whiten=True)
        self._lle = FastICA(2)
        
        # todo: rewrite using pipeline
        X = self._preprocess(documents, kwargs)
        X = [dict(x) for x in X]
        X = self._dvec.fit_transform(X).todense()
        X = self._scaler.fit_transform(X)
        X = self._lle.fit_transform(X)
        return self 
    
    def fit_transform(self, documents, y=None, **kwargs):
        return self.fit(documents, y, **kwargs).transform(documents, **kwargs)
    
    def transform(self, documents, **kwargs):
        X = self._preprocess(documents, kwargs)
        X = [dict(x) for x in X]
        X = self._dvec.transform(X).todense()
        X = self._scaler.transform(X)
        return self._lle.transform(X)
    
    def _load_from_kwargs(self, kwargs):
        ngramtransformer = kwargs['ngramtransformer']
        dictionary = kwargs['dictionary']
        ldamodel = kwargs['ldamodel']
        return ngramtransformer, dictionary, ldamodel
        
    def _check_documents(self, documents):
        for idx, doc in enumerate(documents):
            if not isinstance(doc, unicode):
                raise ValueError(u'Document {0} not unicode!'.format(idx))
    
    def _preprocess(self, documents, kwargs):
        ngramtransformer, dictionary, ldamodel = self._load_from_kwargs(kwargs)
        X = ngramtransformer.transform(documents)
        X = [ldamodel[dictionary.doc2bow(x)] for x in X]
        return X
