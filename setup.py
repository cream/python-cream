from distutils.core import setup

setup(
    name = 'python-cream',
    version = '0.5.3',
    author = 'The Cream Project (http://cream-project.org)',
    url = 'http://github.com/cream/python-cream',
    packages = [
        'cream',
        'cream.gui',
        'cream.config',
        'cream.ipc',
        'cream.util',
        'cream.xdg',
        'cream.xdg.desktopentries'
    ],
    package_data={'cream.config': ['interface/*']}
)
