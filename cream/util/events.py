import os, select

class Event(object):

    def __init__(self):
        self._read_fd, self._write_fd = os.pipe()

    def wait(self, timeout=None):
        rfds, wfds, efds = select.select([self._read_fd], [], [], timeout)
        return self._read_fd in rfds

    def is_set(self):
        return self.wait(0)

    def clear(self):
        if self.is_set():
            os.read(self._read_fd, 1)

    def set(self):
        if not self.is_set():
            os.write(self._write_fd, '1')

    def fileno(self):
        return self._read_fd

    def __del__(self):
        os.close(self._read_fd)
        os.close(self._write_fd)
