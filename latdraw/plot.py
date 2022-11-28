import os
from typing import Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import ocelot
    OCELOT = True
except ImportError:
    OCELOT = False

import latdraw
from latdraw import lattice
import latdraw.interfaces as interfaces


def _get_lattice(lattice_or_path_to_one) -> lattice.Beamline:
    try:
        fpath = os.fspath(lattice_or_path_to_one)
    except TypeError:
        lattice = lattice_or_path_to_one
    else:
        return latdraw.read(fpath)

    try:
        lattice = interfaces.madx_twiss_to_beamline(lattice_or_path_to_one)
    except:
        pass

    return lattice

def subplots_with_lattice(lattice: Union[str, lattice.Beamline, pd.DataFrame],
                          nrows: int = 1, gridspec_kw=None, **kwargs):

    # height_ratios = [1, 0.5, 0.5, 1]
    # the_gridspec_kw = {"height_ratios": height_ratios,
    #                    "hspace": 0.05}
    # if gridspec_kw is None:
    #     gridspec_kw = {}
    # the_gridspec_kw |= gridspec_kw

    # Plot goes at the top
    pattern = [lattice]
    pattern.extend(nrows * [None])
    return subplots_with_lattices(pattern, **kwargs)

def subplots_with_lattices(pattern, **kwargs):
    pattern = np.array(pattern, dtype=object)

    height_ratios = np.full_like(pattern, 1.0, dtype=float)
    # Get indices of where machines should be plotted
    indices = [index for (index, value) in enumerate(pattern) if value is not None]
    height_ratios[indices] = 0.25


    the_gridspec_kw = {"height_ratios": height_ratios,
                       "hspace": 0.05}

    fig, axes = plt.subplots(nrows=len(pattern),
                             sharex=True,
                             gridspec_kw=the_gridspec_kw,
                             **kwargs)

    for lattice, ax in zip(pattern, axes):
        if lattice is None:
            continue

        lattice = _get_lattice(lattice)
        latdraw.draw(fig, ax, lattice)

        ax.set_yticks([], [])

        ax.tick_params(top=False,
                       bottom=False,
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)

        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # ax.spines['top'].set_visible(True)
        # ax.spines['bottom'].set_visible(False)

        ax.set_ylim(-0.25, 0.25)


    return fig, axes
