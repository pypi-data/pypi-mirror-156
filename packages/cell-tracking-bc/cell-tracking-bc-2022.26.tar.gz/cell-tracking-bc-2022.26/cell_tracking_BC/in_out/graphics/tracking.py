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

from typing import Optional, Sequence, Tuple, Union

import numpy as nmpy

import cell_tracking_BC.in_out.graphics.generic.d_3 as thrd
from cell_tracking_BC.in_out.graphics.dbe.matplotlib.context import DRAWING_CONTEXT
from cell_tracking_BC.in_out.graphics.type.axes import axes_3d_t
from cell_tracking_BC.in_out.graphics.type.context import context_t
from cell_tracking_BC.in_out.graphics.type.figure import figure_t
from cell_tracking_BC.type.cell.cell import cell_t
from cell_tracking_BC.type.analysis import analysis_t
from cell_tracking_BC.type.track.single.unstructured import unstructured_track_t


_LOW_AFFINITY = 0.75
_MATPLOTLIB_COLORS = ("b", "g", "r", "c", "m", "y", "k")


def ShowTracking2D(
    analysis: analysis_t,
    /,
    *,
    version: str = None,
    with_segmentation: bool = True,
    with_cell_labels: bool = True,
    with_track_labels: bool = True,
    with_ticks: bool = True,
    with_colorbar: bool = True,
    mode: str = "forking",
    figure_name: str = "tracking-2D",
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    dbe: context_t = DRAWING_CONTEXT,
) -> Optional[figure_t]:
    """"""
    output = None

    explorer = dbe.t_explorer_2d_t.NewForSequence(
        analysis,
        dbe,
        version=version,
        with_segmentation=with_segmentation,
        with_cell_labels=with_cell_labels,
        with_track_labels=with_track_labels,
        with_ticks=with_ticks,
        with_colorbar=with_colorbar,
        mode=mode,
    )

    explorer.figure.Archive(name=figure_name)
    if prepare_only:
        output = explorer
    else:
        explorer.figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output


def ShowTracking3D(
    analysis: analysis_t,
    /,
    *,
    with_track_labels: bool = True,
    with_cell_labels: bool = True,
    figure_name: str = "tracking-3D",
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    dbe: context_t = DRAWING_CONTEXT,
) -> Optional[figure_t]:
    """"""
    output = None

    figure, axes = dbe.figure_3d_t.NewFigureAndAxes()
    axes: axes_3d_t
    colormap = axes.AddColormapFromMilestones(
        "Tracking Affinity", ((0.0, "black"), (0.75, "red"), (1.0, "blue"))
    )

    thrd.PlotFirstFrameAsFloor(analysis.sequence[analysis.sequence.main_channel][0], axes)

    time_scaling = axes.__class__.TimeScaling(analysis.sequence.shape, analysis.sequence.length)
    for t_idx, track in enumerate(analysis.tracks):
        low_affinities = tuple(
            _ffn < _LOW_AFFINITY for _ffn in track.tracking_affinities
        )
        low_fraction = nmpy.count_nonzero(low_affinities) / (
            0.3 * low_affinities.__len__()
        )
        color = colormap(1.0 - min(1.0, low_fraction))

        for cells, start_time_point, label in track.PiecesIterator():
            rows, cols, times, *cell_labels = _AsRowsColsTimes(
                cells, start_time_point, with_labels=with_cell_labels
            )
            times = tuple(time_scaling * _tme for _tme in times)

            axes.PlotLines(rows, cols, times, color=color)

            if with_cell_labels:
                for row, col, time, cell_label in zip(
                    rows, cols, times, cell_labels[0]
                ):
                    axes.PlotText(
                        row,
                        col,
                        time,
                        str(cell_label),
                        fontsize="x-small",
                        color=color,
                    )
            if with_track_labels and (label is not None):
                axes.PlotText(
                    rows[-1],
                    cols[-1],
                    times[-1] + 0.25,
                    str(label),
                    fontsize="x-small",
                    color=color,
                )

    axes.SetTimeAxisProperties(analysis.sequence.length - 1)

    figure.Archive(name=figure_name)
    if prepare_only:
        output = figure
    else:
        figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output


def ShowUnstructuredTracking3D(
    analysis: analysis_t,
    /,
    *,
    with_cell_labels: bool = True,
    figure_name: str = "unstructured-tracking-3D",
    prepare_only: bool = False,
    interactively: bool = True,
    in_main_thread: bool = True,
    dbe: context_t = DRAWING_CONTEXT,
) -> Optional[figure_t]:
    """"""
    output = None

    invalids = [
        _rcd[0]
        for _rcd in analysis.tracks.invalids
        if isinstance(_rcd[0], unstructured_track_t)
    ]
    if invalids.__len__() == 0:
        return

    figure, axes = dbe.figure_3d_t.NewFigureAndAxes()
    axes: axes_3d_t

    colors = _MATPLOTLIB_COLORS
    for t_idx, track in enumerate(invalids):
        color_idx = t_idx % colors.__len__()

        for time_point, *cells, _ in track.segments_iterator:
            rows, cols = tuple(zip(*(_cll.centroid.tolist() for _cll in cells)))
            times = (time_point, time_point + 1)

            axes.PlotLines(rows, cols, times, colors[color_idx])

            if with_cell_labels:
                # TODO: explain why building a tuple, and then taking only the first element
                labels = tuple(_cll.label for _cll in cells)
                for row, col, time, label in zip(rows, cols, times, labels[0]):
                    axes.PlotText(
                        row,
                        col,
                        time,
                        str(label),
                        fontsize="x-small",
                        color=colors[color_idx],
                    )

    axes.SetTimeAxisProperties(analysis.sequence.length - 1)

    figure.Archive(name=figure_name)
    if prepare_only:
        output = figure
    else:
        figure.Show(interactively=interactively, in_main_thread=in_main_thread)

    return output


def _AsRowsColsTimes(
    cells: Sequence[cell_t], start_time_point: int, /, *, with_labels: bool = False
) -> Union[
    Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[int, ...]],
    Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[int, ...], Tuple[int, ...]],
]:
    """"""
    n_cells = cells.__len__()

    rows, cols = tuple(zip(*(_cll.centroid.tolist() for _cll in cells)))
    times = tuple(range(start_time_point, start_time_point + n_cells))

    if with_labels:
        labels = tuple(_cll.label for _cll in cells)
        return rows, cols, times, labels

    return rows, cols, times
