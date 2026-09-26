import os
import re
import json
import pandas as pd
from .player_matcher import clean_text, resolve_player

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_and_aggregate_match_reports():
    reports_csv = os.path.join(ROOT_DIR, "data", "raw", "match_reports_players_g1_g2.csv")
    if not os.path.exists(reports_csv):
        alt_path = "data/raw/match_reports_players_g1_g2.csv"
        if os.path.exists(alt_path):
            reports_csv = alt_path
        else:
            print(f"[MatchReportsProcessor] File {reports_csv} non trovato.")
            return {}
        
    df = pd.read_csv(reports_csv)
    
    player_agg = {}
    
    for _, row in df.iterrows():
        pname = str(row['player_name']).strip()
        team = str(row['team']).strip()
        is_gk = str(row.get('role_gk', '')).strip().lower() in ('true', '1', 'yes', '1.0')
        clean = clean_text(pname)
        key = f"{clean}_{team.lower()}"
        
        if key not in player_agg:
            player_agg[key] = {
                'name': pname,
                'team': team,
                'is_gk': is_gk,
                'presenze_2627': 0,
                'titolarita_count_2627': 0,
                'minuti_2627': 0,
                'gol_2627': 0,
                'assist_2627': 0,
                'tiri_2627': 0,
                'tiri_porta_2627': 0,
                'legni_2627': 0,
                'key_passes_2627': 0,
                'occasioni_create_2627': 0,
                'recuperi_2627': 0,
                'falli_subiti_2627': 0,
                'passaggi_riusciti_2627': 0,
                'passaggi_avanti_2627': 0,
                'ammonizioni_2627': 0,
                'espulsioni_2627': 0,
                'gol_subiti_2627': 0,
                'parate_2627': 0,
                'clean_sheets_2627': 0,
                'giornate_giocate': [],
                'history_by_round': {}
            }
            
        rec = player_agg[key]
        rec['presenze_2627'] += 1
        g_num = int(row.get('giornata', 1))
        rec['giornate_giocate'].append(g_num)
        
        is_starter = bool(row.get('is_starter', False))
        if is_starter:
            rec['titolarita_count_2627'] += 1
            
        rec['minuti_2627'] += int(row.get('minutes', 0))
        rec['history_by_round'][g_num] = {
            'is_starter': is_starter,
            'minutes': int(row.get('minutes', 0)),
            'is_gk': is_gk
        }
        rec['ammonizioni_2627'] += int(row.get('yellow_cards', 0))
        rec['espulsioni_2627'] += int(row.get('red_cards', 0)) + int(row.get('double_yellows', 0))
        
        if is_gk:
            rec['gol_subiti_2627'] += int(row.get('goals_conceded', 0))
            rec['parate_2627'] += int(row.get('saves', 0))
            rec['clean_sheets_2627'] += int(row.get('clean_sheet', 0))
        else:
            rec['gol_2627'] += int(row.get('goals', 0))
            rec['assist_2627'] += int(row.get('assists', 0))
            rec['tiri_2627'] += int(row.get('total_shots', 0))
            rec['tiri_porta_2627'] += int(row.get('shots_on_target', 0))
            rec['legni_2627'] += int(row.get('woodworks', 0))
            rec['key_passes_2627'] += int(row.get('key_passes', 0))
            rec['occasioni_create_2627'] += int(row.get('chances_created', 0))
            rec['recuperi_2627'] += int(row.get('ball_recoveries', 0))
            rec['falli_subiti_2627'] += int(row.get('fouls_drawn', 0))
            rec['passaggi_riusciti_2627'] += int(row.get('passes_completed', 0))
            rec['passaggi_avanti_2627'] += int(row.get('forward_passes', 0))
            
    print(f"[MatchReportsProcessor] Aggregati dati 2026/27 (Match Reports Ufficiali) per {len(player_agg)} calciatori.")
    return player_agg
