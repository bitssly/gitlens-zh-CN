import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('data/package-v18-en.json', encoding='utf-8'))
configs = en['contributes']['configuration']
for i, c in enumerate(configs):
    title = c.get('title', '')
    cid = c.get('id', '')
    props = list(c.get('properties', {}).keys())[:3]
    print(f"{i}|{cid}|{title}|{props}")
