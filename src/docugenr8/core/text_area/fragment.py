from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Callable


if TYPE_CHECKING:
    from ..font import Font
    from .word import Word


class Fragment:
    def __init__(
        self,
        chars: str,
        font: Font,
        font_size: float,
        font_color: tuple[int, int, int],
    ) -> None:
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.chars = chars
        self.length = 0.0
        self.word: None | Word = None
        self.page_number_presentation: Callable[[int], str] | None = None
        self.is_current_page_dummy: bool = False
        self.is_total_pages_dummy: bool = False
        for char in chars:
            self.length += self.font.get_char_width(
                char, self.font_size
            )
        self.ascent = self.font.get_ascent(self.font_size)
        self.height = self.font.get_line_height(self.font_size)

    def change_length(self, new_length: float) -> None:
        length_diff = new_length - self.length
        self.length += length_diff
        if self.word is not None:
            self.word.change_length(length_diff)

    def set_page_number_presentation_and_length(
        self,
        num_of_digits: int,
        presentation: Callable[[int], str]
    ) -> None:
        self.page_number_presentation = presentation
        self.length = num_of_digits * self.font.get_char_width(
            "0", self.font_size
        )


    def inject_page_number(self, page_number: int):
        if self.page_number_presentation is None:
            return
        chars = self.page_number_presentation(page_number)
        new_length = 0.0

        for char in chars:
            new_length += self.font.get_char_width(
                char, self.font_size
            )

        self.change_length(new_length)
        if self.word is not None and self.word.textline is not None and self.word.textline.paragraph is not None:
            self.word.textline.paragraph._reallocate_words_in_paragraph()
            self.word.textline.paragraph.textarea.move_words_between_textareas_and_buffer()
