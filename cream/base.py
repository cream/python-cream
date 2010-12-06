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

from cream.util import get_source_file
from cream.util.dependency import Dependency

from .manifest import Manifest
from .features import FEATURES, NoSuchFeature

EXEC_MODE_PRODUCTIVE = 'EXEC_MODE_PRODUCTIVE'
EXEC_MODE_DEVELOPMENT = 'EXEC_MODE_DEVELOPMENT'

class Context(object):

    def __init__(self, path, exec_mode=EXEC_MODE_PRODUCTIVE):

        self.path = path

        self.execution_mode = exec_mode

        self.environ = os.environ
        self.working_directory = os.path.dirname(self.path)
        self.manifest = Manifest(self.path)


    def expand_path(self, p):

        if self.execution_mode == EXEC_MODE_DEVELOPMENT:
            return os.path.join(self.working_directory, p)


class Component(object):
    """ Baseclass for e. g. cream.Module and cream.extensions.Extension. """

    __manifest__ = 'manifest.xml'

    def __init__(self, path=None, exec_mode=EXEC_MODE_PRODUCTIVE):

        if path:
            self.__manifest__ = path
        else:
            sourcefile = os.path.abspath(get_source_file(self.__class__))
            base_path = os.path.dirname(sourcefile)
            self.__manifest__ = os.path.join(base_path, self.__manifest__)

        # Create context and load manifest file...
        self.context = Context(self.__manifest__, exec_mode)

        os.chdir(self.context.working_directory)


        # Load required features...
        self._features = list()
        self._loaded_features = set()

        for feature_name, kwargs in self.context.manifest['features']:
            try:
                feature_class = FEATURES[feature_name]
            except KeyError:
                raise NoSuchFeature("Could not load feature '%s'" % feature_name)
            else:
                self.load_feature(feature_class, **kwargs)

        for dependency in self.context.manifest['dependencies']:
            Dependency(dependency['id'], dependency['type']).run()

    def load_feature(self, feature_class, **kwargs):
        """ Make sure a feature is only loaded once for a Component. """
        if feature_class not in self._loaded_features:
            self._features.append(feature_class(self, **kwargs))
            self._loaded_features.add(feature_class)
