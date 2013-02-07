# A module to parse commands embedded into the tests themselfes
from functools import partial
from steps     import create_step_append_flags
import logging
import re
import sys


def _check_regex(result, regex, txt, count, expected_result):
    realcount = 0
    for line in result.stdout.splitlines():
        if regex.search(line):
            realcount += 1
            if realcount > count:
                break
    if not expected_result and realcount > 0:
        result.error = "!check '%s' failed" % (txt,)
    elif expected_result and count == 0 and realcount == 0:
        result.error = "check '%s' failed" % (txt,)
    elif count > 0 and realcount != count:
        assert expected_result
        result.error = "check[%s] '%s' failed" % (count, txt,)


def _embedded_add_check(regex_string, count_arg, flag):
    """create a regex check (for assembler output)"""
    c = 0
    if count_arg:
        if flag:
            c = int(count_arg[1:-1])
        else:
            raise Exception("!check cannot be used with an argument")
    regex = re.compile(regex_string)
    return partial(_check_regex, regex=regex, txt=regex_string, count=c, expected_result=flag)


def _parse_embedded_command(cmd, flags, asm_checks):
    """parse one /*$ $*/ embedded command"""
    cmdre = re.compile("(!?check(\[[0-9]+\])?|cflags|ldflags)(.*)")
    m = cmdre.match(cmd)
    if m:
        base = m.group(1)
        if m.group(2):
            base = base[0:-len(m.group(2))]
        if m.group(3):
            arg = m.group(3).strip()

        if base == "check":
            check = _embedded_add_check(arg, m.group(2), True)
            asm_checks.append(check)
        elif base == "!check":
            check = _embedded_add_check(arg, m.group(2), False)
            asm_checks.append(check)
        elif base == "cflags":
            flags["cflags"] += " %s" % (arg,)
        elif base == "ldflags":
            flags["ldflags"] += " %s" % (arg,)
        else:
            logging.error("unsupported embedded command %s" % base)
    else:
        # treat as a cflag option
        flags["cflags"] += " %s" % (cmd.strip(), )


def parse_embedded_commands(test, filename, asm_step_factory=None):
    """Parse a given file for embedded test commands (/*$ ... $*/ sequences).
    Modifies the test and adds an additional assembly generation step with the
    asm_step callback if necessary."""
    cmd_regex  = re.compile("/\\*\\$ (.+) \\$\\*/")
    asm_checks = []
    flags      = dict(cflags="", ldflags="")
    for line in open(filename, "rb"):
        m = cmd_regex.match(line)
        if m:
            cmd = m.group(1)
            logging.info("%s: embedded cmd %s\n" % (filename, cmd))
            _parse_embedded_command(cmd, flags, asm_checks)
    if len(asm_checks) > 0:
        step = asm_step_factory()
        step.add_checks(asm_checks)
    if flags["cflags"] != "":
        test.prepend_step("embedded_cflags", create_step_append_flags(cflags=flags["cflags"]))
    if flags["ldflags"] != "":
        test.prepend_step("embedded_ldflags", create_step_append_flags(ldflags=flags["ldflags"]))
