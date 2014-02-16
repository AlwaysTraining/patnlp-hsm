import cherrypy
import json
import re
import os

from pprint import pprint
from textlab.tools.clusterer import CLUSTERER_NAME, Clusterer, SEGMENT_NAME,\
    DICTIONARY, LDA_MODEL
from util import mimetype
from gensim.corpora.dictionary import Dictionary
from textlab.configuration import DICTIONARY_PATH, LDA_PATH
from gensim.models.ldamodel import LdaModel
from textlab.data.transformer.ngramtransformer import NgramTransformer

NAME_PREFIX = u'clusterertool:'

def encode_name(name):
    return NAME_PREFIX + name

def decode_name(name):
    if name.startswith(NAME_PREFIX):
        return name[len(NAME_PREFIX):]
    raise ValueError('Cannot decode encoded name ' + name)

class ClustererServer(object):
    '''Clustering tool service.'''
    
    def __init__(self, segstorage, docstorage, setstorage):
        self._segstorage = segstorage
        self._docstorage= docstorage
        self._setstorage = setstorage
    
    @cherrypy.expose
    @mimetype('application/json')
    def index(self, **kwargs):
        pprint (kwargs)
        if 'name' in kwargs:
            regex = kwargs['name']
            return self.get_clusterers(regex)

    def get_clusterers(self, regex):
        regex = regex.replace('*', '.*')
        p = re.compile(regex, re.UNICODE)
        names = []
        for name in self._setstorage.list(NAME_PREFIX):
            name = decode_name(name)
            if p.search(name) is not None:
                names.append({'name': name, 'id': name})
        return json.dumps(names)
    
    @cherrypy.expose
    @mimetype('application/json')
    def load(self, name):
        try:
            settings = self._setstorage.load(encode_name(name))
            return json.dumps({'result': 'OK', 'data': settings})
        except Exception, e:
            return json.dumps({'result': 'FAIL', 'error': str(e)})

    @cherrypy.expose
    @mimetype('application/json')
    def save(self, **kwargs):
        # check that we can create the filter
        try:
            clusterer = Clusterer(**kwargs)
            settings = dict(clusterer)
            self._setstorage.save(encode_name(settings[CLUSTERER_NAME]), settings)
            return json.dumps({'result': 'OK'})
        except Exception, e:
            return json.dumps({'result': 'FAIL', 'error': str(e)})

    @cherrypy.expose
    @mimetype('application/json')
    def update(self, name, n=500):
        settings = self._setstorage.load(encode_name(name))
        clusterer = Clusterer(settings)
        
        # load the models
        dictionary = Dictionary.load(os.path.join(DICTIONARY_PATH, settings[DICTIONARY]))
        ngram_size = len(dictionary[0])
        transformer = NgramTransformer(ngram_size)
        ldamodel = LdaModel.load(os.path.join(LDA_PATH, settings[LDA_MODEL]))
        
        # get the input
        segments = self._segstorage.load(name=settings[SEGMENT_NAME], limit=int(n))
        documents = [s.value for s in segments]
        
        # prepare args
        kwargs = {'dictionary': dictionary,
                  'ngramtransformer': transformer,
                  'ldamodel': ldamodel}
        Xt = clusterer.fit_transform(documents, **kwargs)
        data = [{'x': e[0][0], 'y': e[0][1], 'document': e[1]} for e in zip(Xt.tolist(), documents)]
        return json.dumps({'result': 'OK',
                           'data': data})


