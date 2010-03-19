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

from .meta import MetaData

CONFIG_AUTOSAVE = True

class Component(object):
    """ Baseclass for e. g. cream.Module and cream.extensions.Extension. """

    __meta__ = 'meta.xml'
    config_loaded = False

    def __init__(self):

        sourcefile = os.path.abspath(get_source_file(self.__class__))

        base_path = os.path.dirname(sourcefile)
        os.chdir(base_path)

        self.__meta__ = os.path.join(base_path, self.__meta__)
        self.meta = MetaData(self.__meta__)


    def __getattr__(self, attr):

        if attr == 'config':
            self._load_config()
            return self.config
        raise AttributeError(attr)


    def _load_config(self, base_path=None):

        from .config import Configuration
        self.config = Configuration.fromxml(base_path or self.meta['path'])
        self.config_loaded = True


    def _autosave(self):

        if CONFIG_AUTOSAVE:
            if hasattr(self, 'config'):
                # Check if we have a 'config' attribute.
                # If we don't have one, the configuration wasn't loaded,
                # so don't save anything to avoid blowing up the
                # configuration directory with empty configuration files.
                self.config.save()
