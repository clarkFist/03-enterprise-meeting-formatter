"""
MD2PDF Enterprise - 高质量 Markdown 到 PDF 转换工具
====================================================

专业的 Markdown 文档转 PDF 工具，支持企业级样式和多主题。
"""

__version__ = "2.0.0"
__author__ = "Claude Code Skills"
__license__ = "MIT"

from .app import MarkdownToPDFApp, convert_file, convert_files, get_app

__all__ = [
    "MarkdownToPDFApp",
    "convert_file",
    "convert_files",
    "get_app",
    "__version__",
]
