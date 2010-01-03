from gpyconf.fields import *
from gpyconf.frontends._gtk import (font_description_to_dict,
                                    dict_to_font_description)


_FontField = fields.FontField

# Override ``FontField`` to add a ``to_string`` method to it's value dict:
class FontDict(dict):
    def to_string(self):
        return dict_to_font_description(self)

    @classmethod
    def fromstring(cls, string):
        d = font_description_to_dict(string)
        d['color'] = '#000000'
        return cls(d)

    def __xmlserialize__(self):
        return dict(self)

class FontField(_FontField):
    def custom_default(self):
        return FontDict(_FontField.custom_default(self))

    def to_python(self, value):
        if isinstance(value, basestring):
            return FontDict.fromstring(value)
        else:
            return FontDict(_FontField.to_python(self, value))

    def conf_to_python(self, value):
        return FontDict(_FontField.conf_to_python(self, value))
