# 故障排除

## 常见问题

### 安装问题（内置转换）

#### Q: pip install 失败

**错误信息:**
```
ERROR: Could not find a version that satisfies the requirement markdown/pyppeteer/pygments
```

**解决方案:**

1. 升级 pip:
```bash
pip install --upgrade pip
```

2. 检查 Python 版本:
```bash
python --version  # 需要 >= 3.7
```

3. 使用国内镜像:
```bash
pip install markdown pygments pyppeteer -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

#### Q: 权限错误

**错误信息:**
```
PermissionError: [Errno 13] Permission denied
```

**解决方案:**

使用 `--user` 标志:
```bash
pip install --user markdown pygments pyppeteer
```

或使用虚拟环境:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

pip install markdown pygments pyppeteer
```

---

### 运行时问题

#### Q: Chromium 下载慢或失败

**错误信息:**
```
Error: Failed to download Chromium
```

**原因:**
首次运行时 Pyppeteer 会自动下载 Chromium (~170MB)

**解决方案:**

1. 确保网络连接稳定
2. 等待下载完成（可能需要几分钟）
3. 手动下载 Chromium:

```bash
python -c "import pyppeteer; pyppeteer.chromium_downloader.download_chromium()"
```

---

#### Q: 中文显示异常

**问题:**
PDF 中中文显示为乱码或方框

**解决方案:**

1. 确保 Markdown 文件编码为 UTF-8:
```bash
file -I document.md
# 应显示: charset=utf-8
```

2. 转换文件编码:
```bash
iconv -f GB2312 -t UTF-8 document.md > document_utf8.md
```

---

#### Q: 转换失败: 文件不存在

**错误信息:**
```
✗ 转换失败: 源文件不存在
```

**解决方案:**

1. 检查文件路径:
```bash
ls -la document.md
```

2. 使用绝对路径:
```bash
./scripts/convert.sh /absolute/path/to/document.md enterprise
```

3. 检查当前目录:
```bash
pwd
./scripts/convert.sh ./document.md
```

---

### 输出质量问题

#### Q: PDF 表格被截断

**问题:**
长表格在 PDF 中被分页截断

**解决方案:**

Enterprise 主题已自动处理表格分页，如仍有问题:

1. 减小表格宽度
2. 使用简化的表格结构
3. 调整页面边距:

```python
app.update_config(
    margins={
        'top': '15mm',
        'bottom': '15mm',
        'left': '10mm',
        'right': '10mm'
    }
)
```

---

#### Q: 代码块语法高亮不显示

**问题:**
代码块没有语法高亮

**解决方案:**

确保代码块指定了语言:

❌ **错误写法:**
````
```
function hello() {
    console.log("Hello");
}
```
````

✅ **正确写法:**
````
```javascript
function hello() {
    console.log("Hello");
}
```
````

---

#### Q: 图片加载失败

**问题:**
PDF 中图片显示为空白

**解决方案:**

1. 使用绝对路径或 URL:
```markdown
<!-- 本地绝对路径 -->
![Logo](/absolute/path/to/logo.png)

<!-- URL -->
![Logo](https://example.com/logo.png)
```

2. 确保图片文件存在:
```bash
ls -la images/logo.png
```

3. 检查图片格式（支持 PNG, JPG, GIF, SVG）

---

### 性能问题

#### Q: 转换速度慢

**问题:**
大文件转换耗时过长

**预期速度:**
- 小文件 (< 10 页): 2-5 秒
- 中等文件 (10-50 页): 5-15 秒
- 大文件 (> 50 页): 15-60 秒

**优化建议:**

1. 批量转换时使用并行处理（未来版本支持）
2. 减少高分辨率图片
3. 简化复杂表格

---

### 环境问题

#### Q: 命令找不到

**错误信息:**
```
bash: ./scripts/convert.sh: No such file or directory
```

**解决方案:**

1. 确认当前目录正确:
```bash
pwd
ls -la scripts/convert.sh
```

2. 直接使用 Python API:
```bash
python - <<'PY'
from pathlib import Path
import sys
skill_dir = Path("skill-package/markdown-pdf-converter").resolve()
sys.path.insert(0, str(skill_dir / "lib"))
from pdf_converter import convert_markdown_to_pdf
print(convert_markdown_to_pdf("document.md", theme="enterprise", auto_open=False))
PY
```

---

### 兼容性问题

#### Q: macOS 权限提示

**问题:**
macOS 提示需要辅助功能权限

**解决方案:**

这是正常的，Chromium 需要某些权限。在系统设置中授予权限即可。

---

#### Q: Windows Defender 警告

**问题:**
Windows Defender 阻止 Chromium 下载

**解决方案:**

这是误报，Chromium 是安全的浏览器引擎。添加例外或临时关闭实时保护即可。

---

## 获取帮助

### 自助诊断

运行环境检查脚本:
```bash
./scripts/check-env.sh
```

### 查看详细错误

启用详细日志:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 报告问题

如以上方法无法解决，请提供以下信息报告问题:

1. 操作系统和版本
2. Python 版本
3. 依赖版本（markdown/pyppeteer/pygments）
4. 完整错误信息
5. 最小可复现示例

（如需要对内反馈，请附带日志输出与截图）

---

## 相关资源

- [使用指南](usage-guide.md)
- [主题对比](theme-comparison.md)
- [配置选项](../configs/conversion-config.md)
（无外部 md2pdf 依赖）
