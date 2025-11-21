#!/usr/bin/env python3
"""
Simplified PDF Converter for VCU Meeting Minutes
================================================

Self-contained PDF conversion without external dependencies.
"""

import asyncio
import markdown
import sys
from pathlib import Path
from typing import Optional
from pyppeteer import launch


def convert_markdown_to_pdf(
    markdown_file: str,
    theme: str = "enterprise",
    auto_open: bool = True
) -> Optional[Path]:
    """
    Convert Markdown file to PDF

    Args:
        markdown_file: Path to markdown file
        theme: Theme name (enterprise/github)
        auto_open: Whether to open PDF after generation

    Returns:
        Path to generated PDF file, or None if failed
    """
    try:
        markdown_path = Path(markdown_file)
        if not markdown_path.exists():
            print(f"❌ Markdown文件不存在: {markdown_file}")
            return None

        # Read markdown content
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert to HTML
        html_content = _convert_markdown_to_html(markdown_content)

        # Get theme CSS
        theme_css = _get_theme_css(theme)

        # Create full HTML document
        full_html = _create_html_document(
            html_content,
            markdown_path.stem,
            theme_css
        )

        # Convert to PDF
        pdf_path = markdown_path.with_suffix('.pdf')

        # Run async conversion
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_convert_html_to_pdf(full_html, pdf_path))

        if pdf_path.exists():
            print(f"✅ PDF已生成: {pdf_path}")

            if auto_open:
                import subprocess
                if sys.platform == 'darwin':
                    subprocess.run(['open', str(pdf_path)])
                elif sys.platform == 'win32':
                    subprocess.run(['start', str(pdf_path)], shell=True)
                else:
                    subprocess.run(['xdg-open', str(pdf_path)])

            return pdf_path
        else:
            print("❌ PDF生成失败")
            return None

    except Exception as e:
        print(f"❌ PDF转换错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def _convert_markdown_to_html(markdown_content: str) -> str:
    """Convert Markdown to HTML"""
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

    # Add semantic classes for better pagination
    html_content = _add_semantic_classes(html_content)

    return html_content


def _add_semantic_classes(html_content: str) -> str:
    """Add semantic classes to HTML for optimized page breaks"""
    import re

    # Meeting-related section patterns
    meeting_patterns = [
        (r'<h2>([^<]*(?:会议|议程|讨论|决定|行动|任务|问题)[^<]*)</h2>',
         r'<h2 class="meeting-section">\1</h2>'),
        (r'<h3>([^<]*(?:行动项目|任务分配|决策要点)[^<]*)</h3>',
         r'<h3 class="action-items">\1</h3>'),
        (r'<h3>([^<]*(?:决定|决策|结论)[^<]*)</h3>',
         r'<h3 class="decision-points">\1</h3>'),
    ]

    for pattern, replacement in meeting_patterns:
        html_content = re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)

    # Add pagination control classes
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

    # Wrap lists and tables with content-block class
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

    html_content = re.sub(
        r'(<table>.*?</table>)',
        r'<div class="content-block">\1</div>',
        html_content,
        flags=re.DOTALL
    )

    return html_content


def _create_html_document(html_content: str, title: str, theme_css: str) -> str:
    """Create complete HTML document"""
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


async def _convert_html_to_pdf(html_content: str, output_path: Path):
    """Convert HTML to PDF using pyppeteer"""
    pdf_options = {
        'format': 'A4',
        'margin': {
            'top': '2.5cm',
            'bottom': '3cm',
            'left': '2cm',
            'right': '2cm'
        },
        'printBackground': True,
        'displayHeaderFooter': False,
        'preferCSSPageSize': True,
        'scale': 1.0
    }

    launch_kwargs = {
        'headless': True,
        'args': [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-plugins',
        ],
        'handleSIGINT': False,
        'handleSIGTERM': False,
        'handleSIGHUP': False,
    }

    # Detect local browser
    exec_path = _detect_browser_executable()
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

        # Wait for images to load
        try:
            await page.waitForSelector('img', {'timeout': 5000})
            await page.evaluate('''
                () => {
                    return Promise.all(Array.from(document.images).map(img => {
                        if (img.complete) return Promise.resolve(img.naturalHeight !== 0);
                        return new Promise((resolve, reject) => {
                            img.addEventListener('load', resolve);
                            img.addEventListener('error', reject);
                        });
                    }));
                }
            ''')
        except:
            pass  # No images or timeout, continue

        # Generate PDF
        await page.pdf({**pdf_options, 'path': str(output_path)})

    finally:
        await browser.close()


def _detect_browser_executable() -> Optional[str]:
    """Detect local browser executable"""
    import shutil

    candidates = []
    if sys.platform == 'darwin':
        candidates = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
            '/Applications/Chromium.app/Contents/MacOS/Chromium',
        ]
    elif sys.platform == 'win32':
        candidates = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
        ]
    else:  # Linux
        candidates = ['google-chrome', 'chromium', 'chromium-browser', 'microsoft-edge']
        candidates = [shutil.which(c) for c in candidates]

    for path in candidates:
        if path and Path(path).exists():
            return str(path)

    return None


def _get_theme_css(theme_name: str) -> str:
    """Get theme CSS"""
    if theme_name == "github":
        return _get_github_css()
    else:  # Default to enterprise
        return _get_enterprise_css()


def _get_github_css() -> str:
    """GitHub theme CSS"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 14px;
        line-height: 1.6;
        color: #1f2328;
        max-width: 1012px;
        margin: 0 auto;
        padding: 32px;
    }
    h1, h2 {
        padding-bottom: 0.3em;
        border-bottom: 1px solid #d8dee4;
    }
    </style>
    """


def _get_enterprise_css() -> str:
    """Enterprise theme CSS - Complete stylesheet for VCU meeting minutes"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&family=Source+Code+Pro:wght@400;600&display=swap');

    * {
        box-sizing: border-box;
    }

    body {
        font-family: 'Source Sans Pro', 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        line-height: 1.7;
        color: #2c3e50;
        max-width: 980px;
        margin: 0 auto;
        padding: 48px;
        background: #ffffff;
    }

    h1 {
        font-size: 32px;
        font-weight: 700;
        color: #1a365d;
        margin-bottom: 8px;
        padding-bottom: 16px;
        border-bottom: 3px solid #2563eb;
        text-align: center;
    }

    h2,
    h2.meeting-section,
    h2.first-page-section,
    h2.module-reports-section {
        font-size: 24px;
        font-weight: 600;
        color: #1e40af;
        margin: 40px 0 20px 0;
        padding: 12px 0 12px 20px;
        border-left: 5px solid #3b82f6;
        background: linear-gradient(90deg, #dbeafe 0%, rgba(219,234,254,0.0) 100%) !important;
        background-color: #dbeafe !important;
    }

    h3 {
        font-size: 18px;
        font-weight: 600;
        color: #374151;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e5e7eb;
    }

    h4 {
        font-size: 16px;
        font-weight: 600;
        color: #4b5563;
        margin: 24px 0 12px 0;
    }

    p {
        margin: 16px 0;
        text-align: justify;
        color: #374151;
    }

    ul, ol {
        margin: 16px 0;
        padding-left: 24px;
    }

    li {
        margin: 8px 0;
        line-height: 1.6;
    }

    ul li {
        list-style-type: none;
        position: relative;
    }

    ul li:before {
        content: "▸";
        color: #3b82f6;
        font-weight: bold;
        position: absolute;
        left: -20px;
    }

    ol {
        padding-left: 24px;
        margin: 16px 0;
    }

    ol li {
        margin: 8px 0;
        padding-left: 8px;
        text-align: left;
        line-height: 1.6;
    }

    ol li::marker {
        color: #3b82f6;
        font-weight: 600;
    }

    ol ol {
        margin: 4px 0;
        padding-left: 20px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 24px 0;
        font-size: 13px;
        background: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        table-layout: fixed;
    }

    th {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        border: none;
        height: 44px;
    }

    td {
        padding: 12px 16px;
        border-bottom: 1px solid #e5e7eb;
        vertical-align: top;
        height: 52px;
        line-height: 1.4;
    }

    tbody tr {
        height: 52px;
        min-height: 52px;
        max-height: 52px;
    }

    tr:nth-child(even) {
        background: #f8fafc;
    }

    tr:hover {
        background: #eff6ff;
    }

    tr td {
        box-sizing: border-box;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    code {
        font-family: 'Source Code Pro', Menlo, Monaco, monospace;
        background: #f1f5f9;
        color: #1e293b;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 13px;
        border: 1px solid #e2e8f0;
    }

    pre {
        background: #1e293b;
        color: #e2e8f0;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 20px 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    pre code {
        background: none;
        color: inherit;
        padding: 0;
        border: none;
        border-radius: 0;
    }

    blockquote {
        border-left: 4px solid #fbbf24;
        background: #fffbeb;
        margin: 20px 0;
        padding: 16px 20px;
        border-radius: 0 6px 6px 0;
        color: #92400e;
        font-style: italic;
    }

    strong {
        color: #1f2937;
        font-weight: 600;
    }

    em {
        color: #4b5563;
    }

    img {
        max-width: 100%;
        height: auto;
        display: inline-block;
        margin: 2px;
        vertical-align: middle;
    }

    p:first-of-type img {
        margin: 0 4px 0 0;
    }

    p:first-of-type {
        text-align: center;
        margin: 16px 0 24px 0;
        line-height: 1.2;
    }

    a {
        color: #2563eb;
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: all 0.2s ease;
    }

    a:hover {
        color: #1d4ed8;
        border-bottom-color: #1d4ed8;
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #e5e7eb 0%, #9ca3af 50%, #e5e7eb 100%);
        margin: 32px 0;
    }

    @page {
        size: A4;
        margin: 2.5cm 2cm 3cm 2cm;
    }

    body::before {
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
        font-size: 120px;
        color: rgba(59, 130, 246, 0.03);
        z-index: -1;
        font-weight: bold;
        pointer-events: none;
    }

    h1:first-of-type {
        margin-top: 60px;
        position: relative;
    }

    h1:first-of-type::before {
        content: "";
        position: absolute;
        top: -40px;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 50%, #1e40af 100%);
        border-radius: 3px;
    }

    p, li, div {
        orphans: 4;
        widows: 4;
    }

    h1 {
        page-break-before: auto;
        page-break-after: avoid;
        page-break-inside: avoid;
    }

    h1:first-of-type {
        page-break-before: auto;
    }

    .first-page-section {
        page-break-before: avoid !important;
        page-break-after: auto;
    }

    .second-page-section {
        page-break-before: page !important;
    }

    .second-page-section + table {
        page-break-after: page !important;
        margin-bottom: 40px;
    }

    h2[id="3"],
    .module-reports-section,
    h2:nth-of-type(3) {
        page-break-before: auto;
        page-break-after: avoid;
        margin-top: 32px !important;
        padding-top: 16px !important;
    }

    h2, h3, h4, h5, h6 {
        page-break-after: avoid;
        page-break-inside: avoid;
    }

    table, figure, .content-block {
        page-break-inside: avoid;
    }

    ul, ol {
        page-break-inside: auto;
    }

    li {
        page-break-inside: avoid;
    }
    </style>
    """
