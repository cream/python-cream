import gtk

class CompositeBin(gtk.Fixed):
    """ A subclass of `GtkFixed` enabling composition of child widgets to the parent widget. """

    def __init__(self):

        self.alpha = 1

        gtk.Fixed.__init__(self)

        self.connect('realize', self.realize_cb)


    def realize_cb(self, widget):
        self.parent.connect_after('expose-event', self.expose_cb)


    def expose_cb(self, widget, event):

        if self.child.window:
            ctx = widget.window.cairo_create()
            ctx.set_operator(cairo.OPERATOR_OVER)

            alloc = self.child.allocation

            ctx.set_source_pixmap(self.child.window, alloc.x, alloc.y)
            ctx.paint_with_alpha(self.alpha)
        return False


    def add(self, child):
        """
        Add a widget.

        :param child: A `GtkWidget` to add to the `CompositedBin`.
        """

        self.child = child
        self.child.connect('realize', self.child_realize_cb)
        self.put(child, 0, 0)


    def child_realize_cb(self, widget):
        widget.window.set_composited(True)
