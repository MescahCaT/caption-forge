import re

def split_by_double_newline(text: str) -> list[str]:
    """双回车分段"""
    return [s.strip() for s in re.split(r'\n\s*\n', text) if s.strip()]

def remove_spaces(text: str) -> str:
    return text.replace(' ', '')

def truncate_text(text: str, length: int) -> str:
    """截取文本，跳过空格"""
    no_space = remove_spaces(text)
    return no_space[:length]

def is_cjk_char(char: str) -> bool:
    """判断是否为中日韩字符"""
    code = ord(char)
    return (0x4E00 <= code <= 0x9FFF or
            0x3040 <= code <= 0x30FF or
            0xAC00 <= code <= 0xD7AF)
