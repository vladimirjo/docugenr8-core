from .text_area import TextArea


class Page:
    def __init__(self, width: float, height: float) -> None:
        self._width = width
        self._height = height
        self._contents: list[object] = []

    def add_content(self, content: object) -> None:
        match content:
            case TextArea():
                self._contents.append(content)
            case _:
                raise TypeError("Content type not defined.")
