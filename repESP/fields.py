"""Types used to describe fields as values at selected points in space

Attributes
----------
"""

from repESP.types import Coords, Dist

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, InitVar
from typing import Any, cast, Collection, Generic, Iterable, Iterator, List, NewType, Tuple, Type, TypeVar

import functools
import math
import operator


EspT = TypeVar('EspT', bound='Esp')
class Esp(float):
    """Electrostatic potential value in atomic units (:math:`E_h/e`)

    Parameters
    ----------
    value : Any
        Any value convertible to float representing the value in atomic units.
    """

    __slots__ = ()

    def __new__(cls: Type[EspT], value: Any) -> EspT:
        return super().__new__(cls, float(value))  # type: ignore # (Too many arguments for "__new__" of "object")

    def __repr__(self) -> str:
        return f"Esp({super().__repr__()})"

    def __str__(self) -> str:
        return f"{super().__str__()} a.u."


EdT = TypeVar('EdT', bound='Ed')
class Ed(float):
    """Electron density value in atomic units (\ :math:`e / \mathrm{a}_0^3`\ )

    Parameters
    ----------
    value : Any
        Any value convertible to float representing the value in atomic units.
    """

    __slots__ = ()

    def __new__(cls: Type[EdT], value: Any) -> EdT:
        return super().__new__(cls, float(value))  # type: ignore # (Too many arguments for "__new__" of "object")

    def __repr__(self) -> str:
        return f"Ed({super().__repr__()})"

    def __str__(self) -> str:
        return f"{super().__str__()} a.u."


class AbstractMesh(ABC):
    """Abstract base class for collections of points in space

    Calling ``len`` on instances of this class will return the number of points.
    """

    @property
    @abstractmethod
    def points(self) -> Iterator[Coords]:
        """Coordinates of points of which the mesh consists

        The order of iteration must be defined.

        Yields
        ------
        Iterator[Coords]
            Iterator over the point coordinates
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass


@dataclass
class Mesh(AbstractMesh):
    """Collection of points in space without assumptions regarding structure

    This class stores all the points given on initialization and hence it's
    memory footprint is linear in the number of points.

    Parameters
    ----------
    points_ : Collection[Coords]
        The coordinates of points to be stored
    """
    points_: InitVar[Collection[Coords]]
    _points: List[Coords] = field(init=False)

    def __post_init__(self, points_: Collection[Coords]) -> None:
        self._points = list(points_)

    @property
    def points(self) -> Iterator[Coords]:
        """Coordinates of points of which the mesh consists

        The order of iteration is the same as that of the collection provided
        during initialization.

        Yields
        ------
        Iterator[Coords]
            Iterator over the point coordinates
        """
        return iter(self._points)

    def __len__(self) -> int:
        return len(self._points)


@dataclass
class GridMesh(AbstractMesh):
    """Collection of points in space organized in a grid

    This class only stores information regarding the grid which underlies the
    spatial organization of the points and thus it's memory footprint is constant
    with respect to the number of points it describes. This a trade-off for a
    small CPU cost whenever a point is retrieved from the ``points`` iterator.

    Parameters
    ----------
    origin : Coords
        The coordinates of the coordinates system origin.
    axes : Axes
        The coordinates of the coordinates axes' origin.

    Attributes
    ----------
    Axes : Tuple[GridMesh.Axis, GridMesh.Axis, GridMesh.Axis]
        Type alias for a tuple of three ``Axis`` objects. Note that currently
        only axes aligned with the coordinate system axes are supported, i.e.
        the axes' vectors are expected to be::

            ((x_step, 0, 0), (0, y_step, 0), (0, 0, z_step))
    """

    @dataclass
    class Axis:
        """Dataclass describing a coordinate system axis

        Parameters
        ----------
        vector : Coords
            Unit vector in xyz coordinates, for example::

                (Dist(1), Dist(0), Dist(0))

            for a typical x-axis with a point every 1 a₀.

        point_count : int
            The number of points that the grid places along this axis.

        Attributes
        ----------
        vector
            See initialization parameter
        point_count
            See initialization parameter
        """
        vector: Coords
        point_count: int

        def __post_init__(self) -> None:
            if self.point_count < 0:
                raise ValueError(
                    f"Negative value of `point_count` given: {self.point_count}."
                )

    _AxesT = TypeVar('_AxesT', bound='Axes')
    class Axes(Tuple[Axis, Axis, Axis]):
        def __new__(cls: Type["GridMesh._AxesT"], values: Iterable["GridMesh.Axis"]) -> "GridMesh._AxesT":
            self_to_be = super().__new__(cls, values)  # type: ignore # https://github.com/python/mypy/issues/8541
            if len(self_to_be) != 3:
                raise ValueError("Axes constructor expected an iterable yielding three elements.")
            return self_to_be

    origin: Coords
    axes: Axes

    def __post_init__(self) -> None:
        # TODO: Remove this assumption (affects implementation of self.points)
        if (not self._axes_are_aligned_to_coordinate_axes(self.axes)):
            raise NotImplementedError(
                f"GridMesh cannot currently be constructed with axes not aligned"
                f" to coordinate axes. The provided axes are: {self.axes}"
            )

    @staticmethod
    def _axes_are_aligned_to_coordinate_axes(axes: Axes) -> bool:
        return functools.reduce(
            operator.and_,
            (math.isclose(vector_component, Dist(0)) for vector_component in [
                axes[0].vector[1],
                axes[0].vector[2],
                axes[1].vector[0],
                axes[1].vector[2],
                axes[2].vector[0],
                axes[2].vector[1],
            ])
        )

    @property
    def points(self) -> Iterator[Coords]:
        """Coordinates of points of which the mesh consists

        The order of iteration is the same as the order of values in a Gaussian
        "cube" file. Values of `z` are incremented first, then all values of
        `y`, and finally all values of `x`. This is best described with the
        following pseudocode::

            for x in x_values:
                for y in y_values:
                    for z in z_values:
                        yield (x, y, z)

        Yields
        ------
        Iterator[Coords]
            Iterator over the point coordinates
        """
        for i in range(self.axes[0].point_count):
            for j in range(self.axes[1].point_count):
                for k in range(self.axes[2].point_count):
                    yield Coords((
                        Dist(self.origin[0] + i*self.axes[0].vector[0]),
                        Dist(self.origin[1] + j*self.axes[1].vector[1]),
                        Dist(self.origin[2] + k*self.axes[2].vector[2])
                    ))

    def __len__(self) -> int:
        return functools.reduce(
            operator.mul,
            (axis.point_count for axis in self.axes)
        )


FieldValue = TypeVar('FieldValue')
"""typing.TypeVar : The generic type for the values of the `Field` class.

There are no restrictions on what this type can be.
"""

@dataclass
class Field(Generic[FieldValue]):
    """Dataclass representing values of a field at a "mesh" of points in space

    This class is generic in the type of the field value, which can be of any
    type. Classes where `FieldValue` matches `NumericValue`, additionally
    support arithmetic operations (currently only addition and subtraction).

    Parameters
    ----------
    mesh : AbstractMesh
        A "mesh" of points in space at which the field has values
    values\_ : Collection[FieldValue]
        A collection of values corresponding to the points in space given in
        the same order as the `AbstractMesh.points` iterator.

    Attributes
    ----------
    mesh
        See initialization parameter
    values : typing.List[FieldValue]
        Converted from the `values_` initialization parameter
    NumericValue : typing.TypeVar
        Generic type specifying a subset of FieldValue types for which arithmetic
        operations are defined. This can be any type matching "bound=float".
    """

    mesh: AbstractMesh
    values_: InitVar[Collection[FieldValue]]
    values: List[FieldValue] = field(init=False)

    def __post_init__(self, values_: Collection[FieldValue]) -> None:

        if len(values_) != len(self.mesh):
            raise ValueError(
                f"Construction of a Field failed due to mismatch between the "
                f"number of points ({len(self.mesh)}) and the number of values ({len(values_)})"
            )

        self.values = list(values_)

    # TODO: This would ideally be extended to numbers.Number but mypy throws errors.
    NumericValue = TypeVar('NumericValue', bound=float)

    def __add__(self: 'Field[NumericValue]', other: 'Field[NumericValue]') -> 'Field[NumericValue]':

        if not isinstance(other, Field):
            raise TypeError(
                "unsupported operand type(s) for +: 'Field' and 'type(other)"
            )

        if self.mesh != other.mesh:
            raise ValueError(
                "Cannot add or subtract Fields with different meshes."
            )

        return Field(
            self.mesh,
            [
                cast(Field.NumericValue, value_self + value_other)
                for value_self, value_other in zip(self.values, other.values)
            ]
        )

    def __neg__(self: 'Field[NumericValue]') -> 'Field[NumericValue]':
        return Field(
            self.mesh,
            [
                cast(Field.NumericValue, -value)
                for value in self.values
            ]
        )

    def __sub__(self: 'Field[NumericValue]', other: 'Field[NumericValue]') -> 'Field[NumericValue]':
        return self + (-other)

    # TODO: Could add div and sub but it's not needed at the moment.
    # TODO: __iadd__ can be added as an optimization (unless we decide to
    # freeze the dataclass.
