import sys
import json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ps = json.load(open('processed_players_master.json', encoding='utf-8'))

# Players with G3 appearances
p3 = [p for p in ps if p.get('presenze_2627', 0) == 3]
print(f"Giocatori con 3 presenze su 3: {len(p3)}")

# Top scorers / contributors in G3
scorers = [p for p in ps if p.get('gol_2627', 0) > 0]
scorers.sort(key=lambda x: x.get('gol_2627', 0), reverse=True)

print("\n--- TOP MARCATORI 2026/27 (con G3) ---")
for p in scorers[:12]:
    print(f"• {p['name']} ({p['team']}) - Gol 26/27: {p['gol_2627']}, Assist: {p['assist_2627']}, OVR: {p['ovr']}, Prezzo Cons: {p['prezzo_cons']} crediti, Consiglio: {p['consiglio']}")

# Top assist men in G3
assisters = [p for p in ps if p.get('assist_2627', 0) > 0]
assisters.sort(key=lambda x: x.get('assist_2627', 0), reverse=True)
print("\n--- TOP ASSIST-MAN 2026/27 ---")
for p in assisters[:6]:
    print(f"• {p['name']} ({p['team']}) - Assist 26/27: {p['assist_2627']}, Gol: {p['gol_2627']}, OVR: {p['ovr']}, Prezzo Cons: {p['prezzo_cons']}")

# Goalkeepers update
gks = [p for p in ps if p['role'] == 'P' and p.get('presenze_2627', 0) > 0]
gks.sort(key=lambda x: x.get('ovr', 0), reverse=True)
print("\n--- PORTIERI MONITORATI 2026/27 ---")
for p in gks[:8]:
    print(f"• {p['name']} ({p['team']}) - Presenze: {p['presenze_2627']}, Gol Subiti: {p['gol_subiti_2627']}, Parate: {p['parate_2627']}, Clean Sheets: {p['clean_sheets_2627']}, OVR: {p['ovr']}, Prezzo: {p['prezzo_cons']}")

# Titolarità impact
titolari_fissi = [p for p in ps if p.get('starts_2627', 0) >= 3]
print(f"\nCalciatori sempre titolari (3 su 3 finora): {len(titolari_fissi)}")
