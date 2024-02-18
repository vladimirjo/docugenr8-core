from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from .word import Word


if TYPE_CHECKING:
    from .paragraph import Paragraph


class TextLine:
    def __init__(
        self,
        paragraph: None | Paragraph = None,
        left_indent: float = 0.0
        ) -> None:
        self.paragraph = paragraph
        self.left_indent = left_indent
        self.width = 0.0
        self.available_width = 0.0
        self._set_width_and_available_width()
        if self.paragraph is not None:
            self.h_align = self.paragraph.h_align
        else:
            self.h_align = ""
        self.words: deque[Word] = deque()
        self.height: float = 0.0
        self.height_dict: dict[float, int] = {}
        self.ascent: float = 0.0
        self.ascent_dict: dict[float, int] = {}
        self.prev_line: None | TextLine = None
        self.next_line: None | TextLine = None
        self.tabs: list[Word] = []
        self.leading: float = 0.0
        self.inner_spaces: list[Word] = []

    def _append_word_right(
        self,
        word: Word
        ) -> None:
        word.textline = self
        self.words.append(word)
        self._append_height(word.height)
        self._append_ascent(word.ascent)
        self._set_spaces_width_when_append_word_right(word)
        self._set_word_width_right(word)

    def _set_spaces_width_when_append_word_right(
        self,
        word: Word
        ) -> None:
        if word.chars in {"\n", " "}:
            return
        if word.prev_word is None:
            return
        if word.prev_word.textline != self:
            return
        if word.prev_word.chars != " ":
            return
        spaces: deque[Word] = deque()
        iterator = word.prev_word
        while iterator.chars == " " and self == iterator.textline:
            iterator.width = iterator._get_origin_width()
            self.inner_spaces.append(iterator)
            spaces.append(iterator)
            self.available_width -= iterator.width
            if iterator.prev_word is None:
                break
            iterator = iterator.prev_word
        # spaces at the start of a word will not be included in justifying
        if spaces[0] == self.words[0]:
            for space in spaces:
                self.inner_spaces.remove(space)
        return

    def _set_word_width_right(
        self,
        word: Word
        ) -> None:
        if word.chars == " ":
            word.width = 0.0
            return
        if word.is_extendable:
            word._extend_left()
            self.available_width -= word.width
            return
        if word.chars == "\n":
            return
        if word.chars == "\t":
            self.tabs.append(word)
            word.width = self._calc_tab_width(word)
            self.available_width -= word.width
            return

    def _append_word_left(
        self,
        word: Word
        ) -> None:
        word.textline = self
        self.words.appendleft(word)
        self._append_height(word.height)
        self._append_ascent(word.ascent)
        self._set_spaces_width_when_append_word_left(word)
        self._set_word_width_left(word)

    def _set_spaces_width_when_append_word_left(
        self,
        word: Word
        ) -> None:
        if word.chars in {"\n", " "}:
            return
        if word.next_word is None:
            return
        if word.next_word.textline != self:
            return
        if word.next_word.chars != " ":
            return
        spaces: deque[Word] = deque()
        iterator = word.next_word
        while iterator.chars == " " and self == iterator.textline:
            self.inner_spaces.append(iterator)
            spaces.append(iterator)
            if iterator.next_word is None:
                break
            iterator = iterator.next_word
        # spaces at the end of a line will not be included in justifying
        if spaces[-1] == self.words[-1]:
            for space in spaces:
                self.available_width += space.width
                space.width = 0.0
                self.inner_spaces.remove(space)
        return

    def _set_word_width_left(
        self,
        word: Word
        ) -> None:
        if word.chars == " ":
            word.width = word._get_origin_width()
            self.available_width -= word.width
            return
        if word.is_extendable:
            word._extend_right()
            self.available_width -= word.width
            return
        if word.chars == "\n":
            return
        if word.chars == "\t":
            self.tabs.append(word)
            self._recalculate_tab_widths()
            self.available_width -= word.width
            return

    def _split_word(
        self
        ) -> None:
        word = Word()
        textline = self.words[-1].textline
        first_fragment = self.words[-1].fragments[0]
        while word.width + first_fragment.width <= self.width:
            fragment = self.words[-1]._pop_fragment_left()
            word._add_fragment(fragment)
            first_fragment = self.words[-1].fragments[0]
        word.textline = textline
        if textline is not None:
            textline._append_ascent(word.ascent)
            textline._append_height(word.height)
        word.prev_word = self.words[-1].prev_word
        word.next_word = self.words[-1]
        self.words[-1].prev_word = word
        self.words.appendleft(word)

    def _can__move_first_word_from_next_line(
        self
        ) -> bool:
        if self.next_line is None:
            return False
        if len(self.next_line.words) == 0:
            return False
        first_word = self.next_line.words[0]
        if first_word.chars in {" ", "\n"}:
            return True
        word_width = 0.0
        if first_word.chars == "\t":
            word_width = self._calc_tab_width(first_word)
        else:
            word_width = first_word.width
        spaces_width = 0.0
        word_iterator = self.words[-1]
        while word_iterator.chars == " ":
            spaces_width += word_iterator._get_origin_width()
            if word_iterator.prev_word is None:
                break
            word_iterator = word_iterator.prev_word
        if (self.available_width - spaces_width - word_width) < 0.0:  # noqa: PLR2004
            return False
        return True

    def _move_last_word_to_next_line(
        self
        ) -> None:
        word = self._pop_word_right()
        if self.next_line is None:
            if self.paragraph is None:
                raise TypeError("Paragraph object is missing.")
            line = TextLine(self.paragraph, self.paragraph.left_indent)
            line.prev_line = self
            self.next_line = line
            self.paragraph.lines.append(line)
            leading_diff = self._set_leading()
            self.paragraph._change_height(leading_diff)
        self.next_line._append_word_left(word)

    def _move_first_word_from_next_line(
        self
        ) -> None:
        if self.next_line is None:
            raise TypeError("Next line object is missing.")
        word = self.next_line._pop_word_left()
        self._append_word_right(word)

    def _pop_word_right(
        self
        ) -> Word:
        last_word_in_line = self.words.pop()
        if len(self.words) == 0:
            self._remove_line()
        self._set_spaces_width_when_pop_word_right(last_word_in_line)
        last_word_in_line.textline = None
        self._remove_ascent(last_word_in_line.ascent)
        self._remove_height(last_word_in_line.height)
        if self.next_line is not None:
            self._set_leading()
        self.available_width += last_word_in_line.width
        return last_word_in_line

    def _set_spaces_width_when_pop_word_right(
        self,
        word: Word
        ) -> None:
        if word.prev_word is None:
            return
        if word.prev_word.textline != self:
            return
        if word.prev_word.chars != " ":
            return
        iterator = word.prev_word
        while iterator is not None and iterator.chars == " ":
            self.available_width += iterator.width
            iterator.width = 0.0
            if iterator in self.inner_spaces:
                self.inner_spaces.remove(iterator)
            iterator = iterator.prev_word

    def _pop_word_left(
        self
        ) -> Word:
        first_word_in_line = self.words.popleft()
        if len(self.words) == 0:
            self._remove_line()
        self._set_spaces_width_when_pop_word_left(first_word_in_line)
        self._recalculate_tab_widths()
        first_word_in_line.textline = None
        if first_word_in_line.chars in {" ", "\t"}:
            first_word_in_line.width = first_word_in_line._get_origin_width()
        self._remove_ascent(first_word_in_line.ascent)
        self._remove_height(first_word_in_line.height)
        if self.next_line is not None:
            self._set_leading()
        self.available_width += first_word_in_line.width
        return first_word_in_line

    def _set_spaces_width_when_pop_word_left(
        self,
        word: Word
        ) -> None:
        if word.next_word is None:
            return
        if word.next_word.textline != self:
            return
        if word.next_word.chars != " ":
            return
        iterator = word.next_word
        while iterator is not None and iterator.chars == " ":
            if iterator in self.inner_spaces:
                self.inner_spaces.remove(iterator)
            iterator = iterator.next_word

    def _remove_line_and_get_words(
        self
        ) -> deque[Word]:
        for word in self.words:
            if word._has_current_page_fragments:
                word._remove_page_number()
            if word._has_total_pages_fragments:
                word._remove_page_number()
            word._reset_all_stats()
        self._remove_line()
        return self.words

    def _is_first_line_in_paragraph(
        self
        ) -> bool:
        if self.paragraph is None:
            return False
        first_linked_paragraph = self.paragraph._get_first_linked_paragraph()
        return self == first_linked_paragraph.lines[0]

    def _is_last_line_in_paragraph(
        self
        ) -> bool:
        if self.paragraph is None:
            return False
        last_linked_paragraph = self.paragraph._get_last_linked_paragraph()
        return self == last_linked_paragraph.lines[-1]

    def _set_non_first_left_indent(
        self
        ) -> None:
        if self.paragraph is None:
            return
        width_diff = self.left_indent - self.paragraph.left_indent
        self.left_indent = self.paragraph.left_indent
        self.available_width += width_diff
        self.width += width_diff

    def _set_first_left_indent(
        self
        ) -> None:
        if self.paragraph is None:
            return
        width_diff = self.paragraph.first_line_indent - self.left_indent
        self.left_indent = self.paragraph.first_line_indent
        self.available_width -= width_diff
        self.width -= width_diff

    def _get_chars(
        self
        ) -> str:
        chars = ""
        for word in self.words:
            chars += word.chars
        return chars

    def _reallocate_words_in_line(
        self
        ) -> None:
        while self.available_width < 0.0:  # noqa: PLR2004
            if len(self.words) == 1:
                self._split_word()
            self._move_last_word_to_next_line()
        while self._can__move_first_word_from_next_line():
            self._move_first_word_from_next_line()

    def _append_height(
        self,
        height: float
        ) -> None:
        if height not in self.height_dict:
            self.height_dict[height] = 1
        else:
            self.height_dict[height] += 1
        height_diff = 0.0
        if height > self.height:
            height_diff = height - self.height
            self.height += height_diff
        if self.next_line is not None:
            leading_diff = self._set_leading()
            height_diff += leading_diff
        if height_diff != 0.0 and self.paragraph is not None:  # noqa: PLR2004
            self.paragraph._change_height(height_diff)

    def _append_ascent(
        self,
        ascent: float
        ) -> None:
        if ascent not in self.ascent_dict:
            self.ascent_dict[ascent] = 1
        else:
            self.ascent_dict[ascent] += 1
        if ascent > self.ascent:
            ascent_diff = ascent - self.ascent
            self.ascent += ascent_diff

    def _remove_height(
        self,
        height: float
        ) -> None:
        self.height_dict[height] -= 1
        if self.height_dict[height] > 0:
            return
        del self.height_dict[height]
        if len(self.height_dict) == 0:
            return
        if self.height != height:
            return
        height_diff = 0.0
        self.height = max(self.height_dict)
        height_diff = self.height - height
        if self.next_line is not None:
            leading_diff = self._set_leading()
            height_diff += leading_diff
        if self.paragraph is not None:
            self.paragraph._change_height(height_diff)

    def _remove_ascent(
        self,
        ascent: float
        ) -> None:
        self.ascent_dict[ascent] -= 1
        if self.ascent_dict[ascent] > 0:
            return
        del self.ascent_dict[ascent]
        if self.ascent != ascent:
            return
        if len(self.ascent_dict) == 0:
            self.ascent = 0.0
            return
        self.ascent = max(self.ascent_dict)

    def _remove_line(
        self
        ) -> None:
        height_to_remove = self.height
        if self.next_line is not None:
            height_to_remove += self.leading
            self.next_line.prev_line = self.prev_line
        if self.prev_line is not None:
            self.prev_line.next_line = self.next_line
            height_to_remove += self.prev_line._set_leading()
        self.leading = 0.0
        self.next_line = None
        self.prev_line = None
        if self.paragraph is None:
            raise ValueError("Missing Paragraph")
        self.paragraph.lines.remove(self)
        if len(self.paragraph.lines) == 0:
            height_to_remove += (
                self.paragraph.space_before + self.paragraph.space_after
            )
            if self.paragraph.textarea is not None:
                self.paragraph.textarea.paragraphs.remove(self.paragraph)
        self.paragraph._change_height(-height_to_remove)
        self.paragraph = None

    def _calc_line_width(
        self
        ) -> float:
        if self.paragraph is None:
            raise TypeError("Paragraph object is missing.")
        return (self.paragraph.width
                - self.left_indent
                - self.paragraph.right_indent)

    def _set_width_and_available_width(
        self
        ) -> None:
        width_diff = self._calc_line_width() - self.width
        self.width += width_diff
        self.available_width += width_diff

    def _calc_tab_width(
        self,
        word: Word
        ) -> float:
        if self.paragraph is None:
            raise ValueError("missing paragraph")
        tab_size = self.paragraph.tab_size
        width = 0.0
        while word.prev_word is not None:
            if word.textline != word.prev_word.textline:
                break
            if word.chars == " ":
                width += word.fragments[0].width
            width += word.prev_word.width
            word = word.prev_word
        return tab_size - (width % tab_size)

    def _recalculate_tab_widths(
        self
        ) -> None:
        for tab in self.tabs:
            tab.width = self._calc_tab_width(tab)

    def _calc_leading(
        self
        ) -> float:
        if self.paragraph is None:
            raise ValueError("Paragraph is missing")
        return (self.height * self.paragraph.line_height_ratio) - self.height

    def _set_leading(
        self
        ) -> float:
        if self.next_line is None:
            leading_diff = self.leading
            self.leading = 0.0
            return leading_diff
        leading_diff = self._calc_leading() - self.leading
        self.leading += leading_diff
        return leading_diff
