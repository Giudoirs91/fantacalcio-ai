import sys
import os
import urllib.request
import gzip
import json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.player_matcher import clean_text, resolve_player

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUE_SEASONS = {
    'Premier League': {'league_id': 47, 'season_id': '36781'},
    'La Liga': {'league_id': 87, 'season_id': '38843'},
    'Ligue 1': {'league_id': 53, 'season_id': '37298'},
    'Bundesliga': {'league_id': 54, 'season_id': '40040'}
}

STATS_TO_FETCH = [
    'expected_goals', 'expected_goals_per_90', 'expected_assists_per_90',
    'expected_goalsontarget', 'rating', 'mins_played', 'total_tackle', 'interception'
]

def fetch_stat_json(league_id, season_id, stat_name):
    url = f"https://data.fotmob.com/stats/{league_id}/season/{season_id}/{stat_name}.json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            try:
                raw = gzip.decompress(raw)
            except Exception:
                pass
            return json.loads(raw.decode('utf-8'))
    except Exception as e:
        print(f"Error {url}: {e}")
        return None

# Test con Premier League
print("Fetching stats from Premier League 2025/2026...")
pl_players = {}
for s in STATS_TO_FETCH:
    data = fetch_stat_json(47, '36781', s)
    if data and data.get('TopLists'):
        stat_list = data['TopLists'][0].get('StatList', [])
        for p in stat_list:
            pname = p.get('ParticipantName')
            pid = p.get('ParticipantId')
            val = p.get('StatValue')
            subval = p.get('SubstatValue')
            if pid not in pl_players:
                pl_players[pid] = {'id': pid, 'name': pname, 'team': p.get('TeamName', ''), 'league': 'Premier League', 'matches': subval}
            pl_players[pid][s] = val

print(f"Total PL players extracted: {len(pl_players)}")
df_pl = pd.DataFrame(list(pl_players.values()))
print("\nSample PL players:")
print(df_pl.head(5)[['name', 'team', 'expected_goals', 'expected_goals_per_90', 'mins_played']])
