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
        self._set_textline_indent()
        self._spaces_width_at_the_end = 0.0
        self._spaces_at_the_end: list[Word] = []
        self._h_align = self._paragraph._h_align
        self._words: deque[Word] = deque()
        self._height: float = 0.0
        self._height_dict: dict[float, int] = {}
        self._ascent: float = 0.0
        self._ascent_dict: dict[float, int] = {}
        self._prev: None | TextLine = None
        self._next: None | TextLine = None
        self._tabs: list[Word] = []
        self._leading: float = 0.0
        self._inner_spaces: list[Word] = []

    def _append_word(self, word: Word, index: int | None = None) -> None:
        if index is None:
            index = len(self._words)
        if index < 0 or index > len(self._words):
            raise IndexError(f"Index {index} out of range.")
        word._textline = self
        self._words.insert(index, word)
        self._append_height(word._height)
        self._append_ascent(word._ascent)
        self._set_available_width(word)
        self._set_spaces_width_at_the_end()
        self._set_tab_width_if_needed(word)
        self._merge_words_if_possible(word)

    def _pop_word(self, index: int | None = None) -> Word:
        if index is None:
            index = len(self._words) - 1
        if index < 0 or index > len(self._words) - 1:
            raise IndexError(f"Index {index} out of range.")
        word_to_remove = self._words[index]
        self._words.remove(word_to_remove)
        self._remove_ascent(word_to_remove._ascent)
        self._remove_height(word_to_remove._height)
        self._set_spaces_width_at_the_end()
        self._available_width += word_to_remove._width
        if word_to_remove in self._tabs:
            self._tabs.remove(word_to_remove)
        for tab in self._tabs:
            self._recalculate_tab_width(tab)
        word_to_remove._textline = None
        if len(self._words) == 0:
            self._remove_line()
        if self._next is not None:
            self._set_leading()
        return word_to_remove

    def _set_spaces_width_at_the_end(self) -> None:
        if len(self._words) == 0:
            return
        for word in reversed(self._words):
            if word._chars != " ":
                break
            if word not in self._spaces_at_the_end:
                self._spaces_at_the_end.append(word)
                self._spaces_width_at_the_end += word._width
                self._available_width += word._width
        if self._words[-1]._chars != " ":
            self._spaces_at_the_end.clear()
            self._available_width -= self._spaces_width_at_the_end
            self._spaces_width_at_the_end = 0

    def _set_available_width(self, word: Word) -> None:
        if word._chars == "\t":
            return
        self._available_width -= word._width

    def _set_tab_width_if_needed(self, word: Word) -> None:
        if word._chars == "\t" and word not in self._tabs:
            self._add_tab(word)
        for tab in self._tabs:
            self._recalculate_tab_width(tab)

    def _add_tab(self, word: Word) -> None:
        if len(self._tabs) == 0:
            self._tabs.append(word)
            return
        word_index_in_words = self._words.index(word)
        for tab in self._tabs:
            tab_index_in_words = self._words.index(tab)
            if word_index_in_words < tab_index_in_words:
                tab_index_in_tabs = self._tabs.index(tab)
                self._tabs.insert(tab_index_in_tabs, word)
                return
        self._tabs.append(word)

    def _recalculate_tab_width(self, tab: Word) -> None:
        old_tab_width = tab._width
        tab_size = self._paragraph._tab_size
        width = 0
        for word in self._words:
            if word == tab:
                break
            width += word._width
        tab._width = tab_size - (width % tab_size)
        self._available_width = self._available_width + old_tab_width - tab._width

    def _test_tab_width(self) -> float:
        tab_size = self._paragraph._tab_size
        width = 0
        for word in self._words:
            width += word._width
        return tab_size - (width % tab_size)

    def _merge_words_if_possible(self, word: Word) -> None:
        if len(self._words) == 1:
            return
        if not word._is_extendable:
            return
        word_index = self._words.index(word)
        word_index_before = word_index - 1
        if word_index_before >= 0 and self._words[word_index_before]._is_extendable:
            self._merge_words(self._words[word_index_before], self._words[word_index])
            word_index -= 1
        word_index_after = word_index + 1
        if word_index_after < len(self._words) and self._words[word_index_after]._is_extendable:
            self._merge_words(self._words[word_index], self._words[word_index_after])

    def _merge_words(self, word_left: Word, word_right: Word) -> None:
        if not word_left._is_extendable or not word_right._is_extendable:
            return
        new_word = Word()
        for fragment in word_left._fragments:
            new_word._add_fragment(fragment)
        for fragment in word_right._fragments:
            new_word._add_fragment(fragment)
        index = self._words.index(word_left)
        self._words.insert(index, new_word)
        new_word._textline = word_left._textline
        new_word._add_page_number_to_textarea()
        textline = new_word._textline
        if textline is None:
            raise ValueError("Textline is not present.")
        textline._append_ascent(new_word._ascent)
        textline._append_height(new_word._height)

        textline._remove_ascent(word_left._ascent)
        textline._remove_ascent(word_right._ascent)
        textline._remove_height(word_left._height)
        textline._remove_height(word_right._height)

        word_left._remove_page_number_from_textarea()
        word_right._remove_page_number_from_textarea()
        self._words.remove(word_left)
        self._words.remove(word_right)

    # split word takes another paramether:
    # width to split the first part of the word
    def _split_word(
        self,
        right_word: Word,
        left_width_to_split: float,
    ) -> None:
        if right_word not in self._words:
            raise IndexError(f"Word {right_word._chars} " f"is not present in Textline {self._get_chars()}.")
        left_word = Word()
        while left_word._width + right_word._fragments[0]._width <= left_width_to_split:
            first_fragment = right_word._pop_fragment(0)
            left_word._add_fragment(first_fragment)
        if left_word._width == 0:
            return
        left_word._textline = self
        word_index = self._words.index(right_word)
        self._words.insert(word_index, left_word)
        right_word._remove_page_number_from_textarea()
        left_word._add_page_number_to_textarea()
        right_word._add_page_number_to_textarea()
        self._append_ascent(right_word._ascent)
        self._append_height(right_word._height)

    def _can_move_first_word_from_next_line(self) -> bool:
        first_word = self._paragraph._get_first_word_from_next_textline(self)
        if first_word is None:
            return False
        if first_word._chars in {" ", "\n"}:
            return True
        word_width = 0.0
        if first_word._chars == "\t":
            word_width = self._test_tab_width()
        else:
            word_width = first_word._width
        if (self._available_width - self._spaces_width_at_the_end - word_width) < 0:
            return False
        return True

    def _push_exceeded_words_to_next_textline(self) -> None:
        removed_words = deque()
        while self._available_width < 0:
            removed_words.appendleft(self._pop_word())
        if self._next is None:
            self._paragraph._create_textline()
            self._set_leading()
        if self._next is not None:
            while len(removed_words) > 0:
                self._next._append_word(removed_words.pop(), 0)

    def _remove_line_and_get_words(
        self,
    ) -> deque[Word]:
        removed_words = deque()
        while len(self._words) > 0:
            self._words[0]._remove_page_number_from_textarea()
            removed_word = self._pop_word(0)
            removed_words.append(removed_word)
        return removed_words

    def _is_first_line_in_paragraph(self) -> bool:
        first_linked_paragraph = self._paragraph._get_first_linked_paragraph()
        return self == first_linked_paragraph._textlines[0]

    def _is_last_line_in_paragraph(self) -> bool:
        last_linked_paragraph = self._paragraph._get_last_linked_paragraph()
        return self == last_linked_paragraph._textlines[-1]

    def _get_chars(self) -> str:
        chars = ""
        for word in self._words:
            chars += word._chars
        return chars

    def _adjust_words_between_textlines(self) -> None:
        if self._word_width_exceeds_texline_width():
            return
        if self._available_width < 0:
            self._push_exceeded_words_to_next_textline()
        self._pull_available_words_from_next_line()

    def _word_width_exceeds_texline_width(
        self,
    ) -> bool:
        if self._paragraph._textarea._document.settings.text_split_words and self._words[0]._width > self._width:
            self._split_word(self._words[0], self._width)
        if self._words[0]._width > self._width:
            textline_index = self._paragraph._textlines.index(self)
            paragraph_index = self._paragraph._textarea._paragraphs.index(self._paragraph)
            self._paragraph._textarea._empty_textlines_and_paragraphs_from_line(textline_index, paragraph_index)
            self._paragraph._textarea._state_textline_width_overflow = True
            return True
        return False

    def _pull_available_words_from_next_line(self) -> None:
        while self._can_move_first_word_from_next_line():
            if self._next is None:
                raise ValueError("Next textline is not present.")
            self._append_word(self._next._pop_word(0))

    def _append_height(self, height: float) -> None:
        if height not in self._height_dict:
            self._height_dict[height] = 1
        else:
            self._height_dict[height] += 1
        if height <= self._height:
            return
        height_diff = height - self._height
        self._height += height_diff
        if self._next is not None:
            self._set_leading()
        self._paragraph._change_height(height_diff)

    def _append_ascent(self, ascent: float) -> None:
        if ascent not in self._ascent_dict:
            self._ascent_dict[ascent] = 1
        else:
            self._ascent_dict[ascent] += 1
        if ascent > self._ascent:
            ascent_diff = ascent - self._ascent
            self._ascent += ascent_diff

    def _remove_height(self, height: float) -> None:
        self._height_dict[height] -= 1
        if self._height_dict[height] > 0:
            return
        del self._height_dict[height]
        if len(self._height_dict) == 0:
            # ???????
            return
        if self._height != height:
            return
        self._height = max(self._height_dict)
        height_diff = self._height - height
        if self._next is not None:
            self._set_leading()
        self._paragraph._change_height(height_diff)

    def _remove_ascent(self, ascent: float) -> None:
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

    def _remove_line(self) -> None:
        height_to_remove = self._height + self._leading
        if self._next is not None:
            self._next._prev = self._prev
        if self._prev is not None:
            self._prev._next = self._next
            self._prev._set_leading()
        self._leading = 0.0
        self._next = None
        self._prev = None
        paragraph = self._paragraph
        paragraph._textlines.remove(self)
        paragraph._change_height(-height_to_remove)
        if len(paragraph._textlines) == 0:
            textarea = paragraph._textarea
            textarea._available_height -= paragraph._space_before + paragraph._space_after
            textarea._paragraphs.remove(paragraph)

    def _calculate_leading(self) -> float:
        return (self._height * self._paragraph._line_height_ratio) - self._height

    def _set_leading(self) -> None:
        leading_diff = 0
        if self._next is None:
            leading_diff = -self._leading
            self._leading = 0
        else:
            leading_diff = self._calculate_leading() - self._leading
            self._leading += leading_diff
        self._paragraph._change_height(leading_diff)

    def _set_width_and_available_space(self, width: float) -> None:
        width_diff = width - self._width
        self._width += width_diff
        self._available_width += width_diff

    def _set_textline_indent(
        self,
    ) -> None:
        if self._paragraph._prev_linked_paragraph is None and len(self._paragraph._textlines) == 0:
            self._set_width_and_available_space(
                self._paragraph._width
                - self._paragraph._left_indent
                - self._paragraph._first_line_indent
                - self._paragraph._right_indent
            )
        else:
            self._set_width_and_available_space(
                self._paragraph._width
                - self._paragraph._left_indent
                - self._paragraph._hanging_indent
                - self._paragraph._right_indent
            )
