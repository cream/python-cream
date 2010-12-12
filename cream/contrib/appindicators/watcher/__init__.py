"""
    A Python implementation of the status notifier standard.
    See http://www.notmart.org/misc/statusnotifieritem/

    Just kidding. Actually, it's an implementation of the KDE
    StatusNotifier standard that application-indicator seems
    to use.
"""

import dbus

import cream.ipc

# TODO: this should be org.freedesktop.StatusNotifierWatcher,
# but indicator-application doesn't conform to the standard here.
SERVICE_NAME = 'org.kde.StatusNotifierWatcher'
SERVICE_OBJECT = '/StatusNotifierWatcher'
PROTOCOL_VERSION = 'Ayatana Version 1'

ITEM_DEFAULT_OBJ = '/StatusNotifierItem'

def get_service_name(bus_name, path):
    """
        Get the service name of the (bus_name, path) combination.
        We need to transfer the bus name and the object path somehow.
        KDE's statusnotifieritem seems to do that by pasting
        these two together. That sounds funny enough. I'm going
        to try that, too.
    """
    return bus_name + path

def dissect_service_name(service):
    """
        See `get_service_name`.
    """
    if not '/' in service:
        raise ValueError('Malformed service name: %r' % service)
    idx = service.index('/')
    return (service[:idx], service[idx:])

class StatusNotifierWatcher(cream.ipc.Object):

    __ipc_signals__ = {
        'ServiceRegistered': ('s', 'org.kde.StatusNotifierWatcher'),
        'ServiceUnregistered': ('s', 'org.kde.StatusNotifierWatcher'),
        'NotificationHostRegistered': ('', 'org.kde.StatusNotifierWatcher'),
        'NotificationHostUnregistered': ('', 'org.kde.StatusNotifierWatcher')
    }

    def __init__(self):

        cream.ipc.Object.__init__(self,
            SERVICE_NAME,
            SERVICE_OBJECT
        )

        # A list of (bus name, path) of registered status notifier items.
        self.status_notifier_items = []
        # The service name of the currently running host or None.
        self.status_notifier_host = None

    def remove_item(self, service):

        print '--- removed item: %s' % service
        self.status_notifier_items.remove(dissect_service_name(service))
        self.emit_signal('ServiceUnregistered', service)

    # Interface.

    @dbus.service.method(dbus_interface=SERVICE_NAME,
                in_signature='s', out_signature='',
                sender_keyword='sender')
    def RegisterStatusNotifierItem(self, service, sender):

        print '--- registered item: %s' % service

        if service.startswith('/'):
            # We got an object path. Need to figure out the sender.
            add = (sender, service)
        else:
            # We got a bus name. Standard path.
            add = (service, ITEM_DEFAULT_OBJ)
        self.status_notifier_items.append(add)

        service = get_service_name(*add)

        def _name_owner_callback(name):
            """
                Called when a name owner has changed. If name is empty,
                the client has disconnected.
            """
            if not name:
                self.remove_item(service)

        self._bus.watch_name_owner(add[0], _name_owner_callback)
        self.emit_signal('ServiceRegistered', service)

    add_item = RegisterStatusNotifierItem

    @cream.ipc.method('s', '')
    def RegisterNotificationHost(self, service):

        print '--- registered host: %s' % service
        self.status_notifier_host = service
        self.emit_signal('NotificationHostRegistered')

    set_host = RegisterNotificationHost

    # According to the spec, these should be properties.

    @cream.ipc.method('', 'as')
    def RegisteredStatusNotifierItems(self):

        return [get_service_name(*item) for item in self.status_notifier_items]

    @cream.ipc.method('', 's')
    def ProtocolVersion(self):

        return PROTOCOL_VERSION

    @cream.ipc.method('', 'b')
    def IsNotificationHostRegistered(self):

        return bool(self.status_notifier_host)


if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

    watcher = StatusNotifierWatcher()

    import gobject
    mainloop = gobject.MainLoop()
    mainloop.run()
