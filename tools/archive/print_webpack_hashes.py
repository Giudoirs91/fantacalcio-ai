import re

with open('webpack.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('a.u=')
snippet = code[idx:idx+3500]

hashes_snippet = snippet.split('+"."+({')[1].split('})[e]')[0]
hashes = dict(re.findall(r'(\d+):"([^"]+)"', hashes_snippet))

print(f"All {len(hashes)} chunk IDs in webpack.js:")
print(sorted([int(x) for x in hashes.keys()]))
