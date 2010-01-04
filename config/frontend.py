import os
import gtk
from gpyconf.frontends._gtk import GtkConfigurationWindow
from cream.gui.builder import GtkBuilderInterface
from cream.gui import dialogs
from cream.util import joindir

INTERFACE_FILE = os.path.join('interface', 'config-dialog.glade')

class CreamFrontend(GtkConfigurationWindow, GtkBuilderInterface):
    _editable = True
    _new_events = ('profile-changed', 'add-profile', 'remove-profile')

    def __init__(self, backref, fields):
        self.profiles = []

        GtkBuilderInterface.__init__(self, joindir(__file__, INTERFACE_FILE))

        GtkConfigurationWindow.__init__(self, backref, fields)
        self.add_events(self._new_events)

    def build_ui(self):
        # build the UI (bind GtkBuilder stuff to the right variables)
        self._dialog = self.window
        self._widgets = self.notebook
        self._close = self.button_close
        self.profile_selector.connect('changed', self.on_profile_changed)
        self.profile_add.connect('clicked', self.on_add_profile)
        self.profile_remove.connect('clicked', self.on_remove_profile)

        self.profiles_storage = gtk.ListStore(str)
        self.profile_selector.set_model(self.profiles_storage)

        cell_renderer = gtk.CellRendererText()
        self.profile_selector.pack_start(cell_renderer)
        self.profile_selector.add_attribute(cell_renderer, 'text', 0)


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
                self.notebook.set_sensitive(True)
                self.profile_remove.set_sensitive(True)
        else:
            self.notebook.set_sensitive(False)
            self.profile_remove.set_sensitive(False)
        self._editable = value

    def set_active_profile_index(self, index):
        self.profile_selector.set_active(index)

    def run(self):
        GtkConfigurationWindow.run(self)
        self._dialog.destroy()
