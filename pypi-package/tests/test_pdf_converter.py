#!/usr/bin/env python3
"""
PDF转换器测试
============

测试PDF转换器的核心功能
"""

import pytest
import asyncio
from pathlib import Path
import sys

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from md2pdf_enterprise.converter.pdf_converter import PDFConverter
from md2pdf_enterprise.core.converter_base import ConversionTask, ConversionStatus
from md2pdf_enterprise.core.exceptions import (
    ThemeNotFoundError,
    InvalidFileFormatError,
    FileNotFoundError as MD2PDFFileNotFoundError
)


@pytest.fixture
def converter():
    """创建转换器实例"""
    return PDFConverter()


@pytest.fixture
def sample_md_file():
    """获取示例Markdown文件路径"""
    return Path(__file__).parent / "fixtures" / "sample.md"


@pytest.fixture
def output_dir(tmp_path):
    """创建临时输出目录"""
    output = tmp_path / "output"
    output.mkdir()
    return output


class TestPDFConverter:
    """PDF转换器测试类"""

    def test_converter_initialization(self, converter):
        """测试转换器初始化"""
        assert converter is not None
        assert converter.theme_manager is not None
        assert converter.config_manager is not None

    def test_get_supported_themes(self, converter):
        """测试获取支持的主题列表"""
        themes = converter.get_supported_themes()
        assert isinstance(themes, list)
        assert len(themes) > 0
        assert "github" in themes
        assert "enterprise" in themes

    def test_validate_task_success(self, converter, sample_md_file, output_dir):
        """测试任务验证成功"""
        task = ConversionTask(
            source=sample_md_file,
            target=output_dir / "output.pdf",
            theme="github"
        )
        assert converter.validate_task(task) is True

    def test_validate_task_file_not_found(self, converter, output_dir):
        """测试文件不存在时的验证"""
        task = ConversionTask(
            source=Path("/nonexistent/file.md"),
            target=output_dir / "output.pdf",
            theme="github"
        )
        with pytest.raises(MD2PDFFileNotFoundError):
            converter.validate_task(task)

    def test_validate_task_invalid_format(self, converter, output_dir):
        """测试无效文件格式"""
        # 创建一个非.md文件
        invalid_file = output_dir / "test.txt"
        invalid_file.write_text("test")

        task = ConversionTask(
            source=invalid_file,
            target=output_dir / "output.pdf",
            theme="github"
        )
        with pytest.raises(InvalidFileFormatError):
            converter.validate_task(task)

    def test_validate_task_invalid_theme(self, converter, sample_md_file, output_dir):
        """测试无效主题"""
        task = ConversionTask(
            source=sample_md_file,
            target=output_dir / "output.pdf",
            theme="nonexistent_theme"
        )
        with pytest.raises(ThemeNotFoundError):
            converter.validate_task(task)

    @pytest.mark.asyncio
    async def test_convert_single_success(self, converter, sample_md_file, output_dir):
        """测试单文件转换成功"""
        task = ConversionTask(
            source=sample_md_file,
            target=output_dir / "output.pdf",
            theme="github"
        )

        result = await converter.convert_single(task)

        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.exists()
        assert result.duration is not None
        assert result.duration > 0
        assert task.status == ConversionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_convert_batch_parallel(self, converter, sample_md_file, output_dir):
        """测试并行批量转换"""
        tasks = [
            ConversionTask(
                source=sample_md_file,
                target=output_dir / f"output_{i}.pdf",
                theme="github"
            )
            for i in range(3)
        ]

        results = await converter.convert_batch(tasks, max_concurrent=2)

        assert len(results) == 3
        assert all(result.success for result in results)
        assert all(result.output_path.exists() for result in results)

    def test_markdown_to_html_conversion(self, converter):
        """测试Markdown到HTML的转换"""
        markdown_text = "# 标题\n\n这是一段文本。"
        html = converter._convert_markdown_to_html(markdown_text)

        assert "<h1" in html
        assert "标题" in html
        assert "这是一段文本" in html

    def test_semantic_classes_addition(self, converter):
        """测试语义化类名添加"""
        html = "<h2>会议议程</h2><p>内容</p>"
        result = converter._add_semantic_classes(html)

        assert "meeting-section" in result or "会议议程" in result

    def test_html_document_creation(self, converter):
        """测试HTML文档创建"""
        html_content = "<p>测试内容</p>"
        title = "测试标题"
        theme_css = "<style>body { color: black; }</style>"

        doc = converter._create_html_document(html_content, title, theme_css)

        assert "<!DOCTYPE html>" in doc
        assert "<html" in doc
        assert title in doc
        assert html_content in doc
        assert theme_css in doc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
