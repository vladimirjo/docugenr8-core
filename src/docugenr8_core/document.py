from docugenr8_shared.dto import Dto
from docugenr8_shared.dto import DtoFont
from docugenr8_shared.dto import DtoPage

from .build_dto import _generate_dto_text_area
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

    def _build_dto(self) -> Dto:
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
                        dto_page.contents.append(_generate_dto_text_area(content))
                    case _:
                        raise TypeError("Invalid content type.")
        return dto
