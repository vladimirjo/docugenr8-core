from docugenr8 import Document

doc = Document()
doc.add_font(font_name="calibri", path="./calibri.ttf")
doc.add_page(595.2, 842.04)

ta = doc.create_textarea(x=50, y=50, width=200, height=140,)
ta.add_text(unicode_text="The quick brown fox jumped over the lazy dog. 1234567890\n")

ta.add_text(unicode_text="The quick brown fox jumped over the lazy dog. 1234567890\n")
