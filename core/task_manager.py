import random
from pathlib import Path
from typing import Callable
from core.models import Task, TaskMode, TextStyle
from core.media_processor import ImageProcessor, VideoProcessor
from core.output_handler import OutputHandler
from utils.file_utils import is_image, is_video

class TaskManager:

    @staticmethod
    def create_tasks(
        texts: list[str],
        media_files: list[str],
        mode: TaskMode,
        style: TextStyle,
        position: tuple[int, int]
    ) -> list[Task]:
        """创建任务列表"""
        tasks = []

        if mode == TaskMode.SINGLE_COPY:
            text = texts[0] if texts else ''
            for media in media_files:
                output_name = OutputHandler.generate_filename(media, text)
                tasks.append(Task(media, text, style, position, output_name))

        elif mode == TaskMode.ONE_TO_ONE:
            count = min(len(texts), len(media_files))
            for i in range(count):
                output_name = OutputHandler.generate_filename(media_files[i], texts[i])
                tasks.append(Task(media_files[i], texts[i], style, position, output_name))

        elif mode == TaskMode.RANDOM_MATCH:
            count = min(len(texts), len(media_files))
            shuffled_texts = texts.copy()
            random.shuffle(shuffled_texts)
            for i in range(count):
                output_name = OutputHandler.generate_filename(media_files[i], shuffled_texts[i])
                tasks.append(Task(media_files[i], shuffled_texts[i], style, position, output_name))

        return tasks

    @staticmethod
    def execute_tasks(
        tasks: list[Task],
        output_dir: str,
        callback: Callable[[int, int, str], None] = None
    ) -> list[str]:
        """执行任务"""
        output_path = OutputHandler.create_output_directory(output_dir)
        results = []

        for idx, task in enumerate(tasks):
            try:
                output_file = output_path / task.output_name

                if is_image(task.media_path):
                    processed_image = ImageProcessor.draw_text_on_image(
                        task.media_path,
                        task.text,
                        task.style,
                        task.position
                    )
                    OutputHandler.save_image(processed_image, str(output_file))

                elif is_video(task.media_path):
                    VideoProcessor.add_text_to_video(
                        task.media_path,
                        task.text,
                        task.style,
                        task.position,
                        str(output_file)
                    )

                results.append(str(output_file))

                if callback:
                    callback(idx + 1, len(tasks), f'已完成: {task.output_name}')

            except Exception as e:
                if callback:
                    callback(idx + 1, len(tasks), f'失败: {task.output_name} - {e}')

        return results
