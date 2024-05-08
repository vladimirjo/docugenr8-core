"""docugenr8 module.

This module provides functionality to create and manipulate documents and its objects. It includes the `Document` class,
which represents a document and its pages. It has functions to add new pages, create and add objects to pages and pack
information into DTOs for usage in other modules where the information will be rendered.

Example:
    # Create a new document
    doc = Document()

    # Add first page to the document
    doc.add_page(595.2, 842.04)

    # Add font to the document
    doc.add_font(font_name="calibri", path="./fonts/calibri.ttf")

    # Create a text area and fill it with a text
    ta = doc.create_textarea(
    x=50,
    y=50,
    width=180,
    height=140)
    ta.add_text("The quick brown fox jumped over the lazy dog. 1234567890.")


    # Add the text area to the first page
    doc.pages[0].add_content(ta)

    # Pack document information into a DTO
    dto = doc.build_dto()
"""

from .document import Document as Document
