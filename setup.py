from distutils.core import setup

setup(
    name = 'cream-libs',
    version = '0.4',
    author = 'The Cream Project (http://cream-project.org)',
    url = 'http://github.com/cream/libs',
    packages = [
        'cream',
        'cream.gui',
        'cream.config',
        'cream.ipc',
        'cream.util',
        'cream.contrib.desktopentries',
        'cream.contrib.appindicators',
            'cream.contrib.appindicators.dbusmenu',
            'cream.contrib.appindicators.host',
            'cream.contrib.appindicators.watcher',
        'cream.contrib.notifications',
        'cream.contrib.udisks'
    ],
    package_data={'cream.config': ['interface/*']}
)
