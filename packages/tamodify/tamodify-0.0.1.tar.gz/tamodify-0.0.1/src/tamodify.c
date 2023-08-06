#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "tajk_modify.h"

static stru_ta_modify tm;

static PyObject *
p_open(PyObject *self, PyObject *args)
{
    char *fnsrc,*fndst;//Դ�ļ�����Ŀ���ļ���
    if (!PyArg_ParseTuple(args, "ss", &fnsrc,&fndst))return NULL;
    return PyLong_FromLong(tamodify_open(fnsrc,fndst));
}

static PyMethodDef pMethods[] = {
    {"open",  p_open, METH_VARARGS,"ָ��Դ�ļ���Ŀ���ļ���ʼ���ơ��޸�"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef pmodule = {
    PyModuleDef_HEAD_INIT,
    "tamodify",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    pMethods
};

PyObject *
PyInit_tamodify(void){
    tamodify_init(&tm);
    return PyModule_Create(&pmodule);
}
