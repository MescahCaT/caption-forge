#!/usr/bin/env python3
"""
MediaTextWriter 快速测试脚本
测试核心功能（无UI）
"""

from pathlib import Path
from core.models import TextStyle, TaskMode
from core.task_manager import TaskManager
from config.settings import DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR

def quick_test():
    """快速功能测试"""
    print("MediaTextWriter 核心功能测试\n")

    texts = ["测试文案1", "测试文案2", "测试文案3"]
    media_files = ["test1.jpg", "test2.jpg", "test3.jpg"]

    style = TextStyle(
        font_path="",
        font_size=DEFAULT_FONT_SIZE,
        color=DEFAULT_FONT_COLOR
    )

    print("1. 测试单文复制模式")
    tasks = TaskManager.create_tasks(
        texts[:1],
        media_files,
        TaskMode.SINGLE_COPY,
        style,
        (50, 50)
    )
    print(f"   生成任务数: {len(tasks)}")

    print("\n2. 测试一一对应模式")
    tasks = TaskManager.create_tasks(
        texts,
        media_files,
        TaskMode.ONE_TO_ONE,
        style,
        (50, 50)
    )
    print(f"   生成任务数: {len(tasks)}")

    print("\n3. 测试随机对应模式")
    tasks = TaskManager.create_tasks(
        texts,
        media_files,
        TaskMode.RANDOM_MATCH,
        style,
        (50, 50)
    )
    print(f"   生成任务数: {len(tasks)}")
    for i, task in enumerate(tasks):
        print(f"   任务{i+1}: {task.output_name}")

    print("\n[OK] 核心功能测试通过")

if __name__ == '__main__':
    quick_test()
