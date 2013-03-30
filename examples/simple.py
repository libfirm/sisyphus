import test
from glob import glob
from test.test import Test
from test.checks import check_retcode_zero, create_check_reference_output
from test.steps import execute

def step_run(environment):
    """Simple teststep which executes a shell script"""
    cmd = "/bin/sh %(testname)s" % environment
    return execute(environment, cmd, timeout=10)

def make_shell_test(name):
    """Constructs a shell test"""
    test = Test(name)
    test.add_step("run", step_run, checks=[
        check_retcode_zero,
        create_check_reference_output(name+".ref"),
    ])
    return test

# Create testlist
tests = []
for filename in [ "tests/test1.sh", "tests/test2.sh", "tests/fail.sh", "tests/mismatch.sh" ]:
    t = make_shell_test(filename)
    tests.append(t)

test.suite.make("shell", tests=tests)
