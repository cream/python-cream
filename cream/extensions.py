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
import sys
import inspect
import imp

from . import Component
from .manifest import ManifestDB

EXTENSIONS = {}

def register(ext):

    # TODO: Error management!
    path = os.path.abspath(inspect.getsourcefile(ext))
    EXTENSIONS[path] = ext
    return ext


class Extension(Component):
    """ Class for building extensions. """

    def __init__(self, interface):
        Component.__init__(self)
        self.interface = interface

class ExtensionManager(object):
    """ Class for managing extensions. """

    def __init__(self, paths, interface=None):

        self.paths = paths
        self.interface = interface

        self.extensions = ManifestDB(self.paths, type='org.cream.Extension')

    def load_all(self, interface=None, *args, **kwargs):
        return map(lambda ext: self._load(ext, interface),
                   self.extensions.by_name.itervalues())

    def load_by_name(self, name, interface=None, *args, **kwargs):
        ext = self.extensions.get_by_name(name)
        return self._load(ext, interface)


    def load_by_hash(self, hash, interface=None, *args, **kwargs):
        ext = self.extensions.get_by_hash(hash)
        return self._load(ext, interface)


    def _load(self, extension, interface=None, *args, **kwargs):
        module_path = extension['entry'].replace('./', '')

        sys.path.append(module_path)
        imp.load_module(
            extension['name'],
            open(module_path),
            module_path,
            ('.py', 'r', imp.PY_SOURCE)
        )

        extension = EXTENSIONS[module_path]
        instance = extension(interface or self.interface, *args, **kwargs)
        sys.path.remove(module_path)

        return instance
