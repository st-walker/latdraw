import os
from pathlib import Path
from IPython import embed_kernel

import pandas as pd
import pand8
import tfs

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

        match keyword:
            case "DRIFT":
                yield lattice.Drift(name, position, length)
            case "RBEND":
                yield lattice.RBend(name, position, length, tup.ANGLE)
            case "SBEND":
                yield lattice.SBend(name, position, length, tup.ANGLE)
            case "QUADRUPOLE":
                yield lattice.Quadrupole(name, position, length, k1)
            case "SEXTUPOLE":
                yield lattice.Sextupole(name, position, length, k2)
            case "OCTUPOLE":
                yield lattice.Sextupole(name, position, length, k3)
            case "HKICKER":
                yield lattice.HKicker(name, position, length, tup.ANGLE)
            case "VKICKER":
                yield lattice.VKicker(name, position, length, tup.ANGLE)
            case "KICKER":
                yield lattice.Kicker(name, position, length, tup.ANGLE)
            case "MARKER":
                yield lattice.Marker(name, position)
            case "MONITOR":
                yield lattice.Monitor(name,  position)
            case _:
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

        match keyword:
            case "": # Skip this blank element that starts every mad8 lattice?
                pass
            case "DRIF":
                yield lattice.Drift(name, position, length)
            case "RBEN":
                yield lattice.RBend(name, position, length, tup.ANGLE)
            case "SBEN":
                yield lattice.SBend(name, position, length, tup.ANGLE)
            case "QUAD":
                yield lattice.Quadrupole(name, position, length, tup.K1)
            case "SEXT":
                yield lattice.Sextupole(name, position, length, tup.K2)
            case "OCTU":
                yield lattice.Sextupole(name, position, length, tup.K3)
            case "HKIC":
                yield lattice.HKicker(name, position, length, tup.ANGLE)
            case "VKIC":
                yield lattice.VKicker(name, position, length, tup.ANGLE)
            case "KICK":
                yield lattice.Kicker(name, position, length, tup.ANGLE)
            case "MARK":
                yield lattice.Marker(name, position)
            case "MONI":
                yield lattice.Monitor(name,  position)
            case "SOLE":
                yield lattice.Solenoid(name, position, length)
            case "ECOL":
                yield lattice.Collimator(name, position, length)
            case "LCAV":
                yield lattice.Cavity(name, position, length)
            case "MATR":
                yield lattice.GenericMap(name, position, length)
            case _:
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

        match keyword:
            case "drift":
                yield lattice.Drift(name, position, length)
            case "rbend":
                yield lattice.RBend(name, position, length, tup.Angle)
            case "sbend":
                yield lattice.SBend(name, position, length, tup.Angle)
            case "quadrupole":
                yield lattice.Quadrupole(name, position, length, tup.k1)
            case "sextupol":
                yield lattice.Sextupole(name, position, length, tup.k2)
            case "octupole":
                yield lattice.Sextupole(name, position, length, tup.k3)
            case "hkicker":
                yield lattice.HKicker(name, position, length, tup.Angle)
            case "vkicker":
                yield lattice.VKicker(name, position, length, tup.Angle)
            case "kicker":
                yield lattice.Kicker(name, position, length, tup.Angle)
            case _:
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
