import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import json
import time
import urllib.request
import pandas as pd

from src.player_matcher import clean_text, resolve_player
from src.stats_processor import load_quotazioni, safe_float, safe_int

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES_CONFIG = {
    'Serie A': {'league_id': 55, 'season_id': '27044'},
    'Premier League': {'league_id': 47, 'season_id': '27110'},
    'Ligue 1': {'league_id': 53, 'season_id': '27212'},
    'La Liga': {'league_id': 87, 'season_id': '27233'},
    'Bundesliga': {'league_id': 54, 'season_id': '26891'},
    'Eredivisie': {'league_id': 57, 'season_id': '27131'},
    'Liga Portugal': {'league_id': 61, 'season_id': '27181'},
    'Championship': {'league_id': 48, 'season_id': '27195'},
    'Belgian Pro League': {'league_id': 40, 'season_id': '27152'},
    'Brasileirao': {'league_id': 268, 'season_id': '25077'},
    'Super Lig': {'league_id': 52, 'season_id': '28966'}
}

# 12 Metriche essenziali da estrarre
CORE_STATS = [
    'expected_goals', 'expected_goals_per_90', 'expected_assists_per_90',
    'expected_goalsontarget', 'rating', 'mins_played', 'goals', 'goal_assist',
    'total_scoring_att', 'total_tackle', 'interception', '_goals_prevented'
]

def fetch_league_stats(league_name, league_id, season_id):
    print(f"\n--- [Scraping] {league_name} 2025/2026 (League: {league_id}, Season: {season_id}) ---")
    base_url = f"https://www.fotmob.com/it/leagues/{league_id}/stats/season/{season_id}/players/"
    
    # 1. Fetch initial expected_goals to get statsList
    init_url = base_url + "expected_goals"
    req = urllib.request.Request(init_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
    
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not m:
        print(f"Error: no data found for {league_name}")
        return {}

    data = json.loads(m.group(1))['props']['pageProps']['data']
    stats_list = data.get('statsList', [])
    available_stat_names = {s['name'] for s in stats_list}

    league_players = {}

    for s_name in CORE_STATS:
        if s_name not in available_stat_names:
            continue
        stat_url = base_url + s_name
        try:
            req_s = urllib.request.Request(stat_url, headers=HEADERS)
            with urllib.request.urlopen(req_s, timeout=15) as resp_s:
                html_s = resp_s.read().decode('utf-8')
            m_s = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_s)
            if m_s:
                page_data = json.loads(m_s.group(1))['props']['pageProps']['data']
                rows = page_data.get('statsData', [])
                for r in rows:
                    pid = r['id']
                    pname = r['name']
                    team = r.get('teamName', r.get('teamId', ''))
                    pos = r.get('position', '')
                    stat_val = r.get('statValue')
                    if isinstance(stat_val, dict):
                        stat_val = stat_val.get('value')
                    subval = r.get('substatValue')
                    if isinstance(subval, dict):
                        subval = subval.get('value')
                    
                    if pid not in league_players:
                        league_players[pid] = {
                            'id': pid,
                            'name': pname,
                            'team': team,
                            'position': pos,
                            'league': league_name,
                            'matches': subval
                        }
                    league_players[pid][s_name] = stat_val
            time.sleep(0.15)
        except Exception as e:
            print(f"  Warning su {s_name} in {league_name}: {e}")

    print(f"-> {league_name}: Estratti {len(league_players)} calciatori con statistiche 2025/2026.")
    return league_players

def build_unified_preview():
    # Carica alias
    alias_path = "config/player_aliases.json"
    aliases = {}
    if os.path.exists(alias_path):
        with open(alias_path, 'r', encoding='utf-8') as f:
            aliases = json.load(f)

    # 1. Scarica e indicizza tutte le leghe 2025/2026
    all_leagues_players = {}
    for lname, lcfg in LEAGUES_CONFIG.items():
        try:
            l_data = fetch_league_stats(lname, lcfg['league_id'], lcfg['season_id'])
            for pid, pinfo in l_data.items():
                c_name = clean_text(pinfo['name'])
                all_leagues_players[c_name] = pinfo
        except Exception as e:
            print(f"Error fetching {lname}: {e}")

    # 2. Carica Listone 518 calciatori
    df_quot = load_quotazioni()
    print(f"\n=======================================================")
    print(f"MATCHING SUI 518 CALCIATORI DEL LISTONE SERIE A 2026/27")
    print(f"=======================================================")

    unified_records = []
    matched_count = 0
    league_breakdown = {}

    for _, q in df_quot.iterrows():
        pid = int(q['Id'])
        raw_name = str(q['Nome']).strip()
        clean_pname = clean_text(raw_name)
        role = str(q['R']).strip().upper()
        mantra_role = str(q['RM']).strip()
        team = str(q['Squadra']).strip()
        fvm = safe_float(q.get('FVM'), 1.0)

        # Applica alias se presente
        search_name = aliases.get(clean_pname, clean_pname)

        # Risolvi giocatore
        p_stat = resolve_player(search_name, team, all_leagues_players, role=role)

        has_data = False
        league_2526 = "Nessuna / Nuovo 26-27"
        rating_2526 = None
        mins_2526 = None
        goals_2526 = 0
        assists_2526 = 0
        xg_2526 = None
        xg90_2526 = None
        xgot_2526 = None
        xa90_2526 = None
        tkl_int90_2526 = None
        shots90_2526 = None
        goals_prevented_2526 = None

        if p_stat:
            has_data = True
            matched_count += 1
            league_2526 = p_stat.get('league', 'Serie A')
            league_breakdown[league_2526] = league_breakdown.get(league_2526, 0) + 1

            mins_2526 = safe_int(p_stat.get('mins_played'), 0)
            r_val = safe_float(p_stat.get('rating'))
            rating_2526 = round(r_val, 2) if r_val > 0 else None

            goals_2526 = safe_int(p_stat.get('goals'), 0)
            assists_2526 = safe_int(p_stat.get('goal_assist'), 0)

            xg_v = safe_float(p_stat.get('expected_goals'))
            xg_2526 = round(xg_v, 2) if xg_v is not None else 0.0

            xg90_v = safe_float(p_stat.get('expected_goals_per_90'))
            xg90_2526 = round(xg90_v, 2) if xg90_v is not None else 0.0

            xgot_v = safe_float(p_stat.get('expected_goalsontarget'))
            xgot_2526 = round(xgot_v, 2) if xgot_v is not None else 0.0

            xa90_v = safe_float(p_stat.get('expected_assists_per_90'))
            xa90_2526 = round(xa90_v, 2) if xa90_v is not None else 0.0

            shots_v = safe_float(p_stat.get('total_scoring_att'))
            shots90_2526 = round(shots_v, 2) if shots_v is not None else 0.0

            tkl_v = safe_float(p_stat.get('total_tackle'), 0.0)
            int_v = safe_float(p_stat.get('interception'), 0.0)
            tkl_int90_2526 = round(tkl_v + int_v, 2)

            if role == 'P':
                gp_v = safe_float(p_stat.get('_goals_prevented'))
                goals_prevented_2526 = round(gp_v, 2) if gp_v is not None else 0.0

        record = {
            'id': pid,
            'name': raw_name,
            'team_2627': team,
            'role': role,
            'mantra': mantra_role,
            'fvm': fvm,
            'has_data_2526': has_data,
            'league_2526': league_2526,
            'rating_2526': rating_2526,
            'mins_2526': mins_2526,
            'goals_2526': goals_2526,
            'assists_2526': assists_2526,
            'xg_2526': xg_2526,
            'xg90_2526': xg90_2526,
            'xgot_2526': xgot_2526,
            'xa90_2526': xa90_2526,
            'shots90_2526': shots90_2526,
            'tkl_int90_2526': tkl_int90_2526,
            'goals_prevented_2526': goals_prevented_2526
        }
        unified_records.append(record)

    df_out = pd.DataFrame(unified_records)
    
    # Salva il file preview CSV e JSON per il controllo dell'utente
    os.makedirs("data/raw", exist_ok=True)
    csv_preview = "data/raw/preview_all_518_players_stats_2025_26.csv"
    json_preview = "data/raw/preview_all_518_players_stats_2025_26.json"

    df_out.to_csv(csv_preview, index=False, encoding='utf-8')
    with open(json_preview, 'w', encoding='utf-8') as f:
        json.dump(unified_records, f, ensure_ascii=False, indent=2)

    print(f"\nFILE DI PREVIEW GENERATO CON SUCCESSO!")
    print(f"-> Totale Calciatori Listone: {len(df_out)}")
    print(f"-> Calciatori con Dati 2025/2026 Trovati: {matched_count} / {len(df_out)} ({round(matched_count/len(df_out)*100, 1)}%)")
    print(f"-> Ripartizione per Lega 2025/2026:")
    for leg, cnt in league_breakdown.items():
        print(f"     • {leg}: {cnt} calciatori")
    print(f"-> File CSV Anteprima: {csv_preview}")
    print(f"=======================================================")

    return df_out

if __name__ == "__main__":
    build_unified_preview()
