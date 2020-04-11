"""A system for parallel, remote execution of multiple arbitrary tasks.
Much of this, both in concept and execution, was inspired by (and in some 
cases based heavily on) the ``concurrent.futures`` package from Python 3.2,
with some simplifications and adaptations (thanks to Brian Quinlan and his
futures implementation).
"""

import logging

from westpa.work_managers.core import WorkManager, WMFuture, FutureWatcher


# Import core work managers, which should run most everywhere that
# Python does
from westpa.work_managers import serial, threads, processes  # noqa
from westpa.work_managers.serial import SerialWorkManager
from westpa.work_managers.threads import ThreadsWorkManager
from westpa.work_managers.processes import ProcessWorkManager

log = logging.getLogger(__name__)

_available_work_managers = {
    "serial": SerialWorkManager,
    "threads": ThreadsWorkManager,
    "processes": ProcessWorkManager,
}

# Import ZeroMQ work manager if available
try:
    from westpa.work_managers import zeromq
    from westpa.work_managers.zeromq import ZMQWorkManager
except ImportError:
    log.info("ZeroMQ work manager not available")
    log.debug("traceback follows", exc_info=True)
else:
    _available_work_managers["zmq"] = ZMQWorkManager

# Import MPI work manager if available
try:
    from westpa.work_managers import mpi
    from westpa.work_managers.mpi import MPIWorkManager
except ImportError:
    log.info("MPI work manager not available")
    log.debug("traceback follows", exc_info=True)
else:
    _available_work_managers["mpi"] = MPIWorkManager

from westpa.work_managers import environment
from westpa.work_managers.environment import make_work_manager
