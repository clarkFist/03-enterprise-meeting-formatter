#!/usr/bin/env python3
"""
应用程序主接口 - 统一的外部API
=============================

提供简洁的外部接口，隐藏所有内部实现细节
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any

from .core import ConfigManager, ThemeManager
from .converter import ConverterFactory
from .utils import FileScanner, DependencyChecker, CLIFormatter
from .core.converter_base import ConversionTask, ConversionResult


class MarkdownToPDFApp:
    """Markdown转PDF应用程序主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_manager = ConfigManager(config_file)
        self.theme_manager = ThemeManager()
        self.file_scanner = FileScanner()
        self.dependency_checker = DependencyChecker()
        self.cli_formatter = CLIFormatter()
        self.converter = None
        
    def initialize(self) -> bool:
        """初始化应用程序"""
        # 检查依赖
        dep_results = self.dependency_checker.check_all_dependencies()
        if dep_results['missing']:
            return False
        
        # 创建转换器
        self.converter = ConverterFactory.create_converter(
            converter_type='pdf',
            config_manager=self.config_manager
        )
        
        return True
    
    def check_environment(self) -> Dict[str, Any]:
        """检查运行环境"""
        python_valid, python_version = self.dependency_checker.check_python_version()
        dep_results = self.dependency_checker.check_all_dependencies()
        env_info = self.dependency_checker.get_environment_info()
        
        return {
            'python_valid': python_valid,
            'python_version': python_version,
            'dependencies_ok': len(dep_results['missing']) == 0,
            'missing_dependencies': dep_results['missing'],
            'environment': env_info
        }
    
    def install_dependencies(self, verbose: bool = True) -> bool:
        """安装缺失的依赖"""
        success, message = self.dependency_checker.install_dependencies(
            requirements_file="requirements.txt",
            verbose=verbose
        )
        
        if verbose:
            if success:
                print(self.cli_formatter.success(message))
            else:
                print(self.cli_formatter.error(message))
        
        return success
    
    def scan_files(self, recursive: bool = False) -> List[Any]:
        """扫描Markdown文件"""
        return self.file_scanner.scan_markdown_files(recursive=recursive)
    
    def get_available_themes(self) -> List[str]:
        """获取可用主题"""
        if not self.converter:
            themes = self.theme_manager.get_available_themes()
            return [theme.name for theme in themes]
        return self.converter.get_supported_themes()
    
    def create_conversion_task(
        self, 
        source_file: str, 
        output_file: str = None,
        theme: str = "github",
        options: Dict[str, Any] = None
    ) -> ConversionTask:
        """创建转换任务"""
        source_path = Path(source_file)
        
        if output_file:
            target_path = Path(output_file)
        else:
            target_path = source_path.with_suffix('.pdf')
        
        return ConversionTask(
            source=source_path,
            target=target_path,
            theme=theme,
            options=options or {}
        )
    
    async def convert_single(
        self, 
        source_file: str,
        output_file: str = None, 
        theme: str = "github",
        options: Dict[str, Any] = None
    ) -> ConversionResult:
        """转换单个文件"""
        if not self.converter:
            raise RuntimeError("应用程序未初始化，请先调用 initialize()")
        
        task = self.create_conversion_task(source_file, output_file, theme, options)
        return await self.converter.convert_single(task)
    
    async def convert_batch(
        self, 
        source_files: List[str],
        theme: str = "github",
        options: Dict[str, Any] = None
    ) -> List[ConversionResult]:
        """批量转换文件"""
        if not self.converter:
            raise RuntimeError("应用程序未初始化，请先调用 initialize()")
        
        tasks = []
        for source_file in source_files:
            task = self.create_conversion_task(source_file, None, theme, options)
            tasks.append(task)
        
        return await self.converter.convert_batch(tasks)
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        config = self.config_manager.get_config()
        return {
            'theme': config.theme,
            'format': config.format,
            'scale': config.scale,
            'margins': config.margins,
            'auto_open': config.auto_open,
            'output_dir': config.output_dir,
            'batch_mode': config.batch_mode
        }
    
    def update_config(self, **kwargs) -> bool:
        """更新配置"""
        return self.config_manager.update_config(**kwargs)
    
    def generate_environment_report(self) -> str:
        """生成环境检查报告"""
        return self.dependency_checker.generate_report()


# 提供简化的函数式接口
_app_instance = None

def get_app(config_file: Optional[str] = None) -> MarkdownToPDFApp:
    """获取应用程序实例（单例模式）"""
    global _app_instance
    if _app_instance is None:
        _app_instance = MarkdownToPDFApp(config_file)
    return _app_instance

async def convert_file(
    source_file: str,
    output_file: str = None,
    theme: str = "github",
    options: Dict[str, Any] = None,
    auto_init: bool = True
) -> ConversionResult:
    """简化的文件转换函数"""
    app = get_app()
    
    if auto_init and not app.converter:
        if not app.initialize():
            env_check = app.check_environment()
            if not env_check['dependencies_ok']:
                raise RuntimeError("依赖检查失败，请先安装必要依赖")
    
    return await app.convert_single(source_file, output_file, theme, options)

async def convert_files(
    source_files: List[str],
    theme: str = "github", 
    options: Dict[str, Any] = None,
    auto_init: bool = True
) -> List[ConversionResult]:
    """简化的批量转换函数"""
    app = get_app()
    
    if auto_init and not app.converter:
        if not app.initialize():
            env_check = app.check_environment()
            if not env_check['dependencies_ok']:
                raise RuntimeError("依赖检查失败，请先安装必要依赖")
    
    return await app.convert_batch(source_files, theme, options)