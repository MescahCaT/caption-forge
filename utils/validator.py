from pathlib import Path

def validate_task_count(text_count: int, media_count: int, mode: str) -> tuple[bool, str]:
    """校验任务数量"""
    if mode == 'single_copy':
        return True, ''

    if text_count == 0 or media_count == 0:
        return False, '文案或媒体文件缺失'

    min_count = min(text_count, media_count)
    if text_count != media_count:
        return True, f'⚠️ 数量不匹配，将生成{min_count}个文件'

    return True, ''

def validate_font_file(file_path: str) -> bool:
    """校验字体文件"""
    path = Path(file_path)
    return path.exists() and path.suffix.lower() in ['.ttf', '.otf']

def validate_output_dir(dir_path: str) -> bool:
    """校验输出目录"""
    path = Path(dir_path)
    return path.exists() and path.is_dir()
