# GitLens 中文翻译

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitLens](https://img.shields.io/badge/GitLens-v18.1.0-blue.svg)](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
[![Python](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/)

> GitLens VS Code 扩展的中文（简体）非官方翻译项目

## ⚠️ 免责声明

本项目是 [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) 扩展的**非官方**中文翻译，与 GitKraken 或 GitLens 官方团队无关。

- 本项目通过修改 GitLens 扩展的 `package.json` 和编译后的 JS 文件实现翻译
- 翻译仅影响界面显示，不影响 GitLens 的核心功能
- GitLens 更新后需要重新安装翻译
- 如遇问题请在本项目提交 Issue，不要向 GitLens 官方反馈

## 支持版本

- **GitLens v18.1.0**（当前）
- **GitLens v18.0.0**（兼容）
- 参考翻译来源：[1twol/gitlens-chinese](https://github.com/1twol/gitlens-chinese) (v17.0.3)

## 翻译覆盖率

| 类别 | 状态 |
|------|------|
| 扩展名称/描述 | ✅ 已翻译 |
| 设置分区标题 | ✅ 已翻译 |
| 命令标题 | ✅ 已翻译 |
| 设置描述 | ✅ 已翻译 |
| 视图标题 | ✅ 已翻译 |
| JS 运行时 UI 文本 | ✅ 已翻译（按钮、提示、标签等） |
| v18 新增内容 | ⚠️ 部分翻译 |

## 环境要求

- **Python 3.7+**
- **GitLens v18.1.0**（已安装在 VS Code / Cursor 中）

## 快速开始

### 安装翻译

**Windows：**
```bat
install.bat
```

**Linux / macOS：**
```bash
bash install.sh
```

**手动安装：**
```bash
# 1. 翻译 package.json（扩展配置、命令名、设置描述等）
python translate.py install

# 2. 翻译 JS 文件（运行时 UI 文本：按钮、提示、标签等）
python translate_js.py apply
```

安装后重启 VS Code / Cursor 即可生效。

### 恢复英文

**Windows：**
```bat
restore.bat
```

**Linux / macOS：**
```bash
bash restore.sh
```

**手动恢复：**
```bash
python translate.py restore
python translate_js.py restore
```

### 其他命令

```bash
# 查看翻译覆盖率统计
python translate.py stats
python translate_js.py stats

# 提取未翻译字符串
python translate.py extract
python translate_js.py extract

# 预览 JS 翻译效果（不实际修改文件）
python translate_js.py preview
```

## 项目结构

```
gitlens-zh-CN/
├── README.md                         # 本文件
├── LICENSE                           # MIT 许可证
├── .gitignore
│
├── translate.py                      # 主工具：package.json 翻译
├── translate_js.py                   # 主工具：JS 文件字符串替换
│
├── install.bat / install.sh          # 一键安装翻译
├── restore.bat / restore.sh          # 一键恢复英文
├── apply_js.bat / apply_js.sh        # 仅应用 JS 翻译
├── restore_js.bat / restore_js.sh    # 仅恢复 JS 文件
├── preview_js.bat                    # 预览 JS 替换效果
│
├── data/                             # 翻译数据
│   ├── package-v18-en.json           # GitLens v18 英文原版 package.json
│   ├── package-v18-zh-partial.json   # 部分翻译的 package.json
│   ├── package-v17-zh.json           # v17 完整翻译版（参考）
│   ├── contributions-zh.json         # 命令翻译参考
│   ├── js-translations.json          # JS 运行时翻译词典
│   └── webview-translations.json     # Webview UI 翻译词典
│
└── scripts/                          # 辅助脚本
    ├── apply_config_descriptions.py  # 应用配置描述翻译
    ├── apply_translations.py         # 基于索引的翻译应用
    ├── apply_visible_translations.py # 应用可见字段翻译
    ├── categorize_untranslated.py    # 分类未翻译字符串
    ├── extract_*.py                  # 各类提取工具
    ├── find_untranslated_*.py        # 查找未翻译内容
    ├── fix_command_titles.py         # 修复命令标题翻译
    ├── generate_webview_translations.py  # 生成 Webview 翻译词典
    ├── list_*.py                     # 列表查看工具
    ├── test_roundtrip.py             # JSON 序列化测试
    └── verify_apply.py               # 验证翻译应用
```

## 翻译原理

本项目采用**双管齐下**的翻译策略：

### 1. package.json 替换

替换 GitLens 扩展的 `package.json` 文件，翻译其中的：
- 扩展名称和描述（市场展示信息）
- 命令标题（`Ctrl+Shift+P` 命令面板中的文字）
- 设置项标签和描述（设置界面中的文字）
- 视图标题（侧边栏面板标题）

### 2. JS 文件字符串替换

对编译后的 JS 文件（`dist/gitlens.js`、`dist/webviews/*.js`）进行字符串替换，翻译：
- 按钮文字
- 工具提示（tooltip）
- 状态栏文本
- 对话框内容
- Webview 界面文字

替换策略基于字符串长度分级：
- **长字符串**（≥10 字符）：直接精确替换
- **中等字符串**（3-9 字符）：仅在 UI 属性上下文中替换
- **短字符串**（<3 字符）：跳过，避免误替换

## 工作流程

### 贡献翻译

#### 1. 提取未翻译字符串

```bash
python translate.py extract        # package.json 中的未翻译内容
python translate_js.py extract     # JS 文件中的未翻译内容
```

#### 2. 翻译字符串

翻译 `package.json` 内容：编辑 `data/package-v18-zh-partial.json`

翻译 JS 运行时内容：编辑 `data/js-translations.json` 或 `data/webview-translations.json`

#### 3. 安装并验证

```bash
python translate.py install && python translate_js.py apply
# 重启 VS Code 验证翻译效果
```

### 添加新的 JS 翻译词条

在 `data/js-translations.json`（主界面）或 `data/webview-translations.json`（Webview 界面）中添加：

```json
{
    "英文原文": "中文翻译"
}
```

然后运行 `python translate_js.py apply` 应用。

## 翻译规范

### 命令标题

- 使用动词开头
- 保持简洁
- 示例：
  - `Create Branch...` → `创建分支...`
  - `Delete Branch...` → `删除分支...`
  - `Compare with HEAD` → `与 HEAD 比较`

### 设置描述

- 使用"指定..."开头
- 保持技术准确性
- 示例：
  - `Specifies whether to enable...` → `指定是否启用...`
  - `Specifies the format of...` → `指定...的格式`

### 术语对照

| 英文 | 中文 |
|------|------|
| Blame | 责任归属 |
| Commit | 提交 |
| Branch | 分支 |
| Merge | 合并 |
| Rebase | 变基 |
| Stash | 暂存 |
| Tag | 标签 |
| Remote | 远程 |
| Repository | 仓库/存储库 |
| Pull Request | 拉取请求 |
| Worktree | 工作树 |
| CodeLens | 代码透镜 |
| Annotation | 注释/注解 |
| Revision | 修订版 |
| Upstream | 上游 |
| Downstream | 下游 |

## 参考项目

- [ChinaGodMan/gitlens-zh-CN](https://github.com/ChinaGodMan/gitlens-zh-CN) — v15.2.3 翻译
- [1twol/gitlens-chinese](https://github.com/1twol/gitlens-chinese) — v17.0.3 翻译

## 注意事项

1. **GitLens 更新会覆盖翻译** — 每次更新后需要重新运行安装脚本
2. **备份原文件** — 安装翻译时会自动备份原文件（`*.backup`）
3. **重启 VS Code** — 安装或恢复翻译后需要重启才能生效
4. **多编辑器支持** — 支持 VS Code、Cursor、VS Code Server

## 贡献

欢迎提交翻译改进！

1. Fork 本项目
2. 修改翻译文件（`data/` 目录下的 JSON 文件）
3. 测试翻译效果
4. 提交 Pull Request

### 报告问题

如遇翻译问题（错译、漏译、显示异常），请提交 Issue 并附上：
- GitLens 版本
- 编辑器类型（VS Code / Cursor）
- 问题截图
- 期望的正确翻译

## 许可证

本项目基于 [MIT 许可证](LICENSE) 发布。

GitLens 是 [GitKraken](https://www.gitkraken.com/) 的注册商标。本项目与 GitKraken 无关。
