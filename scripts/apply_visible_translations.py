#!/usr/bin/env python3
"""
将用户可见字段的中文翻译应用到 data/package-v18-zh-partial.json
使用完整路径作为 key 进行精确定位（不依赖数组索引猜测）。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
ZH = DATA / "package-v18-zh-partial.json"

# 路径 -> 中文翻译
TRANSLATIONS = {
    # ========== 视图分组（grouped views） ==========
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.commits.description":
        "对“提交”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.worktrees.description":
        "对“工作树”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.branches.description":
        "对“分支”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.remotes.description":
        "对“远程”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.stashes.description":
        "对“贮藏”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.tags.description":
        "对“标签”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.contributors.description":
        "对“贡献者”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.repositories.description":
        "对“仓库”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.fileHistory.description":
        "对“文件历史”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.launchpad.description":
        "对“启动面板”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.views.properties.searchAndCompare.description":
        "对“搜索与比较”视图进行分组",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.commits.description":
        "隐藏“提交”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.worktrees.description":
        "隐藏“工作树”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.branches.description":
        "隐藏“分支”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.remotes.description":
        "隐藏“远程”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.stashes.description":
        "隐藏“贮藏”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.tags.description":
        "隐藏“标签”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.contributors.description":
        "隐藏“贡献者”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.repositories.description":
        "隐藏“仓库”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.fileHistory.description":
        "隐藏“文件历史”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.launchpad.description":
        "隐藏“启动面板”视图",
    "contributes.configuration[11].properties.gitlens.views.scm.grouped.hiddenViews.properties.searchAndCompare.description":
        "隐藏“搜索与比较”视图",

    # ========== 已弃用消息（views formats） ==========
    "contributes.configuration[11].properties.gitlens.views.commitFileFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.files.label`",
    "contributes.configuration[11].properties.gitlens.views.commitFileFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.files.label#`",
    "contributes.configuration[11].properties.gitlens.views.commitFileDescriptionFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.files.description`",
    "contributes.configuration[11].properties.gitlens.views.commitFileDescriptionFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.files.description#`",
    "contributes.configuration[11].properties.gitlens.views.commitFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.commits.label`",
    "contributes.configuration[11].properties.gitlens.views.commitFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.commits.files.label#`",
    "contributes.configuration[11].properties.gitlens.views.commitDescriptionFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.commits.description`",
    "contributes.configuration[11].properties.gitlens.views.commitDescriptionFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.commits.description#`",
    "contributes.configuration[11].properties.gitlens.views.stashFileFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.files.label`",
    "contributes.configuration[11].properties.gitlens.views.stashFileFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.files.label#`",
    "contributes.configuration[11].properties.gitlens.views.stashFileDescriptionFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.files.description`",
    "contributes.configuration[11].properties.gitlens.views.stashFileDescriptionFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.files.description#`",
    "contributes.configuration[11].properties.gitlens.views.stashFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.stashes.label`",
    "contributes.configuration[11].properties.gitlens.views.stashFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.stashes.files.label#`",
    "contributes.configuration[11].properties.gitlens.views.stashDescriptionFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.stashes.description`",
    "contributes.configuration[11].properties.gitlens.views.stashDescriptionFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.stashes.description#`",
    "contributes.configuration[11].properties.gitlens.views.statusFileFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.files.label`",
    "contributes.configuration[11].properties.gitlens.views.statusFileFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.files.label#`",
    "contributes.configuration[11].properties.gitlens.views.statusFileDescriptionFormat.deprecationMessage":
        "已弃用。请改用 `gitlens.views.formats.files.description`",
    "contributes.configuration[11].properties.gitlens.views.statusFileDescriptionFormat.markdownDeprecationMessage":
        "已弃用。请改用 `#gitlens.views.formats.files.description#`",
    "contributes.configuration[16].properties.gitlens.views.repositories.enabled.deprecationMessage":
        "已弃用。此设置不再使用",
    "contributes.configuration[16].properties.gitlens.views.repositories.enabled.markdownDeprecationMessage":
        "已弃用。此设置不再使用",
    "contributes.configuration[19].properties.gitlens.views.lineHistory.enabled.deprecationMessage":
        "已弃用。此设置不再使用",
    "contributes.configuration[19].properties.gitlens.views.lineHistory.enabled.markdownDeprecationMessage":
        "已弃用。此设置不再使用",

    # ========== 图（minimap / scrollMarkers） ==========
    "contributes.configuration[8].properties.gitlens.graph.minimap.additionalTypes.items.enumDescriptions[5]":
        "标记其他工作树的位置（每个工作树检出的位置）",
    "contributes.configuration[8].properties.gitlens.graph.scrollMarkers.additionalTypes.items.enumDescriptions[5]":
        "标记工作树（WIP）行的位置",

    # ========== Launchpad indicator groups ==========
    "contributes.configuration[9].properties.gitlens.launchpad.indicator.groups.items.enumDescriptions[0]":
        "显示可合并的拉取请求",
    "contributes.configuration[9].properties.gitlens.launchpad.indicator.groups.items.enumDescriptions[1]":
        "显示被阻塞的拉取请求",
    "contributes.configuration[9].properties.gitlens.launchpad.indicator.groups.items.enumDescriptions[2]":
        "显示需要您审查的拉取请求",
    "contributes.configuration[9].properties.gitlens.launchpad.indicator.groups.items.enumDescriptions[3]":
        "显示需要跟进的拉取请求",

    # ========== Git Commands skip confirmations ==========
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[0]":
        "在通过命令（如视图操作）执行时跳过分支创建确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[1]":
        "在通过 Git 命令面板执行时跳过分支创建确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[2]":
        "在通过命令（如视图操作）执行时跳过共同作者确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[3]":
        "在通过 Git 命令面板执行时跳过共同作者确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[4]":
        "在通过命令（如视图操作）执行时跳过获取确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[5]":
        "在通过 Git 命令面板执行时跳过获取确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[6]":
        "在通过命令（如视图操作）执行时跳过拉取确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[7]":
        "在通过 Git 命令面板执行时跳过拉取确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[8]":
        "在通过命令（如视图操作）执行时跳过推送确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[9]":
        "在通过 Git 命令面板执行时跳过推送确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[10]":
        "在通过命令（如视图操作）执行时跳过贮藏应用确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[11]":
        "在通过 Git 命令面板执行时跳过贮藏应用确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[12]":
        "在通过命令（如视图操作）执行时跳过贮藏弹出确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[13]":
        "在通过 Git 命令面板执行时跳过贮藏弹出确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[14]":
        "在通过命令（如视图操作）执行时跳过贮藏推入确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[15]":
        "在通过 Git 命令面板执行时跳过贮藏推入确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[16]":
        "在通过命令（如视图操作）执行时跳过切换确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[17]":
        "在通过 Git 命令面板执行时跳过切换确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[18]":
        "在通过命令（如视图操作）执行时跳过标签创建确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.skipConfirmations.items.enumDescriptions[19]":
        "在通过 Git 命令面板执行时跳过标签创建确认",
    "contributes.configuration[31].properties.gitlens.gitCommands.search.showResultsInView.deprecationMessage":
        "已弃用。此设置已重命名为 gitlens.gitCommands.search.showResultsInSideBar",
    "contributes.configuration[31].properties.gitlens.gitCommands.search.showResultsInView.markdownDeprecationMessage":
        "已弃用。此设置已重命名为 `#gitlens.gitCommands.search.showResultsInSideBar#`",

    # ========== Autolinks / Remotes (configuration[32]) ==========
    "contributes.configuration[32].properties.gitlens.autolinks.items.properties.prefix.description":
        "指定用于匹配以为外部资源生成自动链接的短前缀，例如 `GH-` 或 `JIRA-`",
    "contributes.configuration[32].properties.gitlens.autolinks.items.properties.title.description":
        "为生成的自动链接指定可选标题。使用 `<num>` 作为引用编号的变量",
    "contributes.configuration[32].properties.gitlens.autolinks.items.properties.url.description":
        "指定要链接到的外部资源的 URL。使用 `<num>` 作为引用编号的变量",
    "contributes.configuration[32].properties.gitlens.autolinks.items.properties.alphanumeric.description":
        "指定 `<num>` 中是否允许字母数字字符",
    "contributes.configuration[32].properties.gitlens.autolinks.items.properties.ignoreCase.description":
        "指定匹配前缀时是否忽略大小写",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.type.description":
        "指定自定义远程服务的类型",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.domain.description":
        "指定用于将此自定义配置匹配到 Git 远程的域名",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.regex.description":
        "指定用于将此自定义配置匹配到 Git 远程的正则表达式，并捕获“域名”和“路径”",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.name.description":
        "为自定义远程服务指定一个可选的友好名称",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.protocol.description":
        "为自定义远程服务指定一个可选的 URL 协议",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.ignoreSSLErrors.description":
        "指定连接远程服务时是否忽略无效 SSL 证书错误",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.repository.markdownDescription":
        "指定自定义远程服务的仓库 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.branches.markdownDescription":
        "指定自定义远程服务的分支列表 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${branch}` &mdash; 分支",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.branch.markdownDescription":
        "指定自定义远程服务的分支 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${branch}` &mdash; 分支",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.commit.markdownDescription":
        "指定自定义远程服务的提交 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${id}` &mdash; 提交 SHA",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.comparison.markdownDescription":
        "指定自定义远程服务的比较 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${ref1}` &mdash; 引用 1\\\n`${ref2}` &mdash; 引用 2\\\n`${notation}` &mdash; 符号",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.createPullRequest.markdownDescription":
        "指定自定义远程服务的创建拉取请求 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${base}` &mdash; 基础分支\\\n`${compare}` &mdash; 对比分支",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.file.markdownDescription":
        "指定自定义远程服务的文件 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${file}` &mdash; 文件名\\\n`${line}` &mdash; 已格式化的行信息",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.fileInBranch.markdownDescription":
        "指定自定义远程服务的分支内文件 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${file}` &mdash; 文件名\\\n`${branch}` &mdash; 分支\\\n`${line}` &mdash; 已格式化的行信息",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.fileInCommit.markdownDescription":
        "指定自定义远程服务的提交内文件 URL 格式\n\n可用变量\\\n`${repo}` &mdash; 仓库路径\\\n`${file}` &mdash; 文件名\\\n`${id}` &mdash; 提交 SHA\\\n`${line}` &mdash; 已格式化的行信息",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.fileLine.markdownDescription":
        "指定自定义远程服务中文件 URL 的行格式\n\n可用变量\\\n`${line}` &mdash; 行",
    "contributes.configuration[32].properties.gitlens.remotes.items.properties.urls.properties.fileRange.markdownDescription":
        "指定自定义远程服务中文件 URL 的范围格式\n\n可用变量\\\n`${start}` &mdash; 起始行\\\n`${end}` &mdash; 结束行",
    "contributes.configuration[32].properties.gitlens.partners.additionalProperties.properties.enabled.description":
        "指定是否显示合作伙伴集成",
    "contributes.configuration[32].properties.gitlens.partners.additionalProperties.description":
        "指定合作伙伴集成的配置",

    # ========== title ==========
    "contributes.configuration[35].title": "日期与时间",
    "contributes.configuration[41].title": "高级",
    "contributes.commands[874].title": "启动面板",
    # views container 标题保持英文
    "contributes.viewsContainers.activitybar[0].title": "GitLens",
    "contributes.viewsContainers.panel[0].title": "GitLens",

    # ========== Modes (configuration[39]) ==========
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.name.description":
        "指定此用户自定义模式的友好名称",
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.statusBarItemName.description":
        "指定当此用户自定义模式激活时显示在状态栏中的名称",
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.description.description":
        "指定此用户自定义模式的描述",
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.codeLens.description":
        "指定当此用户自定义模式激活时是否显示任何 Git 代码透镜",
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.currentLine.description":
        "指定当此用户自定义模式激活时是否在当前行显示内联责任归属注释",
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.hovers.description":
        "指定当此用户自定义模式激活时是否显示任何悬停",
    "contributes.configuration[39].properties.gitlens.modes.properties.zen.properties.statusBar.description":
        "指定当此用户自定义模式激活时是否在状态栏中显示责任归属信息",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.name.description":
        "指定此用户自定义模式的友好名称",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.statusBarItemName.description":
        "指定当此用户自定义模式激活时显示在状态栏中的名称",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.description.description":
        "指定此用户自定义模式的描述",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.codeLens.description":
        "指定当此用户自定义模式激活时是否显示任何 Git 代码透镜",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.currentLine.description":
        "指定当此用户自定义模式激活时是否在当前行显示内联责任归属注释",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.hovers.description":
        "指定当此用户自定义模式激活时是否显示任何悬停",
    "contributes.configuration[39].properties.gitlens.modes.properties.review.properties.statusBar.description":
        "指定当此用户自定义模式激活时是否在状态栏中显示责任归属信息",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.name.description":
        "指定此用户自定义模式的友好名称",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.statusBarItemName.description":
        "指定当此用户自定义模式激活时显示在状态栏中的名称",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.description.description":
        "指定此用户自定义模式的描述",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.annotations.enumDescriptions[0]":
        "显示文件责任归属注释",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.annotations.enumDescriptions[1]":
        "显示文件变更注释",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.annotations.enumDescriptions[2]":
        "显示文件热力图注释",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.annotations.description":
        "指定当此用户自定义模式激活时显示哪些（如果有）文件注释",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.codeLens.description":
        "指定当此用户自定义模式激活时是否显示任何 Git 代码透镜",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.currentLine.description":
        "指定当此用户自定义模式激活时是否在当前行显示内联责任归属注释",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.hovers.description":
        "指定当此用户自定义模式激活时是否显示任何悬停",
    "contributes.configuration[39].properties.gitlens.modes.additionalProperties.properties.statusBar.description":
        "指定当此用户自定义模式激活时是否在状态栏中显示责任归属信息",
    "contributes.configuration[39].properties.gitlens.modes.default.zen.name": "禅模式",
    "contributes.configuration[39].properties.gitlens.modes.default.zen.statusBarItemName": "禅模式",
    "contributes.configuration[39].properties.gitlens.modes.default.zen.description":
        "提供禅意般的体验，禁用许多视觉功能",
    "contributes.configuration[39].properties.gitlens.modes.default.review.name": "审查",
    "contributes.configuration[39].properties.gitlens.modes.default.review.statusBarItemName": "审查中",
    "contributes.configuration[39].properties.gitlens.modes.default.review.description":
        "用于审查代码，启用许多视觉功能",

    # ========== Advanced messages (configuration[41]) ==========
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressCommitHasNoPreviousCommitWarning.description":
        "提交无前置提交警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressCommitNotFoundWarning.description":
        "未找到提交警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressCreatePullRequestPrompt.description":
        "创建拉取请求提示",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressDebugLoggingWarning.description":
        "调试日志警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressFileNotUnderSourceControlWarning.description":
        "文件未纳入源代码控制警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressGitDisabledWarning.description":
        "Git 已禁用警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressGitMissingWarning.description":
        "Git 缺失警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressGitVersionWarning.description":
        "Git 版本警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressLineUncommittedWarning.description":
        "行未提交警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressNoRepositoryWarning.description":
        "无仓库警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressRebaseSwitchToTextWarning.description":
        "变基切换到文本警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressIntegrationDisconnectedTooManyFailedRequestsWarning.description":
        "集成已断开;失败请求过多警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressIntegrationRequestFailed500Warning.description":
        "集成请求失败（500 状态码）警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressIntegrationRequestTimedOutWarning.description":
        "集成请求超时警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressBlameInvalidIgnoreRevsFileWarning.description":
        "无效的责任归属 IgnoreRevs 文件警告",
    "contributes.configuration[41].properties.gitlens.advanced.messages.properties.suppressBlameInvalidIgnoreRevsFileBadRevisionWarning.description":
        "责任归属 IgnoreRevs 文件中存在无效修订版警告",

    # ========== Output / Insiders ==========
    "contributes.configuration[42].properties.gitlens.outputLevel.markdownDeprecationMessage":
        "此设置已弃用。请使用 **GitLens: 启用调试日志** 与 **GitLens: 禁用调试日志** 命令，或使用 **Developer: Set Log Level...** 命令来控制日志记录。",
    "contributes.configuration[42].properties.gitlens.insiders.deprecationMessage":
        "已弃用。请改用 GitLens 的预发布版本",
    "contributes.configuration[42].properties.gitlens.insiders.markdownDeprecationMessage":
        "已弃用。请改用 GitLens 的预发布版本",

    # ========== Colors descriptions ==========
    "contributes.colors[69].description":
        "指定优先级为“被阻塞”时 _启动面板_ 指示器图标的颜色",
    "contributes.colors[70].description":
        "指定优先级为“被阻塞”时悬停中 _启动面板_ 指示器图标的颜色",
    "contributes.colors[71].description":
        "指定优先级为“需要跟进”或“需要审查”时 _启动面板_ 指示器图标的颜色",
    "contributes.colors[72].description":
        "指定优先级为“需要跟进”或“需要审查”时悬停中 _启动面板_ 指示器图标的颜色",

    # ========== Icons descriptions ==========
    "contributes.icons.gitlens-history-view-filled.description": "history-view-filled 图标",
    "contributes.icons.gitlens-repository.description": "repository 图标",
    "contributes.icons.gitlens-worktree.description": "worktree 图标",
    "contributes.icons.gitlens-worktree-filled.description": "worktree-filled 图标",
    "contributes.icons.gitlens-repository-cloud.description": "repository-cloud 图标",
    "contributes.icons.gitlens-provider-linear.description": "provider-linear 图标",
    "contributes.icons.gitlens-diff-right.description": "diff-right 图标",
    "contributes.icons.gitlens-diff-left.description": "diff-left 图标",
    "contributes.icons.gitlens-accept-right.description": "accept-right 图标",
    "contributes.icons.gitlens-accept-left.description": "accept-left 图标",
    "contributes.icons.gitlens-accept-all-right.description": "accept-all-right 图标",
    "contributes.icons.gitlens-accept-all-left.description": "accept-all-left 图标",
    "contributes.icons.gitlens-continue.description": "continue 图标",
    "contributes.icons.gitlens-skip.description": "skip 图标",
    "contributes.icons.gitlens-abort.description": "abort 图标",
    "contributes.icons.gitlens-pause.description": "pause 图标",
    "contributes.icons.gitlens-kanban-view.description": "kanban-view 图标",

    # ========== Submenus labels ==========
    "contributes.submenus[48].label": "搜索与比较 (0)",
    "contributes.submenus[49].label": "贮藏 (5)",
    "contributes.submenus[50].label": "标签 (6)",
    "contributes.submenus[51].label": "显示 / 隐藏视图",
    "contributes.submenus[52].label": "工作树 (2)",
    "contributes.submenus[53].label": "分支排序方式",
    "contributes.submenus[54].label": "排序方式",
    "contributes.submenus[55].label": "排序方式",
    "contributes.submenus[56].label": "排序方式",
    "contributes.submenus[57].label": "文件夹历史",

    # ========== views.* contextualTitle 与 name (保持 GitLens) ==========
    "contributes.views.scm[0].contextualTitle": "GitLens",
    "contributes.views.scm[1].contextualTitle": "GitLens",
    "contributes.views.scm[2].contextualTitle": "GitLens",
    "contributes.views.scm[3].contextualTitle": "GitLens",
    "contributes.views.scm[4].contextualTitle": "GitLens",
    "contributes.views.scm[5].contextualTitle": "GitLens",
    "contributes.views.scm[6].contextualTitle": "GitLens",
    "contributes.views.scm[7].contextualTitle": "GitLens",
    "contributes.views.scm[8].name": "GitLens",
    "contributes.views.scm[8].contextualTitle": "GitLens",
    "contributes.views.gitlensInspect[0].contextualTitle": "GitLens",
    "contributes.views.gitlensInspect[1].contextualTitle": "GitLens",
    "contributes.views.gitlensInspect[2].contextualTitle": "GitLens",
    "contributes.views.gitlensInspect[3].contextualTitle": "GitLens",
    "contributes.views.gitlensInspect[4].contextualTitle": "GitLens",
    "contributes.views.gitlensInspect[5].contextualTitle": "GitLens",
    "contributes.views.gitlens[0].contextualTitle": "GitLens",
    "contributes.views.gitlens[1].contextualTitle": "GitLens",
    "contributes.views.gitlens[2].contextualTitle": "GitLens",
    "contributes.views.gitlens[3].contextualTitle": "GitLens",
    "contributes.views.gitlens[4].name": "云端工作区",
    "contributes.views.gitlens[4].contextualTitle": "GitLens",
    "contributes.views.gitlensPanel[0].contextualTitle": "GitLens",
    "contributes.views.gitlensPatch[0].contextualTitle": "GitLens",

    # ========== resourceLabelFormatters 保持原值 ==========
    "contributes.resourceLabelFormatters[0].formatting.label": "${path} (${query.ref})",
    "contributes.resourceLabelFormatters[1].formatting.label": "${query.label}",

    # ========== 其它 ==========
    "contributes.mcpServerDefinitionProviders[0].label": "GitKraken（GitLens 内置）",
}


def apply_recursive(obj, translations, path="", applied_set=None):
    """递归遵循 translate.py 的路径拼接方式（key 中可能包含 '.'）。"""
    if applied_set is None:
        applied_set = set()
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            current_path = f"{path}.{key}" if path else key
            value = obj[key]
            if isinstance(value, str) and current_path in translations:
                obj[key] = translations[current_path]
                applied_set.add(current_path)
            elif isinstance(value, list):
                for i in range(len(value)):
                    item_path = f"{current_path}[{i}]"
                    item = value[i]
                    if isinstance(item, str) and item_path in translations:
                        value[i] = translations[item_path]
                        applied_set.add(item_path)
                    elif isinstance(item, (dict, list)):
                        apply_recursive(item, translations, item_path, applied_set)
            elif isinstance(value, dict):
                apply_recursive(value, translations, current_path, applied_set)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            item_path = f"{path}[{i}]"
            item = obj[i]
            if isinstance(item, str) and item_path in translations:
                obj[i] = translations[item_path]
                applied_set.add(item_path)
            elif isinstance(item, (dict, list)):
                apply_recursive(item, translations, item_path, applied_set)
    return applied_set


def main():
    data = json.loads(ZH.read_text(encoding='utf-8'))
    applied_set = apply_recursive(data, TRANSLATIONS)
    applied = len(applied_set)
    missing = [p for p in TRANSLATIONS if p not in applied_set]
    # 写回，使用 TAB 缩进
    with open(ZH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent='\t')
        f.write('\n')
    print(f'已应用翻译: {applied}/{len(TRANSLATIONS)}')
    if missing:
        print(f'未匹配路径: {len(missing)}')
        for p in missing[:10]:
            print('  -', p)
    # JSON 合法性检查
    try:
        json.loads(ZH.read_text(encoding='utf-8'))
        print('JSON 合法性: OK')
    except Exception as e:
        print(f'JSON 解析失败: {e}')


if __name__ == '__main__':
    main()
