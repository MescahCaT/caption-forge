import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dataclasses import replace

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PIL import Image, ImageFont
from PyQt5.QtCore import QEvent, QPointF, QSettings, Qt
from PyQt5.QtGui import QFontDatabase, QImage, QMouseEvent
from PyQt5.QtWidgets import QApplication, QTabWidget, QPushButton, QSlider
from core.media_processor import ImageProcessor
from core.models import TextStyle
from config.style_presets import StylePresets
from ui.main_window import MainWindow


class TestPreviewSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        fonts = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
        candidates = [fonts / name for name in ('arial.ttf', 'msyh.ttc', 'simsun.ttc')]
        candidates.append(Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        cls.font_path = next((str(path) for path in candidates if path.exists()
                              and QFontDatabase.addApplicationFont(str(path)) != -1), None)
        cls.directory = tempfile.TemporaryDirectory()
        cls.files = []
        for index in range(2):
            path = Path(cls.directory.name) / f'{index}.png'
            Image.new('RGB', (500, 320), (20 + index, 30, 40)).save(path)
            cls.files.append(str(path))

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def setUp(self):
        settings = QSettings(str(Path(self.directory.name) / 'preview-styles.ini'), QSettings.IniFormat)
        settings.clear()
        with patch('ui.preview_editor.StylePresets', return_value=StylePresets(settings)):
            self.window = MainWindow()
        for path in self.files:
            self.window.process_dropped_file(path)
        self.editor = self.window.preview_editor

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_text_edit_and_clear(self):
        self.window.text_input.setPlainText('first\nsecond')
        self.assertEqual(self.editor.current_text, 'first\nsecond')
        self.window.text_input.setPlainText('replacement')
        self.assertEqual(self.window.texts, ['replacement'])
        self.assertEqual(self.editor.canvas.text_to_render, 'replacement')
        self.window.text_input.clear()
        self.assertEqual(self.window.texts, [])
        self.assertEqual(self.editor.canvas.text_to_render, '')
        self.assertEqual(self.editor.canvas.pixmap().toImage(), self.editor.canvas.base_pixmap.toImage())

    def test_import_edit_preserves_batch_and_mode(self):
        self.window.set_loaded_texts(['first', 'second'])
        self.window.text_input.setPlainText('edited')
        self.assertEqual(self.window.texts, ['edited', 'second'])
        self.window.file_list.setCurrentRow(1)
        self.assertEqual(self.editor.current_text, 'edited')
        self.window.mode_combo.setCurrentIndex(1)
        self.assertEqual(self.editor.current_text, 'second')
        self.assertEqual(self.window.text_input.toPlainText(), 'second')
        self.window.text_input.setPlainText('second edited')
        self.assertEqual(self.window.texts, ['edited', 'second edited'])

    def test_alignment_changes_pixels_and_switch_preserves_style(self):
        if not self.font_path:
            self.skipTest('No font available for offscreen pixel comparison')
        self.window.text_input.setPlainText('Short text')
        self.editor.apply_style(font_path=self.font_path)
        images = []
        for align, button in [('left', self.editor.align_left),
                              ('center', self.editor.align_center),
                              ('right', self.editor.align_right)]:
            button.click()
            self.assertEqual(self.editor.current_style.align, align)
            images.append(self.editor.canvas.pixmap().toImage())
        self.assertNotEqual(images[0], images[1])
        self.assertNotEqual(images[1], images[2])
        self.editor.size_slider.setValue(47)
        self.editor.bold_btn.click()
        self.editor.line_spin.setValue(17)
        style = self.editor.current_style
        self.window.file_list.setCurrentRow(1)
        self.assertIs(self.editor.current_style, style)
        self.assertEqual(self.editor.current_media, self.files[1])
        self.assertEqual(self.editor.size_slider.value(), 47)
        self.assertEqual(self.editor.size_label.text(), '47')

    def test_clear_media_and_layout(self):
        self.assertEqual(self.window.centralWidget().layout().count(), 2)
        self.assertFalse(self.window.findChildren(QTabWidget))
        left = self.window.centralWidget().layout().itemAt(0).widget()
        self.assertTrue(left.isAncestorOf(self.window.file_list))
        self.window.clear_files()
        self.assertEqual(self.window.media_files, [])
        self.assertIsNone(self.editor.current_media)
        self.assertIsNone(self.editor.canvas.base_pixmap)
        self.assertFalse(hasattr(self.editor, 'text_box'))
        self.assertFalse(any(button.text() == '\u6587\u672c\u6846'
                             for button in self.editor.findChildren(QPushButton)))
        self.assertIsInstance(self.editor.size_slider, QSlider)

    def test_start_task_uses_preview_style(self):
        self.window.text_input.setPlainText('export text')
        self.editor.size_slider.setValue(53)
        self.editor.align_center.click()
        style = self.editor.current_style
        with patch('ui.main_window.TaskWorker') as worker, \
                patch('ui.main_window.TaskManager.create_tasks', return_value=[]) as create:
            self.window.start_task()
        self.assertIs(create.call_args.args[3], style)
        self.assertEqual(create.call_args.args[0], ['export text'])
        worker.return_value.start.assert_called_once_with()

    def test_rounded_line_background(self):
        style = TextStyle(self.font_path or '', 24, (0, 0, 0),
                          bg_color=(255, 255, 255, 180), align='center', bg_radius=10)
        text = 'I\nA much longer line\nShort'
        rounded = ImageProcessor.render_text_overlay((500, 320), text, style, (50, 50))
        square = ImageProcessor.render_text_overlay((500, 320), text,
                                                    replace(style, bg_radius=0), (50, 50))
        self.assertNotEqual(rounded.tobytes(), square.tobytes())
        alpha = rounded.getchannel('A')
        font = ImageFont.truetype(self.font_path, 24) if self.font_path else ImageFont.load_default(size=24)
        ascent, descent = font.getmetrics()
        height = ascent + descent
        spans = []
        for index in range(3):
            y = 50 + index * (height + style.line_spacing) + height // 2
            spans.append(sum(alpha.getpixel((x, y)) > 0 for x in range(500)))
        self.assertGreater(spans[1], spans[0])
        self.assertGreater(spans[1], spans[2])
        self.assertLessEqual(alpha.getpixel((50, 50)), 180)
        background_alpha = {pixel[3] for pixel in rounded.getdata()
                            if pixel[:3] == (255, 255, 255)}
        self.assertEqual(background_alpha, {180})

    def test_preview_matches_export_and_slider_uses_cached_image(self):
        self.window.text_input.setPlainText('Short\nA longer centered line')
        self.editor.apply_style(font_path=self.font_path or '', color=(0, 0, 0),
                                bg_color=(255, 255, 255, 255), align='center')
        with patch('ui.preview_editor.Image.open') as opened:
            self.editor.size_slider.setValue(31)
            self.editor.radius_spin.setValue(12)
        opened.assert_not_called()
        self.assertEqual(self.editor.current_style.bg_radius, 12)
        expected = ImageProcessor.draw_text_on_image(
            self.files[0], self.editor.current_text, self.editor.current_style,
            self.editor.get_final_position())
        pixmap = self.editor.canvas.pixmap()
        expected = expected.resize((pixmap.width(), pixmap.height()), Image.Resampling.LANCZOS)
        data = expected.tobytes('raw', 'RGB')
        qimage = QImage(data, expected.width, expected.height,
                        expected.width * 3, QImage.Format_RGB888)
        self.assertEqual(pixmap.toImage().convertToFormat(QImage.Format_RGB888), qimage)

    def canvas_point(self, x, y):
        canvas = self.editor.canvas
        rect = canvas.contentsRect()
        width, height = canvas.base_pixmap.width(), canvas.base_pixmap.height()
        return QPointF(rect.x() + (rect.width() - width) / 2
                       + x * width / canvas.source_image.width,
                       rect.y() + (rect.height() - height) / 2
                       + y * height / canvas.source_image.height)

    def send_mouse(self, kind, point):
        button = Qt.NoButton if kind == QEvent.MouseMove else Qt.LeftButton
        buttons = Qt.NoButton if kind == QEvent.MouseButtonRelease else Qt.LeftButton
        QApplication.sendEvent(self.editor.canvas, QMouseEvent(kind, point, button, buttons, Qt.NoModifier))

    def test_drag_all_alignments_without_background_and_export_position(self):
        self.window.text_input.setPlainText('Drag me')
        self.editor.apply_style(font_path=self.font_path or '', bg_color=(0, 0, 0, 0))
        for align in ('left', 'center', 'right'):
            with self.subTest(align=align):
                self.editor.text_position = (50, 50)
                self.editor.apply_style(align=align)
                bounds = self.editor.canvas.text_bounds
                start = self.canvas_point((bounds[0] + bounds[2]) / 2,
                                          (bounds[1] + bounds[3]) / 2)
                self.send_mouse(QEvent.MouseButtonPress, start)
                self.assertIsNotNone(self.editor.canvas.drag_start)
                self.send_mouse(QEvent.MouseMove, start + QPointF(-15, 12))
                self.assertEqual(self.editor.get_final_position(), (35, 62))
                self.send_mouse(QEvent.MouseMove, start + QPointF(-25, 20))
                self.assertEqual(self.editor.get_final_position(), (25, 70))
                self.assertEqual(self.editor.canvas.text_bounds,
                                 (bounds[0] - 25, bounds[1] + 20,
                                  bounds[2] - 25, bounds[3] + 20))
                self.send_mouse(QEvent.MouseButtonRelease, start + QPointF(-25, 20))
                self.assertIsNone(self.editor.canvas.drag_start)
                with patch('ui.main_window.TaskWorker'), \
                        patch('ui.main_window.TaskManager.create_tasks', return_value=[]) as create:
                    self.window.start_task()
                self.assertEqual(create.call_args.args[4], (25, 70))
                exported = ImageProcessor.draw_text_on_image(
                    self.files[0], self.editor.current_text, self.editor.current_style, (25, 70))
                data = exported.tobytes('raw', 'RGB')
                expected = QImage(data, exported.width, exported.height,
                                  exported.width * 3, QImage.Format_RGB888)
                self.assertEqual(self.editor.canvas.pixmap().toImage().convertToFormat(
                    QImage.Format_RGB888), expected)

    def test_drag_translation_preserves_wrapped_text(self):
        style = replace(self.editor.current_style, font_path=self.font_path or '', align='right')
        text = 'A sentence that wraps across several lines. ' * 4
        original = ImageProcessor.render_text_overlay((500, 600), text, style, (50, 50))
        moved = ImageProcessor.render_text_overlay((500, 600), text, style, (25, 70))
        original_bounds = original.getbbox()
        moved_bounds = moved.getbbox()
        self.assertEqual(moved_bounds, (original_bounds[0] - 25, original_bounds[1] + 20,
                                        original_bounds[2] - 25, original_bounds[3] + 20))
        self.assertEqual(original.crop(original_bounds).tobytes(), moved.crop(moved_bounds).tobytes())

    def test_drag_scaled_centered_image_and_clamp(self):
        path = Path(self.directory.name) / 'scaled.png'
        Image.new('RGB', (1400, 800), (20, 30, 40)).save(path)
        self.editor.load_preview(str(path), 'Scaled drag', self.editor.current_style)
        canvas = self.editor.canvas
        canvas.setFixedSize(900, 600)
        bounds = canvas.text_bounds
        start = self.canvas_point((bounds[0] + bounds[2]) / 2,
                                  (bounds[1] + bounds[3]) / 2)
        self.send_mouse(QEvent.MouseButtonPress, start)
        self.send_mouse(QEvent.MouseMove, start + QPointF(20, 15))
        self.assertEqual(self.editor.get_final_position(), (90, 80))
        self.send_mouse(QEvent.MouseMove, start + QPointF(30, 20))
        self.assertEqual(self.editor.get_final_position(), (110, 90))
        self.send_mouse(QEvent.MouseMove, start + QPointF(3000, 3000))
        self.assertEqual(self.editor.get_final_position(),
                         (50 + 1400 - bounds[2], 50 + 800 - bounds[3]))
        self.send_mouse(QEvent.MouseMove, start - QPointF(3000, 3000))
        self.assertEqual(self.editor.get_final_position(), (50 - bounds[0], 50 - bounds[1]))
        self.send_mouse(QEvent.MouseButtonRelease, start)

    def test_blank_click_and_clear_cancel_drag(self):
        self.window.text_input.setPlainText('Drag me')
        original = self.editor.get_final_position()
        blank = self.canvas_point(5, 5)
        self.send_mouse(QEvent.MouseButtonPress, blank)
        self.send_mouse(QEvent.MouseMove, blank + QPointF(30, 20))
        self.assertEqual(self.editor.get_final_position(), original)
        self.assertIsNone(self.editor.canvas.drag_start)
        bounds = self.editor.canvas.text_bounds
        text = self.canvas_point((bounds[0] + bounds[2]) / 2,
                                 (bounds[1] + bounds[3]) / 2)
        self.send_mouse(QEvent.MouseButtonPress, text)
        self.window.text_input.clear()
        self.assertIsNone(self.editor.canvas.drag_start)
        self.assertIsNone(self.editor.canvas.text_bounds)
        self.send_mouse(QEvent.MouseMove, text + QPointF(40, 30))
        self.assertEqual(self.editor.get_final_position(), original)
        self.window.clear_files()
        self.assertIsNone(self.editor.canvas.source_image)
        self.assertIsNone(self.editor.canvas.text_bounds)
        self.send_mouse(QEvent.MouseButtonPress, blank)
        self.send_mouse(QEvent.MouseMove, blank + QPointF(30, 20))
        self.assertEqual(self.editor.get_final_position(), original)


if __name__ == '__main__':
    unittest.main()
