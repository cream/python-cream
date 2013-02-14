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

from gi.repository import Gtk as gtk

from gpyconf.frontends.gtk import ConfigurationDialog
from cream.util import joindir

MODE_NORMAL = 1
MODE_EDIT = 2

class CreamFrontend(ConfigurationDialog):
    _editable = True
    _new_events = ('profile-changed', 'add-profile', 'remove-profile')

    def __init__(self, *args, **kwargs):

        self.profiles = []
        self._mode = MODE_NORMAL

        ConfigurationDialog.__init__(self, title='Configuration', *args, **kwargs)
        self.add_events(self._new_events)

        self.interface = gtk.Builder()
        self.interface.add_from_file(joindir(__file__, 'interface/profiles.ui'))

        self.profile_box_edit = self.interface.get_object('profile_box_edit')
        self.profile_entry = self.interface.get_object('profile_entry')
        self.profile_save = self.interface.get_object('profile_save')
        self.profile_cancel = self.interface.get_object('profile_cancel')

        self.profile_box_normal = self.interface.get_object('profile_box_normal')
        self.profile_selector = self.interface.get_object('profile_selector')
        self.profile_add = self.interface.get_object('profile_add')
        self.profile_remove = self.interface.get_object('profile_remove')

        self.profiles_storage = self.interface.get_object('profiles_storage')

        self.profile_selector.connect('changed', self.on_profile_changed)
        self.profile_entry.connect('activate', self.change_mode)
        self.profile_entry.connect('activate', self.on_new_profile_added)
        self.profile_add.connect('clicked', self.change_mode)
        self.profile_save.connect('clicked', self.change_mode)
        self.profile_save.connect('clicked', self.on_new_profile_added)
        self.profile_cancel.connect('clicked', self.change_mode)
        self.profile_remove.connect('clicked', self.on_remove_profile)

        self.alignment = gtk.Alignment.new(1, 0.5, 1, 1)
        self.alignment.add(self.profile_box_normal)

        self.layout.pack_start(self.alignment, False, False, 0)
        self.layout.reorder_child(self.alignment, 0)

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
            index
        )


    def on_remove_profile(self, sender):
        """ User clicked the "remove profile" button """

        dialog = gtk.MessageDialog(
                parent=None,
                flags=gtk.DialogFlags.MODAL,
                type=gtk.MessageType.QUESTION,
                buttons=gtk.ButtonsType.YES_NO)

        dialog.set_markup("<span weight=\"bold\" size=\"large\">Are you sure that you want to remove profile <span style=\"italic\">{0}</span>?</span>\n\nYou will lose all data connected to this profile and won't be able to restore a previously removed profile!".format(self.profiles[self.profile_selector.get_active()]))

        res = dialog.run()
        dialog.destroy()
        if res == gtk.ResponseType.YES:
            self.emit('remove-profile', self.profile_selector.get_active())

    def on_new_profile_added(self, sender):
        """ User is done with editing the Entry """
        name = self.profile_entry.get_text()
        index = self.profile_selector.get_active() + 1
        if name:
            self.emit('add-profile', name, index)


    def change_mode(self, sender):
        """ User clicked on add or save button. Change the mode. """
        max_height = max(self.profile_entry.get_allocated_height(),
            self.profile_selector.get_allocated_height()
        )
        self.alignment.set_size_request(-1, max_height)

        box = [widget for widget in self.alignment][0]
        if self._mode == MODE_NORMAL:
            self.profile_entry.set_text('')
            self.alignment.remove(box)
            self.alignment.add(self.profile_box_edit)
            self.profile_entry.grab_focus()
            self._mode = MODE_EDIT
        else:
            self.alignment.remove(box)
            self.alignment.add(self.profile_box_normal)
            self._mode = MODE_NORMAL

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
