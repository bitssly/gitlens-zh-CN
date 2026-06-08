#!/usr/bin/env python3
"""
GitLens JS 文件翻译工具
对 dist/gitlens.js 进行字符串替换，翻译 UI 文本

用法:
    python translate_js.py apply      # 应用翻译
    python translate_js.py restore    # 恢复原版
    python translate_js.py preview    # 预览替换（不实际修改）
    python translate_js.py stats      # 显示翻译统计
    python translate_js.py extract    # 从 JS 中提取可翻译字符串
"""

import json
import sys
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# ============================================================
# 配置
# ============================================================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR = SCRIPT_DIR / "output"
TRANSLATIONS_FILE = DATA_DIR / "js-translations.json"

# GitLens 扩展搜索路径
EXTENSION_SEARCH_PATHS = [
    Path.home() / '.vscode' / 'extensions',
    Path.home() / '.cursor' / 'extensions',
    Path.home() / '.vscode-server' / 'extensions',
]

# JS 文件相对路径（在扩展目录下）
JS_FILES = [
    'dist/gitlens.js',
    # Webview 文件 - 用户实际看到的 UI
    'dist/webviews/graph.js',
    'dist/webviews/commitDetails.js',
    'dist/webviews/home.js',
    'dist/webviews/composer.js',
    'dist/webviews/patchDetails.js',
    'dist/webviews/rebase.js',
    'dist/webviews/timeline.js',
    'dist/webviews/settings.js',
    'dist/webviews/welcome.js',
]

# Webview 专用翻译字典
WEBVIEW_TRANSLATIONS_FILE = DATA_DIR / "webview-translations.json"


# ============================================================
# 工具函数
# ============================================================

def _load_dict(filepath):
    """从 JSON 文件加载翻译字典，过滤掉注释键"""
    if not filepath.exists():
        return OrderedDict()
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    translations = OrderedDict()
    for k, v in data.items():
        if k.startswith('_') or k.startswith('==='):
            continue
        if not isinstance(v, str) or not v:
            continue
        translations[k] = v
    return translations


def load_translations():
    """加载主翻译字典（gitlens.js 用）"""
    return _load_dict(TRANSLATIONS_FILE)


def load_webview_translations():
    """加载 Webview 专用翻译字典"""
    return _load_dict(WEBVIEW_TRANSLATIONS_FILE)


def load_all_translations():
    """合并所有翻译字典（主字典 + webview 字典）"""
    all_trans = load_translations()
    webview_trans = load_webview_translations()
    # webview 字典优先（如有冲突）
    all_trans.update(webview_trans)
    return all_trans


def find_gitlens_dirs():
    """查找所有 GitLens 扩展目录"""
    found = []
    for search_path in EXTENSION_SEARCH_PATHS:
        if not search_path.exists():
            continue
        for d in search_path.iterdir():
            if d.name.startswith('eamodio.gitlens-'):
                found.append(d)
    return found


def backup_file(filepath):
    """备份文件，返回备份路径"""
    backup_path = filepath.with_suffix(filepath.suffix + '.backup')
    if not backup_path.exists():
        shutil.copy2(filepath, backup_path)
        print(f"  已备份: {backup_path.name}")
    else:
        print(f"  备份已存在: {backup_path.name}")
    return backup_path


def restore_file(filepath):
    """从备份恢复文件"""
    backup_path = filepath.with_suffix(filepath.suffix + '.backup')
    if backup_path.exists():
        shutil.copy2(backup_path, filepath)
        print(f"  已恢复: {filepath.name}")
        return True
    else:
        print(f"  备份不存在: {backup_path.name}")
        return False


# ============================================================
# 翻译策略
# ============================================================

# 不翻译这些极短的通用词（在代码中太容易误匹配）
SKIP_SHORT = {
    "OK", "Yes", "No", "Back", "Next", "Error",
    "Path", "Name", "Type", "Size", "Date",
    "Save", "Edit", "Undo", "Redo", "Copy", "Open",
    "Close", "Auto", "None",
}

# 需要上下文匹配的短词（必须出现在 UI 属性值中才替换）
CONTEXT_SHORT = {
    "Cancel", "Apply", "Delete", "Refresh", "Browse", "Compare",
    "Fetch", "Push", "Pull", "Continue", "Skip", "Abort",
    "Confirm", "Reset", "Enable", "Disable", "Pin", "Choose",
    "Settings", "Accept", "Retry", "Sign In", "Restore",
    "Stash", "Revert", "Create", "Merge", "Rebase",
}

# 长字符串（>=10字符）可以直接安全替换（引号包裹）
LONG_STRING_MIN_LEN = 10

# UI 属性名 - 这些属性的值是面向用户的文本
UI_PROPERTY_NAMES = {
    'tooltip', 'label', 'title', 'detail', 'description',
    'markdownDescription', 'displayName', 'placeholder',
    'placeHolder', 'prompt', 'message', 'text',
    'enumDescription', 'markdownEnumDescriptions',
    # Lit 模板字面量 HTML 属性
    'content', 'slot', 'aria-label', 'aria-description',
}


def build_replacement_rules(translations):
    """
    构建替换规则列表。
    返回 (pattern, replacement, category) 元组列表。
    """
    rules = []

    for en, zh in translations.items():
        # 分类1: 长字符串（安全直接替换）
        if len(en) >= LONG_STRING_MIN_LEN:
            # 用正则精确匹配引号包裹的字符串
            # 匹配 "exact string" 但不匹配属性名
            escaped = re.escape(en)
            # 双引号字符串
            pattern_dq = f'"{escaped}"'
            # 单引号字符串
            pattern_sq = f"'{escaped}'"
            rules.append((pattern_dq, f'"{zh}"', 'long'))
            rules.append((pattern_sq, f"'{zh}'", 'long'))

        # 分类2: 中等长度字符串（需要在 UI 属性上下文中匹配）
        elif len(en) >= 3 and en not in SKIP_SHORT:
            escaped = re.escape(en)
            # 匹配 tooltip:"...", label:"...", title:"..." 等
            for prop in UI_PROPERTY_NAMES:
                # 双引号
                pattern = f'{prop}:"{escaped}"'
                replacement = f'{prop}:"{zh}"'
                rules.append((pattern, replacement, 'context'))
                # 单引号
                pattern = f"{prop}:'{escaped}'"
                replacement = f"{prop}:'{zh}'"
                rules.append((pattern, replacement, 'context'))
                # 冒号后有空格
                pattern = f'{prop}: "{escaped}"'
                replacement = f'{prop}: "{zh}"'
                rules.append((pattern, replacement, 'context'))
                pattern = f"{prop}: '{escaped}'"
                replacement = f"{prop}: '{zh}'"
                rules.append((pattern, replacement, 'context'))

            # 也匹配 return "string" 模式（条件返回的 UI 文本）
            if en in CONTEXT_SHORT or len(en) >= 6:
                rules.append((f'return"{escaped}"', f'return"{zh}"', 'return'))
                rules.append((f"return'{escaped}'", f"return'{zh}'", 'return'))
                rules.append((f'return "{escaped}"', f'return "{zh}"', 'return'))

    return rules


# ============================================================
# 备选策略：逐行扫描替换
# ============================================================

def apply_translations_scanning(content, translations):
    """
    扫描式替换：逐行处理，在合适的上下文中替换字符串。
    更安全但更慢。
    """
    replacement_count = 0
    replaced = {}  # en -> zh 记录实际替换的

    # 按长度降序排列翻译键，先替换长字符串避免子串问题
    sorted_keys = sorted(translations.keys(), key=len, reverse=True)

    for en in sorted_keys:
        zh = translations[en]

        # 策略1: 长字符串直接替换引号包裹的精确匹配
        if len(en) >= LONG_STRING_MIN_LEN:
            dq = f'"{en}"'
            sq = f"'{en}'"
            count = 0
            if dq in content:
                content = content.replace(dq, f'"{zh}"')
                count += content.count(f'"{zh}"')  # 不准确，改用下面的方式
                # 用 replace 返回值计数
                new_content = content.replace(f'"{zh}"', f'"{zh}"', 0)  # no-op
                count = 1  # 简化处理
                replaced[en] = zh

    # 使用更精确的方法
    return _apply_precise(content, translations)


def _apply_precise(content, translations):
    """精确替换：逐个翻译键，在内容中查找并替换"""
    replacement_count = 0
    replaced = OrderedDict()

    # 按长度降序排列，避免短字符串先替换导致长字符串匹配失败
    sorted_keys = sorted(translations.keys(), key=len, reverse=True)

    # 模板字面量中的 HTML 文本上下文标记
    # 匹配 >text< 或 >text</tag> 或 >text</  等模式
    TEMPLATE_HTML_PATTERNS = [
        '>{en}<',           # >text<
        '>{en}</',          # >text</
        '>{en} ',           # >text (后跟空格/属性)
        ' {en}<',           # text< (前有空格)
        '>{en}\n',          # >text\n
        '\n{en}<',          # \ntext<
        '>{en}`',           # >text` (模板字面量结束)
        '`{en}<',           # `text< (模板字面量开始)
        ' {en} ',           # 空格包裹
    ]

    for en in sorted_keys:
        zh = translations[en]

        # 跳过 SKIP_SHORT 中的极短词
        if en in SKIP_SHORT:
            continue

        if len(en) >= LONG_STRING_MIN_LEN:
            # 长字符串：直接替换引号包裹的精确匹配
            dq = f'"{en}"'
            new_content = content.replace(dq, f'"{zh}"')
            if new_content != content:
                count = content.count(dq)
                replacement_count += count
                replaced[en] = zh
                content = new_content

            # 长字符串：也替换模板字面量中的 HTML 文本内容
            # 只有当字符串包含英文字母且足够长时才替换
            if en in content and re.search(r'[A-Za-z]{3}', en):
                for pattern in TEMPLATE_HTML_PATTERNS:
                    old_pat = pattern.replace('{en}', en)
                    new_pat = pattern.replace('{en}', zh)
                    if old_pat in content:
                        new_content = content.replace(old_pat, new_pat)
                        if new_content != content:
                            n = content.count(old_pat)
                            replacement_count += n
                            replaced[en] = zh
                            content = new_content

        elif len(en) >= 3 and en not in SKIP_SHORT:
            # 中短字符串：只在 UI 属性上下文中替换
            count = 0
            for prop in UI_PROPERTY_NAMES:
                # JavaScript 对象属性语法: prop:"value" 或 prop: "value"
                for dq_style in [f'{prop}:"{en}"', f'{prop}: "{en}"',
                                 f"{prop}:'{en}'", f"{prop}: '{en}'"]:
                    if dq_style in content:
                        # 构建替换
                        if '"' in dq_style.split(':', 1)[1]:
                            rep = dq_style.replace(f'"{en}"', f'"{zh}"')
                        else:
                            rep = dq_style.replace(f"'{en}'", f"'{zh}'")
                        new_content = content.replace(dq_style, rep)
                        if new_content != content:
                            n = content.count(dq_style)
                            count += n
                            content = new_content

                # HTML/Lit 模板属性语法: prop="value" (用于模板字面量)
                for html_style in [f'{prop}="{en}"', f"{prop}='{en}'"]:
                    if html_style in content:
                        if '"' in html_style:
                            rep = html_style.replace(f'"{en}"', f'"{zh}"')
                        else:
                            rep = html_style.replace(f"'{en}'", f"'{zh}'")
                        new_content = content.replace(html_style, rep)
                        if new_content != content:
                            n = content.count(html_style)
                            count += n
                            content = new_content

            # return "string" 模式
            for ret_style in [f'return"{en}"', f"return'{en}'",
                              f'return "{en}"', f"return '{en}'"]:
                if ret_style in content:
                    if '"' in ret_style:
                        rep = ret_style.replace(f'"{en}"', f'"{zh}"')
                    else:
                        rep = ret_style.replace(f"'{en}'", f"'{zh}'")
                    new_content = content.replace(ret_style, rep)
                    if new_content != content:
                        n = content.count(ret_style)
                        count += n
                        content = new_content

            # case "string" 模式（switch case 返回文本）
            for case_style in [f'case"{en}"', f"case'{en}'",
                               f'case "{en}"', f"case '{en}'"]:
                if case_style in content:
                    if '"' in case_style:
                        rep = case_style.replace(f'"{en}"', f'"{zh}"')
                    else:
                        rep = case_style.replace(f"'{en}'", f"'{zh}'")
                    new_content = content.replace(case_style, rep)
                    if new_content != content:
                        n = content.count(case_style)
                        count += n
                        content = new_content

            # 三元表达式模式: ?"string" 或 ?"string":
            # 只匹配含空格的描述性字符串（避免误匹配代码标识符）
            if ' ' in en:
                for ternary_style in [f'?\"{en}\"', f'?\"{en}\":', f'?\"{en}\" ']:
                    if ternary_style in content:
                        rep = ternary_style.replace(f'"{en}"', f'"{zh}"')
                        new_content = content.replace(ternary_style, rep)
                        if new_content != content:
                            n = content.count(ternary_style)
                            count += n
                            content = new_content

            # 中短字符串：也替换模板字面量中的 HTML 文本（>=6字符且含英文）
            if len(en) >= 6 and en in content and re.search(r'[A-Za-z]{3}', en):
                for pattern in TEMPLATE_HTML_PATTERNS:
                    old_pat = pattern.replace('{en}', en)
                    new_pat = pattern.replace('{en}', zh)
                    if old_pat in content:
                        new_content = content.replace(old_pat, new_pat)
                        if new_content != content:
                            n = content.count(old_pat)
                            count += n
                            content = new_content

            if count > 0:
                replacement_count += count
                replaced[en] = zh

    return content, replacement_count, replaced


# ============================================================
# 命令实现
# ============================================================

def cmd_apply():
    """应用翻译到所有 JS 文件"""
    main_trans = load_translations()
    webview_trans = load_webview_translations()
    all_trans = load_all_translations()
    print(f"主字典: {len(main_trans)} 条 | Webview 字典: {len(webview_trans)} 条 | 合计: {len(all_trans)} 条\n")

    gitlens_dirs = find_gitlens_dirs()
    if not gitlens_dirs:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    print(f"找到 {len(gitlens_dirs)} 个 GitLens 安装:\n")

    for gitlens_dir in gitlens_dirs:
        print(f"--- {gitlens_dir.name} ---")
        total_count = 0
        for js_rel in JS_FILES:
            js_path = gitlens_dir / js_rel
            if not js_path.exists():
                print(f"  跳过: {js_rel} (不存在)")
                continue

            print(f"  处理: {js_rel}")

            # 备份
            backup_file(js_path)

            # 读取
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_size = len(content)

            # 选择字典：gitlens.js 用主字典，webview 文件用合并字典
            if js_rel == 'dist/gitlens.js':
                translations = main_trans
            else:
                translations = all_trans

            # 应用翻译
            content, count, replaced = _apply_precise(content, translations)

            # 写回
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(content)

            new_size = len(content)
            total_count += count
            print(f"    替换数: {count} | 大小: {original_size:,} -> {new_size:,} bytes")

            # 保存替换日志
            safe_name = js_rel.replace('/', '_').replace('\\', '_').replace('.js', '')
            log_path = OUTPUT_DIR / f"replaced_{gitlens_dir.name}_{safe_name}.json"
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(replaced, f, ensure_ascii=False, indent='\t')

        print(f"  合计替换: {total_count}\n")

    print("翻译应用完成！请重启 VS Code/Cursor 使翻译生效。")


def cmd_restore():
    """恢复原版 gitlens.js"""
    gitlens_dirs = find_gitlens_dirs()
    if not gitlens_dirs:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    for gitlens_dir in gitlens_dirs:
        print(f"--- {gitlens_dir.name} ---")
        for js_rel in JS_FILES:
            js_path = gitlens_dir / js_rel
            if js_path.exists():
                restore_file(js_path)
        print()

    print("恢复完成！请重启 VS Code/Cursor 生效。")


def cmd_preview():
    """预览替换（不实际修改文件）"""
    translations = load_translations()
    print(f"已加载 {len(translations)} 条翻译规则\n")

    gitlens_dirs = find_gitlens_dirs()
    if not gitlens_dirs:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    # 只预览第一个
    gitlens_dir = gitlens_dirs[0]
    js_path = gitlens_dir / JS_FILES[0]

    if not js_path.exists():
        print(f"错误: {js_path} 不存在")
        sys.exit(1)

    print(f"预览目标: {js_path}\n")

    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content, count, replaced = _apply_precise(content, translations)

    print(f"可替换字符串数: {count}")
    print(f"匹配翻译条目数: {len(replaced)}")
    print(f"未匹配翻译条目: {len(translations) - len(replaced)}")
    print()

    # 显示匹配到的
    print("=== 匹配到的翻译 ===")
    for en, zh in sorted(replaced.items()):
        print(f'  "{en}" -> "{zh}"')

    print()
    # 显示未匹配的
    not_matched = {k: v for k, v in translations.items() if k not in replaced}
    if not_matched:
        print(f"=== 未匹配的翻译 ({len(not_matched)} 条) ===")
        for en, zh in sorted(not_matched.items()):
            print(f'  "{en}" -> "{zh}"')


def cmd_stats():
    """显示翻译统计"""
    translations = load_translations()

    gitlens_dirs = find_gitlens_dirs()
    if not gitlens_dirs:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    print("GitLens JS 翻译统计")
    print("=" * 50)
    print(f"翻译字典条目数: {len(translations)}")
    print()

    for gitlens_dir in gitlens_dirs:
        js_path = gitlens_dir / JS_FILES[0]
        if not js_path.exists():
            continue

        print(f"--- {gitlens_dir.name} ---")
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        _, count, replaced = _apply_precise(content, translations)

        print(f"  文件大小: {len(content):,} bytes")
        print(f"  可替换字符串: {count} 处")
        print(f"  匹配翻译条目: {len(replaced)} / {len(translations)}")
        print(f"  覆盖率: {len(replaced)/len(translations)*100:.1f}%")
        print()


def cmd_extract():
    """从 gitlens.js 提取可能需要翻译的字符串"""
    gitlens_dirs = find_gitlens_dirs()
    if not gitlens_dirs:
        print("错误: 找不到 GitLens 扩展目录")
        sys.exit(1)

    js_path = gitlens_dirs[0] / JS_FILES[0]
    print(f"提取自: {js_path}\n")

    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 UI 属性值中的字符串
    ui_strings = set()

    # 模式1: 属性:"值"
    for prop in UI_PROPERTY_NAMES:
        pattern = rf'{prop}:"([^"{{}}]{{3,}})"'
        for m in re.finditer(pattern, content):
            s = m.group(1)
            if not s.startswith('$(') and not s.startswith('http'):
                ui_strings.add(s)

    # 模式2: return "值"
    for m in re.finditer(r'return"([^"]{4,})"', content):
        s = m.group(1)
        if re.search(r'[A-Z][a-z]', s):  # 含英文单词
            ui_strings.add(s)

    # 模式3: 长英文字符串（可能是消息）
    for m in re.finditer(r'"([A-Z][a-zA-Z\s,.\'!?;:()-]{15,})"', content):
        s = m.group(1)
        if not s.startswith('http') and not s.startswith('$('):
            ui_strings.add(s)

    # 过滤掉看起来像代码的
    filtered = set()
    for s in ui_strings:
        # 跳过含特殊字符的
        if any(c in s for c in ['\\n', '\\t', '\\r', '===', '!==', '&&', '||']):
            continue
        # 跳过像路径的
        if '/' in s and ('.' in s or 'dist' in s):
            continue
        # 跳过像 CSS 的
        if any(x in s for x in ['px', 'rgb', 'class', 'style']):
            continue
        filtered.add(s)

    # 保存
    sorted_strings = sorted(filtered)
    output_path = OUTPUT_DIR / 'extracted_strings.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_strings, f, ensure_ascii=False, indent='\t')

    print(f"提取到 {len(sorted_strings)} 个可翻译字符串")
    print(f"已保存到: {output_path}")

    # 同时输出文本版
    txt_path = OUTPUT_DIR / 'extracted_strings.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"# GitLens JS 可翻译字符串\n")
        f.write(f"# 提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 总数: {len(sorted_strings)}\n\n")
        for s in sorted_strings:
            f.write(f'"{s}"\n')

    print(f"文本版已保存到: {txt_path}")


def cmd_help():
    """显示帮助"""
    print("GitLens JS 文件翻译工具")
    print()
    print("用法:")
    print(f"  python {Path(__file__).name} apply      应用翻译到 gitlens.js")
    print(f"  python {Path(__file__).name} restore    恢复原版 gitlens.js")
    print(f"  python {Path(__file__).name} preview    预览替换（不修改文件）")
    print(f"  python {Path(__file__).name} stats      显示翻译统计")
    print(f"  python {Path(__file__).name} extract    提取可翻译字符串")
    print(f"  python {Path(__file__).name} help       显示此帮助")
    print()
    print("说明:")
    print("  此工具对 dist/gitlens.js 进行字符串替换，翻译 GitLens UI 文本。")
    print("  GitLens 更新后需重新运行 apply 命令。")
    print(f"  翻译字典: {TRANSLATIONS_FILE}")


def main():
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(exist_ok=True)

    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        'apply': cmd_apply,
        'restore': cmd_restore,
        'preview': cmd_preview,
        'stats': cmd_stats,
        'extract': cmd_extract,
        'help': cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"未知命令: {command}")
        cmd_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
