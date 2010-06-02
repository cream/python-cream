import dbus

INTERFACE = 'org.freedesktop.DBus.Properties'

def get(self, interface, name):
    return self.Get(interface, name, dbus_interface=INTERFACE)

def set(self, interface, name, value):
    self.Set(interface, name, value, dbus_interface=INTERFACE)

def get_all(self, interface):
    return self.GetAll(interface, dbus_interface=INTERFACE)
