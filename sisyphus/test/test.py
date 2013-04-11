from copy import deepcopy
import logging
import os

def ensure_dir(name):
    try:
        os.makedirs(name)
    except Exception:
        pass
    if not os.path.isdir(name):
        raise Exception("Couldn't create test output directory '%s'" % (name,))


class Environment(dict):
    """Environment objects track settings in the testsuite. The settings are
    normal python attributes. The class just provides some convenience
    functions for constructing/merging configurations."""
    def __init__(self, **kwargs):
        dict.__init__(self)
        self.merge(kwargs)
        self.disable_override = False

    def set(self, **kwargs):
        self.merge(kwargs)

    def merge(self, mutable_set):
        for (key, value) in mutable_set.iteritems():
            self[key] = value

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError("Environment has no attribute '%s'" % name)
    def __setattr__(self, name, value):
        if name in self and self.disable_override:
            raise Exception("Overriding disabled for environment")
        self[name] = value
    def __delattr__(self, name):
        if name in self:
            del self[name]
        raise AttributeError()

class TestStep(object):
    def __init__(self, name, func):
        self.name   = name
        self.func   = func
        self.checks = []
        self.before = lambda env: None

    def set_before(func):
        """Set a function to execute right before step is executed.
        The functions gets the environment as its single argument."""
        self.before = func

    def add_check(self, check):
        self.checks.append(check)

    def add_checks(self, checks):
        self.checks += checks

class Test(object):
    """The default Test which executes a list of steps and checks."""
    def __init__(self, id):
        self.id          = id
        self.steps       = []
        self.environment = Environment(testname = id)

    def add_step(self, name, step_func=None, checks=[]):
        # actually name can be None, but not step_func
        # for backwards compatibility, here comes the workaround
        if step_func == None:
            step_func = name
            name = None
        if not name:
            if hasattr(step_func, "__step_name"):
                name = getattr(step_func, "__step_name")
            else:
                name = step_func.__name__
                if name.startswith("step_"):
                    name = name[5:]
        step = TestStep(name, step_func)
        self.steps.append(step)
        step.add_checks(checks)
        return step

    def prepend_step(self, name, step_func, checks=[]):
        step = TestStep(name, step_func)
        self.steps.insert(0, step)
        step.add_checks(checks)
        return step

    def run(self):
        self.success     = True
        self.result      = "ok"
        self.stepresults = dict()
        # Execute steps
        for step in self.steps:
            step.before(self.environment)
            stepresult = step.func(self.environment)
            if stepresult is None:
                logging.error("%s: stepresult of '%s' is None" % (self.id, step.name))
                continue
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
