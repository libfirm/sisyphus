from functools import partial
import difflib
import logging
import os


def check_retcode_zero(result):
    """Check that the return code of the step command is zero"""
    if result.retcode != 0:
        result.error = "returncode not zero but %s" % result.retcode


def check_retcode_nonzero(result):
    """Check that the return code of the step command is not zero"""
    if result.retcode == 0:
        result.error = "returncode zero"


def _help_check_reference_output(result, reference):
    """Compare stdout with a given reference output"""
    output = result.stdout
    if output == reference:
        return

    result.error = "output mismatch"
    # Try to create a diff
    try:
        ref_decoded = reference.decode("utf-8").splitlines()
        out_decoded = output.decode("utf-8").splitlines()
        result.diff = "\n".join(difflib.unified_diff(out_decoded, ref_decoded))
    except:
        # We might end up here when utf-8 decoding failed
        result.diff = "unable to compare output/reference (non utf-8 encoding?)"


def _help_check_always_fail(result, error):
    result.error = error


def create_check_reference_output(ref_file):
    """Read ref_file and return a checker which compares stdout with it."""
    # check for the common case of missing reference output and produce an
    # understandable message
    if not os.path.isfile(ref_file):
        logging.error("reference output '%s' missing" % (ref_file,))
        return partial(_help_check_always_fail, error="reference output missing")
    else:
        reference = open(ref_file, "rb").read()
        return partial(_help_check_reference_output, reference=reference)
