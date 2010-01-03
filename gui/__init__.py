import gtk
import gobject
import cairo
import pango
import pangocairo
import cream.gui.svg
import time
import math
import os

# TODO:
# * Move 'rotation'-attribute to Object.

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


class Widget(gtk.Widget, object):
    """ `GtkWidget` displaying a CIL interface. """

    def __init__(self):

        gtk.Widget.__init__(self)

        # Enable custom drawing and set the RGBA-colormap.
        self.set_app_paintable(True)
        self.set_colormap(self.get_screen().get_rgba_colormap())

        # Set some general variables.
        self._size = (100, 100)
        self.stack = []
        self.locks = {'render': False, 'shape': None}
        self.alpha = 1
        self.zoom = 1.0

        self.aspect = 1

        self.pressed_object = None
        self.entered_object = None

        # Some event-stuff for GTK.
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
        self.drag_dest_set(gtk.DEST_DEFAULT_ALL, [('text/uri-list', 0, 80)], gtk.gdk.ACTION_COPY)


    def get_size(self):
        """ Get the size of the widget. """

        return (self._size[0] * self.zoom, self._size[1] * self.zoom)


    def set_size(self, size):
        """
        Set the size of the widget.

        :param size: The size to set as a `tuple`.
        """

        self._size = size

    size = property(get_size, set_size)


    def get_width(self):
        return self.size[0]


    def get_height(self):
        return self.size[1]


    def do_realize(self):

        self.set_flags(self.flags() | gtk.REALIZED)

        self.window = gtk.gdk.Window(
            self.get_parent_window(),
            width=self.allocation.width,
            height=self.allocation.height,
            window_type=gtk.gdk.WINDOW_CHILD,
            wclass=gtk.gdk.INPUT_OUTPUT,
            event_mask=gtk.gdk.ALL_EVENTS_MASK,
            visual=self.get_colormap().get_visual(),
            colormap=self.get_colormap())

        self.window.set_user_data(self)
        self.window.move_resize(*self.allocation)


    def do_unrealize(self):
        self.window.destroy()


    def do_size_request(self, requisition):

        requisition.height = self.size[1]
        requisition.width = self.size[0]


    def do_expose_event(self, event):

        if not self.locks['render']:
            self.render()


    def do_button_press_event(self, event):

        objects = self.stack[:]
        objects.reverse()

        for object in objects:
            pos_x = convert_value(object._attributes['x'], self.size[0])
            pos_y = convert_value(object._attributes['y'], self.size[1])
            size_x = convert_value(object._attributes['width'], self.size[0])
            size_y = convert_value(object._attributes['height'], self.size[1])

            if pos_x <= event.x and pos_y <= event.y and pos_x + size_x >= event.x and pos_y + size_y >= event.y:
                object.emit('mouse-press')
                self.pressed_object = object
                break


    def do_button_release_event(self, event):

        objects = self.stack[:]
        objects.reverse()
        self.pressed_object.emit('mouse-release')
        for object in objects:
            pos_x = convert_value(object._attributes['x'], self.size[0])
            pos_y = convert_value(object._attributes['y'], self.size[1])
            size_x = convert_value(object._attributes['width'], self.size[0])
            size_y = convert_value(object._attributes['height'], self.size[1])

            if pos_x <= event.x and pos_y <= event.y and \
                pos_x + size_x >= event.x and pos_y + size_y >= event.y:
                    if self.pressed_object == object:
                        object.emit('mouse-clicked')
                    self.pressed_object = None
                    break


    def do_leave_notify_event(self, event):

        try:
            self.entered_object.emit('mouse-leave')
        except:
            pass


    def do_enter_notify_event(self, event):
        pass


    def do_motion_notify_event(self, event):

        objects = self.stack[:]
        objects.reverse()

        for object in objects:
            pos_x = convert_value(object._attributes['x'], self.size[0])
            pos_y = convert_value(object._attributes['y'], self.size[1])
            size_x = convert_value(object._attributes['width'], self.size[0])
            size_y = convert_value(object._attributes['height'], self.size[1])

            if pos_x <= event.x and pos_y <= event.y and pos_x + size_x >= event.x and pos_y + size_y >= event.y:
                if self.entered_object == None:
                    object.emit('mouse-enter')
                    self.entered_object = object

                elif self.entered_object != object:
                    self.entered_object.emit('mouse-leave')
                    object.emit('mouse-enter')
                    self.entered_object = object

                else:
                    self.entered_object.emit('mouse-move')

                break


    def do_drag_motion(self, context, x, y, time):
        return True


    def do_drag_drop(self, context, x, y, time):
        return True


    def do_drag_data_recieved(self, context, x, y, selection, target_type, time):

        objects = self.stack[:]
        objects.reverse()
        for object in objects:
            pos_x = convert_value(object._attributes['x'], self.size[0])
            pos_y = convert_value(object._attributes['y'], self.size[1])
            size_x = convert_value(object._attributes['width'], self.size[0])
            size_y = convert_value(object._attributes['height'], self.size[1])

            if pos_x <= x and pos_y <= y and pos_x + size_x >= x and pos_y + size_y >= y:
                object.emit('drop', selection.data)
                break


    def get_width(self):
        return self.size[0]


    def get_height(self):
        return self.size[1]


    def add(self, object):

        self.stack.append(object)

        object.connect('redraw', self.draw)
        object.realize(self)


    def draw(self, object, range):
        self.render(range)


    def shape(self, id):

        if self.locks['shape'] == id:
            pixmap = gtk.gdk.Pixmap(self.window, int(self.size[0]), int(self.size[1]), 1)
            pixmap_context = pixmap.cairo_create()
            pixmap_context.set_source_surface(self.buffer_surface, 0, 0)
            pixmap_context.paint()
            self.window.input_shape_combine_mask(pixmap, 0, 0)


    def render(self, mask=None, force_render=False):

        if not self.locks['render'] and self.window:
            self.locks['render'] = True

            width = int(self.size[0])
            height = int(self.size[1])

            if self.window.get_size()[0] < self.size[0] or self.window.get_size()[1] < self.size[1]:
                self.window.resize(width + 50, height + 50)

            self.buffer_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            self.buffer_context = cairo.Context(self.buffer_surface)

            for i in self.stack:
                if force_render:
                    i.render(force=True)
                i.draw(self.buffer_context)

            ctx = self.window.cairo_create()
            ctx.set_operator(cairo.OPERATOR_SOURCE)

            if mask:
                ctx.rectangle(int(round(mask[0] * width)), int(round(mask[1] * height)), int(round(mask[2] * width)), int(round(mask[3] * height)))
                ctx.set_source_rgba(0, 0, 0, 0)
                ctx.fill_preserve()
                ctx.set_operator(cairo.OPERATOR_OVER)
                ctx.set_source_surface(self.buffer_surface, 0, 0)
                ctx.fill()
            else:
                ctx.set_source_rgba(0, 0, 0, 0)
                ctx.paint()
                ctx.set_operator(cairo.OPERATOR_OVER)
                ctx.set_source_surface(self.buffer_surface, 0, 0)
                ctx.paint_with_alpha(self.alpha)

            shape_id = time.time()

            self.locks['shape'] = shape_id
            gobject.timeout_add(70, self.shape, shape_id)

            self.locks['render'] = False


# Register `Widget` as a GObject and add events.
gobject.type_register(Widget)
gobject.signal_new('redraw', Widget, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())

def convert_value(value, comp):
    """
    Convert a given value (e. g. "50%", "10px", "10%+5px", etc.) to an absolute value.

    :param value: The value as a `string`.
    :param comp: A value to wich comp is relative as `int` or `float`.
    """

    if len(value.split('-')) > 1:
        value = value.split('-')
        minuend = convert_value(value[0].strip(), comp)
        for v in value[1:]:
            minuend -= convert_value(v.strip(), comp)
        return minuend
    else:
        if value[-1] == '%':
            return float(value[:-1]) * comp / 100.0
        elif value[-2:] == 'px':
            return float(value[:-2])


class Object(gobject.GObject):
    """ The baseclass for CIL-objects. """

    def __init__(self):

        gobject.GObject.__init__(self)

        self._attributes = {
                'x': '0%',
                'y': '0%',
                'width': '100%',
                'height': '100%',
                'opacity': '1'
            }

        self.parent = None

        self.surface = None
        self.context = None


    def realize(self, parent):
        self.parent = parent


    def set_attribute(self, key, value):
        self._attributes[key] = value


    def get_attribute(self, key):
        return self._attributes[key]


    def render(self):
        pass


    def draw(self, ctx):

        ctx.save()
        ctx.set_operator(cairo.OPERATOR_OVER)

        x = int(round(convert_value(self._attributes['x'], self.parent.get_width())))
        y = int(round(convert_value(self._attributes['y'], self.parent.get_height())))
        width = int(round(convert_value(self._attributes['width'], self.parent.get_width())))
        height = int(round(convert_value(self._attributes['height'], self.parent.get_height())))

        self.factor_x = float(width) / self.surface.get_width()
        if not self.surface.get_height() == 0:
            self.factor_y = float(height) / self.surface.get_height()
        else:
            self.factor_y = 1

        ctx.scale(self.factor_x, self.factor_y)
        ctx.translate(x / self.factor_x, y / self.factor_y)
        ctx.set_source_surface(self.surface, 0, 0)
        ctx.paint_with_alpha(float(self._attributes['opacity']))
        ctx.restore()


class Image(Object):

    def __init__(self):

        Object.__init__(self)

        self._attributes['path'] = ''
        self._attributes['rotation'] = '0'

        self.needs_redraw = True


    def set_attribute(self, key, value):

        if key in ['path', 'size', 'rotation', 'opacity'] and value != self._attributes[key]:
            self.needs_redraw = True

        Object.set_attribute(self, key, value)
        if key == 'path':
            self.handle = cream.gui.svg.Handle(self._attributes['path'])


    def render(self, emit=True, force=False):

        if self.needs_redraw == True or force:
            self.needs_redraw = False

            handle_size = self.handle.get_dimension_data()

            width = int(round(convert_value(self._attributes['width'], self.parent.get_width())))
            height = int(round(convert_value(self._attributes['height'], self.parent.get_height())))

            self.factor_x = float(width) / handle_size[0]
            self.factor_y = float(height) / handle_size[1]

            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
            self.context = cairo.Context(self.surface)

            self.context.save()
            self.context.scale(self.factor_x, self.factor_y)
            if int(self._attributes['rotation']) != 0:
                self.context.translate(handle_size[0]/2.0, handle_size[1]/2.0)
                self.context.rotate(math.radians(int(self._attributes['rotation'])))
                self.context.translate(-handle_size[0]/2.0, -handle_size[1]/2.0)
            self.handle.render_cairo(self.context)
            self.context.restore()

        if emit == True:
            self.emit('redraw', None)


class TiledImage(Object):

    def __init__(self):

        Object.__init__(self)

        self._attributes['path'] = ''

        self.needs_redraw = True


    def set_attribute(self, key, value):

        if key in ['path', 'size', 'opacity'] and value != self._attributes[key]:
            self.needs_redraw = True

        Object.set_attribute(self, key, value)
        if key == 'path':
            self.handle = cream.gui.svg.Handle(self._attributes['path'])


    def render(self, emit=True, force=False):

        if self.needs_redraw == True or force:
            self.needs_redraw = False

            width = int(round(convert_value(self._attributes['width'], self.parent.get_width())))
            height = int(round(convert_value(self._attributes['height'], self.parent.get_height())))

            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
            self.context = cairo.Context(self.surface)

            scale_x = (width - (self.handle.get_dimensions_sub('#north-west')[0] + self.handle.get_dimensions_sub('#north-east')[0])) / float(self.handle.get_dimensions_sub('#north')[0])
            scale_y = (height - (self.handle.get_dimensions_sub('#north-west')[1] + self.handle.get_dimensions_sub('#south-west')[1])) / float(self.handle.get_dimensions_sub('#west')[1])

            nw_x, nw_y = self.handle.get_position_sub('#north-west')
            nw_width, nw_height = self.handle.get_dimensions_sub('#north-west')
            self.context.translate(-nw_x, -nw_y)
            self.handle.render_cairo_sub(self.context, "#north-west")
            self.context.translate(nw_x, nw_y)

            # Reading the following could kill you. Please do not try to get behind this code!
            # Rendering the upper edge.
            n_x, n_y = self.handle.get_position_sub('#north')
            n_width, n_height = self.handle.get_dimensions_sub('#north')
            n_scale_x = round(n_width * scale_x) / n_width
            self.context.translate(-n_x * n_scale_x + nw_width, -n_y)
            self.context.scale(n_scale_x, 1)
            self.handle.render_cairo_sub(self.context, "#north")
            self.context.scale(1.0 / n_scale_x, 1)
            self.context.translate(-(-n_x * n_scale_x + nw_width), n_y)

            # Rendering the upper-right corner.
            ne_x, ne_y = self.handle.get_position_sub('#north-east')
            ne_width, ne_height = self.handle.get_dimensions_sub('#north-east')
            self.context.translate(-ne_x + nw_width + n_width * n_scale_x, -ne_y)
            self.handle.render_cairo_sub(self.context, "#north-east")
            self.context.translate(-(-ne_x + nw_width + n_width * n_scale_x), n_y)

            # Rendering the left edge.
            w_x, w_y = self.handle.get_position_sub('#west')
            w_width, w_height = self.handle.get_dimensions_sub('#west')
            w_scale_y = round(w_height * scale_y) / w_height
            self.context.translate(-w_x, -w_y * w_scale_y + nw_height)
            self.context.scale(1, w_scale_y)
            self.handle.render_cairo_sub(self.context, "#west")
            self.context.scale(1, 1.0 / w_scale_y)
            self.context.translate(w_x, -(-w_y * w_scale_y + nw_height))

            # Rendering the center.
            c_x, c_y = self.handle.get_position_sub('#center')
            c_width, c_height = self.handle.get_dimensions_sub('#center')
            c_scale_x = round(c_width * scale_x) / c_width
            c_scale_y = round(c_height * scale_y) / c_height
            self.context.translate(-c_x * c_scale_x + w_width, -c_y * c_scale_y + n_height)
            self.context.scale(c_scale_x, c_scale_y)
            self.handle.render_cairo_sub(self.context, "#center")
            self.context.scale(1.0 / c_scale_x, 1.0 / c_scale_y)
            self.context.translate(-(-c_x * c_scale_x + w_width), -(-c_y * c_scale_y + n_height))

            # Rendering the right edge.
            e_x, e_y = self.handle.get_position_sub('#east')
            e_width, e_height = self.handle.get_dimensions_sub('#east')
            e_scale_y = round(e_height * scale_y) / e_height
            self.context.translate(-e_x + w_width + c_width * c_scale_x, -e_y * e_scale_y + ne_height)
            self.context.scale(1, e_scale_y)
            self.handle.render_cairo_sub(self.context, "#east")
            self.context.scale(1, 1.0 / e_scale_y)
            self.context.translate(-(-e_x + w_width + c_width * c_scale_x), -(-e_y * e_scale_y + ne_height))

            # Rendering the lower-left corner.
            sw_x, sw_y = self.handle.get_position_sub('#south-west')
            sw_width, sw_height = self.handle.get_dimensions_sub('#south-west')
            self.context.translate(-sw_x, -sw_y + nw_height + w_height * w_scale_y)
            self.handle.render_cairo_sub(self.context, "#south-west")
            self.context.translate(-sw_x, -(-sw_y + nw_height + w_height * w_scale_y))

            # Renderig the lower edge.
            s_x, s_y = self.handle.get_position_sub('#south')
            s_width, s_height = self.handle.get_dimensions_sub('#south')
            s_scale_x = round(s_width * scale_x) / s_width
            self.context.translate(-s_x * s_scale_x + sw_width, -s_y + c_height * c_scale_y + n_height)
            self.context.scale(s_scale_x, 1)
            self.handle.render_cairo_sub(self.context, "#south")
            self.context.scale(1.0 / s_scale_x, 1)
            self.context.translate(-(-s_x * s_scale_x + sw_width), -(-s_y + c_height * c_scale_y + n_height))

            # Renderig the lower-right corner.
            se_x, se_y = self.handle.get_position_sub('#south-east')
            se_width, se_height = self.handle.get_dimensions_sub('#south-east')
            self.context.translate(-se_x + sw_width + s_width * s_scale_x, -s_y + c_height * c_scale_y + n_height)
            self.handle.render_cairo_sub(self.context, "#south-east")
            self.context.translate(-(-se_x + sw_width + s_width * s_scale_x), -(-s_y + c_height * c_scale_y + n_height))

            # ARGH!

        if emit == True:
            self.emit('redraw', None)


class Canvas(Object):

    def __init__(self):
        Object.__init__(self)


    def get_size(self):
        return self.size


    def set_size(self, x, y):

        if self.size != (x, y):
            self.size = (x, y)
            self.needs_redraw = True


    def render(self, emit=True, force=False):

        width = int(round(convert_value(self._attributes['width'], self.parent.get_width()) / self.parent.zoom))
        height = int(round(convert_value(self._attributes['height'], self.parent.get_height()) / self.parent.zoom))

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        self.context = cairo.Context(self.surface)

        self.emit('draw', self.context, width, height)

        if emit == True:
            self.emit('redraw', None)


class Text(Object):

    def __init__(self):

        Object.__init__(self)

        self.lines = ['']

        self._attributes['text'] = ''
        self._attributes['font-size'] = 10
        self._attributes['font-family'] = 'Sans'
        self._attributes['font-weight'] = 'normal'
        self._attributes['font-color'] = (0, 0, 0, 1)
        self._attributes['font-style'] = 'normal'
        self._attributes['alignment'] = 'left'

        self.needs_redraw = True


    def set_attribute(self, key, value):

        if key in ['text', 'alignment', 'font-size', 'font-family', 'font-weight',  'font-color',  'font-style'] and value != self._attributes[key]:
            self.needs_redraw = True

        Object.set_attribute(self, key, value)

        if key in ['text', 'alignment', 'font-size', 'font-family', 'font-weight',  'font-style']:
            self.lines = self.calculate()


    def realize(self, parent):

        res = Object.realize(self, parent)
        self.lines = self.calculate()
        return res


    def calculate(self):

        if self.parent:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
            context = cairo.Context(surface)
            context.set_font_size(int(self._attributes['font-size']) * self.parent.zoom)

            weight = cairo.FONT_WEIGHT_NORMAL

            if self._attributes['font-weight'] == 'bold':
                weight = cairo.FONT_WEIGHT_BOLD

            context.select_font_face(self._attributes['font-family'], cairo.FONT_SLANT_NORMAL, weight)

            text = self._attributes['text']
            line = self._attributes['text']
            original = text

            lines = []

            width_available = convert_value(self._attributes['width'], self.parent.get_width())

            while True:
                xbearing, ybearing, width, height, xadvance, yadvance = (context.text_extents(line))
                while width > width_available:
                    line = ' '.join(line.split(' ')[:-1])

                    xbearing, ybearing, width, height, xadvance, yadvance = (context.text_extents(line))

                lines.append(line)

                line = text[len(line):]
                text = line

                if len(line) > 0:
                    pass
                else:
                    break
            return lines
        else:
            return ['']


    def render(self, emit=True, force=False):
        """
        render the given text

        :param force: useless, but needed, because other Objects.render()
                      have a force argument
        """

        if self.needs_redraw == True:
            self.needs_redraw = False
            width = convert_value(self._attributes['width'], self.parent.get_width())
            height = convert_value(self._attributes['height'], self.parent.get_height())

            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(round(width)), int(round(height)))

            weight = cairo.FONT_WEIGHT_NORMAL

            if self._attributes['font-weight'] == 'bold':
                weight = cairo.FONT_WEIGHT_BOLD

            self.context = cairo.Context(self.surface)
            self.context.set_font_size(int(self._attributes['font-size']) * self.parent.zoom)
            self.context.select_font_face(self._attributes['font-family'], cairo.FONT_SLANT_NORMAL, weight)
            self.context.set_source_rgba(*self._attributes['font-color'])

            y = 0

            for l in self.lines:
                xbearing, ybearing, text_width, text_height, xadvance, yadvance = (self.context.text_extents(l))
                x = 0 - xbearing
                if self._attributes['alignment'] == 'center':
                    x = (width - text_width) / 2 - xbearing
                y += 1.3 * int(int(self._attributes['font-size']) * self.parent.zoom)
                self.context.move_to(x, y)
                self.context.show_text(l)
        if emit == True:
            self.emit('redraw', None)


gobject.type_register(Object)
gobject.signal_new('redraw', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT,))

gobject.signal_new('mouse-press', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new('mouse-release', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new('mouse-clicked', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())

gobject.signal_new('mouse-enter', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new('mouse-leave', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new('mouse-move', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())

gobject.signal_new('drop', Object, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN,  (gobject.TYPE_STRING,))

gobject.signal_new('draw', Canvas, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, gobject.TYPE_INT, gobject.TYPE_INT))

