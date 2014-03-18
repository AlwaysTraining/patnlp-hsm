import re

from hsm.data.document import Document
from hsm.data.prefixmap import PrefixMap


class DocumentStorage(object):
    '''Memory document storage.'''
    
    def __init__(self):
        self._docmap = dict()
        self._prefixmap = PrefixMap()
    
    def load(self, name):
        '''Load a single document with given `name`.'''
        assert isinstance(name, unicode)
        if name not in self._docmap:
            raise self._not_exists(name)
        else:
            return self._docmap[name]
    
    def _check_kwargs(self, limit, regex, neg_regex):
        assert limit is None or limit > 0
        if regex is not None:
            assert isinstance(regex, unicode)
        if neg_regex is not None:
            assert isinstance(neg_regex, unicode)
    
    def load_all(self, prefix, limit=None, regex=None, neg_regex=None):
        '''Load all documents matching criteria.
        Keyword arguments:
        regex - if given, then returns only documents matching the regex.
        neg_regx - if given, does not return documents matching the regex.
        limit - if given, returns only number of documents specified by the limit.'''
        assert isinstance(prefix, unicode)
        self._check_kwargs(limit, regex, neg_regex)
        if regex is not None:
            regex = re.compile(regex, re.UNICODE)
        if neg_regex is not None:
            neg_regex = re.compile(neg_regex, re.UNICODE)
        documents = []
        for name in self._prefixmap.get(prefix):
            doc = self._docmap[name]
            # if document does not match regex, then skip it
            if regex is not None and regex.search(doc.text) is None:
                continue
            # if document matches negative regex, then skip it
            if neg_regex is not None and neg_regex.search(doc.text) is not None:
                continue
            documents.append(doc)
            if limit is not None and len(documents) >= limit:
                break
        return documents
    
    def load_iterator(self, prefix, limit=None, regex=None, neg_regex=None):
        return self._iterator(self.load_all(prefix, limit, regex, neg_regex))
    
    def _iterator(self, iterable):
        for elem in iterable:
            yield elem
    
    def save(self, document):
        '''Save the given `document`.'''
        assert isinstance(document, Document)
        if document.name in self._docmap:
            raise self._exists(document.name)
        self._docmap[document.name] = document
        self._prefixmap.add(document.name, document.name)
    
    def save_all(self, documents):
        '''Save all given documents.'''
        for document in documents:
            assert isinstance(document, Document)
            if document.name in self._docmap:
                raise self._exists(document.name)
        for document in documents:
            self.save(document)
    
    def delete(self, name):
        '''Delete a document with given name.'''
        assert isinstance(name, unicode)
        if name not in self._docmap:
            raise self._not_exists(name)
        del self._docmap[name]
        self._prefixmap.delete(name, name)
    
    def delete_all(self, prefix):
        '''Delete all documents with name starting with given `prefix`.
        Returns the number of deleted documents.'''
        assert isinstance(prefix, unicode)
        num_deleted = 0
        for name in self._prefixmap.get(prefix):
            self.delete(name)
            num_deleted += 1
        return num_deleted
    
    def _not_exists(self, name):
        return DocumentNotExistsException('Document `' + name + '` does not exist!')
    
    def _exists(self, name):
        return DocumentExistsException('Document `' + name + '` already stored!')

class DocumentNotExistsException(Exception):
    pass

class DocumentExistsException(Exception):
    pass
