import gobject
import gtk
import cairo
import time
import math

CURVE_LINEAR = lambda x: x
CURVE_SINE = lambda x: math.sin(math.pi / 2 * x)

FRAMERATE = 30.0

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
            alloc = child.get_allocation()
            ctx.move_to(alloc.x, alloc.y)
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
        self.children.remove(child)


    def child_realize_cb(self, widget):
        try:
            widget.window.set_composited(True)
        except:
            pass


class Timeline(gobject.GObject):

    __gtype_name__ = 'Timeline'
    __gsignals__ = {
        'update': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
        'completed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

    def __init__(self, duration, curve):

        gobject.GObject.__init__(self)

        self.duration = duration
        self.curve = curve

        self._states = []


    def run(self):

        n_frames = (self.duration / 1000.0) * FRAMERATE

        while len(self._states) <= n_frames:
            self._states.append(self.curve(len(self._states) * (1.0 / n_frames)))
        self._states.reverse()

        gobject.timeout_add(int(self.duration / FRAMERATE), self.update)


    def update(self):

        self.emit('update', self._states.pop())
        if len(self._states) == 0:
            self.emit('completed')
            return False
        return True
