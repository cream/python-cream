import gobject
import weakref

FEATURES = {}

class NoSuchFeature(BaseException):
    pass


class ConfigurationFeature(object):

    def __init__(self, component):

        from .config import Configuration
        component.config = Configuration.fromxml(component.context.wd)
        component.config_loaded = True


class HotkeyFeature(gobject.GObject):

    __gtype_name__ = 'HotkeyFeature'
    __gsignals__ = {
        'hotkey-activated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        }

    def __init__(self, component):

        from gpyconf.contrib.gtk import HotkeyField
        import cream.ipc

        gobject.GObject.__init__(self)

        self.component = weakref.ref(component)
        self.component().hotkeys = self

        try:
            self.manager = cream.ipc.get_object('org.cream.hotkeys', '/org/cream/hotkeys')
            self.broker = cream.ipc.get_object('org.cream.hotkeys', self.manager.register(), interface='org.cream.hotkeys.broker')
            self.broker.connect_to_signal('hotkey_activated', self.hotkey_activated_cb)
        except:
            return

        for k, f in self.component().config.fields.iteritems():
            if isinstance(f, HotkeyField):
                self.broker.set_hotkey(f.action, f.value)
                f.connect('value-changed', self.configuration_field_value_changed_cb)


    def configuration_field_value_changed_cb(self, source, field, value):

        self.broker.set_hotkey(field.action, field.value)


    def hotkey_activated_cb(self, action):
        self.emit('hotkey-activated', action)


FEATURES.update({
    'org.cream.hotkeys': HotkeyFeature,
    'org.cream.config': HotkeyFeature,
    })
