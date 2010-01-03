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
import inspect

from xml.dom.minidom import parse as parse_xml_file

import gobject
gobject.threads_init()

import dbus.service
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

import cream.ipc
from cream.util import joindir, cached_property


class MetaDataDB(object): # TODO: Move to cream.meta?

    def __init__(self, path, type=None):

        self.path = path
        self.type = type

        self.by_name = {}
        self.by_hash = {}

        self.scan()


    def scan(self):

        res = MetaData.scan(self.path, self.type)

        for i in res:
            self.by_name[i['name']] = i
            self.by_hash[i['hash']] = i


    def get_by_name(self, name):
        return self.by_name[name]


    def get_by_hash(self, hash):
        return self.by_hash[hash]


class MetaData(dict): # TODO: Move to cream.meta?
    """
    Interface to a module's meta data.

    To get access to meta options, just use it like a normal ``dict``.
    """
    METAFILE_NAME = 'meta.xml'

    def __init__(self, path):

        self['filepath'] = os.path.abspath(path)
        self['path'] = os.path.dirname(self['filepath'])

        self.dom = parse_xml_file(path)

        for n in self.dom.getElementsByTagName('meta')[0].childNodes:
            if n.nodeType == n.ELEMENT_NODE:
                key = n.nodeName
                value = n.childNodes[0].data
                self[key] = value


    @classmethod
    def scan(cls, path, type=None, parent=None):

        path = os.path.abspath(path)
        files = os.listdir(path)
        res = []

        for file in files:
            if os.path.isdir(os.path.join(path, file)):
                res.extend(cls.scan(os.path.join(path, file), type, parent))
            else:
                if file.endswith(cls.METAFILE_NAME):
                    m = cls(os.path.join(path, file))
                    if not type or m['type'] == type:
                        res.append(m)

        return res


class WithConfiguration(object):
    # TODO: Obsolete after changing configuration backend to XML. Remove!
    # ('Configurable', 'Configured', 'ConfigurableObject', 'ConfiguredObject', ...)!
    def __init__(self):
        sourcefile = os.path.abspath(inspect.getfile(self.__class__))
        # /foo/bar.py
        self._base_path = os.path.dirname(sourcefile) # TODO: This should not be here.
                                                      # Maybe common base class for extensions and modules?
        # /foo

    def __getattr__(self, attr):
        if attr == 'config':
            return self._load_config()
        raise AttributeError(attr)


    def _load_config(self, base_path=None):
        # Reload the module's configuration module
        # (placed at /path/to/module/config)
        # and assign it to the `conf` attribute. If that module doesn't exist,
        # set `conf` to `None`.
        import imp

        base_path = base_path or self._base_path
        try:
            fobj, path, descr = imp.find_module('config', [base_path])
        except ImportError, e:
            if hasattr(self, 'default_configuration_factory'):
                self.config = self.default_configuration_factory()
                return self.config
            raise AttributeError("""No such attribute 'config'. If you want to
                use the configuration system, you have to create a package
                named 'config' in your module's root directory.""")
        else:
            self._config_module = imp.load_module('config', fobj, path, descr)
            self.config = self._config_module.Configuration(
                                    basedir=os.path.join(base_path, 'config'))
            try:
                fobj.close()
            except AttributeError:
                pass
                # hrm?
            return self.config


class ModuleBase(cream.ipc.Object): # TODO: Move to some common place for extensions and modules.
    """ Base class for module-like objects like modules and extensions """

    __meta__ = 'meta.xml'
    __ipc_domain__ = None

    def __init__(self):

        sourcefile = os.path.abspath(inspect.getfile(self.__class__))
        # /foo/bar.py
        self._base_path = os.path.dirname(sourcefile)
        # /foo

        os.chdir(self._base_path)

        self.__meta__ = os.path.join(self._base_path, self.__meta__)
        self.meta = MetaData(self.__meta__)

        self._bus_name = '.'.join(self.__ipc_domain__.split('.')[:3])
        self._dbus_bus_name = dbus.service.BusName(self._bus_name,
                                                   cream.ipc.SESSION_BUS)

        cream.ipc.Object.__init__(self, cream.ipc.SESSION_BUS, self._bus_name,
                                  cream.ipc.bus_name_to_path(self.__ipc_domain__))

    @cached_property
    def messages(self):
        from cream.log import Messages
        return Messages(id=self._bus_name)


class Module(ModuleBase, WithConfiguration):
    """ Baseclass for all modules... """

    def __init__(self):
        WithConfiguration.__init__(self)
        ModuleBase.__init__(self)

    def main(self):
        """ Run a GLib-mainloop. """

        self._mainloop = gobject.MainLoop()
        self._mainloop.run()


    def quit(self):
        self._mainloop.quit()

