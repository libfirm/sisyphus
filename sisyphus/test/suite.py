from test import Environment

testsuites        = []
_argparser_setups = []


class _TestSuite(object):
    def __init__(self, name, tests=list(), environment=None, default=True):
        if environment is None:
            environment = Environment()
        self.name        = name
        self.tests       = tests
        self.environment = environment
        self.default     = default


def add(test):
    """Add a test case to the default test suite"""
    global _default_suite
    if _default_suite is None:
        _default_suite = make("default", [])
    _default_suite.tests.append(test)


def make(name, tests, environment=None, default=True):
    """Create a test suite. Make it the default one, if there is no default so far."""
    suite = _TestSuite(name, tests, environment, default)
    testsuites.append(suite)
    return suite


def add_argparser_setup(func):
    global _argparser_setups
    _argparser_setups.append(func)


def run_argparser_setups(argparser, default_env):
    for setup in _argparser_setups:
        setup(argparser, default_env)
