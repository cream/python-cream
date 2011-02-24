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
import gobject
import weakref

FEATURES = dict()

class NoSuchFeature(Exception):
    pass

class Feature(object):
    """ "Feature" that can be "mixed" into Cream components. """
    dependencies = None

    def __new__(cls, component, *args, **kwargs):
        """ Make sure all dependencies for this feature are loaded. """
        if cls.dependencies:
            for dependency in cls.dependencies:
                component.load_feature(dependency, *args, **kwargs)
        return super(Feature, cls).__new__(cls)

    def __finalize__(self):
        pass


class ConfigurationFeature(Feature):
    autosave = True

    def __init__(self, component, read=True):
        
        self.component_ref = weakref.ref(component)

        if read == True or read == 'true':
            read = True
        else:
            read = False

        Feature.__init__(self)

        from .config import Configuration

        scheme_path = os.path.join(component.context.get_path(), 'configuration/scheme.xml')
        config_dir = os.path.join(component.context.get_user_path(), 'configuration/')

        component.config = Configuration(scheme_path,
                                         config_dir,
                                         read=read)
        self.config = component.config


    def __finalize__(self):

        component = self.component_ref()
        if self.autosave:
            component.messages.debug("Automatically saving configuration...")
            self.config.save()


class HotkeyFeature(Feature, gobject.GObject):
    dependencies = (ConfigurationFeature,)

    __gtype_name__ = 'HotkeyFeature'
    __gsignals__ = {
        'hotkey-activated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    def __init__(self, component):

        from gpyconf.contrib.gtk import HotkeyField
        import cream.ipc
        from dbus.exceptions import DBusException

        Feature.__init__(self)
        gobject.GObject.__init__(self)

        self.component = weakref.ref(component)
        self.component().hotkeys = self

        try:
            self.manager = cream.ipc.get_object('org.cream.Hotkeys', '/org/cream/Hotkeys')
        except DBusException:
            import warnings
            warnings.warn("Could not connect to the cream hotkey manager")
            return

        self.broker = cream.ipc.get_object('org.cream.Hotkeys', self.manager.register(), interface='org.cream.Hotkeys.broker')
        self.broker.connect_to_signal('hotkey_activated', self.hotkey_activated_cb)

        for name, field in self.component().config.fields.iteritems():
            if isinstance(field, HotkeyField):
                self.broker.set_hotkey(field.action, field.value)
                field.connect('value-changed', self.configuration_field_value_changed_cb)


    def configuration_field_value_changed_cb(self, source, field, value):

        self.broker.set_hotkey(field.action, field.value)


    def hotkey_activated_cb(self, action):
        self.emit('hotkey-activated', action)


class ExtensionFeature(Feature):
    def __init__(self, component, directory='extensions'):
        Feature.__init__(self, component)

        from cream.extensions import ExtensionManager
        component.extension_manager = ExtensionManager(
            [os.path.join(component.context.working_directory, directory)],
            component.extension_interface
        )


FEATURES.update({
    'org.cream.extensions'  : ExtensionFeature,
    'org.cream.config'      : ConfigurationFeature,
    'org.cream.hotkeys'     : HotkeyFeature
})
