from gi.repository import Gtk as gtk, GObject as gobject


class Widget(gobject.GObject):

    __gsignals__ = {
        'value-changed': (gobject.SignalFlags.RUN_LAST, None, (object,)),
    }

    def __init__(self, gtk_widget):

        gobject.GObject.__init__(self)

        self.widget = gtk_widget


    def on_value_changed(self, *args):

        self.emit('value-changed', self.get_value())



class BooleanWidget(Widget):

    def __init__(self, value):

        Widget.__init__(self, gtk.CheckButton())

        self.widget.connect('toggled', self.on_value_changed)

        self.set_value(value)


    def get_value(self):
        return self.widget.get_active()

    def set_value(self, value):
        self.widget.set_active(value)


class IntegerWidget(Widget):

    def __init__(self, value):

        Widget.__init__(self, gtk.SpinButton())

        self.widget.set_range(0, 100)
        self.widget.set_increments(1, self.widget.get_increments()[0])
        self.widget.connect('value-changed', self.on_value_changed)

        self.set_value(value)


    def get_value(self):
        return int(self.widget.get_value())

    def set_value(self, value):
        self.widget.set_value(value)


class FloatWidget(Widget):

    def __init__(self, value):

        Widget.__init__(self, gtk.SpinButton())

        self.widget.set_range(0, 100)
        self.widget.set_increments(0.01, self.widget.get_increments()[0])
        self.widget.set_digits(2)
        self.widget.connect('value-changed', self.on_value_changed)

        self.set_value(value)


    def get_value(self):
        return self.widget.get_value()

    def set_value(self, value):
        self.widget.set_value(value)


class CharWidget(Widget):

    def __init__(self, value):

        Widget.__init__(self, gtk.Entry())

        self.widget.connect('changed', self.on_value_changed)

        self.set_value(value)


    def get_value(self):
        return self.widget.get_text()

    def set_value(self, value):
        self.widget.set_text(value)


class MultiOptionWidget(Widget):

    def __init__(self, value):

        class ComboBoxText(gtk.ComboBox):
            def __init__(self):
                gtk.ComboBox.__init__(self)
                self.liststore = gtk.ListStore(str)
                self.set_model(self.liststore)
                cell = gtk.CellRendererText()
                self.pack_start(cell, True)
                self.add_attribute(cell, 'text', 0)

        Widget.__init__(self, ComboBoxText())

        self.value = value

        self.update_liststore()

        self.widget.connect('changed', self.on_value_changed)


    def update_liststore(self):

        self.widget.disconnect('changed')
        print 'update'
        self.active_index = 0
        self.widget.liststore.clear()
        for k, v in self.value:
            self.widget.liststore.append((v,))

        print self.active_index
        self.widget.set_active(self.active_index)

        self.widget.connect('changed', self.on_value_changed)

    def get_value(self):
        print 'get_value'
        i = self.active_index
        active = self.widget.get_active()

        self.value[i], self.value[active] = self.value[active], self.value[i]
        self.active_index = active

        return self.value

    def set_value(self, value):

        print 'set_value'
        self.value = value
        self.update_liststore()
