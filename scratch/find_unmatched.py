import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ps = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
for q in ['pellegri', 'israel', 'cande', 'franjic', 'bah', 'nuredini', 'sulemana']:
    found = [p for p in ps if q in p['name'].lower()]
    print(f"{q}: {[(p['name'], p['team'], p['id']) for p in found]}")
