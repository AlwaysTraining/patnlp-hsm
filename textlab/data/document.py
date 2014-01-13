
class Document(object):
    '''Document is a piece of unicode text with metadata.'''
    
    def __init__(self, name, text, metadata=None):
        self.name = name
        self.text = text
        if metadata is None:
            metadata = {}
        self.metadata = metadata

    @staticmethod
    def from_dict(dictionary):
        return Document(dictionary['name'],
                        dictionary['text'],
                        dictionary['metadata'])
    
    @staticmethod
    def to_dict(document):
        return {'name': document.name,
                'text': document.text,
                'metadata': document.metadata}

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        assert isinstance(name, unicode)
        self._name = name

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, text):
        assert isinstance(text, unicode)
        self._text = text
    
    @property
    def metadata(self):
        return self._metadata
    
    @metadata.setter
    def metadata(self, metadata):
        assert isinstance(metadata, dict)
        self._metadata = metadata

    def __eq__(self, other):
        return self.name == other.name and self.text == other.text and self.metadata == other.metadata
    
    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return self.name

    def __repr__(self):
        return object.__repr__(self) + ':' + str(self)

