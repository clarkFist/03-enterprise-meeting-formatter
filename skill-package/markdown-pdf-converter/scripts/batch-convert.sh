#!/bin/bash
# 批量转换脚本（使用内置转换）

set -e

THEME=${1:-github}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "批量转换当前目录所有 .md 文件 (主题: $THEME)"

# 若无文件则提示
shopt -s nullglob
files=( *.md )
if [ ${#files[@]} -eq 0 ]; then
    echo "未找到 .md 文件"
    exit 0
fi

success=0
total=${#files[@]}
for f in "${files[@]}"; do
    echo "→ 转换: $f"
    "$SCRIPT_DIR/convert.sh" "$f" "$THEME" && success=$((success+1))
done
echo "✓ $success/$total 转换完成"
