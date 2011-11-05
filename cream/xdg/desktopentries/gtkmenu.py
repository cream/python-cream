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
import re
from operator import attrgetter, itemgetter
from subprocess import Popen
from collections import defaultdict

from gi.repository import Gtk as gtk
from gi.repository import GObject as gobject

KICK = re.compile('%[ifFuUck]')
ICON_SIZE = 16

CATEGORY_ICONS = {
        "AudioVideo": 'applications-multimedia',
        "Audio": 'applications-multimedia',
        "Video": 'applications-multimedia',
        "Development": 'applications-development',
        "Education": 'applications-science',
        "Game": 'applications-games',
        "Graphics": 'applications-graphics',
        "Network": 'applications-internet',
        "Office": 'applications-office',
        "Settings": 'applications-engineering',
        "System": 'applications-system',
        "Utility": 'applications-other',
}

def activate_entry(widget, entry):
    exec_ = KICK.sub('', entry.exec_)
    if entry.terminal:
        term = os.environ.get('TERM', 'xterm')
        exec_ = '%s -e "%s"' % (term, exec_.encode('string-escape'))
    proc = Popen(exec_, shell=True)

def lookup_icon(icon_name, size=ICON_SIZE): # I'd be so happy to use gtk.ICON_SIZE_MENU here, but it returns empty pixbufs sometimes.
    if os.path.isfile(icon_name):
        return gtk.gdk.pixbuf_new_from_file_at_size(icon_name, size, size)

    theme = gtk.icon_theme_get_default()
    icon_info = theme.lookup_icon(icon_name, size, 0)
    if icon_info:
        path = icon_info.get_filename()
        return gtk.gdk.pixbuf_new_from_file_at_size(path, size, size)
    else:
        return None

def to_gtk(entries):
    tree = defaultdict(gtk.Menu)
    for entry in sorted(entries, key=attrgetter('name')):
        category = entry.recommended_category
        if not category:
            continue
        item = None
        if entry.icon:
            icon = lookup_icon(entry.icon)
            if icon is not None:
                item = gtk.ImageMenuItem()
                item.set_image(gtk.image_new_from_pixbuf(icon))
                item.set_label(entry.name)
        if item is None:
            item = gtk.MenuItem(entry.name)
        item.connect('activate', activate_entry, entry)
        item.show()
        tree[category].append(item)
    menu = gtk.Menu()
    for category, submenu in sorted(tree.iteritems(), key=itemgetter(0)):
        icon = None
        if category in CATEGORY_ICONS:
            icon = lookup_icon(CATEGORY_ICONS[category])
        item = gtk.ImageMenuItem(category)
        if icon is not None:
            item.set_image(gtk.image_new_from_pixbuf(icon))
        item.set_submenu(submenu)
        item.show()
        menu.append(item)
    menu.show()
    return menu
