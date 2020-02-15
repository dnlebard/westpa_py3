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

from .core import WESTToolComponent
import re
import numpy
import westpa
from west.data_manager import seg_id_dtype

re_split_segspec = re.compile(r"\s*:\s*|\s+")


class SegmentSelection:
    def __init__(self, iterable=None):
        """Initialize this segment selection from an iterable of (n_iter,seg_id) pairs."""

        self._segments = set()
        self._segs_by_iter = {}
        self._start_iter = None
        self._stop_iter = None

        if iterable is not None:
            add = self.add
            for pair in iterable:
                add(tuple(pair))

    def __len__(self):
        return len(self._segments)

    def __contains__(self, pair):
        return tuple(pair) in self._segments

    def add(self, pair):

        (n_iter, seg_id) = int(pair[0]), int(pair[1])
        self._segments.add((n_iter, seg_id))
        self._segs_by_iter.setdefault(n_iter, set()).add(seg_id)
        if self._start_iter is None:
            self._start_iter = n_iter
        else:
            self._start_iter = min(self._start_iter, n_iter)
        if self._stop_iter is None:
            self._stop_iter = n_iter + 1
        else:
            self._stop_iter = max(self._stop_iter, n_iter + 1)

    def from_iter(self, n_iter):
        return self._segs_by_iter.get(n_iter, set())

    @property
    def start_iter(self):
        return self._start_iter

    @property
    def stop_iter(self):
        return self._stop_iter

    @classmethod
    def from_text(cls, filename):
        segsel = cls()

        segfile = open(filename, "rt")
        for line in segfile:
            wline = line.strip()
            if wline[0] == "#" or wline == "":
                continue

            fields = re_split_segspec.split(wline)
            if len(fields) != 2:
                raise ValueError("malformed segment selection {!r}".format(line))

            try:
                n_iter, seg_id = list(map(int, fields))
            except ValueError:
                raise ValueError("malformed segment selection {!r}".format(line))

            segsel.add((n_iter, seg_id))
        return segsel


class AllSegmentSelection(SegmentSelection):
    def __init__(self, start_iter=None, stop_iter=None, data_manager=None):
        self.data_manager = data_manager or westpa.rc.get_data_manager()
        self._start_iter = start_iter or 1
        self._stop_iter = stop_iter or self.data_manager.current_iteration
        self._segcount_by_iter = {}

    def _count_from_iter(self, n_iter):
        try:
            segcount = self._segcount_by_iter[n_iter]
        except KeyError:
            segcount = self.data_manager.get_iter_group(n_iter)["seg_index"].shape[0]
            self._segcount_by_iter[n_iter] = segcount
        return segcount

    def add(self, pair):
        raise TypeError("cannot add segments to an AllSegmentSelection")

    def from_iter(self, n_iter):
        return numpy.arange(0, self._count_from_iter(n_iter), dtype=seg_id_dtype)

    def __len__(self):
        segcount = 0
        count_from_iter = self._count_from_iter
        for n_iter in range(self._start_iter, self._stop_iter):
            segcount += count_from_iter(n_iter)
        return segcount

    def __contains__(self, pair):
        (n_iter, seg_id) = pair
        return (
            n_iter >= self._start_iter
            and n_iter < self._stop_iter
            and seg_id < self._count_from_iter(n_iter)
        )


class SegSelector(WESTToolComponent):
    def __init__(self):
        super(SegSelector, self).__init__()
        self.segment_selection = None
        self.segsel_filename = None

    def add_args(self, parser):
        group = parser.add_argument_group("WEST input data options")
        sgroup = group.add_mutually_exclusive_group()
        sgroup.add_argument(
            "--segments-from",
            metavar="SEGLIST_FILE",
            help="""Include only segments listed in SEGLIST_FILE, as generated by w_select
                            (default: include all segments.""",
        )

    def process_args(self, args):
        if args.segments_from:
            self.segsel_filename = args.segments_from
            self.segment_selection = self.parse_segsel_file(self.segsel_filename)
        else:
            self.segment_selection = AllSegmentSelection()

    def parse_segsel_file(self, filename):
        segsel = self.segment_selection = SegmentSelection()

        segfile = open(filename, "rt")
        for line in segfile:
            wline = line.strip()
            if wline[0] == "#" or wline == "":
                continue

            fields = re_split_segspec.split(wline)
            if len(fields) != 2:
                raise ValueError("malformed segment selection {!r}".format(line))

            try:
                n_iter, seg_id = list(map(int, fields))
            except ValueError:
                raise ValueError("malformed segment selection {!r}".format(line))

            segsel.add((n_iter, seg_id))
        return segsel
