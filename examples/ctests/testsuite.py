from glob             import glob
from plugins.c        import step_compile_c
from plugins.compiler import check_no_warnings
from sisyphus.test.checks      import check_retcode_zero, create_check_reference_output
from sisyphus.test.steps       import step_execute
from sisyphus.test.test        import Test
import os
from sisyphus import test

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
