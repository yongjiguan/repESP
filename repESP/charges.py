"""Types used to describe partial charges and higher moments"""

from .exceptions import InputFormatError
from .types import Atom, AtomWithCoords, Coords

from dataclasses import dataclass
# from enum import auto
from typing import Any, List, Collection, Tuple, Type


class Charge(float):

    """Atomic charge [elementary charge]"""

    __slots__ = ()

    def __new__(cls, x: Any):
        return super().__new__(cls, float(x))  # type: ignore # (Too many arguments for "__new__" of "object")


# Could be useful as a common denominator between modules, e.g. to translate
# a given charge type to its corresponding ChargesSectionParser. However, this
# is currently not necessary (and doesn't get rendered very nicely in Sphinx).
#
# class ChargeType(_NoValue):
#     MULLIKEN = auto()
#     MK = auto()
#     CHELP = auto()
#     CHELPG = auto()
#     HLY = auto()
#     NPA = auto()
#     AIM = auto()


@dataclass
class AtomWithCharge(Atom):
    charge: Charge


@dataclass
class AtomWithCoordsAndCharge(AtomWithCharge, AtomWithCoords):
    # NOTE: mypy incorrectly infers the argument order for __init__ to be:
    # (atomic_number, charge, coords), resulting in loads of spurious errors.
    pass


class DipoleMoment(float):

    """Dipole moment [bohr * fundamental charge]"""

    __slots__ = ()

    def __new__(cls, x: Any):
        return super().__new__(cls, float(x))  # type: ignore # (Too many arguments for "__new__" of "object")


@dataclass
class Dipole:
    x: DipoleMoment
    y: DipoleMoment
    z: DipoleMoment


class QuadrupoleMoment(float):

    """Quadrupole moment [bohr^2 * fundamental charge]"""

    __slots__ = ()

    def __new__(cls, x: Any):
        return super().__new__(cls, float(x))  # type: ignore # (Too many arguments for "__new__" of "object")


@dataclass
class Quadrupole:
    xx: QuadrupoleMoment
    yy: QuadrupoleMoment
    zz: QuadrupoleMoment
    xy: QuadrupoleMoment
    xz: QuadrupoleMoment
    yz: QuadrupoleMoment
