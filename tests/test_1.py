from docugenr8_core.text_area.textarea import create_words

def test__check_parameters_of_one_line_text(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("aaaaa aaaaa")
    assert len(ta._paragraphs) == 1
    assert ta._paragraphs[0]._textlines[0]._available_width == 45
    assert ta._paragraphs[0]._textlines[0]._height == 10
    assert len(ta._paragraphs[0]._textlines[0]._height_dict) == 1
    assert ta._paragraphs[0]._textlines[0]._ascent == 6
    assert len(ta._paragraphs[0]._textlines[0]._ascent_dict) == 1
    assert ta._paragraphs[0]._textlines[0]._leading == 0
    assert ta._paragraphs[0]._textlines[0]._width == 100
    assert len(ta._paragraphs[0]._textlines[0]._words) == 3
    assert ta._paragraphs[0]._textlines[0]._words[0]._chars == "aaaaa"
    assert ta._paragraphs[0]._textlines[0]._words[0]._width == 25
    assert ta._paragraphs[0]._textlines[0]._words[0]._chars == "aaaaa"
    assert ta._paragraphs[0]._textlines[0]._words[1]._chars == " "
    assert ta._paragraphs[0]._textlines[0]._words[2]._chars == "aaaaa"


def test__check_textline_available_width_with_spaces(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("    aa  aa     ")
    assert ta._paragraphs[0]._textlines[0]._available_width == 50

def test__check_number_of_paragraphs(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("aaaaa\naaaaa")
    assert len(ta._paragraphs) == 2
    assert ta._paragraphs[0]._textlines[0]._get_chars() == "aaaaa\n"
    assert ta._paragraphs[1]._textlines[0]._get_chars() == "aaaaa"

def test__spaces_at_the_end_of_textline(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("    aaaa aaaa aaaa      aaaa    aaaa  aaaaaa    ")
    assert ta._paragraphs[0]._textlines[0]._available_width == 10
    assert ta._paragraphs[0]._textlines[0]._get_chars() == "    aaaa aaaa aaaa      "
    assert ta._paragraphs[0]._textlines[1]._available_width == 0
    assert ta._paragraphs[0]._textlines[1]._get_chars() == "aaaa    aaaa  aaaaaa    "

def test__tab_widths(doc_with_fonts):
    doc_with_fonts.settings.text_tab_size = 20
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text(" \taa\taa")
    assert ta._paragraphs[0]._textlines[0]._available_width == 50
    assert ta._paragraphs[0]._textlines[0]._words[1]._chars == "\t"
    assert ta._paragraphs[0]._textlines[0]._words[1]._width == 15
    new_words = create_words(
        "a",
        doc_with_fonts.fonts[doc_with_fonts.settings.font_current],
        doc_with_fonts.settings.font_size,
        doc_with_fonts.settings.font_color,
        doc_with_fonts.settings.page_num_current_page_dummy,
        doc_with_fonts.settings.page_num_total_pages_dummy,
        doc_with_fonts.settings.page_num_dummy_length,
        doc_with_fonts.settings.page_num_presentation,
        )
    ta._paragraphs[0]._textlines[0]._append_word(new_words[0], 1)
    assert ta._paragraphs[0]._textlines[0]._available_width == 50
    assert ta._paragraphs[0]._textlines[0]._words[2]._chars == "\t"
    assert ta._paragraphs[0]._textlines[0]._words[2]._width == 10

def test__merge_words(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("aaaa")
    ta.add_text("aaaa")
    assert len(ta._paragraphs[0]._textlines[0]._words) == 1
    assert ta._paragraphs[0]._textlines[0]._words[0]._width == 40
    assert ta._paragraphs[0]._textlines[0]._words[0]._chars == "aaaaaaaa"
    assert ta._paragraphs[0]._textlines[0]._words[0]._textline == ta._paragraphs[0]._textlines[0]
    ta1 = doc_with_fonts.create_textarea(0, 0, 100, 100)
    current_page_dummy = doc_with_fonts.settings.page_num_current_page_dummy
    doc_with_fonts.settings.page_num_dummy_length = 2
    ta1.add_text(current_page_dummy)
    ta1.add_text("aa")
    ta1.add_text(current_page_dummy)
    assert len(ta1._paragraphs[0]._textlines[0]._words) == 1
    assert len(ta1._words_with_current_page_fragments) == 1
    assert ta1._words_with_current_page_fragments[0] == ta1._paragraphs[0]._textlines[0]._words[0]
    assert ta1._paragraphs[0]._textlines[0]._words[0]._width == 30
