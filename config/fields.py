from gpyconf.fields import FontField as _FontField
from gpyconf.frontends.gtk import font_description_to_dict, dict_to_font_description


class FontDict(dict):
    def to_string(self):
        return dict_to_font_description(self)

    @classmethod
    def fromstring(cls, string):
        d = font_description_to_dict(string)
        d['color'] = '#000000'
        return cls(d)

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
