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

import re
import time
from cream.path import MODULE_DIRS
from cream.manifest import ManifestDB
from cream.util.subprocess import Subprocess


class Dependency(object):

    def __init__(self, dependency, type):
        if type == 'org.cream.Module':
            self.process = ModuleSubprocess(dependency)

    def run(self):
        self.process.run()


class ModuleSubprocess(object):

    modules = ManifestDB(MODULE_DIRS, 'org.cream.Module')

    def __init__(self, module):
        if re.match('^(\w+\.)+\w+$', module):
            manifest = self.modules.get_by_id(module)
        else:
            manifest = self.modules.get_by_name(module)

        self.process = Subprocess(['python', manifest['entry']], manifest['name'])

    def run(self):
        self.process.run()
        time.sleep(0.1)