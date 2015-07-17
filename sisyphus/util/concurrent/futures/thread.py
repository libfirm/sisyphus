# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

from __future__ import with_statement
import atexit
import threading
import weakref
import sys

import base

try:
    import queue
except ImportError:
    import Queue as queue

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

# Workers are created as daemon threads. This is done to allow the interpreter
# to exit when there are still idle threads in a ThreadPoolExecutor's thread
# pool (i.e. shutdown() was not called). However, allowing workers to die with
# the interpreter has two undesirable properties:
#   - The workers would still be running during interpretor shutdown,
#     meaning that they would fail in unpredictable ways.
#   - The workers could be killed while evaluating a work item, which could
#     be bad if the callable being evaluated has external side-effects e.g.
#     writing to a file.
#
# To work around this problem, an exit handler is installed which tells the
# workers to exit when their work queues are empty and then waits until the
# threads finish.

_thread_references = set()
_shutdown = False

def _remove_dead_thread_references():
    """Remove inactive threads from _thread_references.

    Should be called periodically to prevent memory leaks in scenarios such as:
    >>> while True:
    ...    t = ThreadPoolExecutor(max_workers=5)
    ...    t.map(int, ['1', '2', '3', '4', '5'])
    """
    for thread_reference in set(_thread_references):
        if thread_reference() is None:
            _thread_references.discard(thread_reference)

class _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        id = "%s(%s,%s)" % (self.fn, self.args, self.kwargs)
        base.LOGGER.debug('run WorkItem: '+id)
        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException:
            e = sys.exc_info()[1]
            self.future.set_exception(e)
            base.LOGGER.debug('WorkItem(%s) finished with exception: %s' % (id, e))
        else:
            self.future.set_result(result)
            base.LOGGER.debug('WorkItem(%s) finished with result: %s' % (id, result))

def _worker(executor_reference, work_queue):
    try:
        while True:
            try:
                work_item = work_queue.get(block=True, timeout=0.1)
            except queue.Empty:
                executor = executor_reference()
                # Exit if:
                #   - The interpreter is shutting down OR
                #   - The executor that owns the worker has been collected OR
                #   - The executor that owns the worker has been shutdown.
                if _shutdown or executor is None or executor._shutdown:
                    return
                del executor
            else:
                work_item.run()
    except BaseException:
        base.LOGGER.critical('Exception in worker', exc_info=True)

class ThreadPoolExecutor(base.Executor):
    def __init__(self, max_workers):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
        """
        _remove_dead_thread_references()

        self._max_workers = max_workers
        self._work_queue = queue.Queue()
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = threading.Lock()
        base.LOGGER.debug('ThreadPoolExecutor with %d workers max' % max_workers)

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                msg = 'cannot schedule new futures after shutdown'
                base.LOGGER.error(msg)
                raise RuntimeError(msg)

            f = base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(w)
            self._adjust_thread_count()
            return f
    submit.__doc__ = base.Executor.submit.__doc__

    def _adjust_thread_count(self):
        # TODO(bquinlan): Should avoid creating new threads if there are more
        # idle threads than items in the work queue.
        if len(self._threads) < self._max_workers:
            t = threading.Thread(target=_worker,
                                 args=(weakref.ref(self), self._work_queue))
            t.daemon = True
            t.start()
            self._threads.add(t)
            _thread_references.add(weakref.ref(t))
            base.LOGGER.info('ThreadPoolExecutor spawned a new thread, now at %d' % len(self._threads))

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
        if wait:
            base.LOGGER.debug('ThreadPoolExecutor shutting down, waiting for threads')
            for t in self._threads:
                t.join()
        base.LOGGER.info('ThreadPoolExecutor shut down')
    shutdown.__doc__ = base.Executor.shutdown.__doc__
