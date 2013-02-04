from test.test   import Test, ensure_dir
from test.steps  import execute
from test.checks import check_retcode_zero, create_check_reference_output

def step_optitest(environment):
    cmd = "./test_optimization.py %(filename)s" % environment.__dict__
    return execute(cmd, environment, timeout=20)

def make_optitest(environment, filename):
    ensure_dir("build/optitest")
    environment.filename = filename

    test = Test(environment, filename)
    test.add_step("optitest", step_optitest, checks=[
        check_retcode_zero,
        create_check_reference_output(environment),
    ])
    return test

def config_optitest(argparser, namespace, values, option_string):
    namespace.default_dirs = [ "optitest" ]
    namespace.arch_dirs    = [ ]
    namespace.expect_url   = "fail_expectations_optitest"

configurations = {
    'optitest': config_optitest
}
