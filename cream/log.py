from time import strftime
import os

import sys
from cream.util import console

DEBUG = 5
NOTE = 4
WARNING = 3
ERROR = 2
FATAL = 1

VERBOSITY = 3

COLORS = {
    DEBUG: console.COLOR_YELLOW,
    NOTE: console.COLOR_GREEN,
    WARNING: console.COLOR_BLUE,
    ERROR: console.COLOR_RED,
    FATAL: console.COLOR_RED_BOLD,
}

SHORTS = {
    DEBUG: 'DBG',
    NOTE: 'NTC',
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


    def notice(self, message):
        self.process_message(NOTE, message)


    def warning(self, message):
        self.process_message(WARNING, message)


    def error(self, message):
        self.process_message(ERROR, message)


    def fatal(self, message):
        self.process_message(FATAL, message)


    def process_message(self, type, message):

        if self.verbosity >= type:
            s = '%(color)s [%(short)s @ %(time)s)] %(messages)s%(uncolor)s' % {
                'color'   : COLORS[type],
                'short'   : SHORTS[type],
                'time'    : strftime("%H:%M:%S"),
                'message' : message,
                'uncolor' : console.COLOR_NORMAL
            }
            print s
