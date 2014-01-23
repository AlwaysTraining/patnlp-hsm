import os
import sys

sys.path.append('/home/cdata/patnlp-hsm')
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
    cherrypy.engine.start(blocking=False)
    atexit.register(cherrypy.engine.stop)

from textlab.server.server import hsm_root
from textlab.configuration import config, CONF_FILE_PATH

application = cherrypy.Application(hsm_root(), script_name=None, config=CONF_FILE_PATH)

def pplication(environ, start_response):
    status = '200 OK' 
    output = str(environ) + str(start_response)

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

