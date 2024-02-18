from docugenr8_shared.dto import DtoFragment
from docugenr8_shared.dto import DtoParagraph
from docugenr8_shared.dto import DtoTextArea
from docugenr8_shared.dto import DtoTextLine
from docugenr8_shared.dto import DtoWord

from .text_area.fragment import Fragment
from .text_area.paragraph import Paragraph
from .text_area.text_area import TextArea
from .text_area.text_line import TextLine
from .text_area.word import Word


def _generate_dto_fragment(
    x: float,
    y: float,
    dto_word: DtoWord,
    fragment: Fragment,
    ) -> DtoFragment:
    dto_fragment = DtoFragment(
        x,
        y,
        dto_word
    )
    dto_fragment.width = fragment.width
    dto_fragment.height = fragment.height
    dto_fragment.baseline = y + fragment.ascent
    dto_fragment.chars = fragment.chars
    dto_fragment.font_name = fragment.font_name
    dto_fragment.font_size = fragment.font_size
    dto_fragment.font_color = fragment.font_color
    return dto_fragment

def _generate_dto_word(
    x: float,
    y: float,
    dto_text_line: DtoTextLine,
    word: Word,
    ) -> DtoWord:
    dto_word = DtoWord(x, y, dto_text_line)
    dto_word.width = word.width
    dto_word.height = word.height
    dto_word.baseline = y + word.ascent
    dto_word.justify_padding_after = word.justify_space
    for fragment in word.fragments:
        dto_fragment = _generate_dto_fragment(
            x,
            y + (word.ascent - fragment.ascent),
            dto_word,
            fragment)
        dto_word.fragments.append(dto_fragment)
        dto_word.text_line.fragments.append(dto_fragment)
        dto_word.text_line.paragraph.fragments.append(dto_fragment)
        dto_word.text_line.paragraph.text_area.fragments.append(dto_fragment)
        x += dto_fragment.width
    return dto_word

def _generate_dto_text_line(
    x: float,
    y: float,
    dto_paragraph: DtoParagraph,
    text_line: TextLine,
    justify_padding_after: float) -> DtoTextLine:
    dto_text_line = DtoTextLine(
        x,
        y,
        dto_paragraph,
        justify_padding_after
    )
    dto_text_line.width = text_line.width
    dto_text_line.height = text_line.height
    dto_text_line.baseline = y + text_line.ascent
    dto_text_line.space_after = text_line.leading
    dto_text_line.paragraph_h_align = dto_paragraph.h_align
    x_offset = 0.0
    match dto_text_line.paragraph_h_align:
        case "left":
            pass
        case "right":
            x_offset = text_line.available_width
        case "center":
            x_offset = (text_line.available_width) / 2
        case "justify":
            if len(text_line.inner_spaces) > 0:
                justify_spacing = (
                    text_line.available_width) / len(text_line.inner_spaces)
                if justify_spacing > 0:
                    for inner_space in text_line.inner_spaces:
                        inner_space.justify_space = justify_spacing
    x += x_offset
    for word in text_line.words:
        dto_word = _generate_dto_word(
            x,
            y + (text_line.ascent - word.ascent),
            dto_text_line,
            word)
        dto_text_line.words.append(dto_word)
        x += dto_word.width + dto_word.justify_padding_after
    # y += dto_text_line.height
    # y += dto_text_line.space_after
    # y += dto_text_line.justify_padding_after
    return dto_text_line


def _generate_dto_paragraph(
    x: float,
    y: float,
    paragraph: Paragraph,
    dto_text_area: DtoTextArea,
    should_distrubute_space_in_lines: bool,
    height_diff: float,
    last_paragraph: bool) -> DtoParagraph:
    dto_paragraph = DtoParagraph(
        x,
        y,
        dto_text_area)
    dto_paragraph.width = paragraph.width
    dto_paragraph.height = paragraph.height
    dto_paragraph.chars = paragraph._get_chars()
    dto_paragraph.tab_size = paragraph.tab_size
    dto_paragraph.line_height_ratio = paragraph.line_height_ratio
    dto_paragraph.first_line_indent = paragraph.first_line_indent
    dto_paragraph.hanging_indent = paragraph.hanging_indent
    dto_paragraph.left_indent = paragraph.left_indent
    dto_paragraph.right_indent = paragraph.right_indent
    dto_paragraph.space_before = paragraph.space_before
    dto_paragraph.space_after = paragraph.space_after
    dto_paragraph.h_align = paragraph.h_align
    num_of_lines_in_paragraph = len(paragraph.lines)
    y += dto_paragraph.space_before
    for line in paragraph.lines:
        line_justify_padding = 0.0
        if should_distrubute_space_in_lines:
            if not last_paragraph:
                line_justify_padding = (height_diff
                                        / num_of_lines_in_paragraph)
            else:
                line_justify_padding = (height_diff
                                        / (num_of_lines_in_paragraph - 1))
        if line == paragraph.lines[0]:
            x_offset = (x
                        + dto_paragraph.first_line_indent)
        else:
            x_offset = x + dto_paragraph.left_indent
        dto_text_line = _generate_dto_text_line(
            x_offset,
            y,
            dto_paragraph,
            line,
            line_justify_padding,
            )
        dto_paragraph.text_lines.append(dto_text_line)
        y += dto_text_line.height
        y += dto_text_line.space_after
        y += dto_text_line.justify_padding_after
    y += dto_paragraph.space_after
    dto_paragraph.height += height_diff
    return dto_paragraph

def generate_dto_text_area(
    text_area: TextArea
    ) -> DtoTextArea:
    y_offset: float = 0.0
    between_paragraphs_padding: float = 0.0
    should_distrubute_space_in_lines: bool = False
    num_of_lines_in_text_area: int = 0
    # ******************************
    match text_area.v_align:
        case "top":
            pass
        case "bottom":
            y_offset += text_area.available_height
        case "center":
            y_offset += text_area.available_height / 2
        case "justify-paragraphs":
            between_paragraphs_padding = (text_area.available_height
                                    / (len(text_area.paragraphs) - 1))
        case "justify-lines":
            should_distrubute_space_in_lines = True
            for paragraph in text_area.paragraphs:
                num_of_lines_in_text_area += len(paragraph.lines)
        case _:
            raise ValueError("Invalid value for vertical alignment.")
    # ******************************
    dto_text_area = DtoTextArea(
        text_area.x,
        text_area.y,
        text_area.width,
        text_area.height
    )
    dto_text_area.height_empty_space = text_area.available_height
    dto_text_area.v_align = text_area.v_align

    y = text_area.y + y_offset
    for paragraph in text_area.paragraphs:
        height_diff = 0.0
        last_paragraph = False
        if should_distrubute_space_in_lines:
            if paragraph != text_area.paragraphs[-1]:
                height_diff = (
                    (len(paragraph.lines) / num_of_lines_in_text_area)
                        * text_area.available_height
                    )
            else:
                height_diff = (
                    ((len(paragraph.lines) - 1) / num_of_lines_in_text_area)
                        * text_area.available_height
                    )
                last_paragraph = True
        # ******************************
        dto_paragraph = _generate_dto_paragraph(
                text_area.x,
                y,
                paragraph,
                dto_text_area,
                should_distrubute_space_in_lines,
                height_diff,
                last_paragraph
            )
        dto_text_area.paragraphs.append(dto_paragraph)
        # ******************************
        y += dto_paragraph.height
        if paragraph != text_area.paragraphs[-1]:
            y += between_paragraphs_padding
    return dto_text_area
