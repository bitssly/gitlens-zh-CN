"""Verify the translated package json: parses, has correct line count, and spot check a few translations."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH_PATH = os.path.join(ROOT, 'data', 'package-v18-zh-partial.json')
EN_PATH = os.path.join(ROOT, 'data', 'package-v18-en.json')

with open(ZH_PATH, 'r', encoding='utf-8') as f:
    raw = f.read()
zh = json.loads(raw)
en = json.load(open(EN_PATH, 'r', encoding='utf-8'))

print(f'JSON parsed OK, file size: {len(raw):,} chars, lines: {raw.count(chr(10))}')

# Spot check
checks = [
    (8, 'gitlens.graph.autoFetch.enabled', 'markdownDescription'),
    (30, 'gitlens.rebaseEditor.density', 'markdownDescription'),
    (34, 'gitlens.ai.enabled', 'markdownDescription'),
    (41, 'gitlens.telemetry.enabled', 'markdownDescription'),
    (43, 'gitlens.signing.showSignatureBadges', 'markdownDescription'),
]
for cfg_idx, prop, field in checks:
    en_v = en['contributes']['configuration'][cfg_idx]['properties'][prop].get(field)
    zh_v = zh['contributes']['configuration'][cfg_idx]['properties'][prop].get(field)
    same = '⚠ STILL EN' if zh_v == en_v else 'OK'
    print(f'[{same}] cfg{cfg_idx} {prop}: {zh_v[:80]}...')

# Count remaining untranslated in our scope
remaining = 0
for cfg_idx, c in enumerate(zh['contributes']['configuration']):
    en_c = en['contributes']['configuration'][cfg_idx]
    for prop, zh_prop in c.get('properties', {}).items():
        en_prop = en_c.get('properties', {}).get(prop, {})
        for field in ('markdownDescription', 'description'):
            if field in zh_prop and field in en_prop:
                if zh_prop[field] == en_prop[field] and len(en_prop[field]) > 5:
                    remaining += 1
        for field in ('enumDescriptions', 'markdownEnumDescriptions'):
            if field in zh_prop and field in en_prop:
                for i, (z, e) in enumerate(zip(zh_prop[field], en_prop[field])):
                    if z == e and isinstance(z, str) and len(z) > 1:
                        remaining += 1
print(f'Remaining untranslated description-like entries: {remaining}')
