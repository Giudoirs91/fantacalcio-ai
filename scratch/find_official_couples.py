import json
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('config/tactical_db.json', encoding='utf-8') as f:
    tactical_db = json.load(f)

wb = openpyxl.load_workbook('data/raw/lega-ferrovia-rosters-1788691861822.xlsx', data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

header = rows[0]
teams = [(header[i], i) for i in range(0, len(header), 3) if header[i]]

real_prices = {}
for r in rows[1:]:
    for t_name, col_idx in teams:
        name = r[col_idx]
        cost = r[col_idx + 1]
        if name and cost is not None:
            clean = str(name).strip().lower()
            if clean not in real_prices:
                real_prices[clean] = int(cost)

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    master = json.load(f)
master_dict = {p['name'].lower().strip(): p for p in master}

print("=== IDENTIFICAZIONE COPPIE TATTICHE UFFICIALI 2026/27 ===")
for team, data in tactical_db.items():
    coach = data.get('all')
    print(f"\nCLUB: {team} (All: {coach})")
    players = data.get('players', {})
    for p_name, p_info in players.items():
        role = p_info.get('ruolo')
        status = p_info.get('status', '')
        oop = p_info.get('oop_desc', '')
        cost = real_prices.get(p_name.lower().strip())
        if cost is None:
            p_obj = master_dict.get(p_name.lower().strip())
            cost = p_obj.get('prezzo_cons', 1) if p_obj else 1
        
        # Look for ballottaggio / rotations / pairings
        if 'vs' in status or 'ballottaggio' in status.lower() or 'rotazione' in status.lower() or 'vs' in oop or 'sub' in status.lower():
            print(f"  - {p_name} ({role}): {cost} CR | {status} {oop}")
