def check_cparser_problems(result):
    """Check output of step command for problematic cparser compiler output"""
    for line in result.stderr.splitlines():
        if "linker reported an error" in line:
            result.error = "linker error"
            break
        elif "assembler reported an error" in line:
            result.error = "assembler error"
            break
