#!/usr/bin/env python3
"""
自动补全工具 - 命令行交互增强
============================

提供主题选择等场景的自动补全功能
"""

import readline
import sys
from typing import List, Optional


class AutoCompleter:
    """自动补全器"""
    
    def __init__(self, options: List[str]):
        self.options = options
        self.matches = []
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """补全函数"""
        if state == 0:
            # 首次调用，计算匹配项
            self.matches = [
                option for option in self.options 
                if option.startswith(text.lower())
            ]
        
        try:
            return self.matches[state]
        except IndexError:
            return None


def setup_autocomplete(options: List[str]) -> None:
    """设置自动补全"""
    if 'libedit' in readline.__doc__:
        # macOS 使用 libedit
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        # Linux 使用 GNU readline
        readline.parse_and_bind("tab: complete")
    
    completer = AutoCompleter(options)
    readline.set_completer(completer.complete)


def input_with_completion(prompt: str, options: List[str], default: str = "") -> str:
    """带自动补全的输入"""
    # 设置自动补全
    setup_autocomplete(options)
    
    # 显示可用选项
    options_str = '/'.join(options)
    full_prompt = f"{prompt} [{options_str}]"
    if default:
        full_prompt += f" ({default})"
    full_prompt += ": "
    
    try:
        result = input(full_prompt).strip()
        return result or default
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    finally:
        # 清理补全设置
        readline.set_completer(None)


def theme_input_with_descriptions(theme_manager, default: str = "github") -> str:
    """带描述的主题选择输入"""
    themes = theme_manager.get_available_themes()
    theme_names = [theme.name for theme in themes]
    
    # 显示主题描述
    print("\n📎 Available themes:")
    for theme in themes:
        marker = "●" if theme.name == default else "○"
        print(f"  {marker} {theme.name}: {theme.description}")
    
    # 输入选择
    theme = input_with_completion("Theme", theme_names, default)
    
    # 验证输入
    if theme not in theme_names:
        print(f"⚠ Unknown theme '{theme}', using {default}")
        return default
    
    return theme


def theme_input(available_themes: List[str], default: str = "github") -> str:
    """主题选择输入（带自动补全）"""
    theme = input_with_completion("Theme", available_themes, default)
    
    # 验证输入
    if theme not in available_themes:
        print(f"⚠ Unknown theme '{theme}', using {default}")
        return default
    
    return theme