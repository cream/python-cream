import time

from lxml import etree

import gobject
import dbus

import cream.ipc

DBUSMENU_INTERFACE = 'org.ayatana.dbusmenu'
DEFAULTS = {
    'type': 'standard',
    'label': '',
    'enabled': True,
    'visible': True,
    'icon-name': '',
    'icon-data': '',
    'toggle-type': '',
    'toggle-state': -1,
    'children-display': True,
}

class Menu(gobject.GObject):
    """
        A Menu instance describes a node inside a menu structure. It has
        an `id` attribute holding the Menu ID (yeah, you guessed right) and
        a `children` attribute that is a list of Menu instances.
        Also, `layout` is a backref to the `Layout` object.
    """
    __gsignals__ = {
        'property-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'properties-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'children-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }

    def __init__(self, layout, id, children=None):
        gobject.GObject.__init__(self)
        self.layout = layout
        self.id = id
        if children is None:
            children = []
        self.children = children
        self.update_cache()

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return '<%s object #%d at 0x%x (%d children)>' % (self.__class__, self.id, id(self), len(self.children))

    def update_children(self, tree):
        menu = self.__class__.parse_tree(self.layout, tree)
        assert menu.id == self.id
        self.children = menu.children
        self.emit('children-changed')

    def add_child(self, menu):
        self.children.append(menu)

    def find_item(self, id):
        if self.id == id:
            return self
        else:
            for child in self.children:
                item = child.find_item(id)
                if item is not None:
                    return item

    def on_item_updated(self):
        self.update_cache()
        self.emit('properties-changed')

    def on_item_property_updated(self, name, value):
        self.update_cache_for(name, value)
        self.emit('property-changed', name)

    def event(self, event_id, data='', timestamp=None):
        self.layout.dbusmenu.event(self.id, event_id, data, timestamp)

    def cache_property(self, name, value):
        """
            Store *name*'s value *value* in the cache.
        """
        self.properties_cache[name] = value

    def update_cache(self):
        """
            Invalidate cache, refill
        """
        self.properties_cache = DEFAULTS.copy()
        self.properties_cache.update(self.get_properties([]))

    def update_cache_for(self, name, value):
        """
            Just update *name*.
        """
        self.properties_cache[name] = value

    def is_cached_property(self, name):
        """
            Return True if the property has a cached value.
        """
        return name in self.properties_cache

    def get_cached_property(self, name):
        """
            If possible, get the property value from the cache.
            Otherwise, request the property value, add it to
            the cache and return it.
        """
        if not self.is_cached_property(name):
            self.cache_property(name, self.get_property(name))
        return self.properties_cache[name]

    def get_cached_properties(self, names):
        """
            Make sure all names in *names* are present in
            the returned dict.
        """
        if not names: # get all names.
            # full cache update!
            self.update_cache()
            return self.properties_cache.copy()
        else:
            result = {}
            for name in names:
                result[name] = self.get_cached_property(name)
            return result

    def get_property(self, name):
        """
            Request the property value. Use `get_cached_property` if possible.
        """
        return self.layout.dbusmenu.get_property(self.id, name)

    def get_properties(self, names):
        """
            Return a dict mapping property names to values. Use
            `get_cached_properties` if possible.
        """
        return self.layout.dbusmenu.get_properties(self.id, names)

    @classmethod
    def parse_element(cls, layout, element):
        id = int(element.get('id'))
        children = [cls.parse_element(layout, subelem) for subelem in element]
        return cls(layout, id, children)

class Layout(object):
    def __init__(self, dbusmenu, revision, layout):
        self.dbusmenu = dbusmenu
        self.revision = revision
        self.layout = layout
        self.menu = None
        self.parse(layout)

    def parse(self, layout):
        """
            Parse the XML layout string at *layout* and store
            it in `self.menu`.
        """
        tree = etree.fromstring(layout)
        self.menu = Menu.parse_element(self, tree)

    def find_item(self, id):
        """
            Find the item or raise a ValueError.
        """
        item = self.menu.find_item(id)
        if item is None:
            raise ValueError('Could not find item %d' % id)
        return item

    def __repr__(self):
        return '<Layout object at 0x%x (%r)>' % (id(self), self.menu)

    def update_tree(self, should_revision, parent_id):
        layout_part = self.dbusmenu.get_layout(parent_id)
        # I guess the revision is global. :S
        self.revision = layout_part.revision
        if parent_id == 0:
            # Replace myself :-(
            self.layout = layout_part.layout
            self.menu = layout_part.menu
        else:
            # Replace a part :-)
            parent_menu = self.menu.find_item(parent_id)

class DBusMenu(dbus.Interface):
    def __init__(self, bus, bus_name, path):
        proxy = bus.get_object(bus_name, path)
        dbus.Interface.__init__(self, proxy, dbus_interface=DBUSMENU_INTERFACE)
        self._layout = None
        self.connect_to_signal('ItemUpdated', self.on_item_updated)
        self.connect_to_signal('ItemPropertyUpdated', self.on_item_property_updated)

    def _get_property(self, name):
        return cream.ipc.properties.get(self.proxy_object, ITEM_INTERFACE, name)

    version = property(lambda self: self._get_property('version'))

    def _get_layout(self):
        if self._layout is None:
            self.update_layout()
        return self._layout

    def update_layout(self):
        self._layout = self.get_layout(0)

    layout = property(_get_layout)

    def get_layout(self, parent_id):
        return Layout(self, *self.GetLayout(parent_id))

    def get_property(self, id, name):
        return self.GetProperty(id, name)

    def get_properties(self, id, names):
        return self.GetProperties(id, names)

    def about_to_show(self, id):
        return self.AboutToShow(id)

    def event(self, id, event_id, data, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        self.Event(id, event_id, data, timestamp)

    def get_group_properties(self, ids, names):
        return self.GetGroupProperties(ids, names)

    def get_children(self, id, names):
        return self.GetChildren(id, names)

    def on_item_updated(self, id):
        """
            Called when an item's properties are updated. Find it. Update it.
        """
        item = self.layout.find_item(id)
        item.on_item_updated()

    def on_item_property_updated(self, id, name, value):
        """
            Again, called when an item's property is updated.
            FIND AND UPDATE.
        """
        item = self.layout.find_item(id)
        item.on_item_property_updated(name, value)
