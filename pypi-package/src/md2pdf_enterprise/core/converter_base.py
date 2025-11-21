#!/usr/bin/env python3
"""
转换器基础类 - 抽象接口定义
===========================

定义统一的转换器接口，隐藏具体实现细节
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ConversionStatus(Enum):
    """转换状态枚举"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConversionTask:
    """转换任务数据结构"""
    source: Path
    target: Path
    theme: str = "github"
    options: Dict[str, Any] = None
    status: ConversionStatus = ConversionStatus.PENDING
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class ConversionResult:
    """转换结果数据结构"""
    task: ConversionTask
    success: bool
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None


class ConverterBase(ABC):
    """转换器基础抽象类"""
    
    @abstractmethod
    async def convert_single(self, task: ConversionTask) -> ConversionResult:
        """转换单个文件"""
        pass
    
    @abstractmethod
    async def convert_batch(self, tasks: List[ConversionTask]) -> List[ConversionResult]:
        """批量转换文件"""
        pass
    
    @abstractmethod
    def get_supported_themes(self) -> List[str]:
        """获取支持的主题列表"""
        pass
    
    @abstractmethod
    def validate_task(self, task: ConversionTask) -> bool:
        """验证转换任务"""
        pass