import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('output/config_descriptions_untranslated.json', encoding='utf-8'))
for i, r in enumerate(d):
    if i < 488:
        continue
    print(f"{i}|{r['cfg_idx']}|{r['prop_name']}|{r['field']}|{r['arr_idx']}|{r['en'][:300]}")
