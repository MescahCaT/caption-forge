# MediaTextWriter 架构设计

## 模块划分

### 1. core/input_handler.py
**职责**：统一输入接口，解析各类输入源

```python
class InputHandler:
    def parse_single_text(text: str) -> list[str]
    def parse_txt_file(file_path: str) -> list[str]
    def parse_excel_file(file_path: str) -> list[tuple[Image, str]]
    def parse_folder(folder_path: str) -> list[str]
    def parse_single_media(file_path: str) -> str
    def validate_input_combination(text_source, media_source) -> bool
```

**关键逻辑**：
- txt双回车分段
- Excel提取嵌入图片
- 文件夹过滤（图片/视频格式）
- 上传规则校验

---

### 2. core/text_processor.py
**职责**：文本处理与换行计算

```python
class TextProcessor:
    def calculate_text_lines(text: str, font, max_width: int) -> list[str]
    def measure_text_size(text: str, font) -> tuple[int, int]
    def apply_line_spacing(lines: list[str], spacing: int) -> int
    def strip_text_prefix(text: str, length: int) -> str
```

**关键逻辑**：
- 按字体宽度自动换行
- 中英文混排处理
- 行间距/字间距计算
- 文本截取（命名用前6字符）

---

### 3. core/media_processor.py
**职责**：图片/视频文本写入

```python
class ImageProcessor:
    def draw_text_on_image(
        image_path: str,
        text: str,
        style: TextStyle,
        position: tuple[int, int]
    ) -> Image
    
class VideoProcessor:
    def add_text_to_video(
        video_path: str,
        text: str,
        style: TextStyle,
        position: tuple[int, int]
    ) -> str
```

**关键逻辑**：
- Pillow绘制文字（图片）
- MoviePy添加TextClip（视频）
- 背景框/边框绘制
- 透明度处理

---

### 4. core/task_manager.py
**职责**：任务调度与模式匹配

```python
class TaskManager:
    def create_tasks(
        texts: list[str],
        media_files: list[str],
        mode: TaskMode
    ) -> list[Task]
    
    def execute_tasks(
        tasks: list[Task],
        output_dir: str,
        callback: Callable
    ) -> list[str]

class Task:
    media_path: str
    text: str
    output_name: str
```

**三种模式**：
- `SINGLE_COPY`：所有媒体用同一文案
- `ONE_TO_ONE`：文案与媒体一一对应
- `RANDOM_MATCH`：随机匹配

---

### 5. core/output_handler.py
**职责**：输出文件生成

```python
class OutputHandler:
    def generate_filename(media_name: str, text: str) -> str
    def save_image(image: Image, output_path: str)
    def save_video(video_path: str, output_path: str)
    def create_output_directory(base_dir: str) -> str
```

**命名规则**：`媒体名前6位_文本前6字符.ext`

---

### 6. ui/main_window.py
**职责**：主界面布局

**区域划分**：
- 顶部：输入区（拖拽上传）
- 左侧：任务模式选择
- 中部：文件列表预览
- 右侧：样式配置面板
- 底部：开始任务按钮

**交互流程**：
```
上传文件 → 校验规则 → 显示警告 → 选择模式 → 配置样式 → 预览编辑 → 执行任务
```

---

### 7. ui/preview_editor.py
**职责**：可视化文本位置调整

```python
class PreviewEditor:
    def load_preview(media_path: str, text: str, style: TextStyle)
    def on_textbox_drag(event)
    def on_textbox_resize(event)
    def get_final_position() -> tuple[int, int]
```

**功能**：
- 显示媒体+文本框
- 拖动改变位置
- 缩放改变大小
- 实时更新样式

---

### 8. ui/style_panel.py
**职责**：样式配置界面

```python
class StylePanel:
    font_selector: FontSelector
    font_size_slider: Slider
    color_picker: ColorPicker
    spacing_inputs: dict
    border_config: BorderConfig
    background_config: BackgroundConfig
```

**配置项**：
- 字体选择/导入
- 字体大小（10-200）
- 行间距/字间距
- 字体颜色
- 边框（颜色、宽度）
- 背景色+透明度（0-100%）

---

### 9. utils/file_utils.py
**职责**：文件操作工具

```python
def is_image(file_path: str) -> bool
def is_video(file_path: str) -> bool
def scan_folder(folder_path: str) -> dict[str, list[str]]
def validate_path(path: str) -> bool
def get_file_extension(file_path: str) -> str
```

---

### 10. utils/text_utils.py
**职责**：文本处理工具

```python
def split_by_double_newline(text: str) -> list[str]
def remove_spaces(text: str) -> str
def truncate_text(text: str, length: int) -> str
def is_cjk_char(char: str) -> bool
```

---

### 11. utils/validator.py
**职责**：输入校验

```python
def validate_task_count(text_count: int, media_count: int, mode: str) -> tuple[bool, str]
def validate_font_file(file_path: str) -> bool
def validate_output_dir(dir_path: str) -> bool
```

---

### 12. config/settings.py
**职责**：全局配置常量

```python
# 支持格式
IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']

# 限制
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_BATCH_COUNT = 500
MAX_TEXT_LENGTH = 1000

# 默认样式
DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_COLOR = (255, 255, 255)
DEFAULT_LINE_SPACING = 10
DEFAULT_CHAR_SPACING = 2

# 输出
VIDEO_OUTPUT_FORMAT = 'mp4'
VIDEO_CODEC = 'libx264'
```

---

## 数据流

```
输入层 (InputHandler)
    ↓ list[str], list[Image/str]
文本处理 (TextProcessor)
    ↓ 分段、换行
任务调度 (TaskManager)
    ↓ list[Task]
媒体处理 (MediaProcessor)
    ↓ 绘制文字
输出层 (OutputHandler)
    ↓ 保存文件
```

## 核心类定义

```python
@dataclass
class TextStyle:
    font_path: str
    font_size: int
    color: tuple[int, int, int]
    line_spacing: int
    char_spacing: int
    border_width: int = 0
    border_color: tuple[int, int, int] = (0, 0, 0)
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0)  # RGBA
    
@dataclass
class Task:
    media_path: str
    text: str
    style: TextStyle
    position: tuple[int, int]
    output_name: str
    
class TaskMode(Enum):
    SINGLE_COPY = "single_copy"
    ONE_TO_ONE = "one_to_one"
    RANDOM_MATCH = "random_match"
```

## 扩展点

### 字体管理
- `config/default_fonts/` 存放内置字体
- `FontManager` 管理字体加载/缓存

### 进度回调
```python
def on_progress(current: int, total: int, status: str):
    # UI更新进度条
    pass
```

### 模板预设
- 保存常用样式配置
- 快速加载预设

## 依赖关系图

```
main.py
  ├── ui.main_window
  │     ├── ui.preview_editor
  │     ├── ui.style_panel
  │     └── core.task_manager
  │           ├── core.input_handler
  │           ├── core.text_processor
  │           ├── core.media_processor
  │           └── core.output_handler
  └── config.settings

utils层被所有模块调用
```
