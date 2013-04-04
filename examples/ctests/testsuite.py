from glob             import glob
from plugins.c        import step_compile_c
from plugins.compiler import check_no_warnings
from test.checks      import check_retcode_zero, create_check_reference_output
from test.steps       import step_execute
from test.test        import Test
import os
import test

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
