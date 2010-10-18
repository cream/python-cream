import os

XDG_DATA_DIRS = os.environ['XDG_DATA_DIRS'].split(':')
XDG_DATA_HOME = os.environ['XDG_DATA_HOME'].split(':')

CONFIG_DIRS = [os.path.join(d, 'cream/config') for d in XDG_DATA_HOME + XDG_DATA_DIRS]
MODULE_DIRS = [os.path.join(d, 'cream/modules') for d in XDG_DATA_HOME + XDG_DATA_DIRS]
DATA_DIRS = [os.path.join(d, 'cream/data') for d in XDG_DATA_HOME + XDG_DATA_DIRS]
