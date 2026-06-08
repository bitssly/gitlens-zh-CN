#!/usr/bin/env python3
"""从 webview JS 文件中提取可翻译字符串"""
import re, json
from pathlib import Path

base = Path.home() / '.vscode' / 'extensions' / 'eamodio.gitlens-18.0.0'

all_strings = set()

for js_file in sorted((base / 'dist' / 'webviews').glob('*.js')):
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # label:"..."
    for m in re.finditer(r'label:"([^"]{3,80})"', content):
        s = m.group(1)
        if re.search(r'[A-Za-z]{2}', s) and not s.startswith('$('):
            all_strings.add(s)

    # tooltip:"..."
    for m in re.finditer(r'tooltip:"([^"]{3,80})"', content):
        all_strings.add(m.group(1))

    # placeholder:"..."
    for m in re.finditer(r'placeholder:"([^"]{3,80})"', content):
        all_strings.add(m.group(1))

    # title:"..."
    for m in re.finditer(r'title:"([^"]{3,80})"', content):
        s = m.group(1)
        if re.search(r'[A-Za-z]{2}', s) and not s.startswith('http'):
            all_strings.add(s)

    # return "String"
    for m in re.finditer(r'return"([A-Z][^"]{4,60})"', content):
        all_strings.add(m.group(1))

    # detail:"..."
    for m in re.finditer(r'detail:"([^"]{5,80})"', content):
        s = m.group(1)
        if re.search(r'[A-Za-z]{2}', s):
            all_strings.add(s)

    # message:"..."
    for m in re.finditer(r'message:"([^"]{5,80})"', content):
        s = m.group(1)
        if re.search(r'[A-Za-z]{2}', s):
            all_strings.add(s)

# Filter out framework internals
skip_patterns = [
    'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'Backspace',
    'CSS1Compat', 'AbortError', 'Assertion error', 'An error was suppressed',
    'Called getPending', 'Called hasSinks', 'Called hasSources',
    'Called introspectSinks', 'Called unwatch', 'Cannot access',
    'Cannot add the same', 'Color needs', 'CloseWatcher',
    'Unexpected private field', 'Agent Activity Treemap',
    'CSSLineClass', 'hasSources without', 'hasSinks without',
]

filtered = set()
for s in all_strings:
    if any(skip in s for skip in skip_patterns):
        continue
    if s.startswith('http'):
        continue
    filtered.add(s)

sorted_strings = sorted(filtered)

out = Path('output/webview_extracted.txt')
with open(out, 'w', encoding='utf-8') as f:
    f.write(f'Extracted from webview files: {len(sorted_strings)} strings\n\n')
    for s in sorted_strings:
        f.write(f'{s}\n')

print(f'Extracted {len(sorted_strings)} strings -> {out}')
