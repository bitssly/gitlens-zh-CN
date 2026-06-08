#!/usr/bin/env python3
"""
从 webview JS 文件中提取所有可能的 UI 字符串，
与翻译字典对比，找出未翻译的字符串。
"""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'output'

# GitLens 扩展路径
GITLENS_DIR = Path.home() / '.vscode' / 'extensions' / 'eamodio.gitlens-18.0.0'

# 加载现有翻译字典
def load_dict(path):
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith('_') and not k.startswith('===') and isinstance(v, str) and v}

main_dict = load_dict(DATA_DIR / 'js-translations.json')
webview_dict = load_dict(DATA_DIR / 'webview-translations.json')
all_dict = {**main_dict, **webview_dict}

# 框架内部字符串 - 跳过
SKIP_PATTERNS = [
    'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'Backspace',
    'CSS1Compat', 'AbortError', 'Assertion error', 'An error was suppressed',
    'Called getPending', 'Called hasSinks', 'Called hasSources',
    'Called introspectSinks', 'Called unwatch', 'Cannot access',
    'Cannot add the same', 'Color needs', 'CloseWatcher',
    'Unexpected private field', 'CSSLineClass', 'Minified React error',
    'StrictMode', 'Suspense', 'SuspenseList', 'Portal', 'Profiler',
    'Fragment', 'Object', 'string', 'object', 'default', 'badge',
    'RPC call failed', 'SHOW_MORE_COMMITS', 'CommitDiffSection-',
    'X.509', 'INPUT', 'Question', 'Permission', '• deserialized',
    '• invalid params', '• no params', 'wip', 'tracking', 'tip',
    'marge-target', 'create-pr', 'pick-file', 'integrations',
    'conflict-detection', 'stash',
]

def should_skip(s):
    """判断字符串是否应该跳过"""
    # 跳过太短的
    if len(s) < 3:
        return True
    # 跳过纯数字
    if s.strip().isdigit():
        return True
    # 跳过框架内部
    for pat in SKIP_PATTERNS:
        if pat in s:
            return True
    # 跳过 URL
    if s.startswith('http'):
        return True
    # 跳过含代码特征的
    if any(c in s for c in ['\\n', '\\t', '\\r', '===', '!==', '&&', '||', '{}', '[]']):
        return True
    # 跳过看起来像代码的
    if re.match(r'^[a-z]+\.[a-z]+', s):
        return True
    # 跳过 CSS 相关
    if any(x in s for x in ['px', 'rgb(', 'rgba(', 'class=', 'style=']):
        return True
    # 跳过已有翻译的
    if s in all_dict:
        return True
    return False


# UI 属性名
UI_PROPS = [
    'label', 'tooltip', 'title', 'detail', 'description',
    'placeholder', 'placeHolder', 'prompt', 'message', 'text',
]

all_strings = {}  # string -> set of files

webview_dir = GITLENS_DIR / 'dist' / 'webviews'
if not webview_dir.exists():
    print(f"错误: {webview_dir} 不存在")
    exit(1)

for js_file in sorted(webview_dir.glob('*.js')):
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    fname = js_file.name
    found = set()

    # 模式1: UI 属性值 (label:"...", tooltip:"..." 等)
    for prop in UI_PROPS:
        for m in re.finditer(rf'{prop}:"([^"]{{3,120}})"', content):
            s = m.group(1)
            if re.search(r'[A-Za-z]{{2}}', s) and not s.startswith('$('):
                found.add(s)

    # 模式2: return "String" (条件返回的 UI 文本)
    for m in re.finditer(r'return"([A-Z][^"]{{3,80}})"', content):
        found.add(m.group(1))

    # 模式3: case "String" (switch case)
    for m in re.finditer(r'case"([A-Z][^"]{{3,80}})"', content):
        found.add(m.group(1))

    # 模式4: 直接引号包裹的长英文字符串 (可能是消息/描述)
    for m in re.finditer(r'"([A-Z][a-zA-Z\s,.\'!?;:()\-]{10,120})"', content):
        s = m.group(1)
        if not s.startswith('$(') and not s.startswith('http'):
            found.add(s)

    for s in found:
        if s not in all_strings:
            all_strings[s] = set()
        all_strings[s].add(fname)

# 过滤
untranslated = {}
for s, files in sorted(all_strings.items()):
    if not should_skip(s):
        untranslated[s] = sorted(files)

# 输出结果
print(f"未翻译的 webview UI 字符串: {len(untranslated)} 个\n")

# 按文件分组统计
file_counts = {}
for s, files in untranslated.items():
    for f in files:
        file_counts[f] = file_counts.get(f, 0) + 1

print("按文件统计:")
for f, count in sorted(file_counts.items(), key=lambda x: -x[1]):
    print(f"  {f}: {count} 个")
print()

# 保存完整列表
out_path = OUTPUT_DIR / 'untranslated_webview.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(untranslated, f, ensure_ascii=False, indent='\t')

print(f"完整列表已保存到: {out_path}")

# 输出前 100 个示例
print("\n前 100 个未翻译字符串:")
for i, (s, files) in enumerate(sorted(untranslated.items())):
    if i >= 100:
        break
    print(f'  "{s}" ({", ".join(files)})')
