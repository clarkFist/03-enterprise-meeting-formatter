#!/usr/bin/env python3
"""
转换器工厂 - 创建和管理转换器实例
===============================

提供统一的转换器创建接口，隐藏具体实现细节
"""

from typing import Dict, Type, Optional
from ..core.converter_base import ConverterBase
from ..core.config_manager import ConfigManager
from .pdf_converter import PDFConverter


class ConverterFactory:
    """转换器工厂类"""
    
    _converters: Dict[str, Type[ConverterBase]] = {
        'pdf': PDFConverter,
        'default': PDFConverter
    }
    
    @classmethod
    def create_converter(
        cls, 
        converter_type: str = 'default',
        config_manager: Optional[ConfigManager] = None
    ) -> ConverterBase:
        """创建转换器实例"""
        
        if converter_type not in cls._converters:
            raise ValueError(f"不支持的转换器类型: {converter_type}")
        
        converter_class = cls._converters[converter_type]
        
        # 根据转换器类型传递不同参数
        if converter_type in ['pdf', 'default']:
            return converter_class(config_manager=config_manager)
        else:
            return converter_class()
    
    @classmethod
    def register_converter(cls, name: str, converter_class: Type[ConverterBase]):
        """注册新的转换器类型"""
        cls._converters[name] = converter_class
    
    @classmethod
    def get_available_converters(cls) -> list:
        """获取可用的转换器类型"""
        return list(cls._converters.keys())