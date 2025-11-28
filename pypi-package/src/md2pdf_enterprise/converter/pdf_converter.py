#!/usr/bin/env python3
"""
PDF转换器 - 具体实现
===================

基于Pyppeteer的高质量PDF转换实现
"""

import asyncio
import os
import re
import shutil
import sys
import markdown
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pyppeteer import launch
from bs4 import BeautifulSoup

from ..core.converter_base import ConverterBase, ConversionTask, ConversionResult, ConversionStatus
from ..core.theme_manager import ThemeManager
from ..core.config_manager import ConfigManager
from ..core.exceptions import (
    BrowserNotFoundError,
    BrowserLaunchError,
    ThemeNotFoundError,
    MarkdownParseError,
    PDFGenerationError,
    InvalidFileFormatError,
    ConfigurationError,
    FileNotFoundError as MD2PDFFileNotFoundError
)


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
    
    async def convert_batch(self, tasks: List[ConversionTask], max_concurrent: int = 3) -> List[ConversionResult]:
        """批量转换文件 - 并行执行以提升性能

        Args:
            tasks: 转换任务列表
            max_concurrent: 最大并发数，默认3（避免资源过度消耗）

        Returns:
            转换结果列表
        """
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def convert_with_semaphore(task: ConversionTask) -> ConversionResult:
            """带信号量控制的转换"""
            async with semaphore:
                return await self.convert_single(task)

        # 并行执行所有转换任务
        results = await asyncio.gather(
            *[convert_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )

        # 处理异常情况
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 如果发生异常，创建失败结果
                task = tasks[i]
                task.status = ConversionStatus.FAILED
                task.error = str(result)
                processed_results.append(ConversionResult(
                    task=task,
                    success=False,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results
    
    def get_supported_themes(self) -> List[str]:
        """获取支持的主题列表"""
        themes = self.theme_manager.get_available_themes()
        return [theme.name for theme in themes]
    
    def validate_task(self, task: ConversionTask) -> bool:
        """验证转换任务"""
        # 检查源文件
        if not task.source.exists():
            raise MD2PDFFileNotFoundError(str(task.source))

        if not task.source.suffix.lower() == '.md':
            raise InvalidFileFormatError(str(task.source), ".md")

        # 检查主题
        if task.theme not in self.get_supported_themes():
            raise ThemeNotFoundError(task.theme)

        # 检查目标目录
        try:
            if not task.target.parent.exists():
                task.target.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigurationError(f"无法创建输出目录 {task.target.parent}: {str(e)}")

        return True

    def _custom_slugify(self, value: str, separator: str = '-') -> str:
        """自定义slug生成函数，支持中文和数字混合的锚点ID

        将标题转换为URL友好的锚点ID，保留中文字符和数字。
        例如: "4.1 商务管理" -> "41-商务管理"

        Args:
            value: 原始标题文本
            separator: 分隔符，默认为'-'

        Returns:
            转换后的slug字符串
        """
        # 移除前后空白
        value = value.strip()

        # 处理数字+点号格式（如"4.1"）
        # 将"4.1 商务管理"转换为"41-商务管理"
        value = re.sub(r'(\d+)\.(\d+)\s+', r'\1\2' + separator, value)

        # 如果没有匹配到上述模式，处理其他格式
        # 移除非中文、非数字、非字母的字符（保留连字符）
        value = re.sub(r'[^\w\u4e00-\u9fff\-]+', separator, value)

        # 移除多余的分隔符
        value = re.sub(r'-+', separator, value)

        # 移除首尾的分隔符
        value = value.strip(separator)

        return value.lower() if value.isascii() else value

    def _fix_anchor_links(self, html_content: str) -> str:
        """修复HTML中的锚点链接，确保链接目标ID存在

        扫描所有<a href="#...">链接，确保对应的id存在。
        如果不存在，尝试从标题文本生成匹配的ID。

        Args:
            html_content: 原始HTML内容

        Returns:
            修复后的HTML内容
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 收集所有已存在的ID
        existing_ids = {elem.get('id') for elem in soup.find_all(id=True)}

        # 收集所有锚点链接
        anchor_links = {}
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.startswith('#'):
                anchor_id = href[1:]  # 移除#
                anchor_links[anchor_id] = link

        # 修复不存在的锚点ID
        for anchor_id, link in anchor_links.items():
            if anchor_id not in existing_ids:
                # 尝试查找匹配的标题
                target_heading = self._find_matching_heading(soup, anchor_id)
                if target_heading:
                    # 为标题添加ID
                    target_heading['id'] = anchor_id
                    existing_ids.add(anchor_id)

        return str(soup)

    def _find_matching_heading(self, soup: BeautifulSoup, anchor_id: str) -> Optional[any]:
        """查找与锚点ID匹配的标题元素

        尝试根据锚点ID查找对应的标题。
        例如: "41-商务管理" 应该匹配 <h3>4.1 商务管理</h3>

        Args:
            soup: BeautifulSoup对象
            anchor_id: 锚点ID（不含#）

        Returns:
            匹配的标题元素，如果找不到返回None
        """
        # 尝试直接ID匹配
        heading = soup.find(id=anchor_id)
        if heading:
            return heading

        # 尝试从锚点ID反推原始文本
        # "41-商务管理" -> "4.1 商务管理" 或 "4.1商务管理"
        pattern = re.match(r'^(\d)(\d+)-(.+)$', anchor_id)
        if pattern:
            major, minor, text = pattern.groups()
            # 尝试多种可能的格式
            possible_texts = [
                f"{major}.{minor} {text}",
                f"{major}.{minor}{text}",
                f"{major}.{minor}  {text}",  # 可能有多个空格
            ]

            for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for heading in soup.find_all(heading_tag):
                    heading_text = heading.get_text().strip()
                    for possible_text in possible_texts:
                        if heading_text == possible_text or heading_text.startswith(possible_text):
                            return heading

        # 尝试模糊匹配：移除分隔符后比较
        clean_anchor = anchor_id.replace('-', '').replace('_', '')
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(heading_tag):
                heading_text = heading.get_text().strip()
                clean_heading = heading_text.replace('.', '').replace(' ', '').replace('-', '').replace('_', '')
                if clean_anchor in clean_heading or clean_heading in clean_anchor:
                    return heading

        return None

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
                    'permalink_title': 'Permanent link',
                    'slugify': self._custom_slugify
                }
            }
        )

        html_content = md.convert(markdown_content)

        # 为企业文档添加语义化类名
        html_content = self._add_semantic_classes(html_content)

        # 修复锚点链接
        html_content = self._fix_anchor_links(html_content)

        return html_content
    
    def _add_semantic_classes(self, html_content: str) -> str:
        """为HTML内容添加语义化类名以优化分页 - 使用BeautifulSoup替代正则表达式"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 识别并标记会议相关章节
        self._mark_meeting_sections(soup)

        # 添加特定页面布局控制类
        self._add_page_layout_classes(soup)

        # 为内容块添加包装
        self._wrap_content_blocks(soup)

        return str(soup)

    def _mark_meeting_sections(self, soup: BeautifulSoup) -> None:
        """标记会议相关章节"""
        meeting_keywords = ['会议', '议程', '讨论', '决定', '行动', '任务', '问题']
        action_keywords = ['行动项目', '任务分配', '决策要点']
        decision_keywords = ['决定', '决策', '结论']

        # 标记h2会议章节
        for h2 in soup.find_all('h2'):
            if h2.get_text() and any(keyword in h2.get_text() for keyword in meeting_keywords):
                h2['class'] = h2.get('class', []) + ['meeting-section']

        # 标记h3行动项目
        for h3 in soup.find_all('h3'):
            text = h3.get_text() if h3.get_text() else ""
            if any(keyword in text for keyword in action_keywords):
                h3['class'] = h3.get('class', []) + ['action-items']
            elif any(keyword in text for keyword in decision_keywords):
                h3['class'] = h3.get('class', []) + ['decision-points']

    def _add_page_layout_classes(self, soup: BeautifulSoup) -> None:
        """添加页面布局控制类"""
        h2_tags = soup.find_all('h2')

        # 为特定章节添加分页控制类
        for i, h2 in enumerate(h2_tags, 1):
            current_classes = h2.get('class', [])

            if h2.get('id') == '1' or i == 1:
                h2['class'] = current_classes + ['first-page-section']
            elif h2.get('id') == '2' or i == 2:
                h2['class'] = current_classes + ['second-page-section']
            elif h2.get('id') == '3' or i == 3:
                h2['class'] = current_classes + ['module-reports-section']

    def _wrap_content_blocks(self, soup: BeautifulSoup) -> None:
        """为内容块添加包装div以便更好的分页控制"""
        # 包装列表
        for tag_name in ['ul', 'ol']:
            for tag in soup.find_all(tag_name):
                if not tag.parent or tag.parent.name != 'div' or 'content-block' not in tag.parent.get('class', []):
                    wrapper = soup.new_tag('div', **{'class': 'content-block'})
                    tag.wrap(wrapper)

        # 包装表格
        for table in soup.find_all('table'):
            if not table.parent or table.parent.name != 'div' or 'content-block' not in table.parent.get('class', []):
                wrapper = soup.new_tag('div', **{'class': 'content-block'})
                table.wrap(wrapper)
    
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
