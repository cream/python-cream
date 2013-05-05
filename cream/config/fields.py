# Copyright: 2007-2013, Sebastian Billaudelle <sbillaudelle@googlemail.com>
#            2010-2013, Kristoffer Kleine <kris.kleine@yahoo.de>

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from gpyconf.fields import FontField as _FontField, MultiOptionField
from gpyconf.frontends.gtk import font_description_to_dict, dict_to_font_description


MultioptionField = MultiOptionField

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