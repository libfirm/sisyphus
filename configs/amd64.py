def config_amd64(argparser, namespace, values, option_string):
    namespace.arch_dirs    = []
    namespace.arch_cflags  = "-m64 -bisa=amd64"
    namespace.arch_ldflags = ""
    namespace.expect_url   = "fail_expectations_amd64"

configurations = {
    'amd64': config_amd64
}
