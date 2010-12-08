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

COLOR_RED = "\033[31m"
COLOR_RED_BOLD = "\033[1;31m"
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"
COLOR_PURPLE = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"
COLOR_GREY = "\033[37m"
COLOR_BLACK = "\033[30m"
COLOR_NORMAL = "\033[0m"

def colorized(string, color):
    """ Returns ``string`` in ``color`` """
    return color + string + COLOR_NORMAL

def get_tty_size():
    import subprocess
    p = subprocess.Popen(('stty', 'size'), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=True)
    size = p.stdout.readlines()[0].strip().split(' ')
    return map(int, reversed(size))
