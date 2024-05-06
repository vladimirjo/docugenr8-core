from docugenr8_pdf.pdf import Pdf
from .build_dto import build_dto

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
    ) -> None:
        page = Page(width, height)
        self.pages.append(page)

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

    def output_to_bytes(self) -> bytes:
        pdf = Pdf(build_dto(self))
        return pdf.output_to_bytes()

    def output_to_file(self, file: str) -> None:
        b = self.output_to_bytes()
        with open(file, "wb") as f:
            f.write(b)
