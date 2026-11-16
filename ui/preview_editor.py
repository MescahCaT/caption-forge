from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QSpinBox, QSlider, QColorDialog, QCheckBox, QButtonGroup, QFileDialog, QGridLayout, QScrollArea,
    QComboBox, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QSignalBlocker, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QImage
from pathlib import Path
from PIL import Image
from dataclasses import replace
from core.models import TextStyle
from core.media_processor import ImageProcessor
from config.settings import DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR
from config.style_presets import StylePresets

class PreviewCanvas(QLabel):
    position_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_pixmap = None
        self.source_image = None
        self.text_to_render = ""
        self.text_style = None
        self.text_position = (50, 50)
        self.text_bounds = None
        self.drag_start = None
        self.setMouseTracking(True)

    def image_point(self, point):
        rect = self.contentsRect()
        width, height = self.base_pixmap.width(), self.base_pixmap.height()
        left = rect.x() + (rect.width() - width) / 2
        top = rect.y() + (rect.height() - height) / 2
        return QPointF((point.x() - left) * self.source_image.width / width,
                       (point.y() - top) * self.source_image.height / height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.text_bounds is not None:
            point = self.image_point(event.pos())
            left, top, right, bottom = self.text_bounds
            if QRectF(left, top, right - left, bottom - top).contains(point):
                self.drag_start = (point, self.text_position, self.text_bounds)
                self.setCursor(Qt.ClosedHandCursor)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_start is not None:
            point, position, bounds = self.drag_start
            delta = self.image_point(event.pos()) - point
            left, top, right, bottom = bounds
            dx = max(-left, min(round(delta.x()), self.source_image.width - right))
            dy = max(-top, min(round(delta.y()), self.source_image.height - bottom))
            self.position_changed.emit(position[0] + dx, position[1] + dy)
            event.accept()
            return
        if self.text_bounds is not None:
            left, top, right, bottom = self.text_bounds
            hit = QRectF(left, top, right - left, bottom - top).contains(self.image_point(event.pos()))
            self.setCursor(Qt.OpenHandCursor if hit else Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_start is not None:
            self.drag_start = None
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_base_image(self, pixmap):
        self.base_pixmap = pixmap
        self.update_display()

    def set_text_style(self, text, style, position):
        self.text_to_render = text
        self.text_style = style
        self.text_position = position
        self.update_display()

    def update_display(self):
        if self.base_pixmap is None:
            return
        if not self.text_to_render or self.source_image is None:
            self.text_bounds = None
            self.drag_start = None
            self.unsetCursor()
            self.setPixmap(self.base_pixmap)
            return
        overlay = ImageProcessor.render_text_overlay(
            self.source_image.size, self.text_to_render, self.text_style, self.text_position
        )
        self.text_bounds = overlay.getchannel('A').getbbox()
        image = Image.alpha_composite(self.source_image, overlay).convert('RGB')
        image = image.resize(
            (self.base_pixmap.width(), self.base_pixmap.height()), Image.Resampling.LANCZOS
        )
        data = image.tobytes('raw', 'RGB')
        qimage = QImage(data, image.width, image.height, image.width * 3, QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qimage))

class PreviewEditor(QWidget):
    style_changed = pyqtSignal(TextStyle)

    def __init__(self, preset_store=None):
        super().__init__()
        self.preset_store = preset_store if preset_store is not None else StylePresets()
        self.presets = {}
        self.current_media = None
        self.current_text = ""
        self.current_style = TextStyle('', DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR)
        self.text_position = (50, 50)
        self.init_ui()
        self.set_style(self.current_style)
        self.load_presets()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addLayout(self._create_preset_controls())

        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        layout.addWidget(self._create_style_controls())

        self.canvas = PreviewCanvas()
        self.canvas.position_changed.connect(self.on_position_changed)
        self.canvas.setToolTip("按住文字拖动位置")
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444;")
        self.canvas.setMinimumSize(500, 400)

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setAlignment(Qt.AlignCenter)
        layout.addWidget(scroll, 1)
        self.setLayout(layout)

    def _create_preset_controls(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("自定义样式"))
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumContentsLength(12)
        self.preset_combo.activated[int].connect(self.apply_preset)
        layout.addWidget(self.preset_combo, 1)
        self.save_preset_btn = QPushButton("保存当前样式")
        self.save_preset_btn.clicked.connect(self.save_preset)
        layout.addWidget(self.save_preset_btn)
        return layout

    def load_presets(self):
        try:
            self.presets = self.preset_store.load()
            self.save_preset_btn.setEnabled(True)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            self.save_preset_btn.setEnabled(False)
            QMessageBox.warning(self, "读取样式失败", str(error))
        self.refresh_presets()

    def refresh_presets(self, selected=None):
        self.preset_combo.clear()
        self.preset_combo.addItem("选择已保存的样式", None)
        for name in sorted(self.presets):
            self.preset_combo.addItem(name, name)
        if selected is not None:
            self.preset_combo.setCurrentIndex(self.preset_combo.findData(selected))

    def save_preset(self):
        if not self.save_preset_btn.isEnabled():
            return
        name, accepted = QInputDialog.getText(self, "保存自定义样式", "样式名称：")
        name = name.strip()
        if not accepted or not name:
            return
        if name in self.presets and QMessageBox.question(
            self, "覆盖样式", f"是否覆盖“{name}”？", QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        ) != QMessageBox.Yes:
            return
        presets = {**self.presets, name: replace(self.current_style)}
        try:
            self.preset_store.save(presets)
        except OSError as error:
            QMessageBox.warning(self, "保存样式失败", str(error))
            return
        self.presets = presets
        self.refresh_presets(name)

    def apply_preset(self, index):
        name = self.preset_combo.itemData(index)
        if name is None:
            return
        style = self.presets[name]
        if style.font_path and not Path(style.font_path).is_file():
            QMessageBox.warning(self, "字体文件不存在", "请重新选择字体后保存该样式。")
            return
        self.set_style(replace(style))
        self.render_text_preview()
        self.style_changed.emit(self.current_style)

    def _create_toolbar(self):
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #f5f5f5; padding: 5px; border-radius: 5px;")
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 200)
        self.size_slider.setMinimumWidth(130)
        self.size_slider.setMaximumWidth(240)
        self.size_slider.valueChanged.connect(self.on_toolbar_change)
        self.size_label = QLabel()
        self.size_label.setMinimumWidth(28)

        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setMaximumWidth(30)
        self.bold_btn.setStyleSheet("font-weight: bold;")
        self.bold_btn.toggled.connect(self.on_toolbar_change)

        self.color_btn = QPushButton("A")
        self.color_btn.setMaximumWidth(30)
        self.color_btn.setStyleSheet("color: white; background-color: black; font-weight: bold;")
        self.color_btn.clicked.connect(self.select_text_color)

        self.bg_check = QCheckBox("背景")
        self.bg_check.setChecked(False)
        self.bg_check.toggled.connect(self.on_toolbar_change)

        self.align_group = QButtonGroup(self)
        self.align_left = QPushButton("左对齐")
        self.align_left.setCheckable(True)
        self.align_left.setChecked(True)
        self.align_left.setMinimumWidth(60)

        self.align_center = QPushButton("居中")
        self.align_center.setCheckable(True)
        self.align_center.setMinimumWidth(60)

        self.align_right = QPushButton("右对齐")
        self.align_right.setCheckable(True)
        self.align_right.setMinimumWidth(60)

        self.align_group.addButton(self.align_left, 0)
        self.align_group.addButton(self.align_center, 1)
        self.align_group.addButton(self.align_right, 2)
        self.align_group.buttonClicked.connect(self.on_toolbar_change)

        layout.addWidget(QLabel("字号:"))
        layout.addWidget(self.size_slider)
        layout.addWidget(self.size_label)
        layout.addWidget(self.bold_btn)
        layout.addWidget(self.color_btn)
        layout.addWidget(self.bg_check)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.align_left)
        layout.addWidget(self.align_center)
        layout.addWidget(self.align_right)
        layout.addStretch()

        toolbar.setLayout(layout)
        return toolbar

    def _create_style_controls(self):
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        font_btn = QPushButton("选择字体")
        font_btn.clicked.connect(self.select_font)
        self.font_label = QLabel("系统默认")
        self.font_label.setMaximumWidth(180)
        layout.addWidget(font_btn, 0, 0)
        layout.addWidget(self.font_label, 0, 1)
        for column, (title, field) in enumerate([
            ("背景色", "bg_color"), ("描边色", "border_color")
        ], 2):
            button = QPushButton(title)
            button.clicked.connect(lambda _checked, name=field: self.select_style_color(name))
            layout.addWidget(button, 0, column)
        self.line_spin = QSpinBox()
        self.line_spin.setRange(0, 50)
        self.char_spin = QSpinBox()
        self.char_spin.setRange(0, 20)
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 10)
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 100)
        for column, (title, spin) in enumerate([
            ("行间距", self.line_spin), ("字间距", self.char_spin),
            ("描边", self.border_spin), ("圆角", self.radius_spin)
        ]):
            row = QHBoxLayout()
            row.addWidget(QLabel(title))
            row.addWidget(spin)
            layout.addLayout(row, 1, column)
            spin.valueChanged.connect(self.on_toolbar_change)
        return panel

    def set_style(self, style):
        controls = [
            self.size_slider, self.bold_btn, self.bg_check, self.line_spin,
            self.char_spin, self.border_spin, self.radius_spin, self.align_left,
            self.align_center, self.align_right
        ]
        blockers = [QSignalBlocker(control) for control in controls]
        self.current_style = style
        self.size_slider.setValue(style.font_size)
        self.size_label.setText(str(style.font_size))
        self.bold_btn.setChecked(style.bold)
        self.bg_check.setChecked(style.bg_color[3] > 0)
        self.line_spin.setValue(style.line_spacing)
        self.char_spin.setValue(style.char_spacing)
        self.border_spin.setValue(style.border_width)
        self.radius_spin.setValue(style.bg_radius)
        self.align_group.button(['left', 'center', 'right'].index(style.align)).setChecked(True)
        self.font_label.setText(Path(style.font_path).name if style.font_path else "系统默认")
        self.color_btn.setStyleSheet(f"background-color: {QColor(*style.color).name()};")
        del blockers

    def apply_style(self, **changes):
        self.preset_combo.setCurrentIndex(0)
        self.set_style(replace(self.current_style, **changes))
        self.render_text_preview()
        self.style_changed.emit(self.current_style)

    def select_font(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择字体文件", "", "字体文件 (*.ttf *.otf)")
        if path:
            self.apply_style(font_path=path)

    def select_style_color(self, field):
        color = QColorDialog.getColor(QColor(*getattr(self.current_style, field)), self)
        if color.isValid():
            value = (color.red(), color.green(), color.blue())
            if field == 'bg_color':
                value += (255,)
            self.apply_style(**{field: value})

    def select_text_color(self):
        self.select_style_color('color')

    def on_toolbar_change(self):
        bg_color = self.current_style.bg_color
        if self.bg_check.isChecked() and bg_color[3] == 0:
            bg_color = (0, 0, 0, 180)
        elif not self.bg_check.isChecked():
            bg_color = (0, 0, 0, 0)
        self.apply_style(
            font_size=self.size_slider.value(),
            bold=self.bold_btn.isChecked(),
            align=['left', 'center', 'right'][self.align_group.checkedId()],
            line_spacing=self.line_spin.value(),
            char_spacing=self.char_spin.value(),
            border_width=self.border_spin.value(),
            bg_radius=self.radius_spin.value(),
            bg_color=bg_color
        )

    def clear_preview(self):
        self.current_media = None
        self.current_text = ""
        self.canvas.base_pixmap = None
        self.canvas.source_image = None
        self.canvas.text_to_render = ""
        self.canvas.text_bounds = None
        self.canvas.drag_start = None
        self.canvas.unsetCursor()
        self.canvas.clear()
        self.canvas.setText("未加载媒体文件")

    def refresh_preview(self):
        if self.current_media:
            self.load_preview(self.current_media, self.current_text, self.current_style)

    def load_preview(self, media_path: str, text: str, style: TextStyle):
        self.canvas.drag_start = None
        self.canvas.unsetCursor()
        self.current_media = media_path
        self.current_text = text
        self.set_style(style)
        if not media_path or not Path(media_path).exists():
            self.clear_preview()
            return

        try:
            with Image.open(media_path) as source:
                self.canvas.source_image = source.convert('RGBA')
            image = self.canvas.source_image.convert('RGB')

            max_width = 700
            max_height = 600
            aspect_ratio = image.height / image.width

            if image.width > max_width:
                display_width = max_width
                display_height = int(display_width * aspect_ratio)
            else:
                display_width = image.width
                display_height = image.height

            if display_height > max_height:
                display_height = max_height
                display_width = int(display_height / aspect_ratio)

            image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

            data = image.tobytes('raw', 'RGB')
            qimage = QImage(data, image.width, image.height, image.width * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            self.canvas.set_base_image(pixmap)
            self.canvas.setFixedSize(pixmap.size())
            self.render_text_preview()

        except Exception as e:
            self.clear_preview()
            self.canvas.setText(f"预览加载失败: {e}")

    def render_text_preview(self):
        self.canvas.set_text_style(
            self.current_text,
            self.current_style,
            self.text_position
        )

    def get_final_position(self) -> tuple[int, int]:
        return self.text_position

    def on_position_changed(self, x, y):
        self.text_position = (x, y)
        self.render_text_preview()
