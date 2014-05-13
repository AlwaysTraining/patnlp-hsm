'''
Script for importing etsa visists.
'''
from hsm.data.importer.etsa import EtsaVisitImporter
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage
import sys

def usage():
    print 'python import_etsa.py [port] [passwd]'
    sys.exit()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        usage()
    port, passwd = args
    port = int(port)
    docstorage = MongoDocumentStorage()
    segstorage = MongoSegmentStorage()
    importer = EtsaVisitImporter(
                    host = u'127.0.0.1',
                    port = port,
                    user = u'etsad',
                    passwd = args[0],
                    db = u'work',
                    table_name = u'events',
                    name_prefix = u'etsa',
                    documentstorage = docstorage,
                    segmentstorage = segstorage)
    importer.import_data()
