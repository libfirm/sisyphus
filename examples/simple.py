from sisyphus import test
from glob import glob
from sisyphus.test.test import Test
from sisyphus.test.checks import check_retcode_zero, create_check_reference_output
from sisyphus.test.steps import execute

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
    ], allow_retries=3)
    return test

# Create testlist
tests = []
for filename in [ "tests/test1.sh", "tests/test2.sh", "tests/fail.sh", "tests/mismatch.sh", "tests/flailing.sh" ]:
    t = make_shell_test(filename)
    tests.append(t)

test.suite.make("shell", tests=tests)
