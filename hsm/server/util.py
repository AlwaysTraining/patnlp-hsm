'''Various utilities for serving purposes.'''

import cherrypy

def mimetype(giventype):
    '''Mime type decorator for cherrypy.'''
    def decorate(func):
        def wrapper(*args, **kwargs):
            cherrypy.response.headers['Content-Type'] = giventype
            return func(*args, **kwargs)
        return wrapper
    return decorate