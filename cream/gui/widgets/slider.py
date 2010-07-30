import gobject
import gtk
import cream.gui

class Slider(gtk.Viewport):
    active_widget = None
    _size_cache = None

    def __init__(self):
        gtk.Viewport.__init__(self)

        self.timeouts = dict()

        self.set_shadow_type(gtk.SHADOW_NONE)

        self.layout = gtk.HBox(True)
        self.content = gtk.EventBox()
        self.content.add(self.layout)

        self.container = gtk.Fixed()
        self.container.add(self.content)
        self.add(self.container)

        self.connect('size-allocate', self.size_allocate_cb)


    def slide_to(self, widget):

        self.active_widget = widget

        def update(source, status):
            pos = end_position - start_position
            adjustment.set_value(start_position + int(round(status * pos)))

        adjustment = self.get_hadjustment()
        start_position = adjustment.get_value()
        end_position = widget.get_allocation().x

        if start_position != end_position:
            timeline = cream.gui.Timeline(500, cream.gui.CURVE_SINE)
            timeline.connect('update', update)
            timeline.run()


    def size_allocate_cb(self, source, allocation):

        if self._size_cache != allocation and self.active_widget:
            adjustment = self.get_hadjustment()
            adjustment.set_value(self.active_widget.get_allocation().x)

        self._size_cache = allocation

        width = (len(self.layout.get_children()) or 1) * allocation.width
        self.content.set_size_request(width, allocation.height)


    def append_widget(self, widget):

        self.layout.pack_start(widget, True, True, 0)

    def add_slide_timeout(self, widget, seconds):
        """
        Adds a timeout for ``widget`` to slide in after ``seconds``.
        """
        if widget in self.timeouts:
            raise RuntimeError("A timeout for '%s' was already added" % widget)

        callback = lambda: self.slide_to(widget)
        self.timeouts[widget] = (gobject.timeout_add_seconds(seconds, callback),
                                 seconds)

    def remove_slide_timeout(self, widget):
        """
        Removes a timeout previously added by ``add_slide_timeout``.
        """
        try:
            gobject.source_remove(self.timeouts.pop(widget)[0])
        except KeyError:
            raise RuntimeError("No timeout for '%s' was added" % widget)

    def reset_slide_timeout(self, widget, seconds=None):
        """
        Shorthand to ``remove_slide_timeout`` plus ``add_slide_timeout``.
        """
        if seconds is None:
            try:
                seconds = self.timeouts[widget][1]
            except KeyError:
                # exception will be thrown by ``remove_slide_timeout`` anyways
                pass
        self.remove_slide_timeout(widget)
        self.add_slide_timeout(widget, seconds)

    def try_remove_slide_timeout(self, widget):
        try:
            self.remove_slide_timeout(widget)
        except RuntimeError:
            pass

    def try_reset_slide_timeout(self, widget, *args, **kwargs):
        """
        Like ``reset_slide_timeout``, but fails silently
        if the timeout for``widget`` does not exist.
        """
        if widget in self.timeouts:
            self.reset_slide_timeout(widget, *args, **kwargs)
