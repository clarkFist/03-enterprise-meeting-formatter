#!/usr/bin/env python3
"""
文件扫描器 - 智能文件发现和管理
=============================

提供Markdown文件的智能扫描和管理功能
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import fnmatch


class FileInfo:
    """文件信息数据结构"""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.stem = path.stem
        self.suffix = path.suffix
        self._stat = path.stat()
        
    @property
    def size(self) -> int:
        """文件大小（字节）"""
        return self._stat.st_size
    
    @property
    def size_human(self) -> str:
        """人类可读的文件大小"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    @property
    def modified_time(self) -> datetime:
        """修改时间"""
        return datetime.fromtimestamp(self._stat.st_mtime)
    
    @property
    def modified_time_human(self) -> str:
        """人类可读的修改时间"""
        return self.modified_time.strftime("%m-%d %H:%M")


class FileScanner:
    """文件扫描器"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
    
    def scan_markdown_files(
        self, 
        patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        recursive: bool = False
    ) -> List[FileInfo]:
        """扫描Markdown文件"""
        
        if patterns is None:
            patterns = ['*.md']
        
        if exclude_patterns is None:
            exclude_patterns = ['README.md']
        
        found_files = []
        
        # 根据是否递归选择扫描方式
        if recursive:
            search_pattern = "**/*.md"
            matched_paths = self.base_dir.glob(search_pattern)
        else:
            matched_paths = []
            for pattern in patterns:
                matched_paths.extend(self.base_dir.glob(pattern))
        
        for path in matched_paths:
            if not path.is_file():
                continue
                
            # 检查排除模式
            excluded = False
            for exclude_pattern in exclude_patterns:
                if fnmatch.fnmatch(path.name, exclude_pattern):
                    excluded = True
                    break
            
            if not excluded:
                found_files.append(FileInfo(path))
        
        # 按修改时间排序（最新的在前）
        found_files.sort(key=lambda f: f.modified_time, reverse=True)
        
        return found_files
    
    def scan_output_files(self, source_files: List[FileInfo]) -> Dict[str, List[Path]]:
        """扫描输出文件（PDF等）"""
        output_files = {
            'pdf': [],
            'other': []
        }
        
        for source_file in source_files:
            # 查找对应的PDF文件
            pdf_path = source_file.path.with_suffix('.pdf')
            if pdf_path.exists():
                output_files['pdf'].append(pdf_path)
        
        return output_files
    
    def get_file_stats(self, files: List[FileInfo]) -> Dict[str, Any]:
        """获取文件统计信息"""
        if not files:
            return {
                'count': 0,
                'total_size': 0,
                'total_size_human': '0B',
                'latest_modified': None
            }
        
        total_size = sum(f.size for f in files)
        latest_modified = max(f.modified_time for f in files)
        
        # 计算人类可读的总大小
        size = total_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                total_size_human = f"{size:.1f}{unit}"
                break
            size /= 1024
        else:
            total_size_human = f"{size:.1f}TB"
        
        return {
            'count': len(files),
            'total_size': total_size,
            'total_size_human': total_size_human,
            'latest_modified': latest_modified
        }