from __future__ import annotations
from typing import TYPE_CHECKING
from collections import deque


if TYPE_CHECKING:
    from .paragraph import Paragraph
    from .word import Word

class TextLine:
    def __init__(self, paragraph: Paragraph, left_indent: float) -> None:
        self.paragraph = paragraph
        self.left_indent = left_indent
        self.length = 0.0
        self.available_length = self.length
        self.set_length()
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
        self.x: None | float = None
        self.y: None | float = None

    # *************************************************************
    #           APPEND A WORD TO THE LINE FROM RIGHT
    # *************************************************************
    def append_word_right(self, word: Word):
        word.textline = self
        self.words.append(word)
        self.append_height(word.height)
        self.append_ascent(word.ascent)
        self.set_spaces_length_when_append_word_right(word)
        self.set_word_length_right(word)

    def set_spaces_length_when_append_word_right(self, word: Word):
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
            iterator.length = iterator.get_origin_length()
            self.inner_spaces.append(iterator)
            spaces.append(iterator)
            self.available_length -= iterator.length
            if iterator.prev_word is None:
                break
            iterator = iterator.prev_word
        # spaces at the start of a word will not be included in justifying
        if spaces[0] == self.words[0]:
            for space in spaces:
                self.inner_spaces.remove(space)
        return

    def set_word_length_right(self, word: Word):
        if word.chars == " ":
            word.length = 0.0
            return
        if word.accepts_additional_fragments:
            word.extend_left()
            self.available_length -= word.length
            return
        if word.chars == "\n":
            return
        if word.chars == "\t":
            self.tabs.append(word)
            word.length = self.calc_tab_length(word)
            self.available_length -= word.length
            return

    # *************************************************************
    #           APPEND A WORD TO THE LINE FROM LEFT
    # *************************************************************

    def append_word_left(self, word: Word) -> None:
        word.textline = self
        self.words.appendleft(word)
        self.append_height(word.height)
        self.append_ascent(word.ascent)
        self.set_spaces_length_when_append_word_left(word)
        self.set_word_length_left(word)

    def set_spaces_length_when_append_word_left(self, word: Word) -> None:
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
                space.length = 0.0
                self.inner_spaces.remove(space)
        return

    def set_word_length_left(self, word: Word) -> None:
        if word.chars == " ":
            word.length = word.get_origin_length()
            self.available_length -= word.length
            return
        if word.accepts_additional_fragments:
            word.extend_right()
            self.available_length -= word.length
            return
        if word.chars == "\n":
            return
        if word.chars == "\t":
            self.tabs.append(word)
            self.recalc_tab_lengths()
            self.available_length -= word.length
            return

    # *************************************************************
    #                   SPLIT LONG WORDS
    # *************************************************************

    def split_word(self) -> None:
        word = Word()
        first_fragment = self.words[-1].fragments[0]
        while word.length + first_fragment.length <= self.length:
            fragment = self.words[-1].pop_fragment_left()
            word.add_fragment(fragment)
            first_fragment = self.words[-1].fragments[0]
        word.prev_word = self.words[-1].prev_word
        word.next_word = self.words[-1]
        self.words[-1].prev_word = word
        self.words.appendleft(word)

    # *************************************************************
    #        CAN MOVE THE FIRST WORD FROM THE NEXT LINE
    # *************************************************************
    def can_move_first_word_from_next_line(self) -> bool:
        if self.next_line is None:
            return False
        if len(self.next_line.words) == 0:
            return False
        first_word = self.next_line.words[0]
        if first_word.chars in {" ", "\n"}:
            return True
        word_length = 0.0
        if first_word.chars == "\t":
            word_length = self.calc_tab_length(first_word)
        else:
            word_length = first_word.length
        spaces_length = 0.0
        word_iterator = self.words[-1]
        while word_iterator.chars == " ":
            spaces_length += word_iterator.get_origin_length()
            if word_iterator.prev_word is None:
                break
            word_iterator = word_iterator.prev_word
        if self.available_length - spaces_length - word_length < 0.0:
            return False
        return True

    # *************************************************************
    #               MOVING WORD BETWEEN LINES
    # *************************************************************
    def move_last_word_to_next_line(self):
        word = self.pop_word_right()
        if self.next_line is None:
            if self.paragraph is None:
                raise TypeError("Paragraph object is missing.")
            line = TextLine(self.paragraph, self.paragraph.left_indent)
            line.prev_line = self
            self.next_line = line
            self.paragraph.lines.append(line)
            leading_diff = self.set_leading()
            self.paragraph.change_height(leading_diff)
        self.next_line.append_word_left(word)

    def move_first_word_from_next_line(self):
        if self.next_line is None:
            raise TypeError("Next line object is missing.")
        word = self.next_line.pop_word_left()
        # if len(self.next_line.words) == 0:
        #     self.next_line.remove_line()
        self.append_word_right(word)

    # *************************************************************
    #        REMOVE THE LAST WORD FROM RIGHT IN THE LINE
    # *************************************************************
    def pop_word_right(self) -> Word:
        last_word_in_line = self.words.pop()
        if len(self.words) == 0:
            self.remove_line()
        self.set_spaces_length_when_pop_word_right(last_word_in_line)
        last_word_in_line.textline = None
        self.remove_ascent(last_word_in_line.ascent)
        self.remove_height(last_word_in_line.height)
        if self.next_line is not None:
            self.set_leading()
        self.available_length += last_word_in_line.length
        return last_word_in_line

    def set_spaces_length_when_pop_word_right(self, word: Word):
        if word.prev_word is None:
            return
        if word.prev_word.textline != self:
            return
        if word.prev_word.chars != " ":
            return
        iterator = word.prev_word
        # if iterator is not None:
        while iterator is not None and iterator.chars == " ":
            self.available_length += iterator.length
            iterator.length = 0.0
            if iterator in self.inner_spaces:
                self.inner_spaces.remove(iterator)
            iterator = iterator.prev_word

    # *************************************************************
    #        REMOVE THE FIRST WORD FROM LEFT IN THE LINE
    # *************************************************************

    def pop_word_left(self) -> Word:
        first_word_in_line = self.words.popleft()
        if len(self.words) == 0:
            self.remove_line()
        self.set_spaces_length_when_pop_word_left(first_word_in_line)
        self.recalc_tab_lengths()
        first_word_in_line.textline = None
        if first_word_in_line.chars in {" ", "\t"}:
            first_word_in_line.length = first_word_in_line.get_origin_length()
        self.remove_ascent(first_word_in_line.ascent)
        self.remove_height(first_word_in_line.height)
        if self.next_line is not None:
            self.set_leading()
        self.available_length += first_word_in_line.length
        return first_word_in_line

    def set_spaces_length_when_pop_word_left(self, word: Word):
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

    # *************************************************************
    #                 REMOVE A LINE AND GET WORDS
    # *************************************************************

    def remove_line_and_get_words(self) -> deque[Word]:
        for word in self.words:
            if word.has_current_page_fragments:
                word.remove_page_number()
            if word.has_total_pages_fragments:
                word.remove_page_number()
            word.reset_all_stats()
        self.remove_line()
        return self.words

    # *************************************************************
    #                       UTILITIES
    # *************************************************************

    def is_first_line_in_paragraph(self) -> bool:
        if self.paragraph is None:
            return False
        first_linked_paragraph = self.paragraph._get_first_linked_paragraph()
        if self == first_linked_paragraph.lines[0]:
            return True
        else:
            return False

    def is_last_line_in_paragraph(self) -> bool:
        if self.paragraph is None:
            return False
        last_linked_paragraph = self.paragraph._get_last_linked_paragraph()
        if self == last_linked_paragraph.lines[-1]:
            return True
        else:
            return False

    # def is_first_in_paragraph(self) -> bool:
    #     return self == self.paragraph.lines[0]

    def set_non_first_left_indent(self):
        if self.paragraph is None:
            return
        length_diff = self.left_indent - self.paragraph.left_indent
        self.left_indent = self.paragraph.left_indent
        self.available_length += length_diff
        self.length += length_diff

    def set_first_left_indent(self):
        if self.paragraph is None:
            return
        length_diff = self.paragraph.first_line_indent - self.left_indent
        self.left_indent = self.paragraph.first_line_indent
        self.available_length -= length_diff
        self.length -= length_diff

    def get_chars(self) -> str:
        chars = ""
        for word in self.words:
            chars += word.chars
        return chars

    def reallocate_words_in_line(self):
        while self.available_length < 0.0:
            if len(self.words) == 1:
                self.split_word()
            self.move_last_word_to_next_line()
        while self.can_move_first_word_from_next_line():
            self.move_first_word_from_next_line()

    def append_height(self, height: float):
        if height not in self.height_dict:
            self.height_dict[height] = 1
        else:
            self.height_dict[height] += 1
        height_diff = 0.0
        if height > self.height:
            height_diff = height - self.height
            self.height += height_diff
        if self.next_line is not None:
            leading_diff = self.set_leading()
            height_diff += leading_diff
        if height_diff != 0.0 and self.paragraph is not None:
            self.paragraph.change_height(height_diff)

    def append_ascent(self, ascent: float):
        if ascent not in self.ascent_dict:
            self.ascent_dict[ascent] = 1
        else:
            self.ascent_dict[ascent] += 1
        if ascent > self.ascent:
            ascent_diff = ascent - self.ascent
            self.ascent += ascent_diff

    def remove_height(self, height: float):
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
            leading_diff = self.set_leading()
            height_diff += leading_diff
        if self.paragraph is not None:
            self.paragraph.change_height(height_diff)

    def remove_ascent(self, ascent: float):
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

    def remove_line(self):
        height_to_remove = self.height
        if self.next_line is not None:
            height_to_remove += self.leading
            self.next_line.prev_line = self.prev_line
        if self.prev_line is not None:
            self.prev_line.next_line = self.next_line
            height_to_remove += self.prev_line.set_leading()

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
            self.paragraph.textarea.paragraphs.remove(self.paragraph)
        self.paragraph.change_height(-height_to_remove)
        self.paragraph = None

    def calc_line_length(self):
        if self.paragraph is None:
            raise TypeError("Paragraph object is missing.")
        return (
            self.paragraph.width
            - self.left_indent
            - self.paragraph.right_indent
        )

    def set_length(self):
        length_diff = self.calc_line_length() - self.length
        self.length += length_diff
        self.available_length += length_diff

    def calc_tab_length(self, word: Word):
        if self.paragraph is None:
            raise ValueError("missing paragraph")
        tab_size = self.paragraph.tab_size
        length = 0.0
        while word.prev_word is not None:
            if word.textline != word.prev_word.textline:
                break
            if word.chars == " ":
                length += word.fragments[0].length
            length += word.prev_word.length
            word = word.prev_word
        return tab_size - (length % tab_size)

    def recalc_tab_lengths(self):
        for tab in self.tabs:
            tab.length = self.calc_tab_length(tab)

    def calc_leading(self) -> float:
        if self.paragraph is None:
            raise ValueError("Paragraph is missing")
        return (self.height * self.paragraph.line_height_ratio) - self.height

    def set_leading(self) -> float:
        if self.next_line is None:
            leading_diff = self.leading
            self.leading = 0.0
            return leading_diff
        leading_diff = self.calc_leading() - self.leading
        self.leading += leading_diff
        return leading_diff
