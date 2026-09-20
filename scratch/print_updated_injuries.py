import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ps = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
inj = [p for p in ps if p.get('is_injured')]
print(f"Total injured in master: {len(inj)}")

teams = {}
for p in inj:
    teams.setdefault(p['team'], []).append(p)

for tm in sorted(teams.keys()):
    print(f"\n--- {tm.upper()} ({len(teams[tm])} infortunati) ---")
    for p in teams[tm]:
        print(f"  • {p['name']} ({p['role']}) - Rientro: {p.get('infortunio_rientro')} | {p.get('infortunio_motivo')} | {p.get('ai_advice')}")
