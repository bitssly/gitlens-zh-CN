"""Test if json.dump(indent='\\t', ensure_ascii=False) is round-trip stable."""
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/package-v18-zh-partial.json', 'r', encoding='utf-8') as f:
    raw = f.read()
obj = json.loads(raw)

dump = json.dumps(obj, indent='\t', ensure_ascii=False)
# Add trailing newline if original has it
if raw.endswith('\n') and not dump.endswith('\n'):
    dump += '\n'

if raw == dump:
    print('ROUND-TRIP STABLE')
else:
    print('NOT STABLE - differences:')
    # Find first difference
    for i, (a, b) in enumerate(zip(raw, dump)):
        if a != b:
            print(f'First diff at char {i}: orig={a!r} ({hex(ord(a))}), dump={b!r} ({hex(ord(b))})')
            print(f'Context orig: {raw[max(0,i-50):i+50]!r}')
            print(f'Context dump: {dump[max(0,i-50):i+50]!r}')
            break
    print(f'len orig={len(raw)} len dump={len(dump)}')
