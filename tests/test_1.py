def test__check_parameters_of_one_line_text(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("aaaaa aaaaa")
    assert len(ta._paragraphs) == 1
    assert ta._paragraphs[0]._textlines[0]._available_width == 45
    assert ta._paragraphs[0]._textlines[0]._height == 10
    assert len(ta._paragraphs[0]._textlines[0]._height_dict) == 1
    assert ta._paragraphs[0]._textlines[0]._ascent == 6
    assert len(ta._paragraphs[0]._textlines[0]._ascent_dict) == 1
    assert len(ta._paragraphs[0]._textlines[0]._inner_spaces) == 1
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
    ta.add_text("     aaaaa aaaaa     ")
    assert ta._paragraphs[0]._textlines[0]._available_width == 45

def test__check_number_of_paragraphs(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("aaaaa\naaaaa")
    assert len(ta._paragraphs) == 2
    assert ta._paragraphs[0]._textlines[0]._get_chars() == "aaaaa\n"
    assert ta._paragraphs[1]._textlines[0]._get_chars() == "aaaaa"

def test__spaces_at_the_end_of_text_line(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 100, 100)
    ta.add_text("    aaaa aaaa aaaa      ")
    print(ta._paragraphs[0]._textlines[0]._available_width)
    assert ta._paragraphs[0]._textlines[0]._available_width == 10
