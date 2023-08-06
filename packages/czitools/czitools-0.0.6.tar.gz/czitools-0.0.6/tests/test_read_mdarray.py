
from czitools.metadata import pylibczirw_metadata as czimd
from czitools.imagedata import pylibczirw_tools
import os
from pathlib import Path

basedir = Path(__file__).resolve().parents[1]


def test_read_mdarray_1():

    # get the CZI filepath
    filepath = os.path.join(basedir, r"data/w96_A1+A2.czi")

    mdarray, dimstring = pylibczirw_tools.read_mdarray(filepath, remove_Adim=False)

    assert (dimstring == "STZCYXA")
    assert (mdarray.shape == (2, 1, 1, 2, 1416, 1960, 1))

    mdarray, dimstring = pylibczirw_tools.read_mdarray(filepath, remove_Adim=True)

    assert (dimstring == "STZCYX")
    assert (mdarray.shape == (2, 1, 1, 2, 1416, 1960))


def test_read_mdarray_2():

    # get the CZI filepath
    filepath = os.path.join(basedir, r"data/S=2_3x3_CH=2.czi")

    mdarray, dimstring = pylibczirw_tools.read_mdarray(filepath, remove_Adim=False)

    assert (dimstring == "STZCYXA")
    assert (mdarray.shape == (2, 1, 1, 2, 1792, 1792, 1))

    mdarray, dimstring = pylibczirw_tools.read_mdarray(filepath, remove_Adim=True)

    assert (dimstring == "STZCYX")
    assert (mdarray.shape == (2, 1, 1, 2, 1792, 1792))


def test_read_mdarray_lazy_1():

    # get the CZI filepath
    filepath = os.path.join(basedir, r"data/w96_A1+A2.czi")

    mdarray, dimstring = pylibczirw_tools.read_mdarray_lazy(filepath, remove_Adim=False)

    assert (dimstring == "STZCYXA")
    assert (mdarray.shape == (2, 1, 1, 2, 1416, 1960, 1))
    assert (mdarray.ndim == 7)
    assert (mdarray.chunksize == (1, 1, 1, 2, 1416, 1960, 1))

    mdarray, dimstring = pylibczirw_tools.read_mdarray_lazy(filepath, remove_Adim=True)

    assert (dimstring == "STZCYX")
    assert (mdarray.shape == (2, 1, 1, 2, 1416, 1960))
    assert (mdarray.ndim == 6)
    assert (mdarray.chunksize == (1, 1, 1, 2, 1416, 1960))
