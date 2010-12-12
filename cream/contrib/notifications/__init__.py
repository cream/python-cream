import gobject

import cream.ipc

from .spec import Server, Notification

FRONTEND_MANAGER_SERVICE_NAME = 'org.cream.notifications.FrontendManager'
FRONTEND_MANAGER_SERVICE_OBJECT = '/org/cream/notifications/FrontendManager'

NOTIFICATION_CODE = 'ususssasa{sv}i'

def notification_to_dbus(n):
    return (n.id,
            n.app_name,
            n.replaces_id,
            n.app_icon,
            n.summary,
            n.body,
            n.action_array,
            n.hints,
            n.expire_timeout)

class FrontendManager(cream.ipc.Object):
    __ipc_signals__ = {
        'show_notification': NOTIFICATION_CODE,
        'hide_notification': NOTIFICATION_CODE,
    }

    def __init__(self):
        cream.ipc.Object.__init__(self,
                FRONTEND_MANAGER_SERVICE_NAME,
                FRONTEND_MANAGER_SERVICE_OBJECT
                )

        self.server = Server()
        self.server.connect('get-capabilities', self.sig_get_capabilities)
        self.server.connect('show-notification', self.sig_show_notification)
        self.server.connect('hide-notification', self.sig_hide_notification)

        self.frontends = {} # bus name: capabilities

    def sig_get_capabilities(self, server):
        """
            Return ALL capabilities.
        """
        all_caps = set()
        for caps in self.frontends.itervalues():
            all_caps.add(caps)
        return list(all_caps)

    def sig_show_notification(self, server, notification):
        self.emit_signal('show_notification', *notification_to_dbus(notification))

    def sig_hide_notification(self, server, notification):
        self.emit_signal('hide_notification', *notification_to_dbus(notification))

    @cream.ipc.method('sas', '')
    def register(self, bus_name, capabilities):
        self.frontends[str(bus_name)] = list(capabilities)

class Frontend(cream.ipc.Object):
    __gsignals__ = {
        'show-notification': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'hide-notification': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self, service_name, service_object, capabilities):
        cream.ipc.Object.__init__(self, service_name, service_object)
        self.capabilities = capabilities
        self.manager = cream.ipc.get_object('org.cream.notifications.FrontendManager')
        self.notifications = {} # id: Notification
        # register
        self.register()
        # connect to signals
        self.manager.connect_to_signal('show_notification', self.on_show_notification)
        self.manager.connect_to_signal('hide_notification', self.on_hide_notification)

    def on_show_notification(self, *args):
        notification = Notification(*args)
        self.emit('show-notification', notification)
        self.notifications[notification.id] = notification

    def on_hide_notification(self, *args):
        id = args[0]
        if id in self.notifications:
            self.emit('hide-notification', self.notifications[id])
            del self.notifications[id]
        else:
            pass # TODO: really just ignore?

    def register(self):
        """
            register myself with the frontend manager.
        """
        self.manager.register(self._bus_name, self.capabilities)

