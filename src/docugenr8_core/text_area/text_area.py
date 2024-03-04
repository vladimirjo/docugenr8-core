from __future__ import annotations

from collections import deque
from collections.abc import Callable
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
        self._accepts_additional_words: bool = True
        self._word_width_exceeds_textline_width: bool = False
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
            self._document.settings.page_num_presentation)
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
        if self._document is not None:
            font_name = self._document.settings.font_current
            if font_name is None:
                raise TypeError("Current name of a font must be set.")
            self._current_font = self._document.fonts[font_name]
            self._current_font_size = self._document.settings.font_size
            self._current_font_color = self._document.settings.font_color
        if self._current_font is None:
            raise TypeError("The font object is missing.")

    def _insert_words_into_buffer(
        self,
        words: list[Word]
        ) -> None:
        buffer = self._get_buffer()
        buffer.extend(words)

    def _set_buffer(
        self,
        words: deque[Word]) -> None:
        current_textarea = self
        while current_textarea._next_textarea is not None:
            current_textarea = current_textarea._next_textarea
        current_textarea._buffer = words

    def _get_buffer(
        self
        ) -> deque[Word]:
        current_textarea = self
        while current_textarea._next_textarea is not None:
            current_textarea = current_textarea._next_textarea
        return current_textarea._buffer

    def _get_the_last_word_from_textareas(
        self
        ) -> Word | None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None or textarea._is_empty():
            return None
        return textarea._paragraphs[-1]._textlines[-1]._words[-1]

    def _get_the_first_textarea_to_accept_words(
        self
        ) -> TextArea | None:
        current_textarea = self
        while current_textarea._accepts_additional_words is False:
            if current_textarea._next_textarea is not None:
                current_textarea = current_textarea._next_textarea
            else:
                return None
        return current_textarea

    def _distrubute_words_in_all_paragraphs(
        self
        ) -> None:
        for paragraph in self._paragraphs:
            paragraph._adjust_words_between_textlines()

    def _move_words_between_areas(
        self
        ) -> None:
        if self._available_height > 0:
            self._pull_next_available_word()
        if self._available_height < 0:
            self._accepts_additional_words = False
            self._push_excess_words_to_next_available_place()

    def _pull_next_available_word(
        self
        ) -> None:
        while self._available_height >= 0:
            next_word = self._get_next_available_word()
            if next_word is None:
                return
            self._create_paragraph_if_needed_for_incoming_word(next_word)
            self._remove_word(next_word)
            self._append_word_to_area(next_word)
            if self._word_width_exceeds_textline_width:
                self._word_width_exceeds_textline_width = False
                break

    def _create_paragraph_if_needed_for_incoming_word(
        self,
        word: Word
        ) -> None:
        paragraph = word._get_paragraph()
        if paragraph is None:
            self._generate_paragraph_from_buffer()
        else:
            self._generate_paragraph_from_text_area(
                word,
                paragraph)

    def _append_word_to_area(
        self,
        word: Word
        ) -> None:
        if word._has_current_page_fragments():
            self._words_with_current_page_fragments.append(word)
        if word._has_total_pages_fragments():
            self._words_with_total_pages_fragments.append(word)
        self._paragraphs[-1]._append_word_right(word)

    def _push_excess_words_to_next_available_place(
        self
        ) -> deque[Word] | None:
        textline_to_push = self._paragraphs[-1]._textlines[-1]
        while self._available_height < 0:
            if self._next_textarea is not None:
                self._next_textarea._generate_paragraph_when_pushing_words(
                    textline_to_push
                )
                words_to_push = textline_to_push._remove_line_from_text_area()
                self._next_textarea._add_words_front_to_textarea(words_to_push)
            else:
                words_to_push = textline_to_push._remove_line_from_text_area()
                words_to_push.extend(self._get_buffer())
                self._set_buffer(words_to_push)
            if len(self._paragraphs) == 0:
                return
            textline_to_push = self._paragraphs[-1]._textlines[-1]
        if self._next_textarea is not None:
            if len(self._paragraphs) == 0:
                self._next_textarea._empty_textarea()
            else:
                self._next_textarea._move_words_between_areas()

    def _generate_paragraph_from_buffer(
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

    def _generate_paragraph_from_text_area(
        self,
        word: Word,
        paragraph: Paragraph
        ) -> None:
        if word._is_first_word_in_paragraph():
            if word._textline is not None:
                paragraph._set_non_first_line_indent(word._textline)
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            new_paragraph._copy_paragraph_parameters_from(paragraph)
            new_paragraph._next_linked_paragraph = paragraph
            paragraph._prev_linked_paragraph = new_paragraph
            return
        if word._is_last_word_in_paragraph():
            self._paragraphs[-1]._next_linked_paragraph = None
            paragraph._prev_linked_paragraph = None
            return
        if self._paragraphs[-1]._next_linked_paragraph != paragraph:
            self._paragraphs[-1]._next_linked_paragraph = paragraph
            paragraph._prev_linked_paragraph = self._paragraphs[-1]
            return

    def _generate_paragraph_when_pushing_words(
        self,
        textline_to_push: TextLine
    ) -> None:
        if (
            len(self._paragraphs) == 0
            and textline_to_push._is_first_line_in_paragraph()):
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = None
            return
        if (
            len(self._paragraphs) == 0
            and not textline_to_push._is_first_line_in_paragraph()
            ):
            new_paragraph = Paragraph(self)
            self._paragraphs.append(new_paragraph)
            if textline_to_push._paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(
                    textline_to_push._paragraph)
            new_paragraph._prev_linked_paragraph = textline_to_push._paragraph
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = new_paragraph
            return
        if textline_to_push._is_last_line_in_paragraph():
            new_paragraph = Paragraph(self)
            self._paragraphs.appendleft(new_paragraph)
            if textline_to_push._paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(
                    textline_to_push._paragraph)
            new_paragraph._prev_linked_paragraph = textline_to_push._paragraph
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = new_paragraph
        if textline_to_push._is_first_line_in_paragraph():
            self._paragraphs[0]._prev_linked_paragraph = None
            if textline_to_push._paragraph is not None:
                textline_to_push._paragraph._next_linked_paragraph = None

    def _remove_word(
        self,
        word: Word
        ) -> None:
        if word._textline is None:
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
            self._paragraphs[0]._textlines[0]._append_word(word, 0)
        self._paragraphs[0]._adjust_words_between_textlines()

    def _get_next_available_word(
        self
        ) -> Word | None:
        """gets the next word from either next paragraph if there is one,
        or from the words buffer
        """
        textarea = self._get_next_textarea_with_words()
        if textarea is not None:
            return textarea._paragraphs[0]._textlines[0]._words[0]
        buffer = self._get_buffer()
        if len(buffer) == 0:
            return None
        return buffer[0]

    def _get_next_textarea_with_words(
        self
        ) -> TextArea | None:
        textarea = self._next_textarea
        while textarea is not None:
            if not textarea._is_empty():
                return textarea
            textarea = textarea._next_textarea
        return None

    def _is_empty(
        self
        ) -> bool:
        if len(self._paragraphs) == 0:
            return True
        if len(self._paragraphs[0]._textlines) == 0:
            return True
        if len(self._paragraphs[0]._textlines[0]._words) == 0:
            return True
        return False

    def _build_current_page_fragments(
        self,
        current_page: int
        ) -> None:
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
                        page_number_width += font._get_char_width(
                            char, fragment._font_size)
                fragment._adjust_width(page_number_width)
                if (fragment._word is not None
                    and fragment._word._textline is not None
                    and fragment._word._textline._paragraph is not None
                    and fragment._word._textline._paragraph._textarea is not None):
                    paragraph = fragment._word._textline._paragraph
                    paragraph._adjust_words_between_textlines()
                    textarea = fragment._word._textline._paragraph._textarea
                    textarea._move_words_between_areas()

    def _build_total_pages_fragments(
        self,
        total_pages: int
        ) -> None:
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
                        new_length += font._get_char_width(
                            char, fragment._font_size)
                fragment._adjust_width(new_length)
                if (fragment._word is not None
                    and fragment._word._textline is not None
                    and fragment._word._textline._paragraph is not None
                    and fragment._word._textline._paragraph._textarea is not None):
                    paragraph = fragment._word._textline._paragraph
                    paragraph._adjust_words_between_textlines()
                    textarea = fragment._word._textline._paragraph._textarea
                    textarea._move_words_between_areas()

    def link_textarea(
        self,
        next_textarea: TextArea
        ) -> None:
        last_textarea = self
        while last_textarea._next_textarea is not None:
            last_textarea = last_textarea._next_textarea
        last_textarea._next_textarea = next_textarea
        next_textarea._buffer = last_textarea._buffer
        last_textarea._buffer = deque()
        self._move_words_in_all_linked_areas()

    def set_width(
        self,
        new_width: float
        ) -> None:
        self._width = new_width
        for paragraph in self._paragraphs:
            paragraph._set_paragraph_width(new_width)
        self._move_words_in_all_linked_areas()

    def _empty_textlines_and_paragraphs_from_line(
        self,
        textline_index: int,
        paragraph_index: int
    ) -> None:
        removed_words = deque()
        first_paragraph_to_remove_words_from = self._paragraphs[paragraph_index]
        while (textline_index
               < len(first_paragraph_to_remove_words_from._textlines)):
            texline = (self._paragraphs[paragraph_index]
                           ._textlines[textline_index])
            removed_words.extend(texline._remove_line_from_text_area())
            textline_index += 1
        if (len(self._paragraphs) > 0
            and (first_paragraph_to_remove_words_from
                    == self._paragraphs[paragraph_index])):
            paragraph_index += 1
        while paragraph_index < len(self._paragraphs):
            paragraph = self._paragraphs[paragraph_index]
            removed_words.extend(paragraph._remove_paragraph_from_text_area())
            # paragraph_index += 1
        textarea_to_empty = self._next_textarea
        while textarea_to_empty is not None:
            removed_words.extend(textarea_to_empty._empty_textarea())
            textarea_to_empty = textarea_to_empty._next_textarea
        word_buffer = self._get_buffer()
        word_buffer.extendleft(removed_words)

    def _empty_textarea(
        self
    ) -> deque[Word]:
        removed_words = deque()
        while len(self._paragraphs) > 0:
            paragraph = self._paragraphs[0]
            removed_words.extend(paragraph._remove_paragraph_from_text_area())
        return removed_words




# CREATE WORDS
def create_words(
    unicode_text: str,
    current_font: Font,
    current_font_size: float,
    current_font_color: tuple[float, float, float],
    current_page_dummy: str | None = None,
    total_pages_dummy: str | None = None,
    page_num_dummy_length: int | None = None,
    page_number_presentation: Callable[[int], str] | None = None,
) -> list[Word]:
    char_idx = 0
    words: list[Word] = []
    while char_idx < len(unicode_text):
        (fragment, increment) = generate_fragment_with_increment(
            unicode_text,
            char_idx,
            current_font,
            current_font_size,
            current_font_color,
            current_page_dummy,
            total_pages_dummy,
            page_num_dummy_length,
            page_number_presentation)
        if fragment._chars in {"\n", "\t", " "}:
            word = Word()
            word._add_fragment(fragment)
            words.append(word)
        else:
            if len(words) == 0:
                words.append(Word())
            if words[-1]._is_extendable:
                words[-1]._add_fragment(fragment)
            else:
                word = Word()
                word._add_fragment(fragment)
                words.append(word)
        char_idx += increment
    return words

def generate_fragment_with_increment(
        unicode_text: str,
        char_idx: int,
        current_font: Font,
        current_font_size: float,
        current_font_color: tuple[float, float, float],
        current_page_dummy: str | None,
        total_pages_dummy: str | None,
        page_num_dummy_length: int | None,
        page_number_presentation: Callable[[int], str] | None,
    ) -> tuple[Fragment, int]:
    if is_carriage_return_with_new_line(
        unicode_text,
        char_idx,
        ):
        fragment = generate_new_line_fragment(
            current_font,
            current_font_size,
            current_font_color,
        )
        return (fragment, 2)
    if is_only_carriage_return(unicode_text, char_idx):
        fragment = generate_new_line_fragment(
            current_font,
            current_font_size,
            current_font_color,
        )
        return (fragment, 1)
    if (current_page_dummy is not None
        and page_num_dummy_length is not None
        and page_number_presentation is not None
        and is_string_current_page_dummy(
            unicode_text,
            char_idx,
            current_page_dummy)):
        (fragment, increment) = generate_current_page_fragment(
            current_font,
            current_font_size,
            current_font_color,
            current_page_dummy,
            page_num_dummy_length,
            page_number_presentation)
        return (fragment, increment)
    if (total_pages_dummy is not None
        and page_num_dummy_length is not None
        and page_number_presentation is not None
        and is_string_total_pages_dummy(
            unicode_text,
            char_idx,
            total_pages_dummy)):
        (fragment, increment) = generate_total_pages_fragment(
            current_font,
            current_font_size,
            current_font_color,
            total_pages_dummy,
            page_num_dummy_length,
            page_number_presentation)
        return (fragment, increment)
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_width = current_font._get_char_width(
        unicode_text[char_idx], current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    fragment = Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        unicode_text[char_idx],
        current_font.name,
        current_font_size,
        current_font_color)
    increment = 1
    return (fragment, increment)

def is_carriage_return_with_new_line(
    unicode_text: str,
    char_idx: int,
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

def is_only_carriage_return(
    unicode_text: str,
    char_idx: int
    ) -> bool:
    if unicode_text[char_idx] == "\r":
        return True
    return False

def is_string_current_page_dummy(
    unicode_text: str,
    char_idx: int,
    current_page_dummy: str,
) -> bool:
    start = char_idx
    end = start + len(current_page_dummy)
    if unicode_text[start:end] == current_page_dummy:
        return True
    return False

def is_string_total_pages_dummy(
    unicode_text: str,
    char_idx: int,
    total_pages_dummy: str
) -> bool:
    start = char_idx
    end = start + len(total_pages_dummy)
    if unicode_text[start:end] == total_pages_dummy:
        return True
    return False

def generate_current_page_fragment(
    current_font: Font,
    current_font_size: float,
    current_font_color: tuple[float, float, float],
    current_page_dummy: str,
    page_num_dummy_length: int,
    page_number_presentation: Callable[[int], str] = (str),
    ) -> tuple[Fragment, int]:
    fragment_width = (page_num_dummy_length
                        * current_font._get_char_width("0", current_font_size))
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    fragment = Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        current_page_dummy,
        current_font.name,
        current_font_size,
        current_font_color)
    fragment._page_number_presentation = (page_number_presentation)
    fragment._is_current_page_dummy = True
    increment = len(current_page_dummy)
    return (fragment, increment)

def generate_total_pages_fragment(
    current_font: Font,
    current_font_size: float,
    current_font_color: tuple[float, float, float],
    total_pages_dummy: str,
    page_num_dummy_length: int,
    page_number_presentation: Callable[[int], str] = (str),
    ) -> tuple[Fragment, int]:
    fragment_width = (page_num_dummy_length
                        * current_font._get_char_width("0", current_font_size))
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    fragment = Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        total_pages_dummy,
        current_font.name,
        current_font_size,
        current_font_color)
    fragment._page_number_presentation = (page_number_presentation)
    fragment._is_total_pages_dummy = True
    increment = len(total_pages_dummy)
    return (fragment, increment)

def generate_new_line_fragment(
    current_font: Font,
    current_font_size: float,
    current_font_color: tuple[float, float, float],
    ) -> Fragment:
    fragment_width = 0.0
    fragment_height = current_font._get_line_height(
        current_font_size)
    fragment_ascent = current_font._get_ascent(
        current_font_size)
    return Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        "\n",
        current_font.name,
        current_font_size,
        current_font_color)
