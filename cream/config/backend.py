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

from gi.repository import GObject as gobject, Gio as gio, GLib as glib

from cream.util.dicts import ordereddict



NAME_DEFAULT = 'Default'

KEY_PROFILES = 'profiles'
KEY_SELECTED = 'profile-selected'

IGNORE_KEYS = [KEY_PROFILES, KEY_SELECTED]


def variant_from_python(obj):

    if isinstance(obj, bool):
        return glib.Variant('b', obj)
    elif isinstance(obj, int):
        return glib.Variant('i', obj)
    elif isinstance(obj, float):
        return glib.Variant('d', obj)
    elif isinstance(obj, basestring):
        return glib.Variant('s', obj)
    elif isinstance(obj, list):
        return glib.Variant('as', obj)



def variant_to_python(variant):

    if variant.get_type_string() == 'b':
        return variant.get_boolean()
    elif variant.get_type_string() == 'i':
        return variant.get_int32()
    elif variant.get_type_string() == 'd':
        return variant.get_double()
    elif variant.get_type_string() == 's':
        return variant.get_string()
    elif variant.get_type_string() == 'as':
        return list(variant)



class Profiles(object):

    def __init__(self, schema):

        self.schema = schema
        self.profiles = ordereddict()
        self._selected_profile = None

        self.default_profile = self.add_profile(NAME_DEFAULT)

        profile_names = self.default_profile.settings.get_value(KEY_PROFILES)
        profile_names = filter(lambda n: n != NAME_DEFAULT, list(profile_names))


        for name in profile_names:
            self.add_profile(name)

        for profile in self.profiles.itervalues():
            if profile.selected:
                self.selected_profile = profile

        if not self.selected_profile:
            self.selected_profile = self.default_profile


    def __iter__(self):
        return iter(self.profiles.itervalues())


    def __len__(self):
        return len(self.profiles)


    @property
    def selected_profile(self):
        return self._selected_profile

    @selected_profile.setter
    def selected_profile(self, profile):

        if self._selected_profile:
            self._selected_profile.selected = False

        profile.selected = True
        self._selected_profile = profile


    def add_profile(self, name):

        if name == NAME_DEFAULT:
            profile = DefaultProfile(name, self.schema)
        else:
            profile = Profile(name, self.schema)
        self.profiles[name] = profile

        return profile


    def remove_profile(self, name):

        profile = self.profiles[name]
        if profile == self.selected_profile:
            index = self.profiles.values().index(profile)
            self.selected_profile = self.profiles.values()[index-1]

        return self.profiles.pop(name)


    def set_profile(self, name):

        profile = self.profiles[name]
        self.selected_profile = profile


    def get_value(self, key):

        return self.selected_profile.get_value(key)


    def set_value(self, key, value):

        self.selected_profile.set_value(key, value)


    def save(self):

        self.default_profile.set_value(KEY_PROFILES, list(self.profiles.keys()))


class Profile(object):

    def __init__(self, name, schema):

        self.name = name
        self.schema = schema
        self.path = '/' + name.lower()
        self.settings = gio.Settings.new_with_path(self.schema, self.path)

        self.is_default = False
        self._selected = self.settings.get_boolean(KEY_SELECTED)


    @property
    def keys(self):
        return (key for key in self.settings.list_keys() if key not in IGNORE_KEYS)


    @property
    def writeable(self):
        return self.name != NAME_DEFAULT


    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        self.settings.set_boolean(KEY_SELECTED, value)


    def get_value(self, key):
        return variant_to_python(self.settings.get_value(key))


    def set_value(self, key, value):
        variant = variant_from_python(value)
        self.settings.set_value(key, variant)


class DefaultProfile(Profile):

    def __init__(self, name, schema):

        Profile.__init__(self, name, schema)

        self.is_default = True


class Backend(gobject.GObject):

    def __init__(self, schema):

        gobject.GObject.__init__(self)

        self.profiles = Profiles(schema)


    def set_profile(self, profile):
        self.profiles.set_profile(profile)


    def add_profile(self, profile):
        self.profiles.add_profile(profile)


    def remove_profile(self, profile):
        self.profiles.remove_profile(profile)


    def set_value(self, key, value):
        self.profiles.set_value(key, value)


    def save(self):

        self.profiles.save()
        gio.Settings.sync()


    def __contains__(self, name):
        return name in self.profiles.default_profile.keys
