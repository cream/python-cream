from distutils.core import setup

setup(
    name = 'Cream Libraries',
    version = '0.1',
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
            'cream.contrib.appindicators.watcher'
    ],
    package_data={'cream.config': ['interface/*']}
)
