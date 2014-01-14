'''Module handling filter tool server part.'''

import cherrypy
import json

from util import mimetype
from itertools import izip
from textlab.tools.filter import Filter, FILTER_NAME


NAME_PREFIX = u'filtertool:'

def encode_name(name):
    return NAME_PREFIX + name

def decode_name(name):
    if name.startswith(NAME_PREFIX):
        return name[len(NAME_PREFIX):]
    raise ValueError('Cannot decode encoded name ' + name)

def convert_boolean(kwargs):
    for key in kwargs:
        if key in Filter.BOOLEAN_KEYWORDS:
            value = kwargs[key]
            if value == u'true':
                kwargs[key] = True
            else:
                kwargs[key] = False
    return kwargs

def remove_missing(kwargs):
    to_remove = set()
    for key in kwargs:
        if key not in Filter.BOOLEAN_KEYWORDS:
            if len(kwargs[key]) == 0:
                to_remove.add(key)
    for key in to_remove:
        del kwargs[key]
    return kwargs

def emphasize_html(segment, docstorage, context_size):
    doc = docstorage.load(segment.doc_name)
    start = max(0, segment.start-context_size)
    end = min(segment.end+context_size, len(doc.text))
    left = doc.text[start:segment.start]
    right = doc.text[segment.end:end]
    middle = doc.text[segment.start:segment.end]
    return u''.join([left, '<b>', middle, '</b>', right])

def segments_html(segs, docstorage, context_size=30):
    htmls = [emphasize_html(seg, docstorage, context_size) for seg in segs]
    return u'<br/>'.join(htmls)

def head(iterable, n):
    elems = []
    for idx, elem in enumerate(iterable):
        if idx >= n:
            return elems
        elems.append(elem)
    return elems

class FilterServer(object):
    
    def __init__(self, segstorage, docstorage, setstorage):
        self._segstorage = segstorage
        self._docstorage= docstorage
        self._setstorage = setstorage

    @cherrypy.expose
    @mimetype('application/json')
    def available_filters(self):
        names = [{'name': decode_name(name), 'id': decode_name(name)} for name in self._setstorage.list(NAME_PREFIX)]
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
    def remove(self, filter_name):
        pass
    
    @cherrypy.expose
    @mimetype('application/json')
    def save_filter(self, **kwargs):
        print kwargs
        kwargs = convert_boolean(kwargs)
        kwargs = remove_missing(kwargs)
        print kwargs
        # check that we can create the filter
        try:
            filt = Filter(**kwargs)
            settings = dict(filt)
            self._setstorage.save(encode_name(settings[FILTER_NAME]), settings)
            return json.dumps({'result': 'OK'})
        except Exception, e:
            return json.dumps({'result': 'FAIL', 'error': str(e)})
    
    @cherrypy.expose
    def rename_filter(self, old_name, new_name):
        pass
    
    @cherrypy.expose
    def preview_sample(self, name):
        try:
            settings = self._setstorage.load(encode_name(name))
            filt = Filter(**settings)
            limit = 150
            context_size = 50
            
            output_segs = head(filt.filter(self._segstorage, self._docstorage), limit)
            output = segments_html(output_segs, self._docstorage, context_size)
            
            data = {'source': u'',
                    'container': u'',
                    'mixin': u'',
                    'output': output}
            
            return json.dumps({'result': 'OK', 'data': data})
        except Exception, e:
            return json.dumps({'result': 'FAIL', 'error': str(e)})
    
    @cherrypy.expose
    def apply_filter(self, name):
        try:
            settings = self._setstorage.load(encode_name(name))
            filt = Filter(**settings)
            filt.apply(self._segstorage, self._docstorage)
        except Exception, e:
            return json.dumps({'result': 'FAIL', 'error': str(e)})

    @cherrypy.expose
    def filter_dependency_graph(self):
        pass
