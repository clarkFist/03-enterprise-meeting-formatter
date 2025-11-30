#!/usr/bin/env python3
"""
增强版Markdown转PDF转换器
支持YAML Front Matter文档类型识别
"""

import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional

# 添加pypi-package到路径
sys.path.insert(0, str(Path(__file__).parent / "pypi-package" / "src"))


def parse_front_matter(content: str) -> Tuple[Dict, str]:
    """
    解析Markdown文件的YAML Front Matter

    Args:
        content: 原始文件内容

    Returns:
        (metadata_dict, content_without_front_matter)
    """
    # 匹配YAML Front Matter: ---\n...yaml...\n---\n
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    yaml_text = match.group(1)
    markdown_content = match.group(2)

    # 简单的YAML解析（避免依赖yaml库）
    metadata = {}
    for line in yaml_text.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'')

            # 处理布尔值
            if value.lower() in ('true', 'yes'):
                value = True
            elif value.lower() in ('false', 'no'):
                value = False

            metadata[key] = value

    return metadata, markdown_content


class DocumentTypeDetector:
    """文档类型智能识别器"""

    FEATURES = {
        'work-summary': {
            'must_have': [
                r'年度成果概览',
                r'姓名：',
            ],
            'should_have': [
                r'^## [一二三四五六七八]、',
                r'工作总结',
                r'版本发布',
            ],
        },
        'meeting-minutes': {
            'must_have': [
                r'参会人员',
                r'会议时间',
            ],
            'should_have': [
                r'会议纪要',
                r'决策事项',
                r'行动计划',
            ],
        }
    }

    def detect(self, content: str) -> str:
        """
        自动识别文档类型

        Returns:
            'work-summary' | 'meeting-minutes' | 'generic'
        """
        scores = {}

        for doc_type, features in self.FEATURES.items():
            score = 0

            # 必须特征（权重3）
            for pattern in features['must_have']:
                if re.search(pattern, content, re.MULTILINE):
                    score += 3

            # 建议特征（权重1）
            for pattern in features['should_have']:
                if re.search(pattern, content, re.MULTILINE):
                    score += 1

            scores[doc_type] = score

        # 返回得分最高的类型
        if scores:
            max_score = max(scores.values())
            if max_score >= 3:  # 置信度阈值
                return max(scores, key=scores.get)

        return 'generic'


class WorkSummaryProcessor:
    """工作总结文档处理器"""

    def __init__(self, metadata: Dict):
        self.metadata = metadata

    def process(self, content: str) -> str:
        """处理工作总结文档"""
        print("📊 应用工作总结处理流程...")

        # 1. 修复锚点链接
        content = self._fix_anchor_links(content)
        print("  ✓ 修复锚点链接")

        # 2. 确保分页标记
        content = self._ensure_page_breaks(content)
        print("  ✓ 添加分页标记")

        # 3. 优化表格
        content = self._optimize_tables(content)
        print("  ✓ 优化表格格式")

        return content

    def _fix_anchor_links(self, content: str) -> str:
        """修复中文章节锚点链接：#一版本发布 → #一、版本发布"""
        pattern = r'\(#([一二三四五六七八])([^\)、]+)\)'

        def replacer(match):
            number = match.group(1)
            title = match.group(2)
            return f'(#{number}、{title})'

        return re.sub(pattern, replacer, content)

    def _ensure_page_breaks(self, content: str) -> str:
        """确保关键位置有分页标记"""
        lines = content.split('\n')
        result = []

        for i, line in enumerate(lines):
            # 在目录前添加分页（如果没有）
            if line.startswith('## 目录'):
                if i > 0 and not lines[i-1].strip().startswith('<div style="page-break'):
                    result.append('<div style="page-break-before: always;"></div>')
                    result.append('')

            # 在大章节前添加分页（如果没有）
            elif re.match(r'^## [一二三四五六七八]、', line):
                if i > 0 and not lines[i-1].strip().startswith('<div style="page-break'):
                    result.append('<div style="page-break-before: always;"></div>')
                    result.append('')

            result.append(line)

        return '\n'.join(result)

    def _optimize_tables(self, content: str) -> str:
        """优化表格：简化数量列"""
        # 简化数量：4个→4, 3项→3, 5次→5
        content = re.sub(r'(\| \d+)[个项次]( \|)', r'\1\2', content)
        return content


class MeetingMinutesProcessor:
    """会议纪要文档处理器"""

    def __init__(self, metadata: Dict):
        self.metadata = metadata

    def process(self, content: str) -> str:
        """处理会议纪要文档"""
        print("📝 应用会议纪要处理流程...")
        print("  ✓ 保持原有格式")
        return content


class GenericProcessor:
    """通用文档处理器"""

    def __init__(self, metadata: Dict):
        self.metadata = metadata

    def process(self, content: str) -> str:
        """通用文档处理"""
        print("📄 使用通用处理流程...")
        return content


def detect_document_type(content: str, metadata: Dict) -> str:
    """
    多层文档类型检测

    优先级:
    1. YAML Front Matter指定
    2. 自动特征识别
    3. 默认为generic
    """
    # 1. 检查YAML Front Matter
    doc_type = metadata.get('doc_type')
    if doc_type:
        print(f"✓ 从YAML Front Matter识别: {doc_type}")
        return doc_type

    # 2. 自动识别
    detector = DocumentTypeDetector()
    doc_type = detector.detect(content)

    if doc_type != 'generic':
        print(f"✓ 自动识别文档类型: {doc_type}")
    else:
        print("ℹ️  使用通用处理流程")

    return doc_type


def get_processor(doc_type: str, metadata: Dict):
    """根据文档类型获取处理器"""
    processors = {
        'work-summary': WorkSummaryProcessor,
        'meeting-minutes': MeetingMinutesProcessor,
        'generic': GenericProcessor,
    }

    processor_class = processors.get(doc_type, GenericProcessor)
    return processor_class(metadata)


def main():
    """主函数"""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description='增强版Markdown转PDF转换器（支持YAML Front Matter）'
    )
    parser.add_argument('input', help='输入Markdown文件')
    parser.add_argument('-t', '--theme', default='github', help='PDF主题')
    parser.add_argument('-o', '--output', help='输出PDF路径')
    parser.add_argument('--type', help='强制指定文档类型')

    args = parser.parse_args()

    # 读取文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"✗ 文件不存在: {input_path}")
        return 1

    print(f"\n📖 读取文件: {input_path.name}")
    content = input_path.read_text(encoding='utf-8')

    # 解析Front Matter
    metadata, markdown_content = parse_front_matter(content)

    if metadata:
        print(f"✓ 发现YAML Front Matter: {len(metadata)}个配置项")

    # 检测文档类型
    doc_type = args.type or detect_document_type(markdown_content, metadata)

    # 获取主题（优先级：命令行 > YAML > 默认）
    theme = args.theme or metadata.get('theme', 'github')

    # 应用处理器
    processor = get_processor(doc_type, metadata)
    processed_content = processor.process(markdown_content)

    # 重新组装（保留Front Matter）
    if metadata:
        yaml_lines = ['---']
        for key, value in metadata.items():
            yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        full_content = '\n'.join(yaml_lines) + '\n\n' + processed_content
    else:
        full_content = processed_content

    # 写入临时文件
    temp_file = input_path.parent / f'.tmp_{input_path.name}'
    temp_file.write_text(full_content, encoding='utf-8')

    # 生成输出路径
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"{input_path.stem}_{timestamp}.pdf"
        output_path = input_path.parent / output_name
    else:
        output_path = Path(args.output)

    # 调用转换器
    print(f"\n🔄 转换为PDF (主题: {theme})...")

    try:
        from md2pdf_enterprise.cli import main_async
        import asyncio
        import argparse as _argparse

        # 构造参数
        converter_args = _argparse.Namespace(
            input=str(temp_file),
            output=str(output_path),
            theme=theme,
            all=False,
            list_themes=False
        )

        # 执行转换
        asyncio.run(main_async(converter_args))

        # 清理临时文件
        temp_file.unlink()

        print(f"\n✓ 转换完成: {output_path.name}")
        return 0

    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
        if temp_file.exists():
            temp_file.unlink()
        return 1


if __name__ == '__main__':
    sys.exit(main())
