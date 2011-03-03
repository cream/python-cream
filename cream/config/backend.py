#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

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

    def __init__(self, scheme_path, path):
        Backend.__init__(self, None)
        dict.__init__(self)
        self.scheme_path = scheme_path
        self.path = path

        self.profile_dir = os.path.join(self.path, PROFILE_DIR)


    def read_scheme(self):

        if not os.path.isfile(self.scheme_path):
            from . import MissingConfigurationDefinitionFile
            raise MissingConfigurationDefinitionFile("Could not find %r." % self.scheme_path)

        tree = parse_xml(self.scheme_path)
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
            obj = unserialize_file(os.path.join(self.path, 'static-options.xml'))
            static_options.update(obj)
        except:
            pass

        if not os.path.exists(self.profile_dir):
            return dict(), tuple()

        for profile in os.listdir(self.profile_dir):
            if os.path.isdir(os.path.join(self.profile_dir, profile)):
                continue
            try:
                obj = unserialize_file(os.path.join(self.profile_dir, profile))
            except XMLSyntaxError,  err:
                self.warn("Could not parse XML configuration file '{file}': {error}".format(
                    file=profile, error=err))
            else:
                profiles.append(obj)
                
        return static_options, profiles


    def save(self, profile_list, fields):

        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)

        # get all saved profiles
        saved_profiles = {}
        for profile in os.listdir(self.profile_dir):
            name = os.path.splitext(profile)[0]
            saved_profiles[name] = os.path.join(self.profile_dir, profile)
            
        for index, profile in enumerate(profile_list):
            if not profile.is_editable: continue

            filename = os.path.join(os.path.join(self.path, PROFILE_DIR), slugify(profile.name)+'.xml')

            serialize_to_file({
                'name' : profile.name,
                'values' : profile.values,
                'position' : index,
                'selected' : profile_list.active == profile
            }, filename, tag=PROFILE_ROOT_NODE)

            if profile.name.lower() in saved_profiles:
                del saved_profiles[profile.name.lower()]
                
        # `saved_profiles` now contains profiles, which have been removed
        # but are still present in the filesystem. Remove them.
        for profile in saved_profiles.values():
            os.remove(profile)

        static_options = dict((name, field.value) for name, field in
                              fields.iteritems() if field.static)
        if static_options:
            serialize_to_file(static_options,
                os.path.join(self.path, STATIC_OPTIONS_FILE),
                tag=STATIC_OPTIONS_ROOT_NODE)
