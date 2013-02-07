import os
from test.test   import Test, ensure_dir, test_factory
from test.steps  import execute, step_execute, create_step_append_flags
from test.checks import check_retcode_zero, check_missing_errors, check_no_errors, check_no_warnings, check_firm_problems, check_cparser_problems, create_check_reference_output, create_check_warnings_reference
from test.embedded_cmds import parse_embedded_commands
from functools import partial


def setup_c_environment(environment):
    environment.cflags  = "%s %s" % (environment.arch_cflags, environment.cflags)
    environment.ldflags = "%s %s" % (environment.arch_ldflags, environment.ldflags)


def step_compile_c(environment):
    """Compile c source code to executable"""
    setup_c_environment(environment)
    environment.executable = environment.builddir + "/" + environment.filename + ".exe"
    ensure_dir(os.path.dirname(environment.executable))
    cmd = "%(cc)s %(filename)s %(cflags)s %(ldflags)s -o %(executable)s" % environment.__dict__
    return execute(environment, cmd, timeout=60)


def step_compile_c_syntax_only(environment):
    setup_c_environment(environment)
    cmd = "%(cc)s %(filename)s %(cflags)s -fsyntax-only" % environment.__dict__
    return execute(environment, cmd, timeout=20)


def step_compile_c_asm(environment):
    """Compile c source code to assembler"""
    cmd = "%(cc)s %(filename)s %(cflags)s -S -o-" % environment.__dict__
    return execute(environment, cmd, timeout=60)


def make_c_test(filename, **kwargs):
    test = Test(filename)
    if addflags:
        test.add_step("flags", create_append_flags_step(**kwargs))
    test.add_step("compile", step_compile_c, checks=[
        check_cparser_problems,
        check_no_errors,
        check_firm_problems,
        check_retcode_zero,
    ])
    parse_embedded_commands(test, filename,
        lambda: test.add_step("asm", step_compile_c_asm)
    )
    test.add_step("execute", step_execute, checks=[
        check_retcode_zero,
        create_check_reference_output(filename + ".ref"),
    ])
    return test


@test_factory(lambda name: is_c_file(name) and "C/should_fail/" in name)
@test_factory(lambda name: is_c_file(name) and "C++/should_fail/" in name)
def make_c_should_fail(filename):
    test = Test(filename)
    test.add_step("compile", step_compile_c_syntax_only, checks=[
        check_missing_errors,
    ])
    parse_embedded_commands(test)
    return test


@test_factory(lambda name: is_c_file(name) and "C/should_warn/" in name)
def make_c_should_warn(filename):
    test = Test(environment, filename)
    test.add_step("flags", create_step_append_flags(
        cflags="-Wall -W",
    ))
    test.add_step("compile", step_compile_c_syntax_only, checks=[
        check_retcode_zero,
        check_no_errors,
        create_check_warnings_reference(filename + ".ref"),
    ])
    parse_embedded_commands(test)
    return test


@test_factory(lambda name: is_c_file(name) and "C/nowarn/" in name)
def make_c_should_not_warn(environment, filename):
    test = Test(environment, filename)
    test.add_step("flags", create_step_append_flags(
        cflags="-Wall -W",
    ))
    test.add_step("compile", step_compile_c_syntax_only, checks=[
        check_retcode_zero,
        check_no_errors,
        check_no_warnings,
    ])
    parse_embedded_commands(test)
    return test

@test_factory(lambda name: is_c_file(name) and "C/gnu99/" in name)
def make_gnu99_test(filename):
    return make_c_test(filename, cflags=" -std=gnu99")

@test_factory(lambda name: is_c_file(name) and "C/MS/" in name)
def make_MS_test(filename):
    return make_c_test(filename, cflags=" --ms")

@test_factory(lambda name: is_c_file(name) and "C/" in name)
def make_generic_test(filename):
    return make_c_test(filename, cflags=" -std=c99")

def is_c_file(name):
    return name.endswith(".c") or name.endswith(".cc")

def register_arguments(argparser):
    group = argparser.add_argument_group("C language")
    group.add_argument("--cc", dest="cc", metavar="CC",
                       help="Use CC to compile c programs")
    group.add_argument("--cflags", dest="cflags", metavar="CFLAGS",
                       help="Use CFLAGS to compile test programs")
    group.add_argument("--archcflags", dest="archcflags", metavar="ARCHCFLAGS",
                       help="Append ARCHCFLAGS to cflags")
    group.add_argument("--ldflags", dest="ldflags", metavar="LDFLAGS",
                       help="Use LDFLAGS to compile test programs")
    group.add_argument("--archldflags", dest="archldflags",
                       metavar="ARCHLDFLAGS",
                       help="Append ARCHLDFLAGS to LDFLAGS")
    argparser.set_defaults(
        cc="cparser",
        cflags="-O3",
        arch_cflags="-march=native -m32",
        ldflags="-lm",
        arch_ldflags="-m32"
    )
