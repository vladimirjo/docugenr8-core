# from docugenr8_shared.dto import DtoFragment
# from docugenr8_shared.dto import DtoParagraph
from docugenr8_shared.dto import DtoTextArea
# from docugenr8_shared.dto import DtoTextLine
# from docugenr8_shared.dto import DtoWord

def test__justify_text(doc_with_fonts):
    doc_with_fonts.settings.paragraph_space_before = 0
    doc_with_fonts.settings.paragraph_space_after = 0
    doc_with_fonts.settings.paragraph_first_line_indent = 0
    doc_with_fonts.settings.paragraph_hanging_indent = 0
    doc_with_fonts.settings.paragraph_left_indent = 0
    doc_with_fonts.settings.paragraph_right_indent = 0
    doc_with_fonts.settings.text_line_height_ratio = 1
    doc_with_fonts.settings.text_split_words = False
    doc_with_fonts.settings.font_size = 10
    doc_with_fonts.settings.text_h_align = "justify"
    ta1 = doc_with_fonts.create_textarea(0, 0, 50, 20)
    ta1.add_text("aa bb ")
    ta1.add_text("cccccc dd")
    doc_with_fonts.add_page(200, 200)
    doc_with_fonts.pages[0].add_content(ta1)
    assert len(ta1._paragraphs[0]._textlines) == 2
    assert ta1._paragraphs[0]._textlines[0]._available_width == 25
    dto = doc_with_fonts.build_dto()
    assert isinstance(dto.pages[0].contents[0], DtoTextArea)
    first_line = dto.pages[0].contents[0].paragraphs[0].text_lines[0]
    second_line = dto.pages[0].contents[0].paragraphs[0].text_lines[1]
    assert first_line.x == 0
    assert first_line.y == 0
    assert first_line.words[0].x == 0
    assert first_line.words[0].y == 0
    assert first_line.words[1].x == 10
    assert first_line.words[1].y == 0
    assert first_line.words[2].x == 40
    assert first_line.words[2].y == 0
    assert second_line.words[2].x == 35
    assert second_line.words[2].y == 10
