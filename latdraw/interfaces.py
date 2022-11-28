import os
from pathlib import Path

import pand8
import pandas as pd
import tfs
from IPython import embed_kernel

try:
    from ocelot.cpbd import elements as ole
except ImportError:
    pass


import latdraw.lattice as lattice


class FileTypeError(RuntimeError):
    pass

class UnknownElementType(RuntimeError):
    pass

def read(fname):
    """Generatl reader function"""
    try:
        return read_madx(fname)
    except tfs.errors.TfsFormatError:
        pass

    return read_mad8(fname)


def read_madx(fname):
    fname = os.fspath(fname)  # Accept any pathlike object

    df = tfs.read(fname)

    file_type = df.headers["TYPE"]
    if file_type not in {"SURVEY", "TWISS"}:
        raise FileTypeError(f"Unsupported TFS TYPE in header: {file_type}")

    latdraw_sequence = _loop_madx_df(df, survey=file_type == "SURVEY")
    return lattice.Beamline(latdraw_sequence)

def read_madx_survey(survey, twiss=None):
    # Optional twiss so for example the quads etc. point in the correct direction...
    pass

def madx_twiss_to_beamline(twiss):
    return lattice.Beamline(_loop_madx_df(twiss, survey=False))

def madx_survey_to_beamline(survey):
    return lattice.Beamline(_loop_madx_df(survey, survey=True))

def _loop_madx_df(tfs_df, survey):
    for tup in tfs_df.itertuples():
        name = tup.NAME
        length = tup.L

        z = tup.Z if survey else tup.S
        position = tup.X, tup.Y, z
        keyword = tup.KEYWORD

        if not survey and keyword.endswith("POLE"):
            k1 = tup.K1L / length
            k2 = tup.K2L / length
            k3 = tup.K3L / length
        else:
            k1 = k2 = k3 = 0

        if keyword == "DRIFT":
            yield lattice.Drift(name, position, length)
        elif keyword == "RBEND":
            yield lattice.RBend(name, position, length, tup.ANGLE)
        elif keyword == "SBEND":
            yield lattice.SBend(name, position, length, tup.ANGLE)
        elif keyword == "QUADRUPOLE":
            yield lattice.Quadrupole(name, position, length, k1)
        elif keyword == "SEXTUPOLE":
            yield lattice.Sextupole(name, position, length, k2)
        elif keyword == "OCTUPOLE":
            yield lattice.Sextupole(name, position, length, k3)
        elif keyword == "HKICKER":
            yield lattice.HKicker(name, position, length, tup.ANGLE)
        elif keyword == "VKICKER":
            yield lattice.VKicker(name, position, length, tup.ANGLE)
        elif keyword == "KICKER":
            yield lattice.Kicker(name, position, length, tup.ANGLE)
        elif keyword == "MARKER":
            yield lattice.Marker(name, position)
        elif keyword == "MONITOR":
            yield lattice.Monitor(name,  position)
        else:
            raise UnknownElementType(f"NAME={name}, KEYWORD={keyword}")

def read_mad8(fname):
    fname = os.fspath(fname) # Accept any pathlike object

    df = pand8.read(fname)

    file_type = df.attrs["DATAVRSN"]
    if file_type == "SURVEY":
        survey = True
    elif file_type == "TWISS":
        survey = False
    else:
        raise TFSTypeError(
            f"Unsupported MAD8 File DATAVRSN in header: {file_type}"
        )

    latdraw_sequence = list(_loop_mad8_df(df, survey))
    return lattice.Beamline(latdraw_sequence)

def _loop_mad8_df(mad8_df, is_survey):
    for tup in mad8_df.itertuples():
        name = tup.NAME
        length = tup.L

        z = tup.Z if is_survey else tup.SUML
        position = tup.X, tup.Y, z
        keyword = tup.KEYWORD

        if keyword == "": # Skip this blank element that starts every mad8 lattice?
            pass
        elif keyword == "DRIF":
            yield lattice.Drift(name, position, length)
        elif keyword == "RBEN":
            yield lattice.RBend(name, position, length, tup.ANGLE)
        elif keyword == "SBEN":
            yield lattice.SBend(name, position, length, tup.ANGLE)
        elif keyword == "QUAD":
            yield lattice.Quadrupole(name, position, length, tup.K1)
        elif keyword == "SEXT":
            yield lattice.Sextupole(name, position, length, tup.K2)
        elif keyword == "OCTU":
            yield lattice.Sextupole(name, position, length, tup.K3)
        elif keyword == "HKIC":
            yield lattice.HKicker(name, position, length, tup.ANGLE)
        elif keyword == "VKIC":
            yield lattice.VKicker(name, position, length, tup.ANGLE)
        elif keyword == "KICK":
            yield lattice.Kicker(name, position, length, tup.ANGLE)
        elif keyword == "MARK":
            yield lattice.Marker(name, position)
        elif keyword == "MONI":
            yield lattice.Monitor(name,  position)
        elif keyword == "SOLE":
            yield lattice.Solenoid(name, position, length)
        elif keyword == "ECOL":
            yield lattice.Collimator(name, position, length)
        elif keyword == "LCAV":
            yield lattice.Cavity(name, position, length)
        elif keyword == "MATR":
            yield lattice.GenericMap(name, position, length)
        else:
            raise UnknownElementType(f"NAME={name}, KEYWORD={keyword}")


# def _like()

def read_bdsim_survey(fname, straighten=False):
    bdsim_survey_df = pd.read_csv(fname,
                                  skiprows=1,
                                  delim_whitespace=True,
                                  skipfooter=2,
                                  # engine="python"  # Because of use of skipfooter
                                  )
    new_columns = []
    for column_name in bdsim_survey_df.columns:
        name_without_units, *_ = column_name.split("[")
        new_columns.append(name_without_units)
    bdsim_survey_df.columns = new_columns

    latdraw_sequence = list(_loop_bdsim_survey_df(bdsim_survey_df, straighten))
    return lattice.Beamline(latdraw_sequence)

def _loop_bdsim_survey_df(bdsim_survey_df, straighten=False):
    ignoreable_types = {"dipolefringe"}
    for tup in bdsim_survey_df.itertuples():
        name = tup.Name
        length = tup.ChordLength

        if straighten:
            position = 0, 0, tup.SEnd
        else:
            position = tup.X, tup.Y, tup.Z

        keyword = tup.Type


        if keyword in ignoreable_types:
            continue

        if keyword == "drift":
            yield lattice.Drift(name, position, length)
        elif keyword == "rbend":
            yield lattice.RBend(name, position, length, tup.Angle)
        elif keyword == "sbend":
            yield lattice.SBend(name, position, length, tup.Angle)
        elif keyword == "quadrupole":
            yield lattice.Quadrupole(name, position, length, tup.k1)
        elif keyword == "sextupol":
            yield lattice.Sextupole(name, position, length, tup.k2)
        elif keyword == "octupole":
            yield lattice.Sextupole(name, position, length, tup.k3)
        elif keyword == "hkicker":
            yield lattice.HKicker(name, position, length, tup.Angle)
        elif keyword == "vkicker":
            yield lattice.VKicker(name, position, length, tup.Angle)
        elif keyword == "kicker":
            yield lattice.Kicker(name, position, length, tup.Angle)
        else:
            raise UnknownElementType(f"NAME={name}, KEYWORD={keyword}")


def lattice_from_ocelot(ocelot_lattice):
    seq = ocelot_lattice

    try:
        seq = ocelot_lattice.sequence
    except AttributeError:
        pass

    return lattice.Beamline(_loop_lattice_from_ocelot(seq))


def _loop_lattice_from_ocelot(ocelot_sequence):


    s = 0
    for ele in ocelot_sequence:
        name = ele.id
        l = ele.l
        s +=  l
        position = [0, 0, s]

        if isinstance(ele, ole.Marker):
            yield lattice.Marker(name, position)
        elif isinstance(ele, ole.Monitor):
            yield lattice.Monitor(name, position)
        elif isinstance(ele, ole.Drift):
            yield lattice.Drift(name, position, l)
        elif isinstance(ele, ole.RBend):
            yield lattice.RBend(name, position, l, ele.angle)
        elif isinstance(ele, ole.SBend):
            yield lattice.SBend(name, position, l, ele.angle)
        elif isinstance(ele, ole.Quadrupole):
            yield lattice.Quadrupole(name, position, l, ele.k1)
        elif isinstance(ele, ole.TDCavity):
            yield lattice.TransverseDeflectingCavity(name, position, l, ele.v)
        elif isinstance(ele, ole.Vcor):
            yield lattice.VKicker(name, position, l, ele.angle)
        elif isinstance(ele, ole.Hcor):
            yield lattice.HKicker(name, position, l, ele.angle)
        elif isinstance(ele, ole.Cavity):
            yield lattice.RFCavity(name, position, l)
        elif isinstance(ele, ole.Solenoid):
            yield lattice.Solenoid(name, position, l, ele.k)
        elif isinstance(ele, ole.Undulator):
            yield lattice.Undulator(name, position, l)
        else:
            raise UnknownElementType(name, type(ele))




    # from IPython import embed; embed()
