import pandas as pd
import json

df = pd.read_excel('Quotazioni_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1)
df = df.dropna(subset=['Id', 'Nome', 'Squadra'])

teams = sorted(df['Squadra'].unique())

team_players_summary = {}

for t in teams:
    t_df = df[df['Squadra'] == t].sort_values(by='FVM', ascending=False)
    team_players_summary[t] = []
    for _, r in t_df.iterrows():
        team_players_summary[t].append({
            'name': str(r['Nome']).strip(),
            'role': str(r['R']).strip(),
            'mantra': str(r['RM']).strip(),
            'fvm': float(r['FVM']) if pd.notnull(r['FVM']) else 1.0,
            'qta': float(r['Qt.A']) if pd.notnull(r['Qt.A']) else 1.0
        })

with open('all_20_teams_roster_2026_27.json', 'w', encoding='utf-8') as f:
    json.dump(team_players_summary, f, ensure_ascii=False, indent=2)

print("Roster completi delle 20 squadre estratti in all_20_teams_roster_2026_27.json")
