from plugins.c import step_compile_c
from test.test import Test
from test.steps import step_execute
from test.checks import check_retcode_zero, check_no_warnings, create_check_reference_output
from glob import glob
import test
import os

def make_c_test(name):
    test = Test(name)
    test.add_step("compile", step_compile_c, checks=[
        check_no_warnings,
        check_retcode_zero,
    ])
    test.add_step("run", step_execute, checks=[
        check_retcode_zero,
        create_check_reference_output(name+".ref"),
    ])
    return test

testfiles = glob(os.path.join(os.path.dirname(__file__), "*.c"))
tests = map(make_c_test, testfiles)
test.suite.make("c", tests=tests)
