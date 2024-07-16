from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_core.document import Document


class Point:
    def __init__(
        self,
        x: float,
        y: float,
    ) -> None:
        self.x = x
        self.y = y


class Bezier:
    def __init__(
        self,
        cp1_x: float,
        cp1_y: float,
        cp2_x: float,
        cp2_y: float,
        endp_x: float,
        endp_y: float,
    ) -> None:
        self.cp1_x = cp1_x
        self.cp1_y = cp1_y
        self.cp2_x = cp2_x
        self.cp2_y = cp2_y
        self.endp_x = endp_x
        self.endp_y = endp_y


class Curve:
    def __init__(
        self,
        x: float,
        y: float,
        closed: bool,
        fill_color: tuple[int, int, int] | None,
        line_color: tuple[int, int, int] | None,
        line_width: float,
        line_pattern: tuple[int, int, int, int, int],
    ) -> None:
        self.path: list[Point | Bezier] = [Point(x, y)]
        self.closed = closed
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.line_pattern = line_pattern
        self.transformations: list[Rotation | Skew] = []

    def add_point(
        self,
        x: float,
        y: float,
    ) -> None:
        self.path.append(Point(x, y))

    def add_bezier(
        self,
        cp1_x: float,
        cp1_y: float,
        cp2_x: float,
        cp2_y: float,
        endp_x: float,
        endp_y: float,
    ) -> None:
        self.path.append(Bezier(cp1_x, cp1_y, cp2_x, cp2_y, endp_x, endp_y))

    def add_rotation(
        self,
        x_origin: float,
        y_origin: float,
        degrees: float,
    ):
        self.transformations.append(Rotation(x_origin, y_origin, degrees))

    def add_skew(
        self,
        x_origin: float,
        y_origin: float,
        vertical_degrees: float,
        horizontal_degrees: float,
    ):
        self.transformations.append(Skew(x_origin, y_origin, vertical_degrees, horizontal_degrees))


class Rectangle:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill_color: tuple[int, int, int] | None,
        line_color: tuple[int, int, int] | None,
        line_width: float,
        line_pattern: tuple[int, int, int, int, int],
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rounded_corner_top_left: float = 0
        self.rounded_corner_top_right: float = 0
        self.rounded_corner_bottom_left: float = 0
        self.rounded_corner_bottom_right: float = 0
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.line_pattern = line_pattern
        self.transformations: list[Rotation | Skew] = []

    def add_rotation(
        self,
        x_origin: float,
        y_origin: float,
        degrees: float,
    ):
        self.transformations.append(Rotation(x_origin, y_origin, degrees))

    def add_skew(
        self,
        x_origin: float,
        y_origin: float,
        vertical_degrees: float,
        horizontal_degrees: float,
    ):
        self.transformations.append(Skew(x_origin, y_origin, vertical_degrees, horizontal_degrees))


class Arc:
    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        line_color: tuple[int, int, int] | None,
        line_width: float,
        line_pattern: tuple[int, int, int, int, int],
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.line_color = line_color
        self.line_width = line_width
        self.line_pattern = line_pattern
        self.transformations: list[Rotation | Skew] = []

    def add_rotation(
        self,
        x_origin: float,
        y_origin: float,
        degrees: float,
    ):
        self.transformations.append(Rotation(x_origin, y_origin, degrees))

    def add_skew(
        self,
        x_origin: float,
        y_origin: float,
        vertical_degrees: float,
        horizontal_degrees: float,
    ):
        self.transformations.append(Skew(x_origin, y_origin, vertical_degrees, horizontal_degrees))


class Ellipse:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill_color: tuple[int, int, int] | None,
        line_color: tuple[int, int, int] | None,
        line_width: float,
        line_pattern: tuple[int, int, int, int, int],
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.line_pattern = line_pattern
        self.transformations: list[Rotation | Skew] = []

    def add_rotation(
        self,
        x_origin: float,
        y_origin: float,
        degrees: float,
    ):
        self.transformations.append(Rotation(x_origin, y_origin, degrees))

    def add_skew(
        self,
        x_origin: float,
        y_origin: float,
        vertical_degrees: float,
        horizontal_degrees: float,
    ):
        self.transformations.append(Skew(x_origin, y_origin, vertical_degrees, horizontal_degrees))


class Rotation:
    def __init__(self, x_origin: float, y_origin: float, degrees: float) -> None:
        self.x_origin = x_origin
        self.y_origin = y_origin
        self.degrees = degrees


class Skew:
    def __init__(
        self,
        x_origin: float,
        y_origin: float,
        vertical_degrees: float,
        horizontal_degrees: float,
    ) -> None:
        self.x_origin = x_origin
        self.y_origin = y_origin
        self.vertical_degrees = vertical_degrees
        self.horizontal_degrees = horizontal_degrees
