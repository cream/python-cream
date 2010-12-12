from distutils.core import setup

setup(
    name = 'cream-libs',
    version = '0.4',
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
