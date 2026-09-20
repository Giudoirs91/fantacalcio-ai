import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

print("--- FROSINONE ATTACKERS ---")
fros_players = [p for p in players if p['team'] == 'Frosinone' and p['role'] == 'A']
for p in fros_players:
    print(json.dumps(p, indent=2, ensure_ascii=False))

