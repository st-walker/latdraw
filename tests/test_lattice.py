import numpy as np
import pytest

from latdraw import lattice


POSITION = [1, 2, 3]
LENGTH = 0.5

def test_init_Drift():
    name = "drift"
    drift = lattice.Drift(name, POSITION, LENGTH)

    assert drift.name == name
    assert drift.position == POSITION
    assert drift.length == LENGTH

def test_init_SBend():
    name = "sbend"
    angle = np.pi / 10
    sbend = lattice.SBend(name, POSITION, LENGTH, angle)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.angle == angle

def test_init_RBend():
    name = "rbend"
    angle = np.pi / 10
    sbend = lattice.RBend(name, POSITION, LENGTH, angle)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.angle == angle

def test_init_Quadrupole():
    name = "quadrupole"
    k1 = 0.005
    sbend = lattice.Quadrupole(name, POSITION, LENGTH, k1)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.k1 == k1

def test_init_Sextupole():
    name = "sextupole"
    k2 = 0.005
    sbend = lattice.Sextupole(name, POSITION, LENGTH, k2)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.k2 == k2

def test_init_Octupole():
    name = "octupole"
    k3 = 0.005
    sbend = lattice.Octupole(name, POSITION, LENGTH, k3)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.k3 == k3
    
def test_init_VKicker():
    name = "vkicker"
    angle = 0.005
    sbend = lattice.VKicker(name, POSITION, LENGTH, angle)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.angle == angle

def test_init_VKicker():
    name = "vkicker"
    angle = 0.005
    sbend = lattice.HKicker(name, POSITION, LENGTH, angle)

    assert sbend.name == name
    assert sbend.position == POSITION
    assert sbend.length == LENGTH
    assert sbend.angle == angle
    
