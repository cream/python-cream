from xml.dom import minidom

import ctypes
from ctypes import *

_lib = CDLL('librsvg-2.so')
gobject = CDLL('libgobject-2.0.so')
gobject.g_type_init()

class RsvgDimensionData(Structure):
    _fields_ = [("width", c_int),
                ("height", c_int),
                ("em",c_double),
                ("ex",c_double)]

class RsvgPositionData(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int)]

class PycairoContext(Structure):
    _fields_ = [("PyObject_HEAD", c_byte * object.__basicsize__),
                ("ctx", c_void_p),
                ("base", c_void_p)]

handle_get_dimensions = _lib.rsvg_handle_get_dimensions
handle_render_cairo = _lib.rsvg_handle_render_cairo
handle_render_cairo_sub = _lib.rsvg_handle_render_cairo_sub
handle_free = _lib.rsvg_handle_free
handle_get_dimensions_sub = _lib.rsvg_handle_get_dimensions_sub
handle_get_position_sub = _lib.rsvg_handle_get_position_sub

__all__ = [
    'handle_new_from_file', 
    'handle_new_from_data', 
    'handle_get_dimensions', 
    'handle_render_cairo',
    'handle_render_cairo_sub',
    'RsvgDimensionData',
]

def set_id_attribute(element):

    try:
        element.setIdAttribute('id')
    except:
        pass

    for c in element.childNodes:
        set_id_attribute(c)


class Handle:

    def __init__(self, path=None):

        self.path = path
        if self.path:
            self.dom = minidom.parse(self.path)
            set_id_attribute(self.dom)
            self.dom.save = self.save_dom
            xml = self.dom.toxml('utf-8')
            self.handle = _lib.rsvg_handle_new_from_data(xml, len(xml))


    def save_dom(self):

        handle_free(self.handle)

        xml = self.dom.toxml('utf-8')
        self.handle = _lib.rsvg_handle_new_from_data(xml, len(xml))


    @classmethod
    def new_from_data(cls, data):

        self = Handle()
        self.dom = minidom.parseString(data)
        set_id_attribute(self.dom)
        self.dom.save = self.save_dom
        xml = self.dom.toxml('utf-8')
        self.handle = _lib.rsvg_handle_new_from_data(xml, len(xml))
        return self


    def get_dimensions_sub(self, element):

        dim = RsvgDimensionData()
        handle_get_dimensions_sub(self.handle, ctypes.byref(dim), element)
        return dim.width, dim.height


    def get_position_sub(self, element):

        dim = RsvgPositionData()
        handle_get_position_sub(self.handle, ctypes.byref(dim), element)
        return dim.x, dim.y


    def render_cairo(self, ctx):

        handle_render_cairo(self.handle, PycairoContext.from_address(id(ctx)).ctx)


    def render_cairo_sub(self, ctx, element):

        handle_render_cairo_sub(self.handle, PycairoContext.from_address(id(ctx)).ctx, element)


    def get_dimension_data(self):

        dim = RsvgDimensionData()
        handle_get_dimensions(self.handle, ctypes.byref(dim))
        return dim.width, dim.height


    def __del__(self):

        handle_free(self.handle)
