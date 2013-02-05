def config_sparc(argparser, namespace, values, option_string):
    namespace.arch_dirs    = ["sparccode"]
    namespace.arch_cflags  = "-mtarget=sparc-linux-gnu"
    namespace.arch_ldflags = "-static"
    namespace.runexe       = "qemu-sparc32plus "
    namespace.expect_url   = "fail_expectations_sparc"

configurations = {
    'sparc': config_sparc
}
