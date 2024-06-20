# from __future__ import annotations

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from docugenr8_shared.dto import DtoCurve
from docugenr8_shared.dto import DtoPoint
from docugenr8_shared.dto import DtoBezier

from docugenr8_core import Document

def test__create_curve_dto():
    doc = Document()
    doc.add_page(100, 100)
    curve1 = doc.create_curve(10, 10)
    doc.pages[0].add_content(curve1)
    dto = doc.build_dto()
    assert len(dto.pages[0].contents) == 1
    assert isinstance(dto.pages[0].contents[0], DtoCurve)

def test__create_curve_with_points():
    doc = Document()
    curve = doc.create_curve(10,10)
    curve.add_point(20, 20)
    curve.add_bezier(30, 30, 20, 20, 10, 10)
    path = curve._dto_curve._path
    assert len(path) == 3
    assert isinstance(path[0], DtoPoint)
    assert isinstance(path[1], DtoPoint)
    assert isinstance(path[2], DtoBezier)
    assert path[0]._x == 10
    assert path[0]._y == 10
