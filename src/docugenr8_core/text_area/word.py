from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .fragment import Fragment
    from .paragraph import Paragraph
    from .text_line import TextLine
    from .word import Word

class Word:
    def __init__(
        self
        ) -> None:
        self._textline: None | TextLine = None
        self._fragments: deque[Fragment] = deque()
        self._chars = ""
        self._width = 0.0
        self._ascent = 0.0
        self._ascent_dict: dict[float, int] = {}
        self._height = 0.0
        self._height_dict: dict[float, int] = {}
        self._justify_space = 0.0
        self._is_extendable: bool = True
        self._should_render: bool = True
        self._prev_word: None | Word = None
        self._next_word: None | Word = None
        self._current_page_fragments: list[Fragment] = []
        self._total_pages_fragments: list[Fragment] = []

    def _remove_page_number(
        self
        ) -> None:
        if self._textline is None:
            return
        if self._textline._paragraph is None:
            return
        if self._textline._paragraph._textarea is None:
            return
        words_with_current_page_fragments = (
            self._textline._paragraph._textarea._words_with_current_page_fragments
        )
        words_with_total_pages_fragments = (
            self._textline._paragraph._textarea._words_with_total_pages_fragments
        )
        if self in words_with_current_page_fragments:
            words_with_current_page_fragments.remove(self)
        if self in words_with_total_pages_fragments:
            words_with_total_pages_fragments.remove(self)

    def _has_current_page_fragments(
        self
        ) -> bool:
        if len(self._current_page_fragments) > 0:
            return True
        return False

    def _has_total_pages_fragments(
        self
        ) -> bool:
        if len(self._total_pages_fragments) > 0:
            return True
        return False

    def _is_first_word_in_paragraph(
        self
        ) -> bool:
        if self._textline is None:
            return False
        if self._textline._paragraph is None:
            return False
        first_linked_paragraph = (
            self._textline._paragraph._get_first_linked_paragraph()
        )
        return self == first_linked_paragraph._textlines[0]._words[0]

    def _is_last_word_in_paragraph(
        self
        ) -> bool:
        if self._textline is None:
            return False
        if self._textline._paragraph is None:
            return False
        last_linked_paragraph = (
            self._textline._paragraph._get_last_linked_paragraph())
        return self == last_linked_paragraph._textlines[-1]._words[-1]

    def _get_paragraph(
        self
        ) -> Paragraph | None:
        if self._textline is None:
            return None
        return self._textline._paragraph

    def _remove_from_line(
        self
        ) -> None:
        if self._textline is None:
            raise ValueError("Missing textline.")
        textline = self._textline
        if self == textline._words[0]:
            textline._set_spaces_width_when_pop_word_left(self)
        if self == textline._words[-1]:
            textline._set_spaces_width_when_pop_word_right(self)
        textline._recalculate_tab_widths()
        textline._remove_ascent(self._ascent)
        textline._remove_height(self._height)
        textline._words.remove(self)
        textline._available_width += self._width
        if len(textline._words) == 0:
            textline._remove_line()
        self._textline = None

    def _get_origin_width(
        self
        ) -> float:
        width = 0.0
        for fragment in self._fragments:
            width += fragment._width
        return width

    def _reset_all_stats(
        self
        ) -> None:
        self._textline = None
        if self._chars in {" ", "\t"}:
            self._width = self._get_origin_width()

    def _append_height(
        self,
        height: float
        ) -> None:
        if height not in self._height_dict:
            self._height_dict[height] = 1
        else:
            self._height_dict[height] += 1
        if height > self._height:
            height_diff = height - self._height
            self._height += height_diff
            if self._textline is not None:
                self._textline._append_height(self._height)

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
            if self._textline is not None:
                self._textline._append_ascent(self._ascent)

    def _remove_height(
        self,
        height: float
        ) -> None:
        self._height_dict[height] -= 1
        if self._height_dict[height] > 0:
            return
        del self._height_dict[height]
        if len(self._height_dict) == 0:
            self._height = 0.0
            return
        if self._height == height:
            self._height = max(self._height_dict)
            if self._textline is not None:
                raise NotImplementedError("Needs implementation "
                                          "for removing height from "
                                          "a textline.")
            # height_diff = self.height - removed_height

    def _remove_ascent(
        self,
        ascent: float
        ) -> None:
        self._ascent_dict[ascent] -= 1
        if self._ascent_dict[ascent] > 0:
            return
        removed_ascent = self._ascent_dict.pop(ascent, None)
        if len(self._ascent_dict) == 0:
            self._ascent = 0.0
            return
        if self._ascent == removed_ascent:
            self._ascent = max(self._ascent_dict)
            if self._textline is not None:
                raise NotImplementedError("Needs implementation "
                                          "for removing ascent from "
                                          "a textline.")
            # ascent_diff = self.ascent - removed_ascent

    def _add_fragment(
        self,
        fragment: Fragment
        ) -> Word:
        fragment._word = self
        if fragment._chars in {" ", "\t", "\n"}:
            self._is_extendable = False
        if fragment._chars in {"\t", "\n"}:
            self._should_render = False
        self._fragments.append(fragment)
        self._adjust_width_by_difference(fragment._width)
        self._append_height(fragment._height)
        self._append_ascent(fragment._ascent)
        self._chars += fragment._chars
        if fragment._is_current_page_dummy:
            self._current_page_fragments.append(fragment)
        if fragment._is_total_pages_dummy:
            self._total_pages_fragments.append(fragment)
        return self

    def _pop_fragment_left(
        self
        ) -> Fragment:
        first_fragment = self._fragments.popleft()
        first_fragment._word = None
        self._chars = self._chars[len(first_fragment._chars) :]
        self._width -= first_fragment._width
        self._remove_height(first_fragment._height)
        self._remove_ascent(first_fragment._ascent)
        return first_fragment

    def _extend_right(
        self
        ) -> None:
        if self._next_word is None:
            return
        if self._next_word._is_extendable is False:
            return
        if self._next_word._textline != self._textline:
            return
        self._fragments.extend(self._next_word._fragments)
        self._chars += self._next_word._chars
        self._width += self._next_word._width
        for ascent in self._next_word._ascent_dict:
            if ascent in self._ascent_dict:
                self._ascent_dict[ascent] += 1
            else:
                self._ascent_dict[ascent] = 1
        if self._ascent < self._next_word._ascent:
            self._ascent = self._next_word._ascent
        for height in self._next_word._height_dict:
            if height in self._height_dict:
                self._height_dict[height] += 1
            else:
                self._height_dict[height] = 1
        if self._height < self._next_word._height:
            self._height = self._next_word._height
        # WHAT ABOUT ADJUSTING HEIGHT AND ASCEND IN TEXT LINE???????????
        word_to_remove = self._next_word
        self._next_word = self._next_word._next_word
        word_to_remove._prev_word = None
        word_to_remove._next_word = None
        word_to_remove._textline = None
        if self._textline is not None:
            self._textline._words.remove(word_to_remove)

    def _extend_left(
        self
        ) -> None:
        if self._prev_word is None:
            return
        if self._prev_word._is_extendable is False:
            return
        if self._prev_word._textline != self._textline:
            return
        self._prev_word._chars += self._chars
        self._prev_word._fragments.extend(self._fragments)
        self._prev_word._width += self._width
        for ascent in self._ascent_dict:
            if ascent in self._prev_word._ascent_dict:
                self._prev_word._ascent_dict[ascent] += self._ascent_dict[ascent]
            else:
                self._prev_word._ascent_dict[ascent] = self._ascent_dict[ascent]
        if self._prev_word._ascent < self._ascent:
            self._prev_word._ascent = self._ascent
        for height in self._height_dict:
            if height in self._prev_word._height_dict:
                self._prev_word._height_dict[height] += self._height_dict[height]
            else:
                self._prev_word._height_dict[height] = self._height_dict[height]
        if self._prev_word._height < self._height:
            self._prev_word._height = self._height
        # WHAT ABOUT ADJUSTING HEIGHT AND ASCEND IN TEXT LINE???????????
        word_to_remove = self
        self._prev_word._next_word = self._next_word
        word_to_remove._prev_word = None
        word_to_remove._next_word = None
        if self._textline is not None:
            self._textline._words.remove(word_to_remove)

    def _calculate_tab_width(
        self
        ) -> float:
        tab_size: float = 0.0
        if (self._textline is not None
                and self._textline._paragraph is not None
                    and self._textline._paragraph._textarea is not None):
            tab_size = (
                self._textline._paragraph._textarea._document.settings.text_tab_size
            )
        word = self
        width = 0.0
        while word._prev_word is not None:
            if word._textline != word._prev_word._textline:
                break
            width += word._prev_word._width
            word = word._prev_word
        return tab_size - (width % tab_size)

    def _adjust_width_by_difference(
        self,
        width_diff: float
        ) -> None:
        self._width += width_diff
        if self._textline is not None:
            self._textline._available_width -= width_diff
            self._textline._recalculate_tab_widths()

    def _calc_width_with_justify(
        self
        ) -> float:
        return self._width + self._justify_space
