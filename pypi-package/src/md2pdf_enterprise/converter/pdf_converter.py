#!/usr/bin/env python3
"""
PDF转换器 - 具体实现
===================

基于Pyppeteer的高质量PDF转换实现
"""

import asyncio
import os
import shutil
import sys
import markdown
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pyppeteer import launch

from ..core.converter_base import ConverterBase, ConversionTask, ConversionResult, ConversionStatus
from ..core.theme_manager import ThemeManager
from ..core.config_manager import ConfigManager


class PDFConverter(ConverterBase):
    """PDF转换器实现"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self.theme_manager = ThemeManager()
        
    async def convert_single(self, task: ConversionTask) -> ConversionResult:
        """转换单个文件"""
        task.status = ConversionStatus.RUNNING
        task.start_time = datetime.now()
        
        try:
            # 验证任务
            if not self.validate_task(task):
                raise ValueError("任务验证失败")
            
            # 读取Markdown内容
            with open(task.source, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 转换为HTML
            html_content = self._convert_markdown_to_html(markdown_content)
            
            # 获取主题CSS
            theme_css = self.theme_manager.get_theme_css(task.theme)
            
            # 创建完整HTML
            full_html = self._create_html_document(html_content, task.source.stem, theme_css)
            
            # 转换为PDF
            await self._convert_html_to_pdf(full_html, task.target, task.options)
            
            task.status = ConversionStatus.COMPLETED
            task.end_time = datetime.now()
            
            # 计算文件大小
            file_size = task.target.stat().st_size if task.target.exists() else None
            duration = (task.end_time - task.start_time).total_seconds()
            
            return ConversionResult(
                task=task,
                success=True,
                output_path=task.target,
                duration=duration,
                file_size=file_size
            )
            
        except Exception as e:
            task.status = ConversionStatus.FAILED
            task.end_time = datetime.now()
            task.error = str(e)
            
            duration = (task.end_time - task.start_time).total_seconds() if task.start_time else None
            
            return ConversionResult(
                task=task,
                success=False,
                error_message=str(e),
                duration=duration
            )
    
    async def convert_batch(self, tasks: List[ConversionTask]) -> List[ConversionResult]:
        """批量转换文件"""
        results = []
        
        for task in tasks:
            result = await self.convert_single(task)
            results.append(result)
            
        return results
    
    def get_supported_themes(self) -> List[str]:
        """获取支持的主题列表"""
        themes = self.theme_manager.get_available_themes()
        return [theme.name for theme in themes]
    
    def validate_task(self, task: ConversionTask) -> bool:
        """验证转换任务"""
        # 检查源文件
        if not task.source.exists():
            return False
        
        if not task.source.suffix.lower() == '.md':
            return False
        
        # 检查主题
        if task.theme not in self.get_supported_themes():
            return False
        
        # 检查目标目录
        if not task.target.parent.exists():
            task.target.parent.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def _convert_markdown_to_html(self, markdown_content: str) -> str:
        """将Markdown转换为HTML"""
        md = markdown.Markdown(
            extensions=[
                'codehilite',
                'toc',
                'tables',
                'fenced_code',
                'nl2br',
                'sane_lists',
                'smarty',
                'attr_list',
                'def_list',
                'abbr',
                'footnotes',
                'admonition'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'codehilite',
                    'use_pygments': True,
                    'guess_lang': True,
                    'linenums': False
                },
                'toc': {
                    'permalink': True,
                    'permalink_class': 'headerlink',
                    'permalink_title': 'Permanent link'
                }
            }
        )
        
        html_content = md.convert(markdown_content)
        
        # 为企业文档添加语义化类名
        html_content = self._add_semantic_classes(html_content)
        
        return html_content
    
    def _add_semantic_classes(self, html_content: str) -> str:
        """为HTML内容添加语义化类名以优化分页"""
        import re
        
        # 识别会议相关章节
        meeting_patterns = [
            (r'<h2>([^<]*(?:会议|议程|讨论|决定|行动|任务|问题)[^<]*)</h2>', 
             r'<h2 class="meeting-section">\1</h2>'),
            (r'<h3>([^<]*(?:行动项目|任务分配|决策要点)[^<]*)</h3>', 
             r'<h3 class="action-items">\1</h3>'),
            (r'<h3>([^<]*(?:决定|决策|结论)[^<]*)</h3>', 
             r'<h3 class="decision-points">\1</h3>'),
        ]
        
        # 应用语义化类名
        for pattern, replacement in meeting_patterns:
            html_content = re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)
        
        # 为特定章节添加分页控制类
        # 直接替换h2标签的id属性，添加class属性以适配包含永久链接的HTML结构
        html_content = re.sub(
            r'<h2 id="1">',
            r'<h2 id="1" class="first-page-section">',
            html_content
        )
        
        html_content = re.sub(
            r'<h2 id="2">',
            r'<h2 id="2" class="second-page-section">',
            html_content
        )
        
        html_content = re.sub(
            r'<h2 id="3">',
            r'<h2 id="3" class="module-reports-section">',
            html_content
        )
        
        # 移除强制页面填充 - 让内容自然流动
        # 注释掉：避免不必要的页面留白，依赖CSS智能分页
        
        # 移除强制分页符插入 - 依赖CSS自动分页控制
        # 注释掉：避免双重分页控制导致的过度留白
        
        # 为列表组添加内容块类
        html_content = re.sub(
            r'(<ul>.*?</ul>)', 
            r'<div class="content-block">\1</div>', 
            html_content, 
            flags=re.DOTALL
        )
        
        html_content = re.sub(
            r'(<ol>.*?</ol>)', 
            r'<div class="content-block">\1</div>', 
            html_content, 
            flags=re.DOTALL
        )
        
        # 为表格添加内容块类
        html_content = re.sub(
            r'(<table>.*?</table>)', 
            r'<div class="content-block">\1</div>', 
            html_content, 
            flags=re.DOTALL
        )
        
        return html_content
    
    def _create_html_document(self, html_content: str, title: str, theme_css: str) -> str:
        """创建完整的HTML文档"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {theme_css}
</head>
<body>
    {html_content}
</body>
</html>"""
    
    async def _convert_html_to_pdf(self, html_content: str, output_path: Path, options: dict):
        """将HTML转换为PDF"""
        config = self.config_manager.get_config()
        
        pdf_options = {
            'format': config.format,
            'margin': config.margins,
            'printBackground': True,
            'displayHeaderFooter': False,
            'preferCSSPageSize': True,
            'scale': config.scale
        }
        
        # 合并用户选项
        if options:
            pdf_options.update(options)
        
        # Prefer using a locally installed Chromium/Chrome/Edge when available to avoid
        # pyppeteer trying to download its own Chromium (blocked in restricted networks).
        launch_kwargs = {
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
            ],
            # Avoid pyppeteer installing signal handlers that can conflict with asyncio
            # teardown on newer Python versions.
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False,
        }

        exec_path = self._detect_browser_executable()
        if exec_path:
            launch_kwargs['executablePath'] = exec_path

        browser = await launch(**launch_kwargs)
        
        try:
            page = await browser.newPage()
            await page.setViewport({
                'width': 1200,
                'height': 800,
                'deviceScaleFactor': 2
            })
            
            await page.setContent(html_content)
            # 等待所有图片加载完成
            try:
                await page.waitForSelector('img', {'timeout': 5000})
                # 等待所有图片加载
                await page.evaluate('''
                    () => {
                        return Promise.all(Array.from(document.images).map(img => {
                            if (img.complete) return Promise.resolve();
                            return new Promise(resolve => {
                                img.onload = resolve;
                                img.onerror = resolve;
                            });
                        }));
                    }
                ''')
            except Exception:
                pass  # 如果没有图片或加载失败，继续执行
            await asyncio.sleep(3)  # 额外等待时间确保外部图片加载
            
            await page.pdf({
                'path': str(output_path),
                **pdf_options
            })
            
        finally:
            await browser.close()

    def _detect_browser_executable(self) -> Optional[str]:
        """Best-effort detection of a local Chromium/Chrome/Edge executable.

        Returns an absolute path if found, otherwise None. This helps avoid
        pyppeteer attempting to download Chromium when network is restricted.
        """
        # Respect an explicit override if user sets it.
        override = os.environ.get('PUPPETEER_EXECUTABLE_PATH') or os.environ.get('PYPPETEER_EXECUTABLE_PATH')
        if override and Path(override).exists():
            return override

        candidates = []

        # macOS bundle locations
        candidates.extend([
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
            '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        ])

        # Common PATH program names on macOS/Linux
        for name in [
            'google-chrome', 'chrome', 'chromium', 'chromium-browser', 'microsoft-edge', 'edge'
        ]:
            path = shutil.which(name)
            if path:
                candidates.append(path)

        # Windows
        if sys.platform.startswith('win'):
            local_app = os.environ.get('LOCALAPPDATA')
            prog_files = [
                os.environ.get('PROGRAMFILES', r'C:\\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', r'C:\\Program Files (x86)'),
            ]
            if local_app:
                candidates.append(os.path.join(local_app, r'Google\Chrome\Application\chrome.exe'))
                candidates.append(os.path.join(local_app, r'Microsoft\Edge\Application\msedge.exe'))
            for base in prog_files:
                if base:
                    candidates.append(os.path.join(base, r'Google\Chrome\Application\chrome.exe'))
                    candidates.append(os.path.join(base, r'Chromium\Application\chrome.exe'))
                    candidates.append(os.path.join(base, r'Microsoft\Edge\Application\msedge.exe'))

        for p in candidates:
            try:
                if p and Path(p).exists():
                    return p
            except Exception:
                continue
        return None
