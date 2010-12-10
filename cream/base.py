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

from cream.util import get_source_file
from cream.util.dependency import Dependency

from .manifest import Manifest
from .features import FEATURES, NoSuchFeature
from .path import CREAM_DIRS

EXEC_MODE_PRODUCTIVE = 'EXEC_MODE_PRODUCTIVE'
EXEC_MODE_DEVELOPMENT = 'EXEC_MODE_DEVELOPMENT'


class Context(object):

    def __init__(self, path, exec_mode=EXEC_MODE_PRODUCTIVE):

        self.path = path

        self.execution_mode = exec_mode

        self.environ = os.environ
        self.working_directory = os.path.dirname(self.path)
        self.manifest = Manifest(self.path)
        self.dirs = [os.path.join(d, self.manifest['id']) for d in CREAM_DIRS]


    def expand_path(self, p, mode='r'):
        """
        Choose the correct location of a path depending on the mode of
        the execution (development, productive) whether you want to
        read or write to the location.
        Please refer to `cream.path` to get a list of valid locations,
        following the XDG standarts.

        :param p: The path to expand.
        :type p: `str`
        :param mode: 'r' for reading and 'w' for writing capabilities.
        """

        if self.execution_mode == EXEC_MODE_DEVELOPMENT:
            return os.path.join(self.working_directory, p)
        else:
            if mode == 'r':
                for directory in self.dirs:
                    if os.path.exists(os.path.join(directory, p)):
                        return os.path.join(directory, p)
            else:
                return os.path.join(self.dirs[-1], p)



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
