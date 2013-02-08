from test import Environment

testsuites    = []
_default_suite = None


class _TestSuite(object):
    def __init__(self, name, tests, environment, register_arguments):
        self.name               = name
        self.tests              = tests
        self.environment        = environment
        self.register_arguments = register_arguments


def get_default_suite():
    return _default_suite


def make(name, tests, environment=None, register_arguments=None):
    global _default_suite
    if environment is None:
        environment = Environment()
    if register_arguments is None:
        register_arguments = lambda: None
    suite = _TestSuite(name, tests, environment, register_arguments)
    testsuites.append(suite)
    if _default_suite is None:
        _default_suite = suite
    return suite
