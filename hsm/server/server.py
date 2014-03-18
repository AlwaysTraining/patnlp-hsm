import cherrypy
import jinja2
import json
import os

from hsm.configuration import config, CONF_FILE_PATH, DICTIONARY_PATH, LDA_PATH
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
from hsm.data.mongosettingsstorage import MongoSettingsStorage
from hsm.server.clustererserver import ClustererServer
from hsm.server.filterserver import FilterServer
from hsm.server.util import mimetype


TEMPLATE_PATH = os.path.join(config.get('/', 'tools.staticdir.root'), 'templates')
loader = jinja2.FileSystemLoader(TEMPLATE_PATH)
env = jinja2.Environment(loader=loader)

class Server(object):
    
    def __init__(self, segstorage, docstorage):
        self._segstorage = segstorage
        self._docstorage = docstorage

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('index.html')
    
    @cherrypy.expose
    @mimetype('application/hsm')
    def dictionaries(self):
        '''Return a list of existing dictionaries.'''
        names = [name for name in os.listdir(DICTIONARY_PATH) if not name.endswith('.txt')]
        return json.dumps(names)
    
    @cherrypy.expose
    @mimetype('application/hsm')
    def ldamodels(self):
        names = [name for name in os.listdir(LDA_PATH) if not name.endswith('.txt')]
        return json.dumps(names)
                

def hsm_root():
    segstorage = MongoSegmentStorage()
    docstorage = MongoDocumentStorage()
    setstorage = MongoSettingsStorage()
    
    root = Server(segstorage, docstorage)
    root.filter = FilterServer(segstorage, docstorage, setstorage)
    root.clusterer = ClustererServer(segstorage, docstorage, setstorage)

    return root

if __name__ == '__main__':
    cherrypy.quickstart(hsm_root(), '', CONF_FILE_PATH)


