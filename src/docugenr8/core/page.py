class Page:
    def __init__(self, page_width: float, page_height: float) -> None:
        self.page_width = page_width
        self.page_height = page_height
        self.page_contents: list[object] = []

    def add_content(self, content: object):
        self.page_contents.append(content)
