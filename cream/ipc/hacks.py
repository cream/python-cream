# Copyright: 2007-2013, Sebastian Billaudelle <sbillaudelle@googlemail.com>
#            2010-2013, Kristoffer Kleine <kris.kleine@yahoo.de>

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import dbus
import dbus.service

def add_method(cls, func, *args, **kwargs):
    """
    add a method to the dbus.service.Object subclass *cls*.
    *func* is the function (don't forget the `self` argument),
    all further arguments are passed verbatim to the
    `dbus.service.method` decorator function.
    This function will add *func* as an attribute to *cls*.
    """

    func = dbus.service.method(*args, **kwargs)(func)
    name = func.__name__

    # some dirty magic follows.
    # patch together some "qualificated" class name.
    # It consists of the module and the class name.
    clsname = '.'.join((cls.__module__, cls.__name__))

    # dbus-python uses a magic `_dbus_class_table` class attribute
    # for storing the methods. It contains some nested dictionaries.
    # The keys are the class names, and the values are dictionaries
    # mapping interface names to dictionaries that map method names
    # to Python functions. Wow.
    # So, we add the new method to the class table here.
    entry = cls._dbus_class_table.setdefault(clsname, {})

    # We just steal the name of the interface from the function.
    # `dbus.service.method` added it for us.
    entry.setdefault(func._dbus_interface, {})[name] = func

    # Finally we set it as an attribute.
    setattr(cls, name, func)

def create_signal_emitter(name, signature, interface, argnames):

    f = lambda *args: None
    f.__name__ = name
    f._dbus_is_signal = True
    f._dbus_interface = interface
    f._dbus_signature = signature
    f._dbus_args = argnames
    return f

def add_signal(cls, name, signature, interface):
    """
        adds a signal named *name* with the signature *signature*
        to the dbus class *cls*.
        If you call the signal emitter, nothing will happen. You
        have to do that yourself.
    """

    # get the argcount from the signature
    signal_argcount = len(list(dbus.Signature(signature))) # len(dbus.Signature(...)) gives strange results
    argnames = ['arg%d' % i for i in xrange(signal_argcount + 1)]
    func = create_signal_emitter(name, signature, interface, argnames)

    # now, essentially the same dirty magic as in `add_function`
    # is done. See above for explanation.
    clsname = '.'.join((cls.__module__, cls.__name__))
    entry = cls._dbus_class_table.setdefault(clsname, {})
    entry.setdefault(func._dbus_interface, {})[name] = func
    setattr(cls, name, func)
