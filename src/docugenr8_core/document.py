from docugenr8_shared.dto import Dto
from docugenr8_shared.dto import DtoFont
from docugenr8_shared.dto import DtoPage

from docugenr8_core.shapes import Curve
from docugenr8_core.shapes import Rectangle
from docugenr8_core.shapes import Arc
from docugenr8_core.shapes import Ellipse
from docugenr8_core.text_box import TextBox

from .build_dto import generate_dto_text_area
from .build_dto import generate_dto_textbox
from .font import Font
from .page import Page
from .settings import Settings
from .text_area import TextArea


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

    def create_elipse():
        # x, y, height, width, rotate, shear
        pass

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

    def build_dto(self) -> Dto:
        dto = Dto()
        for font_name, font in self.fonts.items():
            dto_font = DtoFont(font_name, font.raw_data)
            dto.fonts.append(dto_font)
        for page_number, page in enumerate(self.pages):
            dto_page = DtoPage(page._width, page._height)
            dto.pages.append(dto_page)
            for content in page._contents:
                match content:
                    case TextArea():
                        content._build_current_page_fragments(page_number + 1)
                        content._build_total_pages_fragments(len(self.pages))
                        dto_page.contents.append(generate_dto_text_area(content))
                    case TextBox():
                        content._text_area._build_current_page_fragments(page_number + 1)
                        content._text_area._build_total_pages_fragments(len(self.pages))
                        dto_page.contents.append(generate_dto_textbox(content))
                    case Curve():
                        dto_page.contents.append(content._dto_curve)
                    case Rectangle():
                        dto_page.contents.append(content._dto_rectangle)
                    case Arc():
                        dto_page.contents.append(content._dto_arc)
                    case Ellipse():
                        dto_page.contents.append(content._dto_ellipse)
                    case _:
                        raise TypeError("Invalid content type to generate Dto in Core module.")
        return dto
