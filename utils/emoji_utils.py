from functools import lru_cache
from pathlib import Path

from PIL import Image
from PyQt5.QtCore import QTextBoundaryFinder


EMOJI_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'emoji'


@lru_cache(maxsize=1)
def emoji_presentation_ranges():
    """Unicode 默认以表情呈现的码点范围。"""
    ranges = []
    for line in (EMOJI_DIR / 'emoji-data.txt').read_text(encoding='utf-8').splitlines():
        value = line.split('#', 1)[0].strip()
        if not value:
            continue
        codepoints, property_name = (part.strip() for part in value.split(';'))
        if property_name == 'Emoji_Presentation':
            bounds = codepoints.split('..')
            ranges.append((int(bounds[0], 16), int(bounds[-1], 16)))
    return ranges


def split_graphemes(text):
    """按完整字符分组，保留肤色、旗帜和组合表情。"""
    finder = QTextBoundaryFinder(QTextBoundaryFinder.Grapheme, text)
    encoded = text.encode('utf-16-le', errors='surrogatepass')
    start = 0
    cluster = ''
    while (end := finder.toNextBoundary()) != -1:
        part = encoded[start * 2:end * 2].decode('utf-16-le', errors='surrogatepass')
        if cluster and not cluster.endswith('\u200d') and not part.startswith('\u200d'):
            yield cluster
            cluster = ''
        cluster += part
        start = end
    if cluster:
        yield cluster


@lru_cache(maxsize=256)
def emoji_image(text, size):
    """读取完整表情的离线彩色图片；普通文字返回 None。"""
    if len(text) == 1 and not any(start <= ord(text) <= end
                                   for start, end in emoji_presentation_ranges()):
        return None
    key = '-'.join(f'{ord(char):x}' for char in text)
    for name in dict.fromkeys((key, key.replace('-fe0f', ''))):
        path = EMOJI_DIR / f'{name}.png'
        if path.is_file():
            with Image.open(path) as image:
                return image.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
    return None
