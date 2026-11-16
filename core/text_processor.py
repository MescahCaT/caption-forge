from PIL import ImageFont, ImageDraw
from utils.text_utils import truncate_text, is_cjk_char

class TextProcessor:

    @staticmethod
    def calculate_text_lines(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """计算文本换行"""
        lines = []
        current_line = ''

        for char in text:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines

    @staticmethod
    def measure_text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
        """测量文本尺寸"""
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    @staticmethod
    def apply_line_spacing(lines: list[str], font: ImageFont.FreeTypeFont, spacing: int) -> int:
        """计算总高度（含行间距）"""
        if not lines:
            return 0

        line_height = TextProcessor.measure_text_size(lines[0], font)[1]
        return line_height * len(lines) + spacing * (len(lines) - 1)

    @staticmethod
    def strip_text_prefix(text: str, length: int) -> str:
        """提取文本前N字符（跳过空格）"""
        return truncate_text(text, length)
