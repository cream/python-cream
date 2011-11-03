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


from gi.repository import GObject as gobject, Gtk as gtk

from cream.config import widgets
from cream.util import joindir


MODE_NORMAL = 1
MODE_ADD = 2


def get_widget_for_value(value):

    if isinstance(value, bool):
        return widgets.BooleanWidget
    elif isinstance(value, int):
        return widgets.IntegerWidget
    elif isinstance(value, float):
        return widgets.FloatWidget
    elif isinstance(value, basestring):
        return widgets.CharWidget
    elif isinstance(value, list):
        return widgets.MultiOptionWidget


class ConfigurationDialog(gobject.GObject):

    __gsignals__ = {
        'value-changed': (gobject.SignalFlags.RUN_LAST, None, (str, object)),
        'profile-selected': (gobject.SignalFlags.RUN_LAST, None, (str, )),
        'profile-added': (gobject.SignalFlags.RUN_LAST, None, (str, )),
        'profile-removed': (gobject.SignalFlags.RUN_LAST, None, (str, ))
    }

    def __init__(self, profiles):

        gobject.GObject.__init__(self)

        self.profiles = profiles
        self.widgets = {}

        interface = gtk.Builder()
        interface.add_from_file(joindir(__file__, 'interface/dialog.ui'))

        self.dialog = interface.get_object('dialog')
        self.profile_box = interface.get_object('profile_box')
        self.settings_grid = interface.get_object('settings_grid')
        self.profile_store = interface.get_object('profile_store')

        self.profile_normal = interface.get_object('profile_normal')
        self.profile_selector = interface.get_object('profile_selector')
        self.button_add = interface.get_object('button_add')
        self.button_remove = interface.get_object('button_remove')

        self.profile_add = interface.get_object('profile_add')
        self.profile_entry = interface.get_object('profile_entry')
        self.button_save = interface.get_object('button_save')
        self.button_cancel = interface.get_object('button_cancel')


        # TODO: do this in Glade, stupid thing is crashing
        cell = gtk.CellRendererText()
        self.profile_selector.pack_start(cell, False)
        self.profile_selector.add_attribute(cell, "text", 0)


        self.dialog.connect('delete-event', lambda *x: self.dialog.hide())

        self.profile_selector.connect('changed', self.on_profile_selected)
        self.button_add.connect('clicked', self.change_mode, MODE_ADD)
        self.button_remove.connect('clicked', self.on_profile_removed)
        self.button_save.connect('clicked', self.on_profile_added)
        self.button_cancel.connect('clicked', self.change_mode, MODE_NORMAL)
        self.profile_entry.connect('activate', self.on_profile_added)


        self.profile_box.pack_start(self.profile_normal, True, True, 0)

        self.dialog.set_default_size(250, 150)


        for row, key in enumerate(sorted(self.profiles.default_profile.keys)):
            widget = self.init_widget(key)

            widget.connect('value-changed', self.on_value_changed, key)
            self.widgets[key] = widget

            self.settings_grid.attach(gtk.Label(key), 0, row+1, 1, 1)
            self.settings_grid.attach(widget.widget, 1, row+1, 1, 1)

        self.settings_grid.show_all()
        self.update_profile_list()


    def init_widget(self, key):

        value = self.profiles.selected_profile.get_value(key)
        widget = get_widget_for_value(value)

        return widget(value)


    @property
    def selected_profile(self):
        index = self.profile_selector.get_active()
        return list(self.profiles)[index]


    def change_mode(self, widget, mode):

        if mode == MODE_NORMAL:
            self.profile_entry.set_text('')
            self.profile_box.remove(self.profile_add)
            self.profile_box.pack_start(self.profile_normal, True, True, 0)
        else:
            self.profile_box.remove(self.profile_normal)
            self.profile_box.pack_start(self.profile_add, True, True, 0)
            self.profile_entry.grab_focus()


    def update_profile_list(self):

        self.profile_store.clear()

        for i, profile in enumerate(self.profiles):
            if profile.selected:
                selected_index = i
            self.profile_store.append((profile.name,))
        self.profile_selector.set_active(selected_index)

        if len(self.profiles) == 1:
            self.profile_selector.set_sensitive(False)
        else:
            self.profile_selector.set_sensitive(True)


    def update_values(self):

        for key in self.profiles.selected_profile.keys:
            value = self.profiles.selected_profile.get_value(key)
            self.widgets[key].set_value(value)


    def update_sensitivity(self):

        if self.profiles.selected_profile.is_default:
            self.button_remove.set_sensitive(False)
            self.settings_grid.set_sensitive(False)
        else:
            self.button_remove.set_sensitive(True)
            self.settings_grid.set_sensitive(True)


    def on_profile_selected(self, widget):

        self.emit('profile-selected', self.selected_profile.name)

        self.update_sensitivity()
        self.update_values()


    def on_profile_added(self, widget):

        self.emit('profile-added', self.profile_entry.get_text())

        self.change_mode(None, MODE_NORMAL)
        self.update_profile_list()


    def on_profile_removed(self, widget):

        self.emit('profile-removed', self.selected_profile.name)
        self.update_profile_list()


    def on_value_changed(self, widget, value, key):
        self.emit('value-changed', key, value)


    def run(self):
        return self.dialog.run()


class Frontend(gobject.GObject):

    __gsignals__ = {
        'value-changed': (gobject.SignalFlags.RUN_LAST, None, (str, object)),
        'profile-selected': (gobject.SignalFlags.RUN_LAST, None, (str, )),
        'profile-added': (gobject.SignalFlags.RUN_LAST, None, (str, )),
        'profile-removed': (gobject.SignalFlags.RUN_LAST, None, (str, )),
    }

    def __init__(self, profiles):

        gobject.GObject.__init__(self)


        self.profiles = profiles
        self.dialog = ConfigurationDialog(profiles)

        self.dialog.connect('profile-selected', self.on_profile_selected)
        self.dialog.connect('profile-added', self.on_profile_added)
        self.dialog.connect('profile-removed', self.on_profile_removed)
        self.dialog.connect('value-changed', self.on_value_changed)


    def run(self):
        return self.dialog.run()


    def on_profile_selected(self, dialog, profile):
        self.emit('profile-selected', profile)


    def on_profile_added(self, dialog, profile):

        profiles = map(lambda p: p.name, self.profiles)
        if profile not in profiles:
            self.emit('profile-added', profile)


    def on_profile_removed(self, dialog, profile):
        self.emit('profile-removed', profile)


    def on_value_changed(self, dialog, key, value):
        self.emit('value-changed', key, value)
