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

    def __init__(self, path, expand_paths=True):

        dict.__init__(self)

        self._path = path
        self._tree = parse_xml_file(self._path)

        self['path'] = os.path.dirname(os.path.abspath(path))

        root = self._tree.getroot()
        if root.tag != 'manifest':
            raise ManifestException("Manifest root tag has to 'manifest'")

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
            if expand_paths:
                if p:
                    return os.path.join(os.path.dirname(self._path), p)
            else:
                return p

        # TODO: Use a bottom-down iteration here and lookup node handlers
        # from a dict or so. Much faster!

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
        for license in licenses:
            append_ns(license)
            self['licenses'].append({
                'title'   : license.get('title'),
                'version' : license.get('version')
            })
            remove_ns(license)

        # Icon:
        icon = component.find('icon')
        if icon is not None:
            append_ns(icon)
            self['icon'] = expand_path(icon.get('path'))
            remove_ns(icon)
            
        # Category
        self['categories'] = []
        
        categories = component.findall('category')
        for category in categories:
            append_ns(category)
            self['categories'].append({
                'id'  : expand_ns(category.get('id'))
            })
            remove_ns(category)

        # Descriptions:
        self['descriptions'] = {}

        descriptions = component.findall('description')
        for descr in descriptions:
            append_ns(descr)
            self['descriptions'][descr.get('lang')] = descr.get('content')
            remove_ns(descr)

        self['description'] = self['descriptions'].get('en') or ''

        # Authors:
        self['authors'] = []

        authors = component.findall('author')
        for author in authors:
            append_ns(author)
            self['authors'].append({
                'name': author.get('name'),
                'type': author.get('type'),
                'mail': author.get('mail')
                })
            remove_ns(author)

        # Features:
        self['features'] = []

        features = component.findall('use-feature')
        for feature in features:
            append_ns(feature)
            self['features'].append(
                (expand_ns(feature.attrib.pop('id')), feature.attrib)
            )
            remove_ns(feature)

        # Dependencies:
        self['dependencies'] = []

        dependencies = component.findall('dependency')
        for dependency in dependencies:
            append_ns(dependency)
            self['dependencies'].append({
                'id'        : expand_ns(dependency.get('id')),
                'type'      : expand_ns(dependency.get('type')),
                'required'  : dependency.get('required')
                })
            remove_ns(dependency)

        # Provided component types:
        self['provided-components'] = []

        provided_components = component.findall('provide-component')
        for component in provided_components:
            append_ns(component)
            self['provided-components'].append(expand_ns(component.get('type')))
            remove_ns(component)


        # Package information:
        package = root.find('package')
        if package is None:
            return

        self['package'] = {}

        self['package']['auto'] = package.get('auto') == 'true'

        self['package']['rules'] = {
            'ignore': [],
            'application': [],
            'desktop': [],
            'icon': [],
            'library': [],
        }

        rules = package.findall('rule')
        for rule in rules:
            type  = rule.get('type')
            files = rule.get('files')
            self['package']['rules'][type].append(files)


    def __str__(self):
        return "<Manifest '{0}'>".format(self._path)


class ManifestDB(object):

    def __init__(self, paths, t=None):

        if not type(paths) == list:
            self.paths = [paths]
        else:
            self.paths = paths
        self.type = t

        self.by_name = {}
        self.by_id = {}

        self.scan()


    def scan(self):

        for p in self.paths:
            try:
                res = self._scan(p, self.type)
        
                for i in res:
                    self.by_name[i['name']] = i
                    self.by_id[i['id']] = i
            except:
                pass


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
