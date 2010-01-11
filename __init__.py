#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
import os
import gobject
gobject.threads_init()

import dbus.service
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

import cream.ipc
from cream.util import cached_property, get_source_file


class Component(object):
    def __init__(self):
        sourcefile = os.path.abspath(get_source_file(self.__class__))
        self._base_path = os.path.dirname(sourcefile)


class Configurable(object):
    def __getattr__(self, attr):
        if attr == 'config':
            self._load_config()
            return self.config
        raise AttributeError(attr)

    def _load_config(self, base_path=None):
        from .config.fromxml import configuration_from_xml_file
        klass = configuration_from_xml_file(
            os.path.join(base_path or self._base_path, 'config.xml'))
        self.config = klass(basedir=os.path.join(base_path or self._base_path,'config'))


class ModuleBase(cream.ipc.Object, Component): # TODO: Move to some common place for extensions and modules.
    """ Base class for module-like objects like modules and extensions """

    __meta__ = 'meta.xml'
    __ipc_domain__ = None

    def __init__(self):
        from .meta import MetaData

        Component.__init__(self)
        os.chdir(self._base_path) # er, what.

        self.__meta__ = os.path.join(self._base_path, self.__meta__)
        self.meta = MetaData(self.__meta__)

        self._bus_name = '.'.join(self.__ipc_domain__.split('.')[:3])
        self._dbus_bus_name = dbus.service.BusName(self._bus_name,
                                                   cream.ipc.SESSION_BUS)

        cream.ipc.Object.__init__(self,
            cream.ipc.SESSION_BUS,
            self._bus_name,
            cream.ipc.bus_name_to_path(self.__ipc_domain__)
        )

    @cached_property
    def messages(self):
        from cream.log import Messages
        return Messages(id=self._bus_name)


class Module(ModuleBase, Configurable):
    """ Baseclass for all modules... """
    def main(self):
        """ Run a GLib-mainloop. """

        self._mainloop = gobject.MainLoop()
        self._mainloop.run()


    def quit(self):
        self._mainloop.quit()

