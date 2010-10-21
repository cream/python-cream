#!/usr/bin/env python

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
