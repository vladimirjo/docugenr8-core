"""_summary_."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_core.document import Document

from docugenr8_core.text_area import TextArea


class TextBox:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        document: Document,
    ) -> None:
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._fill_color = document.settings.fill_color
        self._line_color = document.settings.line_color
        self._line_width = document.settings.line_width
        self._line_pattern = document.settings.line_pattern
        self._padding_left = document.settings.textbox_padding_left
        self._padding_right = document.settings.textbox_padding_right
        self._padding_top = document.settings.textbox_padding_top
        self._padding_bottom = document.settings.textbox_padding_bottom
        self._margin_left = document.settings.textbox_margin_left
        self._margin_right = document.settings.textbox_margin_right
        self._margin_top = document.settings.textbox_margin_top
        self._margin_bottom = document.settings.textbox_margin_bottom
        self._text_area = TextArea(
            self._get_textarea_x(),
            self._get_textarea_y(),
            self._get_textarea_width(),
            self._get_textarea_height(),
            document,
        )

    def _get_textarea_x(self) -> float:
        return self._x + self._margin_left + self._padding_left

    def _get_textarea_y(self) -> float:
        return self._y + self._margin_top + self._padding_top

    def _get_textarea_width(self) -> float:
        return self._width - (self._margin_left + self._padding_left) - (self._margin_right + self._padding_right)

    def _get_textarea_height(self) -> float:
        return self._height - (self._margin_top + self._padding_top) - (self._margin_bottom + self._padding_bottom)

    def add_text(self, unicode_text: str) -> None:
        self._text_area.add_text(unicode_text)
