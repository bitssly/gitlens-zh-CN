# GitLens 中文翻译

> GitLens VS Code 扩展的中文（简体）翻译项目

## 支持版本

- GitLens v18.0.0（当前）
- 参考翻译来源：[1twol/gitlens-chinese](https://github.com/1twol/gitlens-chinese) (v17.0.3)

## 翻译覆盖率

| 类别 | 状态 |
|------|------|
| 扩展名称/描述 | ✅ 已翻译 |
| 设置分区标题 | ✅ 已翻译 |
| 命令标题 | ✅ 已翻译 |
| 设置描述 | ✅ 已翻译 |
| 视图标题 | ✅ 已翻译 |
| v18 新增内容 | ⚠️ 部分翻译 |

## 快速开始

### 安装翻译

```bash
python translate.py install
```

### 恢复英文

```bash
python translate.py restore
```

### 查看统计

```bash
python translate.py stats
```

### 提取未翻译字符串

```bash
python translate.py extract
```

## 项目结构

```
gitlens-zh-CN/
├── README.md                 # 本文件
├── translate.py              # 翻译工具脚本
├── data/
│   ├── package-v18-en.json   # GitLens v18 英文原版
│   ├── package-v18-zh-partial.json  # 部分翻译版
│   ├── package-v17-zh.json   # v17 完整翻译版（参考）
│   └── contributions-zh.json # 命令翻译（参考）
└── output/
    ├── untranslated.json     # 未翻译字符串（JSON）
    ├── untranslated.txt      # 未翻译字符串（可读文本）
    └── translations.json     # 翻译映射
```

## 工作流程

### 1. 提取未翻译字符串

```bash
python translate.py extract
```

这会在 `output/` 目录生成：
- `untranslated.json` — 未翻译字符串的 JSON 格式
- `untranslated.txt` — 未翻译字符串的可读文本格式

### 2. 翻译字符串

打开 `output/untranslated.txt`，参考格式进行翻译。

翻译格式示例：
```json
{
    "contributes.commands.gitlens.newCommand.title": "新命令标题",
    "contributes.configuration[0].properties.gitlens.newSetting.markdownDescription": "新设置的描述"
}
```

### 3. 更新翻译

将翻译后的字符串添加到 `data/package-v18-zh-partial.json` 中对应的位置。

### 4. 应用翻译

```bash
python translate.py install
```

### 5. 验证翻译

重启 VS Code，检查翻译是否生效。

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

1. **GitLens 更新会覆盖翻译** — 每次更新后需要重新运行 `python translate.py install`
2. **备份原文件** — 安装翻译时会自动备份原文件到 `package.json.backup`
3. **重启 VS Code** — 安装或恢复翻译后需要重启 VS Code 才能生效

## 贡献

欢迎提交翻译改进！请按照以下步骤：

1. Fork 本项目
2. 修改翻译文件
3. 提交 Pull Request

## 许可证

本项目基于 MIT 许可证发布。
