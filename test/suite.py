from test import Environment

testsuites    = []
_default_suite = None


class _TestSuite(object):
    def __init__(self, name="default", tests=list(), environment=None, register_arguments=None):
        if environment is None:
            environment = Environment()
        if register_arguments is None:
            register_arguments = lambda x: None
        self.name               = name
        self.tests              = tests
        self.environment        = environment
        self.register_arguments = register_arguments


def get_default_suite():
    """Returns the default test suite"""
    return _default_suite

def add(test):
    """Add a test case to the default test suite"""
    global _default_suite
    if _default_suite is None:
        _default_suite = _TestSuite()
    _default_suite.tests.append(test)

def make(name, tests, environment=None, register_arguments=None):
    """Create a test suite. Make it the default one, if there is no default so far."""
    global _default_suite
    suite = _TestSuite(name, tests, environment, register_arguments)
    testsuites.append(suite)
    if _default_suite is None:
        _default_suite = suite
    return suite

def set_environment(environment):
    """Set the initial environment of the default test suite"""
    _default_suite.environment = environment

def set_register_arguments(register_arguments):
    """Set the initial register_arguments function of the default test suite"""
    _default_suite.register_arguments = register_arguments
