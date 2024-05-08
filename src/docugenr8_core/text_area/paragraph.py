from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .textarea import TextArea
    from .word import Word

from .textline import TextLine


class Paragraph:
    def __init__(self, textarea: TextArea) -> None:
        self._textarea = textarea
        self._width: float = textarea._width
        self._height: float = 0.0
        self._space_before: float = textarea._document.settings.paragraph_space_before
        self._space_after: float = textarea._document.settings.paragraph_space_after
        self._change_height(self._space_before + self._space_after)
        self._line_height_ratio: float = textarea._document.settings.textline_height_ratio
        self._tab_size: float = textarea._document.settings.text_tab_size
        self._first_line_indent: float = textarea._document.settings.paragraph_first_line_indent
        self._hanging_indent: float = textarea._document.settings.paragraph_hanging_indent
        self._left_indent: float = textarea._document.settings.paragraph_left_indent
        self._right_indent: float = textarea._document.settings.paragraph_right_indent
        self._h_align: str = textarea._h_align
        self._textlines: list[TextLine] = []
        self._ends_with_br: bool = False
        self._next_linked_paragraph: None | Paragraph = None
        self._prev_linked_paragraph: None | Paragraph = None

    def _get_first_linked_paragraph(self) -> Paragraph:
        first_linked_paragraph = self
        while first_linked_paragraph._prev_linked_paragraph is not None:
            first_linked_paragraph = first_linked_paragraph._prev_linked_paragraph
        return first_linked_paragraph

    def _get_last_linked_paragraph(self) -> Paragraph:
        last_linked_paragraph = self
        while last_linked_paragraph._next_linked_paragraph is not None:
            last_linked_paragraph = last_linked_paragraph._next_linked_paragraph
        return last_linked_paragraph

    def _copy_paragraph_parameters_from(self, other_paragraph: Paragraph) -> None:
        self._line_height_ratio = other_paragraph._line_height_ratio
        self._tab_size = other_paragraph._tab_size
        self._first_line_indent = other_paragraph._first_line_indent
        self._hanging_indent = other_paragraph._hanging_indent
        self._left_indent = other_paragraph._left_indent
        self._right_indent = other_paragraph._right_indent
        height_diff = other_paragraph._space_before - self._space_before
        height_diff += other_paragraph._space_after - self._space_after
        self._space_before = other_paragraph._space_before
        self._space_after = other_paragraph._space_after
        self._change_height(height_diff)

    def _get_chars(self) -> str:
        chars = ""
        for line in self._textlines:
            chars += line._get_chars()
        return chars

    def _adjust_words_between_textlines(self) -> None:
        if len(self._textlines) == 0:
            return
        line = self._textlines[0]
        while line is not None and line._next is not None:
            line._adjust_words_between_textlines()
            line = line._next

    def _change_height(self, height_diff: float) -> None:
        self._height += height_diff
        self._textarea._available_height -= height_diff

    def _append_word_left(self, word: Word) -> None:
        if len(self._textlines) == 0:
            self._create_textline()
        if word._chars == "\n":
            self._ends_with_br = True
        self._textlines[0]._append_word(word, 0)

    def _append_word_right(self, word: Word) -> None:
        if len(self._textlines) == 0:
            self._create_textline()
        if word._chars == "\n":
            self._ends_with_br = True
        last_line = self._textlines[-1]
        last_line._append_word(word)
        last_line._adjust_words_between_textlines()

    def _create_textline(
        self,
        index: int | None = None,
    ) -> None:
        if index is None:
            index = len(self._textlines)
        if index < 0 or index > len(self._textlines):
            raise IndexError(f"Index {index} out of range in paragraph.")

        textline = TextLine(self)
        if self._prev_linked_paragraph is None and len(self._textlines) == 0:
            self._set_first_line_indent(textline)
        else:
            self._set_non_first_line_indent(textline)
        prev_textline = self._textlines[index - 1] if index > 0 else None
        next_textline = self._textlines[index + 1] if index < (len(self._textlines) - 1) else None
        self._textlines.insert(index, textline)
        textline._prev = prev_textline
        textline._next = next_textline
        if prev_textline is not None:
            prev_textline._next = textline
            prev_textline._set_leading()
        if next_textline is not None:
            next_textline._prev = textline

    def _set_non_first_line_indent(self, textline: TextLine) -> None:
        textline._set_width_and_available_space(
            self._width - self._left_indent - self._hanging_indent - self._right_indent
        )

    def _set_first_line_indent(self, textline: TextLine) -> None:
        textline._set_width_and_available_space(
            self._width - self._left_indent - self._first_line_indent - self._right_indent
        )

    def _pop_word_front_from_paragraph(self) -> Word:
        return self._textlines[0]._pop_word(0)

    def _pop_word_back_from_paragraph(self) -> Word:
        return self._textlines[-1]._pop_word(len(self._textlines[-1]._words) - 1)

    def _set_paragraph_width(self, new_width: float) -> None:
        width_diff = new_width - self._width
        self._width += width_diff
        for line in self._textlines:
            if line is self._textlines[0] and self._prev_linked_paragraph is None:
                self._set_first_line_indent(line)
            else:
                self._set_non_first_line_indent(line)
        self._adjust_words_between_textlines()

    def _get_first_word_from_next_textline(self, textline: TextLine) -> Word | None:
        if textline not in self._textlines:
            raise ValueError("Textline object is not present " "in parent paragraph object.")
        textline_index = self._textlines.index(textline)
        next_textline_index = textline_index + 1
        if next_textline_index > len(self._textlines):
            raise ValueError("Invalid index of the textline.")
        if next_textline_index == len(self._textlines):
            return None
        if len(self._textlines[next_textline_index]._words) == 0:
            return None
        return self._textlines[next_textline_index]._words[0]

    def _remove_paragraph_from_text_area(self) -> deque[Word]:
        removed_words = deque()
        while len(self._textlines) > 0:
            removed_words.extend(self._textlines[0]._remove_line_and_get_words())
        return removed_words
