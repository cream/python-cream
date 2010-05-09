def set_process_name(name):
    from procname import setprocname
    return setprocname(name)

def get_process_name():
    from procname import getprocname
    return getprocname()

def get_source_file(object):
    from inspect import getsourcefile
    return getsourcefile(object)

def joindir(_file, *parts):
    import os
    return os.path.join(os.path.dirname(os.path.abspath(_file)), *parts)

def walkfiles(*args, **kwargs):
    import os
    for directory, directories, files in os.walk(*args, **kwargs):
        for file_ in files:
            yield os.path.join(directory, file_)

def urljoin_multi(*parts):
    """
    Joins multiple strings into an url using a slash ('/'). Example::

        >>> urljoin_multi('http://cream-project.org', 'is', 'g', 'reat')
        http://cream-project.org/is/g/reat
        >>> urljoin_multi('http://cream-project.org', 'is', 'g/', 'reat/')
        http://cream-project.org/is/g/reat/
    """
    from urlparse import urljoin
    s = reduce(lambda a,b: urljoin(a, b).rstrip('/')+'/', parts)
    if not parts[-1].endswith('/'):
        s = s[:-1]
    return s

def isiterable(iterable, include_strings=False, include_dicts=True):
    if isinstance(iterable, basestring):
        return include_strings
    if isinstance(iterable, dict):
        return include_dicts
    try:
        iter(iterable)
        return True
    except TypeError:
        return False

def flatten(iterable, n=None, level=0):
    """
    Flatten a list or tuple.
    If `n` is set, stop at level `n`.

    Returns a generator.
    """
    if n is not None and level >= n:
        # reached max. level, don't flatten anymore
        yield iterable
        return

    for item in iterable:
        if isiterable(item, include_dicts=False):
            for subitem in flatten(item, n=n, level=level+1):
                yield subitem
        else:
            yield item

class cached_property(object):
    # taken from werkzeug (BSD license, original author: Armin Ronacher)
    not_none = False
    # if `not_none` is set, `cached_property` won't accept `None` as valid
    # `func` return value but will stay and wait for some non-`None` value.

    def __new__(cls, *args, **kwargs):
        if not args:
            from functools import partial
            return partial(cls, *args, **kwargs)
        else:
            return super(cls, cls).__new__(cls)

    def __init__(self, func, name=None, doc=None, not_none=False):
        self.func = func
        self.__name__ = name or func.__name__
        self.__doc__ = doc or func.__doc__
        self.not_none = not_none

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.func(obj)
        if self.not_none and value is None:
            return None
        setattr(obj, self.__name__, value)
        return value


def random_hash(bits=100, hashfunction='sha256'):
    from random import getrandbits
    import hashlib
    return getattr(hashlib, hashfunction)(str(getrandbits(bits))).hexdigest()
