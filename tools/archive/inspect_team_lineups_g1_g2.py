import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import pandas as pd
from collections import defaultdict

df_reports = pd.read_csv("data/raw/match_reports_players_g1_g2.csv")
with open("data/raw/match_reports_matches_g1_g2.json", "r", encoding="utf-8") as f:
    matches = json.load(f)

# Inspect modulo and lineups per team
teams = sorted(df_reports['team'].unique())
print(f"Squadre trovate: {len(teams)}")

team_match_data = defaultdict(list)

for m in matches:
    h = m['home_team']
    a = m['away_team']
    team_match_data[h].append({
        'giornata': m['giornata'],
        'opp': a,
        'is_home': True,
        'score': f"{m['score_home']}-{m['score_away']}",
        'moduli': m.get('moduli', [])
    })
    team_match_data[a].append({
        'giornata': m['giornata'],
        'opp': h,
        'is_home': False,
        'score': f"{m['score_away']}-{m['score_home']}",
        'moduli': m.get('moduli', [])
    })

print("\n--- RIEPILOGO SQUADRE G1 + G2 ---")
for t in teams:
    sub_df = df_reports[df_reports['team'] == t]
    starters = sub_df[sub_df['is_starter'] == True].groupby('player_name')['minutes'].agg(['count', 'sum']).reset_index()
    starters.columns = ['player_name', 'starts', 'total_mins']
    starters = starters.sort_values(by=['starts', 'total_mins'], ascending=False)
    
    m_info = team_match_data[t]
    print(f"\n[{t}] (Partite giocate: {len(m_info)})")
    for mi in m_info:
        print(f"  G{mi['giornata']} vs {mi['opp']} ({mi['score']}) - Moduli: {mi['moduli']}")
    print(f"  Titolari fissi (2/2 partite): {', '.join(starters[starters['starts'] == 2]['player_name'].tolist())}")
    print(f"  Titolari a rotazione (1/2 partite): {', '.join(starters[starters['starts'] == 1]['player_name'].tolist())}")
