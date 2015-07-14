from functools import partial
from time      import time
import sys
import sisyphus.util.shell as shell

import logging
_LOGGER = logging.getLogger("sisyphus")

def step_name(name):
    """Decorator for step functions to give them a name
    instead of giving a name via the add_step method"""
    def add_attrib(func):
        func.__step_name = name
        return func
    return add_attrib

class StepResult(object):
    """Captures the result of a single "step". Typical steps are the execution
    of 1 external command with additional verification/checking of the results.
    In a typical test we have two steps: compilation with checking of compiler
    warnings+errors and execution of the compiled program with comparison of the
    output with a reference output."""
    def __init__(self):
        self.cmd      = None
        self.error    = None
        self.retcode  = 0
        self.stderr   = ""
        self.stdout   = ""
        self.time     = None

    # please excuse the internet slang method names ;-)
    def fail(self):
        """returns True if there were errors so far"""
        return self.error is not None

    def win(self):
        """returns True if there were no errors so far"""
        return not self.fail()


def execute(environment, cmd, timeout, rlimit=None):
    "Executes an external command and returns a StepResult object"
    result     = StepResult()
    result.cmd = cmd
    _LOGGER.info(cmd)
    try:
        begin = time()
        result.stdout, result.stderr, result.retcode = shell.execute(cmd, timeout=timeout, rlimit=rlimit)
        result.time = time() - begin
    except shell.SigKill as e:
        _LOGGER.debug("SigKill: "+e.name)
        result.error = e.name
    except MemoryError as e:
        _LOGGER.debug("MemoryError")
        result.error = "out of memory"
    except OSError as e:
        _LOGGER.debug("OSError: "+e.strerror)
        result.error = e.strerror
    if result.stderr != "":
        err = result.stderr
        if err[-1:] != '\n':
            err = err + '\n'
        sys.stderr.write(err)
    return result


def step_execute(environment, rlimit=None):
    """Run compiled test program"""
    if not hasattr(environment, "runexe"):
        environment.runexe = ""
    if not hasattr(environment, "executionargs"):
        environment.executionargs = ""
    cmd = "%(runexe)s%(executable)s %(executionargs)s" % environment
    return execute(environment, cmd, timeout=30, rlimit=rlimit)


def _step_append_flags(environment, args):
    for (key, value) in args.iteritems():
        attr_value = getattr(environment, key)
        attr_value += value
        setattr(environment, key, attr_value)
    return StepResult()


def create_step_append_flags(**kwargs):
    return partial(_step_append_flags, args=kwargs)
