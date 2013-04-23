"""Checks for parsing compiler output for warnings/error messages and checking
their presence or absence."""
import difflib

def search_warnings_errors(result):
    """Parse step output for compiler warnings and errors and set
    result.warnings and result.errors list"""
    if hasattr(result, "warnings"):
        assert hasattr(result, "errors")
        return
    result.warnings = []
    result.errors   = []
    for line in result.stderr.splitlines():
        if ": warning: " in line:  # frontend warnings
            result.warnings.append(line)
        elif " error: " in line:  # frontend errors
            result.errors.append(line)


def check_no_errors(result):
    """Check that we had no compiler errors"""
    search_warnings_errors(result)
    n_errors = len(result.errors)
    if n_errors > 0:
        result.error = "%d compile errors" % n_errors


def check_missing_errors(result):
    """Check that we had at least 1 compiler error"""
    search_warnings_errors(result)
    n_errors = len(result.errors)
    if n_errors == 0:
        result.error = "missed error"


def check_missing_warnings(result):
    """Check that we had at least 1 compiler warning"""
    search_warnings_errors(result)
    n_warnings = len(result.warnings)
    if n_warnings == 0:
        result.error = "missed warnings"


def check_no_warnings(result):
    """Check that we had no compiler warnings"""
    search_warnings_errors(result)
    n_warnings = len(result.warnings)
    if n_warnings > 0:
        result.error = "produced invalid warning"


def _help_check_warnings_reference(result, reference):
    search_warnings_errors(result)
    n_warnings   = len(result.warnings)
    n_expected   = len(reference.splitlines())
    warning_text = "\n".join(result.warnings) + "\n"
    if n_warnings != n_expected:
        result.error = "reported %s warnings instead of %s" % (n_warnings, n_expected)
    elif warning_text != reference:
        result.error = "reported different warnings"


def create_check_warnings_reference(warnings_file):
    """Read warnings_file and compare it with the warnings the compiler
    actually reported. If the reference file is missing we just check that
    there are any warnings at all."""
    if not os.path.isfile(warnings_file):
        return check_missing_warnings
    else:
        reference = open(warnings_file, "rb").read()
        return partial(_help_check_warnings_reference, reference=reference)
