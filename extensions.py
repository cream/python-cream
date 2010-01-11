import os
import sys
from . import ModuleBase
from .meta import MetaDataDB

META_TYPE_EXTENSION = 'Cream Extension'

EXTENSIONS = {}

def register(ext):

    # TODO: Error management!
    path = os.path.abspath(inspect.getsourcefile(ext))
    EXTENSIONS[path] = ext
    return ext


class Extension(ModuleBase):
    """ Class for building extensions. """

    def __init__(self, interface):
        """
        :param interface: An `cream.extensions.ExtensionInterface`.
        """
        ModuleBase.__init__(self)
        self.interface = interface

        self.path = self._base_path


class ExtensionManager(object):
    """ Class for managing extensions. """

    def __init__(self, paths, interface=None):

        self.paths = paths
        self.interface = interface

        self.extensions = MetaDataDB(self.paths[0]) # TODO: multiple paths


    def list(self):
        return self.extensions


    def load_by_name(self, name, interface=None):

        ext = self.extensions.get_by_name(name)
        self._load(ext, interface)


    def load_by_hash(self, hash, interface=None):

        ext = self.extensions.get_by_hash(hash)
        self._load(ext, interface)


    def _load(self, extension, interface=None):
        import imp

        module_name = os.path.splitext(os.path.basename(extension['file']))[0]
        module_path = extension['path']

        os.chdir(module_path)

        # Backing up original search path and inserting path of extension.
        _path = sys.path
        sys.path.insert(0, module_path)

        # Importing the extension as a python module.
        file, pathname, description = imp.find_module(module_name, [module_path])
        mod = imp.load_module(module_name, file, pathname, description)

        # Getting and instantiating the extension class.
        cls = getattr(mod, EXTENSIONS[os.path.join(module_path, module_name + '.py')].__name__)
        cls(interface or self.interface)

        # Restoring original search path.
        sys.path = _path


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
