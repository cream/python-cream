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
import sys
import gobject

class Subprocess(gobject.GObject):
    """
    GObject API for handling child processes.

    :param command: The command to be run as a subprocess.
    :param fork: If `True` this process will be detached from its parent and
                 run independent. This means that no excited-signal will be emited.

    :type command: `list`
    :type fork: `bool`
    """

    __gtype_name__ = 'Subprocess'
    __gsignals__ = {
        'exited': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))
        }

    def __init__(self, command, name=None, fork=False):

        gobject.GObject.__init__(self)

        self.process = None
        self.pid = None
        self.stdout = None
        self.stderr = None

        self.command = command
        self.name = name
        self.forked = fork

        if fork:
            self.fork()


    def run(self):
        """ Run the process. """

        process_data = gobject.spawn_async(self.command,
                flags=gobject.SPAWN_SEARCH_PATH|gobject.SPAWN_DO_NOT_REAP_CHILD
                )

        self.pid = process_data[0]

        self.watch = gobject.child_watch_add(self.pid, self.exited_cb)

        return self.pid


    def exited_cb(self, pid, condition):
        if not self.forked:
            self.emit('exited', pid, condition)


    def fork(self):
        try:
            # first fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            # second fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.exit(1)