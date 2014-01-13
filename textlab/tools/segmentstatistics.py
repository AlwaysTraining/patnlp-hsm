'''
Module for providing basic overview of what types of segments
are available in the system.
'''
import cherrypy
import matplotlib.pyplot as plt
import numpy as np
import tempfile

def mimetype(type):
    def decorate(func):
        def wrapper(*args, **kwargs):
            cherrypy.response.headers['Content-Type'] = type
            return func(*args, **kwargs)
        return wrapper
    return decorate

class SegmentStatistics(object):
    
    def __init__(self, segstorage, docstorage):
        self._segstorage = segstorage
        self._docstorage = docstorage

    def _unicode_kwargs(self, kwargs):
        return dict([(entry[0], unicode(entry[1])) for entry in kwargs.iteritems()])

    @cherrypy.expose
    @mimetype('image/svg+xml')
    def segment_count_plot(self, **kwargs):
        kwargs = self._unicode_kwargs(kwargs) 
        counts = self._segstorage.counts(**kwargs)
        return barplot(counts.iteritems())

    @cherrypy.expose
    def segment_value_plot(self, **kwargs):
        kwargs = self._unicode_kwargs(kwargs) 
        counts = self._segstorage.value_counts(**kwargs)
        return counts

    @cherrypy.expose
    def index(self):
        return 'It works!'

def plot_as_string(plt):
    f = tempfile.NamedTemporaryFile(suffix='.svg')
    plt.savefig(f.name)
    f.seek(0)
    string = f.read()
    f.close()
    return string

def barplot(names, values):
    # sort the data decreasingly from counts
    data = zip(names, values)
    data.sort(key=lambda elem: elem[1])
    names, values = zip(*data)
    # create the plot
    n = len(names)
    y_pos = np.arange(n)
    
    plt.barh(y_pos, values, alpha=0.5, align='center')
    for x, y in zip(values, y_pos):
        plt.text(x, y, str(x))
    plt.yticks(y_pos, names)
    plt.xlabel('Frequency')
    plt.title('Distribution of segment types')
    
    return plot_as_string(plt)

