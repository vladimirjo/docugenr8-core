from __future__ import annotations
from typing import TYPE_CHECKING
from collections import deque


if TYPE_CHECKING:
    from .word import Word
    from .text_line import TextLine
    from .fragment import Fragment
    from .paragraph import Paragraph

class Word:
    def __init__(self, textline: None | TextLine = None) -> None:
        self.textline = textline
        self.fragments: deque[Fragment] = deque()
        self.chars = ""
        self.length = 0.0
        self.ascent = 0.0
        self.ascent_dict: dict[float, int] = {}
        self.height = 0.0
        self.height_dict: dict[float, int] = {}
        self.justify_space = 0.0
        self.accepts_additional_fragments: bool = True
        self.prev_word: None | Word = None
        self.next_word: None | Word = None
        self.current_page_fragments: list[Fragment] = []
        self.total_pages_fragments: list[Fragment] = []

    def remove_page_number(self):
        if self.textline is None:
            return
        if self.textline.paragraph is None:
            return
        if self.textline.paragraph.textarea is None:
            return
        words_with_current_page_fragments = (
            self.textline.paragraph.textarea.words_with_current_page_fragments)
        words_with_total_pages_fragments = (
            self.textline.paragraph.textarea.words_with_total_pages_fragments)
        if (self in words_with_current_page_fragments):
            words_with_current_page_fragments.remove(self)
        if (self in words_with_total_pages_fragments):
           words_with_total_pages_fragments.remove(self)

    def has_current_page_fragments(self):
        if len(self.current_page_fragments) > 0:
            return True
        return False

    def has_total_pages_fragments(self):
        if len(self.total_pages_fragments) > 0:
            return True
        return False

    def is_first_word_in_paragraph(self) -> bool:
        if self.textline is None:
            return False
        if self.textline.paragraph is None:
            return False
        first_linked_paragraph = (
            self.textline.paragraph._get_first_linked_paragraph()
        )
        if self == first_linked_paragraph.lines[0].words[0]:
            return True
        else:
            return False

    def is_last_word_in_paragraph(self) -> bool:
        if self.textline is None:
            return False
        if self.textline.paragraph is None:
            return False
        last_linked_paragraph = (
            self.textline.paragraph._get_last_linked_paragraph()
        )
        if self == last_linked_paragraph.lines[-1].words[-1]:
            return True
        else:
            return False

    def get_paragraph(self) -> Paragraph | None:
        if self.textline is None:
            return None
        return self.textline.paragraph

    def remove_from_line(self):
        textline = self.textline
        if textline is None:
            raise ValueError("Missing textline")
        if self == textline.words[0]:
            textline.set_spaces_length_when_pop_word_left(self)
        if self == textline.words[-1]:
            textline.set_spaces_length_when_pop_word_right(self)
        textline.recalc_tab_lengths()
        textline.remove_ascent(self.ascent)
        textline.remove_height(self.height)
        textline.words.remove(self)
        if len(textline.words) == 0:
            textline.remove_line()
        self.textline = None
        textline.available_length += self.length
        return

    def get_origin_length(self) -> float:
        length = 0.0
        for fragment in self.fragments:
            length += fragment.length
        return length

    def reset_all_stats(self):
        self.textline = None
        if self.chars in {" ", "\t"}:
            self.length = self.get_origin_length()
            # self.reset_length()
        # self.next_word = None
        # self.prev_word = None

    def append_height(self, height: float):
        if height not in self.height_dict:
            self.height_dict[height] = 1
        else:
            self.height_dict[height] += 1
        if height > self.height:
            height_diff = height - self.height
            self.height += height_diff
            if self.textline is not None:
                self.textline.append_height(self.height)

    def append_ascent(self, ascent: float):
        if ascent not in self.ascent_dict:
            self.ascent_dict[ascent] = 1
        else:
            self.ascent_dict[ascent] += 1
        if ascent > self.ascent:
            ascent_diff = ascent - self.ascent
            self.ascent += ascent_diff
            if self.textline is not None:
                self.textline.append_ascent(self.ascent)

    def remove_height(self, height: float):
        self.height_dict[height] -= 1
        if self.height_dict[height] > 0:
            return
        del self.height_dict[height]
        if len(self.height_dict) == 0:
            self.height = 0.0
            return
        if self.height == height:
            self.height = max(self.height_dict)
            # height_diff = self.height - removed_height

    def remove_ascent(self, ascent: float):
        self.ascent_dict[ascent] -= 1
        if self.ascent_dict[ascent] > 0:
            return
        removed_ascent = self.ascent_dict.pop(ascent, None)
        if len(self.ascent_dict) == 0:
            self.ascent = 0.0
            return
        if self.ascent == removed_ascent:
            self.ascent = max(self.ascent_dict)
            # ascent_diff = self.ascent - removed_ascent

    def add_fragment(self, fragment: Fragment) -> Word:
        fragment.word = self
        if fragment.chars in {" ", "\t", "\n"}:
            self.accepts_additional_fragments = False
        self.fragments.append(fragment)
        self.change_length(fragment.length)
        self.append_height(fragment.height)
        self.append_ascent(fragment.ascent)
        self.chars += fragment.chars
        if fragment.is_current_page_dummy:
            self.current_page_fragments.append(fragment)
        if fragment.is_total_pages_dummy:
            self.total_pages_fragments.append(fragment)
        return self

    def pop_fragment_left(self) -> Fragment:
        first_fragment = self.fragments.popleft()
        first_fragment.word = None
        self.chars = self.chars[len(first_fragment.chars) :]
        self.length -= first_fragment.length
        self.remove_height(first_fragment.height)
        self.remove_ascent(first_fragment.ascent)
        return first_fragment

    def extend_right(self):
        if self.next_word is None:
            return
        if self.next_word.accepts_additional_fragments == False:
            return
        if self.next_word.textline != self.textline:
            return
        self.fragments.extend(self.next_word.fragments)
        self.chars += self.next_word.chars
        self.length += self.next_word.length
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
        word_to_remove = self.next_word
        self.next_word = self.next_word.next_word
        word_to_remove.prev_word = None
        word_to_remove.next_word = None
        word_to_remove.textline = None
        if self.textline is not None:
            self.textline.words.remove(word_to_remove)

    def extend_left(self):
        if self.prev_word is None:
            return
        if self.prev_word.accepts_additional_fragments == False:
            return
        if self.prev_word.textline != self.textline:
            return
        self.prev_word.chars += self.chars
        self.prev_word.fragments.extend(self.fragments)
        self.prev_word.length += self.length
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
        word_to_remove = self
        self.prev_word.next_word = self.next_word
        word_to_remove.prev_word = None
        word_to_remove.next_word = None
        if self.textline is not None:
            self.textline.words.remove(word_to_remove)

    def calc_tab_length(self) -> float:
        tab_size: float = 0.0
        if self.textline is not None and self.textline.paragraph is not None:
            if self.textline.paragraph.textarea is not None:
                tab_size = (
                    self.textline.paragraph.textarea.document.settings.text_tab_size
                )
        word = self
        length = 0.0
        while word.prev_word is not None:
            if word.textline != word.prev_word.textline:
                break
            length += word.prev_word.length
            word = word.prev_word
        return tab_size - (length % tab_size)

    def change_length(self, length_diff: float):
        self.length += length_diff
        if self.textline is not None:
            self.textline.length += length_diff
            self.textline.available_length -= length_diff
            self.textline.recalc_tab_lengths()

    def calc_length_with_justify(self):
        return self.length + self.justify_space
