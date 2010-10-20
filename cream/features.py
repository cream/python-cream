import os
import gobject
import weakref

FEATURES = dict()

class NoSuchFeature(Exception):
    pass

class Feature(object):
    """ "Feature" that can be "mixed" into Cream components. """
    dependencies = None

    def __new__(cls, component, *args, **kwargs):
        """ Make sure all dependencies for this feature are loaded. """
        if cls.dependencies:
            for dependency in cls.dependencies:
                component.load_feature(dependency, *args, **kwargs)
        return super(Feature, cls).__new__(cls)

    def __finalize__(self):
        pass


class ConfigurationFeature(Feature):
    autosave = True

    def __init__(self, component, read=True):

        if read == True or read == 'true':
            read = True
        else:
            read = False

        Feature.__init__(self)

        from .config import Configuration

        component.config = Configuration(component.context.working_directory,
                                         read=read)
        self.config = component.config

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


class ExtensionFeature(Feature):
    def __init__(self, component, directory='extensions'):
        Feature.__init__(self, component)

        from cream.extensions import ExtensionManager
        component.extension_manager = ExtensionManager(
            [os.path.join(component.context.working_directory, directory)],
            component.extension_interface
        )


FEATURES.update({
    'org.cream.extensions'  : ExtensionFeature,
    'org.cream.config'      : ConfigurationFeature,
    'org.cream.hotkeys'     : HotkeyFeature
})
