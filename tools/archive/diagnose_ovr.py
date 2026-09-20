import json
import pandas as pd

with open('processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

print("=== CHECKING TARGET PLAYERS ===")
for target in ['Dovbyk', 'Raspadori', 'Retegui', 'Lookman', 'Gudmundsson', 'Morata', 'Lukaku', 'Vlahovic', 'Kean', 'Castellanos', 'Soulé', 'Nico Gonzalez']:
    found = [p for p in players if target.lower() in p['name'].lower()]
    for p in found:
        print(f"Nome: {p['name']} | Squadra: {p['team']} | FVM: {p['fvm']} | Presenze: {p['presenze']} | FM: {p['fm']} | MV: {p['mv']} | Titolarità: {p['titolarita']}% | in_11: {p['is_in_11']} | OVR: {p['ovr']} | Prezzo: {p['prezzo_cons']}")

print("\n=== PLAYERS WITH FVM > 30 BUT OVR <= 60 ===")
outliers = [p for p in players if p['fvm'] > 30 and p['ovr'] <= 60]
for p in outliers[:25]:
    print(f"Nome: {p['name']} ({p['team']}) | FVM: {p['fvm']} | Presenze: {p['presenze']} | FM: {p['fm']} | Tit: {p['titolarita']}% | in_11: {p['is_in_11']} | OVR: {p['ovr']}")
