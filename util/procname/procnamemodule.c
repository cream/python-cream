/*
  Copyright (C) 2008  Eugene A. Lisitsky 

  The procname library for Python.

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include <Python.h>
#include <sys/prctl.h>

PyDoc_STRVAR(procname__doc__, "Module for setting/getting process name");

static PyObject *
procname_check(PyObject *self, PyObject *args) {	return Py_BuildValue("i", 1);
};


static PyObject *
procname_getprocname(PyObject *self, PyObject *args) {	int argc;
	char **argv;
	Py_GetArgcArgv(&argc, &argv);
	return Py_BuildValue("s", argv[0]);
};


static PyObject *
procname_setprocname(PyObject *self, PyObject *args) {	int argc;
	char **argv;
	char *name;
	if (!PyArg_ParseTuple(args, "s", &name))
		return NULL;
	Py_GetArgcArgv(&argc, &argv);
	strncpy(argv[0], name , strlen(name));
	memset(&argv[0][strlen(name)], '\0', strlen(&argv[0][strlen(name)]));
	prctl (15 /* PR_SET_NAME */, name, 0, 0, 0);
	Py_INCREF(Py_None);
	return Py_None;
};


static PyMethodDef procname_methods[] = {	{"check", procname_check, METH_VARARGS, "Test func"},
	{"getprocname", procname_getprocname, METH_VARARGS,
		"Get procname.\nReturns name (string)"},
	{"setprocname", procname_setprocname, METH_VARARGS,
		"Set procname.\n  name (string) -> new process name.\nReturns None."},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initprocname(void) {	(void) Py_InitModule3("procname", procname_methods, procname__doc__);
}

