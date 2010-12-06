#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os

from cream.util import cached_property
from cream.util import unique

from .base import Component, EXEC_MODE_PRODUCTIVE, EXEC_MODE_DEVELOPMENT

class Module(Component, unique.UniqueApplication):
    """
    This is the baseclass for every Cream module. It bundles features
    you would need within your application or service, such as:

     - an GObject mainloop,
     - logging capabilities,
     - and meta data handling.
     
    """

    def __init__(self, module_id, *args, **kwargs):

        if os.path.isfile('./manifest.xml'):
            exec_mode = EXEC_MODE_DEVELOPMENT
        else:
            exec_mode = EXEC_MODE_PRODUCTIVE
            raise BaseExcepion('Not implemented yet!')

        Component.__init__(self, *args, exec_mode=exec_mode, **kwargs)
        unique.UniqueApplication.__init__(self, self.context.manifest['id'])


    def main(self, enable_threads=True):
        """
        Run a GObject-mainloop.

        :param enable_threads: Whether to enable GObjects threading
                               capabilities. This can have negative
                               impact on some applications. Please use
                               with care!
        :type enable_threads: `bool`
        """

        import gobject

        if enable_threads:
            gobject.threads_init()

        self._mainloop = gobject.MainLoop()
        try:
            self._mainloop.run()
        except (SystemError, KeyboardInterrupt):
            # shut down gracefully.
            self.quit()


    @cached_property
    def messages(self):
        from cream.log import Messages
        return Messages(id=self.context.manifest['id'])


    def quit(self):
        """ Quit the mainloop and exit the application. """

        unique.UniqueApplication.quit(self)

        # __finalize__ all registered features:
        for feature in self._features:
            feature.__finalize__()

        self._mainloop.quit()

