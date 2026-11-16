from pathlib import Path
from config.settings import IMAGE_FORMATS, VIDEO_FORMATS

def is_image(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in IMAGE_FORMATS

def is_video(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in VIDEO_FORMATS

def scan_folder(folder_path: str) -> dict[str, list[str]]:
    """扫描文件夹，分类图片和视频"""
    folder = Path(folder_path)
    images = [str(f) for f in folder.iterdir() if is_image(str(f))]
    videos = [str(f) for f in folder.iterdir() if is_video(str(f))]
    return {'images': images, 'videos': videos}

def validate_path(path: str) -> bool:
    return Path(path).exists()

def get_file_extension(file_path: str) -> str:
    return Path(file_path).suffix
