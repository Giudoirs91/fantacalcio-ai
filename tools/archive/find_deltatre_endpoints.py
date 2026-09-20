import re

with open('chunk_6972.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

matches = re.findall(r'https://seriea-api\.prd\.sdp\.deltatre\.digital/v1[^\s"\'`<>]+', code)
print(f"Deltatre URLs in chunk_6972: {len(matches)}")
for m in sorted(set(matches)):
    print(" ", m)

# Let's search for template endpoints with deltatre or stats
endpoints = re.findall(r'[`"\'](/v1/[^`"\']+)[\'"`]', code)
for ep in sorted(set(endpoints)):
    print(" Endpoint:", ep)

# Also check for player stats query functions
stats_funcs = re.findall(r'(\w+Stats|\w+Statistics|getPlayers|getPlayerStats)', code)
print("Stats funcs:", set(stats_funcs))
