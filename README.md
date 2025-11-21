# 企业会议格式化工具

## 📄 项目简介

企业级会议纪要文档转换工具，支持高质量的Markdown到PDF转换。提供JavaScript和Python两种实现方式，确保最优的转换效果和文档质量。

## 🚀 快速使用

### 一键启动（推荐）
```bash
# 自动安装依赖并启动
./md2pdf

# 快速转换单个文件
./md2pdf 会议纪要.md

# 批量转换所有文件
./md2pdf --all

# 使用指定主题
./md2pdf --all --theme enterprise

# 查看帮助
./md2pdf --help
```

### 直接调用
```bash
# 安装依赖（仅首次需要）
pip3 install -r requirements.txt

# Claude风格CLI（推荐）
python3 src/cli_converter.py

# 增强版本（多功能）
python3 src/md2pdf_enhanced.py

# 基础版本（简单）
python3 src/md2pdf.py

# JavaScript版本
node md2pdf.js
```

## ✨ 功能特点

- 🎨 **高质量转换**: 参考VS Code Markdown PDF插件样式
- 📖 **丰富格式支持**: 表格、代码块、语法高亮、目录
- 🎯 **企业级样式**: 专业的GitHub风格排版
- ⚙️ **灵活配置**: 支持页面格式、边距、缩放等自定义
- 🔧 **双语言支持**: JavaScript和Python实现
- 📱 **跨平台兼容**: macOS、Windows、Linux全平台支持

## ⚙️ 高级配置

### Python版本选项
```bash
python3 md2pdf.py --help

可选参数:
  --format {A4,A3,A5,Legal,Letter,Tabloid}  页面格式(默认: A4)
  --scale SCALE                             缩放比例(默认: 1.0)
  --margin-top MARGIN_TOP                   上边距(默认: 20mm)
  --margin-bottom MARGIN_BOTTOM             下边距(默认: 20mm)
  --margin-left MARGIN_LEFT                 左边距(默认: 15mm)
  --margin-right MARGIN_RIGHT               右边距(默认: 15mm)
```

### 样式特性

- **企业级设计**: 基于GitHub风格的专业排版
- **完整语法高亮**: 支持多种编程语言代码块
- **优化的表格**: 清晰的边框和条纹背景
- **响应式字体**: Inter字体主体，JetBrains Mono代码
- **打印优化**: 专门的打印样式，避免内容截断

## 🛠️ 技术架构

### Python版本
- **Markdown解析**: Python-Markdown + 扩展
- **PDF生成**: Pyppeteer (Puppeteer的Python版本) 
- **语法高亮**: Pygments
- **样式系统**: GitHub风格CSS + Google Fonts

### JavaScript版本
- **Markdown解析**: marked.js
- **PDF生成**: Puppeteer + Chrome headless
- **语法高亮**: highlight.js
- **样式系统**: GitHub风格CSS

## 📋 项目结构

```
├── md2pdf                    # 🌟 主启动器（推荐）
├── convert                   # 简易启动器
├── requirements.txt          # Python依赖配置
├── package.json             # Node.js依赖配置
├── md2pdf.js                # JavaScript转换器
├── README.md                # 使用说明文档
└── src/                     # 源代码目录
    ├── __init__.py
    ├── cli_converter.py     # Claude风格CLI
    ├── md2pdf_enhanced.py   # 增强版转换器
    ├── md2pdf.py           # 基础版转换器
    ├── batch_convert_example.py  # 批量转换示例
    └── demo.py             # 功能演示
```

## 🔧 故障排除

### 常见问题
1. **Python依赖安装失败**: 确保Python 3.7+版本，使用`pip3 install -r requirements.txt`
2. **Chromium下载慢**: 首次运行时会自动下载Chromium，需要稳定网络连接
3. **字体加载问题**: 确保网络连接正常以加载Google Fonts
4. **中文显示异常**: 检查Markdown文件编码为UTF-8

### 性能优化
- 大文件转换建议使用Python版本
- 批量转换可以编写简单的脚本调用
- 复杂表格建议适当调整页面边距

## 🎨 增强版功能 (md2pdf_enhanced.py)

最新的增强版本提供更多高级功能：

### 🎯 多主题支持
- **GitHub主题**: 现代化的GitHub样式（默认）
- **企业主题**: 专业的商务文档风格
- **学术主题**: 适合学术论文的传统排版

### ⚡ 批量转换
```bash
# 批量转换模式
python3 md2pdf_enhanced.py --batch

# 支持多选：1,3,5 或 1-3 或 all
```

### ⚙️ 配置管理
```bash
# 配置管理
python3 md2pdf_enhanced.py --config

# 示例配置
theme=enterprise
auto_open=true
scale=0.9
```

### 🚀 使用示例
```bash
# 交互式选择（推荐）
python3 md2pdf_enhanced.py

# 使用企业主题
python3 md2pdf_enhanced.py --theme enterprise file.md

# 批量转换所有文件
python3 md2pdf_enhanced.py --batch
```

## 💡 版本对比

| 功能 | 基础版 | 增强版 | Claude CLI |
|------|-------|---------|---------|
| 基础转换 | ✅ | ✅ | ✅ |
| 交互选择 | ✅ | ✅ | ✅ |
| 多主题 | ❌ | ✅ | ✅ |
| 批量转换 | ❌ | ✅ | ✅ |
| 配置管理 | ❌ | ✅ | ❌ |
| 自动打开 | ❌ | ✅ | ❌ |
| 进度显示 | ❌ | ✅ | ✅ |
| CLI友好性 | 一般 | 一般 | ⭐⭐⭐ |
| 命令行参数 | 基础 | 丰富 | 简洁 |
| 使用复杂度 | 简单 | 复杂 | 简单 |

## 💡 选择建议

### 🎯 主启动器 `./md2pdf`（推荐）
- ✅ **一键启动**: 自动检查环境和安装依赖
- ✅ **多模式**: 支持CLI、增强、基础三种模式
- ✅ **参数透传**: 完整支持所有转换器参数
- ✅ **系统管理**: 环境检查、状态显示、帮助信息

### 🔧 Claude CLI版本（日常使用）
- ✅ **简洁高效**: Claude风格的优雅CLI界面
- ✅ **快速上手**: 直观的交互和命令行参数
- ✅ **核心功能**: 包含多主题和批量转换
- ✅ **最佳实践**: 遵循Claude Code设计理念

### 📊 增强版本（高级功能）
- ✅ **功能最全**: 配置管理、自动打开等高级功能
- ✅ **可编程**: 支持API调用和自动化脚本
- ✅ **可定制**: 丰富的配置选项和扩展能力

### 📝 基础版本（学习参考）
- ✅ **最简单**: 无需配置，开箱即用
- ✅ **轻量级**: 功能精简，依赖最少
- ✅ **易理解**: 代码简洁，适合学习