import os
from sisyphus import test.suite
from sisyphus.test.steps  import execute, step_name

@step_name("compile")
def step_compile_d(environment):
	"""Compile file with DC without linking"""
	cmd = "%(dc)s -c %(filename)s %(dflags)s -of%(executable)s" % environment
	return execute(environment, cmd, timeout=240)

@step_name("compile")
def step_compile_and_link_d(environment):
	"""Compile file with DC to executable"""
	cmd = "%(dc)s %(filename)s %(dflags)s -of%(executable)s" % environment
	return execute(environment, cmd, timeout=240)

def setup_arguments(argparser, default_env):
	group = argparser.add_argument_group("D language")
	group.add_argument("--dc", dest="dc",
	                help="Use DC to compile D programs", metavar="DC")
	group.add_argument("--dflags", dest="dflags",
	                help="Use flags to compile D programs")
	default_env.set(
	    dc="dmd",
	    dflags="",
        )
test.suite.add_argparser_setup(setup_arguments)
