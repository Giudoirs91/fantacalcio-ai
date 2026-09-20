import os, glob, re, json
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTI_DIR = os.path.join(ROOT_DIR, "data", "raw", "voti 26-27")
MATCHES_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_matches_g1_g2.json")
PLAYERS_MASTER = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
TOP_FLOP_JSON = os.path.join(ROOT_DIR, "data", "processed", "top_flop_rounds.json")

# 1. Carica match calendar
matches_info = []
if os.path.exists(MATCHES_JSON):
    with open(MATCHES_JSON, 'r', encoding='utf-8') as f:
        matches_info = json.load(f)

team_matches = {}
for m in matches_info:
    g = m.get('giornata')
    h = m.get('home_team', '').upper().strip()
    a = m.get('away_team', '').upper().strip()
    title = m.get('match_title', '').strip()
    sh = m.get('score_home')
    sa = m.get('score_away')
    if g and h and a:
        team_matches[(g, h)] = {
            'opponent': a,
            'is_home': True,
            'score_str': title,
            'team_score': sh,
            'opp_score': sa
        }
        team_matches[(g, a)] = {
            'opponent': h,
            'is_home': False,
            'score_str': title,
            'team_score': sa,
            'opp_score': sh
        }

print(f"Loaded {len(team_matches)} team-match slots.")
