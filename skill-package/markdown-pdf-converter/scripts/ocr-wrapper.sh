#!/bin/bash
################################################################################
# VCU会议图片OCR提取器 - Shell包装脚本
#
# 用法:
#   ./ocr-wrapper.sh <image_path> [options]
#
# 示例:
#   ./ocr-wrapper.sh meeting.png
#   ./ocr-wrapper.sh meeting.png --generate-pdf
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Python脚本路径
PYTHON_SCRIPT="$SCRIPT_DIR/ocr-meeting-extractor.py"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python3
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装"
        echo "请先安装Python3: brew install python3"
        exit 1
    fi
    print_success "Python3已安装: $(python3 --version)"
}

# 检查依赖
check_dependencies() {
    print_info "检查Python依赖..."

    local missing_deps=()

    # 检查anthropic
    if ! python3 -c "import anthropic" 2>/dev/null; then
        missing_deps+=("anthropic")
    fi

    # 检查yaml
    if ! python3 -c "import yaml" 2>/dev/null; then
        missing_deps+=("PyYAML")
    fi

    # 检查Jinja2（生成Markdown必需）
    if ! python3 -c "import jinja2" 2>/dev/null; then
        missing_deps+=("Jinja2")
    fi

    # 检查PDF内置转换所需
    if ! python3 -c "import markdown" 2>/dev/null; then
        missing_deps+=("markdown")
    fi
    if ! python3 -c "import pygments" 2>/dev/null; then
        missing_deps+=("pygments")
    fi
    if ! python3 -c "import pyppeteer" 2>/dev/null; then
        missing_deps+=("pyppeteer")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_warning "缺少依赖: ${missing_deps[*]}"
        print_info "正在安装依赖..."

        for dep in "${missing_deps[@]}"; do
            pip3 install "$dep" || {
                print_error "安装 $dep 失败"
                exit 1
            }
        done

        print_success "依赖安装完成"
    else
        print_success "所有依赖已满足"
    fi
}

# 检查API密钥
check_api_key() {
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        print_error "未设置 ANTHROPIC_API_KEY 环境变量"
        echo ""
        echo "设置方法:"
        echo "  export ANTHROPIC_API_KEY='your-api-key'"
        echo ""
        echo "或将其添加到 ~/.zshrc 或 ~/.bashrc:"
        echo "  echo 'export ANTHROPIC_API_KEY=\"your-api-key\"' >> ~/.zshrc"
        echo "  source ~/.zshrc"
        exit 1
    fi
    print_success "API密钥已配置"
}

# 显示帮助信息
show_help() {
    cat << EOF
═══════════════════════════════════════════════════════════
  VCU会议图片OCR提取器 - 自动生成会议纪要
═══════════════════════════════════════════════════════════

用法:
  $0 <image_path> [options]

参数:
  image_path          参会人员图片路径（必需）

选项:
  -c, --content FILE  会议内容文本文件路径（双输入模式）
  -t, --text TEXT     会议内容直接文本（双输入模式）
  -o, --output FILE   指定输出配置文件路径
  --generate-pdf      自动生成PDF文件
  --no-open          不自动打开生成的文件
  -h, --help         显示此帮助信息

模式说明:
  单图片模式: 图片包含参会人员和会议内容
    $0 meeting-full.png --generate-pdf

  双输入模式: 图片(参会人员) + 文本(会议内容)
    $0 attendees.png --content meeting-notes.txt --generate-pdf
    $0 attendees.png --text "会议内容..." --generate-pdf

示例:
  # 双输入模式：图片 + 文本文件（推荐）
  $0 attendees.png --content meeting-notes.txt --generate-pdf

  # 双输入模式：图片 + 直接文本
  $0 attendees.png --text "会议时间: 2025-11-14..." --generate-pdf

  # 单图片模式：完整信息图片
  $0 meeting-photo.png --generate-pdf

  # 生成PDF但不自动打开
  $0 attendees.png --content notes.txt --generate-pdf --no-open

  # 仅生成配置文件
  $0 attendees.png --content notes.txt -o custom-config.yaml

环境要求:
  • Python 3.7+
  • ANTHROPIC_API_KEY 环境变量
  • 依赖库: anthropic, PyYAML, Pillow

工作流程:
  双输入模式:
    图片(参会人员) → OCR识别 → 匹配数据库
    文本(会议内容) → 结构化解析 → 提取模块/任务/风险
    ↓
    合并生成YAML配置 → Markdown纪要 → 企业级PDF

  单图片模式:
    图片(全部信息) → OCR识别 → YAML配置 → Markdown → PDF

═══════════════════════════════════════════════════════════
EOF
}

# 主函数
main() {
    # 检查参数
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi

    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  VCU会议图片OCR提取器"
    echo "═══════════════════════════════════════════════════════════"
    echo ""

    # 环境检查
    print_info "步骤 1/4: 环境检查"
    check_python
    check_dependencies
    check_api_key
    echo ""

    # 调用Python脚本
    print_info "步骤 2/4: 图片OCR识别"
    echo ""
    python3 "$PYTHON_SCRIPT" "$@"

    echo ""
    print_success "所有步骤完成"
    echo ""
}

# 执行主函数
main "$@"
