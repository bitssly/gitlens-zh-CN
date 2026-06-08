"""
fix_command_titles.py
=====================

Fix the command title misalignment in `data/package-v18-zh-partial.json`.

Background
----------
A previous batch script (`apply_translations.py`) used array-index keys to
overwrite command titles, but the indices were off, so many `title` fields in
`contributes.commands[]` ended up on the wrong commands.

Strategy
--------
Use **command ID** (the `command` field) as the only anchor. For every command
in the English source we determine the correct Chinese translation from
multiple reference sources (in priority order):

1. ``data/contributions-zh.json`` ``commands.<id>.label``  (primary, recent)
2. ``data/package-v17-zh.json``  ``contributes.commands[].title``
3. The same maps but keyed by the *base* id, i.e. without ``:scope`` suffix
   (e.g. ``gitlens.foo:graph`` falls back to ``gitlens.foo``)
4. Hard-coded translations for new v18 titles (see ``MANUAL_TRANSLATIONS``)

For every entry in ``contributes.commands`` of the partial Chinese file we
locate the JSON object by its ``"command": "<id>"`` marker, find the
adjacent ``"title": "..."`` value inside the same object, and overwrite it
with the resolved Chinese title using direct text replacement (so TAB
indentation and field order are preserved).

Only ``contributes.commands[].title`` fields are touched. Everything else
(including ``contributes.configuration``) is left untouched.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_PATH = ROOT / 'data' / 'package-v18-en.json'
ZH_PATH = ROOT / 'data' / 'package-v18-zh-partial.json'
V17_PATH = ROOT / 'data' / 'package-v17-zh.json'
CONTRIB_PATH = ROOT / 'data' / 'contributions-zh.json'

# ---------------------------------------------------------------------------
# Manual translations for new v18 titles that have no counterpart in
# `package-v17-zh.json` or `contributions-zh.json`.
#
# Keyed by the *exact* English title text (without any icon prefix; v18 EN
# titles do not contain inline `$(icon)` markup).
# ---------------------------------------------------------------------------
MANUAL_TRANSLATIONS: dict[str, str] = {
    'Abort': '中止',
    'Abort Rebase': '中止变基',
    'Add to Favorites': '添加到收藏',
    'Apply a Stash...': '应用贮藏...',
    'Ascending': '升序',
    'Change Upstream...': '更改上游...',
    'Close Welcome': '关闭欢迎页',
    'Compare Pull Request': '比较拉取请求',
    'Compose Commits (Preview)...': '组合提交（预览）...',
    'Configure Inline Blame': '配置行内责任归属',
    'Connect GitKraken MCP to More Agents...': '将 GitKraken MCP 连接到更多代理...',
    'Connect Integration': '连接集成',
    'Continue': '继续',
    'Create Branch...': '创建分支...',
    'Create Pull Request...': '创建拉取请求...',
    'Delete Worktree...': '删除工作树...',
    'Descending': '降序',
    'Detach File History View': '分离文件历史视图',
    'Disable Interactive Editor': '禁用交互式编辑器',
    'Disable Interactive Rebase Editor': '禁用交互式变基编辑器',
    'Drop Stash...': '丢弃贮藏...',
    'Drop Stashes...': '丢弃多个贮藏...',
    'Enable AI Features...': '启用 AI 功能...',
    'Enable Interactive Editor': '启用交互式编辑器',
    'Enable Interactive Rebase Editor': '启用交互式变基编辑器',
    'Explain Branch Changes (Preview)': 'AI 解释分支更改（预览）',
    'Explain Branch Changes (Preview)...': 'AI 解释分支更改（预览）...',
    'Explain Changes (Preview)': 'AI 解释更改（预览）',
    'Explain Commit Changes (Preview)...': 'AI 解释提交更改（预览）...',
    'Explain Stash Changes (Preview)...': 'AI 解释贮藏更改（预览）...',
    'Explain Unpushed Changes (Preview)': 'AI 解释未推送更改（预览）',
    'Explain Working Changes (Preview)': 'AI 解释工作区更改（预览）',
    'Explain Working Changes (Preview)...': 'AI 解释工作区更改（预览）...',
    'Fetch': '获取',
    'File History': '文件历史',
    'File History View Options': '文件历史视图选项',
    'Filter Repositories...': '筛选仓库...',
    'Generate Changelog (Preview)...': '生成变更日志（预览）...',
    'Git Add Remote...': 'Git 添加远程...',
    'Git Branch...': 'Git 分支...',
    'Git Change Branch Merge Target...': 'Git 更改分支合并目标...',
    'Git Change Branch Upstream...': 'Git 更改分支上游...',
    'Git Checkout...': 'Git 检出...',
    'Git Cherry Pick...': 'Git 拣选...',
    'Git Copy Working Changes to Worktree...': 'Git 复制工作区更改到工作树...',
    'Git Create Branch...': 'Git 创建分支...',
    'Git Create Tag...': 'Git 创建标签...',
    'Git Create Worktree...': 'Git 创建工作树...',
    'Git Delete Branch...': 'Git 删除分支...',
    'Git Delete Tag...': 'Git 删除标签...',
    'Git Delete Worktree...': 'Git 删除工作树...',
    'Git Drop Stash...': 'Git 丢弃贮藏...',
    'Git History (log)...': 'Git 历史 (log)...',
    'Git Merge...': 'Git 合并...',
    'Git Open Worktree...': 'Git 打开工作树...',
    'Git Pop Stash...': 'Git 弹出贮藏...',
    'Git Prune Branches...': 'Git 修剪分支...',
    'Git Prune Remote...': 'Git 修剪远程...',
    'Git Push Stash...': 'Git 推送贮藏...',
    'Git Rebase...': 'Git 变基...',
    'Git Remote...': 'Git 远程...',
    'Git Remove Remote...': 'Git 移除远程...',
    'Git Rename Branch...': 'Git 重命名分支...',
    'Git Rename Stash...': 'Git 重命名贮藏...',
    'Git Reset...': 'Git 重置...',
    'Git Revert...': 'Git 还原...',
    'Git Show...': 'Git 显示...',
    'Git Stash List...': 'Git 贮藏列表...',
    'Git Stash...': 'Git 贮藏...',
    'Git Status...': 'Git 状态...',
    'Git Switch to...': 'Git 切换到...',
    'Git Tag...': 'Git 标签...',
    'Git Worktree...': 'Git 工作树...',
    'Group All Views': '分组所有视图',
    'Group Branches View': '分组分支视图',
    'Group Commits View': '分组提交视图',
    'Group Contributors View': '分组贡献者视图',
    'Group File History View': '分组文件历史视图',
    'Group Launchpad View': '分组启动面板视图',
    'Group Remotes View': '分组远程视图',
    'Group Repositories View': '分组仓库视图',
    'Group Search & Compare View': '分组搜索和比较视图',
    'Group Stashes View': '分组贮藏视图',
    'Group Tags View': '分组标签视图',
    'Group Worktrees View': '分组工作树视图',
    'Group into GitLens View': '分组到 GitLens 视图',
    'Helpful': '有帮助',
    'Hide Branch Comparison': '隐藏分支比较',
    'Hide Branches': '隐藏分支',
    'Hide Commits': '隐藏提交',
    'Hide Contributors': '隐藏贡献者',
    'Hide Current Branch Status': '隐藏当前分支状态',
    'Hide File History View': '隐藏文件历史视图',
    'Hide Remotes': '隐藏远程',
    'Hide Stashes': '隐藏贮藏',
    'Hide Stashes on Branches': '隐藏分支上的贮藏',
    'Hide Tags': '隐藏标签',
    'Hide Working Tree Markers': '隐藏工作树标记',
    'Hide Worktrees': '隐藏工作树',
    'Install Claude Hooks': '安装 Claude 钩子',
    'Install GitKraken MCP Server': '安装 GitKraken MCP 服务器',
    'Maximize': '最大化',
    'Open AI Agent Session': '打开 AI 代理会话',
    'Open File History': '打开文件历史',
    'Open File History in Commit Graph': '在提交图中打开文件历史',
    'Open File at Revision from Remote': '从远程打开修订版文件',
    'Open Folder History': '打开文件夹历史',
    'Open Folder History in Commit Graph': '在提交图中打开文件夹历史',
    'Open Issue on Remote': '在远程打开议题',
    'Open Logs': '打开日志',
    'Open Pull Request': '打开拉取请求',
    'Open Pull Request Changes': '打开拉取请求更改',
    'Open Visual File History': '打开可视化文件历史',
    'Open Visual Folder History': '打开可视化文件夹历史',
    'Open Worktree': '打开工作树',
    'Open Worktree in New Window': '在新窗口中打开工作树',
    'Open Worktrees in New Window': '在新窗口中打开工作树',
    'Open in Integrated Terminal': '在集成终端中打开',
    'Open in New Window': '在新窗口中打开',
    'Open in Rebase Editor': '在变基编辑器中打开',
    'Pin Branch to Edge': '将分支固定到边缘',
    'Prune': '修剪',
    'Publish Branch': '发布分支',
    'Recompose Commits (Preview)': '重新组合提交（预览）',
    'Recompose Commits (Preview)...': '重新组合提交（预览）...',
    'Recompose Commits From Here (Preview)': '从此处重新组合提交（预览）',
    'Recompose Commits From Here (Preview)...': '从此处重新组合提交（预览）...',
    'Recompose Selected Commits (Preview)': '重新组合选中的提交（预览）',
    'Recompose Selected Commits (Preview)...': '重新组合选中的提交（预览）...',
    'Refresh': '刷新',
    'Refresh Account': '刷新账户',
    'Regenerate': '重新生成',
    'Reinstall GitKraken MCP Server': '重新安装 GitKraken MCP 服务器',
    'Remove Remote': '移除远程',
    'Remove Remote...': '移除远程...',
    'Remove from Favorites': '从收藏中移除',
    'Rename Stash...': '重命名贮藏...',
    'Reset All Views': '重置所有视图',
    'Restore Changes (Checkout)': '还原更改（检出）',
    'Restore Previous Changes': '还原先前更改',
    'Reveal in File Explorer': '在文件资源管理器中展示',
    'Review Changes (Preview)...': '审阅更改（预览）...',
    'Set Upstream...': '设置上游...',
    'Set as Default': '设为默认',
    'Set as Default View': '设为默认视图',
    'Setup Commit Signing...': '设置提交签名...',
    'Show Branch Comparison': '显示分支比较',
    'Show Branches': '显示分支',
    'Show Commits': '显示提交',
    'Show Contributors': '显示贡献者',
    'Show Current Branch Status': '显示当前分支状态',
    'Show File History View': '显示文件历史视图',
    'Show Remotes': '显示远程',
    'Show Stashes': '显示贮藏',
    'Show Stashes on Branches': '显示分支上的贮藏',
    'Show Tags': '显示标签',
    'Show Welcome View': '显示欢迎视图',
    'Show Working Tree Markers': '显示工作树标记',
    'Show Worktrees': '显示工作树',
    'Simulate AI Provider (Debugging)': '模拟 AI 提供商（调试）',
    'Simulate Subscription (Debugging)': '模拟订阅（调试）',
    'Skip': '跳过',
    'Solo Branch': '独占分支',
    'Solo Branch in Commit Graph': '在提交图中独占分支',
    'Solo Tag': '独占标签',
    'Solo Tag in Commit Graph': '在提交图中独占标签',
    'Sort Branches by Date': '按日期排序分支',
    'Sort Branches by Name': '按名称排序分支',
    'Sort by Count': '按数量排序',
    'Sort by Date': '按日期排序',
    'Sort by Discovery Time': '按发现时间排序',
    'Sort by Last Fetched': '按最近获取时间排序',
    'Sort by Name': '按名称排序',
    'Sort by Score': '按评分排序',
    'Stage Current Changes': '暂存当前更改',
    'Stage Incoming Changes': '暂存传入更改',
    'Start PR Review': '开始 PR 审查',
    'Start PR Review with Agent': '使用代理开始 PR 审查',
    'Start Work with Agent': '使用代理开始工作',
    'Start/Continue Rebase': '开始/继续变基',
    'Stash Changes...': '贮藏更改...',
    'Stash Staged Changes...': '贮藏已暂存的更改...',
    'Stash Unstaged Changes...': '贮藏未暂存的更改...',
    'Switch AI Provider/Model...': '切换 AI 提供商/模型...',
    'Switch Branch...': '切换到分支...',
    'Switch Default Agent...': '切换默认代理...',
    'Switch GitLens AI Provider/Model...': '切换 GitLens AI 提供商/模型...',
    'Switch to Branch...': '切换到分支...',
    'Switch to Interactive Editor': '切换到交互式编辑器',
    'Switch to Text Editor': '切换到文本编辑器',
    'Unhelpful': '没帮助',
    'Uninstall Claude Hooks': '卸载 Claude 钩子',
    'Unpin Branch from Edge': '从边缘取消固定分支',
    'Unset as Default': '取消设为默认',
    'View Commits': '查看提交',
    'View Contributors': '查看贡献者',
    'Visualize Repository History': '可视化仓库历史',
}


def load_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def build_reference_map() -> dict[str, str]:
    """Return command_id -> Chinese title from existing reference files."""
    contrib = load_json(CONTRIB_PATH)
    v17 = load_json(V17_PATH)

    ref: dict[str, str] = {}
    # contributions-zh wins (newer / higher quality)
    for cid, body in contrib.get('commands', {}).items():
        label = body.get('label')
        if label:
            ref[cid] = label
    # v17 fills holes
    for c in v17.get('contributes', {}).get('commands', []):
        cid = c.get('command')
        title = c.get('title')
        if cid and title and cid not in ref:
            ref[cid] = title
    return ref


def base_id(cmd_id: str) -> str:
    """Strip the ``:scope`` suffix used by v18 to disambiguate menu variants."""
    return cmd_id.split(':', 1)[0]


def resolve_chinese(cmd_id: str, en_title: str, ref: dict[str, str]) -> str | None:
    """Resolve the correct Chinese title for ``cmd_id``."""
    # 1. Direct command-id hit
    if cmd_id in ref:
        return ref[cmd_id]
    # 2. Strip :scope suffix
    bid = base_id(cmd_id)
    if bid != cmd_id and bid in ref:
        return ref[bid]
    # 3. Fall back to manual map keyed by English title
    if en_title in MANUAL_TRANSLATIONS:
        return MANUAL_TRANSLATIONS[en_title]
    return None


def replace_title_in_block(raw: str, cmd_id: str, new_title: str) -> tuple[str, str | None]:
    """Locate the ``contributes.commands`` entry whose ``command`` is ``cmd_id``
    and rewrite its ``title`` to ``new_title``.

    Returns the (possibly modified) raw text and the previous title (or None if
    no change was made).
    """
    # The unique anchor: "command": "<cmd_id>", (a literal trailing comma
    # disambiguates `gitlens.foo` from `gitlens.foo:graph`, etc.).
    anchor = f'"command": "{cmd_id}",'
    idx = raw.find(anchor)
    if idx == -1:
        return raw, None

    # Find the enclosing JSON object: walk backward to the nearest '{'.
    obj_start = idx
    while obj_start > 0 and raw[obj_start] != '{':
        obj_start -= 1

    # Find the matching '}' (depth-aware, ignoring braces inside strings).
    depth = 0
    in_string = False
    escape = False
    obj_end = obj_start
    while obj_end < len(raw):
        ch = raw[obj_end]
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    break
        obj_end += 1
    if obj_end >= len(raw):
        return raw, None

    block = raw[obj_start:obj_end + 1]

    # Match the title field inside this block. The value may contain any
    # characters except an unescaped quote.
    m = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', block)
    if not m:
        return raw, None

    old_title = m.group(1)
    if old_title == new_title:
        return raw, old_title  # already correct, no change but return for stats

    # JSON-escape new_title (titles in this project are plain text, but be safe)
    encoded_new = json.dumps(new_title, ensure_ascii=False)  # includes quotes
    new_block = block[:m.start()] + f'"title": {encoded_new}' + block[m.end():]
    raw = raw[:obj_start] + new_block + raw[obj_end + 1:]
    return raw, old_title


def main() -> int:
    en = load_json(EN_PATH)
    en_cmds = en['contributes']['commands']

    ref = build_reference_map()
    raw = ZH_PATH.read_text(encoding='utf-8')

    fixed = 0
    unchanged = 0
    unresolved: list[tuple[str, str]] = []  # (cmd_id, en_title)
    not_found: list[str] = []

    for cmd in en_cmds:
        cid = cmd.get('command')
        en_title = cmd.get('title', '')
        if not cid:
            continue
        zh_title = resolve_chinese(cid, en_title, ref)
        if zh_title is None:
            unresolved.append((cid, en_title))
            continue

        new_raw, old = replace_title_in_block(raw, cid, zh_title)
        if old is None:
            not_found.append(cid)
            continue
        if old == zh_title:
            unchanged += 1
        else:
            fixed += 1
        raw = new_raw

    ZH_PATH.write_text(raw, encoding='utf-8')

    # Verify the JSON still parses
    try:
        json.loads(raw)
        print('JSON validation: OK')
    except json.JSONDecodeError as exc:
        print(f'JSON validation: FAILED -> {exc}')
        return 1

    print(f'Fixed     : {fixed}')
    print(f'Unchanged : {unchanged}')
    print(f'Not found : {len(not_found)}')
    print(f'Unresolved: {len(unresolved)}')
    if unresolved:
        print('  examples:')
        for cid, t in unresolved[:15]:
            print(f'    - {cid}: {t!r}')
    if not_found:
        print('  not-found examples:')
        for cid in not_found[:10]:
            print(f'    - {cid}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
