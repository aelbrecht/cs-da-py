from __future__ import annotations

import math


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_square(self) -> float:
        return self.x * self.x + self.y * self.y

    def unit_vector(self) -> Point:
        m = self.magnitude()
        return Point(self.x / m, self.y / m)

    def distance(self, p: Point):
        a = self.x - p.x
        b = self.y - p.y
        return math.sqrt(a * a + b * b)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def dot(self, other: Point) -> float:
        return self.x * other.y - self.y * other.x

    def __mul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __eq__(self, other: Point):
        return self.x == other.x and self.y == other.y


class Disk:
    id: int
    _x: float
    _y: float
    _r: float

    def __str__(self):
        return f"({self.id}) (r: {self._r}) at ({self._x}, {self._y})"

    def __ne__(self, other):
        return self.id != other.id

    def __eq__(self, other):
        return self.id == other.id

    def center(self) -> Point:
        return Point(self._x, self._y)

    def radius(self) -> float:
        return self._r

    def contains(self, other: Disk, tolerance: float = 1.0e-6) -> bool:
        abs_center = self.center() - other.center()
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
        return f"({self.start.x}, {self.start.y}) -> ({self.end.x}, {self.end.y})"

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
        return Point(-dir_vec.y, dir_vec.x)

    def is_point(self):
        return self.start == self.end


def load(filename="./input/N10.txt") -> list[Disk]:
    disks: list[Disk] = []
    with open(filename) as f:
        i = 0
        for line in f:
            xs = line.split("\t")
            if len(xs) != 4:
                continue
            d = Disk()
            d.id = i
            d._x = float(xs[1])
            d._y = float(xs[2])
            d._r = float(xs[3])
            disks.append(d)
            i += 1
    return disks
