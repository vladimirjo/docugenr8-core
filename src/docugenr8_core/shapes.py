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
    def __init__(self, x: float, y: float, doc: Document) -> None:
        self.path: list[Point | Bezier] = [Point(x, y)]
        self.fill_color = doc.settings.fill_color
        self.line_color = doc.settings.line_color
        self.line_width = doc.settings.line_width
        self.line_pattern = doc.settings.line_pattern
        self.line_closed = doc.settings.line_closed
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
        rounded_corner_top_left: float,
        rounded_corner_top_right: float,
        rounded_corner_bottom_left: float,
        rounded_corner_bottom_right: float,
        doc: Document,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rounded_corner_top_left = rounded_corner_top_left
        self.rounded_corner_top_right = rounded_corner_top_right
        self.rounded_corner_bottom_left = rounded_corner_bottom_left
        self.rounded_corner_bottom_right = rounded_corner_bottom_right
        self.fill_color = doc.settings.fill_color
        self.line_color = doc.settings.line_color
        self.line_width = doc.settings.line_width
        self.line_pattern = doc.settings.line_pattern
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
        doc: Document,
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.line_color = doc.settings.line_color
        self.line_width = doc.settings.line_width
        self.line_pattern = doc.settings.line_pattern
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
        doc: Document,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = doc.settings.fill_color
        self.line_color = doc.settings.line_color
        self.line_width = doc.settings.line_width
        self.line_pattern = doc.settings.line_pattern
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
