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

class Context(object):

    def __init__(self, path):

        self.path = path

        self.environ = os.environ
        self.working_directory = os.path.dirname(self.path)
        self.manifest = Manifest(self.path)


class Component(object):
    """ Baseclass for e. g. cream.Module and cream.extensions.Extension. """

    __manifest__ = 'manifest.xml'

    def __init__(self, path=None, features=None):

        if path:
            self.__manifest__ = path
        else:
            sourcefile = os.path.abspath(get_source_file(self.__class__))
            base_path = os.path.dirname(sourcefile)
            self.__manifest__ = os.path.join(base_path, self.__manifest__)

        # Create context and load manifest file...
        self.context = Context(self.__manifest__)

        os.chdir(self.context.working_directory)

        # Load required features...
        self._features = list()
        self._loaded_features = dict()
        # dict is the fastest for "do you have X" lookup, which runs in O(1)

        if features:
            self.context.manifest['features'].extend(features)

        for feature_name in self.context.manifest['features']:
            try:
                feature_class = FEATURES[feature_name]
            except KeyError:
                raise NoSuchFeature("Could not load feature '{0}'!".format(feature_name))
            else:
                self.load_feature(feature_class)

    def load_feature(self, feature_class):
        if feature_class not in self._loaded_features:
            self._features.append(feature_class(self))
            self._loaded_features[feature_class] = None # just some dummy value
