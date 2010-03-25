PYTHON?=python
TESTFLAGS=-p -v
TESTOPTS=
SETUPFLAGS=
GCC=gcc
VER=2.6
DESTDIR=.

all: build

build:
	$(GCC) -c -fpic procnamemodule.c -DHAVE_CONFIG_H -I/usr/include/python$(VER) -I/usr/lib/python$(VER)/config
	$(GCC) -shared procnamemodule.o  -o $(DESTDIR)/procname.so
