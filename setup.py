from distutils.core import setup
from distutils.extension import Extension

setup(
    name = 'Cream Libraries',
    version = '0.1',
    packages = ['cream', 'cream.gui', 'cream.contrib', 'cream.config', 'cream.ipc', 'cream.util'],
    ext_modules=[Extension('cream.util.procname', ['cream/util/procnamemodule.c'])],
    package_data={'cream.config': ['interface/*']}
    )
