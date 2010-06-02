from setuptools import setup, find_packages, Extension

setup(
    name = 'Cream Libraries',
    version = '0.1',
    packages = find_packages(),
    ext_modules=[Extension('cream.util.procname', ['cream/util/procnamemodule.c'])],
    include_package_data = True,
    package_data={'cream.config': ['interface/*']}
    )
