import os

try:
    from xml.etree import cElementTree as elementtree
except ImportError:
    from xml.etree import  ElementTree as elementtree
from xml.parsers.expat import ExpatError

from gpyconf.backends import Backend
from gpyconf.backends._xml.xmlserialize import to_python_object, unserialize, serialize
from cream.config import fields
from cream.util.string import slugify


CONFIGURATION_DIRECTORY   = 'configuration'
STATIC_OPTIONS_FILE       = 'static-options.xml'
CONFIGURATION_SCHEMA_FILE = 'configuration.xml'
PROFILE_ROOT_NODE         = 'configuration_profile'
STATIC_OPTIONS_ROOT_NODE  = 'static_options'

NONFLAT_FIELDS = ('dict', 'list', 'tuple') # opposite of "flat"?

GPYCONF_FIELDS_LOWERCASED = dict((name.lower()[:-5], getattr(fields, name))
                                 for name in fields.__all__)
TYPE_ALIASES = {
    'str' : 'char',
    'int' : 'integer'
}


def field_for_type(type):
    return GPYCONF_FIELDS_LOWERCASED[TYPE_ALIASES.get(type, type)]

class CreamXMLBackend(dict, Backend):
    def __init__(self, directory='.'):
        Backend.__init__(self, None)
        dict.__init__(self)
        self.directory = directory
        self.configuration_dir = os.path.join(self.directory,
                                              CONFIGURATION_DIRECTORY)

    def read_scheme(self):
        field_scheme = {}

        xmltree = elementtree.parse(os.path.join(self.directory,
                                                 CONFIGURATION_SCHEMA_FILE))
        root_node = xmltree.getroot()
        for node in root_node.getchildren():
            option_name = node.tag
            attributes = node.attrib
            field_type = attributes.pop('field')
            if field_type in NONFLAT_FIELDS:
                attributes['default'] = to_python_object(node, field_type)
            else:
                attributes.setdefault('default', node.text)
            field = field_for_type(field_type)(**attributes)

            field_scheme[option_name] = field

        return field_scheme

    def read(self):
        if not os.path.exists(self.configuration_dir):
            return dict(), tuple()

        static_options = {}
        profiles = []

        for profile in os.listdir(self.configuration_dir):
            with open(os.path.join(self.configuration_dir, profile)) as f:
                if profile == STATIC_OPTIONS_FILE:
                    static_options.update(unserialize(f))
                    continue
                try:
                    profile = unserialize(f)
                except ExpatError, e:
                    self.warn("Failed to parse '%s': %s" % (fobj.name, e))
                else:
                    profiles.append(profile)

        return static_options, profiles

    def save(self, profile_list, fields):
        if not os.path.exists(self.configuration_dir):
            os.makedirs(self.configuration_dir)

        for profile in (p for p in profile_list if p.is_editable):
            with open(os.path.join(self.configuration_dir,
                                   slugify(profile.name)+'.xml'), 'w') as fobj:
                serialize({
                    'name' : profile.name,
                    'values' : profile.values,
                    'position' : profile_list.index(profile),
                    'selected' : profile_list.active == profile
                }, root_node=PROFILE_ROOT_NODE, file=fobj)

        with open(os.path.join(self.configuration_dir, STATIC_OPTIONS_FILE), 'w') as f:
            serialize(
                dict((n, f.value) for n, f in  fields.iteritems() if f.static),
                root_node=STATIC_OPTIONS_ROOT_NODE,
                file=f
            )
