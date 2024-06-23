from docugenr8_shared.dto import Dto

from docugenr8_core.dto import dto_build
from docugenr8_core.font import Font
from docugenr8_core.page import Page
from docugenr8_core.settings import Settings
from docugenr8_core.shapes import Arc
from docugenr8_core.shapes import Curve
from docugenr8_core.shapes import Ellipse
from docugenr8_core.shapes import Rectangle
from docugenr8_core.text_area import TextArea
from docugenr8_core.text_box import TextBox


class Document:
    def __init__(self) -> None:
        self.settings = Settings()
        self.pages: list[Page] = []
        self.fonts: dict[str, Font] = {}

    def add_page(
        self,
        width: float,
        height: float,
    ) -> Page:
        page = Page(width, height)
        self.pages.append(page)
        return page

    def add_font(
        self,
        font_name: str,
        path: str,
    ) -> None:
        font = Font(font_name, path)
        self.fonts[font_name] = font
        self.settings.font_current = font_name

    def create_textarea(self, x: float, y: float, width: float, height: float) -> TextArea:
        return TextArea(x, y, width, height, self)

    def create_textbox(self, x: float, y: float, width: float, height: float) -> TextBox:
        return TextBox(x, y, width, height, self)

    def create_curve(self, x: float, y: float):
        return Curve(x, y, self)

    def create_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rotate: float,
        skew: float,
        rounded_corner_top_left: float,
        rounded_corner_top_right: float,
        rounded_corner_bottom_left: float,
        rounded_corner_bottom_right: float,
    ):
        return Rectangle(
            x,
            y,
            width,
            height,
            rotate,
            skew,
            rounded_corner_top_left,
            rounded_corner_top_right,
            rounded_corner_bottom_left,
            rounded_corner_bottom_right,
            self,
        )

    def create_elipse(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rotate: float = 0,
        skew: float = 0,
    ) -> Ellipse:
        return Ellipse(x, y, width, height, rotate, skew, self)

    def create_arc(self, x1: float, y1: float, x2: float, y2: float) -> Arc:
        return Arc(x1, y1, x2, y2, self)

    def create_triangle():
        # x, y, height, width,rotate, shear
        # top_point procent from 0 - 100%
        pass

    def create_diamond():
        # x, y, height, width, rotate, shear
        # mid_point procent from 0 -100%
        pass

    def create_trapezoid():
        # x, y, height, width, rotate, shear
        # left point 0 - 100%
        # right point 0 - 100%
        pass

    def create_poligon():
        # x, y, height, width, rotate, shear
        # number of sides
        # curve from -100% to 100%
        pass

    def create_star():
        # x, y, height, width, rotate, shear
        # number of points
        # inner radius from 0 - 100%
        pass

    def create_table():
        # x, y, height, width
        # number of columns
        # number of rows
        pass

    def export(self, data_type: str = "dto") -> Dto:
        match data_type:
            case "dto":
                return dto_build(self)
            case _:
                raise NotImplementedError("Not implemented data type.")
