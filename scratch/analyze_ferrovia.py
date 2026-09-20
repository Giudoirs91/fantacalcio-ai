import sys
import openpyxl
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

excel_path = 'data/raw/lega-ferrovia-rosters-1788691861822.xlsx'
df = pd.read_excel(excel_path, sheet_name='ROSE')

print("All columns:")
print(df.columns.tolist())

# Inspect the structure
# Typically 10 teams arranged side by side: (TeamName, Cost, [blank]) * 10
teams_data = {}

col_idx = 0
while col_idx < len(df.columns):
    team_col = df.columns[col_idx]
    if 'Unnamed' not in str(team_col) and str(team_col).strip():
        cost_col = df.columns[col_idx + 1] if col_idx + 1 < len(df.columns) else None
        team_name = str(team_col).strip()
        
        players = []
        for row_idx, row in df.iterrows():
            p_name = row.iloc[col_idx]
            p_cost = row.iloc[col_idx + 1] if cost_col else 0
            if pd.notna(p_name) and str(p_name).strip():
                players.append({
                    'index': row_idx + 1,
                    'name': str(p_name).strip(),
                    'cost': int(p_cost) if pd.notna(p_cost) and str(p_cost).isdigit() else float(p_cost) if pd.notna(p_cost) else 0
                })
        teams_data[team_name] = players
        col_idx += 2
    else:
        col_idx += 1

print(f"\nTrovate {len(teams_data)} squadre:")
for tname, p_list in teams_data.items():
    total_spent = sum(p['cost'] for p in p_list)
    print(f"• {tname}: {len(p_list)} giocatori, crediti spesi: {total_spent}")

# Inspect first team
t1 = list(teams_data.keys())[0]
print(f"\nDettaglio {t1}:")
for p in teams_data[t1]:
    print(f"  {p['index']}. {p['name']} -> {p['cost']} cr")
