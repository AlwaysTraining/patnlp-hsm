'''
Script for importing etsa visists.
'''
from hsm.data.importer.etsa import EtsaVisitImporter
from hsm.data.mongodocumentstorage import MongoDocumentStorage
from hsm.data.mongosegmentstorage import MongoSegmentStorage

if __name__ == '__main__':
    docstorage = MongoDocumentStorage()
    segstorage = MongoSegmentStorage()
    importer = EtsaVisitImporter(
                    host = u'127.0.0.1',
                    port = 3306,
                    user = u'etsad',
                    passwd = u'',
                    db = u'work',
                    table_name = u'events',
                    name_prefix = u'etsa',
                    documentstorage = docstorage,
                    segmentstorage = segstorage)
    importer.import_data()
