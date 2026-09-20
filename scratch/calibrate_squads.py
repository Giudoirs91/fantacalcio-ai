import json

with open('processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Build a lookup by role & name
by_role = {'P': [], 'D': [], 'C': [], 'A': []}
p_dict = {}
for p in players:
    by_role[p['role']].append(p)
    p_dict[(p['role'], p['name'].lower())] = p

print(f"Total players loaded: {len(players)}")

# We need prices for key players that reflect empirical auction costs in 1000 CR:
# Top striker: 380-420 CR
# Second striker / winger: 90-140 CR
# Third striker: 25-45 CR
# Low-cost strikers: 1-5 CR
# Top Midfielder: 90-140 CR
# Semi-top Midfielder: 40-70 CR
# Regular Midfielders: 10-30 CR
# Low-cost Midfielders: 1-2 CR
# Top Defender: 30-55 CR
# Regular Defenders: 5-15 CR
# Low-cost Defenders: 1-2 CR
# Top Goalkeeper trio: 80-110 CR
# Mid/low Goalkeeper trio: 40-60 CR
