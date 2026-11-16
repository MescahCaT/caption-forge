from dataclasses import dataclass
from enum import Enum

@dataclass
class TextStyle:
    font_path: str
    font_size: int
    color: tuple[int, int, int]
    line_spacing: int = 10
    char_spacing: int = 2
    border_width: int = 0
    border_color: tuple[int, int, int] = (0, 0, 0)
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0)
    bold: bool = False
    align: str = 'left'  # 'left', 'center', 'right'
    bg_radius: int = 8

@dataclass
class Task:
    media_path: str
    text: str
    style: TextStyle
    position: tuple[int, int]
    output_name: str

class TaskMode(Enum):
    SINGLE_COPY = "single_copy"
    ONE_TO_ONE = "one_to_one"
    RANDOM_MATCH = "random_match"
