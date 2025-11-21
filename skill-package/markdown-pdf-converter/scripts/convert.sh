#!/bin/bash
# Markdown → PDF 转换脚本（使用内置转换器）
# 统一为内置实现，消除对外部 md2pdf 的依赖

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$SKILL_DIR/lib"

usage() {
    echo "用法: $0 <file.md> [theme]"
    echo "示例: $0 document.md enterprise"
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

INPUT_MD="$1"
THEME="${2:-enterprise}"

if [ ! -f "$INPUT_MD" ]; then
    echo "❌ 输入文件不存在: $INPUT_MD"
    exit 1
fi

# 依赖检查（markdown/pyppeteer/pygments）
missing_deps=()
python3 -c "import markdown" 2>/dev/null || missing_deps+=("markdown")
python3 -c "import pyppeteer" 2>/dev/null || missing_deps+=("pyppeteer")
python3 -c "import pygments" 2>/dev/null || missing_deps+=("pygments")

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "⏳ 缺少依赖: ${missing_deps[*]}"
    echo "ℹ️  正在安装所需依赖（需要网络）..."
    for dep in "${missing_deps[@]}"; do
        pip3 install "$dep" || {
            echo "❌ 依赖安装失败: $dep"
            echo "提示: 请手动执行: pip3 install markdown pyppeteer pygments"
            exit 1
        }
    done
fi

# 调用内置转换器（不自动打开，与历史行为保持一致）
MD_FILE="$INPUT_MD" THEME="$THEME" LIB_DIR="$LIB_DIR" python3 - <<'PY'
import os, sys
from pathlib import Path

lib_dir = Path(os.environ["LIB_DIR"])
sys.path.insert(0, str(lib_dir))

try:
    from pdf_converter import convert_markdown_to_pdf
except Exception as e:
    print(f"❌ 导入内置PDF转换模块失败: {e}")
    sys.exit(1)

md_file = os.environ["MD_FILE"]
theme = os.environ.get("THEME", "enterprise")

pdf_path = convert_markdown_to_pdf(md_file, theme=theme, auto_open=False)
if not pdf_path:
    print("❌ PDF转换失败")
    sys.exit(1)
print(f"✅ PDF转换完成: {pdf_path}")
PY
