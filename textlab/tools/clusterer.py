'''
Module for clusterer tool.
'''
from sklearn.manifold import LocallyLinearEmbedding
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold.isomap import Isomap
from sklearn.decomposition.pca import PCA
from sklearn.decomposition.fastica_ import FastICA
from sklearn.lda import LDA
from sklearn.preprocessing import LabelEncoder

import numpy as np
import logging

CLUSTERER_NAME = 'clusterer_name'
SEGMENT_NAME = 'segment_name'
DICTIONARY = 'dictionary'
LDA_MODEL = 'lda_model'
LABEL_DATA = 'label_data'

logger = logging.getLogger('clusterertool')

class Clusterer(dict):
    REQUIRED_KEYWORDS = [CLUSTERER_NAME, SEGMENT_NAME, DICTIONARY, LDA_MODEL]
       
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._check_keywords(kwargs)
        self._dvec = None
        self._scaler = None
        self._dimreduction = None
    
    def _check_keywords(self, kwargs):
        for key in kwargs:
            if key not in Clusterer.REQUIRED_KEYWORDS:
                raise Exception(u'Illegal keyword {0}'.format(key))
            elif not isinstance(kwargs[key], unicode):
                raise ValueError(u'Keyword {0} value {1} not unicode type'.format(key, kwargs[key]))
            elif len(kwargs[key]) == 0:
                raise ValueError(u'Keyword {0} value with zero length'.format(key, kwargs[key]))
        if LABEL_DATA in kwargs and not isinstance(kwargs[LABEL_DATA], dict):
            raise ValueError('label data must be a dictionary')
    
    def _get_method(self, method):
        if method == 'FastICA':
            return FastICA(2)
        elif method == 'PCA':
            return PCA(2)
        elif method == 'IsoMap':
            return Isomap(n_components=2)
        elif method == 'LLE':
            return LocallyLinearEmbedding(n_components=2)
        elif method == 'LDA':
            return LDA(n_components=2)
        else:
            raise ValueError('Invalid method {0} for dimensionality reduction.'.format(method))
    
    def fit(self, documents, y=None, **kwargs):
        self._dvec = DictVectorizer(dtype=np.float32, sparse=True)
        self._scaler = MinMaxScaler((-1, 1))
        #self._dimreduction = pca.PCA(whiten=True)
        method = kwargs.get('method', 'FastICA')
        logger.info('Dimensionality reduction method is {0}'.format(method))
        self._dimreduction = self._get_method(method)
        
        # todo: rewrite using pipeline
        X = self._preprocess(documents, kwargs)
        X = [dict(x) for x in X]
        X = self._dvec.fit_transform(X).todense()
        X = self._scaler.fit_transform(X)
        if method == 'LDA':
            y = LabelEncoder().fit_transform(self.assign_labels(documents))
            # select only documents for LDA that have some meaningful labels
            idxs = [i for i in range(len(documents)) if y[i] != u'unknown']
            X = X[idxs, :]
            y = [yy for yy in y if yy != u'unknown']
            X = self._dimreduction.fit_transform(X, y)
        else:
            X = self._dimreduction.fit_transform(X)
        return self 
    
    def fit_transform(self, documents, y=None, **kwargs):
        return self.fit(documents, y, **kwargs).transform(documents, **kwargs)
    
    def transform(self, documents, **kwargs):
        X = self._preprocess(documents, kwargs)
        X = [dict(x) for x in X]
        X = self._dvec.transform(X).todense()
        X = self._scaler.transform(X)
        return self._dimreduction.transform(X)
    
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

    def assign_labels(self, documents):
        '''Given a number of documents, return labels if possible. Label u'unknown' is
        assigned to documents that have no known label.'''
        label_data = self.get(LABEL_DATA, {})
        labels = [label_data.get(self._escape_key_for_mongo(d), u'unknown') for d in documents]
        return labels
    
    def update_labels(self, labels):
        '''Given a dictionary document -> label pairs, update known labels.'''
        label_data = self.get(LABEL_DATA, {})
        for document, label in labels.iteritems():
            document = self._escape_key_for_mongo(document)
            if not isinstance(document, unicode):
                raise ValueError(u'Document with content "{0}" not unicode!'.format(document))
            if not isinstance(label, unicode):
                raise ValueError(u'Document with content "{0}" does not have unicode label "{1}"!'.format(document, label))
            label_data[document] = label
        self[LABEL_DATA] = label_data
    
    def _escape_key_for_mongo(self, key):
        '''Mongo keys must not contain `.` and `$` signs.'''
        return key.replace('.', '__dot__').replace('$', '__dollar__')
    
    def clear_labels(self):
        self[LABEL_DATA] = {}

