from docugenr8_core.text_area.words_creation import create_words

def test__create_words(font1):
    text = "The quick brown fox jumps over the lazy dog 1234567890 !@#$%^&*()_+[]{};':\",./<>?`~-"
    new_words = create_words(text, font1, 10, (0,0,0))
    assert len(new_words) == 21

def test__words_with_carriage_return(font1):
    pass

def test__words_with_carriage_return_and_new_line(font1):
    pass

def test__words__with_new_line(font1):
    pass

def test__words_with_tab(font1):
    pass

def test__words_with_current_page_number(font1):
    pass

def test__words_with_total_pages_number(font1):
    pass
