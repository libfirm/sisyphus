def config_arm(argparser, namespace, values, option_string):
    namespace.arch_dirs    = ["armcode"]
    namespace.arch_cflags  = "-mtarget=arm-linux-gnueabihf"
    namespace.arch_ldflags = "-static"
    namespace.runexe       = "qemu-arm "
    namespace.expect_url   = "http://pp.info.uni-karlsruhe.de/git/firm-testresults/plain/fail_expectations-arm-linux-gnueabihf"

configurations = {
    'arm': config_arm
}
