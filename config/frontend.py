import os
import gtk
from gpyconf.frontends.gtk import ConfigDialog
from cream.gui import dialogs
from cream.util import joindir

INTERFACE_FILE = os.path.join('interface', 'config-dialog.glade')

class CreamFrontend(ConfigDialog):
    _editable = True
    _new_events = ('profile-changed', 'add-profile', 'remove-profile')

    def __init__(self, *args, **kwargs):

        self.profiles = []

        ConfigDialog.__init__(self, *args, **kwargs)
        self.add_events(self._new_events)

        self.profile_interface = gtk.Builder()
        self.profile_interface.add_from_file(joindir(__file__, 'interface/profiles.ui'))

        self.profile_box = self.profile_interface.get_object('profile_box')
        self.profile_selector = self.profile_interface.get_object('profile_selector')
        self.profile_add = self.profile_interface.get_object('profile_add')
        self.profile_remove = self.profile_interface.get_object('profile_remove')

        self.profile_selector.connect('changed', self.on_profile_changed)
        self.profile_add.connect('clicked', self.on_add_profile)
        self.profile_remove.connect('clicked', self.on_remove_profile)

        self.profiles_storage = gtk.ListStore(str)
        self.profile_selector.set_model(self.profiles_storage)

        cell_renderer = gtk.CellRendererText()
        self.profile_selector.pack_start(cell_renderer)
        self.profile_selector.add_attribute(cell_renderer, 'text', 0)

        self.layout.pack_start(self.profile_box, False, False, 0)
        self.layout.reorder_child(self.profile_box, 0)


    def add_profiles(self, profiles):
        """ Add a list or tuple of `Profile`s to the profile selector """
        for profile in profiles:
            self.add_profile(profile)

    def add_profile(self, profile):
        """ Add a `Profile` instance to the profile selector """
        self.profiles_storage.append([profile.name])
        self.profiles.append(profile.name)

    def insert_profile(self, profile, position):
        """ Insert `profile` at `position` into the profile selector """
        self.profiles_storage.insert(position, [profile.name])
        self.profiles.insert(position, profile.name)

    def remove_profile(self, position):
        """ Remove entry at `position` from the profile selector """
        iter = self.profiles_storage.get_iter_from_string(str(position))
        # huaa?
        self.profiles_storage.remove(iter)
        self.profile_selector.set_active(position-1)


    # CALLBACKS
    def on_profile_changed(self, widget):
        """ User changed the profile-selector dropdown """
        index = widget.get_active()
        if index < 0:
            # empty profile selector (should only happen at startup)
            return
        self.emit('profile-changed',
            self.profiles_storage.get_value(widget.get_active_iter(), 0),
            index)

    def on_add_profile(self, sender):
        """ User clicked the "add profile" button """
        dialog = dialogs.InputDialog('Profile name:', title='Add profile')
        dialog.invalid_inputs = self.profiles
        dialog.error_message = ("A profile named '%s' already exists. "
                                "Please chose another name.")

        name = dialog.run()
        if name:
            self.emit('add-profile', name, self.profile_selector.get_active()+1)

    def on_remove_profile(self, sender):
        """ User clicked the "remove profile" button """
        if dialogs.YesNoDialog("Are you sure you want to delete this profile?\n"
                               "It cannot be recovered.").run():
            self.emit('remove-profile', self.profile_selector.get_active())


    @property
    def editable(self):
        """
        `True` if the window is 'editable' (an editable profile is selected)
        """
        return self._editable

    @editable.setter
    def editable(self, value):
        # set widgets sensitive (or not)
        if value:
            if not self.editable:
                self.content.set_sensitive(True)
                self.profile_remove.set_sensitive(True)
        else:
            self.content.set_sensitive(False)
            self.profile_remove.set_sensitive(False)
        self._editable = value

    def set_active_profile_index(self, index):
        self.profile_selector.set_active(index)

    def run(self):
        ConfigDialog.run(self)
        self.dialog.destroy()
