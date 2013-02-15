import logging
import os


def ensure_dir(name):
    try:
        os.makedirs(name)
    except Exception:
        pass
    if not os.path.isdir(name):
        raise Exception("Couldn't create test output directory '%s'" % (name,))


class Environment(object):
    """Environment objects track settings in the testsuite. The settings are
    normal python attributes. The class just provides some convenience
    functions for constructing/merging configurations."""

    def __init__(self, **kwargs):
        self.merge_dict(kwargs)

    def set(self, **kwargs):
        self.merge_dict(kwargs)

    def merge(self, other):
        self.merge_dict(other.__dict__)

    def merge_dict(self, d):
        for (key, value) in d.iteritems():
            if key.startswith("_"):
                continue
            setattr(self, key, value)


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

    def run(self, environment):
        self.success     = True
        self.result      = "ok"
        self.stepresults = dict()
        # Execute steps
        for step in self.steps:
            step.before(environment)
            stepresult = step.func(environment)
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
