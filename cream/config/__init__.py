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

# TODO: Rewrite this.

from gpyconf import Configuration as _Configuration
from gpyconf.fields import Field

from .backend import CreamXMLBackend, CONFIGURATION_SCHEME_FILE
from cream.util import flatten, cached_property

PROFILE_EXISTS_MARKUP = '''<span weight="bold" size="large"> \
Sorry! A profile with the name <span style="italic">{0}</span> already exists!</span>

Please choose a different name!'''

class MissingConfigurationDefinitionFile(Exception):
    """
    Raised if one tries to access a module's configuration
    but that module hasn't defined any.
    """
    pass

class ProfileNotEditable(Exception):
    pass


class ConfigurationProfile(object):
    """ A configuration profile. Holds name and assigned values. """
    is_editable = True

    def __init__(self, name, values, editable=True):
        self.name = name
        self.default_values = values
        self.is_editable = editable
        self._values = values

    @classmethod
    def fromdict(cls, dct, default_profile):
        values = default_profile.values.copy()
        values.update(dct.get('values', ()))
        return cls(dct.pop('name'), values, dct.pop('editable', True))

    @property
    def values(self):
        return self._values

    # TODO: Very repetitive
    @values.setter
    def values(self, value):
        if not self.is_editable:
            raise ProfileNotEditable(self)
        else:
            self._values = value

    def update(self, iterable):
        if not self.is_editable:
            raise ProfileNotEditable(self)
        self.values.update(iterable)

    def set(self, name, value):
        if not self.is_editable:
            raise ProfileNotEditable(self)
        self.values[name] = value

    def __repr__(self):
        return "<Profile '%s'%s>" % (self.name,
            not self.is_editable and ' (not editable)' or '')

class DefaultProfile(ConfigurationProfile):
    """ Default configuration profile (using in-code defined values) """
    def __init__(self, values):
        ConfigurationProfile.__init__(self, 'Default Profile',
                                      values, editable=False)


class ProfileExistsError(Exception):
    def __init__(self, name):
        Exception.__init__(self, "A profile named '%s' already exists" % name)

class ProfileList(list):
    """ List of profiles """
    default = None
    active = None
    active_index = 0

    def __init__(self, default_profile):
        list.__init__(self)
        list.append(self, default_profile)
        self.default = default_profile

    def insert(self, index, profile, overwrite=False):
        assert index

        if not isinstance(profile, ConfigurationProfile):
            profile = ConfigurationProfile.fromdict(profile, self.default)

        _, old_profile = self.find_by_name(profile.name)
        if old_profile is not None:
            if not overwrite:
                raise ProfileExistsError(profile)
            else:
                old_profile.values = profile.values
        else:
            list.insert(self, index, profile)

    def append(self, *args, **kwargs):
        self.insert(len(self), *args, **kwargs)
    add = append

    def find_by_name(self, name):
        """
        Returns a `(index, profile)` tuple being the `Profile` instance holding
        `name` as `name` attribute and its index in this list.

        If no such profile exists, returns a `(None, None)` tuple instead.
        """
        for index, profile in enumerate(self):
            if profile.name == name:
                return index, profile
        return None, None

    def _use(self, profile):
        if isinstance(profile, int):
            try:
                self.active = self[profile]
                self.active_index = profile
            except IndexError:
                self._use(0)
        else:
            self.active = profile
            self.active_index = self.index(profile)


class Configuration(_Configuration):
    """
    Base class for all cream configurations.
    """
    backend = CreamXMLBackend
    profiles = ()

    @cached_property
    def frontend(self):
        from .frontend import CreamFrontend
        return CreamFrontend


    def __init__(self, scheme_path, path, **kwargs):
        # Make sure this instance's `fields` dict is *not* the classes'
        # `fields` dict (hence, the `fields` attribute of class `cls`),
        # but a copy of it.
        # TODO: There has to be a better way.
        self.fields = self.fields.copy()

        backend = CreamXMLBackend(scheme_path, path)

        try:
            configuration_scheme = backend.read_scheme()
            for name, field in configuration_scheme.iteritems():
                self._add_field(name, field)
        except MissingConfigurationDefinitionFile:
            pass

        _Configuration.__init__(self, backend_instance=backend, **kwargs)


    def _add_field(self, name, field):
        field.field_var = name
        self.fields[name] = field
        field.connect('value-changed', self.on_field_value_changed)

    def read(self):
        if not self.initially_read:
            predefined_profiles = self.profiles
        else:
            predefined_profiles = ()

        self.profiles = ProfileList(DefaultProfile(self.fields.name_value_dict)) # TODO: remove static options

        static_options, profiles = self.backend_instance.read()

        for field_name, value in static_options.iteritems():
            setattr(self, field_name, value)

        active_profile = 0
        for profile in flatten((profiles, predefined_profiles)):
            position = profile.pop('position')
            self.profiles.insert(position, profile, overwrite=True)
            if profile.pop('selected', False):
                active_profile = position

        self.use_profile(active_profile)

        self.initially_read = True

    def __setattr__(self, attr, value):
        new_value = super(Configuration, self).__setattr__(attr, value)
        if new_value is not None and not self.fields[attr].static:
            self.profiles.active.set(attr, new_value)

    def __getattr__(self, name):
        field = self.fields.get(name)
        if field is not None:
            if field.static:
                return field.value
            else:
                return self.profiles.active.values[name]
        else:
            raise AttributeError("No such attribute '%s'" % name)

    def use_profile(self, profile):
        self.profiles._use(profile)
        for name, instance in self.fields.iteritems():
            if instance.static: continue
            instance.value = self.profiles.active.values[name]
            self.profiles.active.values[name] = instance.value


    # FRONTEND:
    def _init_frontend(self, fields):
        _Configuration._init_frontend(self, fields)
        self.window = self.frontend_instance

        self.window.add_profiles(self.profiles)

        self.window.connect('profile-changed', self.frontend_profile_changed)
        self.window.connect('add-profile', self.frontend_add_profile)
        self.window.connect('remove-profile', self.frontend_remove_profile)

        self.window.set_active_profile_index(self.profiles.active_index)

    def frontend_field_value_changed(self, *args):
        if not self._ignore_frontend:
            _Configuration.frontend_field_value_changed(self, *args)


    def frontend_profile_changed(self, sender, profile_name, index):
        """ Profile selection was changed by the frontend (user) """
        self._ignore_frontend = True
        self.use_profile(index)
        self._ignore_frontend = False
        self.window.editable = self.profiles.active.is_editable
        self.save()

    def frontend_add_profile(self, sender, profile_name, position):
        """ User added a profile using the "add profile" button """
        profile = ConfigurationProfile(profile_name, self.fields.name_value_dict)
        try:
            self.profiles.insert(position, profile)
        except ProfileExistsError:
            import gtk
            dialog = gtk.MessageDialog(
                parent=None,
                flags=gtk.DIALOG_MODAL,
                type=gtk.MESSAGE_ERROR,
                buttons=gtk.BUTTONS_CLOSE
            )
            dialog.set_markup(PROFILE_EXISTS_MARKUP.format(profile.name))
            dialog.run()
            dialog.destroy()
        else:
            self.window.insert_profile(profile, position)
            self.window.set_active_profile_index(position)
            self.save()

    def frontend_remove_profile(self, sender, position):
        """ User removed a profile using the "remove profile" button """
        del self.profiles[position]
        self.window.remove_profile(position)
        self.save()


    def run_frontend(self):
        _Configuration.run_frontend(self)
        del self.frontend_instance

    def show_dialog(self):
        self.run_frontend()


    # BACKEND
    def save(self):
        self.emit('pre-save')
        self.backend_instance.save(self.profiles, self.fields)



# Patch the `Field` class to make it accept the
# cream-specific `static` keyword:
def inject_method(klass, method_name):
    def wrapper(func):
        original_meth = getattr(klass, method_name)
        def chained_method(*args, **kwargs):
            original_meth(*args, **kwargs)
            func(*args, **kwargs)
        setattr(klass, method_name, chained_method)
        return func
    return wrapper

@inject_method(Field, '_external_on_initialized')
def on_initialized(self, kwargs):
    self.static = kwargs.pop('static', False)
