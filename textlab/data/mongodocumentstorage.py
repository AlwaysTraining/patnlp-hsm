import pymongo as pm
import re
from textlab.configuration import config
from textlab.data.document import Document
from textlab.data.documentstorage import DocumentStorage


def get_mongoclient():
    return pm.MongoClient(
            config.get('mongodb', 'host'),
            config.getint('mongodb', 'port'))
    
class MongoDocumentStorage(DocumentStorage):
    
    def __init__(self, dbkey='db'):
        '''Initialize Mongodb backed document storage.
        Arguments:
        dbkey - the key to load database name from default configuration.'''
        client = get_mongoclient()
        db = client[config.get('mongodb', dbkey)]
        self._documents = db['documents']
        self._documents.ensure_index([('name', pm.ASCENDING)], unique=True)
    
    def load(self, name):
        '''Load a single document with given `name`.'''
        assert isinstance(name, unicode)
        results = list(self._documents.find({'name': name}))
        if len(results) == 0:
            raise self._not_exists(name)
        return Document.from_dict(results[0])
    
    def load_all(self, prefix, limit=None, regex=None, neg_regex=None):
        return list(self.load_iterator(prefix, limit, regex, neg_regex))
    
    def load_iterator(self, prefix, limit=None, regex=None, neg_regex=None):
        '''Load all documents matching criteria.
        Keyword arguments:
        regex - if given, then returns only documents matching the regex.
        neg_regx - if given, does not return documents matching the regex.
        limit - if given, returns only number of documents specified by the limit.'''
        assert isinstance(prefix, unicode)
        self._check_kwargs(limit, regex, neg_regex)
        query = {'name': {'$regex': '^' + prefix}}
        regex_query = {}
        if regex is not None:
            regex_query['$regex'] = re.compile(regex, re.UNICODE)
        if neg_regex is not None:
            regex_query['$not'] = re.compile(neg_regex, re.UNICODE)
        if regex is not None or neg_regex is not None:
            query['text'] = regex_query
        if limit is None:
            return self._iterator(self._documents.find(query))
        else:
            return self._iterator(self._documents.find(query).limit(limit))
    
    def _iterator(self, cursor):
        for entry in cursor:
            yield Document.from_dict(entry)
    
    def save(self, document):
        '''Save the given `document`.'''
        assert isinstance(document, Document)
        existing = list(self._documents.find({'name': document.name}))
        if len(existing) > 0:
            raise self._exists(document.name)
        self._documents.insert(Document.to_dict(document))
    
    def save_all(self, documents):
        '''Save all given documents.'''
        for document in documents:
            self.save(document)
    
    def delete(self, name):
        '''Delete a document with given name.'''
        assert isinstance(name, unicode)
        if len(list(self._documents.find({'name': name}))) == 0:
            raise self._not_exists(name)
        self._documents.remove({'name': name})
    
    def delete_all(self, prefix):
        '''Delete all documents with name starting with given `prefix`.
        Returns the number of deleted documents.'''
        assert isinstance(prefix, unicode)
        result = self._documents.remove({'name': {'$regex': '^' + prefix}})
        return result['n']
