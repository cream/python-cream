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

import os

try:
    XDG_DATA_DIRS = os.environ['XDG_DATA_DIRS'].split(':')
    XDG_DATA_HOME = os.environ['XDG_DATA_HOME'].split(':')
except:
    XDG_DATA_DIRS = ['/usr/share', '/usr/local/share']
    XDG_DATA_HOME = [os.path.expanduser('~/.local/share')]


CREAM_DIRS = [os.path.join(d, 'cream') for d in XDG_DATA_HOME + XDG_DATA_DIRS]

virtual_env = os.environ.get('VIRTUAL_ENV', '')
if virtual_env:
    CREAM_DIRS.append(os.path.join(virtual_env, 'share/cream/'))
