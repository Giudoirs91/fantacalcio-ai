import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
ps = json.load(open('processed_players_master.json', encoding='utf-8'))
checks = ['Martinez L.', 'Douvikas', 'Soulè', 'Krstovic', 'Svilar', 'Palmisani', 'Robinson', 'Bremer', 'Carnesecchi', 'Nico Paz']

for name in checks:
    matched = [p for p in ps if name.lower() in p['name'].lower()]
    if matched:
        p = matched[0]
        print(f"• {p['name']} ({p['team']}): Titolarità {p['titolarita']}% [{p['titolarita_desc_2627']}] | OVR: {p['ovr']} | Consiglio: {p['consiglio']}")
