from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .text_area import TextArea
    from .word import Word

from .text_line import TextLine


class Paragraph:
    def __init__(
        self,
        textarea: None | TextArea = None
        ) -> None:
        self.textarea = textarea
        if textarea is not None:
            self.width: float = textarea.width
            self.height: float = 0.0
            self.line_height_ratio: float = (
                textarea.document.settings.text_line_height_ratio)
            self.tab_size: float = textarea.document.settings.text_tab_size
            self.first_line_indent: float = (
                textarea.document.settings.paragraph_first_line_indent)
            self.hanging_indent: float = (
                textarea.document.settings.paragraph_hanging_indent)
            self.left_indent: float = (
                textarea.document.settings.paragraph_left_indent)
            self.right_indent: float = (
                textarea.document.settings.paragraph_right_indent)
            self.space_before: float = (
                textarea.document.settings.paragraph_space_before)
            self.space_after: float = (
                textarea.document.settings.paragraph_space_after)
            self.h_align: str = textarea.h_align
        else:
            self.width: float = 0.0
            self.height: float = 0.0
            self.line_height_ratio: float = 0.0
            self.tab_size: float = 0.0
            self.first_line_indent: float = 0.0
            self.hanging_indent: float = 0.0
            self.left_indent: float = 0.0
            self.right_indent: float = 0.0
            self.space_before: float = 0.0
            self.space_after: float = 0.0
            self.h_align: str = ""
        self.lines: list[TextLine] = []
        self.ends_with_br: bool = False
        self.next_linked_paragraph: None | Paragraph = None
        self.prev_linked_paragraph: None | Paragraph = None
        self._change_height(self.space_before + self.space_after)

    def _get_first_linked_paragraph(
        self
        ) -> Paragraph:
        first_linked_paragraph = self
        while first_linked_paragraph.prev_linked_paragraph is not None:
            first_linked_paragraph = (
                first_linked_paragraph.prev_linked_paragraph)
        return first_linked_paragraph

    def _get_last_linked_paragraph(
        self
        ) -> Paragraph:
        last_linked_paragraph = self
        while last_linked_paragraph.next_linked_paragraph is not None:
            last_linked_paragraph = last_linked_paragraph.next_linked_paragraph
        return last_linked_paragraph

    def _copy_paragraph_parameters_from(
        self,
        other_paragraph: Paragraph
        ) -> None:
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
        self._change_height(height_diff)

    def _get_chars(
        self
        ) -> str:
        chars = ""
        for line in self.lines:
            chars += line._get_chars()
        return chars

    def _reallocate_words_in_paragraph(
        self
        ) -> None:
        if len(self.lines) == 0:
            return
        line = self.lines[0]
        while line is not None and line.next_line is not None:
            line._reallocate_words_in_line()
            line = line.next_line

    def _change_height(
        self,
        height_diff: float
        ) -> None:
        self.height += height_diff
        if self.textarea is not None:
            self.textarea.available_height -= height_diff

    def _append_word_left(
        self,
        word: Word
        ) -> None:
        self._generate_textline()
        if word.chars == "\n":
            self.ends_with_br = True
        self.lines[0]._append_word_left(word)

    def _append_word_right(
        self,
        word: Word
        ) -> None:
        self._generate_textline()
        if word.chars == "\n":
            self.ends_with_br = True
        last_line = self.lines[-1]
        last_line._append_word_right(word)
        last_line._reallocate_words_in_line()

    def _generate_textline(
        self
        ) -> None:
        if len(self.lines) != 0:
            return
        if self.prev_linked_paragraph is None:
            self.lines.append(TextLine(self, self.first_line_indent))
        else:
            self.lines.append(TextLine(self, self.left_indent))

    def _pop_word_front_from_paragraph(
        self
        ) -> Word:
        return self.lines[0]._pop_word_left()

    def _pop_word_back_from_paragraph(
        self
        ) -> Word:
        return self.lines[-1]._pop_word_right()

    def _set_paragraph_width(
        self,
        width: float
        ) -> None:
        width_diff = width - self.width
        self.width += width_diff
        for line in self.lines:
            line._set_width_and_available_width()
        self._reallocate_words_in_paragraph()
