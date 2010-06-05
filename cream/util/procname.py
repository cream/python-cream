import sys
import ctypes

libc = ctypes.CDLL(None)

PR_SET_NAME = 15
PR_GET_NAME = 16

prctl = libc.prctl
#prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong] # we don't want no type safety
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
    nextlen = libc.strlen(next)
    libc.memset(next, 0, nextlen)
    if prctl(PR_SET_NAME, name, 0, 0, 0) != 0:
        raise OSError()
