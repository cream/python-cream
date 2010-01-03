"""
    cream.gui.dialogs
    ~~~~~~~~~~~~~~~~~

    ...Description...

    Use it like this::

        >>> Dialog(gtk.Button('Click me'), ('YES', 'NO', 'CANCEL')).run()
        'NO'
        >>> yesno_dialog = YesNoDialog("Sure you wanna destroy our planet?")
        >>> yesno_dialog.run()
        True
        >>> InputDialog("Put something in that box, please!").run()
        'Hello World!'
        >>> InputDialog("Again").run()
        None # User didn't press 'OK' but 'CANCEL' or closed the dialog
"""
import gtk
from cream.util import flatten

GTK_RESPONSES = (
    'NONE',
    'REJECT',
    'ACCEPT',
    'DELETE_EVENT',
    'OK',
    'CANCEL',
    'CLOSE',
    'YES',
    'NO',
    'APPLY',
    'HELP'
)

GTK_BUTTON_SETS = (
    'NONE',
    'OK',
    'CLOSE',
    'CANCEL',
    'YES_NO',
    'OK_CANCEL'
)

def _gtk_message_type_by_name(type):
    if type is None:
        return gtk.MESSAGE_INFO
    else:
        try:
            return getattr(gtk, 'MESSAGE_%s' % type.upper())
        except AttributeError:
            raise TypeError("No such gtk message type '%s'" % type)

def _build_button_tuple(button):
    if not button.startswith('gtk-'):
        try:
            button = getattr(gtk, 'STOCK_%s' % button.upper())
        except AttributeError:
            raise TypeError("No such button '%s' in gtk stock" % button)
    response = getattr(gtk, 'RESPONSE_%s' % button[4:].upper())
    return (button, response)

class GtkResponses(dict):
    def __getitem__(self, item):
        item = 'RESPONSE_%s' % item.upper()
        if hasattr(gtk, item):
            return getattr(gtk, item)
        else:
            raise AttributeError(item)

    def fromid(self, id):
        return GTK_RESPONSES[abs(id)-1]
RESPONSES = GtkResponses()


class Dialog(gtk.Dialog):
    def __init__(self, content, buttons, title=None, parent=None, flags=0):
        buttons = map(_build_button_tuple, buttons)
        self.buttons = dict(buttons)
        gtk.Dialog.__init__(self, title, parent, flags, tuple(flatten(buttons)))
        self.vbox.pack_start(content, True, True)

    def run(self, destroy=True):
        self.show_all()
        response = gtk.Dialog.run(self)
        if destroy:
            self.destroy()
        return RESPONSES.fromid(response)

class YesNoDialog(Dialog):
    """ Shortcut to MessageDialog(..., buttons=('YES', 'NO')) """
    def __init__(self, message, title=None, parent=None, flags=0):
        self.message = message = gtk.Label(message)
        Dialog.__init__(self, message, ('YES', 'NO'), title, parent, flags)

    def run(self):
        return Dialog.run(self) == 'YES'


class InputDialog(Dialog):
    invalid_inputs = ()
    error_message = "Invalid input '%s'!"
    def __init__(self, message, default='', title=None, parent=None, flags=0):
        self.message = message = gtk.Label(message)
        message.set_use_markup(True)

        Dialog.__init__(self, message, ('OK', 'CANCEL'), title, parent, flags)
        self.entry = gtk.Entry()
        self.entry.set_text(default)
        self.entry.connect('activate', (lambda widget:self.emit(
            'response', RESPONSES['OK'])))
        self.vbox.pack_start(self.entry, True, True)

    def run(self):
        ret = Dialog.run(self, destroy=False)
        # do not auto-destroy for we're not sure if this dialog
        # has to re-appear (invalid inputs)
        if ret == 'OK':
            input = self.entry.get_text()
            if input in self.invalid_inputs:
                # invalid input, throw an error message...
               ErrorMessageDialog(self.error_message % input).run()
               # ...and begin and start from scratch
               return self.run()
            else:
                self.destroy()
                return input
        else:
            self.destroy()


class MessageDialog(gtk.MessageDialog):
    def __init__(self, message, button, type=None, parent=None, flags=0):
        type = _gtk_message_type_by_name(type)
        button = GTK_BUTTON_SETS.index(button.upper())
        self.message = message
        gtk.MessageDialog.__init__(self, parent, flags, type, button, message)

    def run(self):
        gtk.MessageDialog.run(self)
        self.destroy()

class ErrorMessageDialog(MessageDialog):
    def __init__(self, message, title='Error', parent=None, flags=0):
        MessageDialog.__init__(self, message, 'CLOSE', title, parent, flags)
