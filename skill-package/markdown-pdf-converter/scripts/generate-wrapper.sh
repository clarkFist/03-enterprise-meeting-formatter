#!/bin/bash
# 会议纪要生成包装脚本
# 提供便捷的命令行接口

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 检查依赖...${NC}"

    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 未安装${NC}"
        exit 1
    fi

    # 检查PyYAML
    if ! python3 -c "import yaml" 2>/dev/null; then
        echo -e "${YELLOW}⏳ 安装 PyYAML...${NC}"
        pip3 install PyYAML
    fi

    # 检查Jinja2
    if ! python3 -c "import jinja2" 2>/dev/null; then
        echo -e "${YELLOW}⏳ 安装 Jinja2...${NC}"
        pip3 install Jinja2
    fi

    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
VCU项目会议纪要生成工具

用法:
  $0 [选项] <input.yaml>

选项:
  -h, --help              显示此帮助信息
  -o, --output <file>     指定输出文件名
  -t, --template <file>   指定模板文件
  -p, --pdf               生成后自动转换为PDF
  --example               使用示例配置生成

示例:
  # 使用示例配置生成
  $0 --example

  # 从YAML文件生成
  $0 my-meeting.yaml

  # 生成并转换为PDF
  $0 -p my-meeting.yaml

  # 指定输出文件名
  $0 -o custom-name.md my-meeting.yaml

模板文件:
  templates/vcu-meeting-template.j2

数据文件:
  data/attendees.yaml                # 参会人员数据库
  data/meeting-input-example.yaml    # 输入示例

EOF
}

# 主函数
main() {
    local input_file=""
    local output_file=""
    local template=""
    local generate_pdf=false
    local use_example=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -t|--template)
                template="$2"
                shift 2
                ;;
            -p|--pdf)
                generate_pdf=true
                shift
                ;;
            --example)
                use_example=true
                shift
                ;;
            -*)
                echo -e "${RED}未知选项: $1${NC}"
                show_help
                exit 1
                ;;
            *)
                input_file="$1"
                shift
                ;;
        esac
    done

    # 检查依赖
    check_dependencies
    echo

    # 使用示例配置
    if [ "$use_example" = true ]; then
        input_file="$SKILL_DIR/data/meeting-input-example.yaml"
        echo -e "${BLUE}📋 使用示例配置: $input_file${NC}"
    fi

    # 检查输入文件
    if [ -z "$input_file" ]; then
        echo -e "${RED}❌ 错误: 未指定输入文件${NC}"
        echo
        show_help
        exit 1
    fi

    if [ ! -f "$input_file" ]; then
        echo -e "${RED}❌ 错误: 输入文件不存在: $input_file${NC}"
        exit 1
    fi

    # 构建命令
    local cmd="python3 $SCRIPT_DIR/generate-meeting.py $input_file"

    if [ -n "$output_file" ]; then
        cmd="$cmd $output_file"
    fi

    if [ -n "$template" ]; then
        cmd="$cmd $template"
    fi

    # 执行生成
    echo -e "${BLUE}🚀 生成会议纪要...${NC}"
    echo

    local result
    result=$($cmd)
    echo "$result"

    # 提取生成的文件名
    local generated_file
    generated_file=$(echo "$result" | grep "会议纪要已生成:" | sed 's/.*: //')

    # 转换为PDF
    if [ "$generate_pdf" = true ] && [ -n "$generated_file" ]; then
        echo
        echo -e "${BLUE}📄 转换为PDF（内置）...${NC}"

        # 检查内置PDF转换依赖（markdown/pyppeteer/pygments）
        missing_deps=()
        python3 -c "import markdown" 2>/dev/null || missing_deps+=("markdown")
        python3 -c "import pyppeteer" 2>/dev/null || missing_deps+=("pyppeteer")
        python3 -c "import pygments" 2>/dev/null || missing_deps+=("pygments")

        if [ ${#missing_deps[@]} -gt 0 ]; then
            echo -e "${YELLOW}⏳ 缺少依赖: ${missing_deps[*]}${NC}"
            echo -e "${BLUE}ℹ️  正在安装所需依赖（需要网络）...${NC}"
            for dep in "${missing_deps[@]}"; do
                pip3 install "$dep" || {
                    echo -e "${RED}❌ 依赖安装失败: $dep${NC}"
                    echo -e "${YELLOW}提示: 请手动执行: pip3 install markdown pyppeteer pygments${NC}"
                    exit 1
                }
            done
        fi

        # 使用内置转换器（不自动打开，与原行为保持一致）
        LIB_DIR="$SKILL_DIR/lib"
        MD_FILE="$generated_file" THEME="enterprise" LIB_DIR="$LIB_DIR" python3 - <<'PY'
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
    fi

    echo
    echo -e "${GREEN}🎉 完成！${NC}"
}

main "$@"
