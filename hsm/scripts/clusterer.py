'''
Shell script for clustering full database given
a model with some annotated labels for training.
'''

import argparse
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
from sklearn.cross_validation import cross_val_score
import logging
import os
import sys
from pprint import pprint

from hsm.configuration import DICTIONARY_PATH, LDA_PATH
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
from hsm.data.mongosettingsstorage import MongoSettingsStorage
from hsm.data.transformer.ngramtransformer import NgramTransformer
from hsm.server.clustererserver import encode_name
from hsm.tools.clusterer import DICTIONARY, LDA_MODEL, SEGMENT_NAME, Clusterer
from hsm.data.clusterer.csvexporter import CsvExporter


logger = logging.getLogger('clusterer script')
logger.setLevel(logging.DEBUG)

def load_next_n(iterator, n=500):
    segments = []
    for i in range(n):
        try:
            segments.append(iterator.next())
        except StopIteration:
            break
    return segments

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
    
    # TODO: implement get_params and set_params for clusterer tool to allow cross-validation for better score estimation
    logger.info('Evaluating score on training data')
    score = clusterer.score(texts, labels, **kwargs)
    logger.info('Score is {0}'.format(score))
    
    exporter = CsvExporter(segstorage, docstorage, args.clustermodel, sys.stdout)
    
    logger.info(u'Classifying segments with name {0}'.format(settings[SEGMENT_NAME]))
    iter = segstorage.load_iterator(name=settings[SEGMENT_NAME])
    segments = load_next_n(iter)
    while len(texts) > 0:
        texts = [s.value for s in segments]
        labels = clusterer.predict(texts, **kwargs)
        exporter.export(segments, labels, [score] * len(segments))
        segments = load_next_n(iter)
    exporter.close()
    logger.info('Completed successfully!\n')
