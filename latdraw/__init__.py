"""Top-level package for latdraw."""

__author__ = """Stuart Derek Walker"""
__email__ = 'stuart.walker@desy.de'
__version__ = '0.1.0'


# If this were to be done properly, the positions etc. wouldn't have to be
# attached to the individual elements, they'd just be calcualted automatically
# w.r.t its positio in the beamline...

from latdraw.interfaces import read, read_bdsim_survey, read_mad8, read_madx
from latdraw.latdraw import draw
from latdraw.plot import subplots_with_lattice, subplots_with_lattices

try:
    import ocelot

    from latdraw.interfaces import lattice_from_ocelot
    del ocelot
except ImportError:
    pass
