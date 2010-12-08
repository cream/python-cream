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
import tempfile
from distutils.core import setup as _setup
from cream.manifest import Manifest

MODULE_DIR = 'share/cream/modules/{pkg_name}'

MODULE_START_SCRIPT_TEMPLATE = """\
#! /usr/bin/env python

import os

from cream.path import MODULE_DIRS
from cream.manifest import ManifestDB
from cream.util.subprocess import Subprocess

modules = ManifestDB(MODULE_DIRS, 'org.cream.Module')
manifest = modules.get_by_id('{id}')

try:
    process = Subprocess(['python', manifest['entry']], manifest['name'])
    pid = process.run()
    os.waitpid(pid, 0)
except KeyboardInterrupt:
    import sys
    sys.exit(0)
"""

def generate_start_script(manifest):


    tmp_dir = tempfile.mkdtemp()
    fh = open(os.path.join(tmp_dir, slugify(manifest['name'])), 'w')
    fh.write(MODULE_START_SCRIPT_TEMPLATE.format(id=manifest['id']))
    fh.close()

    return os.path.join(tmp_dir, slugify(manifest['name']))


def slugify(s):
    return s.lower().replace(' ', '-')


def discover(path):
    manifest = Manifest(path, expand_paths=False)

    start_script_path = generate_start_script(manifest)

    return {
        'name': manifest['id'],
        'version': manifest['version'],
        'scripts': [start_script_path]
        }


def get_pkg_info(manifest=None, **args):

    if manifest:
        pkg_info = discover(manifest)
        pkg_name = pkg_info['name']
    elif os.path.isfile('src/manifest.xml'):
        pkg_info = discover('src/manifest.xml')
        pkg_name = pkg_info['name']
    else:
        pkg_info = {}
        pkg_name = None

    if args.has_key('data_files'):
        df = args['data_files']
        args['data_files'] = []

        for path, files in df:
            print path, files
            args['data_files'].append((path.format(pkg_name=pkg_name, module_dir=MODULE_DIR.format(pkg_name=pkg_name)), files))

    pkg_info.update(args)

    return pkg_info

def setup(manifest=None, **args):
    _setup(**get_pkg_info(manifest, **args))