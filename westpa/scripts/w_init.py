#!/usr/bin/env python
import sys
import logging
import numpy
import argparse
import io

from westpa import work_managers
from westpa.work_managers import make_work_manager

import westpa
from westpa.states import TargetState

log = logging.getLogger("w_init")

log = logging.getLogger("w_init")
EPS = numpy.finfo(numpy.float64).eps

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        "w_init",
        description="""\
    Initialize a new WEST simulation, creating the WEST HDF5 file and preparing the first
    iteration's segments.

    Initial states are generated from one or more "basis states" which are specified either in a file specified with --bstates-from, or
    by one or more "--bstate" arguments. If neither --bstates-from nor at least one "--bstate" argument is provided, then a default
    basis state of probability one identified by the state ID zero and label "basis" will be created (a warning will be printed in this
    case, to remind you of this behavior, in case it is not what you wanted).

    Target states for (non-equilibrium) steady-state simulations are specified either in a file specified with --tstates-from, or
    by one or more --tstate arguments. If neither --tstates-from nor at least one --tstate argument is provided, then an equilibrium
    simulation (without any sinks) will be performed. 
    """,
    )
    westpa.rc.add_args(parser)
    parser.add_argument(
        "--force",
        dest="force",
        action="store_true",
        help="Overwrite any existing simulation data",
    )
    parser.add_argument(
        "--bstate-file",
        "--bstates-from",
        metavar="BSTATE_FILE",
        help="Read basis state names, probabilities, and (optionally) data references from BSTATE_FILE.",
    )
    parser.add_argument(
        "--bstate",
        action="append",
        dest="bstates",
        help="""Add the given basis state (specified as a string 'label,probability[,auxref]')
                        to the list of basis states (after those specified in --bstates-from, if any). This argument
                        may be specified more than once, in which case the given states are appended in the order
                        they are given on the command line.""",
    )
    parser.add_argument(
        "--tstate-file",
        "--tstates-from",
        metavar="TSTATE_FILE",
        help="Read target state names and representative progress coordinates from TSTATE_FILE",
    )
    parser.add_argument(
        "--tstate",
        action="append",
        dest="tstates",
        help="""Add the given target state (specified as a string 'label,pcoord0[,pcoord1[,...]]') to the
                        list of target states (after those specified in the file given by --tstates-from, if any).
                        This argument may be specified more than once, in which case the given states are appended
                        in the order they appear on the command line.""",
    )
    parser.add_argument(
        "--segs-per-state",
        type=int,
        metavar="N",
        default=1,
        help="""Initialize N segments from each basis state (default: %(default)s).""",
    )
    parser.add_argument(
        "--no-we",
        "--shotgun",
        dest="shotgun",
        action="store_true",
        help="""Do not run the weighted ensemble bin/split/merge algorithm on newly-created segments.""",
    )

    work_managers.environment.add_wm_args(parser)
    args = parser.parse_args()
    westpa.rc.process_args(args)
    work_managers.environment.process_wm_args(args)
    westpa.rc.work_manager = work_manager = make_work_manager()

    system = westpa.rc.get_system_driver()
    sim_manager = westpa.rc.get_sim_manager()
    propagator = westpa.rc.get_propagator()
    data_manager = westpa.rc.get_data_manager()
    h5file = data_manager.we_h5filename

    data_manager.system = system
    we_driver = westpa.rc.get_we_driver()
    basis_states = args.bstates

    with work_manager:
        if work_manager.is_master:
            # Process target states
            target_states = []
            if args.tstate_file:
                target_states.extend(
                    TargetState.states_from_file(args.tstate_file, system.pcoord_dtype)
                )
            if args.tstates:
                tstates_strio = io.StringIO("\n".join(args.tstates).replace(",", " "))
                target_states.extend(
                    TargetState.states_from_file(tstates_strio, system.pcoord_dtype)
                )

            if not args.basis_states:
                log.error("At least one basis state is required")
                sys.exit(3)

            # Check that the total probability of basis states adds to one
            tprob = sum(bstate.probability for bstate in basis_states)
            if abs(1.0 - tprob) > len(basis_states) * EPS:
                pscale = 1 / tprob
                log.warning(
                    "Basis state probabilities do not add to unity; rescaling by {:g}".format(
                        pscale
                    )
                )
                for bstate in args.basis_states:
                    bstate.probability *= pscale

            # Prepare simulation
            sim_manager.initialize_simulation(
                basis_states,
                target_states,
                segs_per_state=args.segs_per_state,
                suppress_we=args.shotgun,
            )
        else:
            work_manager.run()
