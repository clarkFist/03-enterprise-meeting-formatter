#!/bin/bash
# 环境检查脚本（内置转换版本）

echo "=== 内置PDF转换 环境检查 ==="
echo

# 检查 Python
echo "检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION"
else
    echo "✗ Python 3 未安装"
    exit 1
fi

# 检查 pip
echo
echo "检查 pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "✓ $PIP_VERSION"
else
    echo "✗ pip 未安装"
    exit 1
fi

# 检查 会议纪要生成依赖
echo
echo "检查 生成器依赖(PyYAML/Jinja2)..."
python3 -c "import yaml" 2>/dev/null && echo "✓ PyYAML 已安装" || echo "✗ 缺少 PyYAML"
python3 -c "import jinja2" 2>/dev/null && echo "✓ Jinja2 已安装" || echo "✗ 缺少 Jinja2"

# 检查 内置PDF转换依赖
echo
echo "检查 内置PDF转换依赖(markdown/pygments/pyppeteer)..."
python3 -c "import markdown" 2>/dev/null && echo "✓ markdown 已安装" || echo "✗ 缺少 markdown"
python3 -c "import pygments" 2>/dev/null && echo "✓ pygments 已安装" || echo "✗ 缺少 pygments"
python3 -c "import pyppeteer" 2>/dev/null && echo "✓ pyppeteer 已安装" || echo "✗ 缺少 pyppeteer"

echo
echo "=== 环境检查完成（若有 ✗ 请按提示安装） ==="
