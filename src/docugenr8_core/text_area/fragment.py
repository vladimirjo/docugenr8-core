from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable

    from .word import Word


class Fragment:
    def __init__(
        self,
        height: float,
        width: float,
        ascent: float,
        chars: str,
        font_name: str,
        font_size: float,
        font_color: tuple[int, int, int],
    ) -> None:
        self.height = height
        self.width = width
        self.ascent = ascent
        self.chars = chars
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.word: None | Word = None
        self.page_number_presentation: Callable[[int], str] | None = None
        self.is_current_page_dummy: bool = False
        self.is_total_pages_dummy: bool = False

    def adjust_width(
        self,
        new_width: float
        ) -> None:
        width_diff = new_width - self.width
        self.width += width_diff
        if self.word is not None:
            self.word._adjust_width_by_difference(width_diff)
