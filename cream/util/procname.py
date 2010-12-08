#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys
import ctypes

libc = ctypes.CDLL(None)
strlen = libc.strlen
strlen.argtypes = [ctypes.c_void_p]
strlen.restype = ctypes.c_size_t

memset = libc.memset
memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
memset.restype = ctypes.c_void_p

PR_SET_NAME = 15
PR_GET_NAME = 16

prctl = libc.prctl
prctl.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong] # we don't want no type safety
prctl.restype = ctypes.c_int

def _get_argc_argv():
    argv = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))()
    argc = ctypes.c_int()
    ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))
    return (argc, argv)

def getprocname():
    argc, argv = _get_argc_argv()
    return ctypes.cast(argv[0], ctypes.c_char_p).value

def setprocname(name):
    argc, argv = _get_argc_argv()
    libc.strncpy(argv[0], name, len(name))
    next = ctypes.addressof(argv[0].contents) + len(name)
    nextlen = strlen(next)
    libc.memset(next, 0, nextlen)
    if prctl(PR_SET_NAME, name, 0, 0, 0) != 0:
        raise OSError()
