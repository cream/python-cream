# Copyright: 2007-2013, Sebastian Billaudelle <sbillaudelle@googlemail.com>
#            2010-2013, Kristoffer Kleine <kris.kleine@yahoo.de>

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import dbus

INTERFACE = 'org.freedesktop.DBus.Properties'

def get(self, interface, name):
    return self.Get(interface, name, dbus_interface=INTERFACE)

def set(self, interface, name, value):
    self.Set(interface, name, value, dbus_interface=INTERFACE)

def get_all(self, interface):
    return self.GetAll(interface, dbus_interface=INTERFACE)
