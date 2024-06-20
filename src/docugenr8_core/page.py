from docugenr8_core.shapes import Curve
from docugenr8_core.text_area import TextArea
from docugenr8_core.text_box import TextBox


class Page:
    def __init__(self, width: float, height: float) -> None:
        self._width = width
        self._height = height
        self._contents: list[object] = []

    def add_content(self, content: object) -> None:
        match content:
            case TextArea():
                self._contents.append(content)
            case TextBox():
                self._contents.append(content)
            case Curve():
                self._contents.append(content)
            case _:
                raise TypeError("Content type not defined in Core module.")
