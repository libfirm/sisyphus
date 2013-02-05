def config_leon(argparser, namespace, values, option_string):
    namespace.arch_dirs    = ["sparccode"]
    namespace.arch_cflags  = "-mtarget=sparc-leon-linux-gnu -msoft-float"
    namespace.arch_ldflags = "-static -msoft-float"
    namespace.runexe       = "qemu-sparc -r 2.6.40 "
    namespace.expect_url   = "http://pp.info.uni-karlsruhe.de/git/firm-testresults/plain/fail_expectations-sparc-leon-linux-gnu"

configurations = {
    'leon': config_leon
}
