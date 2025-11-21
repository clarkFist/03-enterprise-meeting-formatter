#!/usr/bin/env python3
"""
VCU项目会议图片OCR提取器
使用Claude Vision API从会议图片中提取参会人员信息并自动生成会议纪要
"""

import os
import sys
import json
import yaml
import base64
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 尝试导入anthropic，如果未安装则提示
try:
    import anthropic
except ImportError:
    print("❌ 错误: 需要安装 anthropic 库")
    print("   安装命令: pip install anthropic")
    sys.exit(1)


class MeetingImageExtractor:
    """会议图片OCR提取器"""

    def __init__(self, skill_dir=None):
        """初始化提取器

        Args:
            skill_dir: Skill包根目录，默认为脚本所在目录的父目录
        """
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent
        else:
            skill_dir = Path(skill_dir)

        self.skill_dir = skill_dir
        self.data_dir = skill_dir / "data"
        self.scripts_dir = skill_dir / "scripts"

        # 加载参会人员数据库
        self.attendees_db = self._load_attendees_db()

        # 初始化Claude客户端
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ 错误: 未设置 ANTHROPIC_API_KEY 环境变量\n"
                "   设置方法: export ANTHROPIC_API_KEY='your-api-key'"
            )

        self.client = anthropic.Anthropic(api_key=api_key)

    def _load_attendees_db(self) -> Dict:
        """加载参会人员数据库"""
        attendees_file = self.data_dir / "attendees.yaml"
        if not attendees_file.exists():
            raise FileNotFoundError(f"参会人员数据库不存在: {attendees_file}")

        with open(attendees_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """将图片编码为base64

        Args:
            image_path: 图片文件路径

        Returns:
            tuple: (base64编码的图片数据, 媒体类型)
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 根据文件扩展名确定媒体类型
        ext = image_path.suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        return image_data, media_type

    def extract_attendees_from_image(self, image_path: str) -> List[Dict]:
        """从图片中仅提取参会人员信息（用于双输入模式）

        Args:
            image_path: 图片文件路径

        Returns:
            list: 参会人员列表
        """
        print(f"🔍 分析参会人员图片: {image_path}")

        # 编码图片
        image_data, media_type = self._encode_image(image_path)

        # 构建简化的提示词（只关注参会人员）
        prompt = """请仔细分析这张参会人员列表图片，提取所有参会人员的信息。

请以JSON格式返回结果，格式如下：
```json
{
  "attendees": [
    {
      "name": "姓名",
      "employee_id": "工号",
      "role": "角色",
      "module": "负责模块",
      "present": true
    }
  ]
}
```

注意：
1. 工号必须是纯数字，不要包含其他字符
2. 姓名必须是中文全名
3. 如果图片中没有某些信息，可以省略对应字段或返回空值
4. 确保JSON格式正确，可以被解析"""

        # 调用Claude Vision API
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # 解析响应
            response_text = message.content[0].text

            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()

            extracted_data = json.loads(json_str)
            attendees = extracted_data.get('attendees', [])

            print(f"✅ 成功提取 {len(attendees)} 名参会人员")

            return attendees

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应:\n{response_text}")
            raise
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            raise

    def parse_meeting_content(self, content_text: str) -> Dict:
        """从文本中解析会议内容

        Args:
            content_text: 会议内容文本

        Returns:
            dict: 解析后的会议信息，包含meeting_info和modules
        """
        print(f"\n📝 解析会议内容文本...")
        print(f"   文本长度: {len(content_text)} 字符")

        # 构建文本解析提示词
        prompt = f"""请仔细分析以下会议纪要文本，提取会议信息和各模块进展。

会议纪要文本：
```
{content_text}
```

请以JSON格式返回结果，格式如下：
```json
{{
  "meeting_info": {{
    "meeting_time": "YYYY-MM-DD HH:MM-HH:MM",
    "meeting_location": "会议地点",
    "meeting_host": "主持人",
    "recorder": "记录人（工号）",
    "meeting_nature": "会议性质",
    "company_name": "CASCO SIGNAL"
  }},
  "modules": [
    {{
      "section": "3.1",
      "name": "模块名称",
      "owner": "负责人",
      "status": "✅ 按计划推进 / ⚠️ 存在风险，进度延后",
      "progress": ["进展内容1", "进展内容2"],
      "issues": ["问题1", "问题2"],
      "plans": ["计划1", "计划2"]
    }}
  ],
  "leadership_instructions": [
    {{
      "section": "4.1",
      "title": "领导姓名指示",
      "instructions": ["指示内容1", "指示内容2"]
    }}
  ],
  "tasks": [
    {{
      "id": "T001",
      "content": "任务内容",
      "owner": "负责人",
      "deadline": "截止时间",
      "status": "⏳ 进行中 / ✅ 已完成 / ⚠️ 风险",
      "priority": "🔴 高 / 🟡 中 / 🟢 低"
    }}
  ],
  "decisions": [
    "决策事项1",
    "决策事项2"
  ],
  "risks": [
    {{
      "id": "R001",
      "description": "风险描述",
      "level": "🔴 高 / 🟡 中 / 🟢 低",
      "solution": "解决方案",
      "owner": "负责人"
    }}
  ]
}}
```

注意：
1. 如果文本中没有某些信息，可以省略对应字段或返回空值
2. 状态使用emoji表示：✅ 按计划推进，⚠️ 存在风险
3. 优先级和风险等级用emoji：🔴 高，🟡 中，🟢 低
4. 尽可能从文本中提取完整信息
5. 确保JSON格式正确，可以被解析"""

        # 调用Claude API解析文本
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            # 解析响应
            response_text = message.content[0].text

            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()

            parsed_data = json.loads(json_str)

            print(f"✅ 成功解析会议内容")
            if 'modules' in parsed_data:
                print(f"   - 找到 {len(parsed_data.get('modules', []))} 个模块汇报")
            if 'tasks' in parsed_data:
                print(f"   - 找到 {len(parsed_data.get('tasks', []))} 个任务")
            if 'risks' in parsed_data:
                print(f"   - 找到 {len(parsed_data.get('risks', []))} 个风险")

            return parsed_data

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应:\n{response_text}")
            raise
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            raise

    def extract_from_image(self, image_path: str) -> Dict:
        """使用Claude Vision API从图片中提取会议信息

        Args:
            image_path: 图片文件路径

        Returns:
            dict: 提取的会议信息，包含参会人员、会议时间等
        """
        print(f"🔍 分析图片: {image_path}")

        # 编码图片
        image_data, media_type = self._encode_image(image_path)

        # 构建提示词
        prompt = """请仔细分析这张会议相关的图片，提取以下信息：

1. **参会人员列表**：提取所有参会人员的信息
   - 姓名（必须）
   - 工号（如果有）
   - 角色/职位（如果有）
   - 负责模块（如果有）
   - 出席状态（如果有标注）

2. **会议基本信息**（如果图片中包含）：
   - 会议时间
   - 会议地点
   - 会议主持人
   - 记录人员
   - 会议性质

3. **模块进展信息**（如果图片中包含）：
   - 模块名称
   - 负责人
   - 进展状态
   - 存在的问题
   - 后续计划

请以JSON格式返回结果，格式如下：
```json
{
  "meeting_info": {
    "meeting_time": "YYYY-MM-DD HH:MM-HH:MM",
    "meeting_location": "会议地点",
    "meeting_host": "主持人",
    "recorder": "记录人（工号）",
    "meeting_nature": "会议性质",
    "company_name": "CASCO SIGNAL"
  },
  "attendees": [
    {
      "name": "姓名",
      "employee_id": "工号",
      "role": "角色",
      "module": "负责模块",
      "present": true
    }
  ],
  "modules": [
    {
      "name": "模块名称",
      "owner": "负责人",
      "status": "进展状态",
      "progress": ["进展内容1", "进展内容2"],
      "issues": ["问题1", "问题2"],
      "plans": ["计划1", "计划2"]
    }
  ]
}
```

注意：
1. 如果某些信息在图片中不存在，可以省略对应字段或返回空值
2. 工号必须是纯数字，不要包含其他字符
3. 姓名必须是中文全名
4. 确保JSON格式正确，可以被解析"""

        # 调用Claude Vision API
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # 解析响应
            response_text = message.content[0].text

            # 尝试从响应中提取JSON
            # Claude可能会在JSON前后添加说明文字，需要提取```json```块
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()

            extracted_data = json.loads(json_str)

            print(f"✅ 成功提取信息")
            print(f"   - 找到 {len(extracted_data.get('attendees', []))} 名参会人员")
            if 'modules' in extracted_data:
                print(f"   - 找到 {len(extracted_data.get('modules', []))} 个模块汇报")

            return extracted_data

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应:\n{response_text}")
            raise
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            raise

    def match_attendees(self, extracted_attendees: List[Dict]) -> List[Dict]:
        """将提取的参会人员与数据库匹配

        Args:
            extracted_attendees: 从图片中提取的参会人员列表

        Returns:
            list: 匹配后的完整参会人员信息
        """
        print("\n🔗 匹配参会人员数据库...")

        matched = []
        unmatched = []

        # 构建数据库索引（按姓名和工号）
        db_by_name = {}
        db_by_id = {}

        for category in ['hosts', 'managers', 'engineers']:
            if category not in self.attendees_db:
                continue
            for person in self.attendees_db[category]:
                name = person.get('name', '')
                emp_id = person.get('employee_id', '')
                if name:
                    db_by_name[name] = person
                if emp_id:
                    db_by_id[emp_id] = person

        # 匹配每个提取的人员
        for extracted in extracted_attendees:
            name = extracted.get('name', '').strip()
            emp_id = extracted.get('employee_id', '').strip()

            matched_person = None

            # 优先按工号匹配
            if emp_id and emp_id in db_by_id:
                matched_person = db_by_id[emp_id].copy()
                print(f"  ✓ {name} ({emp_id}) - 按工号匹配")
            # 其次按姓名匹配
            elif name and name in db_by_name:
                matched_person = db_by_name[name].copy()
                print(f"  ✓ {name} - 按姓名匹配")

            if matched_person:
                # 更新出席状态
                matched_person['present'] = extracted.get('present', True)
                matched.append(matched_person)
            else:
                # 未匹配到，记录新人员
                unmatched.append(extracted)
                print(f"  ⚠️  {name} ({emp_id}) - 未在数据库中找到")

        if unmatched:
            print(f"\n⚠️  发现 {len(unmatched)} 名新人员，将使用提取的信息")

        print(f"\n✅ 匹配完成: {len(matched)} 人匹配，{len(unmatched)} 人新增")

        return matched, unmatched

    def generate_config(
        self,
        meeting_info: Dict,
        matched_attendees: List[Dict],
        unmatched_attendees: List[Dict],
        modules: Optional[List[Dict]] = None,
        output_path: Optional[str] = None
    ) -> Path:
        """生成会议输入配置文件

        Args:
            meeting_info: 会议基本信息
            matched_attendees: 匹配的参会人员
            unmatched_attendees: 未匹配的参会人员
            modules: 模块进展信息
            output_path: 输出文件路径，默认自动生成

        Returns:
            Path: 生成的配置文件路径
        """
        print("\n📝 生成配置文件...")

        # 确定输出路径
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.data_dir / f"meeting-input-{timestamp}.yaml"
        else:
            output_path = Path(output_path)

        # 按角色分组参会人员
        hosts = []
        managers = []
        engineers = []

        for person in matched_attendees:
            role = person.get('role', '')
            if '项目经理' in role or '主持' in role:
                hosts.append(person)
            elif '管理' in role:
                managers.append(person)
            else:
                engineers.append(person)

        # 将未匹配的人员添加到engineers
        for person in unmatched_attendees:
            engineers.append(person)

        # 构建配置数据
        config_data = {
            'meeting_time': meeting_info.get('meeting_time', datetime.now().strftime("%Y-%m-%d %H:%M-%H:%M")),
            'meeting_location': meeting_info.get('meeting_location', '企业微信会议'),
            'meeting_host': meeting_info.get('meeting_host', hosts[0]['name'] if hosts else ''),
            'recorder': meeting_info.get('recorder', ''),
            'meeting_nature': meeting_info.get('meeting_nature', '定期项目例会'),
            'meeting_type': 'Regular',
            'priority': 'High',
            'company_name': meeting_info.get('company_name', 'CASCO SIGNAL'),
            'attendees': {
                'hosts': hosts,
                'managers': managers,
                'engineers': engineers
            }
        }

        # 添加模块信息（如果有）
        if modules:
            config_data['modules'] = modules

        # 写入YAML文件
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        print(f"✅ 配置文件已生成: {output_path}")
        print(f"   文件大小: {output_path.stat().st_size / 1024:.1f} KB")

        return output_path

    def process_dual_input(
        self,
        image_path: str,
        content_text: str,
        output_path: Optional[str] = None,
        generate_pdf: bool = False,
        auto_open: bool = True
    ) -> Dict:
        """处理双输入模式（图片+文本）

        Args:
            image_path: 参会人员图片路径
            content_text: 会议内容文本
            output_path: 输出配置文件路径
            generate_pdf: 是否自动生成PDF
            auto_open: 是否自动打开生成的文件

        Returns:
            dict: 处理结果，包含生成的文件路径
        """
        result = {}

        print("\n" + "=" * 60)
        print("🚀 双输入模式: 图片(参会人员) + 文本(会议内容)")
        print("=" * 60)

        # 1. 从图片提取参会人员
        print("\n步骤 1/5: 从图片提取参会人员")
        attendees = self.extract_attendees_from_image(image_path)

        # 2. 从文本解析会议内容
        print("\n步骤 2/5: 解析会议内容文本")
        content_data = self.parse_meeting_content(content_text)

        # 3. 匹配参会人员
        print("\n步骤 3/5: 匹配参会人员数据库")
        matched, unmatched = self.match_attendees(attendees)

        # 4. 生成配置文件
        print("\n步骤 4/5: 生成YAML配置")
        meeting_info = content_data.get('meeting_info', {})
        modules = content_data.get('modules', [])

        config_path = self.generate_config(
            meeting_info=meeting_info,
            matched_attendees=matched,
            unmatched_attendees=unmatched,
            modules=modules if modules else None
        )

        # 将其他提取的信息也添加到配置中（如果有）
        if 'leadership_instructions' in content_data:
            config_path_obj = Path(config_path)
            with open(config_path_obj, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            config['leadership_instructions'] = content_data['leadership_instructions']
            if 'tasks' in content_data:
                config['tasks'] = content_data['tasks']
            if 'decisions' in content_data:
                config['decisions'] = content_data['decisions']
            if 'risks' in content_data:
                config['risks'] = content_data['risks']
            with open(config_path_obj, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        result['config_path'] = str(config_path)

        # 5. 生成Markdown
        print("\n步骤 5/5: 生成会议纪要")
        generate_script = self.scripts_dir / "generate-meeting.py"

        try:
            subprocess.run(
                [sys.executable, str(generate_script), str(config_path)],
                check=True,
                capture_output=True,
                text=True
            )

            # 获取生成的Markdown文件路径
            meeting_time = meeting_info.get('meeting_time', datetime.now().strftime("%Y-%m-%d"))
            date_str = meeting_time.split()[0].replace('-', '')
            md_filename = f"RB99125046安全运算与控制平台（VCU）项目例会会议纪要_{date_str}.md"
            md_path = Path.cwd() / md_filename

            if md_path.exists():
                result['markdown_path'] = str(md_path)
                print(f"✅ Markdown已生成: {md_path}")

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Markdown生成失败: {e}")
            print(f"   错误输出: {e.stderr}")

        # 6. 生成PDF（如果需要）
        if generate_pdf and 'markdown_path' in result:
            print("\n📄 转换为PDF...")

            try:
                # 使用内部PDF转换模块
                sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
                from pdf_converter import convert_markdown_to_pdf

                pdf_path = convert_markdown_to_pdf(
                    result['markdown_path'],
                    theme='enterprise',
                    auto_open=auto_open
                )

                if pdf_path:
                    result['pdf_path'] = str(pdf_path)

            except Exception as e:
                print(f"⚠️  PDF生成失败: {e}")
                import traceback
                traceback.print_exc()

        return result

    def process_image(
        self,
        image_path: str,
        generate_pdf: bool = False,
        auto_open: bool = True
    ) -> Dict:
        """处理图片并生成会议纪要

        Args:
            image_path: 图片路径
            generate_pdf: 是否自动生成PDF
            auto_open: 是否自动打开生成的文件

        Returns:
            dict: 处理结果，包含生成的文件路径
        """
        result = {}

        # 1. 提取信息
        extracted_data = self.extract_from_image(image_path)

        # 2. 匹配参会人员
        attendees = extracted_data.get('attendees', [])
        matched, unmatched = self.match_attendees(attendees)

        # 3. 生成配置文件
        meeting_info = extracted_data.get('meeting_info', {})
        modules = extracted_data.get('modules', [])

        config_path = self.generate_config(
            meeting_info=meeting_info,
            matched_attendees=matched,
            unmatched_attendees=unmatched,
            modules=modules if modules else None
        )
        result['config_path'] = str(config_path)

        # 4. 生成Markdown
        print("\n📄 生成会议纪要Markdown...")
        generate_script = self.scripts_dir / "generate-meeting.py"

        try:
            subprocess.run(
                [sys.executable, str(generate_script), str(config_path)],
                check=True,
                capture_output=True,
                text=True
            )

            # 获取生成的Markdown文件路径
            meeting_time = meeting_info.get('meeting_time', datetime.now().strftime("%Y-%m-%d"))
            date_str = meeting_time.split()[0].replace('-', '')
            md_filename = f"RB99125046安全运算与控制平台（VCU）项目例会会议纪要_{date_str}.md"
            md_path = Path.cwd() / md_filename

            if md_path.exists():
                result['markdown_path'] = str(md_path)
                print(f"✅ Markdown已生成: {md_path}")

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Markdown生成失败: {e}")
            print(f"   错误输出: {e.stderr}")

        # 5. 生成PDF（如果需要）
        if generate_pdf and 'markdown_path' in result:
            print("\n📄 转换为PDF...")

            try:
                # 使用内部PDF转换模块
                sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
                from pdf_converter import convert_markdown_to_pdf

                pdf_path = convert_markdown_to_pdf(
                    result['markdown_path'],
                    theme='enterprise',
                    auto_open=auto_open
                )

                if pdf_path:
                    result['pdf_path'] = str(pdf_path)

            except Exception as e:
                print(f"⚠️  PDF生成失败: {e}")
                import traceback
                traceback.print_exc()


        return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='VCU项目会议图片OCR提取器 - 支持单图片或图片+文本双输入模式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单图片模式：提取图片信息并生成配置文件
  %(prog)s meeting-photo.png

  # 单图片模式：提取并自动生成PDF
  %(prog)s meeting-photo.png --generate-pdf

  # 双输入模式：图片(参会人员) + 文本文件(会议内容)
  %(prog)s attendees.png --content meeting-notes.txt --generate-pdf

  # 双输入模式：图片 + 直接文本输入
  %(prog)s attendees.png --text "会议时间: 2025-11-14 14:00-16:00..."

  # 生成PDF但不自动打开
  %(prog)s meeting-photo.png --generate-pdf --no-open

  # 指定输出配置文件路径
  %(prog)s meeting-photo.png -o custom-config.yaml
"""
    )

    parser.add_argument(
        'image',
        help='参会人员图片路径（双输入模式）或完整会议信息图片路径（单图片模式）'
    )

    parser.add_argument(
        '-c', '--content',
        help='会议内容文本文件路径（双输入模式）'
    )

    parser.add_argument(
        '-t', '--text',
        help='会议内容直接文本输入（双输入模式）'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出配置文件路径（默认自动生成）'
    )

    parser.add_argument(
        '--generate-pdf',
        action='store_true',
        help='自动生成PDF文件'
    )

    parser.add_argument(
        '--no-open',
        action='store_true',
        help='不自动打开生成的文件'
    )

    args = parser.parse_args()

    try:
        # 检查输入参数
        if args.content and args.text:
            print("❌ 错误: 不能同时指定 --content 和 --text 参数", file=sys.stderr)
            sys.exit(1)

        # 创建提取器
        extractor = MeetingImageExtractor()

        # 判断处理模式
        if args.content or args.text:
            # 双输入模式
            if args.content:
                # 从文件读取文本
                content_path = Path(args.content)
                if not content_path.exists():
                    print(f"❌ 错误: 文本文件不存在: {args.content}", file=sys.stderr)
                    sys.exit(1)

                with open(content_path, 'r', encoding='utf-8') as f:
                    content_text = f.read()

                print(f"📝 从文件加载会议内容: {args.content}")
                print(f"   文件大小: {content_path.stat().st_size / 1024:.1f} KB")
            else:
                # 直接文本输入
                content_text = args.text
                print(f"📝 使用直接输入的会议内容")

            # 处理双输入
            result = extractor.process_dual_input(
                image_path=args.image,
                content_text=content_text,
                output_path=args.output,
                generate_pdf=args.generate_pdf,
                auto_open=not args.no_open
            )
        else:
            # 单图片模式
            print("\n📸 单图片模式: 从图片提取完整会议信息")
            result = extractor.process_image(
                image_path=args.image,
                generate_pdf=args.generate_pdf,
                auto_open=not args.no_open
            )

        # 输出结果
        print("\n" + "=" * 60)
        print("✅ 处理完成")
        print("=" * 60)

        if 'config_path' in result:
            print(f"📋 配置文件: {result['config_path']}")

        if 'markdown_path' in result:
            print(f"📄 Markdown: {result['markdown_path']}")

        if 'pdf_path' in result:
            print(f"📕 PDF文件: {result['pdf_path']}")

        print("\n💡 使用提示:")
        if args.content or args.text:
            print("  🚀 双输入模式已启用")
            print("     - 从图片提取参会人员")
            print("     - 从文本解析会议内容")
        else:
            print("  📸 单图片模式已启用")
            print("  💡 提示: 使用 --content 文件.txt 启用双输入模式")

        if not args.generate_pdf and 'config_path' in result:
            print(f"\n📌 下一步:")
            print(f"  生成纪要: python scripts/generate-meeting.py {result['config_path']}")
            if 'markdown_path' not in result:
                print(f"  转换PDF: ./scripts/convert.sh RB99125046*.md enterprise")

    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
