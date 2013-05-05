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

from time import strftime
import os

import sys
from cream.util import console

DEBUG = 5
INFO = 4
WARNING = 3
ERROR = 2
FATAL = 1

VERBOSITY = 3

COLORS = {
    DEBUG: console.COLOR_YELLOW,
    INFO: console.COLOR_GREEN,
    WARNING: console.COLOR_BLUE,
    ERROR: console.COLOR_RED,
    FATAL: console.COLOR_RED_BOLD,
}

SHORTS = {
    DEBUG: 'DBG',
    INFO: 'INF',
    WARNING: 'WRN',
    ERROR: 'ERR',
    FATAL: 'FTL',
}

class Messages(object):

    def __init__(self, id=None):

        self.id = id

        self.verbosity = int(os.getenv('CREAM_VERBOSITY', '0')) or VERBOSITY


    def debug(self, message):
        self.process_message(DEBUG, message)


    def info(self, message):
        self.process_message(INFO, message)


    def warning(self, message):
        self.process_message(WARNING, message)


    def error(self, message):
        self.process_message(ERROR, message)


    def fatal(self, message):
        self.process_message(FATAL, message)


    def process_message(self, type, message):

        if self.verbosity >= type:
            s = '%(color)s [%(short)s @ %(time)s] %(message)s%(uncolor)s' % {
                'color'   : COLORS[type],
                'short'   : SHORTS[type],
                'time'    : strftime("%H:%M:%S"),
                'message' : message,
                'uncolor' : console.COLOR_NORMAL
            }
            print s
