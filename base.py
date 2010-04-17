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

from cream.util import cached_property, get_source_file

from .manifest import Manifest
from .features import FEATURES, NoSuchFeature

CONFIG_AUTOSAVE = True

class Context(object):

    def __init__(self, path):

        self.path = path

        self.environ = os.environ
        self.wd = os.path.dirname(self.path)
        self.manifest = Manifest(self.path)


class Component(object):
    """ Baseclass for e. g. cream.Module and cream.extensions.Extension. """

    __manifest__ = 'manifest.xml'
    config_loaded = False

    def __init__(self, path=None, features=[]):

        if path:
            self.__manifest__ = path
        else:
            sourcefile = os.path.abspath(get_source_file(self.__class__))
            base_path = os.path.dirname(sourcefile)
            self.__manifest__ = os.path.join(base_path, self.__manifest__)

        # Create context and load manifest file...
        self.context = Context(self.__manifest__)

        os.chdir(self.context.wd)

        # Load required features...
        f = {}
        self._features = []

        self.context.manifest['features'] += features

        for feature in self.context.manifest['features']:
            try:
                cls, priority = FEATURES[feature]
                if not f.has_key(priority):
                    f[priority] = []
                f[priority].append(cls)
            except KeyError:
                raise NoSuchFeature, "Could not load feature '{0}'!".format(feature)

        for key, val in f.iteritems():
            for cls in val:
                self._features.append(cls(self))
