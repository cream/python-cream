# object oriented wrapper to parts of the os module.
# buggy, haven't tried to use it yet, so don't use.
import os
from .import cached_property

alias = property # just for noow


class FileSystemPath(object):
    def __init__(self, path):
        self._path = path

    def join(self, *parts):
        return os.path.join(self._path, *parts)

    def norm(self):
        self._path = os.path.normcase(self._path)


class FileSystemObject(object):
    def __init__(self, path, expanduser=True):
        if expanduser:
            path = os.path.expanduser(path)
        self._path = FileSystemPath(path)

    def chmod(self, mode):
        return os.chmod(self._path, mode)

    def chown(self, user_id=-1, group_id=-1):
        return os.chown(self._path, user_id, group_id)

    def delete(self):
        raise NotImplementedError()

    def stat(self):
        return os.stat(self._path)

    @cached_property
    def abspath(self):
        return os.path.abspath(self._path)

    @alias
    def absolute_path(self):
        return self.abspath

    @cached_property
    def basename(self):
        return os.path.basename(self._path)

    @cached_property
    def dirname(self):
        return os.path.dirname(self._path)

    def exists(self):
        return os.path.exists(self._path)

    def isdir(self):
        return os.path.isdir(self._path)

    def isfile(self):
        return os.path.isfile(self._path)

    @cached_property
    def relpath(self):
        return os.path.relpath(self._path)

    @alias
    def relative_path(self):
        return self.relpath


class Directory(FileSystemObject):
    def list(self):
        for f in os.listdir(self._path):
            f = os.path.join(self._path, f)
            if os.path.isfile(f):
                yield File(f)
            else:
                yield Directory(f)

    def make(self, mode=0777):
        return os.mkdir(self._path, mode)

    def make_recursive(self, mode=0777):
        if not os.path.isdir(self._path):
            return os.makedirs(self._path, mode)

    def delete(self):
        return os.rmdir(self._path)

    def delete_recursive(self):
        return os.removedirs(self._path)

    def walk(self, *args, **kwargs):
        return os.walk(self, *args, **kwargs)


class File(FileSystemObject):
    _fobj = None

    @cached_property
    def name(self):
        return self.basename

    @cached_property
    def prefix(self):
        return os.path.splitext(self.basename)[1]

    @cached_property
    def mimetype(self):
        import mimetypes
        return mimetypes.guess_type(self._path)

    def isopen(self):
        return self._fobj is None

    def open(self, mode='r'):
        if self.isopen():
            if self._fmode != mode:
                self.close()
            else:
                return self._fobj
        self._fobj = open(self._path, mode)

    def close(self):
        if not self.isopen():
            raise OSError("Cannot close non-open files")
        self._fobj.close()

    @property
    def read(self):
        if not self.isopen():
            self.open()
        return self._fobj.read

    def readlines(self):
        if not self.isopen():
            self.open()
        return self._fobj.readlines

    def delete(self):
        os.remove(self._path)
