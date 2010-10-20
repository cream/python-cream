import gobject

class Subprocess(gobject.GObject):
    """ GObject API for handling child processes. """

    __gtype_name__ = 'Subprocess'
    __gsignals__ = {
        'exited': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT))
        }

    def __init__(self, command, name=None):

        gobject.GObject.__init__(self)

        self.process = None
        self.pid = None
        self.stdout = None
        self.stderr = None

        self.command = command
        self.name = name


    def run(self):
        """ Run the process. """

        process_data = gobject.spawn_async(self.command,
                flags=gobject.SPAWN_SEARCH_PATH|gobject.SPAWN_DO_NOT_REAP_CHILD,
                standard_output=True,
                standard_error=True
                )

        self.pid = process_data[0]
        self.stdout = os.fdopen(process_data[2])
        self.stderr = os.fdopen(process_data[3])

        self.watch = gobject.child_watch_add(self.pid, self.exited_cb)


    def exited_cb(self, pid, condition):
        self.emit('exited', pid, condition)
