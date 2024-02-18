from .text_area import TextArea


class Page:
    def __init__(self, page_width: float, page_height: float) -> None:
        self.page_width = page_width
        self.page_height = page_height
        self.page_contents: list[object] = []

    def add_content(self, content: object):
        match content:
            case TextArea():
                self.page_contents.append(content)
            case _:
                raise TypeError("Content type not defined.")
