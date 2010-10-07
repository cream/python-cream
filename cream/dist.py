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
import tempfile
from distutils.core import setup as _setup
from cream.manifest import Manifest

MODULE_DIR = 'share/cream/modules/{pkg_name}'

MODULE_START_SCRIPT_TEMPLATE = """\
#!/bin/sh

# {module_name} launcher script (automatically generated)

exec python {module_entry} "$@"
exit $?
"""

def generate_start_script(manifest):

    module_name = manifest['name']
    module_entry = os.path.join(MODULE_DIR.format(pkg_name=manifest['id']), manifest['entry'])

    tmp_dir = tempfile.mkdtemp()
    fh = open(os.path.join(tmp_dir, slugify(manifest['name'])), 'w')
    fh.write(MODULE_START_SCRIPT_TEMPLATE.format(module_name=module_name, module_entry=module_entry))
    fh.close()

    return os.path.join(tmp_dir, slugify(manifest['name']))


def slugify(s):
    return s.lower().replace(' ', '-')


def discover(path):
    manifest = Manifest(path, expand_paths=False)

    #print generate_start_script(manifest)

    return {
        'name': manifest['id'],
        'version': manifest['version'],
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
        for path, files in args['data_files']:
            args['data_files'].remove((path, files))
            args['data_files'].append((path.format(pkg_name=pkg_name, module_dir=MODULE_DIR.format(pkg_name=pkg_name)), files))

    pkg_info.update(args)

    return pkg_info

def setup(manifest=None, **args):
    _setup(**get_pkg_info(manifest, **args))
