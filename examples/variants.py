from sisyphus import test
import os
from glob import glob
from sisyphus.test.test import Test, Environment
from sisyphus.test.checks import check_retcode_zero, create_check_reference_output
from sisyphus.test.steps import execute

def step_run(environment):
    """Simple teststep which executes a shell script"""
    cmd = "%(shell)s %(testname)s" % environment
    return execute(environment, cmd, timeout=10)

def make_shell_test(name):
    """Constructs a shell test"""
    test = Test(name)
    test.add_step("run", step_run, checks=[
        check_retcode_zero,
        create_check_reference_output(name+".ref"),
    ])
    return test

# Register custom arguments
def setup_argparser(argparser, default_env):
    group = argparser.add_argument_group("Shell Tests")
    group.add_argument("--shell", dest="shell", metavar="SHELL",
                       help="Use SHELL to execute shell scripts")
    default_env.set(
        shell="/bin/sh",
    )
test.suite.add_argparser_setup(setup_argparser)

# Provide a default environment
bashenv = Environment(
    shell = "/bin/bash",
)
cshenv = Environment(
    shell = "/bin/csh",
)

# Create testlist
tests = []
for filename in glob(os.path.dirname(__file__) + "tests/*.sh"):
    tests.append(make_shell_test(filename))

# Create testsuite
test.suite.make("shelltests-bash", tests=tests, environment=bashenv, default=False)
test.suite.make("shelltests-csh", tests=tests, environment=cshenv, default=False)
