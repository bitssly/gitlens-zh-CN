"""
Extract all untranslated markdownDescription and enumDescriptions in
contributes.configuration[*].properties.* from package-v18-zh-partial.json.

A field is "untranslated" if zh value equals en value.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_PATH = os.path.join(ROOT, 'data', 'package-v18-en.json')
ZH_PATH = os.path.join(ROOT, 'data', 'package-v18-zh-partial.json')

with open(EN_PATH, 'r', encoding='utf-8') as f:
    en = json.load(f)
with open(ZH_PATH, 'r', encoding='utf-8') as f:
    zh = json.load(f)

en_configs = en['contributes']['configuration']
zh_configs = zh['contributes']['configuration']

# We'll output: a list of records: (cfg_idx, prop_name, field, idx_in_array_or_None, en_value, zh_value)
records = []

for ci, (en_c, zh_c) in enumerate(zip(en_configs, zh_configs)):
    en_props = en_c.get('properties', {})
    zh_props = zh_c.get('properties', {})
    for prop_name, en_prop in en_props.items():
        zh_prop = zh_props.get(prop_name, {})
        # markdownDescription
        for field in ('markdownDescription', 'description'):
            if field in en_prop:
                en_val = en_prop[field]
                zh_val = zh_prop.get(field, '')
                if zh_val == en_val and isinstance(en_val, str):
                    records.append({
                        'cfg_idx': ci,
                        'prop_name': prop_name,
                        'field': field,
                        'arr_idx': None,
                        'en': en_val,
                    })
        # enumDescriptions and markdownEnumDescriptions (arrays)
        for field in ('enumDescriptions', 'markdownEnumDescriptions'):
            if field in en_prop:
                en_arr = en_prop[field]
                zh_arr = zh_prop.get(field, [])
                if isinstance(en_arr, list):
                    for i, en_v in enumerate(en_arr):
                        zh_v = zh_arr[i] if i < len(zh_arr) else ''
                        if zh_v == en_v and isinstance(en_v, str):
                            records.append({
                                'cfg_idx': ci,
                                'prop_name': prop_name,
                                'field': field,
                                'arr_idx': i,
                                'en': en_v,
                            })

print(f'Total untranslated config description fields: {len(records)}')
# Write to file for inspection
out_path = os.path.join(ROOT, 'output', 'config_descriptions_untranslated.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
print(f'Written to {out_path}')

# Group counts
from collections import Counter
c = Counter((r['field'],) for r in records)
print(c)

# Print first 5 records
for r in records[:5]:
    print(r)
