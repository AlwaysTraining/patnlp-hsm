'''
Shell script for clustering full database given
a model with some annotated labels for training.
'''

import argparse
import os
import logging

from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from textlab.configuration import DICTIONARY_PATH, LDA_PATH
from textlab.data.mongodocumentstorage import MongoDocumentStorage
from textlab.data.mongosegmentstorage import MongoSegmentStorage
from textlab.data.mongosettingsstorage import MongoSettingsStorage
from textlab.data.transformer.ngramtransformer import NgramTransformer
from textlab.server.clustererserver import encode_name
from textlab.tools.clusterer import DICTIONARY, LDA_MODEL, SEGMENT_NAME,\
    Clusterer
from pprint import pprint

logger = logging.getLogger('clusterer script')

def load_next_n(iterator, n=500):
    documents = []
    for i in range(n):
        try:
            documents.append(iterator.next().value)
        except StopIteration:
            break
    return documents

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cluster segments')
    parser.add_argument('clustermodel', type=unicode, help='The clusterer model to use.')
    
    args = parser.parse_args()

    setstorage = MongoSettingsStorage()
    docstorage = MongoDocumentStorage()
    segstorage = MongoSegmentStorage()
    
    logger.info('Loading clusterer model')
    settings = setstorage.load(encode_name(args.clustermodel))
    dictionary = Dictionary.load(os.path.join(DICTIONARY_PATH, settings[DICTIONARY]))
    ngram_size = len(dictionary[0])
    transformer = NgramTransformer(ngram_size)
    ldamodel = LdaModel.load(os.path.join(LDA_PATH, settings[LDA_MODEL]))
    logger.info('Clusterer model loaded!')
    
    kwargs = {'dictionary': dictionary,
                  'ngramtransformer': transformer,
                  'ldamodel': ldamodel,
                  'method': 'LDA'}
    
    logger.info('Fitting clusterer')
    clusterer = Clusterer(settings)
    docs, labels = clusterer.get_training_data()
    clusterer.fit(docs, labels, **kwargs)
    logger.info('Fitting completed!')
    
    logger.info(u'Classifying segments with name {0}'.format(settings[SEGMENT_NAME]))
    iter = segstorage.load_iterator(name=settings[SEGMENT_NAME])
    docs = load_next_n(iter)
    while len(docs) > 0:
        labels = clusterer.predict(docs, **kwargs)
        pprint(zip(docs, labels))
        docs = load_next_n(iter)

