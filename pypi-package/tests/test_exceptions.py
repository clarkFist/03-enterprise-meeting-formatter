#!/usr/bin/env python3
"""
异常测试
========

测试自定义异常类
"""

import pytest
from pathlib import Path
import sys

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from md2pdf_enterprise.core.exceptions import (
    MD2PDFError,
    ConversionError,
    BrowserNotFoundError,
    BrowserLaunchError,
    ThemeNotFoundError,
    ThemeLoadError,
    MarkdownParseError,
    PDFGenerationError,
    FileNotFoundError,
    InvalidFileFormatError,
    ConfigurationError,
    DependencyError
)


class TestExceptions:
    """异常测试类"""

    def test_base_exception(self):
        """测试基础异常"""
        exc = MD2PDFError("测试错误")
        assert str(exc) == "测试错误"
        assert isinstance(exc, Exception)

    def test_conversion_error(self):
        """测试转换错误"""
        exc = ConversionError("转换失败")
        assert str(exc) == "转换失败"
        assert isinstance(exc, MD2PDFError)

    def test_browser_not_found_error(self):
        """测试浏览器未找到错误"""
        exc = BrowserNotFoundError()
        assert "浏览器" in str(exc)
        assert isinstance(exc, ConversionError)

        exc_custom = BrowserNotFoundError("自定义消息")
        assert str(exc_custom) == "自定义消息"

    def test_browser_launch_error(self):
        """测试浏览器启动错误"""
        exc = BrowserLaunchError()
        assert "启动" in str(exc)
        assert isinstance(exc, ConversionError)

        original = Exception("原始错误")
        exc_with_original = BrowserLaunchError("启动失败", original)
        assert exc_with_original.original_error == original

    def test_theme_not_found_error(self):
        """测试主题未找到错误"""
        exc = ThemeNotFoundError("my_theme")
        assert "my_theme" in str(exc)
        assert exc.theme_name == "my_theme"
        assert isinstance(exc, MD2PDFError)

    def test_theme_load_error(self):
        """测试主题加载错误"""
        exc = ThemeLoadError("my_theme", "文件损坏")
        assert "my_theme" in str(exc)
        assert "文件损坏" in str(exc)
        assert exc.theme_name == "my_theme"
        assert exc.reason == "文件损坏"

    def test_markdown_parse_error(self):
        """测试Markdown解析错误"""
        exc = MarkdownParseError("/path/to/file.md", "语法错误")
        assert "/path/to/file.md" in str(exc)
        assert "语法错误" in str(exc)
        assert exc.file_path == "/path/to/file.md"
        assert exc.reason == "语法错误"

    def test_pdf_generation_error(self):
        """测试PDF生成错误"""
        exc = PDFGenerationError("/path/to/output.pdf", "内存不足")
        assert "/path/to/output.pdf" in str(exc)
        assert "内存不足" in str(exc)
        assert exc.file_path == "/path/to/output.pdf"

    def test_file_not_found_error(self):
        """测试文件未找到错误"""
        exc = FileNotFoundError("/path/to/missing.md")
        assert "/path/to/missing.md" in str(exc)
        assert exc.file_path == "/path/to/missing.md"

    def test_invalid_file_format_error(self):
        """测试无效文件格式错误"""
        exc = InvalidFileFormatError("/path/to/file.txt", ".md")
        assert "/path/to/file.txt" in str(exc)
        assert ".md" in str(exc)
        assert exc.file_path == "/path/to/file.txt"
        assert exc.expected_format == ".md"

    def test_configuration_error(self):
        """测试配置错误"""
        exc = ConfigurationError("配置项缺失")
        assert "配置项缺失" in str(exc)
        assert isinstance(exc, MD2PDFError)

    def test_dependency_error(self):
        """测试依赖项错误"""
        exc = DependencyError("pyppeteer", "版本不兼容")
        assert "pyppeteer" in str(exc)
        assert "版本不兼容" in str(exc)
        assert exc.dependency_name == "pyppeteer"
        assert exc.reason == "版本不兼容"

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        # 所有自定义异常都应该继承自MD2PDFError
        assert issubclass(ConversionError, MD2PDFError)
        assert issubclass(BrowserNotFoundError, ConversionError)
        assert issubclass(ThemeNotFoundError, MD2PDFError)
        assert issubclass(ConfigurationError, MD2PDFError)

    def test_exception_catch_base(self):
        """测试通过基类捕获异常"""
        try:
            raise ThemeNotFoundError("test_theme")
        except MD2PDFError as e:
            assert isinstance(e, ThemeNotFoundError)
            assert "test_theme" in str(e)

    def test_exception_catch_specific(self):
        """测试捕获特定异常"""
        with pytest.raises(ThemeNotFoundError) as exc_info:
            raise ThemeNotFoundError("test_theme")

        assert exc_info.value.theme_name == "test_theme"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
