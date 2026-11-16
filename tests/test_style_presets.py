import os
import json
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PIL import Image
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox
from config.style_presets import StylePresets
from core.models import TextStyle
from ui.main_window import MainWindow
from ui.preview_editor import PreviewEditor


class TestStylePresets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.ini = str(Path(self.directory.name) / 'styles.ini')
        self.store = StylePresets(QSettings(self.ini, QSettings.IniFormat))
        with patch('ui.preview_editor.StylePresets', return_value=self.store):
            self.window = MainWindow()
        self.editor = self.window.preview_editor
        self.style = TextStyle('', 37, (12, 34, 56), line_spacing=19, char_spacing=4,
                               border_width=3, border_color=(67, 89, 101),
                               bg_color=(123, 145, 167, 180), bold=True, align='right', bg_radius=23)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.directory.cleanup()

    def test_store_rebuild_restores_every_style_field(self):
        self.style.font_path = str(Path(self.directory.name) / 'named font.ttf')
        self.store.save({'中文样式': self.style})
        rebuilt = StylePresets(QSettings(self.ini, QSettings.IniFormat))
        self.assertEqual(asdict(rebuilt.load()['中文样式']), asdict(self.style))
        editor = PreviewEditor(rebuilt)
        self.assertEqual(editor.preset_combo.itemData(1), '中文样式')
        self.assertEqual(editor.presets['中文样式'], self.style)
        editor.deleteLater()

    def test_save_apply_updates_controls_preview_and_export(self):
        path = Path(self.directory.name) / 'image.png'
        Image.new('RGB', (500, 320), (20, 30, 40)).save(path)
        self.window.process_dropped_file(str(path))
        self.window.text_input.setPlainText('Saved style')
        self.editor.apply_style(**asdict(self.style))
        expected_image = self.editor.canvas.pixmap().toImage()
        with patch('ui.preview_editor.QInputDialog.getText', return_value=(' Named ', True)):
            self.editor.save_preset_btn.click()
        self.assertEqual(self.store.load(), {'Named': self.style})
        self.assertIsNot(self.editor.presets['Named'], self.editor.current_style)
        self.editor.apply_style(font_size=18, align='left', bg_color=(0, 0, 0, 0))
        self.assertIsNone(self.editor.preset_combo.currentData())
        self.assertEqual(self.store.load()['Named'], self.style)
        self.editor.preset_combo.activated[int].emit(self.editor.preset_combo.findData('Named'))
        self.assertEqual(self.editor.current_style, self.style)
        self.assertEqual(self.window.text_style, self.style)
        self.assertEqual(self.editor.size_slider.value(), 37)
        self.assertEqual(self.editor.line_spin.value(), 19)
        self.assertEqual(self.editor.char_spin.value(), 4)
        self.assertEqual(self.editor.border_spin.value(), 3)
        self.assertEqual(self.editor.radius_spin.value(), 23)
        self.assertTrue(self.editor.bold_btn.isChecked())
        self.assertTrue(self.editor.bg_check.isChecked())
        self.assertTrue(self.editor.align_right.isChecked())
        self.assertEqual(self.editor.canvas.pixmap().toImage(), expected_image)
        with patch('ui.main_window.TaskWorker'), \
                patch('ui.main_window.TaskManager.create_tasks', return_value=[]) as create:
            self.window.start_task()
        self.assertEqual(create.call_args.args[3], self.style)

    def test_cancel_empty_and_declined_overwrite_do_not_write(self):
        self.store.save({'Existing': self.style})
        self.editor.load_presets()
        before = self.store.settings.value('styles')
        with patch.object(self.store, 'save', wraps=self.store.save) as save:
            for answer in [('Cancel', False), ('', True), ('   ', True), ('Existing', True)]:
                with self.subTest(answer=answer), \
                        patch('ui.preview_editor.QInputDialog.getText', return_value=answer), \
                        patch('ui.preview_editor.QMessageBox.question', return_value=QMessageBox.No):
                    self.editor.save_preset_btn.click()
            save.assert_not_called()
        self.assertEqual(self.store.settings.value('styles'), before)
        self.assertEqual(self.editor.presets, {'Existing': self.style})

    def test_confirmed_overwrite_replaces_saved_style(self):
        self.store.save({'Existing': self.style})
        self.editor.load_presets()
        self.editor.apply_style(font_size=65)
        expected = replace(self.editor.current_style)
        with patch('ui.preview_editor.QInputDialog.getText', return_value=('Existing', True)), \
                patch('ui.preview_editor.QMessageBox.question', return_value=QMessageBox.Yes):
            self.editor.save_preset_btn.click()
        self.assertEqual(self.store.load(), {'Existing': expected})
        self.assertEqual(self.editor.preset_combo.count(), 2)

    def test_missing_font_does_not_apply(self):
        missing = replace(self.style, font_path=str(Path(self.directory.name) / 'missing.ttf'))
        self.store.save({'Missing': missing})
        self.editor.load_presets()
        before = self.editor.current_style
        with patch('ui.preview_editor.QMessageBox.warning') as warning, \
                patch.object(self.editor, 'render_text_preview') as render:
            self.editor.preset_combo.activated[int].emit(self.editor.preset_combo.findData('Missing'))
        warning.assert_called_once()
        render.assert_not_called()
        self.assertIs(self.editor.current_style, before)

    def test_output_toggle_keeps_start_visible_and_refresh_inside(self):
        self.window.show()
        self.app.processEvents()
        self.assertFalse(self.window.output_toggle.isChecked())
        self.assertTrue(self.window.output_details.isHidden())
        self.assertFalse(self.window.refresh_btn.isVisible())
        self.assertTrue(self.window.btn_start.isVisible())
        self.assertTrue(self.window.output_details.isAncestorOf(self.window.refresh_btn))
        self.assertFalse(self.window.output_details.isAncestorOf(self.window.btn_start))
        for expanded in (True, False):
            self.window.output_toggle.click()
            self.app.processEvents()
            self.assertEqual(self.window.output_details.isVisible(), expanded)
            self.assertEqual(self.window.refresh_btn.isVisible(), expanded)
            self.assertTrue(self.window.btn_start.isVisible())
            self.assertEqual(self.window.output_toggle.arrowType(),
                             Qt.DownArrow if expanded else Qt.RightArrow)

    def test_refresh_reloads_current_media_and_preserves_style_position(self):
        path = Path(self.directory.name) / 'refresh.png'
        Image.new('RGB', (500, 320), (10, 20, 30)).save(path)
        self.window.process_dropped_file(str(path))
        self.window.text_input.setPlainText('Refresh this')
        self.editor.apply_style(**asdict(self.style))
        self.editor.on_position_changed(23, 71)
        Image.new('RGB', (500, 320), (90, 100, 110)).save(path)
        self.window.output_toggle.click()
        self.window.refresh_btn.click()
        self.assertEqual(self.editor.canvas.source_image.getpixel((0, 0)), (90, 100, 110, 255))
        self.assertEqual(self.editor.current_style, self.style)
        self.assertEqual(self.editor.current_text, 'Refresh this')
        self.assertEqual(self.editor.get_final_position(), (23, 71))

    def test_invalid_preset_values_are_rejected(self):
        invalid = {
            'font_path': [None, 42], 'bold': [0, 'true'], 'align': ['justify', None],
            'font_size': [9, 201, 24.0, True], 'line_spacing': [-1, 51, '10'],
            'char_spacing': [-1, 21], 'border_width': [-1, 11], 'bg_radius': [-1, 101],
            'color': [[1, 2], [0, 0, 256], [False, 2, 3]],
            'border_color': [[-1, 2, 3], [1, 2, 3, 4]],
            'bg_color': [[1, 2, 3], [1, 2, 3, -1], [1, 2, 3, '255']],
        }
        for field, values in invalid.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    data = {**asdict(self.style), field: value}
                    self.store.settings.setValue('styles', json.dumps({'Broken': data}))
                    with self.assertRaises((ValueError, TypeError)):
                        self.store.load()

    def test_failed_load_disables_save_and_preserves_stored_data(self):
        for raw in ('not valid json', json.dumps({'Broken': {**asdict(self.style), 'font_size': 0}})):
            with self.subTest(raw=raw):
                self.store.settings.setValue('styles', raw)
                self.store.settings.sync()
                with patch('ui.preview_editor.QMessageBox.warning') as warning:
                    editor = PreviewEditor(self.store)
                warning.assert_called_once()
                self.assertFalse(editor.save_preset_btn.isEnabled())
                self.assertEqual(editor.preset_combo.count(), 1)
                with patch.object(self.store, 'save') as save, \
                        patch('ui.preview_editor.QInputDialog.getText') as dialog:
                    editor.save_preset_btn.click()
                    editor.save_preset()
                save.assert_not_called()
                dialog.assert_not_called()
                self.assertEqual(self.store.settings.value('styles'), raw)
                editor.deleteLater()


if __name__ == '__main__':
    unittest.main()
