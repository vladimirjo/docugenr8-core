from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8.document import Document
    from docugenr8.font import Font

    from .textline import TextLine
    from .word import Word

from .paragraph import Paragraph
from .words_creation import create_words


class TextArea:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        document: Document,
    ) -> None:
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._document = document
        self._v_align = document.settings.text_v_align
        self._h_align = document.settings.text_h_align
        self._available_height = height
        self._paragraphs: deque[Paragraph] = deque()
        self._buffer: deque[Word] = deque()
        self._next_textarea: None | TextArea = None
        self._prev_textarea: None | TextArea = None
        self._state_accepts_words: bool = True
        self._state_textline_width_overflow: bool = False
        # late binding when adding text
        self._current_font: None | Font = None
        self._current_font_size: float = 0
        self._current_font_color: tuple[int, int, int] = (0, 0, 0)

        # words to fill in with page numbers
        self._words_with_current_page_fragments: list[Word] = []
        self._words_with_total_pages_fragments: list[Word] = []

    def add_text(
        self,
        unicode_text: str,
    ) -> None:
        self._save_font_attributes_from_document_settings()
        self._create_and_insert_words_into_buffer(unicode_text)
        self._distribute_words_in_all_areas()

    def _distribute_words_in_all_areas(self) -> None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None:
            return
        textarea._pull_and_push_words()

    def _save_font_attributes_from_document_settings(self) -> None:
        if self._document is not None:
            font_name = self._document.settings.font_current
            if font_name is None:
                raise TypeError("Current name of a font must be set.")
            self._current_font = self._document.fonts[font_name]
            self._current_font_size = self._document.settings.font_size
            self._current_font_color = self._document.settings.font_color
        if self._current_font is None:
            raise TypeError("The font object is missing.")

    def _create_and_insert_words_into_buffer(
        self,
        unicode_text: str,
    ) -> None:
        if self._current_font is None:
            raise ValueError("Current font must be set in settings.")
        words = create_words(
            unicode_text,
            self._current_font,
            self._current_font_size,
            self._current_font_color,
            self._document.settings.page_num_current_page_dummy,
            self._document.settings.page_num_total_pages_dummy,
            self._document.settings.page_num_dummy_length,
            self._document.settings.page_num_presentation,
        )
        buffer = self._get_buffer()
        buffer.extend(words)

    def _set_buffer(self, words: deque[Word]) -> None:
        current_textarea = self
        while current_textarea._next_textarea is not None:
            current_textarea = current_textarea._next_textarea
        current_textarea._buffer = words

    def _get_buffer(self) -> deque[Word]:
        current_textarea = self
        while current_textarea._next_textarea is not None:
            current_textarea = current_textarea._next_textarea
        return current_textarea._buffer

    def _get_the_last_word_from_textareas(self) -> Word | None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None or textarea._is_empty():
            return None
        return textarea._paragraphs[-1]._textlines[-1]._words[-1]

    def _get_the_first_textarea_to_accept_words(self) -> TextArea | None:
        current_textarea = self
        while current_textarea._state_accepts_words is False:
            if current_textarea._next_textarea is not None:
                current_textarea = current_textarea._next_textarea
            else:
                return None
        return current_textarea

    def _distrubute_words_in_all_paragraphs(self) -> None:
        for paragraph in self._paragraphs:
            paragraph._adjust_words_between_textlines()

    def _pull_and_push_words(self) -> None:
        if self._available_height >= 0:
            self._pull_next_available_word()
        if self._available_height < 0:
            self._state_accepts_words = False
            self._push_excess_words_to_next_available_place()

    def _pull_next_available_word(self) -> None:
        while self._available_height >= 0:
            next_word = self._get_next_word()
            if next_word is None:
                return
            if next_word._is_from_textarea():
                self._create_paragraph_from_textarea_if_needed(next_word)
                next_word._remove_page_number_from_textarea()
                next_word._remove_from_line()
            if next_word._is_from_buffer():
                self._create_paragraph_from_buffer_if_needed()
                self._get_buffer().remove(next_word)
            self._append_word_to_textarea(next_word)
            if self._state_textline_width_overflow:
                self._state_textline_width_overflow = False
                break

    def _append_word_to_textarea(self, word: Word) -> None:
        if word._has_current_page_fragments():
            self._words_with_current_page_fragments.append(word)
        if word._has_total_pages_fragments():
            self._words_with_total_pages_fragments.append(word)
        self._paragraphs[-1]._append_word_right(word)

    def _push_excess_words_to_next_available_place(self) -> deque[Word] | None:
        textline_to_push = self._paragraphs[-1]._textlines[-1]
        while self._available_height < 0:
            words_to_push = textline_to_push._remove_line_and_get_words()
            if self._next_textarea is not None:
                self._next_textarea._generate_paragraph_when_pushing_words(textline_to_push)
                self._next_textarea._add_words_front_to_textarea(words_to_push)
            else:
                words_to_push.extend(self._get_buffer())
                self._set_buffer(words_to_push)
            if len(self._paragraphs) == 0:
                return
            textline_to_push = self._paragraphs[-1]._textlines[-1]
        if self._next_textarea is not None:
            if len(self._paragraphs) == 0:
                self._next_textarea._empty_textarea()
            else:
                self._next_textarea._pull_and_push_words()

    def _create_paragraph_from_buffer_if_needed(
        self,
    ) -> None:
        if len(self._paragraphs) == 0:
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            if self._prev_textarea is not None:
                prev_paragraph = self._prev_textarea._paragraphs[-1]
                prev_paragraph._next_linked_paragraph = new_paragraph
                new_paragraph._prev_linked_paragraph = prev_paragraph
                new_paragraph._copy_paragraph_parameters_from(prev_paragraph)
        if self._paragraphs[-1]._ends_with_br:
            self._paragraphs.append(Paragraph(self))

    def _create_paragraph_from_textarea_if_needed(
        self,
        next_word: Word,
    ) -> None:
        paragraph = next_word._get_paragraph()
        if paragraph is None:
            raise TypeError("Next word is missing paragraph object.")
        if next_word._is_first_word_in_paragraph():
            if next_word._textline is not None:
                paragraph._set_non_first_line_indent(next_word._textline)
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            new_paragraph._copy_paragraph_parameters_from(paragraph)
            new_paragraph._next_linked_paragraph = paragraph
            paragraph._prev_linked_paragraph = new_paragraph
            return
        if next_word._is_last_word_in_paragraph():
            self._paragraphs[-1]._next_linked_paragraph = None
            paragraph._prev_linked_paragraph = None
            return
        if self._paragraphs[-1]._next_linked_paragraph != paragraph:
            self._paragraphs[-1]._next_linked_paragraph = paragraph
            paragraph._prev_linked_paragraph = self._paragraphs[-1]
            return

    def _generate_paragraph_when_pushing_words(self, textline_to_push: TextLine) -> None:
        if len(self._paragraphs) == 0 and textline_to_push._is_first_line_in_paragraph():
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = None
            return
        if len(self._paragraphs) == 0 and not textline_to_push._is_first_line_in_paragraph():
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            if textline_to_push._paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(textline_to_push._paragraph)
            new_paragraph._prev_linked_paragraph = textline_to_push._paragraph
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = new_paragraph
            return
        if textline_to_push._is_last_line_in_paragraph():
            new_paragraph = Paragraph(self)
            self._paragraphs.appendleft(new_paragraph)
            if textline_to_push._paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(textline_to_push._paragraph)
            new_paragraph._prev_linked_paragraph = textline_to_push._paragraph
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = new_paragraph
        if textline_to_push._is_first_line_in_paragraph():
            self._paragraphs[0]._prev_linked_paragraph = None
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = None

    def _add_words_front_to_textarea(self, words: deque[Word]) -> None:
        while len(words) > 0:
            word = words.popleft()
            self._paragraphs[0]._textlines[0]._append_word(word, 0)
        self._paragraphs[0]._adjust_words_between_textlines()

    def _get_next_word(self) -> Word | None:
        """Get next word.

        Gets the next word from either next paragraph if there is one,
        or from the words buffer.
        """
        textarea = self._get_next_textarea_with_words()
        if textarea is not None:
            return textarea._paragraphs[0]._textlines[0]._words[0]
        buffer = self._get_buffer()
        if len(buffer) == 0:
            return None
        return buffer[0]

    def _get_next_textarea_with_words(self) -> TextArea | None:
        textarea = self._next_textarea
        while textarea is not None:
            if not textarea._is_empty():
                return textarea
            textarea = textarea._next_textarea
        return None

    def _is_empty(self) -> bool:
        if len(self._paragraphs) == 0:
            return True
        if len(self._paragraphs[0]._textlines) == 0:
            return True
        if len(self._paragraphs[0]._textlines[0]._words) == 0:
            return True
        return False

    def _build_current_page_fragments(self, current_page: int) -> None:
        for word in self._words_with_current_page_fragments:
            for fragment in word._current_page_fragments:
                if fragment._page_number_presentation is None:
                    continue
                font = self._document.fonts[fragment._font_name]
                chars = fragment._page_number_presentation(current_page)
                page_number_width = 0.0
                if len(chars) > 0:
                    fragment._chars = chars
                    for char in chars:
                        page_number_width += font._get_char_width(char, fragment._font_size)
                fragment._adjust_width(page_number_width)
                if (
                    fragment._word is not None
                    and fragment._word._textline is not None
                    and fragment._word._textline._paragraph is not None
                    and fragment._word._textline._paragraph._textarea is not None
                ):
                    paragraph = fragment._word._textline._paragraph
                    paragraph._adjust_words_between_textlines()
                    textarea = fragment._word._textline._paragraph._textarea
                    textarea._pull_and_push_words()

    def _build_total_pages_fragments(self, total_pages: int) -> None:
        for word in self._words_with_total_pages_fragments:
            for fragment in word._total_pages_fragments:
                if fragment._page_number_presentation is None:
                    continue
                font = self._document.fonts[fragment._font_name]
                chars = fragment._page_number_presentation(total_pages)
                new_length = 0.0
                if len(chars) > 0:
                    fragment._chars = chars
                    for char in chars:
                        new_length += font._get_char_width(char, fragment._font_size)
                fragment._adjust_width(new_length)
                if (
                    fragment._word is not None
                    and fragment._word._textline is not None
                    and fragment._word._textline._paragraph is not None
                    and fragment._word._textline._paragraph._textarea is not None
                ):
                    paragraph = fragment._word._textline._paragraph
                    paragraph._adjust_words_between_textlines()
                    textarea = fragment._word._textline._paragraph._textarea
                    textarea._pull_and_push_words()

    def link_textarea(self, next_textarea: TextArea) -> None:
        last_textarea = self
        while last_textarea._next_textarea is not None:
            last_textarea = last_textarea._next_textarea
        last_textarea._next_textarea = next_textarea
        next_textarea._buffer = last_textarea._buffer
        last_textarea._buffer = deque()
        self._distribute_words_in_all_areas()

    def set_width(self, new_width: float) -> None:
        self._width = new_width
        for paragraph in self._paragraphs:
            paragraph._set_paragraph_width(new_width)
        self._distribute_words_in_all_areas()

    def _empty_textlines_and_paragraphs_from_line(self, textline_index: int, paragraph_index: int) -> None:
        removed_words = deque()
        first_paragraph_to_remove_words_from = self._paragraphs[paragraph_index]
        textline = first_paragraph_to_remove_words_from._textlines[textline_index]
        while textline_index < len(first_paragraph_to_remove_words_from._textlines):
            textline = self._paragraphs[paragraph_index]._textlines[textline_index]
            removed_words.extend(textline._remove_line_and_get_words())
        if len(self._paragraphs) > 0 and (first_paragraph_to_remove_words_from == self._paragraphs[paragraph_index]):
            paragraph_index += 1
        while paragraph_index < len(self._paragraphs):
            paragraph = self._paragraphs[paragraph_index]
            removed_words.extend(paragraph._remove_paragraph_from_text_area())
        textarea_to_empty = self._next_textarea
        while textarea_to_empty is not None:
            removed_words.extend(textarea_to_empty._empty_textarea())
            textarea_to_empty = textarea_to_empty._next_textarea
        word_buffer = self._get_buffer()
        removed_words.extend(word_buffer)
        self._set_buffer(removed_words)

    def _empty_textarea(self) -> deque[Word]:
        removed_words = deque()
        while len(self._paragraphs) > 0:
            paragraph = self._paragraphs[0]
            removed_words.extend(paragraph._remove_paragraph_from_text_area())
        return removed_words
