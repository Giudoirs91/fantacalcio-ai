with open('chunk_7936.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

import re
matches = re.findall(r'childrenComponentName:"([^"]+)"', code)
print("Component names in chunk_7936:", set(matches))

for name in set(matches):
    if 'player' in name or 'stat' in name:
        idx = code.find(f'childrenComponentName:"{name}"')
        print(f"\n=== Component: {name} ===")
        print(code[max(0, idx-500):min(len(code), idx+1000)])
