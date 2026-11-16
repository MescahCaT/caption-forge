from pathlib import Path
from PIL import Image
import openpyxl
from openpyxl_image_loader import SheetImageLoader
from utils.text_utils import split_by_double_newline
from utils.file_utils import scan_folder, validate_path

class InputHandler:

    @staticmethod
    def parse_single_text(text: str) -> list[str]:
        """解析单条文本"""
        return [text.strip()] if text.strip() else []

    @staticmethod
    def parse_txt_file(file_path: str) -> list[str]:
        """解析txt文件，双回车分段"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return split_by_double_newline(content)

    @staticmethod
    def parse_excel_file(file_path: str) -> list[tuple]:
        """解析Excel，返回(图片, 文案)列表"""
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        image_loader = SheetImageLoader(sheet)

        results = []
        for row in range(2, sheet.max_row + 1):
            img_cell = f'A{row}'
            text_cell = sheet[f'B{row}'].value

            if image_loader.image_in(img_cell):
                image = image_loader.get(img_cell)
                results.append((image, text_cell or ''))

        return results

    @staticmethod
    def parse_folder(folder_path: str) -> list[str]:
        """解析文件夹，返回媒体文件路径列表"""
        if not validate_path(folder_path):
            raise ValueError(f'文件夹不存在: {folder_path}')

        files = scan_folder(folder_path)
        return files['images'] + files['videos']

    @staticmethod
    def parse_single_media(file_path: str) -> str:
        """解析单个媒体文件"""
        if not validate_path(file_path):
            raise ValueError(f'文件不存在: {file_path}')
        return file_path

    @staticmethod
    def validate_input_combination(has_text: bool, has_media: bool, is_excel: bool) -> tuple[bool, str]:
        """校验输入组合"""
        if is_excel:
            return True, ''

        if not has_text:
            return False, '缺少文案输入'

        if not has_media:
            return False, '缺少媒体文件'

        return True, ''
