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

try:
    XDG_DATA_DIRS = os.environ['XDG_DATA_DIRS'].split(':')
    XDG_DATA_HOME = os.environ['XDG_DATA_HOME'].split(':')
except:
    XDG_DATA_DIRS = ['/usr/share', '/usr/local/share']
    XDG_DATA_HOME = [os.path.expanduser('~/.local/share')]


CONFIG_DIRS = [os.path.join(d, 'cream/config') for d in XDG_DATA_HOME + XDG_DATA_DIRS]
MODULE_DIRS = [os.path.join(d, 'cream/modules') for d in XDG_DATA_HOME + XDG_DATA_DIRS]
DATA_DIRS = [os.path.join(d, 'cream/data') for d in XDG_DATA_HOME + XDG_DATA_DIRS]