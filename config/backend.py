import os
from gpyconf.backends import Backend
from gpyconf.backends._xml.xmlserialize import serialize, unserialize
from cream.util.string import slugify
from xml.parsers.expat import ExpatError

class CreamXMLBackend(dict, Backend):
    ROOT_ELEMENT = 'profile'

    def __init__(self, backref, folder=None):
        dict.__init__(self)
        Backend.__init__(self, backref)
        self.folder = folder or self.backref().basedir # TODO

        self.profiles = list()
        self.selected_profile = 0

        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)

    def read(self):
        for profile in os.listdir(self.folder):
            with open(os.path.join(self.folder, profile)) as fobj:
                try:
                    profile = unserialize(fobj)
                except ExpatError, e:
                    self.warn("Failed to parse '%s': %s" % (fobj.name, e))
                else:
                    self.profiles.insert(profile['position']-1, profile)
                    if profile.get('selected', False):
                        self.selected_profile = profile['position']

    def save(self):
        def _(s):
            return slugify(s) + '.xml'

        profile_list = self.backref().profiles
        selected_profile = self.backref().active_profile

        for profile in self.backref().profiles:
            if not profile.is_editable: continue
            with open(os.path.join(self.folder, _(profile.name)), 'w') as fobj:
                serialize({
                    'name' : profile.name,
                    'values' : profile.values,
                    'position' : profile_list.index(profile),
                    'selected' : selected_profile == profile
                }, root_node=self.ROOT_ELEMENT, file=fobj)

    def get_option(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise MissingOption(item)
    set_option = lambda self, item, value: self.__setitem__(item, value)

    options = property(lambda self:self.keys())
    tree = property(lambda self:self)
