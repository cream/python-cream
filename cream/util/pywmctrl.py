"""
    pywmctrl for ooxcb
    by Friedrich Weber 2008-2010
    licensed under GNU GPL v2 or later.
"""

from ooxcb import connect
from ooxcb.protocol import xproto

EVENT_MASK = (xproto.EventMask.SubstructureRedirect |
        xproto.EventMask.SubstructureNotify)

class Screen(object):
    def __init__(self, conn=None, root=None):
        if conn is None:
            conn = connect()
        self.conn = conn
        if root is None:
            root = conn.setup.roots[conn.pref_screen].root
        self.root = root

    def _send_clientmessage(self, window, atom_name, format, values):
        """
            send a client message to the root window.

            :Parameters:
                `window`: xproto.Window
                    the window property
                `atom_name`: str
                    the type atom name
                `format`: int
                    the value format, one of 8, 16, 32
                `values`: list
                    a list of values. Can be heterogenous (either ints
                    or Protobj subclasses). Will be padded to the
                    correct size.
        """
        values = values + [0] * ((160 // format) - len(values))
        event = xproto.ClientMessageEvent(self.conn)
        event.format = format
        event.window = window
        event.type = self.conn.atoms[atom_name]
        event.data = xproto.ClientMessageData(self.conn)
        setattr(event.data, 'data%d' % format, values)
        self.root.send_event_checked(EVENT_MASK, event).check()

    def get_active_window(self):
        """
            returns the active window object
        """
        return self.root.get_active_window()

    def change_desktop(self, desktop):
        """
            changes the current desktop. The desktops' count is
            starting at 0.
        """
        self._send_clientmessage(self.root, "_NET_CURRENT_DESKTOP", 32, [desktop])

    def get_current_desktop(self):
        """
            returns the index of the current desktop, starting at 0,
            or None if it couldn't be fetched.
        """
        property = self.root.get_property("_NET_CURRENT_DESKTOP", "CARDINAL") \
                .reply()
        if property.exists:
            return property.value[0]
        else:
            return None

    def toggle_showing_desktop(self, show):
        """
            Show the desktop. Or not.
        """
        self._send_clientmessage(self.root, "_NET_SHOWING_DESKTOP", 32, [show])

if __name__ == '__main__':
    conn = connect()
    wmctrl = Screen(conn, conn.setup.roots[0].root)
    wmctrl.change_desktop(1)
    print wmctrl.get_current_desktop()

