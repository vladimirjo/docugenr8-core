"""build_dto module.

This module provides functionality to build Data Transfer Objects (DTOs) for
transferring document information between modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from docugenr8_core.document import Document

from docugenr8_shared.dto import Dto
from docugenr8_shared.dto import DtoArc
from docugenr8_shared.dto import DtoBezier
from docugenr8_shared.dto import DtoCurve
from docugenr8_shared.dto import DtoEllipse
from docugenr8_shared.dto import DtoFont
from docugenr8_shared.dto import DtoFragment
from docugenr8_shared.dto import DtoPage
from docugenr8_shared.dto import DtoParagraph
from docugenr8_shared.dto import DtoPoint
from docugenr8_shared.dto import DtoRectangle
from docugenr8_shared.dto import DtoRotation
from docugenr8_shared.dto import DtoSkew
from docugenr8_shared.dto import DtoTextArea
from docugenr8_shared.dto import DtoTextBox
from docugenr8_shared.dto import DtoTextLine
from docugenr8_shared.dto import DtoWord

from docugenr8_core.shapes import Arc
from docugenr8_core.shapes import Bezier
from docugenr8_core.shapes import Curve
from docugenr8_core.shapes import Ellipse
from docugenr8_core.shapes import Point
from docugenr8_core.shapes import Rectangle
from docugenr8_core.shapes import Rotation
from docugenr8_core.shapes import Skew
from docugenr8_core.text_area.fragment import Fragment
from docugenr8_core.text_area.paragraph import Paragraph
from docugenr8_core.text_area.textarea import TextArea
from docugenr8_core.text_area.textline import TextLine
from docugenr8_core.text_area.word import Word
from docugenr8_core.text_box import TextBox


def dto_build(doc: Document) -> Dto:
    dto = Dto()
    for font_name, font in doc.fonts.items():
        dto_font = DtoFont(font_name, font.raw_data)
        dto.fonts.append(dto_font)
    for page_number, page in enumerate(doc.pages):
        dto_page = DtoPage(page._width, page._height)
        dto.pages.append(dto_page)
        for content in page._contents:
            match content:
                case TextArea():
                    content._build_current_page_fragments(page_number + 1)
                    content._build_total_pages_fragments(len(doc.pages))
                    dto_page.contents.append(generate_dto_text_area(content))
                case TextBox():
                    content._text_area._build_current_page_fragments(page_number + 1)
                    content._text_area._build_total_pages_fragments(len(doc.pages))
                    dto_page.contents.append(generate_dto_textbox(content))
                case Curve():
                    dto_page.contents.append(generate_dto_curve(content))
                case Rectangle():
                    dto_page.contents.append(generate_dto_rectangle(content))
                case Arc():
                    dto_page.contents.append(generate_dto_arc(content))
                case Ellipse():
                    dto_page.contents.append(generate_dto_ellipse(content))
                case _:
                    raise TypeError("Invalid content type to generate Dto in Core module.")
    return dto


def generate_dto_ellipse(content: Ellipse) -> DtoEllipse:
    dto_ellipse = DtoEllipse(
        content.x,
        content.y,
        content.width,
        content.height,
        content.fill_color,
        content.line_color,
        content.line_width,
        content.line_pattern,
    )
    for transformation in content.transformations:
        if isinstance(transformation, Rotation):
            dto_ellipse.transformations.append(
                DtoRotation(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.degrees,
                )
            )
        elif isinstance(transformation, Skew):
            dto_ellipse.transformations.append(
                DtoSkew(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.vertical_degrees,
                    transformation.horizontal_degrees,
                )
            )
        else:
            raise TypeError("The transformation is not a valid object.")

    return dto_ellipse


def generate_dto_arc(content: Arc) -> DtoArc:
    dto_arc = DtoArc(
        content.x1,
        content.y1,
        content.x2,
        content.y2,
        content.line_color,
        content.line_width,
        content.line_pattern,
    )
    for transformation in content.transformations:
        if isinstance(transformation, Rotation):
            dto_arc.transformations.append(
                DtoRotation(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.degrees,
                )
            )
        elif isinstance(transformation, Skew):
            dto_arc.transformations.append(
                DtoSkew(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.vertical_degrees,
                    transformation.horizontal_degrees,
                )
            )
        else:
            raise TypeError("The transformation is not a valid object.")
    return dto_arc


def generate_dto_rectangle(content: Rectangle) -> DtoRectangle:
    dto_rectangle = DtoRectangle(
        content.x,
        content.y,
        content.width,
        content.height,
        content.rounded_corner_top_left,
        content.rounded_corner_top_right,
        content.rounded_corner_bottom_left,
        content.rounded_corner_bottom_right,
        content.fill_color,
        content.line_color,
        content.line_width,
        content.line_pattern,
    )
    for transformation in content.transformations:
        if isinstance(transformation, Rotation):
            dto_rectangle.transformations.append(
                DtoRotation(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.degrees,
                )
            )
        elif isinstance(transformation, Skew):
            dto_rectangle.transformations.append(
                DtoSkew(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.vertical_degrees,
                    transformation.horizontal_degrees,
                )
            )
        else:
            raise TypeError("The transformation is not a valid object.")
    return dto_rectangle


def generate_dto_curve(content: Curve) -> DtoCurve:
    if not isinstance(content.path[0], Point):
        raise TypeError("First point in the path must have only x and y coordinates.")
    dto_curve = DtoCurve(
        content.path[0].x,
        content.path[0].y,
        content.fill_color,
        content.line_color,
        content.line_width,
        content.line_pattern,
        content.line_closed,
    )
    for index, point in enumerate(content.path):
        if index == 0:
            continue
        if isinstance(point, Point):
            dto_curve.path.append(DtoPoint(point.x, point.y))
        elif isinstance(point, Bezier):
            dto_curve.path.append(
                DtoBezier(
                    point.cp1_x,
                    point.cp1_y,
                    point.cp2_x,
                    point.cp2_y,
                    point.endp_x,
                    point.endp_y,
                )
            )
        else:
            raise TypeError("The point in the path is not a valid object.")
    for transformation in content.transformations:
        if isinstance(transformation, Rotation):
            dto_curve.transformations.append(
                DtoRotation(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.degrees,
                )
            )
        elif isinstance(transformation, Skew):
            dto_curve.transformations.append(
                DtoSkew(
                    transformation.x_origin,
                    transformation.y_origin,
                    transformation.vertical_degrees,
                    transformation.horizontal_degrees,
                )
            )
        else:
            raise TypeError("The transformation is not a valid object.")
    return dto_curve


def generate_dto_textbox(textbox: TextBox) -> DtoTextBox:
    dto_textbox = DtoTextBox(textbox._x, textbox._y, textbox._width, textbox._height)
    dto_textbox._fill_color = textbox._fill_color
    dto_textbox._line_color = textbox._line_color
    dto_textbox._line_width = textbox._line_width
    dto_textbox._line_pattern = textbox._line_pattern
    dto_textbox._text_area = generate_dto_text_area(textbox._text_area)
    return dto_textbox


def _generate_dto_fragment(
    x: float,
    y: float,
    dto_word: DtoWord,
    fragment: Fragment,
) -> DtoFragment:
    """Generate Dto fragment object. Dto fragment object is the smallest posible object that holds one character.

    Args:
        x (float): x position of the fragment
        y (float): y position of the fragment
        dto_word (DtoWord): Parent Dto word object
        fragment (Fragment): Word fragment from text area

    Returns:
        DtoFragment: Dto fragment object
    """
    dto_fragment = DtoFragment(x, y, dto_word)
    dto_fragment.width = fragment._width
    dto_fragment.height = fragment._height
    dto_fragment.baseline = y + fragment._ascent
    dto_fragment.chars = fragment._chars
    dto_fragment.font_name = fragment._font_name
    dto_fragment.font_size = fragment._font_size
    dto_fragment.font_color = fragment._font_color
    return dto_fragment


def _generate_dto_word(
    x: float,
    y: float,
    dto_textline: DtoTextLine,
    word: Word,
) -> DtoWord:
    """_summary_.

    Args:
        x (float): _description_
        y (float): _description_
        dto_textline (DtoTextLine): _description_
        word (Word): _description_

    Returns:
        DtoWord: _description_
    """
    dto_word = DtoWord(x, y, dto_textline)
    dto_word.width = word._width
    dto_word.height = word._height
    dto_word.baseline = y + word._ascent
    dto_word.justify_space = word._justify_space
    for fragment in word._fragments:
        dto_fragment = _generate_dto_fragment(x, y + (word._ascent - fragment._ascent), dto_word, fragment)
        dto_word.fragments.append(dto_fragment)
        dto_word.textline.fragments.append(dto_fragment)
        dto_word.textline.paragraph.fragments.append(dto_fragment)
        dto_word.textline.paragraph.text_area.fragments.append(dto_fragment)
        x += dto_fragment.width
    return dto_word


def _generate_dto_textline(
    x: float, y: float, dto_paragraph: DtoParagraph, textline: TextLine, justify_padding_after: float
) -> DtoTextLine:
    dto_textline = DtoTextLine(x, y, dto_paragraph, justify_padding_after)
    dto_textline.width = textline._width
    dto_textline.height = textline._height
    dto_textline.baseline = y + textline._ascent
    dto_textline.space_after = textline._leading
    dto_textline.paragraph_h_align = dto_paragraph.h_align
    x_offset = 0.0
    justify_space = 0.0
    match dto_textline.paragraph_h_align:
        case "left":
            pass
        case "right":
            x_offset = textline._available_width
        case "center":
            x_offset = (textline._available_width) / 2
        case "justify":
            justify_space = _calculate_justify_space(textline)
    x += x_offset
    for word in textline._words:
        dto_word = _generate_dto_word(x, y + (textline._ascent - word._ascent), dto_textline, word)
        dto_textline.words.append(dto_word)
        if word._chars == " ":
            x += dto_word.width + justify_space
        else:
            x += dto_word.width
    return dto_textline


def _generate_dto_paragraph(
    x: float,
    y: float,
    paragraph: Paragraph,
    dto_text_area: DtoTextArea,
    should_distrubute_space_in_lines: bool,
    height_diff: float,
    last_paragraph: bool,
) -> DtoParagraph:
    dto_paragraph = DtoParagraph(x, y, dto_text_area)
    dto_paragraph.width = paragraph._width
    dto_paragraph.height = paragraph._height
    dto_paragraph.chars = paragraph._get_chars()
    dto_paragraph.tab_size = paragraph._tab_size
    dto_paragraph.line_height_ratio = paragraph._line_height_ratio
    dto_paragraph.first_line_indent = paragraph._first_line_indent
    dto_paragraph.hanging_indent = paragraph._hanging_indent
    dto_paragraph.left_indent = paragraph._left_indent
    dto_paragraph.right_indent = paragraph._right_indent
    dto_paragraph.space_before = paragraph._space_before
    dto_paragraph.space_after = paragraph._space_after
    dto_paragraph.h_align = paragraph._h_align
    num_of_lines_in_paragraph = len(paragraph._textlines)
    y += dto_paragraph.space_before
    for line in paragraph._textlines:
        line_justify_padding = 0.0
        if should_distrubute_space_in_lines:
            if not last_paragraph:
                line_justify_padding = height_diff / num_of_lines_in_paragraph
            else:
                line_justify_padding = height_diff / (num_of_lines_in_paragraph - 1)
        if line._is_first_line_in_paragraph():
            x_offset = x + dto_paragraph.left_indent + dto_paragraph.first_line_indent
        else:
            x_offset = x + dto_paragraph.left_indent + dto_paragraph.hanging_indent
        dto_textline = _generate_dto_textline(
            x_offset,
            y,
            dto_paragraph,
            line,
            line_justify_padding,
        )
        dto_paragraph.textlines.append(dto_textline)
        y += dto_textline.height
        y += dto_textline.space_after
        y += dto_textline.justify_padding_after
    y += dto_paragraph.space_after
    dto_paragraph.height += height_diff
    return dto_paragraph


def generate_dto_text_area(text_area: TextArea) -> DtoTextArea:
    y_offset: float = 0.0
    between_paragraphs_padding: float = 0.0
    should_distrubute_space_in_lines: bool = False
    num_of_lines_in_text_area: int = 0
    # ******************************
    match text_area._v_align:
        case "top":
            pass
        case "bottom":
            y_offset += text_area._available_height
        case "center":
            y_offset += text_area._available_height / 2
        case "justify-paragraphs":
            between_paragraphs_padding = text_area._available_height / (len(text_area._paragraphs) - 1)
        case "justify-lines":
            should_distrubute_space_in_lines = True
            for paragraph in text_area._paragraphs:
                num_of_lines_in_text_area += len(paragraph._textlines)
        case _:
            raise ValueError("Invalid value for vertical alignment.")
    # ******************************
    dto_text_area = DtoTextArea(text_area._x, text_area._y, text_area._width, text_area._height)
    dto_text_area.height_empty_space = text_area._available_height
    dto_text_area.v_align = text_area._v_align

    y = text_area._y + y_offset
    for paragraph in text_area._paragraphs:
        height_diff = 0.0
        last_paragraph = False
        if should_distrubute_space_in_lines:
            if paragraph != text_area._paragraphs[-1]:
                height_diff = (len(paragraph._textlines) / num_of_lines_in_text_area) * text_area._available_height
            else:
                height_diff = (
                    (len(paragraph._textlines) - 1) / num_of_lines_in_text_area
                ) * text_area._available_height
                last_paragraph = True
        # ******************************
        dto_paragraph = _generate_dto_paragraph(
            text_area._x, y, paragraph, dto_text_area, should_distrubute_space_in_lines, height_diff, last_paragraph
        )
        dto_text_area.paragraphs.append(dto_paragraph)
        # ******************************
        y += dto_paragraph.height
        if paragraph != text_area._paragraphs[-1]:
            y += between_paragraphs_padding
    return dto_text_area


def _calculate_justify_space(textline: TextLine) -> float:
    if _textline_has_only_empty_spaces(textline):
        return 0
    if _textline_has_only_one_word(textline):
        return 0
    if textline._is_last_line_in_paragraph():
        return 0
    if textline._available_width == 0:
        return 0
    start_pos = _get_index_first_not_empty_space_word(textline)
    end_pos = _get_index_last_not_empty_space_word(textline)
    num_inner_words = 0
    for i in range(start_pos, end_pos):
        if textline._words[i]._chars == " ":
            num_inner_words += 1
    if num_inner_words == 0:
        return 0
    return textline._available_width / num_inner_words


def _textline_has_only_empty_spaces(textline: TextLine) -> bool:
    return all(word._chars in {" ", "\t", "\n"} for word in textline._words)


def _textline_has_only_one_word(textline: TextLine) -> bool:
    if len(textline._words) <= 1:
        return True
    return False


def _get_index_first_not_empty_space_word(textline: TextLine) -> int:
    for index, word in enumerate(textline._words):
        if word._chars not in {" ", "\t", "\n"}:
            return index
    raise ValueError("Could not obtain index for the first word that" " is not empty space.")


def _get_index_last_not_empty_space_word(textline: TextLine) -> int:
    for index, word in enumerate(reversed(textline._words)):
        if word._chars not in {" ", "\t", "\n"}:
            return len(textline._words) - index - 1
    raise ValueError("Could not obtain index for the last word that" " is not empty space.")
