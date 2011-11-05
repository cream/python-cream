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

import os
from glob import iglob
from future_builtins import map
from ConfigParser import ConfigParser, NoOptionError
from functools import partial

SECTION = 'Desktop Entry'
DEFAULT_CATEGORIES = set(["AudioVideo", "Audio", "Video", "Development", "Education", "Game", "Graphics",
"Network", "Office", "Settings", "System", "Utility"])

class DesktopEntry(ConfigParser):
    def __init__(self, filename):
        ConfigParser.__init__(self)
        self.filename = filename
        self.read(filename)

    def __repr__(self):
        return '<DesktopEntry at 0x%x (%r)>' % (id(self), self.filename)

    @classmethod
    def get_all(cls, path='/usr/share/applications'):
        return map(DesktopEntry, iglob(os.path.join(path, '*.desktop')))

    def get_default(self, key):
        return ConfigParser.get(self, SECTION, key)

    def get_bool(self, key):
        return ConfigParser.getboolean(self, SECTION, key)

    def has_option_default(self, key):
        return ConfigParser.has_option(self, SECTION, key)

    def get_strings(self, key, default=NotImplemented):
        if not self.has_option_default(key):
            return default
        else:
            return self.get_default(key).strip(';').split(';') # TODO: comma separated?

    def get_locale(self, key, locale=''):
        try:
            if not locale:
                return self.get_default(key)
            else:
                return self.get_default('%s[%s]' % key)
        except NoOptionError:
            return None

    type = property(partial(get_default, key='Type'))
    version = property(partial(get_default, key='Version'))
    name = property(partial(get_locale, key='Name'))
    generic_name = property(partial(get_locale, key='GenericName'))
    no_display = property(partial(get_bool, key='NoDisplay'))

    @property
    def recommended_category(self):
        for category in self.categories:
            if category in DEFAULT_CATEGORIES:
                return category
        if self.categories:
            return self.categories[0]
        else:
            return None

    comment = property(partial(get_locale, key='Comment'))
    icon = property(partial(get_locale, key='Icon'))
    hidden = property(partial(get_bool, key='Hidden'))
    only_show_in = property(partial(get_strings, key='OnlyShowIn'))
    not_show_in = property(partial(get_strings, key='NotShowIn'))
    try_exec = property(partial(get_default, key='TryExec'))
    exec_ = property(partial(get_default, key='Exec'))
    path = property(partial(get_default, key='Path'))
    terminal = property(partial(get_bool, key='Terminal'))
    mime_type = property(partial(get_strings, key='MimeType'))
    categories = property(partial(get_strings, key='Categories', default=()))
    startup_notify = property(partial(get_bool, key='StartupNotify'))
    startup_wmclass = property(partial(get_default, key='StartupWMClass'))
    url = property(partial(get_default, key='URL'))

if __name__ == '__main__':
    from gi.repository import Gtk as gtk
    from gtkmenu import to_gtk
    menu = to_gtk(DesktopEntry.get_all())
    menu.popup(None, None, None, 1, 0)
    gtk.main()
