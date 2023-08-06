btm - Built-in Types Modificator
================================

This is a library written in pure python that allows you to modify the python built-in types easily.
For example:

```python
import btm
btm.addattr(int, "lol", 10)
print((1).lol) # Output: 10
```

How this works!?
----------------

- no C extensions, only pure python
- no preprocessors

Using the native library ctypes:
`ctypes.pythonapi._PyObject_GetDictPtr` do the trick.

Installation
------------
The simpliest way is using [pip](https://github.com/pypa/pip)

```bash
pip install btmod
```

or from github:

```bash
git clone https://github.com/nacho00112/btm
cd btm
python3 setup.py install
```

For test:

```bash
python3 test.py
```

Documentation
-------------

The documentation is available in [The btm documentation page](https://github.com/nacho00112/btm/tree/main/docs/index.md)

Contribution
------------

Contributions are welcome, see [CONTRIBUTE.md](https://github.com/nacho00112/btm/tree/main/CONTRIBUTE.md) for more information.

For bugs, questions, suggestions etc.
-------------------------------------

Go to [issues](https://github.com/nacho00112/btm/issues).

Contact
-------
- email
    - <thurealrubiogame@gmail.com>
- issues
    - [issues](https://github.com/nacho00112/btm/issues)

Creators
--------
- [Nacho](https://github.com/nacho00112)
- Only created by me!

