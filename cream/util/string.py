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

def slugify(s):
    """
    Returns a slug-ready version of ``s``.
    (Lowercases all letters, replaces non-alphanumeric letters with hyphens,
    replaces all whitespace with underscores)
    """
    import re
    return re.sub('[^a-z0-9]', '-', re.sub('\s', '_', s.lower()))

def crop_string(s, maxlen, appendix='...'):
    """
    Crop string ``s`` after ``maxlen`` chars and append ``appendix``.
    """
    if len(s) > maxlen:
        return s[:maxlen] + appendix
    else:
        return s
