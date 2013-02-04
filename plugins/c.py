import os
from test.test   import Test, ensure_dir, test_factory
from test.steps  import execute, step_execute
from test.checks import check_retcode_zero, check_missing_errors, check_no_errors, check_no_warnings, check_firm_problems, check_cparser_problems, create_check_reference_output, create_check_warnings_reference
from test.embedded_cmds import parse_embedded_commands
from functools import partial

def step_compile_c(environment):
    """Compile c source code to executable"""
    cmd = "%(cc)s %(filename)s %(cflags)s %(ldflags)s -o %(executable)s" % environment.__dict__
    return execute(environment, cmd, timeout=60)

def step_compile_c_syntax_only(environment):
    cmd = "%(cc)s %(filename)s %(cflags)s -fsyntax-only" % environment.__dict__
    return execute(environment, cmd, timeout=20)

def step_compile_c_asm(environment):
    """Compile c source code to assembler"""
    cmd = "%(cc)s %(filename)s %(cflags)s -S -o %(asmfile)s" % environment.__dict__
    result = execute(environment, cmd, timeout=60)
    if result.fail():
        return result

    try:
        result.asm = open(environment.asmfile, "rb").read()
    except:
        result.error = "couldn't read assembler output"
    return result

def setup_c_environment(environment, filename):
    environment.filename = filename
    environment.cflags  += " %s" % environment.arch_cflags
    environment.cflags  += " -I%s " % os.path.dirname(environment.filename)
    environment.ldflags += " %s" % environment.arch_ldflags

def make_c_test(environment, filename):
    setup_c_environment(environment, filename)
    environment.executable = environment.builddir + "/" + environment.filename + ".exe"
    ensure_dir(os.path.dirname(environment.executable))

    test = Test(environment, filename)
    test.add_step("compile", step_compile_c, checks=[
        check_cparser_problems,
        check_no_errors,
        check_firm_problems,
        check_retcode_zero,
    ])

    asmchecks = parse_embedded_commands(environment, environment.filename)
    if asmchecks:
        environment.asmfile = environment.builddir + "/" + environment.filename + ".s"
        ensure_dir(os.path.dirname(environment.asmfile))
        test.add_step("asm", step_compile_c_asm, checks=asmchecks)

    test.add_step("execute", step_execute, checks=[
        check_retcode_zero,
        create_check_reference_output(environment),
    ])
    return test

@test_factory(lambda name: is_c_file(name) and "C/should_fail/" in name)
@test_factory(lambda name: is_c_file(name) and "C++/should_fail/" in name)
def make_c_should_fail(environment, filename):
    setup_c_environment(environment, filename)
    parse_embedded_commands_no_check(environment)

    test = Test(environment, filename)
    test.add_step("compile", step_compile_c_syntax_only, checks=[
        check_missing_errors,
    ])
    return test

def parse_embedded_commands_no_check(environment):
    checks = parse_embedded_commands(environment, environment.filename)
    if checks:
        raise Exception("embedded checks not allowed")

@test_factory(lambda name: is_c_file(name) and "C/should_warn/" in name)
def make_c_should_warn(environment, filename):
    setup_c_environment(environment, filename)
    environment.cflags += " -Wall -W"
    parse_embedded_commands_no_check(environment)

    test = Test(environment, filename)
    test.add_step("compile", step_compile_c_syntax_only, checks=[
        check_retcode_zero,
        check_no_errors,
        create_check_warnings_reference(environment),
    ])
    return test

@test_factory(lambda name: is_c_file(name) and "C/nowarn/" in name)
def make_c_should_not_warn(environment, filename):
    setup_c_environment(environment, filename)
    environment.cflags += " -Wall -W"
    parse_embedded_commands_no_check(environment)

    test = Test(environment, filename)
    test.add_step("compile", step_compile_c_syntax_only, checks=[
        check_retcode_zero,
        check_no_errors,
        check_no_warnings,
    ])
    return test

@test_factory(lambda name: is_c_file(name) and "C/gnu99/" in name)
def make_gnu99_test(environment, filename):
    environment.cflags += " -std=gnu99"
    return make_c_test(environment, filename)

@test_factory(lambda name: is_c_file(name) and "C/MS/" in name)
def make_MS_test(environment, filename):
    environment.cflags += " --ms"
    return make_c_test(environment, filename)

@test_factory(lambda name: is_c_file(name) and "C/" in name)
def make_generic_test(environment, filename):
    environment.cflags += " -std=c99"
    return make_c_test(environment, filename)

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
