import os
from gpyconf.backends import Backend
try:
    from xml.etree import cElementTree as elementtree
except ImportError:
    from xml.etree import  ElementTree as elementtree

from cream.util.string import slugify

STATIC_OPTIONS_FILE       = 'static-options.xml'
CONFIGURATION_SCHEMA_FILE = 'configuration.xml'

class CreamXMLBackend(dict, Backend):
    def __init__(self, profiles_folder):
        dict.__init__(self)
        self.profiles_folder = self.profiles_folder

    def get_option(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise MissingOption(item)

    set_option = dict.__setitem__

    options = dict.keys
    tree = property(lambda self:self)

    def read(self):
        pass

    def save(self, profile_list, fields):
        pass
