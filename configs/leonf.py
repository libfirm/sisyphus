def config_leonf(argparser, namespace, values, option_string):
    namespace.arch_dirs    = ["sparccode"]
    namespace.arch_cflags  = "-mtarget=sparc-leon-linux-gnu -bspiller=daemel -bregalloc=pref"
    namespace.arch_ldflags = "-static"
    namespace.runexe       = "qemu-sparc -r 2.6.40 "
    namespace.expect_url   = "fail_expectations_sparc_leonf"

configurations = {
    "leonf": config_leonf
}
