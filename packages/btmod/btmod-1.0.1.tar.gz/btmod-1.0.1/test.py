
"""
Test of btm - Buit-in Types Modificator. 
"""

import btm

def _run_test(test_function):
    test_name = "btm." + test_function.__name__[len("_test_"):]
    print("testing %s" % test_name)
    try:
        test_function()
        print("%s test is passed" % test_name)
    except:
        import traceback
        traceback.print_exc()
        return "%s test failed" % test_name

_test_functions = []

def _test():
    for test_function in _test_functions:
        error = _run_test(test_function)
        if error:
            return error
    print("All tests were sucessfully passed") 
    return 0

def _add_test(test_function):
    _test_functions.append(test_function)

@_add_test
def _test_addattr():
    btm.addattr(int, "lol", 10)
    assert (1).lol == 10

@_add_test
def _test_subattr():
    print("btm.subattr is btm.addattr")

@_add_test
def _test_addmeth():
    @btm.addmeth(str)
    def print(self):
        global print
        print(self)
    "Lol".print()

@_add_test
def _test_submeth():
    print("btm.submeth is btm.addmeth")

@_add_test
def _test_subclass():
    global str
    @btm.subclass(str)
    class str:
        prop = "Hello World!"
        def print_hello(self):
            print(self.prop)
    
    "".print_hello()

    # This is equivalent:

    class str_subclass:
        prop = "Hello World!"
        def print_hello(self):
            print(self.prip)

    btm.subclass(str, str_subclass)

    "".print_hello()

if __name__ == "__main__":
    exit(_test())

