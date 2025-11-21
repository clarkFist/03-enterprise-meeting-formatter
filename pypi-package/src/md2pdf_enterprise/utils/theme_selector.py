#!/usr/bin/env python3
"""
交互式主题选择器
================

提供上下键选择主题的交互界面
"""

import sys
import tty
import termios
from typing import List, Optional


class ThemeSelector:
    """交互式主题选择器"""
    
    def __init__(self, themes, default_theme: str = "github"):
        self.themes = themes
        self.theme_names = [theme.name for theme in themes]
        self.current_index = 0
        
        # 设置默认选中项
        if default_theme in self.theme_names:
            self.current_index = self.theme_names.index(default_theme)
    
    def display_themes(self):
        """显示主题列表"""
        print("\n📎 Available themes:")
        for i, theme in enumerate(self.themes):
            if i == self.current_index:
                marker = "●"  # 选中状态
                style = "\033[1;34m"  # 蓝色高亮
                reset = "\033[0m"
            else:
                marker = "○"  # 未选中状态
                style = ""
                reset = ""
            
            print(f"  {style}{marker} {theme.name}: {theme.description}{reset}")
    
    def get_char(self):
        """获取单个字符输入"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC序列
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def select_theme(self) -> str:
        """交互式选择主题"""
        try:
            # 隐藏光标
            print("\033[?25l", end="")
            
            while True:
                # 清屏并显示主题
                print("\033[2J\033[H", end="")  # 清屏并移动到开头
                self.display_themes()
                print(f"\n↑/↓: Navigate  Enter: Select  q: Quit")
                print(f"Selected: {self.themes[self.current_index].name}")
                
                # 获取用户输入
                key = self.get_char()
                
                if key == '\x1b[A':  # 上箭头
                    self.current_index = (self.current_index - 1) % len(self.themes)
                elif key == '\x1b[B':  # 下箭头
                    self.current_index = (self.current_index + 1) % len(self.themes)
                elif key == '\r' or key == '\n':  # 回车
                    break
                elif key == 'q' or key == 'Q':  # 退出
                    return None
                elif key == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
            
            return self.themes[self.current_index].name
            
        except KeyboardInterrupt:
            return None
        finally:
            # 显示光标
            print("\033[?25h", end="")


def is_interactive_terminal() -> bool:
    """检查是否为交互式终端"""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:
        return False


def interactive_theme_selection(theme_manager, default: str = "github") -> Optional[str]:
    """交互式主题选择"""
    # 检查是否支持交互式终端
    if not is_interactive_terminal():
        raise Exception("Non-interactive terminal detected")
    
    try:
        themes = theme_manager.get_available_themes()
        selector = ThemeSelector(themes, default)
        
        selected = selector.select_theme()
        
        # 清屏
        print("\033[2J\033[H", end="")
        
        if selected:
            selected_theme = next(t for t in themes if t.name == selected)
            print(f"✓ Selected theme: {selected_theme.name}")
            return selected
        else:
            print("✗ Theme selection cancelled")
            return None
            
    except Exception as e:
        # 对于非交互终端，直接抛出异常让调用者处理
        raise e
    
    
def fallback_theme_selection(theme_manager, default: str = "github") -> str:
    """备用的简单主题选择（用于不支持交互的终端）"""
    themes = theme_manager.get_available_themes()
    
    print("\n📎 Available themes:")
    for i, theme in enumerate(themes, 1):
        marker = "●" if theme.name == default else "○"
        print(f"  {i}. {marker} {theme.name}: {theme.description}")
    
    try:
        choice = input(f"\nSelect theme (1-{len(themes)}) or press Enter for {default}: ").strip()
        
        if not choice:
            return default
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(themes):
                return themes[index].name
        except ValueError:
            pass
        
        print(f"✗ Invalid choice, using {default}")
        return default
        
    except (KeyboardInterrupt, EOFError):
        print(f"\n✗ Cancelled, using {default}")
        return default