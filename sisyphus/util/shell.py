"""
Convenience function
Alternative to subprocess and os.system
"""
import subprocess
import resource
import sys
import signal
import threading

import logging
_LOG = logging.getLogger("sisyphus")

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
    def __init__(self, cmd, timeout, env, rlimit):
        self.cmd       = cmd
        self.timeout   = timeout
        self.env       = env
        self.proc      = None
        self.exception = None
        self.rlimit    = rlimit
        MB = 1024 * 1024
        if not 'RLIMIT_CORE' in rlimit:
            rlimit['RLIMIT_CORE'] = 0
        if not 'RLIMIT_DATA' in rlimit:
            rlimit['RLIMIT_DATA'] = 1024 * MB
        if not 'RLIMIT_STACK' in rlimit:
            rlimit['RLIMIT_STACK'] = 1024 * MB
        if not 'RLIMIT_FSIZE' in rlimit:
            rlimit['RLIMIT_FSIZE'] = 32 * MB

    def _set_rlimit(self):
        if self.timeout > 0.0:
            _lower_rlimit(resource.RLIMIT_CPU, self.timeout)
        for k,v in self.rlimit.items():
            _lower_rlimit(getattr(resource,k), v)

    def _run_process(self):
        try:
            self.proc = subprocess.Popen(self.cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         preexec_fn=self._set_rlimit,
                                         env=self.env)
            x = self.proc.communicate()
            self.out, self.err = x
            self.returncode = self.proc.returncode
        except Exception as e:
            self.exception = e

    def run(self):
        if self.timeout > 0.0:
            _LOG.debug("run with timeout %.1f" % float(self.timeout))
            thread = threading.Thread(target=self._run_process)
            thread.start()
            thread.join(float(self.timeout))
            if self.exception is not None:
                raise self.exception
            if thread.is_alive():
                _LOG.debug("timeout %.1f reached, terminate process" % self.timeout)
                if self.proc is not None:
                    self.proc.terminate()
                    thread.join(1.0)
                    if thread.is_alive():
                        _LOG.debug("termination ignored, now kill process")
                        self.proc.kill()
                        thread.join()
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
            _LOG.debug("returncode %d recognized as '%s'" % (self.returncode, _EXIT_CODES[self.returncode]))
            raise SigKill(self.returncode, _EXIT_CODES[self.returncode])
        return (self.out, self.err, self.returncode)

def execute(cmd, env=None, timeout=0, rlimit=None):
    """Execute a command and return stderr and stdout data"""
    if not rlimit:
        rlimit = dict()
    cmd = filter(lambda x: x, cmd.split(' '))
    exc = _Execute(cmd, timeout, env, rlimit)
    (out, err, returncode) = exc.run()
    return (out, err, returncode)


if __name__ == "__main__":
    out, err, retcode = execute("hostname")
    print (out)
