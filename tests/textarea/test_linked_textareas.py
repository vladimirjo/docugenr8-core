from docugenr8_core.text_area.text_area import create_words

def test__textarea_linked_textareas(doc_with_fonts):
    doc_with_fonts.settings.paragraph_space_before = 0
    doc_with_fonts.settings.paragraph_space_after = 0
    doc_with_fonts.settings.paragraph_first_line_indent = 0
    doc_with_fonts.settings.paragraph_hanging_indent = 0
    doc_with_fonts.settings.paragraph_left_indent = 0
    doc_with_fonts.settings.paragraph_right_indent = 0
    doc_with_fonts.settings.text_line_height_ratio = 1
    doc_with_fonts.settings.text_split_words = False
    ta1 = doc_with_fonts.create_textarea(0, 0, 15, 20)
    ta1.add_text("aa bb cc dd ee ")
    assert len(ta1._paragraphs) == 1
    assert len(ta1._paragraphs[0]._textlines) == 2
    assert len(ta1._get_buffer()) == 6
    ta2 = doc_with_fonts.create_textarea(0, 0, 15, 20)
    ta1.link_textarea(ta2)
    assert len(ta2._paragraphs) == 1
    assert len(ta2._paragraphs[0]._textlines) == 2
    assert len(ta2._get_buffer()) == 2
    ta3 = doc_with_fonts.create_textarea(0, 0, 15, 20)
    ta2.link_textarea(ta3)
    assert len(ta3._paragraphs) == 1
    assert len(ta3._paragraphs[0]._textlines) == 1
    assert len(ta3._get_buffer()) == 0

def test__textarea_linked_textareas_emptying(doc_with_fonts):
    doc_with_fonts.settings.paragraph_space_before = 0
    doc_with_fonts.settings.paragraph_space_after = 0
    doc_with_fonts.settings.paragraph_first_line_indent = 0
    doc_with_fonts.settings.paragraph_hanging_indent = 0
    doc_with_fonts.settings.paragraph_left_indent = 0
    doc_with_fonts.settings.paragraph_right_indent = 0
    doc_with_fonts.settings.text_line_height_ratio = 1
    doc_with_fonts.settings.text_split_words = False
    ta1 = doc_with_fonts.create_textarea(0, 0, 15, 20)
    ta1.add_text("aa bb cc dd ee ")
    ta2 = doc_with_fonts.create_textarea(0, 0, 15, 20)
    ta1.link_textarea(ta2)
    ta3 = doc_with_fonts.create_textarea(0, 0, 15, 20)
    ta2.link_textarea(ta3)
    new_words = create_words(
        "abcdefg ",
        doc_with_fonts.fonts["font1"],
        doc_with_fonts.settings.font_size,
        doc_with_fonts.settings.font_color)
    ta2._paragraphs[0]._textlines[0]._append_word(new_words[0])
    ta2._paragraphs[0]._textlines[0]._append_word(new_words[1])
    ta2._paragraphs[0]._textlines[0]._adjust_words_between_textlines()
    ta2._paragraphs[0]._textlines[1]._adjust_words_between_textlines()
    assert len(ta2._paragraphs[0]._textlines) == 1
    assert len(ta3._paragraphs) == 0
    words_buffer = ta3._get_buffer()
    assert len(words_buffer) == 6
    assert words_buffer[0]._chars == "abcdefg"
    assert words_buffer[1]._chars == " "
    assert words_buffer[2]._chars == "dd"
    assert words_buffer[3]._chars == " "
    assert words_buffer[4]._chars == "ee"
    assert words_buffer[5]._chars == " "
