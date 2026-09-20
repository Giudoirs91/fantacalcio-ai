import re

with open('chunks/b9e39b43-b5eda7c146674b07.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# search for all .js chunk references
matches = re.findall(r'(\d+):"([a-f0-9]+)"', code)
print(f"Found {len(matches)} chunk entries in b9e39b43:")
for m in matches:
    print(m)
