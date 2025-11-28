#!/usr/bin/env python3
"""
主题管理器 - 统一主题接口
=========================

管理所有转换主题，提供统一访问接口
"""

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
from abc import ABC, abstractmethod

from .exceptions import ThemeNotFoundError, ThemeLoadError


@dataclass
class Theme:
    """主题数据结构"""
    name: str
    display_name: str
    description: str
    css_content: str
    

class ThemeProvider(ABC):
    """主题提供者抽象类"""
    
    @abstractmethod
    def get_theme_css(self, theme_name: str) -> str:
        """获取主题CSS"""
        pass
    
    @abstractmethod
    def get_available_themes(self) -> List[Theme]:
        """获取可用主题列表"""
        pass


class ThemeManager:
    """主题管理器 - 从外部CSS文件加载主题"""

    def __init__(self):
        self._themes: Dict[str, Theme] = {}
        self._providers: List[ThemeProvider] = []
        self._theme_dir = Path(__file__).parent.parent / "themes"
        self._initialize_builtin_themes()

    def _initialize_builtin_themes(self):
        """初始化内置主题 - 从外部CSS文件加载"""
        # GitHub主题
        github_theme = Theme(
            name="github",
            display_name="GitHub",
            description="Modern technical documentation style",
            css_content=self._load_css_from_file("github.css")
        )
        self._themes["github"] = github_theme

        # 企业主题
        enterprise_theme = Theme(
            name="enterprise",
            display_name="Enterprise",
            description="Professional business document style with corporate branding",
            css_content=self._load_css_from_file("enterprise.css")
        )
        self._themes["enterprise"] = enterprise_theme

    def _load_css_from_file(self, filename: str) -> str:
        """从文件加载CSS内容"""
        css_path = self._theme_dir / filename
        if not css_path.exists():
            raise ThemeLoadError(
                theme_name=filename.replace('.css', ''),
                reason=f"主题文件不存在: {css_path}"
            )

        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        except Exception as e:
            raise ThemeLoadError(
                theme_name=filename.replace('.css', ''),
                reason=f"读取主题文件失败: {str(e)}"
            )

        # 包装在<style>标签中
        return f"<style>\n{css_content}\n</style>"
        
    
    def get_theme(self, name: str) -> Theme:
        """获取主题"""
        if name not in self._themes:
            raise ThemeNotFoundError(name)
        return self._themes[name]
    
    def get_theme_css(self, name: str) -> str:
        """获取主题CSS"""
        return self.get_theme(name).css_content
    
    def get_available_themes(self) -> List[Theme]:
        """获取所有可用主题"""
        return list(self._themes.values())
    
    def register_provider(self, provider: ThemeProvider):
        """注册主题提供者"""
        self._providers.append(provider)

        # 加载提供者的主题
        for theme in provider.get_available_themes():
            self._themes[theme.name] = theme
    
