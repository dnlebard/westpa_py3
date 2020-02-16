"""WEST Analyis framework -- an unholy mess of classes exploiting each other"""


class ArgumentError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisMixin:
    def __init__(self):
        super().__init__()

    def add_args(self, parser, upcall=True):
        if upcall:
            try:
                upfunc = super(AnalysisMixin, self).add_args
            except AttributeError:
                pass
            else:
                upfunc(parser)

    def process_args(self, args, upcall=True):
        if upcall:
            try:
                upfunc = super(AnalysisMixin, self).process_args
            except AttributeError:
                pass
            else:
                upfunc(args)


# These imports have to be here, because its a 'unholy mess'
from westpa.oldtools.aframe import atool
from westpa.oldtools.aframe.atool import WESTAnalysisTool
from westpa.oldtools.aframe.iter_range import IterRangeMixin
from westpa.oldtools.aframe.data_reader import (
    WESTDataReaderMixin,
    ExtDataReaderMixin,
    BFDataManager,
)
from westpa.oldtools.aframe.binning import BinningMixin
from westpa.oldtools.aframe.mcbs import MCBSMixin
from westpa.oldtools.aframe.trajwalker import TrajWalker
from westpa.oldtools.aframe.output import CommonOutputMixin
from westpa.oldtools.aframe.plotting import PlottingMixin
from westpa.oldtools.aframe.transitions import (
    TransitionAnalysisMixin,
    TransitionEventAccumulator,
    BFTransitionAnalysisMixin,
)
from westpa.oldtools.aframe.kinetics import KineticsAnalysisMixin
