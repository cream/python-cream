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
from distutils.core import setup as _setup
from cream.manifest import Manifest

MODULE_DIR = 'share/cream/modules/{pkg_name}'

def slugify(s):
    return s.lower().replace(' ', '-')


def discover(path):
    manifest = Manifest(path)

    return {
        'name': slugify(manifest['name']),
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

    print pkg_info
    return pkg_info

def setup(manifest=None, **args):
    _setup(**get_pkg_info(manifest, **args))
