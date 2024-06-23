from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_core.document import Document

from docugenr8_shared.dto import DtoBezier
from docugenr8_shared.dto import DtoCurve
from docugenr8_shared.dto import DtoPoint
from docugenr8_shared.dto import DtoRectangle
from docugenr8_shared.dto import DtoArc
from docugenr8_shared.dto import DtoEllipse


class Curve:
    def __init__(self, x: float, y: float, doc: Document) -> None:
        self._dto_curve = DtoCurve(
            x,
            y,
            doc.settings.fill_color,
            doc.settings.line_color,
            doc.settings.line_width,
            doc.settings.line_pattern,
            doc.settings.line_closed,
        )

    def add_point(
        self,
        x: float,
        y: float,
    ) -> None:
        self._dto_curve._path.append(DtoPoint(x, y))

    def add_bezier(
        self,
        cp1_x: float,
        cp1_y: float,
        cp2_x: float,
        cp2_y: float,
        endp_x: float,
        endp_y: float,
    ) -> None:
        self._dto_curve._path.append(DtoBezier(cp1_x, cp1_y, cp2_x, cp2_y, endp_x, endp_y))


class Rectangle:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rotate: float,
        skew: float,
        rounded_corner_top_left: float,
        rounded_corner_top_right: float,
        rounded_corner_bottom_left: float,
        rounded_corner_bottom_right: float,
        doc: Document,
    ) -> None:
        self._dto_rectangle = DtoRectangle(
            x,
            y,
            width,
            height,
            rotate,
            skew,
            rounded_corner_top_left,
            rounded_corner_top_right,
            rounded_corner_bottom_left,
            rounded_corner_bottom_right,
            doc.settings.fill_color,
            doc.settings.line_color,
            doc.settings.line_width,
            doc.settings.line_pattern,
        )


class Arc:
    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        doc: Document,
    ) -> None:
        self._dto_arc = DtoArc(
            x1,
            y1,
            x2,
            y2,
            doc.settings.line_color,
            doc.settings.line_width,
            doc.settings.line_pattern,
        )


class Ellipse:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rotate: float,
        skew: float,
        doc: Document,
    ) -> None:
        self._dto_ellipse = DtoEllipse(
            x,
            y,
            width,
            height,
            rotate,
            skew,
            doc.settings.fill_color,
            doc.settings.line_color,
            doc.settings.line_width,
            doc.settings.line_pattern,
        )
