import sys
import os
import pandas as pd
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_rose_grid import extract_ole_streams, parse_workbook

with open('Rose-Lega-2025-2026.xls', 'rb') as f:
    streams = extract_ole_streams(f.read())
    wb_data = streams.get('Workbook')
    df = parse_workbook(wb_data)

teams = []
# Each team takes 4 columns: [Role, Name, Price, Team/Notes]
num_teams = df.shape[1] // 4
print(f"Total Teams in File: {num_teams}")

team_data = {}

for t_idx in range(num_teams):
    base_col = t_idx * 4
    team_name = df.iloc[0, base_col + 1]
    team_budget_rem = df.iloc[0, base_col + 2] # Or remaining budget
    
    players = []
    total_spent = 0
    role_counts = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    role_spent = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    
    for r in range(1, 26):
        role = df.iloc[r, base_col]
        name = df.iloc[r, base_col + 1]
        price = df.iloc[r, base_col + 2]
        real_team = df.iloc[r, base_col + 3]
        
        try:
            p_val = float(price)
        except:
            p_val = 0.0
            
        players.append({
            'role': role,
            'name': name,
            'price': p_val,
            'team': real_team
        })
        total_spent += p_val
        if role in role_counts:
            role_counts[role] += 1
            role_spent[role] += p_val
            
    team_data[team_name] = {
        'budget_cell': team_budget_rem,
        'total_spent': total_spent,
        'total_budget_implied': total_spent + (float(team_budget_rem) if pd.notnull(team_budget_rem) else 0),
        'role_counts': role_counts,
        'role_spent': role_spent,
        'players': players
    }

print("\n================== DETTAGLIO SQUADRE LEGA 2025/2026 ==================")
for tname, d in team_data.items():
    print(f"\n--- SQUADRA: {tname} ---")
    print(f"Crediti Spesi Totali: {d['total_spent']} CR | Valore in cella header: {d['budget_cell']} CR | Totale Calcolato: {d['total_budget_implied']} CR")
    print(f"Spesa per Ruolo:")
    print(f"  🧤 P (Portieri, {d['role_counts']['P']} slot): {d['role_spent']['P']} CR ({d['role_spent']['P']/d['total_spent']*100:.1f}%)")
    print(f"  🛡️ D (Difensori, {d['role_counts']['D']} slot): {d['role_spent']['D']} CR ({d['role_spent']['D']/d['total_spent']*100:.1f}%)")
    print(f"  🪄 C (Centrocampisti, {d['role_counts']['C']} slot): {d['role_spent']['C']} CR ({d['role_spent']['C']/d['total_spent']*100:.1f}%)")
    print(f"  ⚡ A (Attaccanti, {d['role_counts']['A']} slot): {d['role_spent']['A']} CR ({d['role_spent']['A']/d['total_spent']*100:.1f}%)")
    print(f"Top Acquisti:")
    top_p = sorted(d['players'], key=lambda x: x['price'], reverse=True)[:5]
    for tp in top_p:
        print(f"   [{tp['role']}] {tp['name']} ({tp['team']}): {tp['price']} CR")

# Let's save a structured JSON for future analysis
with open('data/processed/league_rosters_2025_26.json', 'w', encoding='utf-8') as f:
    json.dump(team_data, f, indent=2, ensure_ascii=False)

print("\n-> Saved structured league rosters to 'data/processed/league_rosters_2025_26.json'")
