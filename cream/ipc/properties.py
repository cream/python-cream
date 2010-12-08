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

import dbus

INTERFACE = 'org.freedesktop.DBus.Properties'

def get(self, interface, name):
    return self.Get(interface, name, dbus_interface=INTERFACE)

def set(self, interface, name, value):
    self.Set(interface, name, value, dbus_interface=INTERFACE)

def get_all(self, interface):
    return self.GetAll(interface, dbus_interface=INTERFACE)
