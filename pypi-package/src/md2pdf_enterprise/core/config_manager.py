#!/usr/bin/env python3
"""
配置管理器 - 统一配置接口
=========================

提供统一的配置管理，支持多种配置源
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ConverterConfig:
    """转换器配置数据结构"""
    theme: str = "github"
    format: str = "A4"
    scale: float = 1.0
    margins: Dict[str, str] = None
    auto_open: bool = False
    output_dir: str = ""
    batch_mode: bool = False
    
    def __post_init__(self):
        if self.margins is None:
            self.margins = {
                "top": "20mm",
                "bottom": "20mm", 
                "left": "15mm",
                "right": "15mm"
            }


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file or ".md2pdf_config.json")
        self._config = self._load_config()
    
    def _load_config(self) -> ConverterConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return ConverterConfig(**config_data)
            except Exception:
                # 配置文件损坏，使用默认配置
                pass
        
        return ConverterConfig()
    
    def save_config(self) -> bool:
        """保存配置"""
        try:
            config_data = asdict(self._config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get_config(self) -> ConverterConfig:
        """获取配置"""
        return self._config
    
    def update_config(self, **kwargs) -> bool:
        """更新配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
            return self.save_config()
        except Exception:
            return False
    
    def reset_config(self) -> bool:
        """重置为默认配置"""
        self._config = ConverterConfig()
        return self.save_config()