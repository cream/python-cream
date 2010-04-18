import gobject
import weakref

FEATURES = dict()


class NoSuchFeature(BaseException):
    pass


class Feature(object):
    dependencies = None

    def __finalize__(self):
        pass

    def __new__(cls, component):
        """ Make sure all dependencies for this feature are loaded. """
        if cls.dependencies:
            for dependency in cls.dependencies:
                if dependency not in component._loaded_features:
                    component.load_feature(dependency)
        return super(Feature, cls).__new__(cls, component)


class ConfigurationFeature(Feature):

    def __init__(self, component):

        Feature.__init__(self)

        from .config import Configuration

        component.config = Configuration.fromxml(component.context.working_directory)
        self.config = component.config

        self.autosave = True


    def __finalize__(self):

        if self.autosave:
            self.config.save()


class HotkeyFeature(Feature, gobject.GObject):
    dependencies = (ConfigurationFeature,)

    __gtype_name__ = 'HotkeyFeature'
    __gsignals__ = {
        'hotkey-activated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    def __init__(self, component):

        from gpyconf.contrib.gtk import HotkeyField
        import cream.ipc
        from dbus.exceptions import DBusException

        Feature.__init__(self)
        gobject.GObject.__init__(self)

        self.component = weakref.ref(component)
        self.component().hotkeys = self

        try:
            self.manager = cream.ipc.get_object('org.cream.hotkeys', '/org/cream/hotkeys')
        except DBusException:
            import warnings
            warnings.warn("Could not connect to the cream hotkey manager")
            return

        self.broker = cream.ipc.get_object('org.cream.hotkeys', self.manager.register(), interface='org.cream.hotkeys.broker')
        self.broker.connect_to_signal('hotkey_activated', self.hotkey_activated_cb)

        for name, field in self.component().config.fields.iteritems():
            if isinstance(field, HotkeyField):
                self.broker.set_hotkey(field.action, field.value)
                field.connect('value-changed', self.configuration_field_value_changed_cb)


    def configuration_field_value_changed_cb(self, source, field, value):

        self.broker.set_hotkey(field.action, field.value)


    def hotkey_activated_cb(self, action):
        self.emit('hotkey-activated', action)



FEATURES.update({
    'org.cream.config' : ConfigurationFeature,
    'org.cream.hotkeys': HotkeyFeature
})
