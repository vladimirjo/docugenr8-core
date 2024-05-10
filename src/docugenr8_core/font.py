import os
import pathlib
from io import BytesIO

from fontTools import ttLib


TAB = 9
NEW_LINE = 10
SPACE = 32


class Font:
    def __init__(
        self,
        font_name: str,
        path: str,
    ) -> None:
        self.name = font_name
        self.raw_data = pathlib.Path(_resolve_file_path(path)).read_bytes()
        self.ttfont = ttLib.TTFont(BytesIO(self.raw_data), recalcTimestamp=False)
        self.cmap = self.ttfont.getBestCmap()
        self.em: float = self.ttfont["head"].unitsPerEm  # type: ignore
        self.ascent_per_em: float = self.ttfont["hhea"].ascent  # type: ignore
        self.descent_per_em: float = self.ttfont["hhea"].descent  # type: ignore
        self.line_height_per_em: float = self.ascent_per_em - self.descent_per_em

    def _get_char_width(self, char: str, font_size: float) -> float:
        unicode = ord(char)
        if unicode in {TAB, NEW_LINE}:
            return 0.0
        try:
            glyph_name = self.cmap[unicode]
            glyph_width = self.ttfont["hmtx"].metrics[glyph_name][0]  # type: ignore
        # for unicodes not defined in font
        except KeyError:
            glyph_name = ".notdef"
            glyph_width = self.ttfont["hmtx"].metrics[glyph_name][0]  # type: ignore
        return font_size * glyph_width / self.em

    def _get_ascent(self, font_size: float) -> float:
        return font_size * (self.ascent_per_em / self.em)

    def _get_descent(self, font_size: float) -> float:
        return font_size * (self.descent_per_em / self.em)

    def _get_line_height(self, font_size: float) -> float:
        return font_size * (self.line_height_per_em / self.em)


def _resolve_file_path(path: str) -> pathlib.Path:
    root_dir = pathlib.Path(os.getcwd())
    return root_dir / path
