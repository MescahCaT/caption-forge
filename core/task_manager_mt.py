from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable
from core.models import Task
from core.media_processor import ImageProcessor, VideoProcessor
from core.output_handler import OutputHandler
from utils.file_utils import is_image, is_video

class TaskManagerMT:

    @staticmethod
    def execute_tasks_parallel(
        tasks: list[Task],
        output_dir: str,
        callback: Callable[[int, int, str], None] = None,
        max_workers: int = 4
    ) -> list[str]:
        output_path = OutputHandler.create_output_directory(output_dir)
        results = []
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    TaskManagerMT._process_single_task,
                    task,
                    output_path
                ): task for task in tasks
            }

            for future in as_completed(futures):
                completed += 1
                task = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    if callback:
                        callback(completed, len(tasks), f'完成: {task.output_name}')
                except Exception as e:
                    if callback:
                        callback(completed, len(tasks), f'失败: {task.output_name} - {str(e)}')

        return results

    @staticmethod
    def _process_single_task(task: Task, output_path: Path) -> str:
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

        return str(output_file)
