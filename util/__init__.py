def joindir(_file, *parts):
    import os
    return os.path.join(os.path.dirname(os.path.abspath(_file)), *parts)

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

def isiterable(iterable, flatten_strings=False, flatten_dicts=False):
    """
    Return `True` if `iterable` is iterable.
    If `iterable` is a string, return the value of `include_strings`.
    """
    if (not flatten_strings and isinstance(iterable, str)
        or not flatten_dicts and isinstance(iterable, dict)): return False
    else:
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
        yield iterable; return

    for item in iterable:
        if isiterable(item):
            for subitem in flatten(item, n=n, level=level+1):
                yield subitem
        else:
            yield item

class cached_property(object):
    # taken from werkzeug (BSD license, original author: Armin Ronacher)
    def __init__(self, func, name=None, doc=None):
        self.func = func
        self.__name__ = name or func.__name__
        self.__doc__ = doc or func.__doc__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.__name__, value)
        return value
