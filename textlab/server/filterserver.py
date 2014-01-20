'''Module handling filter tool server part.'''

import cherrypy
import json
import re

from util import mimetype
from itertools import izip
from pprint import pprint
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
    return (left, middle, right)

def segments_html(segs, docstorage, context_size=30):
    htmls = [emphasize_html(seg, docstorage, context_size) for seg in segs]
    htmls.sort(key=lambda (left, middle, right): (middle, left[:-5:-1]))
    htmls = [left + u'<b>' + middle + '</b>' + right for left, middle, right in htmls]
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
    def index(self, **kwargs):
        pprint (kwargs)
        if 'name' in kwargs:
            regex = kwargs['name']
            return self.get_filters(regex)

    def get_filters(self, regex):
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
    @mimetype('application/json')
    def graph(self):
        names = []
        nodes = []
        links = []
        for name in self._setstorage.list(NAME_PREFIX):
            settings = self._setstorage.load(name)
            filter_name = decode_name(name)
            output_name = settings['output_name']
            segment_name = settings['segment_name']
            if filter_name not in names:
                nodes.append({'name': filter_name, 'group': 1})
                names.append(filter_name)
            if segment_name not in names:
                nodes.append({'name': segment_name, 'group': 2})
                names.append(segment_name)
            if output_name not in names:
                nodes.append({'name': output_name, 'group': 3})
                names.append(output_name)
            
            links.append({'source': names.index(segment_name), 'target': names.index(filter_name), 'value': 1})
            links.append({'source': names.index(filter_name), 'target': names.index(output_name), 'value': 1})
            
        return json.dumps({'nodes': list(nodes), 'links': list(links)})
