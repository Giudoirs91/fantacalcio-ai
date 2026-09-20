import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

gks_by_team = {}
for p in players:
    if p['role'] == 'P':
        team = p['team']
        if team not in gks_by_team:
            gks_by_team[team] = []
        gks_by_team[team].append(f"{p['name']} (OVR {p['ovr']}, Prezzo {p['prezzo_cons']} CR, Advice: {p['ai_advice']})")

print(f"Total Goalkeepers in Listone 2026/27: {sum(len(v) for v in gks_by_team.values())}")
for tm, gks in sorted(gks_by_team.items()):
    print(f"\n{tm.upper()}:")
    for g in gks:
        print(f"  - {g}")
