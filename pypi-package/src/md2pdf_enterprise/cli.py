#!/usr/bin/env python3
"""
MD2PDF Enterprise - 命令行接口
============================

提供简洁的 Claude-style CLI 交互
"""

import sys
import asyncio
import argparse
from pathlib import Path
from typing import Optional

from .app import MarkdownToPDFApp
from .utils import CLIFormatter


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='md2pdf',
        description='高质量 Markdown 到 PDF 转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  md2pdf document.md                      # 基础转换
  md2pdf document.md -t enterprise        # 使用企业主题
  md2pdf document.md -o output/doc.pdf    # 指定输出路径
  md2pdf --all -t github                  # 批量转换当前目录
  md2pdf --list-themes                    # 查看所有主题
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='输入的 Markdown 文件'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出 PDF 文件路径'
    )

    parser.add_argument(
        '-t', '--theme',
        default='github',
        help='PDF 主题 (默认: github)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='转换当前目录所有 .md 文件'
    )

    parser.add_argument(
        '--list-themes',
        action='store_true',
        help='列出所有可用主题'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )

    return parser


async def main_async(args: argparse.Namespace) -> int:
    """异步主函数"""
    formatter = CLIFormatter()
    app = MarkdownToPDFApp()

    # 列出主题
    if args.list_themes:
        themes = app.get_available_themes()
        print("可用主题:")
        for theme in themes:
            print(f"  • {theme}")
        return 0

    # 初始化应用
    if not app.initialize():
        env_check = app.check_environment()
        if not env_check['dependencies_ok']:
            missing = [dep.name for dep in env_check['missing_dependencies']]
            print(f"✗ 缺少依赖: {', '.join(missing)}")
            print("\n安装依赖:")
            print("  pip install -r requirements.txt")
            return 1
        print("✗ 初始化失败")
        return 1

    # 批量转换
    if args.all:
        files = app.scan_files()
        if not files:
            print("✗ 未找到 .md 文件")
            return 1

        print(f"找到 {len(files)} 个文件")

        results = await app.convert_batch(
            [str(f.path) for f in files],
            theme=args.theme
        )

        successful = sum(1 for r in results if r.success)
        print(f"\n✓ {successful}/{len(results)} 转换完成")

        if successful < len(results):
            print("\n失败的文件:")
            for result in results:
                if not result.success:
                    print(f"  ✗ {result.task.source.name}: {result.error_message}")
            return 1

        return 0

    # 单文件转换
    if args.input:
        input_path = Path(args.input)

        if not input_path.exists():
            print(f"✗ 文件不存在: {args.input}")
            return 1

        result = await app.convert_single(
            args.input,
            args.output,
            theme=args.theme
        )

        if result.success:
            size_kb = result.file_size // 1024 if result.file_size else 0
            duration = f"{result.duration:.1f}s" if result.duration else ""
            print(f"✓ {result.output_path.name} ({size_kb}KB) {duration}")
            return 0
        else:
            print(f"✗ 转换失败: {result.error_message}")
            return 1

    # 没有提供参数，显示帮助
    create_parser().print_help()
    return 0


def main():
    """CLI 主入口"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        exit_code = asyncio.run(main_async(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n✗ 已取消")
        sys.exit(130)
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
