from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
try:
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
except ImportError:
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
from core.models import TextStyle
from config.settings import VIDEO_CODEC
from utils.emoji_utils import emoji_image, split_graphemes

class ImageProcessor:

    @staticmethod
    def draw_text_on_image(
        image_path: str,
        text: str,
        style: TextStyle,
        position: tuple[int, int]
    ) -> Image.Image:
        """在图片上绘制文本"""
        with Image.open(image_path) as image:
            overlay = ImageProcessor.render_text_overlay(image.size, text, style, position)
            return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')

    @staticmethod
    def render_text_overlay(size, text, style, position):
        overlay = Image.new('RGBA', size, (0, 0, 0, 0))
        if not text:
            return overlay
        font_path = style.font_path if style.font_path and Path(style.font_path).exists() else "arial.ttf"
        try:
            font = ImageFont.truetype(font_path, style.font_size)
        except OSError:
            font = ImageFont.load_default(size=style.font_size)
        draw = ImageDraw.Draw(overlay)
        padding = max(8, (style.line_spacing + 1) // 2)
        x_base, y = position
        area_width = max(1, size[0] - 90)
        spacing = style.char_spacing
        paragraphs = [list(split_graphemes(paragraph)) for paragraph in text.split('\n')]
        tokens = {token for paragraph in paragraphs for token in paragraph}
        emojis = {token: emoji_image(token, style.font_size) for token in tokens}
        advances = {
            token: style.font_size if emojis[token] is not None else draw.textlength(token, font=font)
            for token in tokens
        }

        def measure(line):
            return sum(advances[char] for char in line) + max(0, len(line) - 1) * spacing

        lines = []
        for paragraph in paragraphs:
            line = []
            for char in paragraph:
                if line and measure(line + [char]) > area_width:
                    lines.append(line)
                    line = []
                line.append(char)
            lines.append(line)
        ascent, descent = font.getmetrics()
        height = ascent + descent
        line_data = []
        for line in lines:
            width = measure(line)
            offset = area_width - width
            x = x_base + (offset / 2 if style.align == 'center' else offset if style.align == 'right' else 0)
            line_data.append((line, x, y, width))
            y += height + style.line_spacing
        if style.bg_color[3] > 0:
            for line, x, y, width in line_data:
                if ''.join(line).strip():
                    draw.rounded_rectangle(
                        (x - padding, y - padding, x + width + padding, y + height + padding),
                        radius=min(max(0, style.bg_radius), (width + padding * 2) / 2,
                                   (height + padding * 2) / 2),
                        fill=style.bg_color
                    )
        for line, x, y, _ in line_data:
            for char in line:
                if emojis[char] is not None:
                    overlay.alpha_composite(
                        emojis[char], (round(x), round(y + max(0, (height - style.font_size) / 2)))
                    )
                else:
                    draw.text(
                        (x, y), char, font=font, anchor='la', fill=style.color,
                        stroke_width=style.border_width + int(style.bold),
                        stroke_fill=style.border_color if style.border_width else style.color
                    )
                x += advances[char] + spacing
        return overlay

class VideoProcessor:

    @staticmethod
    def add_text_to_video(
        video_path: str,
        text: str,
        style: TextStyle,
        position: tuple[int, int],
        output_path: str
    ):
        """在视频上添加文本"""
        video = VideoFileClip(video_path)
        txt_clip = final = None
        try:
            overlay = ImageProcessor.render_text_overlay(tuple(video.size), text, style, position)
            txt_clip = ImageClip(np.array(overlay), duration=video.duration)
            final = CompositeVideoClip([video, txt_clip])
            final.write_videofile(output_path, codec=VIDEO_CODEC, audio_codec='aac')
        finally:
            if final is not None:
                final.close()
            if txt_clip is not None:
                txt_clip.close()
            video.close()
