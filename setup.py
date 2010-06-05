from distutils.core import setup
from distutils.extension import Extension

setup(
    name = 'Cream Libraries',
    version = '0.1',
    packages = ['cream', 'cream.gui', 'cream.contrib', 'cream.config', 'cream.ipc', 'cream.util'],
    package_data={'cream.config': ['interface/*']}
    )
