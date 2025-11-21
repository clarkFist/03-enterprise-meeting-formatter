#!/usr/bin/env python3
"""
Test script for internal PDF converter
"""

import sys
from pathlib import Path

# Add lib path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from pdf_converter import convert_markdown_to_pdf

def test_converter():
    """Test PDF conversion"""
    print("🧪 测试内部PDF转换模块...")
    print("-" * 60)

    # Find a test markdown file
    test_dir = Path(__file__).parent.parent
    md_files = list(test_dir.glob("*.md"))

    if not md_files:
        print("❌ 未找到测试用的Markdown文件")
        return False

    test_file = md_files[0]
    print(f"📄 测试文件: {test_file.name}")
    print(f"📍 路径: {test_file}")
    print()

    try:
        result = convert_markdown_to_pdf(
            str(test_file),
            theme='enterprise',
            auto_open=False  # Don't open PDF during test
        )

        if result and result.exists():
            file_size = result.stat().st_size
            print()
            print("=" * 60)
            print("✅ 测试通过！")
            print(f"📕 PDF文件: {result}")
            print(f"📊 文件大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print("=" * 60)
            return True
        else:
            print()
            print("❌ 测试失败：PDF文件未生成")
            return False

    except Exception as e:
        print()
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_converter()
    sys.exit(0 if success else 1)
