import os

from lxml.etree import XMLSyntaxError, parse as parse_xml
from cream.util.string import slugify

from gpyconf.backends import Backend
from xmlserialize import unserialize_file, unserialize_atomic, serialize_to_file
import gpyconf.fields
import gpyconf.contrib.gtk
import cream.config.fields

FIELD_TYPE_MAP = {
    'char' : 'str',
    'color' : 'str',
    'font' : 'str',
    'file' : 'tuple',
    'integer' : 'int',
    'hotkey' : 'str',
    'boolean' : 'bool',
    'multioption' : 'tuple'
}


CONFIGURATION_DIRECTORY   = 'configuration'
STATIC_OPTIONS_FILE       = 'static-options.xml'
CONFIGURATION_SCHEME_FILE = 'scheme.xml'
PROFILE_ROOT_NODE         = 'configuration_profile'
STATIC_OPTIONS_ROOT_NODE  = 'static_options'
PROFILE_DIR               = 'profiles'


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
        conf_file = os.path.join(self.configuration_dir, CONFIGURATION_SCHEME_FILE)
        if not os.path.isfile(conf_file):
            from . import MissingConfigurationDefinitionFile
            raise MissingConfigurationDefinitionFile("Could not find %r." % conf_file)

        tree = parse_xml(conf_file)
        root = tree.getroot()
        scheme = {}

        for child in root.getchildren():
            option_name = child.tag
            attributes = dict(child.attrib)
            option_type = attributes.pop('type')
            if option_type.startswith('multioption'):
                # TODO: Hrm
                attributes['default'] = child.attrib.pop('default', None)
                attributes['options'] = unserialize_atomic(child, FIELD_TYPE_MAP)
            else:
                if not (
                    FIELD_TYPE_MAP.get(option_type) in ('list', 'tuple', 'dict')
                    and not child.getchildren()
                ):
                    attributes['default'] = unserialize_atomic(child, FIELD_TYPE_MAP)
            scheme[option_name] = get_field(option_type)(**attributes)

        return scheme


    def read(self):

        static_options = {}
        profiles = []

        try:
            obj = unserialize_file(os.path.join(self.configuration_dir, STATIC_OPTIONS_FILE))
            static_options.update(obj)
        except:
            pass

        if not os.path.exists(os.path.join(self.configuration_dir, PROFILE_DIR)):
            return dict(), tuple()

        for profile in os.listdir(os.path.join(self.configuration_dir, PROFILE_DIR)):
            if os.path.isdir(os.path.join(self.configuration_dir, profile)):
                continue
            try:
                obj = unserialize_file(os.path.join(self.configuration_dir, profile))
            except XMLSyntaxError,  err:
                self.warn("Could not parse XML configuration file '{file}': {error}".format(
                    file=profile, error=err))
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
