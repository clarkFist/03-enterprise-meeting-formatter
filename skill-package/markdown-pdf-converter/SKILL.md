---
name: markdown-pdf-converter
description: 企业级文档工具：会议纪要OCR智能生成 + Markdown到PDF高质量转换，支持图片识别参会人员、VCU项目会议纪要模板和多主题PDF输出
version: 2.5.0
category: document-tools
tags: [markdown, pdf, converter, meeting-minutes, documentation, theming, batch-processing, vcu-project, ocr, vision-api]
dependencies:
  external:
    - PyYAML>=6.0               # YAML配置解析
    - Jinja2>=3.0               # 模板引擎
    - anthropic>=0.40.0         # Claude Vision API
    - Pillow>=10.0.0            # 图片处理
    - markdown>=3.4.0           # Markdown 转 HTML（内置PDF转换所需）
    - pyppeteer>=1.0.2          # Chromium 引擎（内置PDF转换所需）
    - pygments>=2.15.0          # 代码高亮（内置PDF转换所需）
---

# Markdown PDF Converter & Meeting Minutes Generator

> 企业级文档工具：**会议纪要智能生成** + **Markdown到PDF高质量转换**

## 何时使用（触发条件）
- 当用户提供“参会人员图片 + 会议文本（文件或直接文本）”时，自动生成企业级会议纪要（YAML → Markdown → PDF）
- 当用户仅提供“参会人员图片”时，从图片解析出人员/会议信息，生成 YAML/Markdown，必要时生成 PDF
- 当用户提供“已有 Markdown 文档”时，将其转换为企业主题风格的 PDF 文档

## 输入 / 输出
- 输入
  - 图片：参会人员名单、会议截图（PNG/JPG/JPEG/GIF/WebP）
  - 文本：会议内容（TXT/Markdown/自由格式），或直接文本
  - 可选：已有 YAML 配置（按模板字段）
- 输出
  - YAML：会议配置（data/meeting-input-YYYYMMDD_HHMMSS.yaml）
  - Markdown：会议纪要（RB99125046安全运算与控制平台（VCU）项目例会会议纪要_YYYYMMDD.md）
  - PDF：企业主题 PDF（同名 .pdf）

## 快速概览

### 🚀 OCR智能生成流程（新功能）
图片上传 → Claude Vision识别 → 自动匹配数据库 → 生成配置 → 生成纪要 → 可选PDF

### 📋 传统会议纪要生成流程
编写YAML配置 → 自动填充模板 → 生成Markdown → 可选转换PDF

### 📄 PDF转换流程
Markdown文档 → 选择主题 → 渲染输出 → 企业级PDF

## 核心能力

### 🆕 OCR智能识别（v2.2.0新增）
- 🔍 **图片识别**: 使用Claude Vision API识别会议图片
- 👥 **参会人员提取**: 自动提取姓名、工号、角色信息
- 🎯 **智能匹配**: 自动匹配参会人员数据库（16人）
- 📊 **模块提取**: 可选提取会议进展、问题、计划
- ⚡ **一键生成**: 从图片直接生成PDF会议纪要
- 🔄 **增量更新**: 自动处理新参会人员

### 🆕 会议纪要生成
- ✨ **自动生成**: 基于YAML配置自动生成VCU项目会议纪要
- ✨ **模板引擎**: Jinja2模板支持，灵活可定制
- ✨ **人员管理**: 参会人员数据库，快速复用
- ✨ **智能命名**: 自动生成带日期的文件名
- ✨ **完整结构**: 包含参会人员、进展汇报、领导指示、任务跟踪、风险管理

### 文档转换
- ✅ 单文件转换
- ✅ 批量转换
- ✅ 自定义输出路径
- ✅ 自动依赖检查

### 主题支持
- 🎨 **GitHub 主题**: 现代技术文档风格
- 🏢 **Enterprise 主题**: 专业商务文档风格（推荐用于会议纪要）
- 📚 **Academic 主题**: 传统学术论文排版

### 质量保证
- 📄 基于 Chromium 渲染引擎
- 🎯 企业级排版质量
- 🔧 灵活的配置选项

## 快速开始

### 安装依赖

```bash
# PDF转换依赖（内置转换）
pip install markdown pygments pyppeteer

# 会议纪要生成依赖
pip install PyYAML Jinja2

# OCR智能识别依赖（新增）
pip install anthropic Pillow
```

### 环境配置

```bash
# 设置Claude API密钥（OCR功能必需）
export ANTHROPIC_API_KEY='your-api-key'

# 或添加到 ~/.zshrc 或 ~/.bashrc 永久生效
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> ~/.zshrc
source ~/.zshrc
```

### 🚀 OCR智能生成（推荐 - 最快捷的方式）

#### 方式一：一键生成PDF

```bash
cd skill-package/markdown-pdf-converter

# 从图片直接生成PDF会议纪要
./scripts/ocr-wrapper.sh meeting-photo.png --generate-pdf
```

#### 方式二：分步操作

```bash
# 1. 从图片提取信息，生成配置文件
./scripts/ocr-wrapper.sh meeting-photo.png

# 2. 查看生成的配置文件
# 输出：data/meeting-input-YYYYMMDD_HHMMSS.yaml

# 3. 根据需要编辑配置文件（可选）

# 4. 生成会议纪要Markdown
python scripts/generate-meeting.py data/meeting-input-*.yaml

# 5. 转换为PDF
./scripts/convert.sh RB99125046*.md
```

#### 方式三：使用Python脚本直接调用

```bash
# 基本用法
python scripts/ocr-meeting-extractor.py meeting-photo.png

# 一键生成PDF
python scripts/ocr-meeting-extractor.py meeting-photo.png --generate-pdf

# 生成PDF但不自动打开
python scripts/ocr-meeting-extractor.py meeting-photo.png --generate-pdf --no-open

# 指定输出配置文件路径
python scripts/ocr-meeting-extractor.py meeting-photo.png -o custom-config.yaml
```

**OCR功能特点**：
- ✅ 自动识别参会人员（姓名、工号、角色）
- ✅ 智能匹配现有16人数据库
- ✅ 自动提取会议时间、地点、主持人
- ✅ 可选提取模块进展、问题、计划
- ✅ 支持新参会人员自动添加
- ✅ 一键生成完整PDF会议纪要

### 🆕 传统会议纪要生成（手动配置YAML）

#### 方式一：使用示例配置快速体验

```bash
# 一键生成示例会议纪要
cd skill-package/markdown-pdf-converter
./scripts/generate-wrapper.sh --example

# 生成并自动转换为PDF
./scripts/generate-wrapper.sh --example -p
```

#### 方式二：自定义YAML配置

```bash
# 1. 复制并编辑配置模板
cp data/meeting-input-example.yaml my-meeting.yaml
# 编辑 my-meeting.yaml 填写实际会议信息

# 2. 生成会议纪要
./scripts/generate-wrapper.sh my-meeting.yaml

# 3. 生成并转换为PDF
./scripts/generate-wrapper.sh -p my-meeting.yaml
```

#### 方式三：直接使用Python脚本

```bash
# 使用示例配置
python scripts/generate-meeting.py data/meeting-input-example.yaml

# 使用自定义配置
python scripts/generate-meeting.py my-meeting.yaml output.md
```

### PDF转换（适用于已有Markdown文档）

```bash
# 转换单个文件
./scripts/convert.sh document.md

# 使用企业主题（推荐用于会议纪要）
./scripts/convert.sh meeting-notes.md enterprise

# 批量转换
./scripts/batch-convert.sh github
```

---

## 🆕 会议纪要生成详解

### YAML配置文件结构

会议纪要配置文件包含以下主要部分：

```yaml
# ============= 基本信息 =============
meeting_time: "2025-11-21 14:00-15:30"
meeting_duration: "90分钟"                    # 可选
meeting_location: "企业微信会议"
meeting_host: "傅李育"
meeting_nature: "定期项目例会"
recorder: "刘浩洋(63356)"
company_name: "CASCO SIGNAL"
meeting_type: "Regular"
priority: "High"
meeting_id: "VCU-MEET-20251121"            # 可选，否则自动生成

# ============= 参会人员 =============
attendees:
  hosts:      # 会议主持人
    - name: "傅李育"
      id: "61349"
      role: "项目经理"
      module: "项目整体协调"
      present: true  # 可选，默认为true
  managers:   # 管理人员
  engineers:  # 技术人员

# ============= 项目整体状态 =============
project_phase: "3月版VCU开发阶段 - 样机功能转安全功能"
project_overview:
  - "3月版VCU以样机为基础，将展示类通信/交互功能转为安全功能"
  - "评审方式改为会议集中评审，流程已申请简化"
key_milestones:                            # 可选
  - "2025年11月（本周）：完成300C发布"
critical_risks:                            # 关键路径风险
  - "VV测试人力缺口且已滞后"
  - "安全保证计划滞后"

# ============= 模块进展汇报 =============
modules:
  - section: "4.1"
    name: "项目整体规划"
    owner: "傅李育"
    status: "⚠️ 时间紧/风险高"
    priority: "🔴 高"                      # 可选
    completed:                            # 支持两种格式
      "系统需求文档完成初稿": "2025-11-21"  # 映射格式（带时间）
      # 或列表格式: ["工作项1", "工作项2"]
    progress:                             # 当前进展
      - "📝 以样机为基础将展示类通信/交互功能转为安全相关功能"
    plans: []                             # 后续计划
    issues:                               # 支持两种格式
      - description: "预算被否，环境资源受限"  # 详细格式（带影响/解决方案）
        impact: "影响测试和开发资源投入"
        solution: "补充环境/设备使用明细，重新提交预算申请"
        owner: "傅李育"
        deadline: "尽快"
      # 或简单列表: ["问题1", "问题2"]
    notes: []                             # 备注

# ============= 领导指示 =============
leadership_instructions:
  - section: "5.1"
    name: "包莉"
    instructions:
      "人力协调":                          # 分类指示（嵌套格式）
        - "针对安全/测试人力缺口既成事实，将向上协调安全、测试及院内领导增补人手"
      "文档评审":
        - "文档评审已向上申请，受CBI25项目影响改为线下评审"

# ============= 关键任务 =============
tasks:
  - id: "T001"
    content: "完成安全保证计划评审并定稿"
    owner: "张辉"
    deadline: "下周"
    status: "⏳ 进行中"
    priority: "🔴 高"

# ============= 决策事项（可选）=============
decisions:                                # 可选部分
  - id: "D001"
    content: "3月版VCU以样机为基础，将展示功能转安全功能"
    status: "✅ 已确认"
    owner: "傅李育"
    time: "已执行"
    scope: "项目整体方向"
    prerequisite: "-"

# ============= 风险识别与应对 =============
risks:
  - id: "R001"
    description: "VV测试计划无进度且人力不足，已形成滞后"
    level: "🔴 高"
    solution: "补充人力或外包方案，明确里程碑"
    owner: "朱程辉"

# ============= 会议结束信息 =============
meeting_end_time: "2025-11-21 15:30"
approval_info: "傅李育 - 审核时间：2025-11-21"
distribution_scope: "项目组全员 / 相关管理层"
```

### 参会人员数据库

`data/attendees.yaml` 包含VCU项目的常用参会人员信息：

- **会议主持人**: 项目经理
- **管理人员**: 项目管理团队
- **技术人员**: 硬件工程师、驱动工程师、软件工程师

可直接引用或自定义参会人员。

### 模板系统

**VCU项目模板**: `templates/vcu-meeting-template.j2`

特性：
- ✅ 完整的会议纪要结构
- ✅ 自动生成参会人员表格（支持主持人/管理人员/技术人员分类）
- ✅ 支持多模块进展汇报（已完成/当前工作/下周计划/问题与解决方案/备注）
- ✅ 灵活的数据格式支持（列表或映射格式）
- ✅ 领导指示记录（支持嵌套分类）
- ✅ 任务跟踪表格（带状态和优先级）
- ✅ 决策事项记录（可选）
- ✅ 风险识别与应对（等级化管理）
- ✅ 项目整体状态（阶段/概况/里程碑/关键路径风险）
- ✅ 徽章显示（公司、项目、会议类型、优先级、版本）
- ✅ 自动会议编号生成（VCU-MEET-YYYYMMDD）
- ✅ 动态章节编号（自动调整章节序号）

### 文件命名规则

自动生成的文件名格式：
```
RB99125046安全运算与控制平台（VCU）项目例会会议纪要_YYYYMMDD.md
```

例如：`RB99125046安全运算与控制平台（VCU）项目例会会议纪要_20251114.md`

### 完整工作流示例

```bash
# 1. 创建会议配置
cp data/meeting-input-example.yaml meeting-20251114.yaml

# 2. 编辑配置文件，填写实际会议信息
# 编辑 meeting-20251114.yaml

# 3. 生成Markdown会议纪要
./scripts/generate-wrapper.sh meeting-20251114.yaml

# 4. 转换为PDF（企业主题）
./scripts/convert.sh "RB99125046安全运算与控制平台（VCU）项目例会会议纪要_20251114.md" enterprise

# 或者一步完成：生成并转换
./scripts/generate-wrapper.sh -p meeting-20251114.yaml
```

---

## 详细文档

### 使用指南
详见: [docs/usage-guide.md](docs/usage-guide.md)

### 主题对比
详见: [docs/theme-comparison.md](docs/theme-comparison.md)

### 配置选项
详见: [configs/conversion-config.md](configs/conversion-config.md)

### 故障排除
详见: [docs/troubleshooting.md](docs/troubleshooting.md)

---

## 输出标准

### 成功转换

```
✓ document.pdf (235KB) 2.3s
```

### 批量转换

```
找到 5 个文件

✓ 5/5 转换完成
```

### 转换失败

```
✗ 转换失败: 文件不存在: nonexistent.md
```

---

## 适用场景

✅ **适用于**:
- **🆕 VCU项目会议纪要自动生成**
- **🆕 企业会议纪要标准化管理**
- 技术文档转 PDF
- 项目报告格式化
- 开发文档归档
- 学术论文排版

❌ **不适用于**:
- 复杂的表单处理
- 交互式 PDF 生成
- 图像批量处理

---

## 工具脚本

### 🆕 会议纪要生成脚本

```bash
# 快捷包装脚本（推荐）
./scripts/generate-wrapper.sh --example        # 使用示例配置
./scripts/generate-wrapper.sh -p input.yaml   # 生成并转换PDF
./scripts/generate-wrapper.sh -h              # 查看帮助

# Python脚本
python scripts/generate-meeting.py input.yaml [output.md] [template.j2]
```

### PDF转换脚本

```bash
./scripts/convert.sh file.md [theme]
```

### 批量转换

```bash
./scripts/batch-convert.sh [theme]
```

### 环境检查

```bash
./scripts/check-env.sh
```

详见: [scripts/README.md](scripts/README.md)

---

### 示例

#### 🆕 示例 1: VCU项目会议纪要生成

```bash
# 方式一：快速体验（使用增强版示例）
./scripts/generate-wrapper.sh --example

# 方式二：使用完整示例配置
python scripts/generate-meeting.py \
  data/meeting-input-enhanced-example.yaml

# 方式三：自定义配置
# 1. 复制并编辑增强版示例
cp data/meeting-input-enhanced-example.yaml my-meeting.yaml
# 编辑 my-meeting.yaml

# 2. 生成纪要并转换为PDF
./scripts/generate-wrapper.sh -p my-meeting.yaml
```

**示例展示的高级特性**：
- 项目整体状态（阶段、概况、关键路径风险）
- 模块进展（支持"既定滞后"标记）
- 详细问题跟踪（带影响/解决方案/负责人/期限）
- 领导指示（分类嵌套格式）
- 任务和风险管理（优先级和等级化）
- 自动章节编号（决策事项可选）

完整示例请查看：
- 配置文件: `data/meeting-input-enhanced-example.yaml`
- 输出示例: `examples/meeting-notes.md`

#### 示例 2: 技术文档转换

详见: [examples/technical-doc.md](examples/technical-doc.md)

#### 示例 3: 会议纪要转换

详见: [examples/meeting-notes.md](examples/meeting-notes.md)

---

## Python API

### 🆕 会议纪要生成 API

```python
from pathlib import Path
import sys

# 将技能目录加入 sys.path，然后导入 scripts.generate_meeting
skill_dir = Path("skill-package/markdown-pdf-converter").resolve()
sys.path.insert(0, str(skill_dir))
from scripts.generate_meeting import MeetingMinutesGenerator  # noqa

# 创建生成器并生成
generator = MeetingMinutesGenerator()
output_path = generator.generate("meeting-config.yaml", "output.md", "vcu-meeting-template.j2")

print(f"生成完成: {output_path}")
```

### PDF转换 API

```python
from pathlib import Path
import sys

# 将内置 lib 加入 sys.path，然后导入内置转换器
skill_dir = Path("skill-package/markdown-pdf-converter").resolve()
sys.path.insert(0, str(skill_dir / "lib"))
from pdf_converter import convert_markdown_to_pdf  # noqa

# 转换单个文件（不自动打开）
pdf_path = convert_markdown_to_pdf("document.md", theme="enterprise", auto_open=False)

if pdf_path:
    print(f"✓ {pdf_path}")
```

---

## 故障排除与FAQ

### 会议纪要生成问题

**Q: PyYAML 或 Jinja2 安装失败?**

A: 使用以下命令安装：
```bash
pip install PyYAML Jinja2
# 或使用包装脚本自动安装
./scripts/generate-wrapper.sh --example
```

**Q: 模板渲染失败?**

A: 检查YAML配置文件格式，确保缩进正确，字符串使用引号

**Q: 参会人员显示异常?**

A: 确保attendees.yaml文件存在且格式正确，或在配置中明确指定参会人员

### PDF转换问题

**Q: 内置PDF转换依赖安装失败?**

A: 确保 Python >= 3.7，先升级 pip：`pip install --upgrade pip`；然后分别安装：
```bash
pip install markdown pygments pyppeteer
```

**Q: Chromium 下载慢?**

A: 首次运行会自动下载 Chromium，需要稳定网络连接

**Q: 中文显示异常?**

A: 确保 Markdown 文件编码为 UTF-8

完整故障排除: [docs/troubleshooting.md](docs/troubleshooting.md)

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| **2.5.0** | **2025-11-21** | **🆕 模板系统增强版** |
|       |                | - 新增项目整体状态字段（project_phase, project_overview, critical_risks） |
|       |                | - 支持详细问题格式（description/impact/solution/owner/deadline） |
|       |                | - 领导指示支持嵌套分类格式 |
|       |                | - 模块支持"既定滞后"标记 |
|       |                | - 自动会议编号生成（meeting_id） |
|       |                | - 动态章节编号（自动调整章节序号） |
|       |                | - 增强版YAML示例（meeting-input-enhanced-example.yaml） |
| **2.4.0** | **2025-11-14** | **🆕 内置PDF转换；命令与文档统一为内置实现** |
| **2.1.0** | **2024-11-14** | **🆕 重大更新: 增加VCU项目会议纪要自动生成功能** |
|       |                | - 添加Jinja2模板引擎支持 |
|       |                | - 新增VCU项目会议纪要模板 |
|       |                | - 创建参会人员数据库管理 |
|       |                | - 支持YAML配置驱动生成 |
|       |                | - 添加便捷包装脚本 |
| 2.0.0 | 2024-10-21 | 基于 PyPI 包重构,符合官方 Skills 标准 |
| 1.0.0 | 2024-09-13 | 初始版本,本地代码实现 |

---

## 相关资源

- [官方 Skills 文档](https://docs.claude.com/en/docs/claude-code/skills) - Claude Code Skills
- [Jinja2 文档](https://jinja.palletsprojects.com/) - 模板引擎
- [PyYAML 文档](https://pyyaml.org/wiki/PyYAMLDocumentation) - YAML解析

---

**Version**: 2.5.0
**Category**: Document Tools
**Maintained by**: Claude Code Skills
**License**: MIT
