'''
Shell script for clustering full database given
a model with some annotated labels for training.
'''

import argparse
import logging
import os

from hsm import Dictionary, LdaModel, pprint
from hsm.configuration import DICTIONARY_PATH, LDA_PATH
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
from hsm.data.mongosettingsstorage import MongoSettingsStorage
from hsm.data.transformer.ngramtransformer import NgramTransformer
from hsm.server.clustererserver import encode_name
from hsm.tools.clusterer import DICTIONARY, LDA_MODEL, SEGMENT_NAME, Clusterer


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
    texts, labels = clusterer.get_training_data()
    clusterer.fit(texts, labels, **kwargs)
    logger.info('Fitting completed!')
    
    logger.info(u'Classifying segments with name {0}'.format(settings[SEGMENT_NAME]))
    iter = segstorage.load_iterator(name=settings[SEGMENT_NAME])
    texts = load_next_n(iter)
    while len(texts) > 0:
        labels = clusterer.predict(texts, **kwargs)
        pprint(zip(texts, labels))
        texts = load_next_n(iter)

