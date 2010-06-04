import os
import sys
import inspect
import imp

from . import Component
from .manifest import ManifestDB

META_TYPE_EXTENSION = 'Cream Extension'

EXTENSIONS = {}

def register(ext):

    # TODO: Error management!
    path = os.path.abspath(inspect.getsourcefile(ext))
    EXTENSIONS[path] = ext
    return ext


class Extension(Component):
    """ Class for building extensions. """

    def __init__(self, interface):
        """
        :param interface: An `cream.extensions.ExtensionInterface`.
        """
        Component.__init__(self)
        self.interface = interface


class ExtensionManager(object):
    """ Class for managing extensions. """

    def __init__(self, paths, interface=None):

        self.paths = paths
        self.interface = interface

        self.extensions = ManifestDB(self.paths[0], type='org.cream.Extension') # TODO: multiple paths


    def list(self):
        return self.extensions


    def load_all(self, interface=None):
        return map(lambda ext: self._load(ext, interface),
                   self.extensions.by_name.itervalues())

    def load_by_name(self, name, interface=None):

        ext = self.extensions.get_by_name(name)
        return self._load(ext, interface)


    def load_by_hash(self, hash, interface=None):

        ext = self.extensions.get_by_hash(hash)
        return self._load(ext, interface)


    def _load(self, extension, interface=None):
        # '/foo/bar/extensions/myext.py' --> 'myext'
        module_name = os.path.splitext(os.path.basename(extension['entry']))[0]
        module_path = extension['path']

        sys.path.append(module_path)

        # Importing the extension as a python module.
        file, pathname, description = imp.find_module(module_name, [module_path])
        mod = imp.load_module(module_name, file, pathname, description)

        # Getting and instantiating the extension class.
        cls = getattr(mod, EXTENSIONS[os.path.join(module_path, module_name + '.py')].__name__)
        instance = cls(interface or self.interface)

        sys.path.remove(module_path)

        return instance


class ExtensionInterface(object):
    """ Class for building an API for extensions. """

    def __init__(self, interface):
        """
        :param interface: A `dict` containing the API for extensions:

        Example::

            ExtensionInterface({
                'foo': foo_function,
                'bar': bar_function
            })
        """

        self.interface = interface


    def __getattr__(self, key):

        return self.interface[key]
