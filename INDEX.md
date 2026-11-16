# MediaTextWriter - 项目文档导航

## 🚀 快速导航

### 立即开始
- **[快速入门](QUICKSTART.md)** ⭐ 5分钟上手指南
- **[发布说明](RELEASE.md)** - MVP完成报告

### 使用文档
- **[README](README.md)** - 产品介绍与功能说明
- **[用户手册](USER_GUIDE.md)** - 详细操作指南

### 开发文档
- **[项目规划](PROJECT_PLAN.md)** - 技术栈与开发阶段
- **[架构设计](ARCHITECTURE.md)** - 模块划分与接口
- **[代码规范](CODE_STANDARD.md)** - 开发规范要求
- **[开发进度](PROGRESS.md)** - 任务清单与状态
- **[项目总结](SUMMARY.md)** - 初始化完成报告

---

## 📂 项目结构

```
MediaTextWriter/
├── 📖 文档 (9份)
│   ├── QUICKSTART.md          ⭐ 快速入门
│   ├── RELEASE.md             MVP发布说明
│   ├── README.md              产品介绍
│   ├── USER_GUIDE.md          使用手册
│   ├── PROJECT_PLAN.md        项目规划
│   ├── ARCHITECTURE.md        架构设计
│   ├── CODE_STANDARD.md       代码规范
│   ├── PROGRESS.md            开发进度
│   └── SUMMARY.md             项目总结
│
├── 💻 核心代码
│   ├── main.py                启动入口
│   ├── core/                  业务逻辑 (6模块)
│   ├── ui/                    PyQt5界面
│   ├── utils/                 工具函数 (3模块)
│   └── config/                配置管理
│
├── 🧪 测试
│   ├── tests/                 单元测试 (8个)
│   ├── test_core.py           功能测试
│   └── assets/                测试资源
│
└── 📦 配置
    └── requirements.txt       依赖列表

```

---

## 🎯 使用场景指南

### 我是新用户
1. 阅读 [QUICKSTART.md](QUICKSTART.md)
2. 运行 `python main.py`
3. 使用 `assets/` 中的测试数据试用

### 我想深入了解
1. 阅读 [README.md](README.md) - 了解产品特性
2. 阅读 [USER_GUIDE.md](USER_GUIDE.md) - 学习所有功能
3. 查看测试案例理解使用场景

### 我是开发者
1. 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) - 理解架构
2. 阅读 [CODE_STANDARD.md](CODE_STANDARD.md) - 遵循规范
3. 查看 [PROGRESS.md](PROGRESS.md) - 了解待办任务

### 我要贡献代码
1. 遵循 [CODE_STANDARD.md](CODE_STANDARD.md)
2. 查看 [PROGRESS.md](PROGRESS.md) 选择任务
3. 编写测试用例
4. 提交前运行 `python -m unittest discover tests`

---

## ✅ 项目状态

**版本**：v1.0-MVP  
**状态**：可用于生产  
**完成度**：80%

### 已完成
- ✅ 核心配字功能
- ✅ PyQt5 UI界面
- ✅ 三种任务模式
- ✅ 5种输入方式
- ✅ 完整测试系统

### 待开发
- ⏳ 高级样式配置
- ⏳ 可视化编辑器
- ⏳ 性能优化

---

## 🛠️ 快速命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py

# 运行测试
python test_core.py
python -m unittest discover tests -v

# 查看帮助
python main.py --help  # (暂未实现)
```

---

## 📊 文档分类

### 用户文档
| 文档 | 用途 | 阅读时长 |
|-----|------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 快速上手 | 5分钟 |
| [README.md](README.md) | 产品介绍 | 10分钟 |
| [USER_GUIDE.md](USER_GUIDE.md) | 详细手册 | 30分钟 |

### 开发文档
| 文档 | 用途 | 阅读时长 |
|-----|------|---------|
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | 项目规划 | 15分钟 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构设计 | 20分钟 |
| [CODE_STANDARD.md](CODE_STANDARD.md) | 代码规范 | 15分钟 |

### 管理文档
| 文档 | 用途 | 阅读时长 |
|-----|------|---------|
| [PROGRESS.md](PROGRESS.md) | 开发进度 | 10分钟 |
| [SUMMARY.md](SUMMARY.md) | 项目总结 | 15分钟 |
| [RELEASE.md](RELEASE.md) | 发布说明 | 10分钟 |

---

## 🔍 常见问题快速查找

**如何启动？** → [QUICKSTART.md](QUICKSTART.md)  
**如何配字？** → [QUICKSTART.md](QUICKSTART.md) 示例1-3  
**支持什么格式？** → [README.md](README.md) 功能详解  
**三种模式区别？** → [QUICKSTART.md](QUICKSTART.md) 任务模式  
**文件命名规则？** → [QUICKSTART.md](QUICKSTART.md) 命名规则  
**遇到错误？** → [USER_GUIDE.md](USER_GUIDE.md) 常见问题  
**想贡献代码？** → [CODE_STANDARD.md](CODE_STANDARD.md)  
**架构设计？** → [ARCHITECTURE.md](ARCHITECTURE.md)  
**开发计划？** → [PROGRESS.md](PROGRESS.md)  

---

## 📞 获取帮助

1. **查看文档** - 先查阅相关文档
2. **测试资源** - 使用 `assets/` 测试数据验证
3. **运行测试** - `python test_core.py` 验证环境
4. **查看日志** - 控制台输出错误信息

---

## ⭐ 推荐阅读顺序

### 新用户（20分钟）
1. [QUICKSTART.md](QUICKSTART.md) - 5分钟
2. [README.md](README.md) - 10分钟
3. 实际操作 - 5分钟

### 开发者（1小时）
1. [README.md](README.md) - 10分钟
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 20分钟
3. [CODE_STANDARD.md](CODE_STANDARD.md) - 15分钟
4. 阅读源码 - 15分钟

### 贡献者（1.5小时）
1. 开发者路径 - 1小时
2. [PROGRESS.md](PROGRESS.md) - 10分钟
3. [PROJECT_PLAN.md](PROJECT_PLAN.md) - 20分钟

---

**最后更新**：2026-08-26  
**项目状态**：✅ MVP完成
