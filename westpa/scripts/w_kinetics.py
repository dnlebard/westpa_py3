#!/usr/bin/env python
import sys
from westpa.westtools import (
    WESTMasterCommand,
    WESTParallelTool,
)

from westpa.scripts.w_direct import DKinetics

# Just a shim to make sure everything works and is backwards compatible.


class WKinetics(DKinetics):
    subcommand = "trace"
    help_text = "averages and CIs for path-tracing kinetics analysis"
    default_output_file = "kintrace.h5"


class WDirect(WESTMasterCommand, WESTParallelTool):
    prog = "w_kinetics"
    subcommands = [WKinetics]
    subparsers_title = "calculate state-to-state kinetics by tracing trajectories"
    description = """\
Calculate state-to-state rates and transition event durations by tracing
trajectories.

A bin assignment file (usually "assign.h5") including trajectory labeling
is required (see "w_assign --help" for information on generating this file).

The output generated by this program is used as input for the ``w_kinavg``
tool, which converts the flux data in the output file into average rates
with confidence intervals. See ``w_kinavg trace --help`` for more
information.

-----------------------------------------------------------------------------
Output format
-----------------------------------------------------------------------------

The output file (-o/--output, by default "kintrace.h5") contains the
following datasets:

  ``/conditional_fluxes`` [iteration][state][state]
    *(Floating-point)* Macrostate-to-macrostate fluxes. These are **not**
    normalized by the population of the initial macrostate.

  ``/conditional_arrivals`` [iteration][stateA][stateB]
    *(Integer)* Number of trajectories arriving at state *stateB* in a given
    iteration, given that they departed from *stateA*.

  ``/total_fluxes`` [iteration][state]
    *(Floating-point)* Total flux into a given macrostate.

  ``/arrivals`` [iteration][state]
    *(Integer)* Number of trajectories arriving at a given state in a given
    iteration, regardless of where they originated.

  ``/duration_count`` [iteration]
    *(Integer)* The number of event durations recorded in each iteration.

  ``/durations`` [iteration][event duration]
    *(Structured -- see below)*  Event durations for transition events ending
    during a given iteration. These are stored as follows:

      istate
        *(Integer)* Initial state of transition event.
      fstate
        *(Integer)* Final state of transition event.
      duration
        *(Floating-point)* Duration of transition, in units of tau.
      weight
        *(Floating-point)* Weight of trajectory at end of transition, **not**
        normalized by initial state population.

Because state-to-state fluxes stored in this file are not normalized by
initial macrostate population, they cannot be used as rates without further
processing. The ``w_kinavg`` command is used to perform this normalization
while taking statistical fluctuation and correlation into account. See
``w_kinavg trace --help`` for more information.  Target fluxes (total flux
into a given state) require no such normalization.

-----------------------------------------------------------------------------
Command-line options
-----------------------------------------------------------------------------
"""


if __name__ == "__main__":
    print(
        "WARNING: {} is being deprecated.  Please use w_direct instead.".format(
            WDirect.prog
        )
    )

    try:
        if sys.argv[1] != "trace":
            sys.argv.insert(1, "trace")
    except Exception:
        sys.argv.insert(1, "trace")
    WDirect().main()
