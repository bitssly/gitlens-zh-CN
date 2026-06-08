#!/usr/bin/env python3
"""
从 gitlens.js 中提取未翻译的 UI 字符串
"""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'

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

js_path = GITLENS_DIR / 'dist' / 'gitlens.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

UI_PROPS = ['label', 'tooltip', 'title', 'detail', 'description',
            'placeholder', 'placeHolder', 'prompt', 'message', 'text']

found = set()

# UI 属性值
for prop in UI_PROPS:
    for m in re.finditer(rf'{prop}:"([^"]{{3,120}})"', content):
        s = m.group(1)
        if re.search(r'[A-Za-z]{2}', s) and not s.startswith('$(') and not s.startswith('http'):
            found.add(s)

# return "String"
for m in re.finditer(r'return"([A-Z][^"]{3,80})"', content):
    found.add(m.group(1))

# case "String"
for m in re.finditer(r'case"([A-Z][^"]{3,80})"', content):
    found.add(m.group(1))

# 过滤
SKIP = [
    'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'Backspace',
    'CSS1Compat', 'AbortError', 'Assertion error', 'An error was suppressed',
    'Called getPending', 'Called hasSinks', 'Called hasSources',
    'Called introspectSinks', 'Called unwatch', 'Cannot access',
    'Cannot add the same', 'Color needs', 'CloseWatcher',
    'Minified React error', 'StrictMode', 'Suspense',
]

untranslated = {}
for s in found:
    if len(s) < 3:
        continue
    if s.strip().isdigit():
        continue
    if any(pat in s for pat in SKIP):
        continue
    if s.startswith('http'):
        continue
    if any(c in s for c in ['\\n', '\\t', '\\r', '===', '!==', '&&', '||']):
        continue
    if s in all_dict:
        continue
    untranslated[s] = True

print(f"gitlens.js 中未翻译的 UI 字符串: {len(untranslated)} 个\n")
for s in sorted(untranslated.keys()):
    print(f'  "{s}"')
