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

def get_cost(name):
    clean = name.lower().strip()
    if clean in real_prices:
        return real_prices[clean]
    p = master_dict.get(clean)
    if p:
        return p.get('prezzo_cons', 1)
    return 1

print("=== TUTTI I BALLOTTAGGI / COPPIE DI CLUB UFFICIALI 2026/27 ===")
for team, data in tactical_db.items():
    coach = data.get('all')
    bals = data.get('ballottaggi', [])
    print(f"\n--- {team} (All: {coach}) ---")
    seen = set()
    for b in bals:
        p1 = b['player']
        vs = b['vs']
        p2 = vs.split('(')[0].strip()
        pair_key = tuple(sorted([p1.lower(), p2.lower()]))
        if pair_key not in seen:
            seen.add(pair_key)
            c1 = get_cost(p1)
            c2 = get_cost(p2)
            role1 = master_dict.get(p1.lower().strip(), {}).get('role', '?')
            role2 = master_dict.get(p2.lower().strip(), {}).get('role', '?')
            print(f"  [{role1}] {p1} ({c1} CR, {b['pct']}%)  <--->  {p2} ({c2} CR) | Costo Coppia: {c1 + c2} CR")
