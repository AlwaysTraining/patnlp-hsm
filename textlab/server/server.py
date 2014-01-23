import cherrypy
import jinja2
import os

from textlab.configuration import config, CONF_FILE_PATH
from textlab.data.mongodocumentstorage import MongoDocumentStorage
from textlab.data.mongosegmentstorage import MongoSegmentStorage
from textlab.data.mongosettingsstorage import MongoSettingsStorage
from textlab.server.filterserver import FilterServer


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

def hsm_root():
    segstorage = MongoSegmentStorage()
    docstorage = MongoDocumentStorage()
    setstorage = MongoSettingsStorage()
    
    root = Server(segstorage, docstorage)
    root.filter = FilterServer(segstorage, docstorage, setstorage)

    return root

if __name__ == '__main__':
    cherrypy.quickstart(hsm_root(), '', CONF_FILE_PATH)


