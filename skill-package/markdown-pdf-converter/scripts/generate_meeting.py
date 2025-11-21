#!/usr/bin/env python3
"""
VCU项目会议纪要生成器（可导入模块）
基于YAML配置文件和Jinja2模板生成会议纪要Markdown文档
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class MeetingMinutesGenerator:
    """会议纪要生成器"""

    def __init__(self, skill_dir=None):
        """初始化生成器

        Args:
            skill_dir: Skill包根目录，默认为脚本所在目录的父目录
        """
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent
        else:
            skill_dir = Path(skill_dir)

        self.skill_dir = skill_dir
        self.templates_dir = skill_dir / "templates"
        self.data_dir = skill_dir / "data"

        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def load_yaml(self, yaml_file):
        """加载YAML配置文件"""
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {yaml_file}")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_filename(self, meeting_time):
        """生成会议纪要文件名"""
        try:
            # 优先从 meeting_time 提取日期 YYYY-MM-DD
            dt = datetime.strptime(meeting_time.split()[0], "%Y-%m-%d")
            date_str = dt.strftime("%Y%m%d")
        except Exception:
            date_str = datetime.now().strftime("%Y%m%d")
        return f"RB99125046安全运算与控制平台（VCU）项目例会会议纪要_{date_str}.md"

    def merge_attendees(self, config_data):
        """合并参会人员数据（若未提供，则从 attendees.yaml 加载默认）"""
        if 'attendees' not in config_data or not config_data['attendees']:
            attendees_file = self.data_dir / "attendees.yaml"
            if attendees_file.exists():
                with open(attendees_file, 'r', encoding='utf-8') as f:
                    attendees_data = yaml.safe_load(f)
                    config_data['attendees'] = {
                        'hosts': [attendees_data['hosts'][0]] if 'hosts' in attendees_data else [],
                        'managers': attendees_data.get('managers', []),
                        'engineers': attendees_data.get('engineers', [])
                    }
                    # 默认出席
                    for category in config_data['attendees'].values():
                        for person in category:
                            person['present'] = person.get('present', True)
        return config_data

    def generate(self, input_file, output_file=None, template="vcu-meeting-template.j2"):
        """生成会议纪要 Markdown"""
        print(f"📄 加载配置: {input_file}")
        config_data = self.load_yaml(input_file)
        config_data = self.merge_attendees(config_data)

        if output_file is None:
            meeting_time = config_data.get('meeting_time', datetime.now().strftime("%Y-%m-%d"))
            output_file = self.generate_filename(meeting_time)

        output_path = Path(output_file)
        print(f"📋 使用模板: {template}")
        try:
            template_obj = self.jinja_env.get_template(template)
        except TemplateNotFound:
            raise FileNotFoundError(f"模板文件不存在: {self.templates_dir / template}")

        print(f"⚙️  生成会议纪要...")
        content = template_obj.render(**config_data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 会议纪要已生成: {output_path}")
        print(f"   文件大小: {output_path.stat().st_size / 1024:.1f} KB")
        return output_path


def main():
    """兼容 CLI 的入口"""
    if len(sys.argv) < 2:
        print("用法: python generate-meeting.py <input.yaml> [output.md] [template.j2]")
        print()
        print("示例:")
        print("  python generate-meeting.py data/meeting-input-example.yaml")
        print("  python generate-meeting.py input.yaml output.md")
        print("  python generate-meeting.py input.yaml output.md custom-template.j2")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    template = sys.argv[3] if len(sys.argv) > 3 else "vcu-meeting-template.j2"
    try:
        generator = MeetingMinutesGenerator()
        output_path = generator.generate(input_file, output_file, template)
        print()
        print("📌 下一步:")
        print(f"  查看文件: open '{output_path}'")
        print(f"  转换PDF:  ./scripts/convert.sh '{output_path}'")
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

