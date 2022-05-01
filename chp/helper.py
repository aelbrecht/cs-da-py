from __future__ import annotations

import math
from enum import Enum


class Point:
    _x: float
    _y: float

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    def magnitude(self) -> float:
        return math.sqrt(self._x * self._x + self._y * self._y)

    def unit_vector(self) -> Point:
        m = self.magnitude()
        return Point(self._x / m, self._y / m)

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y

    def __str__(self):
        return f"Point({self._x}, {self._y})"

    def __sub__(self, other: Point) -> Point:
        return Point(self._x - other._x, self._y - other._y)

    def dot(self, other: Point) -> float:
        return self._x * other._y - self._y * other._x

    def __mul__(self, scalar: float) -> Point:
        return Point(self._x * scalar, self._y * scalar)

    def __add__(self, other: Point) -> Point:
        return Point(self._x + other._x, self._y + other._y)

    def __neg__(self):
        return Point(-self._x, -self._y)

    def __eq__(self, other: Point):
        return self._x == other._x and self._y == other._y


class Disk(Point):
    _id: int
    _r: float

    def __init__(self, uid: int, x: float, y: float, radius: float):
        super().__init__(x, y)
        self._r = radius
        self._id = uid

    def __str__(self):
        return f"Disk({self._id}) (r: {self._r}) at Point({self._x}, {self._y})"

    def __ne__(self, other):
        return self._id != other.id()

    def __eq__(self, other):
        if isinstance(other, Point):
            return super().__eq__(other)
        elif isinstance(other, Disk):
            return self._id == other.id()
        return False

    def id(self) -> int:
        return self._id

    def point(self) -> Point:
        return Point(self._x, self._y)

    def radius(self) -> float:
        return self._r

    def contains(self, other: Disk, tolerance: float = 1.0e-6) -> bool:
        abs_center = self.point() - other.point()
        distance = abs_center.magnitude()
        return self.radius() >= (other.radius() + distance) - tolerance


class Line:
    start: Point
    end: Point

    def __init__(self, a: Point, b: Point):
        assert isinstance(a, Point)
        assert isinstance(b, Point)
        self.start = a
        self.end = b

    def __str__(self):
        return f"({self.start.x()}, {self.start.y()}) -> ({self.end.x()}, {self.end.y()})"

    def signed_distance(self, p: Point):
        sp_vector = p - self.start
        line_vector = self.end - self.start
        return line_vector.dot(sp_vector) / line_vector.magnitude()

    def perpendicular(self, p: Point):
        dir_vec = self.normal_vector()
        return Line(p, p + dir_vec)

    def vector(self) -> Point:
        return self.end - self.start

    def normal_vector(self):
        dir_vec = self.vector()
        return Point(-dir_vec.y(), dir_vec.x())

    def is_point(self):
        return self.start == self.end


class Sliver(Enum):
    SLIVER_CASE_A = 1
    SLIVER_CASE_B = 2
    SLIVER_CASE_C1 = 3
    SLIVER_CASE_C2 = 4
