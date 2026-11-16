import contextlib
import io
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import numpy as np
from PIL import Image, ImageFont
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication
from config.style_presets import StylePresets
from core.media_processor import ImageProcessor, VideoProcessor, VideoFileClip
from core.models import TextStyle
from ui.preview_editor import PreviewEditor
from utils.emoji_utils import emoji_image, split_graphemes


EMOJIS = ('\U0001f44b', '\U0001f44b\U0001f3fd', '\U0001f1fa\U0001f1f8',
          '\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466',
          '\u2764\ufe0f', '1\ufe0f\u20e3')


class TestEmojiRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.style = TextStyle('', 40, (255, 0, 255), char_spacing=0)

    def tearDown(self):
        self.directory.cleanup()

    def test_combined_emoji_are_single_tokens_and_have_color_assets(self):
        self.assertEqual(list(split_graphemes('A' + ''.join(EMOJIS) + 'B')), ['A', *EMOJIS, 'B'])
        for token in EMOJIS:
            with self.subTest(token=token):
                self.assertEqual(list(split_graphemes(token)), [token])
                image = emoji_image(token, 40)
                self.assertIsNotNone(image)
                self.assertEqual(image.size, (40, 40))
                pixels = np.asarray(image)
                visible = pixels[pixels[:, :, 3] > 200, :3]
                self.assertGreater(np.unique(visible, axis=0).shape[0], 10)
                self.assertTrue(np.any(np.ptp(visible.astype(int), axis=1) > 30))

    def test_emoji_pixels_ignore_text_color_bold_and_outline(self):
        text = ''.join(EMOJIS)
        image = ImageProcessor.render_text_overlay((500, 140), text, self.style, (20, 20))
        changed = ImageProcessor.render_text_overlay(
            (500, 140), text, replace(self.style, color=(0, 255, 0), bold=True,
                                     border_width=7, border_color=(0, 0, 255)), (20, 20))
        self.assertIsNotNone(image.getbbox())
        self.assertEqual(image.tobytes(), changed.tobytes())

    def test_plain_text_uses_font_without_emoji_image(self):
        text = 'Plain ABC 123'
        for token in split_graphemes(text):
            self.assertIsNone(emoji_image(token, 40))
        normal = ImageProcessor.render_text_overlay((500, 140), text, self.style, (20, 20))
        with patch('core.media_processor.emoji_image', return_value=None) as lookup:
            without_assets = ImageProcessor.render_text_overlay((500, 140), text, self.style, (20, 20))
        self.assertIsNotNone(normal.getbbox())
        self.assertEqual(normal.tobytes(), without_assets.tobytes())
        self.assertEqual({call.args[0] for call in lookup.call_args_list}, set(text))

    def test_text_presentation_symbols_require_vs16_for_emoji(self):
        for symbol in ('\u00a9', '\u00ae', '\u2122', '\u2194', '\u2600'):
            with self.subTest(symbol=symbol):
                self.assertIsNone(emoji_image(symbol, 40))
                self.assertIsNotNone(emoji_image(symbol + '\ufe0f', 40))
        self.assertIsNotNone(emoji_image(EMOJIS[0], 40))

    def test_wrap_keeps_complete_emoji_sequences(self):
        size = (135, 450)
        rendered = ImageProcessor.render_text_overlay(size, ''.join(EMOJIS), self.style, (10, 10))
        expected = Image.new('RGBA', size)
        try:
            font = ImageFont.truetype('arial.ttf', 40)
        except OSError:
            font = ImageFont.load_default(size=40)
        ascent, descent = font.getmetrics()
        height = ascent + descent
        for index, token in enumerate(EMOJIS):
            y = 10 + index * (height + self.style.line_spacing)
            expected.alpha_composite(emoji_image(token, 40),
                                     (10, round(y + max(0, (height - 40) / 2))))
        self.assertEqual(rendered.tobytes(), expected.tobytes())

    def test_preview_matches_saved_image_export(self):
        source = Path(self.directory.name) / 'source.png'
        output = Path(self.directory.name) / 'export.png'
        Image.new('RGB', (500, 300), (30, 40, 50)).save(source)
        settings = QSettings(str(Path(self.directory.name) / 'styles.ini'), QSettings.IniFormat)
        editor = PreviewEditor(StylePresets(settings))
        try:
            text = 'Hello ' + ''.join(EMOJIS)
            editor.load_preview(str(source), text, self.style)
            ImageProcessor.draw_text_on_image(str(source), text, self.style,
                                              editor.get_final_position()).save(output)
            with Image.open(output) as exported:
                data = exported.tobytes('raw', 'RGB')
                expected = QImage(data, exported.width, exported.height,
                                  exported.width * 3, QImage.Format_RGB888)
                self.assertEqual(editor.canvas.pixmap().toImage().convertToFormat(
                    QImage.Format_RGB888), expected)
        finally:
            editor.deleteLater()

    def test_short_video_contains_color_emoji(self):
        try:
            from moviepy import ColorClip
        except ImportError:
            from moviepy.editor import ColorClip
        source = str(Path(self.directory.name) / 'source.mp4')
        output = str(Path(self.directory.name) / 'emoji.mp4')
        clip = ColorClip((320, 180), color=(25, 25, 25), duration=0.3)
        try:
            clip.write_videofile(source, fps=10, codec='libx264', audio=False, logger=None)
        finally:
            clip.close()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            VideoProcessor.add_text_to_video(source, EMOJIS[1], self.style, (50, 50), output)
        video = VideoFileClip(output)
        try:
            frame = video.get_frame(0.1).astype(int)
            expected = np.asarray(ImageProcessor.draw_text_on_image(
                self.make_video_background(), EMOJIS[1], self.style, (50, 50))).astype(int)
            crop = frame[50:105, 50:95]
            self.assertGreater(np.count_nonzero(np.ptp(crop, axis=2) > 35), 200)
            self.assertLess(np.abs(frame - expected).mean(), 5)
        finally:
            video.close()

    def make_video_background(self):
        path = Path(self.directory.name) / 'video-background.png'
        Image.new('RGB', (320, 180), (25, 25, 25)).save(path)
        return str(path)


if __name__ == '__main__':
    unittest.main()
