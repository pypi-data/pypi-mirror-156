
"""
btm - Built-in Types Modificator

Modify Python built-in types.

Home page - See btm.URL.

"""

from ctypes import pythonapi, POINTER, py_object

__all__ = ["addattr", "subattr", "addmeth", "submeth", "subclass", "delattr"]

_getdictptr = pythonapi._PyObject_GetDictPtr
_getdictptr.restype = POINTER(py_object)
_getdictptr.argtypes = [py_object]

def _get_dict(value):
    dictionary_pointer = _getdictptr(value)
    try:
        return dictionary_pointer.contents.value
    except ValueError as exception:
        message = "%r isn't a built-in class" % value 
        raise ValueError(message) from exception

def addattr(cls, name, attribute):
    name = str(name)
    if not name.isidentifier():
        message = "%r isn't a identifier" % name
        raise ValueError(message)
    _get_dict(cls)[name] = attribute
subattr = addattr # substitution and addition is equivalent

def addmeth(cls, name = None):
    def add_method_decorator(method):
        nonlocal name
        if name is None:
            name = method.__name__
        addattr(cls, name, method)
    return add_method_decorator

submeth = addmeth # subtitution and addition is equivalent

def _real_subclass(cls, subclass):
    dictionary = _get_dict(cls)
    additions = dict(subclass.__dict__)
    for delete in ("__module__", "__dict__", "__weakref__", "__doc__"):
        del additions[delete]
    for name, value in additions.items():
        addattr(cls, name, value)
    return cls

def subclass(cls, subclass = None):
    if isinstance(subclass, type):
        return _real_subclass(cls, subclass)
    else:
        def subclass_decorator(subclass):
            return _real_subclass(cls, subclass)
        return subclass_decorator

def delattr(cls, name):
    # del _get_dict(cls)[name] # For some reason this not work
    raise NotImplementedError

