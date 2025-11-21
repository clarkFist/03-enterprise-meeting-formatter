#!/usr/bin/env python3
# 兼容旧入口的包装器：转发到可导入模块 scripts/generate_meeting.py

import sys
from pathlib import Path

def _run():
    # 将当前脚本所在目录的父目录（技能根目录）加入 sys.path
    skill_dir = Path(__file__).parent.parent.resolve()
    sys.path.insert(0, str(skill_dir))
    from scripts.generate_meeting import main  # type: ignore
    return main()

if __name__ == "__main__":
    _run()
