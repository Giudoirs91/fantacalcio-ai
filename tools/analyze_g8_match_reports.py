import os
import sys
import glob
import json
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.parse_and_sync_match_reports import parse_pdf_match_report

def main():
    pdf_files = sorted(glob.glob(os.path.join(ROOT_DIR, "data", "raw", "match report 26-27", "8_*.pdf")))
    print(f"Trovati {len(pdf_files)} match reports per la Giornata 8:\n")
    
    all_scorers = []
    all_assists = []
    all_gks = []
    
    for f in pdf_files:
        m, players, teams, rankings = parse_pdf_match_report(f)
        print(f"=== {m['match_title']} (Moduli: {', '.join(m.get('moduli', []))}) ===")
        
        scorers = [p for p in players if p.get('goals', 0) > 0]
        assisters = [p for p in players if p.get('assists', 0) > 0]
        gks = [p for p in players if p.get('role_gk')]
        
        for p in scorers:
            print(f"  ⚽ GOL: [{p['team']}] {p['player_name']} ({p['goals']} gol, {p['shots_on_target']}/{p['total_shots']} tiri)")
            all_scorers.append((m['match_title'], p['team'], p['player_name'], p['goals']))
            
        for p in assisters:
            print(f"  🎯 ASSIST: [{p['team']}] {p['player_name']} ({p['assists']} assist, {p['key_passes']} key passes)")
            all_assists.append((m['match_title'], p['team'], p['player_name'], p['assists']))
            
        # Check cards
        yellows = [p for p in players if p.get('yellow_cards', 0) > 0]
        reds = [p for p in players if p.get('red_cards', 0) > 0 or p.get('double_yellows', 0) > 0]
        if yellows:
            print(f"  🟨 Ammoniti: {', '.join([f'{p[\"player_name\"]} ({p[\"team\"]})' for p in yellows])}")
        if reds:
            print(f"  🟥 Espulsi: {', '.join([f'{p[\"player_name\"]} ({p[\"team\"]})' for p in reds])}")

        for g in gks:
            cs = "SI (Clean Sheet!)" if g['clean_sheet'] else "NO"
            print(f"  🧤 PORTIERE: [{g['team']}] {g['player_name']} (GS: {g['goals_conceded']}, Parate: {g['saves']}, CleanSheet: {cs})")
            all_gks.append((m['match_title'], g['team'], g['player_name'], g['goals_conceded'], g['saves'], g['clean_sheet']))
            
        # Top physical performers
        sorted_km = sorted(players, key=lambda x: x.get('km_distance', 0.0), reverse=True)[:2]
        sorted_sp = sorted(players, key=lambda x: x.get('sprint_speed_max', 0.0), reverse=True)[:2]
        km_str = ", ".join([f"{p['player_name']} ({p['km_distance']} km)" for p in sorted_km if p.get('km_distance', 0) > 0])
        sp_str = ", ".join([f"{p['player_name']} ({p['sprint_speed_max']} km/h)" for p in sorted_sp if p.get('sprint_speed_max', 0) > 0])
        if km_str:
            print(f"  🏃 Top Chilometri: {km_str}")
        if sp_str:
            print(f"  ⚡ Top Sprint: {sp_str}")
            
        print()

if __name__ == '__main__':
    main()
