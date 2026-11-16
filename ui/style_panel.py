from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QSlider, QFileDialog, QColorDialog, QGroupBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontDatabase
from pathlib import Path
from core.models import TextStyle
from config.settings import DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR

class StylePanel(QWidget):
    style_changed = pyqtSignal(TextStyle)

    def __init__(self):
        super().__init__()
        self.font_path = ''
        self.font_size = DEFAULT_FONT_SIZE
        self.font_bold = False
        self.color = DEFAULT_FONT_COLOR
        self.line_spacing = 10
        self.char_spacing = 2
        self.border_width = 0
        self.border_color = (0, 0, 0)
        self.bg_color = (0, 0, 0, 0)
        self.bg_enabled = False
        self.text_align = 'left'
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        font_group = self._create_font_section()
        color_group = self._create_color_section()
        align_group = self._create_align_section()
        spacing_group = self._create_spacing_section()
        border_group = self._create_border_section()

        layout.addWidget(font_group)
        layout.addWidget(color_group)
        layout.addWidget(align_group)
        layout.addWidget(spacing_group)
        layout.addWidget(border_group)
        layout.addStretch()
        self.setLayout(layout)

    def _create_font_section(self):
        group = QGroupBox("字体设置")
        layout = QVBoxLayout()

        self.font_label = QLabel("系统默认")
        self.font_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")

        self.font_preview = QLabel("预览文字 AaBbCc 123")
        self.font_preview.setStyleSheet("""
            padding: 10px;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 3px;
            font-size: 16px;
        """)
        self.font_preview.setAlignment(Qt.AlignCenter)

        btn_font = QPushButton("选择字体文件")
        btn_font.clicked.connect(self.select_font)

        size_layout = QHBoxLayout()
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 200)
        self.size_spin.setValue(self.font_size)
        self.size_spin.valueChanged.connect(self.on_size_change)

        self.bold_checkbox = QCheckBox("加粗")
        self.bold_checkbox.setChecked(self.font_bold)
        self.bold_checkbox.stateChanged.connect(self.on_bold_change)

        size_layout.addWidget(QLabel("字号:"))
        size_layout.addWidget(self.size_spin, 1)
        size_layout.addWidget(self.bold_checkbox)

        layout.addWidget(QLabel("字体文件:"))
        layout.addWidget(self.font_label)
        layout.addWidget(btn_font)
        layout.addWidget(QLabel("字体预览:"))
        layout.addWidget(self.font_preview)
        layout.addLayout(size_layout)

        group.setLayout(layout)
        return group

    def _create_color_section(self):
        group = QGroupBox("颜色设置")
        layout = QVBoxLayout()

        self.color_btn = QPushButton("选择文字颜色")
        self.color_btn.setStyleSheet(f"background-color: rgb{self.color}")
        self.color_btn.clicked.connect(self.select_color)

        bg_layout = QHBoxLayout()
        self.bg_enabled_checkbox = QCheckBox("启用背景色")
        self.bg_enabled_checkbox.setChecked(self.bg_enabled)
        self.bg_enabled_checkbox.stateChanged.connect(self.on_bg_enabled_change)

        self.bg_color_btn = QPushButton("选择背景色")
        self.bg_color_btn.setEnabled(self.bg_enabled)
        self.bg_color_btn.clicked.connect(self.select_bg_color)

        bg_layout.addWidget(self.bg_enabled_checkbox)
        bg_layout.addWidget(self.bg_color_btn)

        layout.addWidget(self.color_btn)
        layout.addLayout(bg_layout)

        group.setLayout(layout)
        return group

    def _create_spacing_section(self):
        group = QGroupBox("间距设置")
        layout = QVBoxLayout()

        self.line_spin = QSpinBox()
        self.line_spin.setRange(0, 50)
        self.line_spin.setValue(self.line_spacing)
        self.line_spin.valueChanged.connect(self.on_line_spacing_change)

        self.char_spin = QSpinBox()
        self.char_spin.setRange(0, 20)
        self.char_spin.setValue(self.char_spacing)
        self.char_spin.valueChanged.connect(self.on_char_spacing_change)

        layout.addWidget(QLabel("行间距:"))
        layout.addWidget(self.line_spin)
        layout.addWidget(QLabel("字间距:"))
        layout.addWidget(self.char_spin)

        group.setLayout(layout)
        return group

    def _create_border_section(self):
        group = QGroupBox("边框设置")
        layout = QVBoxLayout()

        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 10)
        self.border_spin.setValue(self.border_width)
        self.border_spin.valueChanged.connect(self.on_border_width_change)

        self.border_color_btn = QPushButton("选择边框颜色")
        self.border_color_btn.clicked.connect(self.select_border_color)

        layout.addWidget(QLabel("边框宽度:"))
        layout.addWidget(self.border_spin)
        layout.addWidget(self.border_color_btn)

        group.setLayout(layout)
        return group

    def select_font(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择字体文件", "",
            "字体文件 (*.ttf *.otf)"
        )
        if file_path:
            self.font_path = file_path
            font_name = Path(file_path).name
            self.font_label.setText(font_name)
            self.update_font_preview()
            self.emit_style_changed()

    def update_font_preview(self):
        if self.font_path and Path(self.font_path).exists():
            font_id = QFontDatabase.addApplicationFont(self.font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font = QFont(font_families[0], 16)
                    font.setBold(self.font_bold)
                    self.font_preview.setFont(font)
                    self.font_preview.setStyleSheet("""
                        padding: 10px;
                        background-color: white;
                        border: 1px solid #4CAF50;
                        border-radius: 3px;
                        font-size: 16px;
                    """)
                    return

        font = QFont()
        font.setBold(self.font_bold)
        self.font_preview.setFont(font)
        self.font_preview.setStyleSheet("""
            padding: 10px;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 3px;
            font-size: 16px;
        """)

    def select_color(self):
        color = QColorDialog.getColor(QColor(*self.color), self, "选择文字颜色")
        if color.isValid():
            self.color = (color.red(), color.green(), color.blue())
            self.color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.emit_style_changed()

    def select_bg_color(self):
        color = QColorDialog.getColor(QColor(*self.bg_color[:3]), self, "选择背景颜色")
        if color.isValid():
            self.bg_color = (color.red(), color.green(), color.blue(), 200)
            self.bg_enabled = True
            self.bg_enabled_checkbox.setChecked(True)
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.emit_style_changed()

    def select_border_color(self):
        color = QColorDialog.getColor(QColor(*self.border_color), self, "选择边框颜色")
        if color.isValid():
            self.border_color = (color.red(), color.green(), color.blue())
            self.border_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.emit_style_changed()

    def _create_align_section(self):
        group = QGroupBox("对齐方式")
        layout = QHBoxLayout()

        self.align_left_btn = QPushButton("左对齐")
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.setChecked(True)
        self.align_left_btn.clicked.connect(lambda: self.on_align_change('left'))

        self.align_center_btn = QPushButton("居中")
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.clicked.connect(lambda: self.on_align_change('center'))

        self.align_right_btn = QPushButton("右对齐")
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.clicked.connect(lambda: self.on_align_change('right'))

        layout.addWidget(self.align_left_btn)
        layout.addWidget(self.align_center_btn)
        layout.addWidget(self.align_right_btn)

        group.setLayout(layout)
        return group

    def on_align_change(self, align):
        self.text_align = align
        self.align_left_btn.setChecked(align == 'left')
        self.align_center_btn.setChecked(align == 'center')
        self.align_right_btn.setChecked(align == 'right')
        self.emit_style_changed()

    def on_size_change(self, value):
        self.font_size = value
        self.emit_style_changed()

    def on_bold_change(self, state):
        self.font_bold = (state == Qt.Checked)
        self.update_font_preview()
        self.emit_style_changed()

    def on_bg_enabled_change(self, state):
        self.bg_enabled = (state == Qt.Checked)
        self.bg_color_btn.setEnabled(self.bg_enabled)
        if not self.bg_enabled:
            self.bg_color = (0, 0, 0, 0)
        self.emit_style_changed()

    def on_line_spacing_change(self, value):
        self.line_spacing = value
        self.emit_style_changed()

    def on_char_spacing_change(self, value):
        self.char_spacing = value
        self.emit_style_changed()

    def on_border_width_change(self, value):
        self.border_width = value
        self.emit_style_changed()

    def emit_style_changed(self):
        self.style_changed.emit(self.get_style())
        self.font_size = value
        self.emit_style_changed()

    def on_bold_change(self, state):
        self.font_bold = (state == Qt.Checked)
        self.update_font_preview()
        self.emit_style_changed()

    def on_bg_enabled_change(self, state):
        self.bg_enabled = (state == Qt.Checked)
        self.bg_color_btn.setEnabled(self.bg_enabled)
        if not self.bg_enabled:
            self.bg_color = (0, 0, 0, 0)
        self.emit_style_changed()

    def on_line_spacing_change(self, value):
        self.line_spacing = value
        self.emit_style_changed()

    def on_char_spacing_change(self, value):
        self.char_spacing = value
        self.emit_style_changed()

    def on_border_width_change(self, value):
        self.border_width = value
        self.emit_style_changed()

    def emit_style_changed(self):
        self.style_changed.emit(self.get_style())

    def get_style(self):
        return TextStyle(
            font_path=self.font_path,
            font_size=self.font_size,
            color=self.color,
            line_spacing=self.line_spacing,
            char_spacing=self.char_spacing,
            border_width=self.border_width,
            border_color=self.border_color,
            bg_color=self.bg_color,
            bold=self.font_bold,
            align=self.text_align
        )
