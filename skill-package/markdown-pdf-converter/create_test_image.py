#!/usr/bin/env python3
"""
Create a test image with attendee information
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_test_attendee_image(output_path: str):
    """Create test image with attendee table"""
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Try to use system font
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
        font_normal = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
        font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 16)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Title
    title = "VCU项目例会参会人员统计表"
    draw.text((50, 30), title, fill='black', font=font_large)

    # Draw table header
    y_start = 100
    col_widths = [100, 150, 150, 180]
    headers = ["姓名", "工号", "角色", "部门"]

    x = 50
    for i, header in enumerate(headers):
        draw.text((x, y_start), header, fill='black', font=font_normal)
        x += col_widths[i]

    # Draw table data
    attendees = [
        ["傅李育", "60001", "项目经理", "VCU项目部"],
        ["房华玲", "60234", "硬件工程师", "硬件设计部"],
        ["刘浩洋", "60456", "软件工程师", "软件开发部"],
        ["张三", "60123", "测试工程师", "质量保证部"],
        ["李四", "60789", "系统工程师", "系统集成部"],
    ]

    y = y_start + 40
    for attendee in attendees:
        x = 50
        for i, value in enumerate(attendee):
            draw.text((x, y), value, fill='black', font=font_small)
            x += col_widths[i]
        y += 40

    # Additional info
    y += 40
    info_text = [
        "会议时间：2025-11-15 14:00-16:00",
        "会议地点：企业微信会议",
        f"参会人数：{len(attendees)}人"
    ]

    for text in info_text:
        draw.text((50, y), text, fill='blue', font=font_small)
        y += 30

    # Save image
    image.save(output_path)
    print(f"✅ 测试图片已生成: {output_path}")
    print(f"📐 尺寸: {width}x{height}")

    # Get file size
    size = Path(output_path).stat().st_size
    print(f"📊 大小: {size:,} bytes ({size/1024:.1f} KB)")

if __name__ == "__main__":
    output = "test_attendees_image.png"
    create_test_attendee_image(output)
