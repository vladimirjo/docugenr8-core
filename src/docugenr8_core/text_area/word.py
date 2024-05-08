from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .fragment import Fragment
    from .paragraph import Paragraph
    from .textline import TextLine
    from .word import Word


class Word:
    def __init__(self) -> None:
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
        self._current_page_fragments: list[Fragment] = []
        self._total_pages_fragments: list[Fragment] = []

    def _has_current_page_fragments(self) -> bool:
        if len(self._current_page_fragments) > 0:
            return True
        return False

    def _has_total_pages_fragments(self) -> bool:
        if len(self._total_pages_fragments) > 0:
            return True
        return False

    def _is_first_word_in_paragraph(self) -> bool:
        if self._textline is None:
            return False
        if self._textline._paragraph is None:
            return False
        first_linked_paragraph = self._textline._paragraph._get_first_linked_paragraph()
        return self == first_linked_paragraph._textlines[0]._words[0]

    def _is_last_word_in_paragraph(self) -> bool:
        if self._textline is None:
            return False
        if self._textline._paragraph is None:
            return False
        last_linked_paragraph = self._textline._paragraph._get_last_linked_paragraph()
        return self == last_linked_paragraph._textlines[-1]._words[-1]

    def _get_paragraph(self) -> Paragraph | None:
        if self._textline is None:
            return None
        return self._textline._paragraph

    def _remove_from_line(self) -> None:
        if self._textline is None:
            raise ValueError("Missing textline.")
        word_index = self._textline._words.index(self)
        self._textline._pop_word(word_index)

    def _add_page_number_to_textarea(self) -> None:
        if self._textline is None:
            return
        words_with_current_page_fragments = self._textline._paragraph._textarea._words_with_current_page_fragments
        words_with_total_pages_fragments = self._textline._paragraph._textarea._words_with_total_pages_fragments
        if self._has_current_page_fragments():
            words_with_current_page_fragments.append(self)
        if self._has_total_pages_fragments():
            words_with_total_pages_fragments.append(self)

    def _remove_page_number_from_textarea(self) -> None:
        if self._textline is None:
            return
        words_with_current_page_fragments = self._textline._paragraph._textarea._words_with_current_page_fragments
        words_with_total_pages_fragments = self._textline._paragraph._textarea._words_with_total_pages_fragments
        if self in words_with_current_page_fragments:
            words_with_current_page_fragments.remove(self)
        if self in words_with_total_pages_fragments:
            words_with_total_pages_fragments.remove(self)

    def _get_origin_width(self) -> float:
        width = 0.0
        for fragment in self._fragments:
            width += fragment._width
        return width

    def _append_height(self, height: float) -> None:
        if height not in self._height_dict:
            self._height_dict[height] = 1
        else:
            self._height_dict[height] += 1
        if height > self._height:
            height_diff = height - self._height
            self._height += height_diff
            if self._textline is not None:
                self._textline._append_height(self._height)

    def _append_ascent(self, ascent: float) -> None:
        if ascent not in self._ascent_dict:
            self._ascent_dict[ascent] = 1
        else:
            self._ascent_dict[ascent] += 1
        if ascent > self._ascent:
            ascent_diff = ascent - self._ascent
            self._ascent += ascent_diff
            if self._textline is not None:
                self._textline._append_ascent(self._ascent)

    def _remove_height(self, height: float) -> None:
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
                raise NotImplementedError("Needs implementation " "for removing height from " "a textline.")
            # height_diff = self.height - removed_height

    def _remove_ascent(self, ascent: float) -> None:
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
                raise NotImplementedError("Needs implementation " "for removing ascent from " "a textline.")
            # ascent_diff = self.ascent - removed_ascent

    def _add_fragment(self, fragment: Fragment) -> Word:
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

    def _pop_fragment_left(self) -> Fragment:
        first_fragment = self._fragments.popleft()
        first_fragment._word = None
        self._chars = self._chars[len(first_fragment._chars) :]
        self._width -= first_fragment._width
        self._remove_height(first_fragment._height)
        self._remove_ascent(first_fragment._ascent)
        return first_fragment

    def _pop_fragment(self, index: int) -> Fragment:
        if index < 0 or index > len(self._fragments):
            raise IndexError(f"Fragment index {index} is out of range in word.")
        fragment_to_remove = self._fragments[index]
        fragment_to_remove._word = None
        chars_left = self._chars[:index]
        chars_right = self._chars[index + 1 :]
        self._chars = chars_left + chars_right
        self._fragments.remove(fragment_to_remove)
        self._width -= fragment_to_remove._width
        self._remove_height(fragment_to_remove._height)
        self._remove_ascent(fragment_to_remove._ascent)
        if fragment_to_remove._is_current_page_dummy:
            self._current_page_fragments.remove(fragment_to_remove)
        if fragment_to_remove._is_total_pages_dummy:
            self._total_pages_fragments.remove(fragment_to_remove)
        return fragment_to_remove

    def _adjust_width_by_difference(self, width_diff: float) -> None:
        self._width += width_diff

    def _calc_width_with_justify(self) -> float:
        return self._width + self._justify_space

    def _is_from_textarea(
        self,
    ) -> bool:
        if self._get_paragraph() is not None:
            return True
        return False

    def _is_from_buffer(self) -> bool:
        if self._get_paragraph() is None:
            return True
        return False
