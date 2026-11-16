from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QListWidget, QFileDialog,
    QComboBox, QProgressBar, QMessageBox, QGroupBox, QCheckBox, QSpinBox, QToolButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import sys
from pathlib import Path
from core.models import TaskMode, TextStyle
from core.task_manager import TaskManager
from core.task_manager_mt import TaskManagerMT
from core.input_handler import InputHandler
from utils.validator import validate_task_count
from ui.preview_editor import PreviewEditor

class TaskWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(list)

    def __init__(self, tasks, output_dir, use_multithread=False, max_workers=4):
        super().__init__()
        self.tasks = tasks
        self.output_dir = output_dir
        self.use_multithread = use_multithread
        self.max_workers = max_workers

    def run(self):
        if self.use_multithread:
            results = TaskManagerMT.execute_tasks_parallel(
                self.tasks,
                self.output_dir,
                self.progress.emit,
                self.max_workers
            )
        else:
            results = TaskManager.execute_tasks(
                self.tasks,
                self.output_dir,
                self.progress.emit
            )
        self.finished.emit(results)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.texts = []
        self.editing_text_index = 0
        self.media_files = []
        self.output_dir = str(Path.home() / "Desktop")
        self.task_mode = TaskMode.SINGLE_COPY
        self.text_style = None
        self.text_position = (50, 50)
        self.use_multithread = False
        self.max_workers = 4
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MediaTextWriter - 批量配字工具')
        self.setGeometry(100, 100, 1400, 800)
        self.setAcceptDrops(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 5)
        self.text_input.textChanged.connect(self.on_text_changed)

    def create_left_panel(self):
        panel = QGroupBox("输入区")
        layout = QVBoxLayout()

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("直接输入文案，或拖入TXT/Excel文件...")
        self.text_input.setMaximumHeight(150)
        layout.addWidget(QLabel("文案输入:"))
        layout.addWidget(self.text_input)

        btn_load_txt = QPushButton("选择TXT文件")
        btn_load_txt.clicked.connect(self.load_txt_file)
        layout.addWidget(btn_load_txt)

        btn_load_excel = QPushButton("选择Excel文件")
        btn_load_excel.clicked.connect(self.load_excel_file)
        layout.addWidget(btn_load_excel)

        layout.addWidget(QLabel("\n任务模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["单文复制", "单独对应", "随机对应"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_change)
        layout.addWidget(self.mode_combo)

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.warning_label)

        layout.addWidget(self.create_media_panel(), 1)
        panel.setLayout(layout)
        return panel

    def create_media_panel(self):
        panel = QGroupBox("媒体文件")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("拖入图片/视频/文件夹:"))
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.currentRowChanged.connect(self.update_preview)
        layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("添加文件")
        btn_add.clicked.connect(self.add_media_files)
        btn_folder = QPushButton("添加文件夹")
        btn_folder.clicked.connect(self.add_folder)
        btn_clear = QPushButton("清空列表")
        btn_clear.clicked.connect(self.clear_files)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_folder)
        btn_layout.addWidget(btn_clear)
        layout.addLayout(btn_layout)

        panel.setLayout(layout)
        return panel

    def create_right_panel(self):
        panel = QGroupBox("样式与预览")
        layout = QVBoxLayout()

        self.preview_editor = PreviewEditor()
        self.preview_editor.style_changed.connect(self.on_preview_style_changed)

        layout.addWidget(self.preview_editor, 1)

        self.output_toggle = QToolButton()
        self.output_toggle.setText("输出设置与进度")
        self.output_toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.output_toggle.setArrowType(Qt.RightArrow)
        self.output_toggle.setCheckable(True)
        self.output_toggle.setStyleSheet("QToolButton { border: none; padding: 5px 0; }")
        self.output_toggle.toggled.connect(self.toggle_output_settings)
        layout.addWidget(self.output_toggle)

        self.output_details = QWidget()
        output_group = self.output_details
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(4, 0, 4, 4)
        self.refresh_btn = QPushButton("刷新预览")
        self.refresh_btn.clicked.connect(self.preview_editor.refresh_preview)
        output_layout.addWidget(self.refresh_btn, 0, Qt.AlignLeft)

        dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel(self.output_dir)
        self.output_dir_label.setWordWrap(True)
        btn_select_dir = QPushButton("选择目录")
        btn_select_dir.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(self.output_dir_label, 3)
        dir_layout.addWidget(btn_select_dir, 1)
        output_layout.addLayout(dir_layout)

        perf_layout = QHBoxLayout()
        self.mt_checkbox = QCheckBox("多线程加速")
        self.mt_checkbox.setChecked(self.use_multithread)
        self.mt_checkbox.stateChanged.connect(self.on_multithread_toggle)
        self.worker_spin = QSpinBox()
        self.worker_spin.setRange(2, 8)
        self.worker_spin.setValue(self.max_workers)
        self.worker_spin.valueChanged.connect(self.on_workers_change)
        perf_layout.addWidget(self.mt_checkbox)
        perf_layout.addWidget(QLabel("线程数:"))
        perf_layout.addWidget(self.worker_spin)
        output_layout.addLayout(perf_layout)

        self.progress_bar = QProgressBar()
        output_layout.addWidget(QLabel("任务进度:"))
        output_layout.addWidget(self.progress_bar)

        self.btn_start = QPushButton("开始任务")
        self.btn_start.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        self.btn_start.clicked.connect(self.start_task)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        output_group.hide()
        layout.addWidget(self.btn_start)

        panel.setLayout(layout)
        return panel

    def toggle_output_settings(self, expanded):
        self.output_details.setVisible(expanded)
        self.output_toggle.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.process_dropped_file(file_path)

    def process_dropped_file(self, file_path):
        path = Path(file_path)

        if path.suffix.lower() == '.txt':
            self.set_loaded_texts(InputHandler.parse_txt_file(file_path))
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            self.load_excel_file_path(file_path)
        elif path.is_dir():
            self.add_folder_path(file_path)
        else:
            self.media_files.append(file_path)
            self.file_list.addItem(path.name)

        self.check_input_validation()
        self.update_preview()

    def load_txt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择TXT文件", "", "文本文件 (*.txt)")
        if file_path:
            self.set_loaded_texts(InputHandler.parse_txt_file(file_path))
            self.check_input_validation()
            self.update_preview()

    def load_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)")
        if file_path:
            self.load_excel_file_path(file_path)

    def load_excel_file_path(self, file_path):
        try:
            data = InputHandler.parse_excel_file(file_path)
            self.set_loaded_texts([str(item[1]) for item in data])
            self.check_input_validation()
            self.update_preview()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"Excel解析失败: {e}")

    def add_media_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择媒体文件", "",
            "媒体文件 (*.jpg *.jpeg *.png *.bmp *.webp *.mp4 *.avi *.mov *.mkv)"
        )
        for file_path in files:
            self.media_files.append(file_path)
            self.file_list.addItem(Path(file_path).name)
        self.check_input_validation()
        self.update_preview()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.add_folder_path(folder)

    def add_folder_path(self, folder):
        files = InputHandler.parse_folder(folder)
        self.media_files.extend(files)
        for f in files:
            self.file_list.addItem(Path(f).name)
        self.check_input_validation()
        self.update_preview()

    def clear_files(self):
        self.media_files.clear()
        self.file_list.clear()
        self.check_input_validation()
        self.update_preview()

    def set_loaded_texts(self, texts):
        self.texts = texts
        self.editing_text_index = 0
        self.text_input.blockSignals(True)
        self.text_input.setPlainText(texts[0] if texts else "")
        self.text_input.blockSignals(False)

    def on_text_changed(self):
        text = self.text_input.toPlainText()
        if text.strip() and (len(self.texts) > 1 or self.editing_text_index > 0):
            self.texts.extend([""] * max(0, self.editing_text_index + 1 - len(self.texts)))
            self.texts[self.editing_text_index] = text.strip()
        else:
            self.texts = InputHandler.parse_single_text(text)
        self.check_input_validation()
        self.update_preview()

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_dir = directory
            self.output_dir_label.setText(directory)

    def on_mode_change(self, index):
        modes = [TaskMode.SINGLE_COPY, TaskMode.ONE_TO_ONE, TaskMode.RANDOM_MATCH]
        self.task_mode = modes[index]
        self.check_input_validation()
        self.update_preview()

    def check_input_validation(self):
        text_count = len(self.texts)
        media_count = len(self.media_files)

        valid, message = validate_task_count(text_count, media_count, self.task_mode.value)
        self.warning_label.setText(message)

        return valid

    def start_task(self):
        if not self.check_input_validation():
            QMessageBox.warning(self, "警告", "请检查输入内容")
            return

        if not self.texts or not self.media_files:
            QMessageBox.warning(self, "警告", "请提供文案和媒体文件")
            return

        self.text_style = self.preview_editor.current_style
        self.text_position = self.preview_editor.get_final_position()

        tasks = TaskManager.create_tasks(
            self.texts,
            self.media_files,
            self.task_mode,
            self.text_style,
            self.text_position
        )

        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)

        self.worker = TaskWorker(tasks, self.output_dir, self.use_multithread, self.max_workers)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_preview_style_changed(self, style: TextStyle):
        self.text_style = style

    def on_multithread_toggle(self, state):
        self.use_multithread = (state == Qt.Checked)

    def on_workers_change(self, value):
        self.max_workers = value

    def update_preview(self, _row=None):
        editor = self.preview_editor
        if not self.media_files:
            editor.clear_preview()
            return
        row = max(0, self.file_list.currentRow())
        text_index = row if self.task_mode == TaskMode.ONE_TO_ONE else 0
        text = self.texts[text_index] if text_index < len(self.texts) else ""
        if self.editing_text_index != text_index:
            self.text_input.blockSignals(True)
            self.text_input.setPlainText(text)
            self.text_input.blockSignals(False)
            self.editing_text_index = text_index
        media_path = self.media_files[row]
        if editor.current_media == media_path:
            editor.current_text = text
            editor.render_text_preview()
        else:
            editor.load_preview(media_path, text, editor.current_style)

    def on_progress(self, current, total, message):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)

    def on_finished(self, results):
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(100)
        QMessageBox.information(
            self, "完成",
            f"任务完成！\n生成文件数: {len(results)}\n输出目录: {self.output_dir}"
        )

def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
