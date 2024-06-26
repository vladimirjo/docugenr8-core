from collections.abc import Callable


class Settings:
    def __init__(self) -> None:
        self.font_current: None | str = None
        self.font_size: float = 11.0
        self.font_color: tuple[int, int, int] = (0, 0, 0)  # black color 0, 0, 0
        self.text_tab_size = 35.4375
        self.text_h_align: str = "left"
        self.text_v_align: str = "top"
        self.textline_height_ratio: float = 1.2
        self.text_split_words: bool = True
        self.paragraph_first_line_indent: float = 20.0
        self.paragraph_hanging_indent: float = 0.0
        self.paragraph_left_indent: float = 10.0
        self.paragraph_right_indent: float = 10.0
        self.paragraph_space_before: float = 10.0
        self.paragraph_space_after: float = 10.0
        self.page_num_current_page_dummy: str = "%%pn%%"
        self.page_num_total_pages_dummy: str = "%%tp%%"
        self.page_num_dummy_length: int = 2
        self.page_num_presentation: Callable[[int], str] = str
        self.fill_color: tuple[int, int, int] = (255, 255, 255)  # white color 255, 255, 255
        self.line_color: tuple[int, int, int] = (0, 0, 0)  # black color 0, 0, 0
        self.line_width: float = 1.0
        self.line_pattern: tuple[int, int, int, int, int] = (0, 0, 0, 0, 0)
        self.line_closed: bool = False
        self.textbox_padding_left: float = 0.0
        self.textbox_padding_right: float = 0.0
        self.textbox_padding_top: float = 0.0
        self.textbox_padding_bottom: float = 0.0
        self.textbox_margin_left: float = 0.0
        self.textbox_margin_right: float = 0.0
        self.textbox_margin_top: float = 0.0
        self.textbox_margin_bottom: float = 0.0
