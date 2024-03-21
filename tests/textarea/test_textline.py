from docugenr8_core.text_area.textarea import create_words

def test__textline_append_word(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 25, 100)
    ta.add_text("aa bb cc dd ee ")
    assert len(ta._paragraphs) == 1
    assert len(ta._paragraphs[0]._textlines) == 3
    assert ta._paragraphs[0]._textlines[0]._get_chars() == "aa bb "
    assert ta._paragraphs[0]._textlines[1]._get_chars() == "cc dd "
    assert ta._paragraphs[0]._textlines[2]._get_chars() == "ee "

    new_words = create_words(
        "ab",
        doc_with_fonts.fonts["font2"],
        doc_with_fonts.settings.font_size,
        doc_with_fonts.settings.font_color)

    ta._paragraphs[0]._textlines[2]._append_word(new_words[0], 2)
    assert len(ta._paragraphs[0]._textlines[2]._height_dict) == 2
    assert ta._paragraphs[0]._textlines[2]._height_dict[10] == 2
    assert ta._paragraphs[0]._textlines[2]._height_dict[20] == 1
    assert len(ta._paragraphs[0]._textlines[2]._ascent_dict) == 2
    assert ta._paragraphs[0]._textlines[2]._ascent_dict[6] == 2
    assert ta._paragraphs[0]._textlines[2]._ascent_dict[12] == 1
    assert ta._paragraphs[0]._textlines[2]._height == 20
    assert ta._paragraphs[0]._textlines[2]._ascent == 12

def test__textline_pop_word(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 25, 100)
    ta.add_text("aa bb cc dd ee ")
    new_words = create_words(
        "ab",
        doc_with_fonts.fonts["font2"],
        doc_with_fonts.settings.font_size,
        doc_with_fonts.settings.font_color)

    ta._paragraphs[0]._textlines[2]._append_word(new_words[0], 2)
    ta._paragraphs[0]._textlines[2]._pop_word()
    assert len(ta._paragraphs[0]._textlines[2]._height_dict) == 1
    assert ta._paragraphs[0]._textlines[2]._height_dict[10] == 2
    assert len(ta._paragraphs[0]._textlines[2]._ascent_dict) == 1
    assert ta._paragraphs[0]._textlines[2]._ascent_dict[6] == 2
    assert ta._paragraphs[0]._textlines[2]._height == 10
    assert ta._paragraphs[0]._textlines[2]._ascent == 6

def test__textline_split_word(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 25, 100)
    ta.add_text("aa bb cc dd ee ")
    new_words = create_words(
        "ab",
        doc_with_fonts.fonts["font2"],
        doc_with_fonts.settings.font_size,
        doc_with_fonts.settings.font_color)
    ta._paragraphs[0]._textlines[2]._append_word(new_words[0], 2)
    words = ta._paragraphs[0]._textlines[2]._words
    ta._paragraphs[0]._textlines[2]._split_word(words[0], 5)
    assert len(ta._paragraphs[0]._textlines[2]._words) == 4
    assert ta._paragraphs[0]._textlines[2]._words[0]._chars == "e"
    assert ta._paragraphs[0]._textlines[2]._words[1]._chars == "e"
    assert ta._paragraphs[0]._textlines[2]._words[2]._chars == " "
    assert ta._paragraphs[0]._textlines[2]._words[3]._chars == "ab"

def test__textline_delete_textline(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 25, 100)
    doc_with_fonts.settings.text_line_height_ratio = 1.5
    ta.add_text("aa bb cc dd ee ")
    new_words = create_words(
        "ab",
        doc_with_fonts.fonts["font2"],
        doc_with_fonts.settings.font_size,
        doc_with_fonts.settings.font_color)
    ta._paragraphs[0]._textlines[2]._append_word(new_words[0], 2)
    words = ta._paragraphs[0]._textlines[2]._words
    ta._paragraphs[0]._textlines[2]._split_word(words[0], 4)
    assert ta._paragraphs[0]._height == (ta._paragraphs[0]._space_before
                                         + ta._paragraphs[0]._textlines[0]._height
                                         + ta._paragraphs[0]._textlines[0]._leading
                                         + ta._paragraphs[0]._textlines[1]._height
                                         + ta._paragraphs[0]._textlines[1]._leading
                                         + ta._paragraphs[0]._textlines[2]._height
                                         + ta._paragraphs[0]._textlines[2]._leading
                                         + ta._paragraphs[0]._space_after)
    removed_words = ta._paragraphs[0]._textlines[1]._remove_line_and_get_words()
    assert len(ta._paragraphs[0]._textlines) == 2
    assert ta._paragraphs[0]._textlines[0]._prev == None
    assert ta._paragraphs[0]._textlines[0]._next == ta._paragraphs[0]._textlines[1]
    assert ta._paragraphs[0]._textlines[1]._prev == ta._paragraphs[0]._textlines[0]
    assert ta._paragraphs[0]._textlines[1]._next == None
    assert ta._paragraphs[0]._height == (ta._paragraphs[0]._space_before
                                         + ta._paragraphs[0]._textlines[0]._height
                                         + ta._paragraphs[0]._textlines[0]._leading
                                         + ta._paragraphs[0]._textlines[1]._height
                                         + ta._paragraphs[0]._textlines[1]._leading
                                         + ta._paragraphs[0]._space_after)
    assert removed_words[0]._chars == "cc"
    assert removed_words[1]._chars == " "
    assert removed_words[2]._chars == "dd"
    assert removed_words[3]._chars == " "

def test__textline_word_width_exceeds_textline_width(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 25, 100)
    doc_with_fonts.settings.text_line_height_ratio = 1.5
    doc_with_fonts.settings.text_split_words = False
    ta.add_text("aa bb cccccc dd ee ")
    words_buffer = ta._get_buffer()
    assert len(words_buffer) == 6
    words_buffer.clear()
    doc_with_fonts.settings.text_split_words = True
    ta.add_text("cccccc dd ee ")
    assert len(words_buffer) == 0

def test__textline_fragment_width_exceeds_textline_width(doc_with_fonts):
    doc_with_fonts.settings.paragraph_first_line_indent = 0
    doc_with_fonts.settings.paragraph_hanging_indent = 0
    doc_with_fonts.settings.paragraph_left_indent = 0
    doc_with_fonts.settings.paragraph_right_indent = 0
    doc_with_fonts.settings.text_split_words = True
    ta = doc_with_fonts.create_textarea(0, 0, 4, 100)
    ta.add_text("aa bb cc")
    words_buffer = ta._get_buffer()
    assert len(ta._paragraphs) == 0
    assert len(words_buffer) == 5

def test__textarea_word_exceed_textarea_height(doc_with_fonts):
    doc_with_fonts.settings.paragraph_first_line_indent = 0
    doc_with_fonts.settings.paragraph_hanging_indent = 0
    doc_with_fonts.settings.paragraph_left_indent = 0
    doc_with_fonts.settings.paragraph_right_indent = 0
    doc_with_fonts.settings.text_split_words = True
    ta = doc_with_fonts.create_textarea(0, 0, 50, 4)
    ta.add_text("aa bb cc")
    words_buffer = ta._get_buffer()
    assert len(ta._paragraphs) == 0
    assert len(words_buffer) == 5

def test__append_and_remove_words(doc_with_fonts):
    doc_with_fonts.settings.paragraph_space_before = 0
    doc_with_fonts.settings.paragraph_space_after = 0
    doc_with_fonts.settings.paragraph_first_line_indent = 0
    doc_with_fonts.settings.paragraph_hanging_indent = 0
    doc_with_fonts.settings.paragraph_left_indent = 0
    doc_with_fonts.settings.paragraph_right_indent = 0
    doc_with_fonts.settings.text_line_height_ratio = 1
    doc_with_fonts.settings.text_split_words = False
    doc_with_fonts.settings.font_size = 10
    ta = doc_with_fonts.create_textarea(0, 0, 120, 20)
    ta.add_text("aa bb cc")
    doc_with_fonts.settings.font_current = "font2"
    doc_with_fonts.settings.font_size = 15
    ta.add_text("dd ee ff")
    assert len(ta._paragraphs) == 1
    assert len(ta._paragraphs[0]._textlines) == 1
    assert len(ta._paragraphs[0]._textlines[0]._words) == 9
    textline = ta._paragraphs[0]._textlines[0]
    while len(textline._words) > 0:
        textline._words[-1]._remove_from_line()
    assert len(ta._paragraphs) == 0
    assert ta._available_height == 20

def test__word_split(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 50, 10)
    ta.add_text("ab%%pn%%cd%%tp%%ef")
    textline = ta._paragraphs[0]._textlines[0]
    word = ta._paragraphs[0]._textlines[0]._words[0]
    assert len(ta._paragraphs[0]._textlines[0]._words[0]._fragments) == 8
    assert len(ta._words_with_current_page_fragments) == 1
    assert ta._words_with_current_page_fragments[0] == textline._words[0]
    assert len(ta._words_with_total_pages_fragments) == 1
    assert ta._words_with_total_pages_fragments[0] == textline._words[0]
    textline = ta._paragraphs[0]._textlines[0]
    word = ta._paragraphs[0]._textlines[0]._words[0]
    textline._split_word(word, 25)
    assert len(textline._words) == 2
    assert len(ta._words_with_current_page_fragments) == 1
    assert ta._words_with_current_page_fragments[0] == textline._words[0]
    assert len(ta._words_with_total_pages_fragments) == 1
    assert ta._words_with_total_pages_fragments[0] == textline._words[1]

def test__merge_words(doc_with_fonts):
    ta = doc_with_fonts.create_textarea(0, 0, 50, 10)
    ta.add_text("ab%%pn%%c")
    ta.add_text("d%%tp%%ef")
    textline = ta._paragraphs[0]._textlines[0]
    assert len(ta._paragraphs[0]._textlines[0]._words) == 1
    assert len(ta._paragraphs[0]._textlines[0]._words[0]._fragments) == 8
    assert len(ta._words_with_current_page_fragments) == 1
    assert ta._words_with_current_page_fragments[0] == textline._words[0]
    assert len(ta._words_with_total_pages_fragments) == 1
    assert ta._words_with_total_pages_fragments[0] == textline._words[0]
