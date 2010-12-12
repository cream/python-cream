import os
from subprocess import Popen, PIPE
import re

import gobject
import gtk
import dbus

import cream.ipc
from cream.ipc import properties
from cream.util import cached_property

ACTION = 'org.freedesktop.udisks.filesystem-mount'
COOKIE = 'cream-volume-manager-yay'
MOUNT_POINT_RE = re.compile('^mount point to be used: (.*)$', re.MULTILINE)

def mount(device):
    proc = Popen(['pmount', '-d', device], stdout=PIPE)
    stdout = proc.communicate()[0]
    return MOUNT_POINT_RE.search(stdout).group(1)

def unmount(device):
    if os.path.exists(device):
        proc = Popen(['pumount', device])
        proc.wait()

class Device(dbus.Interface):
    def __init__(self, path):
        dbus.Interface.__init__(self,
            cream.ipc.SYSTEM_BUS.get_object('org.freedesktop.UDisks', path),
            'org.freedesktop.UDisks.Device'
        )

    def get_property(self, name):
        return properties.get(self, self.dbus_interface, name)

    fstype = cached_property(lambda self: self.get_property('IdType'))
    label = cached_property(lambda self: self.get_property('IdLabel'))

    @cached_property
    def device_file(self):
        return self.get_property('DeviceFile')

    @cached_property
    def description(self):
        return self.label or self.device_file

    def mount(self):
        return mount(self.device_file)

    def unmount(self):
        unmount(self.device_file)

class UDisks(dbus.Interface, gobject.GObject):
    __gsignals__ = {
        'device-mounted': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING)),
        'device-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self):
        dbus.Interface.__init__(self,
            cream.ipc.SYSTEM_BUS.get_object('org.freedesktop.UDisks', '/org/freedesktop/UDisks'),
            'org.freedesktop.UDisks'
        )
        gobject.GObject.__init__(self)
        self.devices = {}
        self.connect_to_signal('DeviceAdded', self.on_device_added)
        self.connect_to_signal('DeviceRemoved', self.on_device_removed)

    # !!%!%!%!%!%!%%!
    def do_device_mounted(self, fu, ub):
        pass

    def on_device_added(self, path):
        device = Device(path)
        if device.fstype:
            mount_path = device.mount()
            self.devices[path] = device
            self.emit('device-mounted', device, mount_path)

    def do_device_removed(self, fu):
        pass

    def on_device_removed(self, path):
        try:
            device = self.devices[path]
        except KeyError:
            pass # TODO?
        else:
            device.unmount()
            self.emit('device-removed', device)
            del self.devices[path]

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

    udisks = UDisks()

    import gobject
    mainloop = gobject.MainLoop()
    mainloop.run()


