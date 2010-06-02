"""
    pywmctrl
    Copyright (c) 2008-2010 Friedrich Weber <fred@reichbier.de>

    licensed under GNU GPL v2 (or later)
"""

import Xlib, Xlib.display, Xlib.Xatom

class WMException(Exception):
    pass

def get_process_executable(pid):
    """ return a process executable by its pid or None """
    try:
        f = file('/proc/%d/status' % pid, 'r')
    except IOError:
        return None
    name = None
    while 1:
        line = f.readline().lower()
        if line.startswith('name'):
            name = line[len('name:'):].strip()
            break
    return name

def get_timestamp():
    """ return the UNIX timestamp for now. I am sure it can be easier ^_^ """
    return int(time.mktime(time.gmtime()))

class Screen():
    def __init__(self):
        self.display = Xlib.display.Display()
        self.root = self.display.screen().root

    def _get_atom(self, name):
#        return self.display.intern_atom(name)
        a = self.display.intern_atom(name)
        return a

    def _send_clientmessage(self, window, atom_name, data, format=32):
        """
            internal: send a client message to a window

            :param window: The target Xlib.Window
            :param atom_name: The atom name as string
            :param data: The given data as list,
                         will be expanded to five elements
            :param format: The format of the given data as bits. A format of
                           32 means that we have 5 32bit integers to send.
                           `data` is padded to the correct count.
        """
        assert format in (8, 16, 32)
        length = {
                8: 20,
                16:10,
                32: 5
                }
        expanded_data = data + [0]*(length[format] - len(data))
        event = Xlib.protocol.event.ClientMessage(
                window=window,
                client_type=self._get_atom(atom_name),
                data=(format, expanded_data))
        mask = (Xlib.X.SubstructureRedirectMask|Xlib.X.SubstructureNotifyMask)
        self.root.send_event(event, event_mask=mask)
        self.display.flush() # flush should be enough.

    def _get_property(self, window, atom_name, type_=None):
        """
            wrapper for window.get_full_property

            :param window: the target Xlib.Window
            :param atom_name: The atom name as string
            :param type_: The property type as string, e.g.
                         "CARDINAL" or None -> AnyPropertyType
            :returns: Xlib.protocol.request.GetProperty stuff
            :note: raises WMException if property not found
        """
        if not type_:
            type_ = Xlib.X.AnyPropertyType
        else:
            type_ = self._get_atom(type_)

        prop = window.get_full_property(
                self._get_atom(atom_name),
                type_)
        if not prop:
            raise WMException("Could not fetch property '%s'" % atom_name)
        return prop

    def change_workspace(self, workspace):
        """
            change the current workspace.

            :param workspace: new workspace number, starting at 0
        """
        self._send_clientmessage(self.root, "_NET_CURRENT_DESKTOP",
                [workspace])

    def get_current_workspace(self):
        """
            returns the number of the current workspace, starting at 0.
            If an error occured, it returns -1
        """
        prop = self._get_property(self.root, "_NET_CURRENT_DESKTOP",
                "CARDINAL")
        if prop:
            return prop.value[0]
        else:
            return -1

    def get_active_window_id(self):
        """
            returns the active window id or -1
        """
        prop = self._get_property(self.root, "_NET_ACTIVE_WINDOW") # why .. does .. that .. work?
        if prop:
            return prop.value[0]
        else:
            return -1

    def get_active_window(self):
        """
            return the active window as Xlib.Window or None
        """
        xid = self.get_active_window_id()
        if xid:
            return self.display.create_resource_object('window', xid)
        else:
            return None

    def move_window_to_workspace(self, window, workspace, source_indication=1):
        """
            move a window to a workspace.

            :param window: Xlib.Window
            :param workspace: workspace id, starting at 0
            :param source_indication: the source indication, required by netwm
                                       standard. see
                                       http://standards.freedesktop.org/wm-spec/wm-spec-latest.html#sourceindication
            :note: Use it on your own risk. Non-existant workspaces could be your suicide.
        """
        self._send_clientmessage(window, "_NET_WM_DESKTOP", [workspace, indication])

    def close_window(self, window, source_indication=1):
        """
            we want the window closed.

            :param window: Xlib.Window
            :param source_indication: see http://standards.freedesktop.org/wm-spec/wm-spec-latest.html#sourceindication
        """
        self._send_clientmessage(window, "_NET_CLOSE_WINDOW", [get_timestamp(), source_indication])

    def moveresize_window(self, window, gravity=0, x=-1, y=-1, width=-1, height=-1):
        """
            Move or resize the window
            :param window: Xlib.Window
            :param gravity: The desired gravity. See http://standards.freedesktop.org/wm-spec/wm-spec-latest.html
            :param x: desired x or -1
            :param y: desired y or -1
            :param width: desired width or -1
            :param height: desired height or -1
            :note: a negative value would be the apocalypse.
        """
        flags = gravity
        # calculate the flags
        if x > -1:
            flags |= 1 << 8
        else:
            x = 0
        if y > -1:
            flags |= 1 << 9
        else:
            y = 0
        if width > 0:
            flags |= 1 << 10
        else:
            width = 0
        if height > 0:
            flags |= 1 << 11
        else:
            height = 0
        self._send_clientmessage(window, "_NET_MOVERESIZE_WINDOW", [flags, x, y, width, height])

    def get_desktop_names(self):
        """
            return a list of UTF-8 desktop names or [], if an error occured
        """
        prop = self._get_property(self.root, "_NET_DESKTOP_NAMES")
        if prop:
            return [x for x in prop.value.split('\x00') if x] # do not return empty strings
        else:
            return []

    def get_number_of_desktops(self):
        """
            return the number of desktops or -1
        """
        prop = self._get_property(self.root, "_NET_NUMBER_OF_DESKTOPS")
        if prop:
            return prop.value[0]
        else:
            return -1

    def get_window_pid(self, window):
        """
            return the PID of the current window or 0
        """
        prop = self._get_property(window, "_NET_WM_PID")
        if prop:
            return prop.value[0]
        else:
            return -1

    def maximize_window(self, window):
        """
            maximize the window `window` horizontally and vertically.
        """
        self._send_clientmessage(window, "_NET_WM_STATE",
                [1, # _NET_WM_STATE_ADD
                    self._get_atom('_NET_WM_STATE_MAXIMIZED_VERT'),
                    self._get_atom('_NET_WM_STATE_MAXIMIZED_HORZ'),
                1])

    def toggle_showing_desktop(self, show):
        """
            Show the desktop. Or not.
        """
        self._send_clientmessage(self.root, "_NET_SHOWING_DESKTOP", [show])

if __name__ == '__main__':
    wmctrl = Screen()
    print 'Active workspace (starting at 0):', wmctrl.get_current_workspace()
    print 'Active window id:', wmctrl.get_active_window_id()
    print 'Number of desktops:', wmctrl.get_number_of_desktops()
    print 'Desktop names:', wmctrl.get_desktop_names()
    print 'PID of active window:', wmctrl.get_window_pid(wmctrl.get_active_window()), '=>', get_process_executable(wmctrl.get_window_pid(wmctrl.get_active_window()))
#    wmctrl.moveresize_window(wmctrl.get_active_window(), x=100, y=100)
#    wmctrl.close_window(wmctrl.get_active_window())
#    wmctrl.change_workspace(1)
#    wmctrl.move_window_to_workspace(wmctrl.get_active_window(), 1)
#    wmctrl.maximize_window(wmctrl.get_active_window())
