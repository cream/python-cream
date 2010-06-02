from gtk import Builder

class GtkBuilderInterface(object):
    """
    Integrates GTKBuilder interfaces into a class so that you can access
    widgets defined in the UI file as if they were attributes of the class.

    Example::

        class MyGreatWindow(GtkBuilderInterface):
            def __init__(self):
                GtkBuilderInterface.__init__(self, '/path/to/ui.glade')
                self.window.show_all()

    where ``window`` is a window defined in the UI file.

    :param builder_file: Path to the UI file
    """
    def __init__(self, builder_file):
        self._builder_file = builder_file
        self._builder_tree = Builder()
        self._builder_tree.add_from_file(builder_file)

    def __getattr__(self, attr):
        obj = self._builder_tree.get_object(attr)
        if obj is None:
            raise AttributeError(attr)
        return obj

    def connect_signals(self, *a):
        self._builder_tree.connect_signals(*a)
