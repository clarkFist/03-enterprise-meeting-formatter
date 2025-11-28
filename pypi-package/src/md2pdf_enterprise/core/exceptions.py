#!/usr/bin/env python3
"""
异常定义模块
============

定义项目中所有自定义异常类型
"""


class MD2PDFError(Exception):
    """MD2PDF转换错误基类"""
    pass


class ConversionError(MD2PDFError):
    """转换错误基类"""
    pass


class BrowserNotFoundError(ConversionError):
    """浏览器未找到错误"""

    def __init__(self, message: str = "未找到Chromium/Chrome/Edge浏览器"):
        self.message = message
        super().__init__(self.message)


class BrowserLaunchError(ConversionError):
    """浏览器启动失败错误"""

    def __init__(self, message: str = "浏览器启动失败", original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class ThemeNotFoundError(MD2PDFError):
    """主题未找到错误"""

    def __init__(self, theme_name: str):
        self.theme_name = theme_name
        self.message = f"主题不存在: {theme_name}"
        super().__init__(self.message)


class ThemeLoadError(MD2PDFError):
    """主题加载失败错误"""

    def __init__(self, theme_name: str, reason: str = ""):
        self.theme_name = theme_name
        self.reason = reason
        self.message = f"主题加载失败: {theme_name}"
        if reason:
            self.message += f" - {reason}"
        super().__init__(self.message)


class MarkdownParseError(ConversionError):
    """Markdown解析错误"""

    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        self.message = f"Markdown解析失败: {file_path}"
        if reason:
            self.message += f" - {reason}"
        super().__init__(self.message)


class PDFGenerationError(ConversionError):
    """PDF生成错误"""

    def __init__(self, file_path: str, reason: str = ""):
        self.file_path = file_path
        self.reason = reason
        self.message = f"PDF生成失败: {file_path}"
        if reason:
            self.message += f" - {reason}"
        super().__init__(self.message)


class FileNotFoundError(MD2PDFError):
    """文件未找到错误"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.message = f"文件不存在: {file_path}"
        super().__init__(self.message)


class InvalidFileFormatError(MD2PDFError):
    """无效文件格式错误"""

    def __init__(self, file_path: str, expected_format: str = ".md"):
        self.file_path = file_path
        self.expected_format = expected_format
        self.message = f"无效文件格式: {file_path}，期望格式: {expected_format}"
        super().__init__(self.message)


class ConfigurationError(MD2PDFError):
    """配置错误"""

    def __init__(self, message: str):
        self.message = f"配置错误: {message}"
        super().__init__(self.message)


class DependencyError(MD2PDFError):
    """依赖项错误"""

    def __init__(self, dependency_name: str, reason: str = ""):
        self.dependency_name = dependency_name
        self.reason = reason
        self.message = f"依赖项错误: {dependency_name}"
        if reason:
            self.message += f" - {reason}"
        super().__init__(self.message)
