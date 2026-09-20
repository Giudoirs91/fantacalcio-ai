import re

with open('chunk_6972.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# search for path templates like "/players", "/stats", "/teams", "/matches", "/competitions"
matches = re.findall(r'[`"\'](/[a-zA-Z0-9_\-/{}]+)[\'"`]', code)
interesting = []
for m in sorted(set(matches)):
    if any(k in m for k in ['stats', 'player', 'team', 'season', 'comp', 'leader', 'table', 'standings', 'ranking', 'match']):
        interesting.append(m)

print(f"Found {len(interesting)} interesting endpoint paths:")
for item in interesting:
    print("  ->", item)
