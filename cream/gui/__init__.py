#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from gi.repository import GObject as gobject
from gi.repository import Gtk as gtk
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
        ctx.clip()

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


    def raise_child(self, child):

        child.window.raise_()
        self.children.remove(child)
        self.children.insert(len(self.children), child)
        self.window.invalidate_rect(child.allocation, True)


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
        self._stopped = False


    def run(self):

        n_frames = (self.duration / 1000.0) * FRAMERATE

        while len(self._states) <= n_frames:
            self._states.append(self.curve(len(self._states) * (1.0 / n_frames)))
        self._states.reverse()

        gobject.timeout_add(int(self.duration / n_frames), self.update)


    def stop(self):
        self._stopped = True


    def update(self):
        
        if self._stopped:
            self.emit('completed')
            return False

        self.emit('update', self._states.pop())
        if len(self._states) == 0:
            self.emit('completed')
            return False
        return True
