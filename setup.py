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
        'cream.xdg.desktopentries'
    ],
    package_data={'cream.config': ['interface/*']}
)
