import sys
from pathlib import Path
from core.models import TextStyle, Task, TaskMode
from core.task_manager import TaskManager
from core.task_manager_mt import TaskManagerMT

def test_style_panel():
    """测试样式配置"""
    style = TextStyle(
        font_path="",
        font_size=32,
        color=(255, 255, 0),
        line_spacing=15,
        char_spacing=3,
        border_width=2,
        border_color=(0, 0, 0),
        bg_color=(255, 0, 0, 100)
    )
    print(f"[OK] 样式配置测试通过: {style}")

def test_multithread():
    """测试多线程处理"""
    test_images = list(Path("assets").glob("*.jpg"))[:3]
    if not test_images:
        print("[WARN] 未找到测试图片，跳过多线程测试")
        return

    style = TextStyle("", 24, (255, 255, 255), 10, 2)
    tasks = [
        Task(str(img), f"测试文本{i}", style, (50, 50), f"test_mt_{i}.jpg")
        for i, img in enumerate(test_images)
    ]

    output_dir = Path("test_output_mt")
    output_dir.mkdir(exist_ok=True)

    results = TaskManagerMT.execute_tasks_parallel(
        tasks, str(output_dir), max_workers=2
    )

    print(f"[OK] 多线程测试完成，生成{len(results)}个文件")

def test_preview_position():
    """测试位置计算"""
    from PyQt5.QtWidgets import QApplication
    from ui.preview_editor import PreviewEditor
    app = QApplication.instance() or QApplication([])
    editor = PreviewEditor()
    editor.text_position = (100, 200)
    pos = editor.get_final_position()
    assert pos == (100, 200), "位置计算错误"
    editor.close()
    app.processEvents()
    print(f"[OK] 位置计算测试通过: {pos}")

if __name__ == "__main__":
    print("=== 新功能测试 ===\n")

    test_style_panel()
    test_preview_position()

    if "--mt" in sys.argv:
        test_multithread()

    print("\n[OK] 所有测试完成")
