import os
from test.test   import ensure_dir
from test.steps  import execute
from functools import partial


def setup_c_environment(environment):
    environment.cflags  = "%s %s" % (environment.arch_cflags, environment.cflags)
    environment.ldflags = "%s %s" % (environment.arch_ldflags, environment.ldflags)


def step_compile_c(environment):
    """Compile c source code to executable"""
    setup_c_environment(environment)
    environment.executable = environment.builddir + "/" + environment.filename + ".exe"
    ensure_dir(os.path.dirname(environment.executable))
    cmd = "%(cc)s %(cflags)s %(ldflags)s -o %(executable)s %(filename)s" % environment
    return execute(environment, cmd, timeout=60)


def step_compile_c_syntax_only(environment):
    setup_c_environment(environment)
    cmd = "%(cc)s %(cflags)s -fsyntax-only %(filename)s" % environment
    return execute(environment, cmd, timeout=20)


def step_compile_c_asm(environment):
    """Compile c source code to assembler"""
    cmd = "%(cc)s %(cflags)s -S -o- %(filename)s" % environment
    return execute(environment, cmd, timeout=60)


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
