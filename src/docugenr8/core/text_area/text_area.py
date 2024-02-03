from __future__ import annotations
from typing import TYPE_CHECKING
from collections import deque


if TYPE_CHECKING:
    from ..document import Document
    from ..font import Font

from .text_line import TextLine
from .paragraph import Paragraph
from .word import Word
from .fragment import Fragment

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

        # late binding when adding text
        self.current_font: None | Font = None
        self.current_font_size: float = 0.0
        self.current_font_color: tuple[int, int, int] = (0, 0, 0)

        # words to fill in with page numbers
        self.words_with_current_page_fragments: list[Word] = []
        self.words_with_total_pages_fragments: list[Word] = []

        self.available_height = height
        self.paragraphs: deque[Paragraph] = deque()
        self.buffer: deque[Word] = deque()
        self.next_textarea: None | TextArea = None
        self.accepts_additional_words: bool = True

    def add_text(
        self,
        unicode_text: str,
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
        words = self._create_words(
            unicode_text,
            self.current_font,
            self.current_font_size,
            self.current_font_color,
        )
        self._establish_link_with_last_word(words[0])
        self._insert_words_into_buffer(words)
        self._transfer_words_from_buffer_to_textarea()


    def _insert_words_into_buffer(self, words:list[Word]) -> None:
        buffer = self._get_buffer()
        buffer.extend(words)

    def _transfer_words_from_buffer_to_textarea(self) -> None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None:
            return
        textarea.move_words_between_textareas_and_buffer()

    def _create_words(
        self,
        unicode_text: str,
        font: Font,
        font_size: float,
        font_color: tuple[int, int, int],
    ) -> list[Word]:
        char_idx = 0
        words: list[Word] = []
        while char_idx < len(unicode_text):
            (fragment, increment) = self._generate_fragment_with_increment(
                unicode_text, char_idx, font, font_size, font_color
            )
            if fragment.chars in {"\n", "\t", " "}:
                word = Word()
                word.add_fragment(fragment)
                if len(words) > 0:
                    word.prev_word = words[-1]
                    words[-1].next_word = word
                words.append(word)
            else:
                if len(words) == 0:
                    words.append(Word())
                if words[-1].accepts_additional_fragments == True:
                    words[-1].add_fragment(fragment)
                else:
                    word = Word()
                    word.add_fragment(fragment)
                    if len(words) > 0:
                        word.prev_word = words[-1]
                        words[-1].next_word = word
                    words.append(word)
            char_idx += increment
        return words

    def _establish_link_with_last_word(self, first_word: Word) -> None:
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

    def _set_buffer(self, words: deque[Word]) -> None:
        current_textarea = self
        while current_textarea.next_textarea is not None:
            current_textarea = current_textarea.next_textarea
        current_textarea.buffer = words

    def _get_buffer(self) -> deque[Word]:
        current_textarea = self
        while current_textarea.next_textarea is not None:
            current_textarea = current_textarea.next_textarea
        return current_textarea.buffer

    def _get_the_last_word_from_textareas(self) -> Word | None:
        textarea = self._get_the_first_textarea_to_accept_words()
        if textarea is None or textarea._is_empty():
            return None
        return textarea.paragraphs[-1].lines[-1].words[-1]

    def _generate_fragment_with_increment(
        self,
        unicode_text: str,
        char_idx: int,
        font: Font,
        font_size: float,
        font_color: tuple[int, int, int],
    ) -> tuple[Fragment, int]:
        if self._is_string_current_page_dummy(unicode_text, char_idx):
            (fragment, increment) = self._generate_current_page_fragment(
                font, font_size, font_color
            )
            return (fragment, increment)
        if self._is_string_total_pages_dummy(unicode_text, char_idx):
            (fragment, increment) = self._generate_total_pages_fragment(
                font, font_size, font_color
            )
            return (fragment, increment)
        fragment = Fragment(unicode_text[char_idx], font, font_size, font_color)
        increment = 1
        return (fragment, increment)

    def _is_string_current_page_dummy(self, unicode_text: str, char_idx: int) -> bool:
        current_page_dummy = self.document.settings.page_num_current_page_dummy
        start = char_idx
        end = start + len(current_page_dummy)
        if unicode_text[start:end] == current_page_dummy:
            return True
        return False

    def _is_string_total_pages_dummy(self, unicode_text: str, char_idx: int) -> bool:
        total_pages_dummy = self.document.settings.page_num_total_pages_dummy
        start = char_idx
        end = start + len(total_pages_dummy)
        if unicode_text[start:end] == total_pages_dummy:
            return True
        return False

    def _generate_current_page_fragment(
        self, font: Font, font_size: float, font_color: tuple[int, int, int]
    ) -> tuple[Fragment, int]:
        current_page_dummy = self.document.settings.page_num_current_page_dummy
        dummy_length = self.document.settings.page_num_dummy_length
        presentation = self.document.settings.page_num_presentation
        fragment = Fragment(current_page_dummy, font, font_size, font_color)
        fragment.set_page_number_presentation_and_length(dummy_length, presentation)
        fragment.is_current_page_dummy = True
        # self.fragments_with_page_number.append(fragment)
        increment = len(self.document.settings.page_num_current_page_dummy)
        return (fragment, increment)

    def _generate_total_pages_fragment(
        self, font: Font, font_size: float, font_color: tuple[int, int, int]
    ) -> tuple[Fragment, int]:
        total_pages_dummy = self.document.settings.page_num_total_pages_dummy
        dummy_length = self.document.settings.page_num_dummy_length
        presentation = self.document.settings.page_num_presentation
        fragment = Fragment(total_pages_dummy, font, font_size, font_color)
        fragment.set_page_number_presentation_and_length(dummy_length, presentation)
        fragment.is_total_pages_dummy = True
        # self.fragments_with_page_number.append(fragment)
        increment = len(self.document.settings.page_num_current_page_dummy)
        return (fragment, increment)

    def _get_the_first_textarea_to_accept_words(self) -> TextArea | None:
        current_textarea = self
        while current_textarea.accepts_additional_words == False:
            if current_textarea.next_textarea is not None:
                current_textarea = current_textarea.next_textarea
            else:
                return None
        return current_textarea

    def move_words_between_textareas_and_buffer(self):
        if self.available_height > 0.0:
            self.pull_next_available_word()
        if self.available_height < 0.0:
            self.accepts_additional_words = False
            self.push_excess_words_to_next_available_place()

    def pull_next_available_word(self):
        while self.available_height >= 0.0:
            next_word = self.get_next_word()
            if next_word is None:
                return

            # current page and total pages
            if next_word.has_current_page_fragments:
                self.words_with_current_page_fragments.append(next_word)
            if next_word.has_total_pages_fragments:
                self.words_with_total_pages_fragments.append(next_word)
            # ###########################

            self.paragraph_generator_when_pulling_words(next_word)
            self.remove_word(next_word)
            self.paragraphs[-1].append_word_right(next_word)

    def push_excess_words_to_next_available_place(self) -> deque[Word] | None:
        textline_to_push = self.paragraphs[-1].lines[-1]
        while self.available_height < 0.0:
            if self.next_textarea is not None:
                self.next_textarea.paragraph_generator_when_pushing_words(
                    textline_to_push
                )
                words_to_push = textline_to_push.remove_line_and_get_words()
                self.next_textarea.add_words_front_to_textarea(words_to_push)
            else:
                words_to_push = textline_to_push.remove_line_and_get_words()
                words_to_push.extend(self._get_buffer())
                self._set_buffer(words_to_push)
            if len(self.paragraphs) == 0:
                return
            textline_to_push = self.paragraphs[-1].lines[-1]
        if self.next_textarea is not None:
            self.next_textarea.move_words_between_textareas_and_buffer()

    def paragraph_generator_when_pulling_words(self, next_word: Word):
        next_paragraph = next_word.get_paragraph()
        if next_paragraph is None:
            if len(self.paragraphs) == 0:
                self.paragraphs.append(Paragraph(self))
            if self.paragraphs[-1].ends_with_br == True:
                self.paragraphs.append(Paragraph(self))
            return
        if next_word.is_first_word_in_paragraph():
            if next_word.textline is not None:
                next_word.textline.set_non_first_left_indent()
            paragraph = Paragraph(self)
            self.paragraphs.append(paragraph)
            paragraph._copy_paragraph_parameters_from(next_paragraph)
            paragraph.next_linked_paragraph = next_paragraph
            next_paragraph.prev_linked_paragraph = paragraph
            return
        if next_word.is_last_word_in_paragraph():
            self.paragraphs[-1].next_linked_paragraph = None
            next_paragraph.prev_linked_paragraph = None
            return
        if self.paragraphs[-1].next_linked_paragraph != next_paragraph:
            self.paragraphs[-1].next_linked_paragraph = next_paragraph
            next_paragraph.prev_linked_paragraph = self.paragraphs[-1]
            return

    def paragraph_generator_when_pushing_words(
        self, textline_to_push: TextLine
    ):
        if (
            len(self.paragraphs) == 0
            and textline_to_push.is_first_line_in_paragraph()
        ):
            new_paragraph = Paragraph(self)
            self.paragraphs.append(new_paragraph)
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = None
            return
        if (
            len(self.paragraphs) == 0
            and not textline_to_push.is_first_line_in_paragraph()
        ):
            new_paragraph = Paragraph(self)
            self.paragraphs.append(new_paragraph)
            if textline_to_push.paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(
                    textline_to_push.paragraph
                )
            new_paragraph.prev_linked_paragraph = textline_to_push.paragraph
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = new_paragraph
            return
        if textline_to_push.is_last_line_in_paragraph():
            new_paragraph = Paragraph(self)
            self.paragraphs.appendleft(new_paragraph)
            if textline_to_push.paragraph is not None:
                new_paragraph._copy_paragraph_parameters_from(
                    textline_to_push.paragraph
                )
            new_paragraph.prev_linked_paragraph = textline_to_push.paragraph
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = new_paragraph
        if textline_to_push.is_first_line_in_paragraph():
            self.paragraphs[0].prev_linked_paragraph = None
            if textline_to_push.paragraph is not None:
                textline_to_push.paragraph.next_linked_paragraph = None

    def remove_word(self, next_word: Word):
        if next_word.textline is None:
            self._get_buffer().remove(next_word)
        else:
            next_word.remove_page_number()
            next_word.remove_from_line()

    def add_words_front_to_textarea(self, words: deque[Word]):
        while len(words) > 0:
            word = words.popleft()
            self.paragraphs[0].append_word_left(word)
        self.paragraphs[0]._reallocate_words_in_paragraph()

    def get_next_word(self) -> Word | None:
        """gets the next word from either next paragraph if there is one,
        or from the words buffer
        """
        textarea = self._get_next_textarea_with_words()
        if textarea is not None:
            return textarea.paragraphs[0].lines[0].words[0]
        else:
            buffer = self._get_buffer()
            if len(buffer) == 0:
                return None
            return buffer[0]

    def _get_next_textarea_with_words(self) -> TextArea | None:
        textarea = self.next_textarea
        while textarea is not None:
            if not textarea._is_empty():
                return textarea
            textarea = textarea.next_textarea
        return None

    def _is_empty(self) -> bool:
        if len(self.paragraphs) == 0:
            return True
        if len(self.paragraphs[0].lines) == 0:
            return True
        if len(self.paragraphs[0].lines[0].words) == 0:
            return True
        return False
