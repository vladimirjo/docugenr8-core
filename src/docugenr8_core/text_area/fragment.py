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
        self._height = height
        self._width = width
        self._ascent = ascent
        self._chars = chars
        self._font_name = font_name
        self._font_size = font_size
        self._font_color = font_color
        self._word: None | Word = None
        self._page_number_presentation: Callable[[int], str] | None = None
        self._is_current_page_dummy: bool = False
        self._is_total_pages_dummy: bool = False

    def _adjust_width(self, new_width: float) -> None:
        width_diff = new_width - self._width
        self._width += width_diff
        if self._word is not None:
            self._word._adjust_width_by_difference(width_diff)
