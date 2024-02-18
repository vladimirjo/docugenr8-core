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
        self.textline: None | TextLine = None
        self.fragments: deque[Fragment] = deque()
        self.chars = ""
        self.width = 0.0
        self.ascent = 0.0
        self.ascent_dict: dict[float, int] = {}
        self.height = 0.0
        self.height_dict: dict[float, int] = {}
        self.justify_space = 0.0
        self.is_extendable: bool = True
        self.should_render: bool = True
        self.prev_word: None | Word = None
        self.next_word: None | Word = None
        self.current_page_fragments: list[Fragment] = []
        self.total_pages_fragments: list[Fragment] = []

    def _remove_page_number(
        self
        ) -> None:
        if self.textline is None:
            return
        if self.textline.paragraph is None:
            return
        if self.textline.paragraph.textarea is None:
            return
        words_with_current_page_fragments = (
            self.textline.paragraph.textarea.words_with_current_page_fragments
        )
        words_with_total_pages_fragments = (
            self.textline.paragraph.textarea.words_with_total_pages_fragments
        )
        if self in words_with_current_page_fragments:
            words_with_current_page_fragments.remove(self)
        if self in words_with_total_pages_fragments:
            words_with_total_pages_fragments.remove(self)

    def _has_current_page_fragments(
        self
        ) -> bool:
        if len(self.current_page_fragments) > 0:
            return True
        return False

    def _has_total_pages_fragments(
        self
        ) -> bool:
        if len(self.total_pages_fragments) > 0:
            return True
        return False

    def _is_first_word_in_paragraph(
        self
        ) -> bool:
        if self.textline is None:
            return False
        if self.textline.paragraph is None:
            return False
        first_linked_paragraph = (
            self.textline.paragraph._get_first_linked_paragraph()
        )
        return self == first_linked_paragraph.lines[0].words[0]

    def _is_last_word_in_paragraph(
        self
        ) -> bool:
        if self.textline is None:
            return False
        if self.textline.paragraph is None:
            return False
        last_linked_paragraph = (
            self.textline.paragraph._get_last_linked_paragraph())
        return self == last_linked_paragraph.lines[-1].words[-1]

    def _get_paragraph(
        self
        ) -> Paragraph | None:
        if self.textline is None:
            return None
        return self.textline.paragraph

    def _remove_from_line(
        self
        ) -> None:
        if self.textline is None:
            raise ValueError("Missing textline.")
        textline = self.textline
        if self == textline.words[0]:
            textline._set_spaces_width_when_pop_word_left(self)
        if self == textline.words[-1]:
            textline._set_spaces_width_when_pop_word_right(self)
        textline._recalculate_tab_widths()
        textline._remove_ascent(self.ascent)
        textline._remove_height(self.height)
        textline.words.remove(self)
        textline.available_width += self.width
        if len(textline.words) == 0:
            textline._remove_line()
        self.textline = None

    def _get_origin_width(
        self
        ) -> float:
        width = 0.0
        for fragment in self.fragments:
            width += fragment.width
        return width

    def _reset_all_stats(
        self
        ) -> None:
        self.textline = None
        if self.chars in {" ", "\t"}:
            self.width = self._get_origin_width()

    def _append_height(
        self,
        height: float
        ) -> None:
        if height not in self.height_dict:
            self.height_dict[height] = 1
        else:
            self.height_dict[height] += 1
        if height > self.height:
            height_diff = height - self.height
            self.height += height_diff
            if self.textline is not None:
                self.textline._append_height(self.height)

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
            if self.textline is not None:
                self.textline._append_ascent(self.ascent)

    def _remove_height(
        self,
        height: float
        ) -> None:
        self.height_dict[height] -= 1
        if self.height_dict[height] > 0:
            return
        del self.height_dict[height]
        if len(self.height_dict) == 0:
            self.height = 0.0
            return
        if self.height == height:
            self.height = max(self.height_dict)
            if self.textline is not None:
                raise NotImplementedError("Needs implementation "
                                          "for removing height from "
                                          "a textline.")
            # height_diff = self.height - removed_height

    def _remove_ascent(
        self,
        ascent: float
        ) -> None:
        self.ascent_dict[ascent] -= 1
        if self.ascent_dict[ascent] > 0:
            return
        removed_ascent = self.ascent_dict.pop(ascent, None)
        if len(self.ascent_dict) == 0:
            self.ascent = 0.0
            return
        if self.ascent == removed_ascent:
            self.ascent = max(self.ascent_dict)
            if self.textline is not None:
                raise NotImplementedError("Needs implementation "
                                          "for removing ascent from "
                                          "a textline.")
            # ascent_diff = self.ascent - removed_ascent

    def _add_fragment(
        self,
        fragment: Fragment
        ) -> Word:
        fragment.word = self
        if fragment.chars in {" ", "\t", "\n"}:
            self.is_extendable = False
        if fragment.chars in {"\t", "\n"}:
            self.should_render = False
        self.fragments.append(fragment)
        self._adjust_width_by_difference(fragment.width)
        self._append_height(fragment.height)
        self._append_ascent(fragment.ascent)
        self.chars += fragment.chars
        if fragment.is_current_page_dummy:
            self.current_page_fragments.append(fragment)
        if fragment.is_total_pages_dummy:
            self.total_pages_fragments.append(fragment)
        return self

    def _pop_fragment_left(
        self
        ) -> Fragment:
        first_fragment = self.fragments.popleft()
        first_fragment.word = None
        self.chars = self.chars[len(first_fragment.chars) :]
        self.width -= first_fragment.width
        self._remove_height(first_fragment.height)
        self._remove_ascent(first_fragment.ascent)
        return first_fragment

    def _extend_right(
        self
        ) -> None:
        if self.next_word is None:
            return
        if self.next_word.is_extendable is False:
            return
        if self.next_word.textline != self.textline:
            return
        self.fragments.extend(self.next_word.fragments)
        self.chars += self.next_word.chars
        self.width += self.next_word.width
        for ascent in self.next_word.ascent_dict:
            if ascent in self.ascent_dict:
                self.ascent_dict[ascent] += 1
            else:
                self.ascent_dict[ascent] = 1
        if self.ascent < self.next_word.ascent:
            self.ascent = self.next_word.ascent
        for height in self.next_word.height_dict:
            if height in self.height_dict:
                self.height_dict[height] += 1
            else:
                self.height_dict[height] = 1
        if self.height < self.next_word.height:
            self.height = self.next_word.height
        # WHAT ABOUT ADJUSTING HEIGHT AND ASCEND IN TEXT LINE???????????
        word_to_remove = self.next_word
        self.next_word = self.next_word.next_word
        word_to_remove.prev_word = None
        word_to_remove.next_word = None
        word_to_remove.textline = None
        if self.textline is not None:
            self.textline.words.remove(word_to_remove)

    def _extend_left(
        self
        ) -> None:
        if self.prev_word is None:
            return
        if self.prev_word.is_extendable is False:
            return
        if self.prev_word.textline != self.textline:
            return
        self.prev_word.chars += self.chars
        self.prev_word.fragments.extend(self.fragments)
        self.prev_word.width += self.width
        for ascent in self.ascent_dict:
            if ascent in self.prev_word.ascent_dict:
                self.prev_word.ascent_dict[ascent] += self.ascent_dict[ascent]
            else:
                self.prev_word.ascent_dict[ascent] = self.ascent_dict[ascent]
        if self.prev_word.ascent < self.ascent:
            self.prev_word.ascent = self.ascent
        for height in self.height_dict:
            if height in self.prev_word.height_dict:
                self.prev_word.height_dict[height] += self.height_dict[height]
            else:
                self.prev_word.height_dict[height] = self.height_dict[height]
        if self.prev_word.height < self.height:
            self.prev_word.height = self.height
        # WHAT ABOUT ADJUSTING HEIGHT AND ASCEND IN TEXT LINE???????????
        word_to_remove = self
        self.prev_word.next_word = self.next_word
        word_to_remove.prev_word = None
        word_to_remove.next_word = None
        if self.textline is not None:
            self.textline.words.remove(word_to_remove)

    def _calculate_tab_width(
        self
        ) -> float:
        tab_size: float = 0.0
        if (self.textline is not None
                and self.textline.paragraph is not None
                    and self.textline.paragraph.textarea is not None):
            tab_size = (
                self.textline.paragraph.textarea.document.settings.text_tab_size
            )
        word = self
        width = 0.0
        while word.prev_word is not None:
            if word.textline != word.prev_word.textline:
                break
            width += word.prev_word.width
            word = word.prev_word
        return tab_size - (width % tab_size)

    def _adjust_width_by_difference(
        self,
        width_diff: float
        ) -> None:
        self.width += width_diff
        if self.textline is not None:
            self.textline.width += width_diff
            self.textline.available_width -= width_diff
            self.textline._recalculate_tab_widths()

    def _calc_width_with_justify(
        self
        ) -> float:
        return self.width + self.justify_space
