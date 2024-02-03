from fontTools import ttLib


class Font:
    def __init__(self, font_name: str, path: str) -> None:
        self.name = font_name
        self.path = path
        self.ttfont = ttLib.TTFont(self._is_file(path), recalcTimestamp=False)
        self.cmap = self.ttfont.getBestCmap()
        self.em: float = self.ttfont["head"].unitsPerEm  # type: ignore
        self.ascent_per_em: float = self.ttfont["hhea"].ascent  # type: ignore
        self.descent_per_em: float = self.ttfont["hhea"].descent  # type: ignore
        self.line_height_per_em: float = (
            self.ascent_per_em - self.descent_per_em
        )

    def _is_file(self, path: str):
        import os
        import pathlib

        root_dir = pathlib.Path(os.getcwd())
        return root_dir / path

    def get_char_width(self, char: str, font_size: float):
        unicode = ord(char)
        try:
            glyph_name = self.cmap[unicode]
            glyph_width = self.ttfont["hmtx"].metrics[glyph_name][0]  # type: ignore
        # for unicodes not defined in font
        except:
            glyph_name = ".notdef"
            glyph_width = self.ttfont["hmtx"].metrics[glyph_name][0]  # type: ignore
        char_width = font_size * glyph_width / self.em
        return char_width

    def get_ascent(self, font_size: float) -> float:
        return font_size * (self.ascent_per_em / self.em)

    def get_descent(self, font_size: float) -> float:
        return font_size * (self.descent_per_em / self.em)

    def get_line_height(self, font_size: float) -> float:
        return font_size * (self.line_height_per_em / self.em)
