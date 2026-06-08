#!/usr/bin/env python3
"""
提取 untranslated.txt 中的用户可见字段（title/description/label/name/detail/displayName）
仅提取以这些后缀结尾的路径，跳过技术性字段。
输出到 output/visible_untrans.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"

# 用户可见字段（含数组项）。markdownDeprecationMessage / deprecationMessage 也是显示在 settings UI 上的提示
VISIBLE_FIELDS = (
    'title', 'description', 'label', 'name', 'detail',
    'displayName', 'markdownDescription', 'contextualTitle',
    'enumDescriptions', 'markdownEnumDescriptions',
    'deprecationMessage', 'markdownDeprecationMessage',
    'statusBarItemName',
)

# 跳过这些字段
SKIP_PATHS = (
    '.command', '.id', '.when', '.icon', '.enablement', '.key',
    '.scope', '.category', '.group', '.path', '.version', '.publisher',
    '.repository', '.engines', '.main', '.browser', '.bugs', '.author',
    '.badges', '.activationEvents', '.qna', '.homepage', '.icon',
    '.preview', '.l10n', '.capabilities', '.extensionDependencies',
    '.extensionPack', '.keywords',
)

def is_visible_path(path: str) -> bool:
    if '.defaults.' in path:
        return False
    m = re.search(r'\.([a-zA-Z]+)(\[\d+\])?$', path)
    if not m:
        return False
    return m.group(1) in VISIBLE_FIELDS


def main():
    untranslated = json.loads((OUT / 'untranslated.json').read_text(encoding='utf-8'))
    visible = {p: t for p, t in untranslated.items() if is_visible_path(p)}
    # 按字段类型统计
    by_suf = {}
    for p in visible:
        m = re.search(r'\.([a-zA-Z]+)(\[\d+\])?$', p)
        if m:
            by_suf[m.group(1)] = by_suf.get(m.group(1), 0) + 1
    (OUT / 'visible_untrans.json').write_text(
        json.dumps(visible, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'用户可见未翻译条数: {len(visible)}')
    for suf, n in sorted(by_suf.items(), key=lambda x: -x[1]):
        print(f'  {suf}: {n}')


if __name__ == '__main__':
    main()
