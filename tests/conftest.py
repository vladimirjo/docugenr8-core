import pytest
from unittest.mock import MagicMock

from docugenr8 import Document
from docugenr8.font import Font

@pytest.fixture
def font1() -> Font:
    def font1_get_char_width(char, font_size):
        # Custom function to simulate getting character width
        if char in {"\t", "\n"}:
            return 0
        return 5

    def font1_get_ascent(
        font_size: float
        ) -> float:
        return 6

    def font1_get_descent(
        font_size: float
        ) -> float:
        return 4

    def font1_get_line_height(
        font_size,
        ) -> float:
        return 10

    font1 = MagicMock(spec=Font)
    font1.raw_data = bytes()
    font1._get_char_width.side_effect  = font1_get_char_width
    font1._get_ascent.side_effect  = font1_get_ascent
    font1._get_descent.side_effect  = font1_get_descent
    font1._get_line_height.side_effect  = font1_get_line_height
    font1.name = "font1"
    return font1

@pytest.fixture
def font2() -> Font:
    def font2_get_char_width(char, font_size):
        # Custom function to simulate getting character width
        if char in {"\t", "\n"}:
            return 0
        return 10

    def font2_get_ascent(
        font_size: float
        ) -> float:
        return 12

    def font2_get_descent(
        font_size: float
        ) -> float:
        return 8

    def font2_get_line_height(
        font_size,
        ) -> float:
        return 20
    font2 = MagicMock(spec=Font)
    font2.raw_data = bytes()
    font2._get_char_width.side_effect  = font2_get_char_width
    font2._get_ascent.side_effect  = font2_get_ascent
    font2._get_descent.side_effect  = font2_get_descent
    font2._get_line_height.side_effect  = font2_get_line_height
    font2.name = "font2"
    return font2

@pytest.fixture()
def doc_with_fonts(font1, font2):
    doc = Document()
    doc.fonts["font1"] = font1
    doc.fonts["font2"] = font2
    doc.settings.font_current = "font1"
    doc.settings.paragraph_first_line_indent = 0
    doc.settings.paragraph_hanging_indent = 0
    doc.settings.paragraph_left_indent = 0
    doc.settings.paragraph_right_indent = 0
    doc.settings.paragraph_space_after = 0
    doc.settings.paragraph_space_before = 0
    return doc
