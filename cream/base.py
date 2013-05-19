# Copyright: 2007-2013, Sebastian Billaudelle <sbillaudelle@googlemail.com>
#            2010-2013, Kristoffer Kleine <kris.kleine@yahoo.de>

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os

from cream.util import get_source_file

from .manifest import Manifest
from .features import FEATURES, NoSuchFeature
from .path import CREAM_DIRS, XDG_DATA_HOME


class Context(object):

    def __init__(self, path, user_path_prefix=''):

        self.path = path
        self.user_path_prefix = user_path_prefix

        self.environ = os.environ
        self.working_directory = os.path.dirname(self.path)
        self.manifest = Manifest(self.path)


    def get_path(self):
        return os.path.dirname(self.path)


    def get_user_path(self):
        if self.user_path_prefix:
            user_path =os.path.join(XDG_DATA_HOME[0], 'cream', self.user_path_prefix, self.manifest['id'])
        else:
            user_path = os.path.join(XDG_DATA_HOME[0], 'cream', self.manifest['id'])

        if not os.path.exists(user_path):
            os.makedirs(user_path)

        return user_path


class Component(object):
    """ Baseclass for e. g. cream.Module and cream.extensions.Extension. """

    __manifest__ = 'manifest.xml'

    def __init__(self, path=None, user_path_prefix=''):

        if path:
            self.__manifest__ = path
        else:
            sourcefile = os.path.abspath(get_source_file(self.__class__))
            base_path = os.path.dirname(sourcefile)
            self.__manifest__ = os.path.join(base_path, self.__manifest__)

        # Create context and load manifest file...
        self.context = Context(self.__manifest__, user_path_prefix)

        try:
            os.chdir(self.context.working_directory)
        except OSError:
            import warnings
            warnings.warn("Could not change directory to the module's working directory!")

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


    def load_feature(self, feature_class, **kwargs):
        """ Make sure a feature is only loaded once for a Component. """
        if feature_class not in self._loaded_features:
            self._features.append(feature_class(self, **kwargs))
            self._loaded_features.add(feature_class)
