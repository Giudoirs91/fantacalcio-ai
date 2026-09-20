import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
import re
import json
import pandas as pd
from src.player_matcher import clean_text, resolve_player
from src.stats_processor import load_quotazioni

df_quot = load_quotazioni()
df_reports = pd.read_csv("data/raw/match_reports_players_g1_g2.csv")

print(f"Listone: {len(df_quot)} calciatori.")
print(f"Match reports raw rows: {len(df_reports)} righe.")

# Aggregate stats by player in reports
player_agg = {}

for _, row in df_reports.iterrows():
    pname = str(row['player_name']).strip()
    team = str(row['team']).strip()
    is_gk = bool(row['role_gk'])
    clean = clean_text(pname)
    key = (clean, team.lower())
    
    if key not in player_agg:
        player_agg[key] = {
            'name_report': pname,
            'team': team,
            'is_gk': is_gk,
            'matches': 0,
            'starts': 0,
            'minutes': 0,
            'goals': 0,
            'assists': 0,
            'shots': 0,
            'shots_on_target': 0,
            'key_passes': 0,
            'recoveries': 0,
            'fouls_drawn': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'goals_conceded': 0,
            'saves': 0,
            'clean_sheets': 0
        }
        
    rec = player_agg[key]
    rec['matches'] += 1
    if row['is_starter']:
        rec['starts'] += 1
    rec['minutes'] += int(row['minutes'])
    rec['yellow_cards'] += int(row['yellow_cards'])
    rec['red_cards'] += int(row['red_cards']) + int(row['double_yellows'])
    
    if is_gk:
        rec['goals_conceded'] += int(row['goals_conceded'])
        rec['saves'] += int(row['saves'])
        rec['clean_sheets'] += int(row['clean_sheet'])
    else:
        rec['goals'] += int(row['goals'])
        rec['assists'] += int(row['assists'])
        rec['shots'] += int(row['total_shots'])
        rec['shots_on_target'] += int(row['shots_on_target'])
        rec['key_passes'] += int(row['key_passes'])
        rec['recoveries'] += int(row['ball_recoveries'])
        rec['fouls_drawn'] += int(row['fouls_drawn'])

print(f"Giocatori unici aggregati da G1+G2: {len(player_agg)}")

# Match with Quotazioni Listone
matched = 0
for _, q in df_quot.iterrows():
    pname = clean_text(str(q['Nome']))
    team = str(q['Squadra']).lower()
    
    # Try exact match or resolve_player
    found = None
    for (r_name, r_team), r_data in player_agg.items():
        if (pname in r_name or r_name in pname) and (team in r_team or r_team in team):
            found = r_data
            break
            
    if found:
        matched += 1

print(f"Matchati con successo con il Listone 2026/27: {matched}/{len(df_quot)}")
