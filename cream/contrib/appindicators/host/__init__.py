import os

import dbus
import gobject

import cream.ipc
from cream.util import cached_property

from cream.contrib.appindicators import watcher
from cream.contrib.appindicators.dbusmenu import DBusMenu
from cream.contrib.appindicators.dbusmenu.dbusmenu_gtk import DBusMenuGTK

SERVICE_NAME = 'org.kde.StatusNotifierHost-%d' % os.getpid()
SERVICE_OBJECT = '/org/cream/StatusNotifierHost'
ITEM_INTERFACE = 'org.kde.StatusNotifierItem'

class Status(object):
    Passive = 'Passive'
    Active = 'Active'
    NeedsAttention = 'NeedsAttention'

class ItemProxy(dbus.Interface, gobject.GObject):
    __gsignals__ = {
        'icon-new': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'attention-icon-new': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'status-new': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    def __init__(self, bus, service):
        """
            With extra service name dissection!
        """
        self.bus = bus
        self.service = service
        bus_name, path = watcher.dissect_service_name(service)
        dbus.Interface.__init__(self, bus.get_object(bus_name, path), dbus_interface=ITEM_INTERFACE)
        gobject.GObject.__init__(self)
        # I wanna getse events.
        self.connect_to_signal('NewIcon', self.on_new_icon)
        self.connect_to_signal('NewAttentionIcon', self.on_new_attention_icon)
        self.connect_to_signal('NewStatus', self.on_new_status)
        # Make sure `id` is cached.
        self.id = self._id

    def on_new_icon(self):
        del self.cached_icon_filename
        self.emit('icon-new')

    def on_new_attention_icon(self):
        del self.cached_attention_icon_filename
        self.emit('attention-icon-new')

    def on_new_status(self, status):
        self.emit('status-new', status)

    # gobject tries to call `do_$signal` for every signal.
    # dbus tries to translate this to a call and chokes.
    # workaround time!
    def do_status_new(self, status):
        pass

    def do_new_icon(self):
        pass

    def do_new_attention_icon(self):
        pass

    def get_property(self, name):
        return cream.ipc.properties.get(self.proxy_object, ITEM_INTERFACE, name)

    def show_menu(self):
        self.dbusmenu_gtk.popup()

    _id = property(lambda self: self.get_property('Id'))
    category = property(lambda self: self.get_property('Category'))
    status = property(lambda self: self.get_property('Status'))
    icon_name = property(lambda self: self.get_property('IconName'))
    attention_icon_name = property(lambda self: self.get_property('AttentionIconName'))
    icon_theme_path = property(lambda self: self.get_property('IconThemePath'))
    menu = property(lambda self: self.get_property('Menu'))
    dbusmenu = property(lambda self: DBusMenu(self.bus, self.bus_name, self.menu))
    dbusmenu_gtk = cached_property(lambda self: DBusMenuGTK(self.dbusmenu))

    def get_icon_filename(self):
        import gtk
        theme = gtk.icon_theme_get_default()
        if self.icon_theme_path:
            theme.append_search_path(self.icon_theme_path)
        info = theme.lookup_icon(self.icon_name, gtk.ICON_SIZE_LARGE_TOOLBAR, 0)
        if info is None:
            raise ValueError('Icon wasn\'t found! %r' % self.icon_name)
        return info.get_filename()

    def get_attention_icon_filename(self):
        import gtk
        theme = gtk.icon_theme_get_default()
        if self.icon_theme_path:
            theme.append_search_path(self.icon_theme_path)
        info = theme.lookup_icon(self.attention_icon_name, gtk.ICON_SIZE_LARGE_TOOLBAR, 0)
        if info is None:
            raise ValueError('Icon wasn\'t found! %r' % self.attention_icon_name)
        return info.get_filename()

    cached_icon_filename = cached_property(get_icon_filename)
    cached_attention_icon_filename = cached_property(get_attention_icon_filename)

    def get_current_icon_filename(self):
        if self.status == Status.NeedsAttention:
            return self.get_attention_icon_filename()
        else:
            return self.get_icon_filename()

class StatusNotifierHost(cream.ipc.Object):
    __gsignals__ = {
        'item-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'item-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }

    def __init__(self):

        cream.ipc.Object.__init__(self,
            SERVICE_NAME,
            SERVICE_OBJECT,
            )

        self.bus = dbus.SessionBus()
        self.watcher = self.bus.get_object(watcher.SERVICE_NAME, watcher.SERVICE_OBJECT)
        self.items = []

        self.register()

    def get_item_proxy(self, service):
        return ItemProxy(self.bus, service)

    def register(self):
        """
            Register myself with the watcher.
        """
        self.watcher.RegisterNotificationHost(SERVICE_NAME)
        self.watcher.connect_to_signal('ServiceRegistered', self.on_service_registered)
        self.watcher.connect_to_signal('ServiceUnregistered', self.on_service_unregistered)
        # Add all existing items.
        for service in self.watcher.RegisteredStatusNotifierItems():
            self.add_item(self.get_item_proxy(service))

    def add_item(self, item):
        print 'Hell yeah!'
        for prop in ('id', 'category', 'status', 'icon_name', 'attention_icon_name', 'icon_theme_path', 'menu'):
            print ' - %r = %r' % (prop, getattr(item, prop))
        self.items.append(item)
        self.emit('item-added', item)

    def remove_item(self, service):
        for hell_yeah_item in self.items:
            if hell_yeah_item.service == service:
                print 'Hell no! Removed %r' % hell_yeah_item
                self.items.remove(hell_yeah_item)
                self.emit('item-removed', hell_yeah_item)
                return
        raise ValueError('Not found: %r' % service)

    def get_item_by_id(self, id):
        for item in self.items:
            if item.id == id:
                return item
        raise ValueError('Not found. %r' % id)

    def on_service_registered(self, service):
        """
            Called when the watcher gets a new service registered. Add the item.
        """
        self.add_item(self.get_item_proxy(service))

    def on_service_unregistered(self, service):
        print 'Oh no! %r got unregistered. :-(' % service
        self.remove_item(service)

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

    host = StatusNotifierHost()

    import gobject
    mainloop = gobject.MainLoop()
    mainloop.run()

