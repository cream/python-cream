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

from cream.config.frontend import Frontend
from cream.config.backend import Backend


class Configuration(object):

    def __init__(self, schema):

        self.backend = Backend(schema)
        self.frontend = Frontend(self.backend.profiles)

        self.frontend.connect('profile-selected', lambda f, p: self.backend.set_profile(p))
        self.frontend.connect('profile-added', lambda f, p: self.backend.add_profile(p))
        self.frontend.connect('profile-removed', lambda f, p: self.backend.remove_profile(p))
        self.frontend.connect('value-changed', lambda f, k, v: self.backend.set_value(k, v))


    def show_dialog(self):

        self.frontend.run()

    def save(self):

        self.backend.save()



    def __getattr__(self, name):

        if name in self.backend:
            return self.backend.get_value(name)

        raise AttributeError("No such attribute '{0}'".format(name))


    def __setattr__(self, name, value):

        if 'frontend' in self.__dict__ and name in self.backend:
            return self.backend.set_value(name, value)
        else:
            return object.__setattr__(self, name, value)

        raise AttributeError("No such attribute '{0}'".format(name))


if __name__ == '__main__':
    conf = Configuration('org.cream.melange')

    conf.show_dialog()
