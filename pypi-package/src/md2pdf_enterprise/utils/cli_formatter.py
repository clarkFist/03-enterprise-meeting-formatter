#!/usr/bin/env python3
"""
CLI Formatter - Claude Code Compliant
====================================

Minimal, direct CLI output formatting
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class CLIFormatter:
    """Claude Code compliant CLI formatter"""
    
    @staticmethod
    def header(text: str, char: str = "=", width: int = 50) -> str:
        """Create header"""
        return f"\n{text}\n{char * width}"
    
    @staticmethod
    def success(text: str) -> str:
        """Success message"""
        return f"✓ {text}"
    
    @staticmethod
    def error(text: str) -> str:
        """Error message"""
        return f"✗ {text}"
    
    @staticmethod
    def warning(text: str) -> str:
        """Warning message"""
        return f"⚠ {text}"
    
    @staticmethod
    def info(text: str) -> str:
        """Info message"""
        return f"ℹ {text}"
    
    @staticmethod
    def progress(current: int, total: int, item: str = "", width: int = 20) -> str:
        """Progress indicator"""
        percentage = (current / total) * 100 if total > 0 else 0
        filled = int(width * current // total) if total > 0 else 0
        bar = '█' * filled + '░' * (width - filled)
        
        item_text = f" {item}" if item else ""
        return f"[{bar}] {percentage:.0f}% ({current}/{total}){item_text}"
    
    @staticmethod
    def table(
        headers: List[str], 
        rows: List[List[str]], 
        widths: Optional[List[int]] = None,
        indent: str = "  "
    ) -> str:
        """Table formatter"""
        if not headers or not rows:
            return ""
        
        if widths is None:
            widths = []
            for i, header in enumerate(headers):
                max_width = len(header)
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                widths.append(max_width + 2)
        
        lines = []
        
        # Header
        header_line = indent + "".join(
            str(header).ljust(width) for header, width in zip(headers, widths)
        )
        lines.append(header_line)
        
        # Separator
        separator = indent + "-" * sum(widths)
        lines.append(separator)
        
        # Data rows
        for row in rows:
            row_line = indent + "".join(
                str(row[i] if i < len(row) else "").ljust(width) 
                for i, width in enumerate(widths)
            )
            lines.append(row_line)
        
        return "\n".join(lines)
    
    @staticmethod
    def list_items(items: List[str], bullet: str = "•", indent: str = "  ") -> str:
        """List formatter"""
        return "\n".join(f"{indent}{bullet} {item}" for item in items)
    
    @staticmethod
    def key_value_pairs(
        pairs: Dict[str, Any], 
        indent: str = "  ",
        separator: str = ": "
    ) -> str:
        """Key-value formatter"""
        lines = []
        for key, value in pairs.items():
            lines.append(f"{indent}{key}{separator}{value}")
        return "\n".join(lines)
    
    @staticmethod
    def section(title: str, content: str, indent: str = "") -> str:
        """Section formatter"""
        return f"{indent}{title}\n{content}"
    
    @staticmethod
    def timestamp(dt: datetime = None, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Timestamp formatter"""
        if dt is None:
            dt = datetime.now()
        return dt.strftime(format)
    
    @staticmethod
    def file_size(size_bytes: int) -> str:
        """File size formatter"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}PB"
    
    @staticmethod
    def duration(seconds: float) -> str:
        """Duration formatter"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @classmethod
    def conversion_summary(
        cls, 
        total: int, 
        completed: int, 
        failed: int,
        duration: float = None
    ) -> str:
        """Conversion summary"""
        lines = []
        
        if completed > 0:
            lines.append(cls.success(f"{completed}/{total} completed"))
        
        if failed > 0:
            lines.append(cls.error(f"{failed}/{total} failed"))
        
        if duration is not None:
            lines.append(cls.info(f"Duration: {cls.duration(duration)}"))
        
        return "\n".join(lines)