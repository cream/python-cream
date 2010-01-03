from gpyconf import Configuration as _Configuration

from .backend import CreamXMLBackend
from .frontend import CreamFrontend
from cream.util import flatten


class ConfigurationProfile(object):
    """ A configuration profile. Holds name and assigned values. """
    _values = None
    is_editable = True

    def __init__(self, name, editable=True, **values):
        self.name = name
        self.default_values = values
        self.is_editable = editable

    @classmethod
    def fromdict(cls, dct):
        return cls(dct.pop('name'), dct.pop('editable', True),
                   **dct.get('values', dct))

    @property
    def values(self):
        return self._values or self.default_values

    @values.setter
    def values(self, values):
        self._values = values

    def __repr__(self):
        return "<Profile '%s'%s>" % (self.name,
            not self.is_editable and ' (not editable)' or '')

class DefaultProfile(ConfigurationProfile):
    """ Default configuration profile (using in-code defined values) """
    def __init__(self, **values):
        ConfigurationProfile.__init__(self, 'Default Profile', False, **values)


class ProfileExistsError(Exception):
    def __init__(self, name):
        Exception.__init__(self, "A profile named '%s' already exists" % name)

class ProfileList(list):
    """ List of profiles """
    def append(self, profile, overwrite=False):
        self.insert(len(self), profile, overwrite=overwrite)

    def insert(self, index, profile, overwrite=False):
        """
        Insert `profile` at `index` if `profile` not in `self` and not `overwrite`.
        Else, raise `ProfileExistsError`.
        """
        old_profile = self.by_name(profile.name)
        if old_profile is not None:
            if not overwrite:
                raise ProfileExistsError(profile)
            else:
                old_profile.values = profile.values
        else:
            list.insert(self, index, profile)

    def by_name(self, name):
        """
        Returns the `Profile` instance holding `name` as `name` attribute
        (or `None` if no such profile exists)
        """
        for profile in self:
            if profile.name == name:
                return profile


class Configuration(_Configuration):
    """
    Base class for all cream configurations.
    """
    frontend = CreamFrontend
    backend = CreamXMLBackend

    active_profile = None
    active_profile_index = 0
    profiles = ()

    def __init__(self, **kwargs):
        predefined_profiles = self.profiles
        self.profiles = ProfileList()

        default_profile = self.make_default_profile()
        self.active_profile = default_profile
        # activate default profile for now (avoiding GTK+ warnings)

        _Configuration.__init__(self, **kwargs)

        backend = self.backend_instance
        # add profiles loaded by the backend
        for profile in flatten((backend.profiles, predefined_profiles)):
            if isinstance(profile, dict):
                profile = ConfigurationProfile.fromdict(profile)
            self.profiles.append(profile, overwrite=True)

        self.profiles.insert(0, default_profile)
        # add the default profile
        # (added not until here to make sure it's ALWAYS the first item)

        #for field_name, value in backend.static_options.iteritems():
        #    setattr(self, field_name, value)

        if len(self.profiles) > 1:
            self.on_profile_changed(self, None, backend.selected_profile)


    def make_default_profile(self):
        return DefaultProfile(**self.fields.name_value_dict)


    def _init_frontend(self, fields):
        _Configuration._init_frontend(self, fields)

        self.window.add_profiles(self.profiles)

        self.window.connect('profile-changed', self.on_profile_changed)
        self.window.connect('add-profile', self.on_add_profile)
        self.window.connect('remove-profile', self.on_remove_profile)

        self.window.set_active_profile_index(self.active_profile_index)


    def on_field_value_changed(self, sender, field, value):
        """ User changed a value of some field """
        if isinstance(field, basestring):
            field = self.fields[field]
        if self.active_profile.is_editable:
            self.active_profile.values[field.field_var] = value

        _Configuration.on_field_value_changed(self, sender, field, value)


    def on_profile_changed(self, sender, profile_name, index):
        """ Profile selection was changed by the frontend (user) """
        # TODO: two expensive loops...
        self.active_profile = self.profiles[index]
        self.active_profile_index = index
        for field_name, value in self.active_profile.values.iteritems():
            if not hasattr(self, field_name):
                self.log("Profile update: Ignoring field '%s' that misses in "
                         "the configuration definition", level='warning')
                continue
            #if is_static(self.fields[field_name]):
            #    # this is a profile-independent (static) field, ignore it
            #    continue
            setattr(self, field_name, value)

        # a list of all fields the currently selected profile does not provide:
        undefined_field_values = (set(self.profiles[0].values.keys()) -
                                  set(self.active_profile.values.keys()))
        # use the options of the default profile instead:
        for field_name in undefined_field_values:
            #if is_static(self.fields[field_name]):
            #    continue
            setattr(self, field_name, self.profiles[0].values[field_name])

        self.window.editable = self.active_profile.is_editable


    def on_add_profile(self, sender, profile, position):
        """ User added a profile using the "add profile" button """
        profile = ConfigurationProfile(profile, **self.fields.name_value_dict)
        self.profiles.insert(position, profile)
        self.window.insert_profile(profile, position)
        self.window.set_active_profile_index(position)


    def on_remove_profile(self, sender, position):
        """ User removed a profile using the "remove profile" button """
        if self.active_profile.is_editable:
            self.profiles.pop(position)
            self.window.remove_profile(position)


    def run_frontend(self):
        _Configuration.run_frontend(self)
        del self.frontend_instance
