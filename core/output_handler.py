from pathlib import Path
from core.models import Task, TextStyle
from core.text_processor import TextProcessor
from utils.file_utils import get_file_extension

class OutputHandler:

    @staticmethod
    def generate_filename(media_path: str, text: str) -> str:
        """生成输出文件名：媒体名前6位_文本前6字符"""
        media_name = Path(media_path).stem
        media_prefix = media_name[:6]
        text_prefix = TextProcessor.strip_text_prefix(text, 6)
        ext = get_file_extension(media_path)

        if ext.lower() in ['.avi', '.mov', '.mkv']:
            ext = '.mp4'

        return f"{media_prefix}_{text_prefix}{ext}"

    @staticmethod
    def save_image(image, output_path: str):
        """保存图片"""
        image.save(output_path, quality=95)

    @staticmethod
    def create_output_directory(base_dir: str) -> Path:
        """创建输出目录"""
        output_dir = Path(base_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
