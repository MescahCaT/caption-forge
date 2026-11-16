# MediaTextWriter 代码规范

## 文件组织

### 模块职责
- `core/` - 业务逻辑，无UI依赖
- `ui/` - 界面层，调用core
- `utils/` - 纯函数工具
- `config/` - 配置常量

### 单一职责
每个模块只处理一类问题，函数长度≤50行

## 命名规范

```python
# 文件名：snake_case
input_handler.py
text_processor.py

# 类名：PascalCase
class MediaProcessor:
class TaskManager:

# 函数/变量：snake_case
def process_text():
media_file_path = ""

# 常量：UPPER_CASE
MAX_TEXT_LENGTH = 1000
DEFAULT_FONT_SIZE = 24
```

## 注释规范

### 只写必要注释
```python
# ✅ 好的注释
def split_text_by_width(text: str, max_width: int) -> list[str]:
    """按宽度分割文本，超出自动换行"""
    pass

# ❌ 不必要的注释
# 循环遍历列表
for item in items:
    # 处理item
    process(item)
```

### 关键逻辑标注
```python
# Excel图片列需手动提取嵌入对象
images = extract_embedded_images(worksheet)

# #FIXME: 视频处理超10MB时内存占用过高
```

## 导入规范

```python
# 标准库
import os
from pathlib import Path

# 第三方库
from PIL import Image, ImageDraw
import openpyxl

# 本地模块
from core.text_processor import TextProcessor
from utils.file_utils import validate_path
```

**删除未使用的导入**

## 函数规范

### 类型注解
```python
def process_image(
    image_path: str,
    text: str,
    font_size: int = 24
) -> str:
    """
    处理单张图片
    
    Args:
        image_path: 图片路径
        text: 待写入文本
        font_size: 字体大小，默认24
    
    Returns:
        输出文件路径
    """
    pass
```

### 参数数量
- 参数≤5个，超过用dataclass或dict

### 返回值
- 单一类型，避免`Union[str, None, list]`
- 错误用异常，不返回None表示失败

## 错误处理

### 关键流程捕获
```python
def load_excel(file_path: str) -> list[tuple]:
    try:
        workbook = openpyxl.load_workbook(file_path)
        return parse_worksheet(workbook.active)
    except Exception as e:
        raise ValueError(f"Excel解析失败: {e}")
```

### 不做多层冗余
```python
# ❌ 过度防御
try:
    try:
        data = load_file()
    except:
        data = None
except:
    pass

# ✅ 简洁明确
data = load_file()  # 让调用者处理异常
```

## 代码清洁

### 禁止提交
```python
# ❌ 调试代码
print(f"DEBUG: {variable}")
# import pdb; pdb.set_trace()

# ❌ 注释的旧代码
# old_function()
# if False:
#     legacy_logic()

# ❌ 未使用变量
temp = calculate()  # 未被读取
```

### 配置外置
```python
# ❌ 硬编码
if font_size > 100:
    
# ✅ 配置常量
from config.settings import MAX_FONT_SIZE
if font_size > MAX_FONT_SIZE:
```

## 分层架构

```
UI层 → Core层 → Utils层
 ↓       ↓        ↓
只调用  业务逻辑  纯函数
下层    无UI依赖  无状态
```

### 依赖方向
- UI可调用Core和Utils
- Core可调用Utils
- Utils不依赖任何模块
- Core不依赖UI

## 测试规范

### 关键逻辑必测
- 文本分段逻辑
- 文件名生成规则
- 任务模式匹配
- 换行计算

### 测试文件
```
tests/
├── test_text_processor.py
├── test_media_processor.py
└── test_file_utils.py
```

## Git提交

### Commit格式
```
[模块] 简短描述

详细说明（可选）
```

示例：
```
[core] 实现文本自动换行

根据字体宽度计算换行位置，支持中英文混排
```

### 提交粒度
- 一个功能点一次提交
- 不混杂多个改动
- 删除废代码单独提交

## 性能约束

- 单图处理<2秒
- 批量任务显示进度
- 大文件流式读取
- 避免全局变量缓存

## 禁止项

❌ 全局可变状态  
❌ 循环导入  
❌ 硬编码路径  
❌ 裸露异常（except: pass）  
❌ 魔法数字（直接写数值）  
❌ 超长函数（>50行）  
❌ 深层嵌套（>3层）
