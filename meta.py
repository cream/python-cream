import os
from xml.dom.minidom import parse as parse_xml_file

class MetaDataDB(object): # TODO: Move to cream.meta?

    def __init__(self, path, type=None):

        self.path = path
        self.type = type

        self.by_name = {}
        self.by_hash = {}

        self.scan()


    def scan(self):

        res = MetaData.scan(self.path, self.type)

        for i in res:
            self.by_name[i['name']] = i
            self.by_hash[i['hash']] = i


    def get_by_name(self, name):
        return self.by_name[name]


    def get_by_hash(self, hash):
        return self.by_hash[hash]


class MetaData(dict): # TODO: Move to cream.meta?
    """
    Interface to a module's meta data.

    To get access to meta options, just use it like a normal ``dict``.
    """
    METAFILE_NAME = 'meta.xml'

    def __init__(self, path):

        self['filepath'] = os.path.abspath(path)
        self['path'] = os.path.dirname(self['filepath'])

        self.dom = parse_xml_file(path)

        for n in self.dom.getElementsByTagName('meta')[0].childNodes:
            if n.nodeType == n.ELEMENT_NODE:
                key = n.nodeName
                value = n.childNodes[0].data
                self[key] = value


    @classmethod
    def scan(cls, path, type=None, parent=None):

        path = os.path.abspath(path)
        files = os.listdir(path)
        res = []

        for file in files:
            if os.path.isdir(os.path.join(path, file)):
                res.extend(cls.scan(os.path.join(path, file), type, parent))
            else:
                if file.endswith(cls.METAFILE_NAME):
                    m = cls(os.path.join(path, file))
                    if not type or m['type'] == type:
                        res.append(m)

        return res
