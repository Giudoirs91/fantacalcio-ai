import re

with open('chunk_6972.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# Let's search for player stats data structures or methods
# Notice in React components or query hooks: usePlayerStats, getPlayerStats, etc.
matches = re.findall(r'(\w+)\s*=\s*async\s*\([^)]*\)\s*=>\s*\{[^}]*stats[^}]*\}', code)
print(f"Async stats functions: {len(matches)}")

# Let's search for strings matching /seasons/ or /competitions/ or /stats/
routes = re.findall(r'`([^`]*(?:/seasons/|/competitions/|/stats/|/players/|/football/)[^`]*)`', code)
print(f"Template routes found: {len(routes)}")
for r in set(routes):
    print("  Route:", r)
