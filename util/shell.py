"""
Convenience function
Alternative to subprocess and os.system
"""
import subprocess
import resource
import sys
import signal
import threading

_EXIT_CODES = dict((-k, v) for v, k in signal.__dict__.items() if v.startswith('SIG'))
del _EXIT_CODES[0]


class SigKill(Exception):
    def __init__(self, retcode, name):
        self.retcode = retcode
        self.name = name


def _lower_rlimit(res, limit):
    (soft, hard) = resource.getrlimit(res)
    if soft > limit or soft == resource.RLIM_INFINITY:
        soft = limit
    if hard > limit or hard == resource.RLIM_INFINITY:
        hard = limit
    resource.setrlimit(res, (soft, hard))


class _Execute(object):
    def __init__(self, cmd, timeout, env):
        self.cmd = cmd
        self.process = None
        self.timeout = timeout
        self.env     = env

    def _set_rlimit(self):
        if self.timeout > 0.0:
            _lower_rlimit(resource.RLIMIT_CPU, self.timeout)
        MB = 1024 * 1024
        _lower_rlimit(resource.RLIMIT_CORE,  0)
        _lower_rlimit(resource.RLIMIT_DATA,  1024 * MB)
        _lower_rlimit(resource.RLIMIT_STACK, 1024 * MB)
        _lower_rlimit(resource.RLIMIT_FSIZE,   32 * MB)

    def _run_process(self):
        self.proc = subprocess.Popen(self.cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     preexec_fn=self._set_rlimit,
                                     env=self.env)
        self.out, self.err = self.proc.communicate()
        self.returncode = self.proc.returncode

    def run(self):
        if self.timeout > 0.0:
            thread = threading.Thread(target=self._run_process)
            thread.start()
            thread.join(float(self.timeout))
            if thread.is_alive():
                self.proc.terminate()
                thread.join(1.0)
                if thread.is_alive():
                    self.proc.kill()
                raise SigKill(signal.SIGXCPU, "SIGXCPU")
        else:
            self._run_process()

        # Usually python can recognize application terminations triggered by
        # signals, but somehow it doesn't do this for java (I suspect, that java
        # catches the signals itself but then shuts down more 'cleanly' than it
        # should. Calculate to python convention returncode
        if self.returncode > 127:
            self.returncode = 128 - self.returncode
        if self.returncode in _EXIT_CODES:
            raise SigKill(self.returncode, _EXIT_CODES[self.returncode])
        return (self.out, self.err, self.returncode)

def execute(cmd, env=None, timeout=0):
    """Execute a command and return stderr and stdout data"""

    cmd = filter(lambda x: x, cmd.split(' '))
    exc = _Execute(cmd, timeout, env)
    (out, err, returncode) = exc.run()
    return (out, err, returncode)


if __name__ == "__main__":
    out, err, retcode = execute("hostname")
    print (out)
