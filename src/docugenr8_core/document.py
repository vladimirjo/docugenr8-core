from docugenr8_shared.dto import Dto
from docugenr8_shared.dto import DtoFont
from docugenr8_shared.dto import DtoPage

from .build_dto import generate_dto_text_area
from .font import Font
from .page import Page
from .settings import Settings
from .text_area import TextArea


class Document:
    def __init__(self) -> None:
        self.settings = Settings()
        self.pages: list[Page] = []
        self.fonts: dict[str, Font] = {}

    def add_page(self, page_width: float, page_height: float) -> None:
        page = Page(page_width, page_height)
        self.pages.append(page)

    def add_font(self, font_name: str, path: str) -> None:
        font = Font(font_name, path)
        self.fonts[font_name] = font
        self.settings.font_current = font_name

    def create_textarea(
        self, x: float, y: float, width: float, height: float
    ) -> TextArea:
        return TextArea(x, y, width, height, self)

    def build_dto(self) -> Dto:
        dto = Dto()
        for font_name, font in self.fonts.items():
            dto_font = DtoFont(font_name, font.raw_data)
            dto.fonts.append(dto_font)
        for page in self.pages:
            dto_page = DtoPage(page.page_width, page.page_height)
            dto.pages.append(dto_page)
            for content in page.page_contents:
                match content:
                    case TextArea():
                        dto_page.contents.append(
                            generate_dto_text_area(content)
                            )
                    case _:
                        raise TypeError("Invalid content type.")
        return dto
