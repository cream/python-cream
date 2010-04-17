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

    def __init__(self, features=[]):

        sourcefile = os.path.abspath(get_source_file(self.__class__))

        base_path = os.path.dirname(sourcefile)
        os.chdir(base_path)

        self.__manifest__ = os.path.join(base_path, self.__manifest__)
        self.context = Context(self.__manifest__)

        for feature in self.context.manifest['features']:
            try:
                f = FEATURES[feature](self)
            except KeyError:
                raise NoSuchFeature, "Could not load feature '{0}'!".format(feature)


    def __getattr__(self, attr):

        if attr == 'config':
            self._load_config()
            return self.config
        raise AttributeError(attr)


    def _load_config(self, base_path=None):

        from .config import Configuration
        self.config = Configuration.fromxml(base_path or self.context.wd)
        self.config_loaded = True


    def _autosave(self):

        if CONFIG_AUTOSAVE:
            if hasattr(self, 'config'):
                # Check if we have a 'config' attribute.
                # If we don't have one, the configuration wasn't loaded,
                # so don't save anything to avoid blowing up the
                # configuration directory with empty configuration files.
                self.config.save()
