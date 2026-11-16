import json
from dataclasses import asdict

from PyQt5.QtCore import QSettings

from core.models import TextStyle


class StylePresets:
    """当前用户的命名文字样式。"""

    def __init__(self, settings=None):
        self.settings = settings if settings is not None else QSettings('MediaTextWriter', 'StylePresets')

    def load(self):
        data = json.loads(self.settings.value('styles', '{}'))
        presets = {}
        for name, values in data.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError('自定义样式名称无效')
            values = dict(values)
            for field in ('color', 'border_color', 'bg_color'):
                values[field] = tuple(values[field])
            style = TextStyle(**values)
            self.validate(style)
            presets[name] = style
        return presets

    @staticmethod
    def validate(style):
        if (not isinstance(style.font_path, str) or type(style.bold) is not bool
                or style.align not in ('left', 'center', 'right')):
            raise ValueError('自定义样式字体或对齐设置无效')
        for field, lower, upper in (
            ('font_size', 10, 200), ('line_spacing', 0, 50), ('char_spacing', 0, 20),
            ('border_width', 0, 10), ('bg_radius', 0, 100)
        ):
            value = getattr(style, field)
            if type(value) is not int or not lower <= value <= upper:
                raise ValueError(f'自定义样式参数无效：{field}')
        for field, length in (('color', 3), ('border_color', 3), ('bg_color', 4)):
            value = getattr(style, field)
            if len(value) != length or any(type(channel) is not int or not 0 <= channel <= 255
                                           for channel in value):
                raise ValueError(f'自定义样式颜色无效：{field}')

    def save(self, presets):
        self.settings.setValue('styles', json.dumps(
            {name: asdict(style) for name, style in presets.items()}, ensure_ascii=False
        ))
        self.settings.sync()
        if self.settings.status() != QSettings.NoError:
            raise OSError('无法保存自定义样式，请检查用户配置目录权限')
