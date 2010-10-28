#!/usr/bin/env python

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
