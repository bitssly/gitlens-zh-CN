import json
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'output/config_descriptions_untranslated.json'), encoding='utf-8'))
lines = []
for i, r in enumerate(d):
    cfg = r['cfg_idx']
    if cfg < 30 or cfg > 37:
        continue
    en = r['en'].replace('\n', ' \\n ')
    lines.append(f"{i}|{cfg}|{r['prop_name']}|{r['field']}|{r['arr_idx']}|{en[:280]}")
with open(os.path.join(ROOT, 'output/list_untrans3.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'wrote {len(lines)} lines')
