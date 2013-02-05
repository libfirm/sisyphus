import os

annotated_test_factories = list()

def ensure_dir(name):
    try:
        os.makedirs(name)
    except Exception:
        pass
    if not os.path.isdir(name):
        raise Exception("Couldn't create test output directory '%s'" % (name,))

def test_factory(matcher):
    """Annotation for functions which generate Tests.
    Requires a function to decide if a filename is a valid test file."""
    def register(func):
        annotated_test_factories.append((matcher, func))
    return register

class TestStep(object):
    def __init__(self, name, func):
        self.name   = name
        self.func   = func
        self.checks = []

    def add_check(self, check):
        self.checks.append(check)

    def add_checks(self, checks):
        self.checks += checks


class Test(object):
    """The default Test which executes a list of steps and checks."""
    def __init__(self, environment, id):
        self.id          = id
        self.steps       = []
        self.environment = environment

    def add_step(self, name, func):
        step = TestStep(name, func)
        self.steps.append(step)
        return step

    def run(self):
        self.success     = True
        self.result      = "ok"
        self.stepresults = dict()
        # Execute steps
        for step in self.steps:
            stepresult = step.func(self.environment)
            # while stepresult is fine use checks
            for check in step.checks:
                if stepresult.fail():
                    break
                check(stepresult)
            self.stepresults[step.name] = stepresult
            if stepresult.fail():
                self.success = False
                self.result  = "%s: %s" % (step.name, stepresult.error)
                break

# vim: expandtab ts=4 st=4 sw=4
