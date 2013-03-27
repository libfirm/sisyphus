from test import Environment

testsuites        = []
_argparser_setups = []
_default_suite    = None


class _TestSuite(object):
    def __init__(self, name="default", tests=list(), environment=None):
        if environment is None:
            environment = Environment()
        self.name               = name
        self.tests              = tests
        self.environment        = environment


def get_default_suite():
    """Returns the default test suite"""
    return _default_suite


def add(test):
    """Add a test case to the default test suite"""
    global _default_suite
    if _default_suite is None:
        _default_suite = _TestSuite()
    _default_suite.tests.append(test)


def make(name, tests, environment=None):
    """Create a test suite. Make it the default one, if there is no default so far."""
    global _default_suite
    suite = _TestSuite(name, tests, environment)
    testsuites.append(suite)
    if _default_suite is None:
        _default_suite = suite
    return suite


def add_argparser_setup(func):
    global _argparser_setups
    _argparser_setups.append(func)


def run_argparser_setups(argparser, default_env):
    for setup in _argparser_setups:
        setup(argparser, default_env)
