# 脚本说明

## 可用脚本

### convert.sh

单文件转换脚本

**用法:**
```bash
./scripts/convert.sh document.md
./scripts/convert.sh document.md enterprise
```

**功能:**
- 使用内置 PDF 转换器（不依赖外部 md2pdf）
- 自动检测并按需安装依赖（markdown/pyppeteer/pygments）
- 主题参数（github/enterprise）

---

### batch-convert.sh

批量转换脚本

**用法:**
```bash
./scripts/batch-convert.sh              # 使用默认 github 主题
./scripts/batch-convert.sh enterprise   # 使用企业主题
```

**功能:**
- 转换当前目录所有 .md 文件
- 支持指定主题
- 自动检查依赖

---

### check-env.sh

环境检查脚本

**用法:**
```bash
./scripts/check-env.sh
```

**检查项:**
- ✅ Python 3 安装
- ✅ pip 安装
- ✅ 生成器依赖（PyYAML/Jinja2）
- ✅ 内置转换依赖（markdown/pyppeteer/pygments）

---

## 依赖要求

所有脚本都需要:
- Python 3.7+
- pip
- markdown / pyppeteer / pygments（按需自动安装）

---

## 故障排除

### 脚本无法执行

```bash
chmod +x scripts/*.sh
```

更多问题请查看 `docs/troubleshooting.md`。
