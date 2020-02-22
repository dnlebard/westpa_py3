#!/usr/bin/env python
# Copyright (C) 2013 Matthew C. Zwier and Lillian T. Chong
#
# This file is part of WESTPA.
#
# WESTPA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WESTPA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WESTPA.  If not, see <http://www.gnu.org/licenses/>.

import sys
import logging
import argparse
import traceback

from westpa import rc
from westpa import work_managers
from westpa.work_managers import make_work_manager

log = logging.getLogger("w_run")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("w_run", "start/continue a WEST simulation")
    rc.add_args(parser)
    parser.add_argument(
        "--oneseg",
        dest="only_one_segment",
        action="store_true",
        help="only propagate one segment (useful for debugging propagators)",
    )

    work_managers.environment.add_wm_args(parser)

    args = parser.parse_args()
    rc.process_args(args)
    work_managers.environment.process_wm_args(args)
    work_manager = rc.work_manager = make_work_manager()

    # Load the sim manager and other drivers
    sim_manager = rc.get_sim_manager()
    system = rc.get_system_driver()
    data_manager = rc.get_data_manager()
    we_driver = rc.get_we_driver()
    propagator = rc.get_propagator()

    propagator.system = system
    data_manager.system = system
    we_driver.system = system

    sim_manager.data_manager = data_manager
    sim_manager.system = system
    sim_manager.propagator = propagator
    sim_manager.we_driver = we_driver

    with work_manager:
        if work_manager.is_master:
            work_manager.install_sigint_handler()
            sim_manager.load_plugins()

            log.debug("preparing run")
            sim_manager.prepare_run()

            try:
                log.debug("beginning run")
                sim_manager.run()

                log.debug("finalizing run")
                sim_manager.finalize_run()
            except KeyboardInterrupt:
                rc.pstatus("interrupted; shutting down")
                sys.exit(1)
            except Exception:
                rc.pstatus("exception caught; shutting down")
                log.error(traceback.format_exc())
                sys.exit(1)
        else:
            work_manager.run()
