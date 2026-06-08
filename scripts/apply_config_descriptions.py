"""
Apply Chinese translations for markdownDescription/enumDescriptions/description fields
in contributes.configuration[*].properties.* of package-v18-zh-partial.json.

Map keys: (cfg_idx, prop_name, field, arr_idx).
Round-trip via json.load/json.dump(indent='\\t', ensure_ascii=False) is verified stable.
"""
import json
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_PATH = os.path.join(ROOT, 'data', 'package-v18-en.json')
ZH_PATH = os.path.join(ROOT, 'data', 'package-v18-zh-partial.json')

sys.stdout.reconfigure(encoding='utf-8')

# ---------- Reusable per-view translations ----------
# Files layout family - shared template across many views
def files_layout_descs(view_name):
    return {
        ('markdownDescription', None): f'指定 _{view_name}_ 视图如何显示文件',
        ('enumDescriptions', 0): f'根据 `#gitlens.views.{{key}}.files.threshold#` 设置和每个嵌套层级的文件数量，自动在以 `tree` 或 `list` 形式显示文件之间切换',
        ('enumDescriptions', 1): '以列表显示文件',
        ('enumDescriptions', 2): '以树状显示文件',
    }

FILE_ICON_DESC = '将文件状态显示为图标'
FILE_TYPE_ICON_DESC = '将文件类型（主题图标）显示为图标'

# ---------- Master translation map ----------
# Key: (cfg_idx, prop_name, field, arr_idx) → Chinese string
T = {}

# Helper to add files.layout/threshold/compact/icon set
def add_files_set(cfg_idx, prefix, view_name, key_for_threshold):
    # key_for_threshold is the gitlens.views.<X>.files.threshold path
    T[(cfg_idx, f'{prefix}.files.layout', 'markdownDescription', None)] = f'指定 _{view_name}_ 视图如何显示文件'
    T[(cfg_idx, f'{prefix}.files.layout', 'enumDescriptions', 0)] = f'根据 `#{key_for_threshold}#` 设置和每个嵌套层级的文件数量，自动在以 `tree` 或 `list` 形式显示文件之间切换'
    T[(cfg_idx, f'{prefix}.files.layout', 'enumDescriptions', 1)] = '以列表显示文件'
    T[(cfg_idx, f'{prefix}.files.layout', 'enumDescriptions', 2)] = '以树状显示文件'
    T[(cfg_idx, f'{prefix}.files.threshold', 'markdownDescription', None)] = f'指定何时根据 _{view_name}_ 视图中嵌套层级的文件数量在以 `tree` 或 `list` 形式显示文件之间切换。仅当 `#{key_for_threshold.replace(".threshold", ".layout")}#` 设置为 `auto` 时适用'
    T[(cfg_idx, f'{prefix}.files.compact', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中紧凑（扁平化）不必要的文件嵌套。仅当 `#{key_for_threshold.replace(".threshold", ".layout")}#` 设置为 `tree` 或 `auto` 时适用'
    T[(cfg_idx, f'{prefix}.files.icon', 'markdownDescription', None)] = f'指定 _{view_name}_ 视图如何显示文件图标'
    T[(cfg_idx, f'{prefix}.files.icon', 'enumDescriptions', 0)] = FILE_ICON_DESC
    T[(cfg_idx, f'{prefix}.files.icon', 'enumDescriptions', 1)] = FILE_TYPE_ICON_DESC

def add_branches_layout(cfg_idx, prefix, view_name, what='分支'):
    T[(cfg_idx, f'{prefix}.branches.layout', 'markdownDescription', None)] = f'指定 _{view_name}_ 视图如何显示{what}'
    T[(cfg_idx, f'{prefix}.branches.layout', 'enumDescriptions', 0)] = f'以列表显示{what}'
    T[(cfg_idx, f'{prefix}.branches.layout', 'enumDescriptions', 1)] = f'当名称包含斜杠 `/` 时以树状显示{what}'
    T[(cfg_idx, f'{prefix}.branches.compact', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中紧凑（扁平化）不必要的{what.replace("和标签","").replace("标签","")}嵌套。仅当 `#gitlens.views.{prefix.replace("gitlens.views.", "")}.branches.layout#` 设置为 `tree` 时适用'

def add_branch_compare(cfg_idx, prefix, view_name, with_working_tree=True):
    T[(cfg_idx, f'{prefix}.showBranchComparison', 'enumDescriptions', 0)] = '隐藏分支比较'
    if with_working_tree:
        T[(cfg_idx, f'{prefix}.showBranchComparison', 'enumDescriptions', 1)] = '将当前分支与用户选择的引用进行比较'
        T[(cfg_idx, f'{prefix}.showBranchComparison', 'enumDescriptions', 2)] = '将工作树与用户选择的引用进行比较'
    else:
        T[(cfg_idx, f'{prefix}.showBranchComparison', 'enumDescriptions', 1)] = '将分支与用户选择的引用进行比较'

def add_pr(cfg_idx, prefix, view_name, has_branches=True, has_commits=True):
    T[(cfg_idx, f'{prefix}.pullRequests.enabled', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中查询与分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
    if has_branches:
        T[(cfg_idx, f'{prefix}.pullRequests.showForBranches', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中显示与分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
    if has_commits:
        T[(cfg_idx, f'{prefix}.pullRequests.showForCommits', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'

def add_avatars(cfg_idx, prefix, view_name, with_status=True):
    if with_status:
        T[(cfg_idx, f'{prefix}.avatars', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中显示头像图像而不是提交（或状态）图标'
    else:
        T[(cfg_idx, f'{prefix}.avatars', 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中显示头像图像而不是状态图标'

def add_reveal(cfg_idx, prop, view_name, item_name):
    T[(cfg_idx, prop, 'markdownDescription', None)] = f'指定是否在 _{view_name}_ 视图中显示{item_name}，否则在 _仓库_ 视图中显示'

# ============ cfg 8: Commit Graph ============
T[(8, 'gitlens.graph.autoFetch.enabled', 'markdownDescription', None)] = '指定当 _提交图_ 在视图中时是否自动获取仓库。间隔由内置的 `#git.autofetchPeriod#` 设置控制。如果启用了 `#git.autofetch#`，VS Code 会处理自动获取，此设置无效。'
T[(8, 'gitlens.graph.details.location', 'markdownDescription', None)] = '指定 _提交图_ 中详情面板的位置'
T[(8, 'gitlens.graph.details.location', 'enumDescriptions', 0)] = '在提交图右侧显示详情面板'
T[(8, 'gitlens.graph.details.location', 'enumDescriptions', 1)] = '在提交图下方显示详情面板'
T[(8, 'gitlens.graph.editorOpeningBehavior', 'markdownDescription', None)] = '指定从 _提交图_ 打开的编辑器（文件、差异等）在提交图位于编辑器选项卡时应出现在哪个编辑器组中。当提交图作为面板显示时此设置无效。'
T[(8, 'gitlens.graph.editorOpeningBehavior', 'enumDescriptions', 0)] = '当提交图为活动编辑器时，在提交图旁打开编辑器；否则在活动编辑器组中打开'
T[(8, 'gitlens.graph.editorOpeningBehavior', 'enumDescriptions', 1)] = '始终在活动编辑器组中打开编辑器'
T[(8, 'gitlens.graph.multiselect', 'enumDescriptions', 0)] = '不允许选择多个提交'
T[(8, 'gitlens.graph.multiselect', 'enumDescriptions', 1)] = '允许无限制地选择多个提交'
T[(8, 'gitlens.graph.multiselect', 'enumDescriptions', 2)] = '允许按拓扑顺序选择多个提交'
T[(8, 'gitlens.graph.minimap.reversed', 'markdownDescription', None)] = '指定是否反转 _提交图_ 中小地图的方向，使较旧的提交显示在左侧而较新的提交显示在右侧'
T[(8, 'gitlens.graph.sidebar.pinned', 'markdownDescription', None)] = '指定 _提交图_ 侧边栏是否固定。固定时，侧边栏与提交图共享空间；取消固定时，侧边栏浮动在提交图之上，并在失去焦点时自动折叠'
T[(8, 'gitlens.graph.branchesVisibility', 'enumDescriptions', 3)] = '仅显示已收藏的分支'
T[(8, 'gitlens.graph.branchesVisibility', 'enumDescriptions', 4)] = '仅显示与活动代理关联的分支（运行中或闲置不超过 24 小时）'
T[(8, 'gitlens.graph.initialRowSelection', 'markdownDescription', None)] = '指定 _提交图_ 中默认选择的行'
T[(8, 'gitlens.graph.initialRowSelection', 'enumDescriptions', 0)] = '选择"工作进行中"（WIP）行'
T[(8, 'gitlens.graph.initialRowSelection', 'enumDescriptions', 1)] = '选择 HEAD 行'
T[(8, 'gitlens.graph.dateStyle', 'enumDescriptions', 2)] = '例如 2018年7月25日 下午7:18'
T[(8, 'gitlens.graph.stickyTimeline', 'markdownDescription', None)] = '指定是否在 _提交图_ 中显示在滚动时保持可见的粘性时间线标题'
T[(8, 'gitlens.graph.showWorktreeWipStats', 'markdownDescription', None)] = '指定是否在 _提交图_ 中每个工作树的 _WIP_ 行上显示行内工作树更改统计。禁用时，仅显示主工作树的 _WIP_ 行和当前选中工作树的 _WIP_ 行的更改统计'
T[(8, 'gitlens.graph.experimental.kanban.enabled', 'markdownDescription', None)] = '（实验性）指定是否在 _提交图_ 上启用代理看板模式'
T[(8, 'gitlens.graph.experimental.visualizations.enabled', 'markdownDescription', None)] = '（实验性）指定是否在 _提交图_ 上的可视化历史时间线旁启用树状图可视化模式（文件、提交、代理活动）。禁用时，仅显示时间线视图'

# ============ cfg 9: Launchpad ============
T[(9, 'gitlens.launchpad.ignoredRepositories', 'markdownDescription', None)] = '指定要在 _启动面板_ 中忽略的仓库'
T[(9, 'gitlens.launchpad.includedOrganizations', 'markdownDescription', None)] = '指定要在 _启动面板_ 中包含的组织。如果为空，则包含所有组织'
T[(9, 'gitlens.launchpad.ignoredOrganizations', 'markdownDescription', None)] = '指定要在 _启动面板_ 中忽略的组织'
T[(9, 'gitlens.launchpad.staleThreshold', 'markdownDescription', None)] = '指定多少天后拉取请求被视为陈旧并在 _启动面板_ 中移至"其他"'
T[(9, 'gitlens.launchpad.indicator.enabled', 'markdownDescription', None)] = '指定是否启用 _启动面板_ 的状态栏指示器'
T[(9, 'gitlens.launchpad.indicator.icon', 'markdownDescription', None)] = '指定 _启动面板_ 状态栏指示器图标的样式'
T[(9, 'gitlens.launchpad.indicator.icon', 'enumDescriptions', 0)] = '显示启动面板图标'
T[(9, 'gitlens.launchpad.indicator.icon', 'enumDescriptions', 1)] = '显示最高优先级组的图标'
T[(9, 'gitlens.launchpad.indicator.label', 'markdownDescription', None)] = '指定 _启动面板_ 状态栏指示器标签的显示方式'
T[(9, 'gitlens.launchpad.indicator.label', 'enumDescriptions', 0)] = '隐藏标签'
T[(9, 'gitlens.launchpad.indicator.label', 'enumDescriptions', 1)] = '显示需要您关注的最高优先级项'
T[(9, 'gitlens.launchpad.indicator.label', 'enumDescriptions', 2)] = '显示需要您关注的项的状态计数'
T[(9, 'gitlens.launchpad.indicator.groups', 'markdownDescription', None)] = '指定要在 _启动面板_ 状态栏指示器上显示的拉取请求分组'
T[(9, 'gitlens.launchpad.indicator.useColors', 'markdownDescription', None)] = '指定是否在 _启动面板_ 状态栏指示器上使用颜色'
T[(9, 'gitlens.launchpad.indicator.polling.enabled', 'markdownDescription', None)] = '指定状态栏指示器是否将为 _启动面板_ 获取并显示拉取请求数据'
T[(9, 'gitlens.launchpad.indicator.polling.interval', 'markdownDescription', None)] = '指定状态栏指示器为 _启动面板_ 获取拉取请求数据的频率（以分钟为单位）。使用 0 可禁用自动轮询'
T[(9, 'gitlens.launchpad.allowMultiple', 'markdownDescription', None)] = '指定是否允许将多个 _启动面板_ 实例作为编辑器选项卡打开'
T[(9, 'gitlens.launchpad.experimental.queryLimit', 'markdownDescription', None)] = '（实验性）指定 _启动面板_ 中要查询的拉取请求数量限制'

# ============ cfg 10: Cloud Patches ============
T[(10, 'gitlens.cloudPatches.enabled', 'markdownDescription', None)] = '指定是否启用 _云端补丁_ 的预览，它允许您与特定团队成员和其他开发人员私密、安全地共享代码'
T[(10, 'gitlens.cloudPatches.experimental.layout', 'markdownDescription', None)] = '（实验性）指定 _云端补丁_ 的首选布局'
T[(10, 'gitlens.cloudPatches.experimental.layout', 'enumDescriptions', 0)] = '优先在编辑器区域显示云端补丁'
T[(10, 'gitlens.cloudPatches.experimental.layout', 'enumDescriptions', 1)] = '优先在视图中显示云端补丁'

# ============ cfg 11: Views ============
T[(11, 'gitlens.views.scm.grouped.default', 'markdownDescription', None)] = '指定打开 _GitLens_ 视图时显示的默认视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 0)] = '提交视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 1)] = '工作树视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 2)] = '分支视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 3)] = '远程视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 4)] = '贮藏视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 5)] = '标签视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 6)] = '贡献者视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 7)] = '仓库视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 8)] = '文件历史视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 9)] = '启动面板视图'
T[(11, 'gitlens.views.scm.grouped.default', 'enumDescriptions', 10)] = '搜索和比较视图'
T[(11, 'gitlens.views.scm.grouped.views', 'markdownDescription', None)] = '指定将分组到源代码管理侧边栏上 _GitLens_ 视图中的视图'
T[(11, 'gitlens.views.scm.grouped.hiddenViews', 'markdownDescription', None)] = '指定分组到源代码管理侧边栏上 _GitLens_ 视图中时将被隐藏的视图'
T[(11, 'gitlens.views.collapseWorktreesWhenPossible', 'markdownDescription', None)] = '指定是否尝试在可能时将打开的工作树折叠到视图中的单个（公共）仓库'
T[(11, 'gitlens.views.multiselect', 'markdownDescription', None)] = '指定是否允许在视图中选择多个项'
T[(11, 'gitlens.views.showCurrentBranchOnTop', 'markdownDescription', None)] = '指定是否始终在视图顶部显示当前分支'
T[(11, 'gitlens.views.showComparisonContributors', 'markdownDescription', None)] = '指定是否在视图的比较结果中显示 _贡献者_ 部分'
T[(11, 'gitlens.views.showContributorsStatistics', 'markdownDescription', None)] = '指定是否在视图的 _贡献者_ 部分显示贡献者统计。这可能需要一些时间来计算，具体取决于仓库大小'
T[(11, 'gitlens.views.showRelativeDateMarkers', 'markdownDescription', None)] = '指定是否在视图中的修订（提交）历史上显示相对日期标记（_不到一周前_、_超过一周前_、_超过一个月前_ 等）'
T[(11, 'gitlens.views.defaultItemLimit', 'markdownDescription', None)] = '指定视图列表中显示的默认项数。使用 0 可指定无限制'
T[(11, 'gitlens.views.pageItemLimit', 'markdownDescription', None)] = '指定分页视图列表时每页显示的项数。使用 0 可指定无限制'
T[(11, 'gitlens.views.formats.commits.label', 'markdownDescription', None)] = '指定视图中提交的格式。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/gitkraken/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.formats.commits.description', 'markdownDescription', None)] = '指定视图中提交的描述格式。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/gitkraken/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.formats.commits.tooltip', 'markdownDescription', None)] = '指定视图中提交的工具提示格式（Markdown）。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/eamodio/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.formats.commits.tooltipWithStatus', 'markdownDescription', None)] = '指定视图中"文件"提交的工具提示格式（Markdown）。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/eamodio/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.formats.files.label', 'markdownDescription', None)] = '指定视图中文件的格式。请参阅 GitLens 文档中的 [_文件令牌_](https://github.com/gitkraken/vscode-gitlens/wiki/Custom-Formatting#file-tokens)'
T[(11, 'gitlens.views.formats.files.description', 'markdownDescription', None)] = '指定视图中文件的描述格式。请参阅 GitLens 文档中的 [_文件令牌_](https://github.com/gitkraken/vscode-gitlens/wiki/Custom-Formatting#file-tokens)'
T[(11, 'gitlens.views.formats.stashes.label', 'markdownDescription', None)] = '指定视图中贮藏的格式。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/gitkraken/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.formats.stashes.description', 'markdownDescription', None)] = '指定视图中贮藏的描述格式。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/gitkraken/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.formats.stashes.tooltip', 'markdownDescription', None)] = '指定视图中贮藏的工具提示格式（Markdown）。请参阅 GitLens 文档中的 [_提交令牌_](https://github.com/eamodio/vscode-gitlens/wiki/Custom-Formatting#commit-tokens)'
T[(11, 'gitlens.views.openChangesInMultiDiffEditor', 'markdownDescription', None)] = '指定是在多差异编辑器（单选项卡）中打开多个更改，还是在各个差异编辑器（多个选项卡）中打开'

# ============ cfg 12: Launchpad View ============
add_files_set(12, 'gitlens.views.launchpad', '启动面板', 'gitlens.views.launchpad.files.threshold')
T[(12, 'gitlens.views.launchpad.avatars', 'markdownDescription', None)] = '指定是否在 _启动面板_ 视图中显示头像图像而不是提交（或状态）图标'

# ============ cfg 13: Commits View ============
T[(13, 'gitlens.views.commits.showStashes', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中显示贮藏'
T[(13, 'gitlens.views.commits.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中显示当前分支或工作树与用户选择的引用（分支、标签等）的比较'
add_branch_compare(13, 'gitlens.views.commits', '提交', with_working_tree=True)
T[(13, 'gitlens.views.commits.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中查询与当前分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(13, 'gitlens.views.commits.pullRequests.showForBranches', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中显示与当前分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(13, 'gitlens.views.commits.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
add_files_set(13, 'gitlens.views.commits', '提交', 'gitlens.views.commits.files.threshold')
T[(13, 'gitlens.views.commits.avatars', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中显示头像图像而不是提交（或状态）图标'
T[(13, 'gitlens.views.commits.reveal', 'markdownDescription', None)] = '指定是否在 _提交_ 视图中显示提交，否则在 _仓库_ 视图中显示'

# ============ cfg 14: Inspect / Commit Details View ============
T[(14, 'gitlens.views.commitDetails.autolinks.enabled', 'markdownDescription', None)] = '指定是否自动链接提交消息中的外部资源'
T[(14, 'gitlens.views.commitDetails.autolinks.enhanced', 'markdownDescription', None)] = '指定是否查找提交消息中自动链接的外部资源的附加详情。需要连接到受支持的远程服务（例如 GitHub）'
T[(14, 'gitlens.views.commitDetails.pullRequests.enabled', 'markdownDescription', None)] = '指定是否查询关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
add_files_set(14, 'gitlens.views.commitDetails', '提交详情', 'gitlens.views.commitDetails.files.threshold')
T[(14, 'gitlens.views.commitDetails.avatars', 'markdownDescription', None)] = '指定是否在 _提交详情_ 视图中显示头像图像而不是提交（或状态）图标'

# ============ cfg 15: Pull Request View ============
add_files_set(15, 'gitlens.views.pullRequest', '拉取请求', 'gitlens.views.pullRequest.files.threshold')
T[(15, 'gitlens.views.pullRequest.avatars', 'markdownDescription', None)] = '指定是否在 _拉取请求_ 视图中显示头像图像而不是提交（或状态）图标'

# ============ cfg 16: Repositories View ============
T[(16, 'gitlens.views.repositories.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中显示当前分支或工作树与用户选择的引用（分支、标签等）的比较'
add_branch_compare(16, 'gitlens.views.repositories', '仓库', with_working_tree=True)
T[(16, 'gitlens.views.repositories.showUpstreamStatus', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示当前分支的上游状态'
T[(16, 'gitlens.views.repositories.includeWorkingTree', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库包含工作树文件状态'
T[(16, 'gitlens.views.repositories.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中查询与分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(16, 'gitlens.views.repositories.pullRequests.showForBranches', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中显示与分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(16, 'gitlens.views.repositories.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(16, 'gitlens.views.repositories.showCommits', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示当前分支上的提交'
T[(16, 'gitlens.views.repositories.showBranches', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示分支'
T[(16, 'gitlens.views.repositories.showRemotes', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示远程'
T[(16, 'gitlens.views.repositories.showStashes', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示贮藏'
T[(16, 'gitlens.views.repositories.showTags', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示标签'
T[(16, 'gitlens.views.repositories.showContributors', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示贡献者'
T[(16, 'gitlens.views.repositories.showWorktrees', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示工作树'
T[(16, 'gitlens.views.repositories.showIncomingActivity', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中为每个仓库显示实验性的传入活动'
T[(16, 'gitlens.views.repositories.autoRefresh', 'markdownDescription', None)] = '指定是否在仓库或文件系统更改时自动刷新 _仓库_ 视图'
T[(16, 'gitlens.views.repositories.autoReveal', 'markdownDescription', None)] = '指定是否在打开文件时自动在 _仓库_ 视图中显示仓库'
T[(16, 'gitlens.views.repositories.avatars', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中显示头像图像而不是提交（或状态）图标'
T[(16, 'gitlens.views.repositories.branches.layout', 'markdownDescription', None)] = '指定 _仓库_ 视图如何显示分支和标签'
T[(16, 'gitlens.views.repositories.branches.layout', 'enumDescriptions', 0)] = '以列表显示分支和标签'
T[(16, 'gitlens.views.repositories.branches.layout', 'enumDescriptions', 1)] = '当名称包含斜杠 `/` 时以树状显示分支和标签'
T[(16, 'gitlens.views.repositories.branches.compact', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中紧凑（扁平化）不必要的分支和标签嵌套。仅当 `#gitlens.views.repositories.branches.layout#` 设置为 `tree` 时适用'
add_files_set(16, 'gitlens.views.repositories', '仓库', 'gitlens.views.repositories.files.threshold')
T[(16, 'gitlens.views.repositories.compact', 'markdownDescription', None)] = '指定是否以紧凑显示密度显示 _仓库_ 视图'
T[(16, 'gitlens.views.repositories.branches.showStashes', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图的 _提交_ 和 _分支_ 部分显示贮藏'
T[(16, 'gitlens.views.repositories.branches.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _仓库_ 视图中每个分支下显示该分支与用户选择的引用（分支、标签等）的比较'
T[(16, 'gitlens.views.repositories.branches.showBranchComparison', 'enumDescriptions', 0)] = '隐藏分支比较'
T[(16, 'gitlens.views.repositories.branches.showBranchComparison', 'enumDescriptions', 1)] = '将分支与用户选择的引用进行比较'
T[(16, 'gitlens.views.repositories.worktrees.viewAs', 'markdownDescription', None)] = '指定 _仓库_ 视图如何显示工作树'
T[(16, 'gitlens.views.repositories.worktrees.viewAs', 'enumDescriptions', 0)] = '显示工作树名称'
T[(16, 'gitlens.views.repositories.worktrees.viewAs', 'enumDescriptions', 1)] = '显示工作树路径'
T[(16, 'gitlens.views.repositories.worktrees.viewAs', 'enumDescriptions', 2)] = '显示工作树相对路径'

# ============ cfg 17: File History View ============
T[(17, 'gitlens.views.fileHistory.mode', 'markdownDescription', None)] = '指定 _文件历史_ 视图的默认模式'
T[(17, 'gitlens.views.fileHistory.mode', 'enumDescriptions', 0)] = '显示所选文件或文件夹的提交'
T[(17, 'gitlens.views.fileHistory.mode', 'enumDescriptions', 1)] = '显示所选文件或文件夹的贡献者'
T[(17, 'gitlens.views.fileHistory.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _文件历史_ 视图中查询与提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(17, 'gitlens.views.fileHistory.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _文件历史_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
add_files_set(17, 'gitlens.views.fileHistory', '文件历史', 'gitlens.views.fileHistory.files.threshold')
T[(17, 'gitlens.views.fileHistory.avatars', 'markdownDescription', None)] = '指定是否在 _文件历史_ 视图中显示头像图像而不是状态图标'
T[(17, 'gitlens.advanced.fileHistoryFollowsRenames', 'markdownDescription', None)] = '指定文件历史是否跟随重命名'
T[(17, 'gitlens.advanced.fileHistoryShowAllBranches', 'markdownDescription', None)] = '指定文件历史是否显示所有分支的提交'
T[(17, 'gitlens.advanced.fileHistoryShowMergeCommits', 'markdownDescription', None)] = '指定文件历史是否显示合并提交'

# ============ cfg 18: Visual File History ============
T[(18, 'gitlens.visualHistory.allowMultiple', 'markdownDescription', None)] = '指定是否允许在编辑器区域中打开多个 _可视化文件历史_ 实例'
T[(18, 'gitlens.visualHistory.editorOpeningBehavior', 'markdownDescription', None)] = '指定从 _可视化文件历史_ 打开的编辑器（文件、差异等）在其位于编辑器选项卡时应出现在哪个编辑器组中。当显示在侧边栏中时此设置无效。'
T[(18, 'gitlens.visualHistory.editorOpeningBehavior', 'enumDescriptions', 0)] = '当可视化文件历史为活动编辑器时，在其旁打开编辑器；否则在活动编辑器组中打开'
T[(18, 'gitlens.visualHistory.editorOpeningBehavior', 'enumDescriptions', 1)] = '始终在活动编辑器组中打开编辑器'
T[(18, 'gitlens.visualHistory.queryLimit', 'markdownDescription', None)] = '由于速率限制，指定可在 _可视化文件历史_ 中查询统计信息的提交数量限制。仅适用于虚拟工作区。'

# ============ cfg 19: Line History View ============
T[(19, 'gitlens.views.lineHistory.avatars', 'markdownDescription', None)] = '指定是否在 _行历史_ 视图中显示头像图像而不是状态图标'

# ============ cfg 20: Branches View ============
T[(20, 'gitlens.views.branches.showRemoteBranches', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示默认远程的远程分支'
T[(20, 'gitlens.views.branches.showStashes', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示贮藏'
T[(20, 'gitlens.views.branches.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示分支与用户选择的引用（分支、标签等）的比较'
add_branch_compare(20, 'gitlens.views.branches', '分支', with_working_tree=False)
T[(20, 'gitlens.views.branches.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中查询与每个分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(20, 'gitlens.views.branches.pullRequests.showForBranches', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示与每个分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(20, 'gitlens.views.branches.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(20, 'gitlens.views.branches.branches.layout', 'markdownDescription', None)] = '指定 _分支_ 视图如何显示分支'
T[(20, 'gitlens.views.branches.branches.layout', 'enumDescriptions', 0)] = '以列表显示分支'
T[(20, 'gitlens.views.branches.branches.layout', 'enumDescriptions', 1)] = '当名称包含斜杠 `/` 时以树状显示分支'
T[(20, 'gitlens.views.branches.branches.compact', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中紧凑（扁平化）不必要的分支嵌套。仅当 `#gitlens.views.branches.branches.layout#` 设置为 `tree` 时适用'
add_files_set(20, 'gitlens.views.branches', '分支', 'gitlens.views.branches.files.threshold')
T[(20, 'gitlens.views.branches.avatars', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示头像图像而不是提交（或状态）图标'
T[(20, 'gitlens.views.branches.reveal', 'markdownDescription', None)] = '指定是否在 _分支_ 视图中显示分支，否则在 _仓库_ 视图中显示'

# ============ cfg 21: Remotes View ============
T[(21, 'gitlens.views.remotes.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _远程_ 视图中查询与每个分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(21, 'gitlens.views.remotes.pullRequests.showForBranches', 'markdownDescription', None)] = '指定是否在 _远程_ 视图中显示与每个分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(21, 'gitlens.views.remotes.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _远程_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(21, 'gitlens.views.remotes.branches.layout', 'markdownDescription', None)] = '指定 _远程_ 视图如何显示分支'
T[(21, 'gitlens.views.remotes.branches.layout', 'enumDescriptions', 0)] = '以列表显示分支'
T[(21, 'gitlens.views.remotes.branches.layout', 'enumDescriptions', 1)] = '当名称包含斜杠 `/` 时以树状显示分支'
T[(21, 'gitlens.views.remotes.branches.compact', 'markdownDescription', None)] = '指定是否在 _远程_ 视图中紧凑（扁平化）不必要的分支嵌套。仅当 `#gitlens.views.remotes.branches.layout#` 设置为 `tree` 时适用'
add_files_set(21, 'gitlens.views.remotes', '远程', 'gitlens.views.remotes.files.threshold')
T[(21, 'gitlens.views.remotes.avatars', 'markdownDescription', None)] = '指定是否在 _远程_ 视图中显示头像图像而不是提交（或状态）图标'
T[(21, 'gitlens.views.remotes.reveal', 'markdownDescription', None)] = '指定是否在 _远程_ 视图中显示远程，否则在 _仓库_ 视图中显示'

# ============ cfg 22: Stashes View ============
add_files_set(22, 'gitlens.views.stashes', '贮藏', 'gitlens.views.stashes.files.threshold')
T[(22, 'gitlens.views.stashes.reveal', 'markdownDescription', None)] = '指定是否在 _贮藏_ 视图中显示贮藏，否则在 _仓库_ 视图中显示'

# ============ cfg 23: Tags View ============
T[(23, 'gitlens.views.tags.branches.layout', 'markdownDescription', None)] = '指定 _标签_ 视图如何显示标签'
T[(23, 'gitlens.views.tags.branches.layout', 'enumDescriptions', 0)] = '以列表显示标签'
T[(23, 'gitlens.views.tags.branches.layout', 'enumDescriptions', 1)] = '当名称包含斜杠 `/` 时以树状显示标签'
T[(23, 'gitlens.views.tags.branches.compact', 'markdownDescription', None)] = '指定是否在 _标签_ 视图中紧凑（扁平化）不必要的标签嵌套。仅当 `#gitlens.views.tags.branches.layout#` 设置为 `tree` 时适用'
add_files_set(23, 'gitlens.views.tags', '标签', 'gitlens.views.tags.files.threshold')
T[(23, 'gitlens.views.tags.avatars', 'markdownDescription', None)] = '指定是否在 _标签_ 视图中显示头像图像而不是提交（或状态）图标'
T[(23, 'gitlens.views.tags.reveal', 'markdownDescription', None)] = '指定是否在 _标签_ 视图中显示标签，否则在 _仓库_ 视图中显示'

# ============ cfg 24: Worktrees View ============
T[(24, 'gitlens.worktrees.promptForLocation', 'markdownDescription', None)] = '指定在创建新工作树时是否提示输入路径'
T[(24, 'gitlens.worktrees.defaultLocation', 'markdownDescription', None)] = '指定创建新工作树的默认路径'
T[(24, 'gitlens.worktrees.openAfterCreate', 'markdownDescription', None)] = '指定如何以及何时在创建工作树后打开它'
T[(24, 'gitlens.worktrees.openAfterCreate', 'enumDescriptions', 0)] = '始终在当前窗口中打开新工作树'
T[(24, 'gitlens.worktrees.openAfterCreate', 'enumDescriptions', 1)] = '始终在新窗口中打开新工作树'
T[(24, 'gitlens.worktrees.openAfterCreate', 'enumDescriptions', 2)] = '仅在没有打开文件夹时才在当前窗口中打开新工作树'
T[(24, 'gitlens.worktrees.openAfterCreate', 'enumDescriptions', 3)] = '从不打开新工作树'
T[(24, 'gitlens.worktrees.openAfterCreate', 'enumDescriptions', 4)] = '始终提示打开新工作树'
T[(24, 'gitlens.views.worktrees.showStashes', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中显示贮藏'
T[(24, 'gitlens.views.worktrees.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中显示工作树分支与用户选择的引用（分支、标签等）的比较'
T[(24, 'gitlens.views.worktrees.showBranchComparison', 'enumDescriptions', 0)] = '隐藏分支比较'
T[(24, 'gitlens.views.worktrees.showBranchComparison', 'enumDescriptions', 1)] = '将工作树分支与用户选择的引用进行比较'
T[(24, 'gitlens.views.worktrees.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中查询与工作树分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(24, 'gitlens.views.worktrees.pullRequests.showForBranches', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中显示与工作树分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(24, 'gitlens.views.worktrees.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(24, 'gitlens.views.worktrees.worktrees.viewAs', 'markdownDescription', None)] = '指定 _工作树_ 视图如何显示工作树'
T[(24, 'gitlens.views.worktrees.worktrees.viewAs', 'enumDescriptions', 0)] = '显示工作树名称'
T[(24, 'gitlens.views.worktrees.worktrees.viewAs', 'enumDescriptions', 1)] = '显示工作树路径'
T[(24, 'gitlens.views.worktrees.worktrees.viewAs', 'enumDescriptions', 2)] = '显示工作树相对路径'
T[(24, 'gitlens.views.worktrees.branches.layout', 'markdownDescription', None)] = '指定 _工作树_ 视图如何显示工作树分支'
T[(24, 'gitlens.views.worktrees.branches.layout', 'enumDescriptions', 0)] = '以列表显示工作树分支'
T[(24, 'gitlens.views.worktrees.branches.layout', 'enumDescriptions', 1)] = '当名称包含斜杠 `/` 时以树状显示工作树分支'
T[(24, 'gitlens.views.worktrees.branches.compact', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中紧凑（扁平化）不必要的分支嵌套。仅当 `#gitlens.views.worktrees.branches.layout#` 设置为 `tree` 时适用'
add_files_set(24, 'gitlens.views.worktrees', '工作树', 'gitlens.views.worktrees.files.threshold')
T[(24, 'gitlens.views.worktrees.avatars', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中显示头像图像而不是提交（或状态）图标'
T[(24, 'gitlens.views.worktrees.reveal', 'markdownDescription', None)] = '指定是否在 _工作树_ 视图中显示工作树，否则在 _仓库_ 视图中显示'

# ============ cfg 25: Contributors View ============
T[(25, 'gitlens.views.contributors.showAllBranches', 'markdownDescription', None)] = '指定是否在 _贡献者_ 视图中显示所有分支的提交'
T[(25, 'gitlens.views.contributors.showStatistics', 'markdownDescription', None)] = '指定是否在 _贡献者_ 视图中显示贡献者统计。这可能需要一些时间来计算，具体取决于仓库大小'
T[(25, 'gitlens.views.contributors.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _贡献者_ 视图中查询与分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(25, 'gitlens.views.contributors.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _贡献者_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
add_files_set(25, 'gitlens.views.contributors', '贡献者', 'gitlens.views.contributors.files.threshold')
T[(25, 'gitlens.views.contributors.avatars', 'markdownDescription', None)] = '指定是否在 _贡献者_ 视图中显示头像图像而不是提交（或状态）图标'
T[(25, 'gitlens.views.contributors.reveal', 'markdownDescription', None)] = '指定是否在 _贡献者_ 视图中显示贡献者，否则在 _仓库_ 视图中显示'
T[(25, 'gitlens.views.contributors.maxWait', 'markdownDescription', None)] = '指定等待所有贡献者加载的最长时间（以秒为单位）。使用 0 可无限期等待（无超时）'

# ============ cfg 26: Search & Compare View ============
T[(26, 'gitlens.views.searchAndCompare.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _搜索和比较_ 视图中查询与提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(26, 'gitlens.views.searchAndCompare.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _搜索和比较_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
add_files_set(26, 'gitlens.views.searchAndCompare', '搜索和比较', 'gitlens.views.searchAndCompare.files.threshold')
T[(26, 'gitlens.views.searchAndCompare.avatars', 'markdownDescription', None)] = '指定是否在 _搜索和比较_ 视图中显示头像图像而不是提交（或状态）图标'

# ============ cfg 27: Cloud Patches View ============
add_files_set(27, 'gitlens.views.drafts', '云端补丁', 'gitlens.views.drafts.files.threshold')
T[(27, 'gitlens.views.drafts.avatars', 'markdownDescription', None)] = '指定是否在 _云端补丁_ 视图中显示头像图像而不是提交（或状态）图标'

# ============ cfg 28: Patch Details View ============
add_files_set(28, 'gitlens.views.patchDetails', '补丁详情', 'gitlens.views.patchDetails.files.threshold')
T[(28, 'gitlens.views.patchDetails.avatars', 'markdownDescription', None)] = '指定是否在 _补丁详情_ 视图中显示头像图像而不是提交（或状态）图标'

# ============ cfg 29: Cloud Workspaces View ============
T[(29, 'gitlens.views.workspaces.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中显示当前分支或工作树与用户选择的引用（分支、标签等）的比较'
add_branch_compare(29, 'gitlens.views.workspaces', '云端工作区', with_working_tree=True)
T[(29, 'gitlens.views.workspaces.showUpstreamStatus', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示当前分支的上游状态'
T[(29, 'gitlens.views.workspaces.includeWorkingTree', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库包含工作树文件状态'
T[(29, 'gitlens.views.workspaces.pullRequests.enabled', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中查询与分支和提交关联的拉取请求。需要连接到受支持的远程服务（例如 GitHub）'
T[(29, 'gitlens.views.workspaces.pullRequests.showForBranches', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中显示与分支关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(29, 'gitlens.views.workspaces.pullRequests.showForCommits', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中显示与提交关联的拉取请求（如有）。需要连接到受支持的远程服务（例如 GitHub）'
T[(29, 'gitlens.views.workspaces.showCommits', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示当前分支上的提交'
T[(29, 'gitlens.views.workspaces.showBranches', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示分支'
T[(29, 'gitlens.views.workspaces.showRemotes', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示远程'
T[(29, 'gitlens.views.workspaces.showStashes', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示贮藏'
T[(29, 'gitlens.views.workspaces.showTags', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示标签'
T[(29, 'gitlens.views.workspaces.showContributors', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示贡献者'
T[(29, 'gitlens.views.workspaces.showWorktrees', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示工作树'
T[(29, 'gitlens.views.workspaces.showIncomingActivity', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中为每个仓库显示实验性的传入活动'
T[(29, 'gitlens.views.workspaces.avatars', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中显示头像图像而不是提交（或状态）图标'
T[(29, 'gitlens.views.workspaces.branches.layout', 'markdownDescription', None)] = '指定 _云端工作区_ 视图如何显示分支和标签'
T[(29, 'gitlens.views.workspaces.branches.layout', 'enumDescriptions', 0)] = '以列表显示分支和标签'
T[(29, 'gitlens.views.workspaces.branches.layout', 'enumDescriptions', 1)] = '当名称包含斜杠 `/` 时以树状显示分支和标签'
T[(29, 'gitlens.views.workspaces.branches.compact', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中紧凑（扁平化）不必要的分支和标签嵌套。仅当 `#gitlens.views.workspaces.branches.layout#` 设置为 `tree` 时适用'
T[(29, 'gitlens.views.workspaces.worktrees.viewAs', 'markdownDescription', None)] = '指定 _云端工作区_ 视图如何显示工作树'
T[(29, 'gitlens.views.workspaces.worktrees.viewAs', 'enumDescriptions', 0)] = '显示工作树名称'
T[(29, 'gitlens.views.workspaces.worktrees.viewAs', 'enumDescriptions', 1)] = '显示工作树路径'
T[(29, 'gitlens.views.workspaces.worktrees.viewAs', 'enumDescriptions', 2)] = '显示工作树相对路径'
add_files_set(29, 'gitlens.views.workspaces', '云端工作区', 'gitlens.views.workspaces.files.threshold')
T[(29, 'gitlens.views.workspaces.compact', 'markdownDescription', None)] = '指定是否以紧凑显示密度显示 _云端工作区_ 视图'
T[(29, 'gitlens.views.workspaces.branches.showStashes', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图的 _提交_ 和 _分支_ 部分显示贮藏'
T[(29, 'gitlens.views.workspaces.branches.showBranchComparison', 'markdownDescription', None)] = '指定是否在 _云端工作区_ 视图中每个分支下显示该分支与用户选择的引用（分支、标签等）的比较'
T[(29, 'gitlens.views.workspaces.branches.showBranchComparison', 'enumDescriptions', 0)] = '隐藏分支比较'
T[(29, 'gitlens.views.workspaces.branches.showBranchComparison', 'enumDescriptions', 1)] = '将分支与用户选择的引用进行比较'

# ============ cfg 30: Interactive Rebase Editor ============
T[(30, 'gitlens.rebaseEditor.density', 'markdownDescription', None)] = '指定 _交互式变基编辑器_ 的布局密度'
T[(30, 'gitlens.rebaseEditor.density', 'enumDescriptions', 0)] = '紧凑布局，间距最小'
T[(30, 'gitlens.rebaseEditor.density', 'enumDescriptions', 1)] = '舒适布局，行间留有更多空间'
T[(30, 'gitlens.rebaseEditor.ordering', 'markdownDescription', None)] = '指定 _交互式变基编辑器_ 中如何显示 Git 提交'
T[(30, 'gitlens.rebaseEditor.ordering', 'enumDescriptions', 0)] = '最早的提交显示在最前'
T[(30, 'gitlens.rebaseEditor.ordering', 'enumDescriptions', 1)] = '最新的提交显示在最前'
T[(30, 'gitlens.rebaseEditor.openOnPausedRebase', 'markdownDescription', None)] = '指定在检测到已暂停的变基时是否自动打开 _交互式变基编辑器_'
T[(30, 'gitlens.rebaseEditor.openOnPausedRebase', 'enumDescriptions', 0)] = '从不自动打开编辑器'
T[(30, 'gitlens.rebaseEditor.openOnPausedRebase', 'enumDescriptions', 1)] = '仅在检测到交互式变基时自动打开编辑器'
T[(30, 'gitlens.rebaseEditor.openOnPausedRebase', 'enumDescriptions', 2)] = '在检测到任何已暂停的变基时自动打开编辑器'
T[(30, 'gitlens.rebaseEditor.openBehavior', 'markdownDescription', None)] = '指定当 _交互式变基编辑器_ 在已暂停的变基上自动重新打开时，应在哪个编辑器组中打开'
T[(30, 'gitlens.rebaseEditor.openBehavior', 'enumDescriptions', 0)] = '当多窗格布局已存在时，在提交消息编辑器旁打开编辑器；否则在活动编辑器组中打开'
T[(30, 'gitlens.rebaseEditor.openBehavior', 'enumDescriptions', 1)] = '始终在活动编辑器旁打开编辑器，必要时创建新的编辑器组'
T[(30, 'gitlens.rebaseEditor.revealLocation', 'markdownDescription', None)] = '指定在何处显示提交和引用'
T[(30, 'gitlens.rebaseEditor.revealLocation', 'enumDescriptions', 0)] = '在 _提交图_ 中显示提交'
T[(30, 'gitlens.rebaseEditor.revealLocation', 'enumDescriptions', 1)] = '在 _检查_ 视图中显示提交'
T[(30, 'gitlens.rebaseEditor.revealBehavior', 'markdownDescription', None)] = '指定何时在 `#gitlens.rebaseEditor.revealLocation#` 位置自动显示提交'
T[(30, 'gitlens.rebaseEditor.revealBehavior', 'enumDescriptions', 0)] = '双击行时自动显示提交'
T[(30, 'gitlens.rebaseEditor.revealBehavior', 'enumDescriptions', 1)] = '选择更改时或双击行时自动显示提交'

# ============ cfg 31: Git Command Palette ============
T[(31, 'gitlens.gitCommands.avatars', 'markdownDescription', None)] = '指定是否在快速选择菜单中显示头像图像（如适用）'
T[(31, 'gitlens.gitCommands.sortBy', 'markdownDescription', None)] = '指定 _Git 命令面板_ 中 Git 命令的排序方式'
T[(31, 'gitlens.gitCommands.sortBy', 'enumDescriptions', 0)] = '按名称对命令排序'
T[(31, 'gitlens.gitCommands.sortBy', 'enumDescriptions', 1)] = '按上次使用日期对命令排序'
T[(31, 'gitlens.gitCommands.skipConfirmations', 'markdownDescription', None)] = '指定哪些（以及何时）Git 命令将跳过确认步骤，使用格式：`git-command-name:(menu|command)`'
T[(31, 'gitlens.gitCommands.closeOnFocusOut', 'markdownDescription', None)] = '指定当焦点丢失时是否关闭 _Git 命令面板_（如果不关闭，按 `ESC` 键关闭）'
T[(31, 'gitlens.gitCommands.search.showResultsInSideBar', 'markdownDescription', None)] = '指定是否将提交搜索结果直接显示在快速选择菜单中、显示在侧边栏中，或根据上下文决定'
T[(31, 'gitlens.gitCommands.search.matchAll', 'markdownDescription', None)] = '指定是否匹配所有或任意提交消息搜索模式'
T[(31, 'gitlens.gitCommands.search.matchCase', 'markdownDescription', None)] = '指定提交搜索模式匹配时是否区分大小写'
T[(31, 'gitlens.gitCommands.search.matchRegex', 'markdownDescription', None)] = '指定是否使用正则表达式匹配提交搜索模式'

# ============ cfg 32: Integrations / Autolinks / Remotes ============
T[(32, 'gitlens.autolinks', 'markdownDescription', None)] = '指定提交消息中外部资源的自动链接。使用 `<num>` 作为引用编号的变量'
T[(32, 'gitlens.integrations.enabled', 'markdownDescription', None)] = '指定是否启用与任何受支持远程服务的丰富集成'
T[(32, 'gitlens.cloudIntegrations.enabled', 'markdownDescription', None)] = '指定在通过 GitHub 进行身份验证时是否使用基于云的集成'
T[(32, 'gitlens.remotes', 'markdownDescription', None)] = '指定要与 Git 远程匹配的自定义远程服务，用于检测内置远程服务的自定义域名或为自定义远程服务提供支持'
T[(32, 'gitlens.partners', 'description', None)] = '指定合作伙伴集成的配置'
T[(32, 'gitlens.liveshare.enabled', 'description', None)] = '指定是否启用与 Visual Studio Live Share 的集成'
T[(32, 'gitlens.liveshare.allowGuestAccess', 'description', None)] = '指定使用 Visual Studio Live Share 时是否允许访客访问 GitLens 功能'

# ============ cfg 33: Terminal / GitKraken CLI ============
T[(33, 'gitlens.terminalLinks.enabled', 'markdownDescription', None)] = '指定是否启用终端链接 &mdash; 集成终端中的自动链接，可快速跳转到提交、分支、标签等的更多详情'
T[(33, 'gitlens.terminalLinks.showDetailsView', 'markdownDescription', None)] = '指定在集成终端中点击提交链接时是否显示 _提交详情_ 视图'
T[(33, 'gitlens.gitkraken.cli.localPath', 'markdownDescription', None)] = '指定用于开发的本地 GitKraken CLI 二进制文件的路径。在开发模式下设置时，将禁用 CLI 的自动安装和自动更新。_仅在以开发模式运行时适用。_'
T[(33, 'gitlens.gitkraken.cli.insiders.enabled', 'markdownDescription', None)] = '指定是否启用实验性的 GitKraken CLI 内测版本。未设置时，将在 GitLens 的预发布版本和调试版本中自动启用'
T[(33, 'gitlens.gitkraken.mcp.autoEnabled', 'markdownDescription', None)] = '指定是否自动安装并启用 GitKraken MCP。仅适用于 VS Code 1.101 及更高版本。'
T[(33, 'gitlens.terminal.overrideGitEditor', 'markdownDescription', None)] = '指定是否将 VS Code 用作 GitLens 终端命令的 Git `core.editor`'

# ============ cfg 34: AI ============
T[(34, 'gitlens.ai.model', 'markdownDescription', None)] = '指定用于 GitLens AI 功能的 AI 提供商和模型。应使用 `provider:model` 格式（例如 `openai:gpt-4o` 或 `anthropic:claude-3-5-sonnet-latest`），使用 `gitkraken` 表示 GitKraken AI 提供的模型，或使用 `vscode` 表示 VS Code 扩展 API 提供的模型'
T[(34, 'gitlens.ai.gitkraken.model', 'markdownDescription', None)] = '指定用于 GitLens AI 功能的 GitKraken AI 提供的模型，格式为 `provider:model`'
T[(34, 'gitlens.ai.vscode.model', 'markdownDescription', None)] = '指定用于 GitLens AI 功能的 VS Code 提供的模型，格式为 `provider:model`'
T[(34, 'gitlens.ai.ollama.url', 'markdownDescription', None)] = '指定用于访问的 Ollama URL'
T[(34, 'gitlens.ai.openai.url', 'markdownDescription', None)] = '指定用于访问 OpenAI 模型的自定义 URL。'
T[(34, 'gitlens.ai.azure.url', 'markdownDescription', None)] = '指定用于访问 Azure OpenAI 模型的自定义 URL。Azure URL 应使用以下格式：https://{your-resource-name}.openai.azure.com/openai/deployments/{deployment-id}/chat/completions?api-version={api-version}'
T[(34, 'gitlens.ai.openaicompatible.url', 'markdownDescription', None)] = '指定用于访问 OpenAI 兼容模型的自定义 URL。'
T[(34, 'gitlens.ai.largePromptWarningThreshold', 'markdownDescription', None)] = '指定提示词过长时显示警告的阈值（以 token 计）'
T[(34, 'gitlens.ai.modelOptions.temperature', 'markdownDescription', None)] = '指定用于 AI 模型的温度（输出随机性的度量）。值越高随机性越大（例如更具创造性），值越低则越确定'
T[(34, 'gitlens.ai.explainChanges.customInstructions', 'markdownDescription', None)] = '指定生成更改摘要时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.reviewChanges.customInstructions', 'markdownDescription', None)] = '指定审查一组更改时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.generateChangelog.customInstructions', 'markdownDescription', None)] = '指定从一组更改生成变更日志时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.generateCommitMessage.customInstructions', 'markdownDescription', None)] = '指定生成提交消息时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.generateCommits.customInstructions', 'markdownDescription', None)] = '指定生成提交时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.enabled', 'markdownDescription', None)] = '指定是否启用 GitLens 的 AI 驱动功能'
T[(34, 'gitlens.ai.openInAgent', 'markdownDescription', None)] = '当 `#showOpenInAgent#` 已设置时，开始工作 / 开始 PR 审查的默认路由：`ask` 显示手动 / 代理选择器；`manual` 跳过并继续手动操作；`agent` 跳过并打开代理选择器（或已设置的 `#gitlens.ai.defaultAgent#`）。'
T[(34, 'gitlens.ai.openInAgent', 'enumDescriptions', 0)] = '每次询问（默认）'
T[(34, 'gitlens.ai.openInAgent', 'enumDescriptions', 1)] = '始终手动继续'
T[(34, 'gitlens.ai.openInAgent', 'enumDescriptions', 2)] = '始终在代理中打开'
T[(34, 'gitlens.ai.defaultAgent', 'markdownDescription', None)] = '当路由为 `agent` 时，开始工作 / 开始 PR 审查的默认代理。以不透明 ID 形式存储（例如 `ide-chat`、`claude-extension`、`cli:claude-cli`）。当持久化的代理不再可用时，会回退到代理选择器。'
T[(34, 'gitlens.ai.exclude.files', 'markdownDescription', None)] = '指定生成提交消息、解释更改等时从 AI 提示中排除的文件 glob 模式。类似于 `files.exclude`，使用 glob 模式作为键，`true` 表示排除，`false` 表示包含。'
T[(34, 'gitlens.ai.generateStashMessage.customInstructions', 'markdownDescription', None)] = '指定生成贮藏消息时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.generateCreateCloudPatch.customInstructions', 'markdownDescription', None)] = '指定生成云端补丁标题和描述时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.generateCreateCodeSuggest.customInstructions', 'markdownDescription', None)] = '指定生成代码建议标题和描述时提供给 AI 提供商的自定义指令'
T[(34, 'gitlens.ai.generateCreatePullRequest.customInstructions', 'markdownDescription', None)] = '指定生成拉取请求标题和描述时提供给 AI 提供商的自定义指令'

# ============ cfg 35: Default Date / Time ============
T[(35, 'gitlens.defaultDateStyle', 'markdownDescription', None)] = '指定默认情况下日期的显示方式'
T[(35, 'gitlens.defaultDateStyle', 'enumDescriptions', 0)] = '例如 1 天前'
T[(35, 'gitlens.defaultDateStyle', 'enumDescriptions', 1)] = '例如 2018年7月25日 下午7:18'
T[(35, 'gitlens.defaultDateFormat', 'markdownDescription', None)] = '指定默认情况下绝对日期的格式化方式。受支持的格式见 [Moment.js 文档](https://momentjs.com/docs/#/displaying/format/)'
T[(35, 'gitlens.defaultDateLocale', 'markdownDescription', None)] = '指定用于日期格式化的区域设置（[BCP 47 语言标签](https://en.wikipedia.org/wiki/IETF_language_tag#List_of_major_primary_language_subtags)），默认为 VS Code 区域设置。使用 `system` 跟随当前系统区域设置，或选择特定区域设置（例如 `en-US`）'
T[(35, 'gitlens.defaultDateShortFormat', 'markdownDescription', None)] = '指定默认情况下简短绝对日期的格式化方式。受支持的格式见 [Moment.js 文档](https://momentjs.com/docs/#/displaying/format/)'
T[(35, 'gitlens.defaultTimeFormat', 'markdownDescription', None)] = '指定默认情况下时间的格式化方式。受支持的格式见 [Moment.js 文档](https://momentjs.com/docs/#/displaying/format/)'
T[(35, 'gitlens.defaultDateSource', 'markdownDescription', None)] = '指定提交日期应使用作者日期还是提交日期'
T[(35, 'gitlens.defaultDateSource', 'enumDescriptions', 0)] = '使用更改的创作日期（即最初编写时的日期）'
T[(35, 'gitlens.defaultDateSource', 'enumDescriptions', 1)] = '使用更改的提交日期'

# ============ cfg 36: Sort By ============
T[(36, 'gitlens.sortRepositoriesBy', 'markdownDescription', None)] = '指定快速选择菜单和视图中仓库的排序方式'
T[(36, 'gitlens.sortRepositoriesBy', 'enumDescriptions', 0)] = '按发现或工作区顺序排序仓库'
T[(36, 'gitlens.sortRepositoriesBy', 'enumDescriptions', 1)] = '按上次获取日期降序排序仓库'
T[(36, 'gitlens.sortRepositoriesBy', 'enumDescriptions', 2)] = '按上次获取日期升序排序仓库'
T[(36, 'gitlens.sortRepositoriesBy', 'enumDescriptions', 3)] = '按名称升序排序仓库'
T[(36, 'gitlens.sortRepositoriesBy', 'enumDescriptions', 4)] = '按名称降序排序仓库'
T[(36, 'gitlens.sortBranchesBy', 'markdownDescription', None)] = '指定快速选择菜单和视图中分支的排序方式'
T[(36, 'gitlens.sortBranchesBy', 'enumDescriptions', 0)] = '按最近提交日期降序排序分支'
T[(36, 'gitlens.sortBranchesBy', 'enumDescriptions', 1)] = '按最近提交日期升序排序分支'
T[(36, 'gitlens.sortBranchesBy', 'enumDescriptions', 2)] = '按名称升序排序分支'
T[(36, 'gitlens.sortBranchesBy', 'enumDescriptions', 3)] = '按名称降序排序分支'
T[(36, 'gitlens.sortTagsBy', 'markdownDescription', None)] = '指定快速选择菜单和视图中标签的排序方式'
T[(36, 'gitlens.sortTagsBy', 'enumDescriptions', 0)] = '按日期降序排序标签'
T[(36, 'gitlens.sortTagsBy', 'enumDescriptions', 1)] = '按日期升序排序标签'
T[(36, 'gitlens.sortTagsBy', 'enumDescriptions', 2)] = '按名称升序排序标签'
T[(36, 'gitlens.sortTagsBy', 'enumDescriptions', 3)] = '按名称降序排序标签'
T[(36, 'gitlens.sortWorktreesBy', 'markdownDescription', None)] = '指定快速选择菜单和视图中工作树的排序方式'
T[(36, 'gitlens.sortWorktreesBy', 'enumDescriptions', 0)] = '按最近提交日期降序排序工作树'
T[(36, 'gitlens.sortWorktreesBy', 'enumDescriptions', 1)] = '按最近提交日期升序排序工作树'
T[(36, 'gitlens.sortWorktreesBy', 'enumDescriptions', 2)] = '按名称升序排序工作树'
T[(36, 'gitlens.sortWorktreesBy', 'enumDescriptions', 3)] = '按名称降序排序工作树'
T[(36, 'gitlens.sortContributorsBy', 'markdownDescription', None)] = '指定快速选择菜单和视图中贡献者的排序方式'
T[(36, 'gitlens.sortContributorsBy', 'enumDescriptions', 0)] = '按提交数降序排序贡献者'
T[(36, 'gitlens.sortContributorsBy', 'enumDescriptions', 1)] = '按提交数升序排序贡献者'
T[(36, 'gitlens.sortContributorsBy', 'enumDescriptions', 2)] = '按最近提交日期降序排序贡献者'
T[(36, 'gitlens.sortContributorsBy', 'enumDescriptions', 3)] = '按最近提交日期升序排序贡献者'
T[(36, 'gitlens.sortContributorsBy', 'enumDescriptions', 4)] = '按名称升序排序贡献者'
T[(36, 'gitlens.sortContributorsBy', 'enumDescriptions', 5)] = '按名称降序排序贡献者'

# ============ cfg 37: Menus ============
T[(37, 'gitlens.menus', 'markdownDescription', None)] = '指定将哪些命令添加到哪些菜单'

# ============ cfg 38: Keymap ============
T[(38, 'gitlens.keymap', 'markdownDescription', None)] = '指定 GitLens 快捷键使用的键位映射'
T[(38, 'gitlens.keymap', 'enumDescriptions', 0)] = '添加一组以 `Alt`（macOS 上为 ⌥）开头的备用快捷键'
T[(38, 'gitlens.keymap', 'enumDescriptions', 1)] = '添加一组以 `Ctrl+Shift+G`（macOS 上为 `⌥⌘G`）开头的和弦快捷键'
T[(38, 'gitlens.keymap', 'enumDescriptions', 2)] = '不会添加任何快捷键'

# ============ cfg 39: Modes ============
T[(39, 'gitlens.mode.statusBar.enabled', 'markdownDescription', None)] = '指定是否在状态栏中显示活动的 GitLens 模式'
T[(39, 'gitlens.mode.statusBar.alignment', 'markdownDescription', None)] = '指定状态栏中活动 GitLens 模式的对齐方式'
T[(39, 'gitlens.mode.statusBar.alignment', 'enumDescriptions', 0)] = '左对齐'
T[(39, 'gitlens.mode.statusBar.alignment', 'enumDescriptions', 1)] = '右对齐'
T[(39, 'gitlens.mode.active', 'markdownDescription', None)] = '指定当前活动的 GitLens 模式（如有）'
T[(39, 'gitlens.modes', 'markdownDescription', None)] = '指定用户定义的 GitLens 模式'

# ============ cfg 40: GitKraken ============
T[(40, 'gitlens.gitkraken.activeOrganizationId', 'markdownDescription', None)] = '指定 GitLens 中用户当前活动的 GitKraken 组织的 ID'

# ============ cfg 41: Advanced ============
T[(41, 'gitlens.detectNestedRepositories', 'markdownDescription', None)] = '指定打开文件时是否尝试检测嵌套仓库'
T[(41, 'gitlens.telemetry.enabled', 'markdownDescription', None)] = '指定是否允许 GitLens 发送产品使用遥测数据。\n\n_**注意：** 要让 GitLens 发送任何遥测数据，此设置和 VS Code 遥测都必须启用。如果其中一个被禁用，则不会发送任何遥测数据。_'
T[(41, 'gitlens.advanced.messages', 'markdownDescription', None)] = '指定应抑制哪些消息'
T[(41, 'gitlens.advanced.repositorySearchDepth', 'markdownDescription', None)] = '指定搜索仓库的文件夹深度。默认为 `#git.repositoryScanMaxDepth#`'
T[(41, 'gitlens.advanced.abbreviatedShaLength', 'markdownDescription', None)] = '指定缩写提交 SHA 的长度'
T[(41, 'gitlens.advanced.abbreviateShaOnCopy', 'markdownDescription', None)] = '指定将完整还是缩写的提交 SHA 复制到剪贴板。缩写至 `#gitlens.advanced.abbreviatedShaLength#` 指定的长度。'
T[(41, 'gitlens.advanced.commitOrdering', 'markdownDescription', None)] = '指定提交的显示顺序。如果未指定，提交将按反向时间顺序显示'
T[(41, 'gitlens.advanced.commitOrdering', 'enumDescriptions', 0)] = '按反向时间顺序显示提交'
T[(41, 'gitlens.advanced.commitOrdering', 'enumDescriptions', 1)] = '按提交时间戳的反向时间顺序显示提交'
T[(41, 'gitlens.advanced.commitOrdering', 'enumDescriptions', 2)] = '按作者时间戳的反向时间顺序显示提交'
T[(41, 'gitlens.advanced.commitOrdering', 'enumDescriptions', 3)] = '按提交时间戳的反向时间顺序显示提交，但避免多条历史记录线的交错'
T[(41, 'gitlens.blame.ignoreWhitespace', 'markdownDescription', None)] = '指定在责任归属操作中比较修订版时是否忽略空白字符'
T[(41, 'gitlens.advanced.blame.customArguments', 'markdownDescription', None)] = '指定传递给 `git blame` 命令的额外参数'
T[(41, 'gitlens.advanced.similarityThreshold', 'markdownDescription', None)] = '指定一对已删除和已添加的文件被视为重命名所需的相似度（百分比）'
T[(41, 'gitlens.advanced.externalDiffTool', 'markdownDescription', None)] = '指定一个可选的外部差异工具，用于比较文件。必须是已配置的 [Git difftool](https://git-scm.com/docs/git-config#Documentation/git-config.txt-difftool)。'
T[(41, 'gitlens.advanced.externalDirectoryDiffTool', 'markdownDescription', None)] = '指定一个可选的外部差异工具，用于比较目录。必须是已配置的 [Git difftool](https://git-scm.com/docs/git-config#Documentation/git-config.txt-difftool)。'
T[(41, 'gitlens.advanced.quickPick.closeOnFocusOut', 'markdownDescription', None)] = '指定当焦点丢失时是否关闭快速选择菜单（如果不关闭，按 `ESC` 键关闭）'
T[(41, 'gitlens.advanced.skipOnboarding', 'markdownDescription', None)] = '指定是否跳过引导体验，例如欢迎视图和演练。适用于容器或沙盒等临时环境'
T[(41, 'gitlens.advanced.git.timeout', 'markdownDescription', None)] = '指定 Git 命令的超时时间（以秒为单位）。使用 0 可禁用超时。一些长时间运行的操作（例如合并、变基和回滚）始终禁用超时'
T[(41, 'gitlens.advanced.git.maxConcurrentProcesses', 'markdownDescription', None)] = '指定可同时运行的后台 Git 进程的最大数量。如果在大型仓库中遇到系统变慢，请减小此值'
T[(41, 'gitlens.advanced.maxListItems', 'markdownDescription', None)] = '指定列表中显示的最大项目数。使用 0 表示不限制'
T[(41, 'gitlens.advanced.maxSearchItems', 'markdownDescription', None)] = '指定搜索中显示的最大项目数。使用 0 表示不限制'
T[(41, 'gitlens.advanced.caching.gitPath', 'markdownDescription', None)] = '指定是否缓存（按工作区）GitLens 使用的 Git 可执行文件路径'
T[(41, 'gitlens.debug', 'markdownDescription', None)] = '指定调试模式'
T[(41, 'gitlens.deepLinks.schemeOverride', 'markdownDescription', None)] = '指定是否使用环境值或指定值覆盖默认深层链接方案 (vscode://)'
T[(41, 'gitlens.advanced.resolveSymlinks', 'markdownDescription', None)] = '指定在确定 Git 操作的文件路径时是否解析符号链接'
T[(41, 'gitlens.advanced.commits.delayLoadingFileDetails', 'markdownDescription', None)] = '指定是否延迟加载提交文件详情直到需要时。这可以提高打开具有大量历史记录的仓库时的性能，但会导致更多的增量 Git 调用'

# ============ cfg 42: General ============
T[(42, 'gitlens.showWhatsNewAfterUpgrades', 'markdownDescription', None)] = '指定升级到新功能版本后是否显示新功能通知'
T[(42, 'gitlens.defaultCurrentUserNameStyle', 'markdownDescription', None)] = '指定当前 git 用户的名称在责任归属注释、悬停提示和其他 UI 元素中的显示方式'
T[(42, 'gitlens.defaultCurrentUserNameStyle', 'enumDescriptions', 0)] = '为当前用户显示"您"'
T[(42, 'gitlens.defaultCurrentUserNameStyle', 'enumDescriptions', 1)] = '显示来自 git config 的用户名'
T[(42, 'gitlens.defaultCurrentUserNameStyle', 'enumDescriptions', 2)] = '显示用户名后跟"（您）"，例如"Jane Doe（您）"'
T[(42, 'gitlens.defaultGravatarsStyle', 'markdownDescription', None)] = '指定 gravatar 默认（回退）图像的样式'
T[(42, 'gitlens.defaultGravatarsStyle', 'enumDescriptions', 0)] = '几何图案'
T[(42, 'gitlens.defaultGravatarsStyle', 'enumDescriptions', 1)] = '简单的卡通风格人物剪影轮廓（不随邮箱哈希变化）'
T[(42, 'gitlens.defaultGravatarsStyle', 'enumDescriptions', 2)] = '不同颜色、面孔等的怪物图像'
T[(42, 'gitlens.defaultGravatarsStyle', 'enumDescriptions', 3)] = '8 位街机风格的像素化面孔'
T[(42, 'gitlens.defaultGravatarsStyle', 'enumDescriptions', 4)] = '不同颜色、面孔等的机器人图像'
T[(42, 'gitlens.defaultGravatarsStyle', 'enumDescriptions', 5)] = '具有不同特征和背景的面孔'
T[(42, 'gitlens.plusFeatures.enabled', 'markdownDescription', None)] = '指定是否隐藏或显示需要试用或 GitLens Pro 且在已打开仓库及当前试用或方案下不可访问的功能'
T[(42, 'gitlens.virtualRepositories.enabled', 'markdownDescription', None)] = '指定是否启用虚拟仓库支持'

# ============ cfg 43: Commit Signing ============
T[(43, 'gitlens.signing.showSignatureBadges', 'markdownDescription', None)] = '指定是否在 _提交图_ 和其他视图中显示提交的签名验证徽章'
T[(43, 'gitlens.signing.enableKeyGeneration', 'markdownDescription', None)] = '指定是否启用在 GitLens 内生成签名密钥的功能'

print(f'Defined translations so far: {len(T)}')

# ============ Apply translations ============
with open(EN_PATH, 'r', encoding='utf-8') as f:
    en = json.load(f)
with open(ZH_PATH, 'r', encoding='utf-8') as f:
    zh = json.load(f)

en_props_list = [c.get('properties', {}) for c in en['contributes']['configuration']]
zh_props_list = [c.get('properties', {}) for c in zh['contributes']['configuration']]

applied = 0
skipped_unchanged = 0
missing = 0

for (cfg_idx, prop_name, field, arr_idx), zh_val in T.items():
    if cfg_idx >= len(en_props_list):
        missing += 1
        continue
    en_prop = en_props_list[cfg_idx].get(prop_name)
    zh_prop = zh_props_list[cfg_idx].get(prop_name)
    if en_prop is None or zh_prop is None:
        missing += 1
        print(f'MISSING: cfg{cfg_idx} {prop_name}')
        continue
    en_val = en_prop.get(field)
    cur_val = zh_prop.get(field)
    if arr_idx is None:
        if cur_val is None:
            missing += 1
            continue
        if cur_val == en_val:
            zh_prop[field] = zh_val
            applied += 1
        else:
            skipped_unchanged += 1
    else:
        if not isinstance(cur_val, list) or arr_idx >= len(cur_val):
            missing += 1
            continue
        if cur_val[arr_idx] == en_val[arr_idx]:
            cur_val[arr_idx] = zh_val
            applied += 1
        else:
            skipped_unchanged += 1

print(f'Applied: {applied}, AlreadyTranslatedSkipped: {skipped_unchanged}, Missing: {missing}')

if applied > 0:
    with open(ZH_PATH, 'w', encoding='utf-8') as f:
        json.dump(zh, f, indent='\t', ensure_ascii=False)
        f.write('\n')
    print(f'Wrote {ZH_PATH}')
else:
    print('Nothing applied; file not modified')
