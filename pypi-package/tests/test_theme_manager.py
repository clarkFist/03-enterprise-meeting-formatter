#!/usr/bin/env python3
"""
主题管理器测试
==============

测试主题管理器的功能
"""

import pytest
from pathlib import Path
import sys

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from md2pdf_enterprise.core.theme_manager import ThemeManager, Theme
from md2pdf_enterprise.core.exceptions import ThemeNotFoundError, ThemeLoadError


@pytest.fixture
def theme_manager():
    """创建主题管理器实例"""
    return ThemeManager()


class TestThemeManager:
    """主题管理器测试类"""

    def test_theme_manager_initialization(self, theme_manager):
        """测试主题管理器初始化"""
        assert theme_manager is not None
        assert len(theme_manager._themes) >= 2  # github和enterprise

    def test_get_available_themes(self, theme_manager):
        """测试获取可用主题列表"""
        themes = theme_manager.get_available_themes()
        assert isinstance(themes, list)
        assert len(themes) >= 2

        # 检查必需的主题
        theme_names = [theme.name for theme in themes]
        assert "github" in theme_names
        assert "enterprise" in theme_names

    def test_get_theme_success(self, theme_manager):
        """测试成功获取主题"""
        github_theme = theme_manager.get_theme("github")
        assert isinstance(github_theme, Theme)
        assert github_theme.name == "github"
        assert github_theme.display_name == "GitHub"
        assert github_theme.css_content is not None
        assert len(github_theme.css_content) > 0

        enterprise_theme = theme_manager.get_theme("enterprise")
        assert isinstance(enterprise_theme, Theme)
        assert enterprise_theme.name == "enterprise"
        assert enterprise_theme.display_name == "Enterprise"
        assert enterprise_theme.css_content is not None
        assert len(enterprise_theme.css_content) > 0

    def test_get_theme_not_found(self, theme_manager):
        """测试获取不存在的主题"""
        with pytest.raises(ThemeNotFoundError) as exc_info:
            theme_manager.get_theme("nonexistent_theme")

        assert "nonexistent_theme" in str(exc_info.value)

    def test_get_theme_css(self, theme_manager):
        """测试获取主题CSS"""
        github_css = theme_manager.get_theme_css("github")
        assert isinstance(github_css, str)
        assert "<style>" in github_css
        assert "</style>" in github_css
        assert len(github_css) > 100  # CSS应该足够长

        enterprise_css = theme_manager.get_theme_css("enterprise")
        assert isinstance(enterprise_css, str)
        assert "<style>" in enterprise_css
        assert "</style>" in enterprise_css
        assert len(enterprise_css) > 100

    def test_css_files_exist(self, theme_manager):
        """测试CSS文件是否存在"""
        theme_dir = theme_manager._theme_dir
        assert theme_dir.exists()
        assert (theme_dir / "github.css").exists()
        assert (theme_dir / "enterprise.css").exists()

    def test_css_content_validity(self, theme_manager):
        """测试CSS内容的有效性"""
        github_css = theme_manager.get_theme_css("github")
        # 检查基本CSS结构
        assert "body" in github_css
        assert "font-family" in github_css
        assert "@page" in github_css or "@media print" in github_css

        enterprise_css = theme_manager.get_theme_css("enterprise")
        assert "body" in enterprise_css
        assert "font-family" in enterprise_css
        assert "@page" in enterprise_css or "@media print" in enterprise_css

    def test_theme_css_differences(self, theme_manager):
        """测试不同主题的CSS确实不同"""
        github_css = theme_manager.get_theme_css("github")
        enterprise_css = theme_manager.get_theme_css("enterprise")

        # CSS内容应该不同
        assert github_css != enterprise_css

        # 但都应该包含基本结构
        for css in [github_css, enterprise_css]:
            assert "body" in css
            assert "h1" in css or "h2" in css

    def test_load_css_from_file_success(self, theme_manager):
        """测试成功从文件加载CSS"""
        css_content = theme_manager._load_css_from_file("github.css")
        assert isinstance(css_content, str)
        assert css_content.startswith("<style>")
        assert css_content.endswith("</style>")
        assert len(css_content) > 100

    def test_load_css_from_file_not_found(self, theme_manager):
        """测试加载不存在的CSS文件"""
        with pytest.raises(ThemeLoadError) as exc_info:
            theme_manager._load_css_from_file("nonexistent.css")

        assert "nonexistent" in str(exc_info.value)

    def test_theme_structure(self, theme_manager):
        """测试主题数据结构"""
        theme = theme_manager.get_theme("github")

        # 检查Theme数据类的结构
        assert hasattr(theme, 'name')
        assert hasattr(theme, 'display_name')
        assert hasattr(theme, 'description')
        assert hasattr(theme, 'css_content')

        assert theme.name == "github"
        assert isinstance(theme.display_name, str)
        assert isinstance(theme.description, str)
        assert isinstance(theme.css_content, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])