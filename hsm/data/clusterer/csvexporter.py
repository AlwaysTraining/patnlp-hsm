'''Module for converting clustering
data to CSV files.
'''
from itertools import izip
import csv

class CsvExporter(object):
    '''Class for exporting clustering tool results to
       a CSV file that can be consumed by other applications.
    '''
    
    def __init__(self, segstorage, docstorage, name, outfile, ctxt_radius=25):
        '''Initialize CsvExporter instance.
        segstorage - segment storage instance.
        docstorage - document storage instance
        name - the name of the model or the thing to be extracted
        outfile - the file stream the CSV data will be written to
        ctxt_radius - the context size in characters for left and right parts surrounding the content.
        '''
        self._segstorage = segstorage
        self._docstorage = docstorage
        self._ctxt_radius = ctxt_radius
        self._name = name
        self._outfile = outfile
        self._writer = None
    
    def export(self, segments, labels, scores):
        '''Export function can be called consequently many times.
        The first call to the function writes the header of the CSV file, which
        includes everything also in the document metadata.'''
        assert len(segments) == len(labels)
        assert len(labels) == len(scores)
        
        for seg, lab, score in izip(segments, labels, scores):
            doc = self._docstorage.load(seg.doc_name)
            data = dict(doc.metadata.items() +
                    {'content': doc.text[seg.start:seg.end].encode('utf-8'),
                    'value': lab,
                    'confidence': score,
                    'name': self._name,
                    'left_ctxt': doc.text[max(0, seg.start-self._ctxt_radius):seg.start].encode('utf-8'),
                    'right_ctxt': doc.text[seg.end:min(seg.end+self._ctxt_radius, len(doc.text))].encode('utf-8')}.items())
            if self._writer == None:
                keynames = ['name', 'value', 'confidence', 'left_ctxt', 'content', 'right_ctxt'] + list(doc.metadata.keys())
                self._writer = csv.DictWriter(self._outfile, keynames)
                self._writer.writeheader()
            self._writer.writerow(data)
    
    def close(self):
        self._outfile.close()

    