#!/usr/bin/env python3
"""MD2PDF Enterprise Converter - 启动器"""

import sys
import asyncio
from pathlib import Path

# 添加pypi-package/src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "pypi-package" / "src"))

from md2pdf_enterprise.app import MarkdownToPDFApp
from md2pdf_enterprise.utils import interactive_theme_selection, fallback_theme_selection

ASCII_TITLE = """
 ███╗   ███╗██████╗ ██████╗ ██████╗ ███████╗
 ████╗ ████║██╔══██╗╚════██╗██╔══██╗██╔════╝
 ██╔████╔██║██║  ██║ █████╔╝██████╔╝█████╗  
 ██║╚██╔╝██║██║  ██║██╔═══╝ ██╔══██╗██╔══╝  
 ██║ ╚═╝ ██║██████╗███████╗██║  ██║██║     
 ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     
 Enterprise Meeting Formatter v2.0
"""

async def main():
    """主入口"""
    try:
        print(ASCII_TITLE)
        app = MarkdownToPDFApp()
        
        # 环境检查
        env_status = app.check_environment()
        if not env_status['dependencies_ok']:
            missing = [dep.name for dep in env_status['missing_dependencies']]
            print(f"✗ 缺少依赖: {', '.join(missing)}")
            
            if input("安装依赖? (y/N): ").strip().lower() == 'y':
                print("⏳ 安装中...")
                success = app.install_dependencies(verbose=False)
                print("✓ 安装完成" if success else "✗ 安装失败")
                if not success:
                    return
            else:
                return
        
        # 初始化
        if not app.initialize():
            print("✗ 初始化失败")
            return
        
        await run_conversion(app)
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)

async def run_conversion(app):
    """运行转换过程"""
    files = app.scan_files()
    
    if not files:
        print("✗ 未找到markdown文件")
        return
    
    # 显示文件列表
    print(f"\n找到 {len(files)} 个markdown文件:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.name} ({f.size_human})")
    
    # 选择文件
    choice = input("\n选择文件 (1,3,5 | 1-3 | all | q): ").strip().lower()
    
    if choice == 'q':
        return
    
    selected = parse_selection(choice, files)
    if not selected:
        print("✗ 无效选择")
        return
    
    # 主题选择
    try:
        theme = interactive_theme_selection(app.theme_manager, "github")
        if not theme:
            print("✗ 未选择主题")
            return
    except Exception:
        theme = fallback_theme_selection(app.theme_manager, "github")
    
    # 转换
    print(f"⏳ 转换 {len(selected)} 个文件...")
    
    if len(selected) == 1:
        result = await app.convert_single(selected[0], theme=theme)
        display_result(result)
    else:
        results = await app.convert_batch(selected, theme=theme)
        display_batch_results(results)

def parse_selection(choice: str, files) -> list:
    """解析用户选择"""
    if choice == 'all':
        return [str(f.path) for f in files]
    
    selected = set()
    for part in choice.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                selected.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                selected.add(int(part))
            except ValueError:
                continue
    
    valid_indices = [i for i in selected if 1 <= i <= len(files)]
    return [str(files[i-1].path) for i in valid_indices]

def display_result(result):
    """显示单个转换结果"""
    if result.success:
        size = f" ({result.file_size//1024}KB)" if result.file_size else ""
        duration = f" {result.duration:.1f}s" if result.duration else ""
        print(f"✓ {result.output_path.name}{size}{duration}")
    else:
        print(f"✗ {result.task.source.name}: {result.error_message}")

def display_batch_results(results):
    """显示批量转换结果"""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    total_time = sum(r.duration for r in results if r.duration)
    
    print(f"\n✓ {len(successful)}/{len(results)} 完成 ({total_time:.1f}s)")
    
    if failed:
        print("✗ 失败的文件:")
        for result in failed:
            print(f"  {result.task.source.name}: {result.error_message}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✗ 已取消")
        sys.exit(0)