import os

from lxml.etree import parse as parse_xml

import gpyconf.fields
import gpyconf.contrib.gtk
import cream.config.fields
from gpyconf.backends import Backend
from gpyconf.backends._xml.xmlserialize import unserialize_file, unserialize_atomic, serialize_to_file
from lxml.etree import XMLSyntaxError
from cream.util.string import slugify

FIELD_TYPE_MAP = {
    'char' : 'str',
    'color' : 'str',
    'font' : 'str',
    'integer' : 'int',
    'hotkey' : 'str'
}


CONFIGURATION_DIRECTORY   = 'configuration'
STATIC_OPTIONS_FILE       = 'static-options.xml'
CONFIGURATION_SCHEME_FILE = 'configuration.xml'
PROFILE_ROOT_NODE         = 'configuration_profile'
STATIC_OPTIONS_ROOT_NODE  = 'static_options'


def get_field(name):
    if not name.endswith('Field'):
        name = name.title() + 'Field'

    try: return getattr(cream.config.fields, name)
    except AttributeError: pass
    try: return getattr(gpyconf.fields, name)
    except AttributeError: pass
    try: return getattr(gpyconf.contrib.gtk, name)
    except AttributeError:
        raise FieldNotFound(name)


class FieldNotFound(Exception):
    pass

class CreamXMLBackend(dict, Backend):
    compatibility_mode = False

    def __init__(self, directory='.'):
        Backend.__init__(self, None)
        dict.__init__(self)
        self.directory = directory
        self.configuration_dir = os.path.join(self.directory,
                                              CONFIGURATION_DIRECTORY)

    def read_scheme(self):
        tree = parse_xml(os.path.join(self.directory, CONFIGURATION_SCHEME_FILE))
        root = tree.getroot()
        scheme = {}

        for child in root.getchildren():
            option_name = child.tag
            attributes = dict(child.attrib)
            option_type = attributes.pop('type')
            attributes['default'] = unserialize_atomic(child, FIELD_TYPE_MAP)
            scheme[option_name] = get_field(option_type)(**attributes)

        return scheme


    def read(self):
        if not os.path.exists(self.configuration_dir):
            return dict(), tuple()

        static_options = {}
        profiles = []

        for profile in os.listdir(self.configuration_dir):
            try:
                obj = unserialize_file(os.path.join(self.configuration_dir, profile))
            except XMLSyntaxError,  err:
                self.warn("Could not parse XML configuration file '{file}': {error}".format(
                    file=profile, error=err))
            else:
                if profile == STATIC_OPTIONS_FILE:
                    static_options.update(obj)
                    continue
                else:
                    profiles.append(obj)

        return static_options, profiles

    def save(self, profile_list, fields):
        if not os.path.exists(self.configuration_dir):
            os.makedirs(self.configuration_dir)

        for index, profile in enumerate(profile_list):
            if not profile.is_editable: continue

            filename = os.path.join(self.configuration_dir,
                                    slugify(profile.name)+'.xml')

            serialize_to_file({
                'name' : profile.name,
                'values' : profile.values,
                'position' : index,
                'selected' : profile_list.active == profile
            }, filename, tag=PROFILE_ROOT_NODE)

        static_options = dict((name, field.value) for name, field in
                              fields.iteritems() if field.static)
        if static_options:
            serialize_to_file(static_options,
                os.path.join(self.configuration_dir, STATIC_OPTIONS_FILE),
                tag=STATIC_OPTIONS_ROOT_NODE)
