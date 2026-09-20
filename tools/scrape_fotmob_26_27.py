import os
import re
import sys
import json
import time
import requests
import urllib.request
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT_DIR, "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

BASE_URL = "https://www.fotmob.com/it/leagues/55/stats/season/36072/players/"
API_BASE = "https://data.fotmob.com/stats/55/season/36072/"

# Comprehensive list: 13 user targets + complementary metrics
TARGET_STATS = [
    # 13 Richieste specifiche dell'utente:
    'expected_assists_per_90',
    'total_scoring_att',
    'ontarget_scoring_att',
    'expected_goalsontarget',
    'expected_goals_per_90',
    'big_chance_created',
    'won_contest',
    'big_chance_missed',
    'poss_won_att_3rd',
    'goals_conceded',
    '_save_percentage',
    'clean_sheet',
    'total_tackle',
    # Metriche complementari essenziali già censite:
    'total_att_assist',
    'expected_goals',
    'expected_assists',
    '_expected_goals_and_expected_assists_per_90',
    'rating',
    'mins_played',
    'defensive_contributions',
    'ball_recovery'
]

def fetch_metric_data(stat_name):
    """
    Tenta prima la chiamata diretta CDN JSON di FotMob (veloce e affidabile),
    con fallback sullo scraping HTML di __NEXT_DATA__.
    """
    json_url = f"{API_BASE}{stat_name}.json"
    try:
        r = requests.get(json_url, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            d = r.json()
            top_lists = d.get('TopLists', [])
            if top_lists and len(top_lists) > 0:
                stat_list = top_lists[0].get('StatList', [])
                if stat_list:
                    # Normalizza i campi per la struttura comune
                    norm_rows = []
                    for item in stat_list:
                        pid = item.get('ParticiantId') or item.get('ParticipantId') or item.get('id')
                        pname = item.get('ParticipantName') or item.get('name')
                        team_id = item.get('TeamId') or item.get('teamId')
                        team_name = item.get('TeamName') or item.get('teamName')
                        positions = item.get('Positions', [])
                        pos = positions[0] if positions else None
                        
                        stat_val = item.get('StatValue')
                        sub_val = item.get('SubStatValue')
                        mins = item.get('MinutesPlayed', 0)
                        matches = item.get('MatchesPlayed', 0)
                        rank = item.get('Rank')

                        norm_rows.append({
                            'id': pid,
                            'name': pname,
                            'teamId': team_id,
                            'teamName': team_name,
                            'position': pos,
                            'statValue': stat_val,
                            'substatValue': sub_val,
                            'minutesPlayed': mins,
                            'matchesPlayed': matches,
                            'rank': rank
                        })
                    return norm_rows
    except Exception as e:
        print(f"  [API Direct Warning] {stat_name}: {e}, provo fallback HTML...")

    # Fallback su pagina HTML Next.js
    url = f"{BASE_URL}{stat_name}/serie-players"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            data = json.loads(m.group(1))
            return data['props']['pageProps']['data'].get('statsData', [])
    except Exception as e:
        print(f"  [HTML Fallback Error] {stat_name}: {e}")

    return []

def run_scraper():
    print("=== AVVIO SCRAPING FOTMOB SERIE A 2026/2027 (SEASON 36072) ===")
    print(f"Totale metriche avanzate da acquisire: {len(TARGET_STATS)}")
    players_dict = {} # pid -> dict

    for idx, stat_name in enumerate(TARGET_STATS, 1):
        print(f"[{idx}/{len(TARGET_STATS)}] Scaricamento metrica: {stat_name} ...")
        rows = fetch_metric_data(stat_name)
        print(f"  -> Trovati {len(rows)} calciatori per {stat_name}.")

        for r in rows:
            pid = r.get('id')
            if not pid:
                continue
            pname = r.get('name')
            team_id = r.get('teamId')
            team_name = r.get('teamName')
            pos = r.get('position')
            mins = r.get('minutesPlayed')
            matches = r.get('matchesPlayed')

            stat_val_obj = r.get('statValue')
            stat_val = stat_val_obj.get('value') if isinstance(stat_val_obj, dict) else stat_val_obj

            sub_val_obj = r.get('substatValue')
            sub_val = sub_val_obj.get('value') if isinstance(sub_val_obj, dict) else sub_val_obj

            if pid not in players_dict:
                players_dict[pid] = {
                    'id': pid,
                    'name': pname,
                    'team_id': team_id,
                    'team_name': team_name,
                    'position': pos,
                    'minutes_played': mins,
                    'matches_played': matches,
                    'stats_2627': {}
                }

            if mins and not players_dict[pid].get('minutes_played'):
                players_dict[pid]['minutes_played'] = mins
            if matches and not players_dict[pid].get('matches_played'):
                players_dict[pid]['matches_played'] = matches
            if team_name and not players_dict[pid].get('team_name'):
                players_dict[pid]['team_name'] = team_name

            players_dict[pid]['stats_2627'][stat_name] = stat_val
            if sub_val is not None:
                players_dict[pid]['stats_2627'][f"{stat_name}_sub"] = sub_val
            if r.get('rank'):
                players_dict[pid]['stats_2627'][f"{stat_name}_rank"] = r.get('rank')

        time.sleep(0.15)

    print(f"\nScraping completato con successo! Totale calciatori censiti in FotMob 26/27: {len(players_dict)}")

    # Save JSON
    json_path = os.path.join(OUT_DIR, "fotmob_seriea_2026_27_stats.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(players_dict, f, indent=2, ensure_ascii=False)
    print(f"✓ Salvato JSON: {json_path}")

    # Save flat CSV
    flat_rows = []
    for pid, pdata in players_dict.items():
        row = {
            'id': pid,
            'name': pdata['name'],
            'team_id': pdata['team_id'],
            'team_name': pdata['team_name'],
            'position': pdata['position'],
            'minutes_played': pdata.get('minutes_played'),
            'matches_played': pdata.get('matches_played')
        }
        for s_name, s_val in pdata['stats_2627'].items():
            row[s_name] = s_val
        flat_rows.append(row)

    df = pd.DataFrame(flat_rows)
    csv_path = os.path.join(OUT_DIR, "fotmob_seriea_2026_27_stats.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✓ Salvato CSV: {csv_path} (colonne: {len(df.columns)}, righe: {len(df)})")

if __name__ == '__main__':
    run_scraper()
