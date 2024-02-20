from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_core.document import Document
    from docugenr8_core.font import Font

    from .text_line import TextLine


from .fragment import Fragment
from .paragraph import Paragraph
from .word import Word


class TextArea:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        document: Document,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.document = document
        self.v_align = document.settings.text_v_align
        self.h_align = document.settings.text_h_align
        self.available_height = height
        self.paragraphs: deque[Paragraph] = deque()
        self.buffer: deque[Word] = deque()
        self.next_textarea: None | TextArea = None
        self.prev_textarea: None | TextArea = None
        self.accepts_additional_words: bool = True

        # late binding when adding text
        self.current_font: None | Font = None
        self.current_font_size: float = 0
        self.current_font_color: tuple[int, int, int] = (0, 0, 0)

        # words to fill in with page numbers
        self.words_with_current_page_fragments: list[Word] = []
        self.words_with_total_pages_fragments: list[Word] = []

    def add_text(
        self,
        unicode_text: str,
    ) -> None:
        self._save_font_attributes_from_document_settings()
        words = self._create_words(unicode_text)
        self._establish_link_with_last_word(words[0])
        self._insert_words_into_buffer(words)
        self._move_words_in_all_linked_areas()

    def _move_words_in_all_linked_areas(
        self
        ) -> None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None:
            return
        textarea._move_words_between_areas()

    def _save_font_attributes_from_document_settings(
        self
        ) -> None:
        if self.document is not None:
            font_name = self.document.settings.font_current
            if font_name is None:
                raise TypeError("Current name of a font must be set.")
            self.current_font = self.document.fonts[font_name]
            self.current_font_size = self.document.settings.font_size
            self.current_font_color = self.document.settings.font_color
        if self.current_font is None:
            raise TypeError("The font object is missing.")

    def _insert_words_into_buffer(
        self,
        words: list[Word]
        ) -> None:
        buffer = self._get_buffer()
        buffer.extend(words)

    def _create_words(
        self,
        unicode_text: str,
    ) -> list[Word]:
        char_idx = 0
        words: list[Word] = []
        while char_idx < len(unicode_text):
            (fragment, increment) = self._generate_fragment_with_increment(
                unicode_text, char_idx)
            if fragment.chars in {"\n", "\t", " "}:
                word = Word()
                word._add_fragment(fragment)
                if len(words) > 0:
                    word.prev_word = words[-1]
                    words[-1].next_word = word
                words.append(word)
            else:
                if len(words) == 0:
                    words.append(Word())
                if words[-1].is_extendable:
                    words[-1]._add_fragment(fragment)
                else:
                    word = Word()
                    word._add_fragment(fragment)
                    if len(words) > 0:
                        word.prev_word = words[-1]
                        words[-1].next_word = word
                    words.append(word)
            char_idx += increment
        return words

    def _establish_link_with_last_word(
        self,
        first_word: Word
        ) -> None:
        buffer = self._get_buffer()
        if len(buffer) > 0:
            first_word.prev_word = buffer[-1]
            buffer[-1].next_word = first_word
            return
        last_word = self._get_the_last_word_from_textareas()
        if last_word is not None:
            first_word.prev_word = last_word
            last_word.next_word = first_word
            return

    def _set_buffer(
        self,
        words: deque[Word]) -> None:
        current_textarea = self
        while current_textarea.next_textarea is not None:
            current_textarea = current_textarea.next_textarea
        current_textarea.buffer = words

    def _get_buffer(
        self
        ) -> deque[Word]:
        current_textarea = self
        while current_textarea.next_textarea is not None:
            current_textarea = current_textarea.next_textarea
        return current_textarea.buffer

    def _get_the_last_word_from_textareas(
        self
        ) -> Word | None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None or textarea._is_empty():
            return None
        return textarea.paragraphs[-1].lines[-1].words[-1]

    def _generate_fragment_with_increment(
        self,
        unicode_text: str,
        char_idx: int,
    ) -> tuple[Fragment, int]:
        if self._is_carriage_return_with_new_line(unicode_text, char_idx):
            fragment = self._generate_new_line_fragment()
            return (fragment, 2)
        if self._is_only_carriage_return(unicode_text, char_idx):
            fragment = self._generate_new_line_fragment()
            return (fragment, 1)
        if self._is_string_current_page_dummy(unicode_text, char_idx):
            (fragment, increment) = self._generate_current_page_fragment()
            return (fragment, increment)
        if self._is_string_total_pages_dummy(unicode_text, char_idx):
            (fragment, increment) = self._generate_total_pages_fragment()
            return (fragment, increment)
        if self.current_font is None:
            raise ValueError("Current font is missing.")
        fragment_height = self.current_font._get_line_height(
            self.current_font_size)
        fragment_width = self.current_font._get_char_width(
            unicode_text[char_idx], self.current_font_size)
        fragment_ascent = self.current_font._get_ascent(self.current_font_size)
        fragment = Fragment(
            fragment_height,
            fragment_width,
            fragment_ascent,
            unicode_text[char_idx],
            self.current_font.name,
            self.current_font_size,
            self.current_font_color)
        increment = 1
        return (fragment, increment)

    def _is_carriage_return_with_new_line(  # noqa: PLR6301
        self,
        unicode_text: str,
        char_idx: int
        ) -> bool:
        carriage_return = unicode_text[char_idx]
        try:
            new_line = unicode_text[char_idx + 1]
        except IndexError:
            return False
        if (carriage_return == "\r"
            and new_line == "\n"):
            return True
        return False

    def _is_only_carriage_return(  # noqa: PLR6301
        self,
        unicode_text: str,
        char_idx: int
        ) -> bool:
        if unicode_text[char_idx] == "\r":
            return True
        return False

    def _is_string_current_page_dummy(
        self,
        unicode_text: str,
        char_idx: int
    ) -> bool:
        current_page_dummy = self.document.settings.page_num_current_page_dummy
        start = char_idx
        end = start + len(current_page_dummy)
        if unicode_text[start:end] == current_page_dummy:
            return True
        return False

    def _is_string_total_pages_dummy(
        self,
        unicode_text: str,
        char_idx: int
    ) -> bool:
        total_pages_dummy = self.document.settings.page_num_total_pages_dummy
        start = char_idx
        end = start + len(total_pages_dummy)
        if unicode_text[start:end] == total_pages_dummy:
            return True
        return False

    def _generate_current_page_fragment(
        self
        ) -> tuple[Fragment, int]:
        if self.current_font is None:
            raise ValueError("Current font is missing.")
        fragment_width = (self.document.settings.page_num_dummy_length
                          * self.current_font._get_char_width(
                              "0", self.current_font_size))
        fragment_height = self.current_font._get_line_height(
            self.current_font_size)
        fragment_ascent = self.current_font._get_ascent(
            self.current_font_size)
        fragment = Fragment(
            fragment_height,
            fragment_width,
            fragment_ascent,
            self.document.settings.page_num_current_page_dummy,
            self.current_font.name,
            self.current_font_size,
            self.current_font_color)
        fragment.page_number_presentation = (
            self.document.settings.page_num_presentation)
        fragment.is_current_page_dummy = True
        increment = len(self.document.settings.page_num_current_page_dummy)
        return (fragment, increment)

    def _generate_total_pages_fragment(
        self
        ) -> tuple[Fragment, int]:
        if self.current_font is None:
            raise ValueError("Current font is missing.")
        fragment_width = (self.document.settings.page_num_dummy_length
                          * self.current_font._get_char_width(
                              "0", self.current_font_size))
        fragment_height = self.current_font._get_line_height(
            self.current_font_size)
        fragment_ascent = self.current_font._get_ascent(
            self.current_font_size)
        fragment = Fragment(
            fragment_height,
            fragment_width,
            fragment_ascent,
            self.document.settings.page_num_total_pages_dummy,
            self.current_font.name,
            self.current_font_size,
            self.current_font_color)
        fragment.page_number_presentation = (
            self.document.settings.page_num_presentation)
        fragment.is_total_pages_dummy = True
        increment = len(self.document.settings.page_num_total_pages_dummy)
        return (fragment, increment)

    def _generate_new_line_fragment(
        self
        ) -> Fragment:
        if self.current_font is None:
            raise ValueError("Current font is missing.")
        fragment_width = 0.0
        fragment_height = self.current_font._get_line_height(
            self.current_font_size)
        fragment_ascent = self.current_font._get_ascent(
            self.current_font_size)
        return Fragment(
            fragment_height,
            fragment_width,
            fragment_ascent,
            "\n",
            self.current_font.name,
            self.current_font_size,
            self.current_font_color)

    def _get_the_first_textarea_to_accept_words(
        self
        ) -> TextArea | None:
        current_textarea = self
        while current_textarea.accepts_additional_words is False:
            if current_textarea.next_textarea is not None:
                current_textarea = current_textarea.next_textarea
            else:
                return None
        return current_textarea

    def _distrubute_words_in_all_paragraphs(
        self
        ) -> None:
        for paragraph in self.paragraphs:
            paragraph._distribute_words_in_lines()

    def _move_words_between_areas(
        self
        ) -> None:
        if self.available_height > 0:
            self._pull_next_available_word()
        if self.available_height < 0:
            self.accepts_additional_words = False
            self._push_excess_words_to_next_available_place()

    def _pull_next_available_word(
        self
        ) -> None:
        while self.available_height >= 0:
            next_word = self._get_next_available_word()
            if next_word is None:
                return
            self._create_paragraph_if_needed_for_incoming_word(next_word)
            self._remove_word(next_word)
            self._append_word_to_area(next_word)

    def _create_paragraph_if_needed_for_incoming_word(
        self,
        word: Word
        ) -> None:
        paragraph = word._get_paragraph()
        if paragraph is None:
            self._generate_paragraph_from_buffer(word)
        else:
            self._generate_paragraph_from_text_area(
                word,
                paragraph)

    def _append_word_to_area(
        self,
        word: Word
        ) -> None:
        if word._has_current_page_fragments():
            self.words_with_current_page_fragments.append(word)
        if word._has_total_pages_fragments():
            self.words_with_total_pages_fragments.append(word)
        self.paragraphs[-1]._append_word_right(word)

    def _push_excess_words_to_next_available_place(
        self
        ) -> deque[Word] | None:
        textline_to_push = self.paragraphs[-1].lines[-1]
        while self.available_height < 0:
            if self.next_textarea is not None:
                self.next_textarea._generate_paragraph_when_pushing_words(
                    textline_to_push
                )
                words_to_push = textline_to_push._remove_line_and_get_words()
                self.next_textarea._add_words_front_to_textarea(words_to_push)
            else:
                words_to_push = textline_to_push._remove_line_and_get_words()
                words_to_push.extend(self._get_buffer())
                self._set_buffer(words_to_push)
            if len(self.paragraphs) == 0:
                return
            textline_to_push = self.paragraphs[-1].lines[-1]
        if self.next_textarea is not None:
            self.next_textarea._move_words_between_areas()

    def _generate_paragraph_from_buffer(
        self,
        word: Word,
    ) -> None:
        if len(self.paragraphs) == 0:
            paragraph = Paragraph(self)
            self.paragraphs.append(paragraph)
            if word.prev_word is not None:
                prev_paragraph = word.prev_word._get_paragraph()
                paragraph.prev_linked_paragraph = prev_paragraph
                if prev_paragraph is not None:
                    prev_paragraph.next_linked_paragraph = paragraph
                    paragraph._copy_paragraph_parameters_from(prev_paragraph)
        if self.paragraphs[-1].ends_with_br:
            paragraph = Paragraph(self)
            self.paragraphs.append(paragraph)

    def _generate_paragraph_from_text_area(
        self,
        word: Word,
        paragraph: Paragraph
        ) -> None:
        if word._is_first_word_in_paragraph():
            if word.textline is not None:
                paragraph._set_non_first_line_indent(word.textline)
            new_paragraph = Paragraph(self)
            self.paragraphs.append(new_paragraph)
            new_paragraph._copy_paragraph_parameters_from(paragraph)
            new_paragraph.next_linked_paragraph = paragraph
            paragraph.prev_linked_paragraph = new_paragraph
            return
        if word._is_last_word_in_paragraph():
            self.paragraphs[-1].next_linked_paragraph = None
            paragraph.prev_linked_paragraph = None
            return
        if self.paragraphs[-1].next_linked_paragraph != paragraph:
            self.paragraphs[-1].next_linked_paragraph = paragraph
            paragraph.prev_linked_paragraph = self.paragraphs[-1]
            return

    def _generate_paragraph_when_pushing_words(
        self,
        textline_to_push: TextLine
    ) -> None:
        if (
            len(self.paragraphs) == 0
            and textline_to_push._is_first_line_in_paragraph()):
            new_paragraph = Paragraph(self)
            self.paragraphs.append(new_paragraph)
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = None
            return
        if (
            len(self.paragraphs) == 0
            and not textline_to_push._is_first_line_in_paragraph()
            ):
            new_paragraph = Paragraph(self)
            self.paragraphs.append(new_paragraph)
            if textline_to_push.paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(
                    textline_to_push.paragraph)
            new_paragraph.prev_linked_paragraph = textline_to_push.paragraph
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = new_paragraph
            return
        if textline_to_push._is_last_line_in_paragraph():
            new_paragraph = Paragraph(self)
            self.paragraphs.appendleft(new_paragraph)
            if textline_to_push.paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(
                    textline_to_push.paragraph)
            new_paragraph.prev_linked_paragraph = textline_to_push.paragraph
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = new_paragraph
        if textline_to_push._is_first_line_in_paragraph():
            self.paragraphs[0].prev_linked_paragraph = None
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = None

    def _remove_word(
        self,
        word: Word
        ) -> None:
        if word.textline is None:
            self._get_buffer().remove(word)
        else:
            word._remove_page_number()
            word._remove_from_line()

    def _add_words_front_to_textarea(
        self,
        words: deque[Word]
        ) -> None:
        while len(words) > 0:
            word = words.popleft()
            self.paragraphs[0]._append_word_left(word)
        self.paragraphs[0]._distribute_words_in_lines()

    def _get_next_available_word(
        self
        ) -> Word | None:
        """gets the next word from either next paragraph if there is one,
        or from the words buffer
        """
        textarea = self._get_next_textarea_with_words()
        if textarea is not None:
            return textarea.paragraphs[0].lines[0].words[0]
        buffer = self._get_buffer()
        if len(buffer) == 0:
            return None
        return buffer[0]

    def _get_next_textarea_with_words(
        self
        ) -> TextArea | None:
        textarea = self.next_textarea
        while textarea is not None:
            if not textarea._is_empty():
                return textarea
            textarea = textarea.next_textarea
        return None

    def _is_empty(
        self
        ) -> bool:
        if len(self.paragraphs) == 0:
            return True
        if len(self.paragraphs[0].lines) == 0:
            return True
        if len(self.paragraphs[0].lines[0].words) == 0:
            return True
        return False

    def _build_current_page_fragments(
        self,
        current_page: int
        ) -> None:
        for word in self.words_with_current_page_fragments:
            for fragment in word.current_page_fragments:
                if fragment.page_number_presentation is None:
                    continue
                font = self.document.fonts[fragment.font_name]
                chars = fragment.page_number_presentation(current_page)
                page_number_width = 0.0
                if len(chars) > 0:
                    fragment.chars = chars
                    for char in chars:
                        page_number_width += font._get_char_width(
                            char, fragment.font_size)
                fragment._adjust_width(page_number_width)
                if (fragment.word is not None
                    and fragment.word.textline is not None
                    and fragment.word.textline.paragraph is not None
                    and fragment.word.textline.paragraph.textarea is not None):
                    paragraph = fragment.word.textline.paragraph
                    paragraph._distribute_words_in_lines()
                    textarea = fragment.word.textline.paragraph.textarea
                    textarea._move_words_between_areas()

    def _build_total_pages_fragments(
        self,
        total_pages: int
        ) -> None:
        for word in self.words_with_total_pages_fragments:
            for fragment in word.total_pages_fragments:
                if fragment.page_number_presentation is None:
                    continue
                font = self.document.fonts[fragment.font_name]
                chars = fragment.page_number_presentation(total_pages)
                new_length = 0.0
                if len(chars) > 0:
                    fragment.chars = chars
                    for char in chars:
                        new_length += font._get_char_width(
                            char, fragment.font_size)
                fragment._adjust_width(new_length)
                if (fragment.word is not None
                    and fragment.word.textline is not None
                    and fragment.word.textline.paragraph is not None
                    and fragment.word.textline.paragraph.textarea is not None):
                    paragraph = fragment.word.textline.paragraph
                    paragraph._distribute_words_in_lines()
                    textarea = fragment.word.textline.paragraph.textarea
                    textarea._move_words_between_areas()

    def link_textarea(
        self,
        next_textarea: TextArea
        ) -> None:
        last_textarea = self
        while last_textarea.next_textarea is not None:
            last_textarea = last_textarea.next_textarea
        last_textarea.next_textarea = next_textarea
        next_textarea.buffer = last_textarea.buffer
        last_textarea.buffer = deque()
        self._move_words_in_all_linked_areas()

    def set_width(
        self,
        new_width: float
        ) -> None:
        self.width = new_width
        for paragraph in self.paragraphs:
            paragraph._set_paragraph_width(new_width)
        self._move_words_in_all_linked_areas()
