# YAML Front Matter 使用指南

## 📖 什么是YAML Front Matter？

YAML Front Matter是在Markdown文档开头用三个短横线(`---`)包裹的配置区域，用于存储文档的元数据。

## ✨ 核心优势

| 优势 | 说明 |
|------|------|
| **明确性** | 无需猜测，直接指定文档类型 |
| **标准化** | 被Jekyll、Hugo、Obsidian等广泛使用 |
| **灵活性** | 可以存储任意配置和元数据 |
| **向后兼容** | 没有Front Matter时自动识别 |

---

## 🎯 支持的文档类型

### 1. 工作总结 (work-summary)

适用于年度/季度工作总结、述职报告等

```markdown
---
doc_type: work-summary
title: 2025年度工作总结
author: 刘浩洋
department: 研发部_成都公司
position: 软件开发工程师
year: 2025
theme: github
---

# 2025年度工作总结
...
```

**自动处理：**
- ✅ 修复中文章节锚点链接（#一版本发布 → #一、版本发布）
- ✅ 自动添加分页标记（目录和大章节前）
- ✅ 优化表格格式（简化数量列）

### 2. 会议纪要 (meeting-minutes)

适用于各类会议记录、讨论纪要等

```markdown
---
doc_type: meeting-minutes
title: VCU项目周会
date: 2025-11-30
time: "14:00-16:00"
attendees:
  - 张三
  - 李四
  - 王五
location: 会议室A
theme: enterprise
---

# VCU项目周会纪要
...
```

**自动处理：**
- ✅ 保持原有格式
- ✅ 适配会议纪要样式

### 3. 通用文档 (generic)

适用于技术文档、报告等其他类型

```markdown
---
doc_type: generic
title: 技术设计文档
theme: github
---

# 技术设计文档
...
```

---

## 🔧 配置项说明

### 必填项

| 配置项 | 说明 | 示例 |
|-------|------|------|
| `doc_type` | 文档类型 | `work-summary` / `meeting-minutes` / `generic` |

### 可选项

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `title` | 文档标题 | 文件名 |
| `author` | 作者 | - |
| `theme` | PDF主题 | `github` |
| `year` | 年份 | - |
| `department` | 部门 | - |

### 主题选择

| 主题名称 | 适用场景 | 风格特点 |
|---------|---------|---------|
| `github` | 技术文档、工作总结 | 现代化、清晰易读 |
| `enterprise` | 商务文档、会议纪要 | 专业、正式 |

---

## 💻 使用方法

### 方法1：使用增强转换器（推荐）

```bash
# 自动识别YAML Front Matter
python3 enhanced_converter.py document.md

# 指定主题（覆盖YAML配置）
python3 enhanced_converter.py -t github document.md

# 指定输出路径
python3 enhanced_converter.py -o output.pdf document.md

# 强制指定文档类型
python3 enhanced_converter.py --type work-summary document.md
```

### 方法2：直接使用CLI

```bash
# 原有方式仍然有效
python3 -m md2pdf_enterprise.cli document.md
```

---

## 🎨 完整示例

### 工作总结示例

```markdown
---
doc_type: work-summary
title: 2025年度工作总结
author: 刘浩洋
department: 研发部_成都公司
position: 软件开发工程师
year: 2025
theme: github
---

# 2025年度工作总结

**姓名：** 刘浩洋
**部门：** 研发部_成都公司
**岗位：** 软件开发工程师
**年度：** 2025

---

## 📊 年度成果概览

| 类别 | 数量 | 具体成果 |
|:---:|:---:|:---|
| 🚀 **[版本发布](#一、版本发布)** | 4 | CB125-KA-VCU200安全功能样机、VCU V1.1.5C |
| 🛠️ **[工具开发](#二、工具开发)** | 3 | VCU自动插桩工具、Gitlab CI/CD |

---

## 目录

1. [版本发布](#一、版本发布)
2. [工具开发](#二、工具开发)

---

## 一、版本发布

### 1.1 VCU V1.1.5C 版本发布
...
```

**处理结果：**
- ✓ 从YAML识别为工作总结文档
- ✓ 自动修复锚点链接
- ✓ 目录和大章节自动分页
- ✓ 表格数量列自动简化
- ✓ 使用GitHub主题生成PDF

---

## 🔍 识别优先级

转换器按以下优先级识别文档类型：

1. **命令行参数** (`--type`)
   ```bash
   python3 enhanced_converter.py --type work-summary doc.md
   ```

2. **YAML Front Matter** (`doc_type`)
   ```yaml
   ---
   doc_type: work-summary
   ---
   ```

3. **自动特征识别**
   - 检测关键词和结构特征
   - 计算置信度分数

4. **默认为通用文档** (`generic`)

---

## 📊 特征识别规则

### 工作总结特征

**必须包含（权重高）：**
- "年度成果概览"
- "姓名："

**建议包含（权重低）：**
- 中文章节编号（## 一、二、三...）
- "工作总结"关键词
- "版本发布"、"工具开发"等

### 会议纪要特征

**必须包含（权重高）：**
- "参会人员"
- "会议时间"

**建议包含（权重低）：**
- "会议纪要"
- "决策事项"
- "行动计划"

---

## 🚀 快速开始

### 1. 为现有文档添加Front Matter

在文档开头添加：

```yaml
---
doc_type: work-summary
theme: github
---
```

### 2. 运行转换

```bash
python3 enhanced_converter.py your-document.md
```

### 3. 查看输出

自动生成带时间戳的PDF：
```
your-document_20251130_122201.pdf
```

---

## 💡 最佳实践

### 1. 始终添加doc_type

即使可以自动识别，明确指定文档类型可以避免歧义：

```yaml
---
doc_type: work-summary  # 明确指定
---
```

### 2. 使用有意义的元数据

充分利用元数据功能：

```yaml
---
doc_type: work-summary
title: 2025年度工作总结
author: 刘浩洋
date: 2025-12-31
version: 1.0
confidential: false
---
```

### 3. 保持YAML格式正确

```yaml
# ✅ 正确
---
key: value
list:
  - item1
  - item2
---

# ❌ 错误（缺少空格）
---
key:value
---
```

---

## 🐛 故障排除

### YAML解析错误

**问题：** `⚠️  YAML解析错误`

**解决：**
- 检查冒号后是否有空格：`key: value`
- 检查缩进是否正确（使用空格，不要用Tab）
- 检查三个短横线是否完整

### 文档类型识别失败

**问题：** `ℹ️  使用通用处理流程`

**解决：**
- 添加YAML Front Matter明确指定类型
- 或使用`--type`参数强制指定

---

## 📚 参考资源

- [YAML官方文档](https://yaml.org/)
- [Jekyll Front Matter](https://jekyllrb.com/docs/front-matter/)
- [Hugo Front Matter](https://gohugo.io/content-management/front-matter/)

---

**最后更新：** 2025-11-30
**版本：** 1.0.0
