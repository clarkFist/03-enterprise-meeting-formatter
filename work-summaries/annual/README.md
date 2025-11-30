# 年度工作总结

本目录存放年度工作总结文档。

## 📋 当前文档

- **2024年度工作总结_刘浩洋.md** - 2024年度工作总结（Markdown源文件）
- **2024年度工作总结_刘浩洋_20251130_115736.pdf** - 已生成的PDF版本

## 🚀 使用SKILLS快速转换

### 方式一：使用项目根目录的转换工具

```bash
# 回到项目根目录
cd /Users/fistclark/Desktop/03-enterprise-meeting-formatter

# 转换为PDF（企业主题）
python3 run.py work-summaries/annual/2024年度工作总结_刘浩洋.md --theme enterprise

# 转换为PDF（学术主题）
python3 run.py work-summaries/annual/2024年度工作总结_刘浩洋.md --theme academic
```

### 方式二：使用Claude Skills

如果项目中集成了Claude Skills（markdown-pdf-converter），可以直接在对话中使用：

```
请使用markdown-pdf-converter技能转换这个文件：
work-summaries/annual/2024年度工作总结_刘浩洋.md
```

### 方式三：批量转换

```bash
# 转换annual目录下所有Markdown文件
cd /Users/fistclark/Desktop/03-enterprise-meeting-formatter
python3 run.py --batch work-summaries/annual/
```

## 🎨 推荐主题

| 主题 | 适用场景 | 特点 |
|------|---------|------|
| **enterprise** | 年度总结汇报 | 专业商务风格，适合正式汇报 |
| **academic** | 学术性总结 | 传统学术风格，适合研究型工作 |
| **github** | 技术工作总结 | 现代技术风格，适合IT行业 |
| **minimal** | 简约总结 | 极简主义设计，突出内容 |

## 📝 文件命名规范

建议使用以下格式：

```
年度工作总结_姓名_YYYY.md
或
annual_YYYY_姓名.md
```

示例：
- `2024年度工作总结_刘浩洋.md`
- `annual_2024_刘浩洋.md`

## 🔧 高级选项

### 自定义页面设置

```bash
python3 run.py work-summaries/annual/2024年度工作总结_刘浩洋.md \
  --theme enterprise \
  --format A4 \
  --margin-top 20mm \
  --margin-bottom 20mm
```

### 使用YAML Front Matter

在Markdown文件开头添加配置：

```yaml
---
theme: enterprise
format: A4
margin_top: 20mm
margin_bottom: 20mm
margin_left: 15mm
margin_right: 15mm
---
```

## 📂 相关目录

- [工作总结主目录](../README.md)
- [月度总结](../monthly/)
- [项目总结](../project/)

---

**创建日期**: 2025-11-30
**维护者**: Claude AI Assistant
