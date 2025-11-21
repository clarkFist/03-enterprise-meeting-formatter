# 转换配置选项（内置）

内置转换器目前支持主题选择（github/enterprise）与是否自动打开（通过 Python API 控制）。页面格式与边距已在主题样式内优化固定。

## 主题设置

可选值:
- `github`: 现代技术文档风格
- `enterprise`: 商务会议纪要风格

示例:
```bash
./scripts/convert.sh document.md github
./scripts/convert.sh document.md enterprise
```

## 自动打开（Python API）

说明: CLI 默认不自动打开。若通过 Python API 调用，可设置 `auto_open=True`。

示例:
```python
from pathlib import Path
import sys
skill_dir = Path("skill-package/markdown-pdf-converter").resolve()
sys.path.insert(0, str(skill_dir / "lib"))
from pdf_converter import convert_markdown_to_pdf  # noqa

convert_markdown_to_pdf("document.md", theme="enterprise", auto_open=True)
```

---

## 批量转换

转换当前目录的所有 .md 文件:

```bash
./scripts/batch-convert.sh
./scripts/batch-convert.sh enterprise
```

> 说明：当前不提供全局配置文件，批量与单文件参数通过 CLI/调用参数传入。

---

## 配置选项详解

已见上文“主题设置 / 自动打开”。（页面格式、边距与缩放暂不支持 CLI 覆盖，已在主题样式优化）

---

## 常用配置组合

### 技术文档

```yaml
theme: github
format: A4
scale: 1.0
margins:
  top: 20mm
  bottom: 20mm
  left: 15mm
  right: 15mm
```

### 商务报告

```yaml
theme: enterprise
format: A4
scale: 0.9
margins:
  top: 25mm
  bottom: 25mm
  left: 20mm
  right: 20mm
```

### 演示文稿

```yaml
theme: github
format: Letter
scale: 1.2
margins:
  top: 15mm
  bottom: 15mm
  left: 15mm
  right: 15mm
```

---

## 下一步

- [使用指南](../docs/usage-guide.md) - 学习基础用法
- [主题对比](../docs/theme-comparison.md) - 了解各主题特点
- [故障排除](../docs/troubleshooting.md) - 解决常见问题
*** End Patch```. Please apply this patch.}니다 ***!
') to=functions.apply_patch ющих codeassistant.`|`
