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
from lxml.etree import parse as parse_xml_file

class ManifestException(BaseException):
    pass

class NoNamespaceDefinedException(BaseException):
    pass

class Manifest(dict):

    def __init__(self, path):

        dict.__init__(self)

        self._path = path
        self._tree = parse_xml_file(self._path)

        root = self._tree.getroot()
        if not root.tag == 'manifest':
            raise ManifestException

        namespaces = []

        def append_ns(e):
            if e.get('namespace'):
                namespaces.append(e.get('namespace'))

        def remove_ns(e):
            if e.get('namespace'):
                namespaces.remove(e.get('namespace'))

        def expand_ns(s):
            if s.startswith('.'):
                if len(namespaces):
                    return namespaces[-1] + s
                else:
                    raise NoNamespaceDefinedException
            else:
                return s

        def expand_path(p):
            if p:
                return os.path.join(os.path.dirname(self._path), p)

        append_ns(root)

        component = root.find('component')
        append_ns(component)

        # General meta information:
        self['id'] = expand_ns(component.get('id'))
        self['type'] = expand_ns(component.get('type'))
        self['name'] = component.get('name')
        self['version'] = component.get('version')
        self['entry'] = expand_path(component.get('entry'))

        # Licenses:
        self['licenses'] = []

        licenses = component.findall('license')
        for l in licenses:
            append_ns(l)
            self['licenses'].append({
                'title': l.get('title'),
                'version': l.get('version')
                })
            remove_ns(l)

        # Icons:
        self['icons'] = {
            'scalable': None
            }

        icons = component.findall('icon')
        for i in icons:
            append_ns(i)
            self['icons'][i.get('size')] = expand_path(i.get('path'))
            remove_ns(i)

        # Descriptions:
        self['descriptions'] = {
            }

        descriptions = component.findall('description')
        for d in descriptions:
            append_ns(d)
            self['descriptions'][d.get('lang')] = d.get('content')
            remove_ns(d)

        self['description'] = self['descriptions'].get('en') or ''

        # Authors:
        self['authors'] = []

        authors = component.findall('author')
        for a in authors:
            append_ns(a)
            self['authors'].append({
                'name': a.get('name'),
                'type': a.get('type'),
                'mail': a.get('mail')
                })
            remove_ns(a)

        # Features:
        self['features'] = []

        features = component.findall('use-feature')
        for f in features:
            append_ns(f)
            self['features'].append(expand_ns(f.get('id')))
            remove_ns(f)

        # Dependencies:
        self['dependencies'] = []

        dependencies = component.findall('dependency')
        for d in dependencies:
            append_ns(d)
            self['dependencies'].append({
                'id': expand_ns(d.get('id')),
                'type': expand_ns(d.get('type')),
                'required': d.get('required')
                })
            remove_ns(d)

        # Provided component types:
        self['provided-components'] = []

        provided_components = component.findall('provide-component')
        for c in provided_components:
            append_ns(c)
            self['provided-components'].append(expand_ns(c.get('type')))
            remove_ns(c)


        # Package information:
        package = root.find('package')
        if package is None:
            return

        self['package'] = {}

        if package.get('auto') == 'true':
            self['package']['auto'] = True
        else:
            self['package']['auto'] = False

        self['package']['rules'] = {
            'ignore': [],
            'application': [],
            'desktop': [],
            'icon': [],
            'library': [],
            }

        rules = package.findall('rule')
        for r in rules:
            type = r.get('type')
            files = r.get('files')
            self['package']['rules'][type].append(files)


    def __str__(self):
        return "<Manifest '{0}'>".format(self._path)


class ManifestDB(object):

    def __init__(self, path, type=None):

        self.path = path
        self.type = type

        self.by_name = {}
        self.by_id = {}

        self.scan()


    def scan(self):

        res = self._scan(self.path, self.type)

        for i in res:
            self.by_name[i['name']] = i
            self.by_id[i['id']] = i


    def get_by_name(self, name):
        return self.by_name[name]


    def get_by_id(self, id):
        return self.by_id[id]


    def _scan(self, path, type=None):

        path = os.path.abspath(path)
        files = os.listdir(path)
        res = []

        for file in files:
            if os.path.isdir(os.path.join(path, file)):
                res.extend(self._scan(os.path.join(path, file), type))
            else:
                if file == 'manifest.xml':
                    m = Manifest(os.path.join(path, file))
                    if not type or m['type'] == type:
                        res.append(m)

        return res
