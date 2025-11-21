# 使用指南

## 安装

### 安装内置转换所需依赖

```bash
pip install markdown pygments pyppeteer
```

### 验证环境

```bash
./scripts/check-env.sh
```

---

## 基础用法

### 转换单个文件

```bash
./scripts/convert.sh document.md
```

生成 `document.pdf` 在同一目录下。

### 使用不同主题

```bash
# GitHub 主题 (默认)
./scripts/convert.sh document.md github

# Enterprise 主题
./scripts/convert.sh document.md enterprise
```

---

## 批量转换

### 转换当前目录所有 .md 文件

```bash
./scripts/batch-convert.sh
```

### 批量转换并指定主题

```bash
./scripts/batch-convert.sh enterprise
```

---

## Python API

### 基础使用（内置转换）

```python
from pathlib import Path
import sys

# 加入内置库
skill_dir = Path("skill-package/markdown-pdf-converter").resolve()
sys.path.insert(0, str(skill_dir / "lib"))
from pdf_converter import convert_markdown_to_pdf  # noqa

pdf_path = convert_markdown_to_pdf("document.md", theme="enterprise", auto_open=False)
print(pdf_path)
```

### 批量转换

```python
from pathlib import Path
import sys

skill_dir = Path("skill-package/markdown-pdf-converter").resolve()
sys.path.insert(0, str(skill_dir / "lib"))
from pdf_converter import convert_markdown_to_pdf  # noqa

md_files = list(Path(".").glob("*.md"))
ok = 0
for f in md_files:
    if convert_markdown_to_pdf(str(f), theme="github", auto_open=False):
        ok += 1
print(f"✓ {ok}/{len(md_files)} 转换完成")
```

> 说明：当前内置转换器支持 `theme`（github/enterprise）与 `auto_open`。页面格式/边距在样式中已优化固定，暂无 CLI 参数。

---

## 高级用法

### 环境检查

```bash
./scripts/check-env.sh
```

> OCR/生成纪要流程请使用 `./scripts/ocr-wrapper.sh` 与 `./scripts/generate-wrapper.sh`。

---

## 常见场景

### 场景 1: 技术文档

```bash
./scripts/convert.sh technical-guide.md github
```

适合开发文档、API 文档、技术教程。

### 场景 2: 会议纪要

```bash
./scripts/convert.sh meeting-notes.md enterprise
```

适合企业会议纪要、项目报告、商务文档。

---

## 输出示例

### 成功输出

```
✓ document.pdf (235KB) 2.3s
```

### 批量输出

```
找到 5 个文件

✓ 5/5 转换完成
```

### 失败输出

```
✗ 转换失败: 源文件不存在
```

---

## 下一步

- [主题对比](theme-comparison.md) - 了解各主题特点
- [配置选项](../configs/conversion-config.md) - 自定义转换参数
- [故障排除](troubleshooting.md) - 解决常见问题
