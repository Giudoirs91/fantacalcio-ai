import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ps = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
prev_inj = [p for p in ps if p.get('is_injured')]

print(f"Previously injured: {len(prev_inj)}")
for p in prev_inj:
    print(f"  [{p['team']}] {p['name']} (Rientro: {p.get('infortunio_rientro')}, Motivo: {str(p.get('infortunio_motivo'))[:35]})")
