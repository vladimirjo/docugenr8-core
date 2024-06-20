from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_core.document import Document

from docugenr8_shared.dto import DtoCurve


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
        self._dto_curve.add_point(x, y)

    def add_bezier(
        self,
        cp1_x: float,
        cp1_y: float,
        cp2_x: float,
        cp2_y: float,
        endp_x: float,
        endp_y: float,
    ) -> None:
        self._dto_curve.add_bezier(cp1_x, cp1_y, cp2_x, cp2_y, endp_x, endp_y)
