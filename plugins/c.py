import os
from test.test   import ensure_dir
from test.steps  import execute
from functools import partial


def setup_c_environment(environment):
    environment.cppflags = "%(arch_cppflags)s %(cppflags)s" % environment
    environment.cflags   = "%(arch_cflags)s %(cflags)s" % environment
    environment.cxxflags = "%(arch_cxxflags)s %(cxxflags)s" % environment
    environment.ldflags  = "%(arch_ldflags)s %(ldflags)s" % environment


def step_compile_c(environment):
    """Compile C source code to executable"""
    setup_c_environment(environment)
    environment.executable = "%(builddir)s/%(testname)s.exe" % environment
    ensure_dir(os.path.dirname(environment.executable))
    cmd = "%(cc)s %(cppflags)s %(cflags)s %(ldflags)s -o %(executable)s %(filename)s" % environment
    return execute(environment, cmd, timeout=60)


def step_compile_cxx(environment):
    """Compile C++ source code to executable"""
    setup_c_environment(environment)
    environment.executable = "%(builddir)s/%(testname)s.exe" % environment
    ensure_dir(os.path.dirname(environment.executable))
    cmd = "%(cxx)s %(cppflags)s %(cxxflags)s %(ldflags)s -o %(executable)s %(filename)s" % environment
    return execute(environment, cmd, timeout=60)


def register_arguments(argparser):
    group = argparser.add_argument_group("C language")
    group.add_argument("--cc", dest="cc", metavar="CC",
                       help="Use CC to compile C programs")
    group.add_argument("--cxx", dest="cxx", metavar="CXX",
                       help="Use CXX to compile C++ programs")
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
