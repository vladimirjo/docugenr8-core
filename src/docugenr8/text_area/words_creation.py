from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8.font import Font

from collections.abc import Callable

from .fragment import Fragment
from .word import Word


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
            page_number_presentation,
        )
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
    if (
        current_page_dummy is not None
        and page_num_dummy_length is not None
        and page_number_presentation is not None
        and is_string_current_page_dummy(unicode_text, char_idx, current_page_dummy)
    ):
        (fragment, increment) = generate_current_page_fragment(
            current_font,
            current_font_size,
            current_font_color,
            current_page_dummy,
            page_num_dummy_length,
            page_number_presentation,
        )
        return (fragment, increment)
    if (
        total_pages_dummy is not None
        and page_num_dummy_length is not None
        and page_number_presentation is not None
        and is_string_total_pages_dummy(unicode_text, char_idx, total_pages_dummy)
    ):
        (fragment, increment) = generate_total_pages_fragment(
            current_font,
            current_font_size,
            current_font_color,
            total_pages_dummy,
            page_num_dummy_length,
            page_number_presentation,
        )
        return (fragment, increment)
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_width = current_font._get_char_width(unicode_text[char_idx], current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    fragment = Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        unicode_text[char_idx],
        current_font.name,
        current_font_size,
        current_font_color,
    )
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
    if carriage_return == "\r" and new_line == "\n":
        return True
    return False


def is_only_carriage_return(unicode_text: str, char_idx: int) -> bool:
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


def is_string_total_pages_dummy(unicode_text: str, char_idx: int, total_pages_dummy: str) -> bool:
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
    fragment_width = page_num_dummy_length * current_font._get_char_width("0", current_font_size)
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    fragment = Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        current_page_dummy,
        current_font.name,
        current_font_size,
        current_font_color,
    )
    fragment._page_number_presentation = page_number_presentation
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
    fragment_width = page_num_dummy_length * current_font._get_char_width("0", current_font_size)
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    fragment = Fragment(
        fragment_height,
        fragment_width,
        fragment_ascent,
        total_pages_dummy,
        current_font.name,
        current_font_size,
        current_font_color,
    )
    fragment._page_number_presentation = page_number_presentation
    fragment._is_total_pages_dummy = True
    increment = len(total_pages_dummy)
    return (fragment, increment)


def generate_new_line_fragment(
    current_font: Font,
    current_font_size: float,
    current_font_color: tuple[float, float, float],
) -> Fragment:
    fragment_width = 0.0
    fragment_height = current_font._get_line_height(current_font_size)
    fragment_ascent = current_font._get_ascent(current_font_size)
    return Fragment(
        fragment_height, fragment_width, fragment_ascent, "\n", current_font.name, current_font_size, current_font_color
    )
