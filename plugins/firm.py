def check_firm_problems(result):
    """Check output of step command for problematic messages from libFirm
    library"""
    for line in result.stderr.splitlines():
        if line.startswith("Verify warning:"):  # libfirm verifier warnings
            result.error = "verify warning"
            break
        elif "libFirm panic" in line:
            result.errors_msg = "libFirm panic"
            break
