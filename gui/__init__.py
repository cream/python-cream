import gtk
import cairo
import time

class CompositeBin(gtk.Fixed):
    """ A subclass of `GtkFixed` enabling composition of child widgets to the parent widget. """

    def __init__(self):

        self.alpha = 1
        self.children = []

        gtk.Fixed.__init__(self)

        self.connect('realize', self.realize_cb)


    def realize_cb(self, widget):
        self.parent.connect_after('expose-event', self.expose_cb)


    def expose_cb(self, widget, event):

        ctx = widget.window.cairo_create()
        ctx.set_operator(cairo.OPERATOR_OVER)

        ctx.rectangle(*event.area)

        for child in self.children:
            alloc = child.allocation
            ctx.set_source_pixmap(child.window, alloc.x, alloc.y)
            ctx.paint()
        return False


    def add(self, child, x, y):
        """
        Add a widget.

        :param child: A `GtkWidget` to add to the `CompositedBin`.
        """

        self.children.append(child)
        child.connect('realize', self.child_realize_cb)
        self.put(child, x, y)


    def remove(self, child):

        gtk.Fixed.remove(self, child)
        child.realize()


    def child_realize_cb(self, widget):
        try:
            widget.window.set_composited(True)
        except:
            pass
