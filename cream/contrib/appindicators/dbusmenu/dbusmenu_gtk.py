import gtk

from cream.contrib.appindicators.dbusmenu import DBusMenu, Menu

class DBusMenuGTK(object):
    def __init__(self, dbusmenu):
        self.dbusmenu = dbusmenu
        self.initialize()

    def create_gtk_menu(self, menus):
        widget = gtk.Menu()
        for menu in menus:
            widget.append(self.create_gtk_menuitem(menu))
        return widget

    def create_gtk_menuitem(self, menu):
        # Figure out the item type.
        item_type = menu.get_cached_property('type')
        if item_type == 'standard':
            # it can still be a check or radio item.
            cls = {
                'checkmark': gtk.CheckMenuItem,
                'radio': gtk.RadioMenuItem,
                '': gtk.ImageMenuItem,
            }[menu.get_cached_property('toggle-type')]
        else:
            cls = gtk.SeparatorMenuItem
        widget = cls()
        widget.set_label(menu.get_cached_property('label'))
        widget.set_sensitive(menu.get_cached_property('enabled'))
        widget.set_visible(menu.get_cached_property('visible'))
        # get the image
        if cls == gtk.ImageMenuItem:
            if menu.get_cached_property('icon-name'):
                widget.set_image(
                    gtk.image_new_from_icon_name(
                        menu.get_cached_property('icon-name'),
                        gtk.ICON_SIZE_MENU,
                    )
                )
            if menu.get_cached_property('icon-data'):
                icon_data = menu.get_cached_property('icon-data')
                # let's hope this works.
                pixbuf = gtk.gdk.pixbuf_new_from_inline(len(icon_data), icon_data, False)
                widget.set_image(gtk.image_new_from_pixbuf(pixbuf))
        if menu.get_cached_property('toggle-state') == 1:
            widget.toggle()
        if (menu.children and menu.get_cached_property('children-display')):
            # Yay children.
            widget.set_submenu(self.create_gtk_menu(menu.children))
        # Well I wanna get clicks and motions.
        widget.connect('activate', self.sig_activate, menu)
        widget.connect('enter-notify-event', self.sig_enter_notify, menu)
        # And changes to the menu structure.
        menu.connect('property-changed', self.sig_property_changed, widget)
        menu.connect('properties-changed', self.sig_properties_changed, widget)
        menu.connect('children-changed', self.sig_children_changed, widget)
        return widget

    def sig_property_changed(self, menu, name, widget):
        # Apparently, we can't replace menu items in gtk.Menu instances. We have to
        # redo the whole menu. Bad. TODO?
        self.initialize()

    def sig_properties_changed(self, menu, widget):
        self.initialize()

    def sig_children_changed(self, menu, widget):
        self.initialize()

    def sig_activate(self, widget, menu):
        """
            Called when a menu item gets activated. trigger event.
        """
        menu.event('clicked')

    def sig_enter_notify(self, widget, event, menu):
        """
            got hovered! trigger event.
        """
        menu.event('hovered')

    def initialize(self):
        """
            Read the dbusmenu stuff.
        """
        # Find and create se menus.
        self.root_widget = self.create_gtk_menu(self.dbusmenu.layout.menu.children)

    def popup(self):
        self.root_widget.popup(None, None, None, 1, 0)
