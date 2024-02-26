from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from .word import Word


if TYPE_CHECKING:
    from .paragraph import Paragraph


class TextLine:
    def __init__(
        self,
        paragraph: Paragraph,
        ) -> None:
        self._paragraph = paragraph
        self._width = 0.0
        self._available_width = 0.0
        self._h_align = self._paragraph._h_align
        self._words: deque[Word] = deque()
        self._height: float = 0.0
        self._height_dict: dict[float, int] = {}
        self._ascent: float = 0.0
        self._ascent_dict: dict[float, int] = {}
        self._prev_line: None | TextLine = None
        self._next_line: None | TextLine = None
        self._tabs: list[Word] = []
        self._leading: float = 0.0
        self._inner_spaces: list[Word] = []

    def _append_word_right(
        self,
        word: Word
        ) -> None:
        word._textline = self
        self._words.append(word)
        self._append_height(word._height)
        self._append_ascent(word._ascent)
        self._set_spaces_width_when_append_word_right(word)
        self._set_word_width_right(word)

    def _set_spaces_width_when_append_word_right(
        self,
        word: Word
        ) -> None:
        if word._chars in {"\n", " "}:
            return
        if word._prev_word is None:
            return
        if word._prev_word._textline != self:
            return
        if word._prev_word._chars != " ":
            return
        spaces: deque[Word] = deque()
        iterator = word._prev_word
        while iterator._chars == " " and self == iterator._textline:
            iterator._width = iterator._get_origin_width()
            self._inner_spaces.append(iterator)
            spaces.append(iterator)
            self._available_width -= iterator._width
            if iterator._prev_word is None:
                break
            iterator = iterator._prev_word
        # spaces at the start of a word will not be included in justifying
        if spaces[0] == self._words[0]:
            for space in spaces:
                self._available_width += space._width
                space._width = 0.0
                self._inner_spaces.remove(space)
        return

    def _set_word_width_right(
        self,
        word: Word
        ) -> None:
        if word._chars == " ":
            word._width = 0.0
            return
        if word._is_extendable:
            word._extend_left()
            self._available_width -= word._width
            return
        if word._chars == "\n":
            return
        if word._chars == "\t":
            self._tabs.append(word)
            word._width = self._calc_tab_width(word)
            self._available_width -= word._width
            return

    def _append_word_left(
        self,
        word: Word
        ) -> None:
        word._textline = self
        self._words.appendleft(word)
        self._append_height(word._height)
        self._append_ascent(word._ascent)
        self._set_spaces_width_when_append_word_left(word)
        self._set_word_width_left(word)

    def _set_spaces_width_when_append_word_left(
        self,
        word: Word
        ) -> None:
        if word._chars in {"\n", " "}:
            return
        if word._next_word is None:
            return
        if word._next_word._textline != self:
            return
        if word._next_word._chars != " ":
            return
        spaces: deque[Word] = deque()
        iterator = word._next_word
        while iterator._chars == " " and self == iterator._textline:
            self._inner_spaces.append(iterator)
            spaces.append(iterator)
            if iterator._next_word is None:
                break
            iterator = iterator._next_word
        # spaces at the end of a line will not be included in justifying
        if spaces[-1] == self._words[-1]:
            for space in spaces:
                self._available_width += space._width
                space._width = 0.0
                self._inner_spaces.remove(space)
        return

    def _set_word_width_left(
        self,
        word: Word
        ) -> None:
        if word._chars == " ":
            word._width = word._get_origin_width()
            self._available_width -= word._width
            return
        if word._is_extendable:
            word._extend_right()
            self._available_width -= word._width
            return
        if word._chars == "\n":
            return
        if word._chars == "\t":
            self._tabs.append(word)
            self._recalculate_tab_widths()
            self._available_width -= word._width
            return

    def _split_word(
        self
        ) -> None:
        word = Word()
        textline = self._words[-1]._textline
        first_fragment = self._words[-1]._fragments[0]
        assert first_fragment._width < self._width, (
            "Fragment width exceeds text line width.")
        while word._width + first_fragment._width <= self._width:
            fragment = self._words[-1]._pop_fragment_left()
            word._add_fragment(fragment)
            first_fragment = self._words[-1]._fragments[0]
        word._textline = textline
        if textline is not None:
            textline._append_ascent(word._ascent)
            textline._append_height(word._height)
        word._prev_word = self._words[-1]._prev_word
        word._next_word = self._words[-1]
        self._words[-1]._prev_word = word
        self._words.appendleft(word)

    def _can_move_first_word_from_next_line(
        self
        ) -> bool:
        if self._next_line is None:
            return False
        if len(self._next_line._words) == 0:
            return False
        first_word = self._next_line._words[0]
        if first_word._chars in {" ", "\n"}:
            return True
        word_width = 0.0
        if first_word._chars == "\t":
            word_width = self._calc_tab_width(first_word)
        else:
            word_width = first_word._width
        spaces_width = 0.0
        word_iterator = self._words[-1]
        while word_iterator._chars == " ":
            spaces_width += word_iterator._get_origin_width()
            if word_iterator._prev_word is None:
                break
            word_iterator = word_iterator._prev_word
        if (self._available_width - spaces_width - word_width) < 0.0:  # noqa: PLR2004
            return False
        return True

    def _move_last_word_to_next_line(
        self
        ) -> None:
        word = self._pop_word_right()
        if self._next_line is None:
            self._paragraph._generate_textline()
            leading_diff = self._set_leading()
            self._paragraph._change_height(leading_diff)
        if self._next_line is None:
            raise ValueError("Next line is missing after generating new line.")
        self._next_line._append_word_left(word)

    def _move_first_word_from_next_line(
        self
        ) -> None:
        if self._next_line is None:
            raise TypeError("Next line object is missing.")
        word = self._next_line._pop_word_left()
        self._append_word_right(word)

    def _pop_word_right(
        self
        ) -> Word:
        last_word_in_line = self._words.pop()
        if len(self._words) == 0:
            self._remove_line()
        self._set_spaces_width_when_pop_word_right(last_word_in_line)
        last_word_in_line._textline = None
        self._remove_ascent(last_word_in_line._ascent)
        self._remove_height(last_word_in_line._height)
        if self._next_line is not None:
            self._set_leading()
        self._available_width += last_word_in_line._width
        return last_word_in_line

    def _set_spaces_width_when_pop_word_right(
        self,
        word: Word
        ) -> None:
        if word._prev_word is None:
            return
        if word._prev_word._textline != self:
            return
        if word._prev_word._chars != " ":
            return
        iterator = word._prev_word
        while iterator is not None and iterator._chars == " ":
            self._available_width += iterator._width
            iterator._width = 0.0
            if iterator in self._inner_spaces:
                self._inner_spaces.remove(iterator)
            iterator = iterator._prev_word

    def _pop_word_left(
        self
        ) -> Word:
        first_word_in_line = self._words.popleft()
        if len(self._words) == 0:
            self._remove_line()
        self._set_spaces_width_when_pop_word_left(first_word_in_line)
        self._recalculate_tab_widths()
        first_word_in_line._textline = None
        if first_word_in_line._chars in {" ", "\t"}:
            first_word_in_line._width = first_word_in_line._get_origin_width()
        self._remove_ascent(first_word_in_line._ascent)
        self._remove_height(first_word_in_line._height)
        if self._next_line is not None:
            self._set_leading()
        self._available_width += first_word_in_line._width
        return first_word_in_line

    def _set_spaces_width_when_pop_word_left(
        self,
        word: Word
        ) -> None:
        if word._next_word is None:
            return
        if word._next_word._textline != self:
            return
        if word._next_word._chars != " ":
            return
        iterator = word._next_word
        while iterator is not None and iterator._chars == " ":
            if iterator in self._inner_spaces:
                self._inner_spaces.remove(iterator)
            iterator = iterator._next_word

    def _remove_line_and_get_words(
        self
        ) -> deque[Word]:
        for word in self._words:
            if word._has_current_page_fragments:
                word._remove_page_number()
            if word._has_total_pages_fragments:
                word._remove_page_number()
            word._reset_all_stats()
        self._remove_line()
        return self._words

    def _is_first_line_in_paragraph(
        self
        ) -> bool:
        first_linked_paragraph = self._paragraph._get_first_linked_paragraph()
        return self == first_linked_paragraph._textlines[0]

    def _is_last_line_in_paragraph(
        self
        ) -> bool:
        last_linked_paragraph = self._paragraph._get_last_linked_paragraph()
        return self == last_linked_paragraph._textlines[-1]

    def _get_chars(
        self
        ) -> str:
        chars = ""
        for word in self._words:
            chars += word._chars
        return chars

    def _adjust_words_between_textlines(
        self
        ) -> None:
        if self._available_width < 0:
            if len(self._words) == 1:
                self._split_word()
            self._move_last_word_to_next_line()
            if self._available_width < 0:
                self._adjust_words_between_textlines()
        if self._can_move_first_word_from_next_line():
            self._move_first_word_from_next_line()
            if self._can_move_first_word_from_next_line():
                self._adjust_words_between_textlines()

    def _append_height(
        self,
        height: float
        ) -> None:
        if height not in self._height_dict:
            self._height_dict[height] = 1
        else:
            self._height_dict[height] += 1
        height_diff = 0.0
        if height > self._height:
            height_diff = height - self._height
            self._height += height_diff
        if self._next_line is not None:
            leading_diff = self._set_leading()
            height_diff += leading_diff
        if height_diff != 0.0:  # noqa: PLR2004
            self._paragraph._change_height(height_diff)

    def _append_ascent(
        self,
        ascent: float
        ) -> None:
        if ascent not in self._ascent_dict:
            self._ascent_dict[ascent] = 1
        else:
            self._ascent_dict[ascent] += 1
        if ascent > self._ascent:
            ascent_diff = ascent - self._ascent
            self._ascent += ascent_diff

    def _remove_height(
        self,
        height: float
        ) -> None:
        self._height_dict[height] -= 1
        if self._height_dict[height] > 0:
            return
        del self._height_dict[height]
        if len(self._height_dict) == 0:
            return
        if self._height != height:
            return
        height_diff = 0.0
        self._height = max(self._height_dict)
        height_diff = self._height - height
        if self._next_line is not None:
            leading_diff = self._set_leading()
            height_diff += leading_diff
        self._paragraph._change_height(height_diff)

    def _remove_ascent(
        self,
        ascent: float
        ) -> None:
        self._ascent_dict[ascent] -= 1
        if self._ascent_dict[ascent] > 0:
            return
        del self._ascent_dict[ascent]
        if self._ascent != ascent:
            return
        if len(self._ascent_dict) == 0:
            self._ascent = 0.0
            return
        self._ascent = max(self._ascent_dict)

    def _remove_line(
        self
        ) -> None:
        height_to_remove = self._height
        if self._next_line is not None:
            height_to_remove += self._leading
            self._next_line._prev_line = self._prev_line
        if self._prev_line is not None:
            self._prev_line._next_line = self._next_line
            height_to_remove += self._prev_line._set_leading()
        self._leading = 0.0
        self._next_line = None
        self._prev_line = None
        self._paragraph._textlines.remove(self)
        if len(self._paragraph._textlines) == 0:
            height_to_remove += (
                self._paragraph._space_before + self._paragraph._space_after
            )
            self._paragraph._textarea._paragraphs.remove(self._paragraph)
        self._paragraph._change_height(-height_to_remove)

    def _calc_tab_width(
        self,
        word: Word
        ) -> float:
        tab_size = self._paragraph._tab_size
        width = 0.0
        while word._prev_word is not None:
            if word._textline != word._prev_word._textline:
                break
            if word._chars == " ":
                width += word._fragments[0]._width
            width += word._prev_word._width
            word = word._prev_word
        return tab_size - (width % tab_size)

    def _recalculate_tab_widths(
        self
        ) -> None:
        for tab in self._tabs:
            tab._width = self._calc_tab_width(tab)

    def _calc_leading(
        self
        ) -> float:
        return ((self._height * self._paragraph._line_height_ratio)
                    - self._height)

    def _set_leading(
        self
        ) -> float:
        if self._next_line is None:
            leading_diff = self._leading
            self._leading = 0.0
            return leading_diff
        leading_diff = self._calc_leading() - self._leading
        self._leading += leading_diff
        return leading_diff

    def _set_width_and_available_space(
        self,
        width: float) -> None:
        width_diff = width - self._width
        self._width += width_diff
        self._available_width += width_diff
