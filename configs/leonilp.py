def config_leon_ilp(argparser, namespace, values, option_string):
    namespace.arch_dirs    = ["sparccode"]
    namespace.arch_cflags  = "-mtarget=sparc-leon-linux-gnu -bspiller=daemel -bra-chordal-co-algo=ilp"
    namespace.arch_ldflags = "-static"
    namespace.runexe       = "qemu-sparc -r 2.6.40 "
    namespace.expect_url   = "fail_expectations_sparc_leonilp"

configurations = {
    "leonilp": config_leon_ilp
}
