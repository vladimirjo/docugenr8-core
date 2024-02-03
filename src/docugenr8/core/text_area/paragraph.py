from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .text_area import TextArea
    from .word import Word

from .text_line import TextLine

class Paragraph:
    def __init__(self, textarea: TextArea) -> None:
        self.textarea = textarea
        self.width: float = textarea.width
        self.height: float = 0.0
        self.line_height_ratio: float = (
            textarea.document.settings.text_line_height_ratio
        )
        self.tab_size: float = textarea.document.settings.text_tab_size
        self.first_line_indent: float = (
            textarea.document.settings.paragraph_first_line_indent
        )
        self.hanging_indent: float = (
            textarea.document.settings.paragraph_hanging_indent
        )
        self.left_indent: float = (
            textarea.document.settings.paragraph_left_indent
        )
        self.right_indent: float = (
            textarea.document.settings.paragraph_right_indent
        )
        self.space_before: float = (
            textarea.document.settings.paragraph_space_before
        )
        self.space_after: float = (
            textarea.document.settings.paragraph_space_after
        )
        self.lines: list[TextLine] = []
        self.ends_with_br: bool = False
        self.next_linked_paragraph: None | Paragraph = None
        self.prev_linked_paragraph: None | Paragraph = None
        self.change_height(self.space_before + self.space_after)

    def _get_first_linked_paragraph(self) -> Paragraph:
        first_linked_paragraph = self
        while first_linked_paragraph.prev_linked_paragraph is not None:
            first_linked_paragraph = (
                first_linked_paragraph.prev_linked_paragraph
            )
        return first_linked_paragraph

    def _get_last_linked_paragraph(self) -> Paragraph:
        last_linked_paragraph = self
        while last_linked_paragraph.next_linked_paragraph is not None:
            last_linked_paragraph = last_linked_paragraph.next_linked_paragraph
        return last_linked_paragraph

    def _copy_paragraph_parameters_from(self, other_paragraph: Paragraph):
        self.line_height_ratio = other_paragraph.line_height_ratio
        self.tab_size = other_paragraph.tab_size
        self.first_line_indent = other_paragraph.first_line_indent
        self.hanging_indent = other_paragraph.hanging_indent
        self.left_indent = other_paragraph.left_indent
        self.right_indent = other_paragraph.right_indent
        height_diff = other_paragraph.space_before - self.space_before
        height_diff += other_paragraph.space_after - self.space_after
        self.space_before = other_paragraph.space_before
        self.space_after = other_paragraph.space_after
        self.change_height(height_diff)

    def _get_chars(self) -> str:
        chars = ""
        for line in self.lines:
            chars += line.get_chars()
        return chars

    def _reallocate_words_in_paragraph(self):
        if len(self.lines) == 0:
            return
        line = self.lines[0]
        while line is not None and line.next_line is not None:
            line.reallocate_words_in_line()
            line = line.next_line

    def change_height(self, height_diff: float) -> None:
        self.height += height_diff
        self.textarea.available_height -= height_diff

    def append_word_left(self, word: Word) -> None:
        self._textline_generator()
        if word.chars == "\n":
            self.ends_with_br = True
        self.lines[0].append_word_left(word)

    def append_word_right(self, word: Word) -> None:
        self._textline_generator()
        if word.chars == "\n":
            self.ends_with_br = True
        last_line = self.lines[-1]
        last_line.append_word_right(word)
        last_line.reallocate_words_in_line()

    def _textline_generator(self):
        if len(self.lines) != 0:
            return
        if self.prev_linked_paragraph is None:
            self.lines.append(TextLine(self, self.first_line_indent))
        else:
            self.lines.append(TextLine(self, self.left_indent))

    def pop_word_front_from_paragraph(self) -> Word:
        word_in_front = self.lines[0].pop_word_left()
        return word_in_front

    def pop_word_back_from_paragraph(self) -> Word:
        word_in_back = self.lines[-1].pop_word_right()
        return word_in_back

    def set_paragraph_width(self, width: float):
        width_diff = width - self.width
        self.width += width_diff
        for line in self.lines:
            line.set_length()
        self._reallocate_words_in_paragraph()
