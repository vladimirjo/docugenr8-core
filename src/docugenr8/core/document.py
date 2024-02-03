from .text_area import TextArea
from .page import Page
from .font import Font
from .settings import Settings

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
        self.fonts[font.name] = font
        self.settings.font_current = font_name

    def create_textarea(
        self, x: float, y: float, width: float, height: float
    ) -> TextArea:
        textarea = TextArea(x, y, width, height, self)
        return textarea
