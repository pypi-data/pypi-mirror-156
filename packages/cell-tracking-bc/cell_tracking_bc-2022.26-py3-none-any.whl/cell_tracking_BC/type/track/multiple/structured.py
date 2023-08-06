# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from __future__ import annotations

import dataclasses as dtcl
from operator import attrgetter as GetAttribute
from operator import itemgetter as ItemAt
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import json_any.json_any as jsnr

import cell_tracking_BC.standard.issue as isse
from cell_tracking_BC.standard.uid import Identity
from cell_tracking_BC.type.cell.cell import cell_t
from cell_tracking_BC.type.track.single.universal import any_track_h, structured_track_h
from cell_tracking_BC.type.track.single.forking import forking_track_t
from cell_tracking_BC.type.track.single.thread import thread_track_t
from cell_tracking_BC.type.track.single.structured import (
    cells_w_optional_time_points_h,
    feature_filtering_h,
    per_thread_cell_h,
    per_thread_cells_h,
    per_thread_feature_h,
)
from cell_tracking_BC.type.track.single.unstructured import unstructured_track_t
from cell_tracking_BC.type.track.multiple.unstructured import unstructured_tracks_t


TrackIssues_h = Callable[
    [structured_track_h, dict], Optional[Union[str, Sequence[str]]]
]


@dtcl.dataclass(repr=False, eq=False)
class tracks_t(List[structured_track_h]):

    invalids: List[Tuple[any_track_h, Sequence[str]]] = dtcl.field(
        init=False, default_factory=list
    )
    fully_pruned: List[structured_track_h] = dtcl.field(
        init=False, default_factory=list
    )

    NewFromJsonString: ClassVar[Callable[[str], tracks_t]] = jsnr.ObjectFromJsonString

    @classmethod
    def NewFromUnstructuredTracks(cls, tracks: unstructured_tracks_t, /) -> tracks_t:
        """"""
        instance = cls()

        next_thread_label = 1
        for unstructured in tracks.track_iterator:
            issues = unstructured.Issues()
            if issues is None:
                (
                    forking_track,
                    next_thread_label,
                ) = forking_track_t.NewFromUnstructuredTrack(
                    unstructured, next_thread_label
                )

                if forking_track.leaves.__len__() > 1:
                    instance.append(forking_track)
                else:
                    thread_track = forking_track.AsThreadTrack()
                    instance.append(thread_track)
            else:
                instance.invalids.append((unstructured, issues))

        return instance

    @classmethod
    def __NewFromJsonDescription__(
        cls,
        description,
        /,
    ) -> tracks_t:
        """"""
        tracks, attributes = description

        instance = cls.__new__(
            cls
        )  # Do not use cls(tracks) (reason? because it is a dataclass?)
        instance.extend(tracks)
        for key, value in attributes.items():
            setattr(instance, key, value)

        return instance

    def __DescriptionForJSON__(self) -> Any:
        """"""
        # Do not use dtcl.asdict(self) since it recurses into dataclass instances which, if they extend a "container"
        # class like list or dict, will lose information.
        attributes = {_fld.name: getattr(self, _fld.name) for _fld in dtcl.fields(self)}

        return list(self), attributes

    def FilterOut(
        self,
        TrackIssues: TrackIssues_h,
        /,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        TrackIssues: Arguments are: track and (optional) keyword arguments; Returned value can be None, an str, or a
            sequence of str.
        kwargs: Passed to TrackIsInvalid as keyword arguments
        """
        t_idx = 0
        while t_idx < self.__len__():
            track = self[t_idx]
            issues = TrackIssues(track, **kwargs)
            if issues is None:
                t_idx += 1
            else:
                self.invalids.append((track, issues))
                del self[t_idx]

    def RootCells(
        self, /, *, with_time_point: bool = False
    ) -> cells_w_optional_time_points_h:
        """"""
        if with_time_point:
            what = GetAttribute("root", "root_time_point")
        else:
            what = GetAttribute("root")

        return tuple(map(what, self))

    def MarkDividingCells(
        self,
        before_deaths: bool,
        /,
        *,
        division_responses: Dict[int, Optional[Sequence[float]]] = None,
        lower_bound: float = None,
        CombinedResponse: Callable[[Iterable], float] = max,
    ) -> None:
        """"""
        for track in self:
            if isinstance(track, forking_track_t):
                track.MarkDividingCells(
                    before_deaths,
                    division_responses=division_responses,
                    lower_bound=lower_bound,
                    CombinedResponse=CombinedResponse,
                )

    def DividingCells(
        self,
        /,
        *,
        with_time_point: bool = False,
        per_thread: bool = False,
    ) -> Union[cells_w_optional_time_points_h, per_thread_cells_h]:
        """"""
        if per_thread:
            output = {}
            AddDividing = output.update
        else:
            output = []
            AddDividing = output.extend

        for track in self:
            if isinstance(track, forking_track_t):
                dividing = track.DividingCells(
                    with_time_point=with_time_point, per_thread=per_thread
                )
                AddDividing(dividing)

        if with_time_point and not per_thread:
            output.sort(key=ItemAt(1))

        return output

    def DivisionTimePoints(self) -> Dict[int, Optional[Sequence[int]]]:
        """"""
        output = {}

        for track in self:
            if isinstance(track, forking_track_t):
                time_points = track.DivisionTimePoints()
                output.update(time_points)
            else:
                output[track.label] = None

        return output

    def MarkDeadCells(
        self,
        death_responses: Dict[int, Optional[Sequence[float]]],
        lower_bound: float,
        after_divisions: bool,
        /,
        *,
        CombinedResponse: Callable[[Iterable], float] = max,
    ) -> None:
        """
        A death is set if the highest response at a cell among the adjacent threads is above the threshold.
        """
        t_idx = 0
        while t_idx < self.__len__():
            track = self[t_idx]
            fully_pruned = track.MarkDeadCells(
                death_responses,
                lower_bound,
                after_divisions,
                CombinedResponse=CombinedResponse,
                called_from_educated_code=True,
            )
            if fully_pruned:
                self.fully_pruned.append(track)
                del self[t_idx]
            else:
                t_idx += 1

    def DeadCells(
        self,
        sequence_length: int,
        /,
        *,
        with_time_point: bool = False,
        with_living_leaves: bool = False,
        per_thread: bool = False,
    ) -> Union[cells_w_optional_time_points_h, per_thread_cell_h]:
        """"""
        if per_thread:
            output = {}
            AddDead = output.update
        else:
            output = []
            AddDead = output.extend

        for track in self:
            dead = track.DeadCells(
                sequence_length,
                with_time_point=with_time_point,
                with_living_leaves=with_living_leaves,
                per_thread=per_thread,
            )
            AddDead(dead)

        return output

    def DeathTimePoints(
        self,
        sequence_length: int,
        /,
        *,
        with_living_leaves: bool = False,
    ) -> Dict[int, Optional[int]]:
        """"""
        output = {}

        for track in self:
            time_points = track.DeathTimePoints(
                sequence_length,
                with_living_leaves=with_living_leaves,
            )
            output.update(time_points)

        return output

    def LeafCells(
        self, /, *, with_time_point: bool = False
    ) -> Union[cells_w_optional_time_points_h, per_thread_cells_h]:
        """"""
        leaves = []
        time_points = []
        for track in self:
            leaves.extend(track.leaves)
            time_points.extend(track.leaves_time_points)

        if with_time_point:
            return tuple(zip(leaves, time_points))

        return tuple(leaves)

    @property
    def topologic_labels(self) -> Sequence[int]:
        """"""
        output = []

        for track in self:
            output.extend(track.topologic_labels)

        return sorted(output)

    @property
    def labels(self) -> Sequence[int]:
        """"""
        output = []

        for track in self:
            output.extend(track.labels)

        return sorted(output)

    def TrackLabelsContainingCell(self, cell: cell_t, /) -> Sequence[int]:
        """"""
        for track in self:
            if cell in track:
                return track.TrackLabelsContainingCell(cell)

        raise ValueError(f"{cell}: Not a tracked cell")

    def AddFeature(
        self,
        name: str,
        cell_feature_name: Union[str, Sequence[str]],
        FeatureComputation: feature_filtering_h,
        /,
        *args,
        **kwargs,
    ) -> None:
        """
        /!\ There is no already-existing check
        """
        if isinstance(cell_feature_name, str):
            cell_feature_names = (cell_feature_name,)
        else:
            cell_feature_names = cell_feature_name
        available_features = self[0].topologic_root.available_features
        if any(_ftr not in available_features for _ftr in cell_feature_names):
            raise ValueError(f"{cell_feature_name}: Invalid cell feature(s)")

        for track in self:
            track.AddFeature(
                name, cell_feature_names, FeatureComputation, *args, **kwargs
            )

    def Feature(self, feature: str, /) -> per_thread_feature_h:
        """"""
        output = {}

        for track in self:
            output.update(track.features[feature])

        return output

    def Print(self) -> None:
        """"""
        for track in self:
            print(track)

    def PrintValidInvalidSummary(self) -> None:
        """"""
        n_invalids = []
        issues_per_type = {}
        for track_type in (unstructured_track_t, thread_track_t, forking_track_t):
            invalids = [
                _rcd for _rcd in self.invalids if isinstance(_rcd[0], track_type)
            ]
            track_type = track_type.__name__[:-2].replace("_", " ").capitalize()
            if invalids.__len__() == 0:
                number = f"{track_type}: None"
            else:
                number = f"{track_type}: {invalids.__len__()}"

                issues = (
                    f"    Track {_ThreadLabelsAsStr(_tck)}{isse.ISSUE_SEPARATOR}"
                    f"{isse.FactorizedIssuesAsStr(_iss, max_n_contexts=5)}"
                    for _tck, _iss in invalids
                )
                issues_per_type[track_type] = "\n".join(issues)

            n_invalids.append(number)

        n_invalids = ", ".join(n_invalids)
        issues_per_type = "\n".join(
            f"{_typ}:\n{_iss}" for _typ, _iss in issues_per_type.items()
        )

        print(
            f"Tracks: valid={self.__len__()}; "
            f"invalid={n_invalids}; "
            f"fully pruned={self.fully_pruned.__len__()}\n"
            f"{issues_per_type}"
        )

    def __hash__(self) -> int:
        """"""
        return hash(tuple(hash(_tck) for _tck in self))

    def __repr__(self) -> str:
        """"""
        return Identity(self)

    def __str__(self) -> str:
        """"""
        return f"{self.__repr__()}:\n    {self.__len__()=}\n    {self.invalids=}\n    {self.fully_pruned=}"

    def __contains__(self, cell: cell_t, /) -> bool:
        """"""
        return any(cell in _tck for _tck in self)

    def __eq__(self, other) -> bool:
        """"""
        return jsnr.JsonStringOf(self) == jsnr.JsonStringOf(other)


def _ThreadLabelsAsStr(track: thread_track_t, /) -> str:
    """"""
    return "+".join(str(_lbl) for _lbl in sorted(track.labels))
