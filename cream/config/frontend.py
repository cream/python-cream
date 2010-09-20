import os
import gtk
from gpyconf.frontends.gtk import ConfigurationDialog
from cream.gui import dialogs
from cream.util import joindir

INTERFACE_FILE = os.path.join('interface', 'config-dialog.glade')

class CreamFrontend(ConfigurationDialog):
    _editable = True
    _new_events = ('profile-changed', 'add-profile', 'remove-profile')

    def __init__(self, *args, **kwargs):

        self.profiles = []

        ConfigurationDialog.__init__(self, *args, **kwargs)
        self.add_events(self._new_events)

        self.interface = gtk.Builder()
        self.interface.add_from_file(joindir(__file__, 'interface/profiles.ui'))

        self.profile_box = self.interface.get_object('profile_box')
        self.profile_selector = self.interface.get_object('profile_selector')
        self.profile_add = self.interface.get_object('profile_add')
        self.profile_remove = self.interface.get_object('profile_remove')
        self.profiles_storage = self.interface.get_object('profiles_storage')

        self.profile_selector.connect('changed', self.on_profile_changed)
        self.profile_add.connect('clicked', self.on_add_profile)
        self.profile_remove.connect('clicked', self.on_remove_profile)
        self.profile_selector.connect('editing-done', self.on_new_profile_added)

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
        self.profile_selector.editing_done()

    def on_remove_profile(self, sender):
        """ User clicked the "remove profile" button """
        if dialogs.YesNoDialog("Are you sure you want to delete this profile?\n"
                               "It cannot be recovered.").run():
            self.emit('remove-profile', self.profile_selector.get_active())
            
    def on_new_profile_added(self, sender):
        """User is done with editing the Entry"""
        name = sender.get_active_text()
        index = self.profile_selector.get_active() + 2
        if name:
            self.emit('add-profile', name, index)

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
        ConfigurationDialog.run(self)
        self.dialog.destroy()
