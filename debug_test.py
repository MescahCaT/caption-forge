#!/usr/bin/env python3
"""
调试脚本 - 测试完整流程
"""

from pathlib import Path
from core.input_handler import InputHandler
from core.task_manager import TaskManager
from core.models import TextStyle, TaskMode
from config.settings import DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR, DEFAULT_LINE_SPACING, DEFAULT_CHAR_SPACING

def debug_test():
    print("=" * 60)
    print("MediaTextWriter 调试测试")
    print("=" * 60)

    # 测试1: 解析文本
    print("\n[测试1] 解析单条文本")
    text = "测试文案内容"
    texts = InputHandler.parse_single_text(text)
    print(f"  输入: {text}")
    print(f"  解析结果: {texts}")
    print(f"  文案数量: {len(texts)}")

    # 测试2: 解析TXT文件
    print("\n[测试2] 解析TXT文件")
    txt_file = "assets/test_captions.txt"
    if Path(txt_file).exists():
        texts = InputHandler.parse_txt_file(txt_file)
        print(f"  文件: {txt_file}")
        print(f"  文案数量: {len(texts)}")
        for i, t in enumerate(texts, 1):
            print(f"  文案{i}: {t[:20]}...")
    else:
        print(f"  文件不存在: {txt_file}")

    # 测试3: 扫描媒体文件
    print("\n[测试3] 扫描媒体文件")
    folder = "assets"
    if Path(folder).exists():
        media_files = InputHandler.parse_folder(folder)
        print(f"  文件夹: {folder}")
        print(f"  媒体数量: {len(media_files)}")
        for f in media_files:
            print(f"  - {Path(f).name}")
    else:
        print(f"  文件夹不存在: {folder}")

    # 测试4: 创建任务
    print("\n[测试4] 创建任务")
    if texts and media_files:
        style = TextStyle(
            font_path="",
            font_size=DEFAULT_FONT_SIZE,
            color=DEFAULT_FONT_COLOR,
            line_spacing=DEFAULT_LINE_SPACING,
            char_spacing=DEFAULT_CHAR_SPACING
        )

        tasks = TaskManager.create_tasks(
            texts,
            media_files,
            TaskMode.SINGLE_COPY,
            style,
            (50, 50)
        )

        print(f"  模式: 单文复制")
        print(f"  生成任务数: {len(tasks)}")
        for i, task in enumerate(tasks[:3], 1):
            print(f"  任务{i}: {task.output_name}")
    else:
        print("  跳过 - 缺少文案或媒体文件")

    # 测试5: 实际处理一个任务
    print("\n[测试5] 实际处理测试")
    if len(texts) > 0 and len(media_files) > 0:
        from core.media_processor import ImageProcessor
        from core.output_handler import OutputHandler
        from utils.file_utils import is_image

        test_media = None
        for f in media_files:
            if is_image(f):
                test_media = f
                break

        if test_media:
            print(f"  测试图片: {Path(test_media).name}")
            print(f"  测试文案: {texts[0][:20]}...")

            try:
                output_dir = Path("test_output")
                output_dir.mkdir(exist_ok=True)

                processed = ImageProcessor.draw_text_on_image(
                    test_media,
                    texts[0],
                    style,
                    (100, 100)
                )

                output_name = OutputHandler.generate_filename(test_media, texts[0])
                output_path = output_dir / output_name
                OutputHandler.save_image(processed, str(output_path))

                print(f"  输出文件: {output_path}")
                print(f"  文件大小: {output_path.stat().st_size} bytes")
                print("  [OK] 处理成功!")

            except Exception as e:
                print(f"  [ERROR] 处理失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("  跳过 - 没有找到图片文件")

    print("\n" + "=" * 60)
    print("调试测试完成")
    print("=" * 60)

if __name__ == '__main__':
    debug_test()
