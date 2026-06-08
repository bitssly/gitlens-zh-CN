"""
Apply Chinese translations to package-v18-zh-partial.json command titles.
Uses targeted text replacement to preserve TAB indentation.
"""
import json
import re

# Translation map: keyed by index in commands array
# Built from output/titles_to_translate.txt
TRANSLATIONS = {
    89: "复制远程分支 URL",
    791: "隐藏头像",
    792: "显示头像",
    793: "隐藏分支拉取请求",
    794: "显示分支拉取请求",
    795: "升序",
    796: "按日期排序分支",
    797: "按名称排序分支",
    798: "降序",
    799: "远程视图选项",
    800: "重命名分支...",
    801: "分组到 GitLens 视图",
    802: "复制",
    803: "刷新",
    804: "禁用自动刷新",
    805: "启用自动刷新",
    806: "以列表查看分支",
    807: "以树状查看分支",
    808: "隐藏分支比较",
    809: "显示分支比较",
    810: "隐藏分支上的贮藏",
    811: "显示分支上的贮藏",
    812: "自动查看文件",
    813: "以列表查看文件",
    814: "以树状查看文件",
    815: "隐藏头像",
    816: "显示头像",
    817: "隐藏分支比较",
    818: "显示分支比较",
    819: "隐藏分支",
    820: "显示分支",
    821: "隐藏提交",
    822: "显示提交",
    823: "隐藏贡献者",
    824: "显示贡献者",
    825: "隐藏分节",
    826: "隐藏远程",
    827: "显示远程",
    828: "隐藏贮藏",
    829: "显示贮藏",
    830: "隐藏标签",
    831: "显示标签",
    832: "隐藏当前分支状态",
    833: "显示当前分支状态",
    834: "隐藏工作树",
    835: "显示工作树",
    836: "升序",
    837: "按发现时间排序",
    838: "按最近获取时间排序",
    839: "按名称排序",
    840: "降序",
    841: "仓库视图选项",
    842: "将当前分支重置到上一个提交...",
    843: "将当前分支重置到提交...",
    844: "将当前分支重置到顶端...",
    845: "在文件资源管理器中展示",
    846: "在文件资源管理器中展示",
    847: "还原提交...",
    848: "分组所有视图",
    849: "分支",
    850: "分组分支视图",
    851: "分离分支视图",
    852: "设为默认视图",
    853: "隐藏分支视图",
    854: "显示分支视图",
    855: "提交",
    856: "分组提交视图",
    857: "分离提交视图",
    858: "设为默认视图",
    859: "隐藏提交视图",
    860: "显示提交视图",
    861: "贡献者",
    862: "分组贡献者视图",
    863: "分离贡献者视图",
    864: "设为默认视图",
    865: "隐藏贡献者视图",
    866: "显示贡献者视图",
    867: "分离所有视图",
    868: "文件历史",
    869: "分组文件历史视图",
    870: "分离文件历史视图",
    871: "设为默认视图",
    872: "隐藏文件历史视图",
    873: "显示文件历史视图",
    874: "启动面板",
    875: "分组启动面板视图",
    876: "分离启动面板视图",
    877: "设为默认视图",
    878: "隐藏启动面板视图",
    879: "显示启动面板视图",
    880: "刷新",
    881: "远程",
    882: "分组远程视图",
    883: "分离远程视图",
    884: "设为默认视图",
    885: "隐藏远程视图",
    886: "显示远程视图",
    887: "仓库",
    888: "分组仓库视图",
    889: "分离仓库视图",
    890: "设为默认视图",
    891: "隐藏仓库视图",
    892: "显示仓库视图",
    893: "重置所有视图",
    894: "搜索和比较",
    895: "分组搜索和比较视图",
    896: "分离搜索和比较视图",
    897: "设为默认视图",
    898: "隐藏搜索和比较视图",
    899: "显示搜索和比较视图",
    900: "贮藏",
    901: "分组贮藏视图",
    902: "分离贮藏视图",
    903: "设为默认视图",
    904: "隐藏贮藏视图",
    905: "显示贮藏视图",
    906: "标签",
    907: "分组标签视图",
    908: "分离标签视图",
    909: "设为默认视图",
    910: "隐藏标签视图",
    911: "显示标签视图",
    912: "工作树",
    913: "分组工作树视图",
    914: "分离工作树视图",
    915: "设为默认视图",
    916: "隐藏工作树视图",
    917: "显示工作树视图",
    918: "分组到 GitLens 视图",
    919: "清除结果",
    920: "复制",
    921: "刷新",
    922: "搜索提交...",
    923: "比较引用...",
    924: "自动查看文件",
    925: "以列表查看文件",
    926: "以树状查看文件",
    927: "隐藏头像",
    928: "显示头像",
    929: "交换比较",
    930: "搜索和比较视图选项",
    931: "选择以比较",
    932: "选择以比较",
    933: "选择以比较",
    934: "选择以比较",
    935: "选择以比较",
    936: "与分支 (HEAD) 比较",
    937: "与工作树比较",
    938: "隐藏贡献者统计",
    939: "显示贡献者统计",
    940: "按作者筛选提交...",
    941: "清除筛选",
    942: "清除筛选",
    943: "仅显示左侧文件",
    944: "仅显示右侧文件",
    945: "隐藏日期标记",
    946: "显示日期标记",
    947: "暂存所有更改",
    948: "暂存更改",
    949: "暂存更改",
    950: "暂存更改",
    951: "分组到 GitLens 视图",
    952: "复制",
    953: "筛选仓库...",
    954: "刷新",
    955: "自动查看文件",
    956: "以列表查看文件",
    957: "以树状查看文件",
    958: "贮藏视图选项",
    959: "检出提交...",
    960: "检出标签...",
    961: "分组到 GitLens 视图",
    962: "复制",
    963: "筛选仓库...",
    964: "刷新",
    965: "自动查看文件",
    966: "以列表查看文件",
    967: "以树状查看文件",
    968: "以列表查看",
    969: "以树状查看",
    970: "隐藏头像",
    971: "显示头像",
    972: "升序",
    973: "按日期排序",
    974: "按名称排序",
    975: "降序",
    976: "标签视图选项",
    977: "刷新",
    978: "创建分支...",
    979: "创建标签...",
    980: "创建工作树...",
    981: "撤销提交",
    982: "取消暂存所有更改",
    983: "取消暂存更改",
    984: "取消暂存更改",
    985: "取消暂存更改",
    986: "关闭欢迎页",
    987: "刷新",
    988: "添加仓库...",
    989: "从关联工作区添加仓库...",
    990: "更改关联工作区自动添加行为...",
    991: "转换为云端工作区...",
    992: "复制",
    993: "创建云端工作区...",
    994: "创建 VS Code 工作区...",
    995: "删除工作区...",
    996: "了解云端工作区...",
    997: "定位仓库...",
    998: "在当前窗口中打开 VS Code 工作区...",
    999: "在新窗口中打开 VS Code 工作区...",
    1000: "刷新",
    1001: "将仓库添加到 VS Code 工作区",
    1002: "定位仓库...",
    1003: "打开仓库",
    1004: "在新窗口中打开仓库",
    1005: "从工作区移除...",
    1006: "分组到 GitLens 视图",
    1007: "复制",
    1008: "筛选仓库...",
    1009: "刷新",
    1010: "自动查看文件",
    1011: "以列表查看文件",
    1012: "以树状查看文件",
    1013: "以列表查看",
    1014: "以树状查看",
    1015: "隐藏头像",
    1016: "显示头像",
    1017: "隐藏分支比较",
    1018: "显示分支比较",
    1019: "隐藏分支拉取请求",
    1020: "显示分支拉取请求",
    1021: "隐藏贮藏",
    1022: "显示贮藏",
    1023: "升序",
    1024: "按日期排序",
    1025: "按名称排序",
    1026: "降序",
    1027: "工作树视图选项",
    1028: "打开可视化文件历史",
    1029: "打开可视化文件历史",
    1030: "打开可视化文件历史",
    1031: "打开可视化文件历史",
    1032: "打开可视化文件历史",
    1033: "打开可视化文件历史",
    1034: "打开可视化文件历史",
    1035: "打开可视化文件夹历史",
    1036: "打开可视化文件夹历史",
    1037: "打开可视化文件夹历史",
    1038: "打开可视化文件夹历史",
    1039: "可视化仓库历史",
    1040: "可视化仓库历史",
}

print(f'Loaded {len(TRANSLATIONS)} translations')

# Load English JSON for source titles
with open('data/package-v18-en.json', 'r', encoding='utf-8') as f:
    en = json.load(f)
en_cmds = en['contributes']['commands']

# Load zh JSON to verify
with open('data/package-v18-zh-partial.json', 'r', encoding='utf-8') as f:
    zh = json.load(f)
zh_cmds = zh['contributes']['commands']

# Read raw text
with open('data/package-v18-zh-partial.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# For each idx, find the command block in raw text and replace title
modified = 0
for idx in sorted(TRANSLATIONS.keys()):
    cmd_id = en_cmds[idx]['command']
    en_title = en_cmds[idx]['title']
    zh_title = zh_cmds[idx].get('title', '')
    new_title = TRANSLATIONS[idx]

    # Skip if zh already has this Chinese translation
    if zh_title == new_title:
        continue

    # Verify zh currently has English title (which is what untranslated.txt says)
    if zh_title != en_title:
        # zh has some other Chinese - we still want to overwrite if title is in untrans list
        # But here, since we filtered to only entries where title is untranslated (=English),
        # zh_title should equal en_title. If not, skip with warning.
        print(f'WARN idx={idx} cmd={cmd_id}: zh.title="{zh_title}" != en.title="{en_title}" - SKIP')
        continue

    # Build pattern: "command": "<cmd_id>", possibly with various whitespace,
    # then look for the "title": "<en_title>" within the same object.
    # Escape regex special chars in cmd_id and en_title
    cmd_pat = re.escape(cmd_id)
    title_pat = re.escape(en_title)

    # Find the command id occurrence in the file
    cmd_marker = f'"command": "{cmd_id}"'
    cmd_pos = raw.find(cmd_marker)
    if cmd_pos == -1:
        print(f'ERROR: cannot find command marker for idx={idx} cmd={cmd_id}')
        continue

    # Find the closing brace of this command object - search for next standalone "}"
    # We will look for the next `"title": "<en_title>"` within a small window after the cmd_marker
    title_marker = f'"title": "{en_title}"'
    title_pos = raw.find(title_marker, cmd_pos)
    # The title can appear before or after command. Also check before cmd_pos within the same object.
    # The object is bracketed by { ... }. Find the enclosing { for cmd_pos.
    # Walk backward to find '{' for this object
    obj_start = cmd_pos
    while obj_start > 0 and raw[obj_start] != '{':
        obj_start -= 1
    # Find matching '}'
    depth = 0
    obj_end = obj_start
    while obj_end < len(raw):
        c = raw[obj_end]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        obj_end += 1
    block = raw[obj_start:obj_end + 1]
    # Find title in block
    block_title_pos = block.find(title_marker)
    if block_title_pos == -1:
        print(f'ERROR: cannot find title marker for idx={idx} cmd={cmd_id} title={en_title!r}')
        continue
    new_title_marker = f'"title": "{new_title}"'
    new_block = block[:block_title_pos] + new_title_marker + block[block_title_pos + len(title_marker):]
    raw = raw[:obj_start] + new_block + raw[obj_end + 1:]
    modified += 1

print(f'Modified {modified} entries')

# Write back
with open('data/package-v18-zh-partial.json', 'w', encoding='utf-8') as f:
    f.write(raw)

# Verify
with open('data/package-v18-zh-partial.json', 'r', encoding='utf-8') as f:
    zh2 = json.load(f)
print('JSON re-load OK, len:', len(zh2['contributes']['commands']))
