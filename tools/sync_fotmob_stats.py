"""
Script automatico ad alte prestazioni per sincronizzare le statistiche Serie A 2026/27 da FotMob.
Accetta opzionalmente come argomento il link della pagina FotMob di fine giornata:
    python tools/sync_fotmob_stats.py "https://www.fotmob.com/it/leagues/55/stats/serie/players"

Se nessun argomento viene passato, usa l'URL predefinito della Serie A 2026/27.
Esegue:
1. Scraping parallelo (thread pool) di tutte le 36 metriche ufficiali FotMob.
2. Salvataggio raw in data/raw/fotmob_seriea_2026_27_stats.json.
3. Matching intelligente e aggiornamento di data/processed/processed_players_master.json.
4. Ricompilazione immediata di Dashboard_Fanta_1000.html e sincronizzazione Android.
"""

import os
import sys
import re
import json
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from src.player_matcher import clean_text, match_player_name

OUT_DIR = os.path.join(ROOT_DIR, "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)

DEFAULT_URL = "https://www.fotmob.com/it/leagues/55/stats/serie/players"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
    'Accept': 'application/json, text/plain, */*'
}

# 36 metriche ufficiali censite
METRICS_MAP = {
    'goals': 'gol_fotmob_2627',
    'goal_assist': 'assist_fotmob_2627',
    '_goals_and_goal_assist': 'goals_and_assists_2627',
    'rating': 'rating_fotmob_2627',
    'mins_played': 'minuti_fotmob_2627',
    'goals_per_90': 'goals_per_90_2627',
    'expected_goals': 'xg_2627',
    'expected_goals_per_90': 'xg90_2627',
    'expected_goalsontarget': 'xgot_2627',
    'ontarget_scoring_att': 'ontarget_scoring_att_2627',
    'total_scoring_att': 'total_scoring_att_2627',
    'accurate_pass': 'accurate_pass_per_90_2627',
    'big_chance_created': 'big_chances_created_2627',
    'total_att_assist': 'chances_created_2627',
    'accurate_long_balls': 'accurate_long_balls_per_90_2627',
    'expected_assists': 'xa_2627',
    'expected_assists_per_90': 'xa90_2627',
    '_expected_goals_and_expected_assists_per_90': 'xg_xa90_2627',
    'won_contest': 'won_contest_2627',
    'big_chance_missed': 'big_chance_missed_2627',
    'defensive_contributions': 'defensive_contributions_2627',
    'total_tackle': 'total_tackle_2627',
    'interception': 'interception_2627',
    'effective_clearance': 'effective_clearance_2627',
    'outfielder_block': 'outfielder_block_2627',
    'ball_recovery': 'ball_recovery_fotmob_2627',
    'penalty_conceded': 'penalty_conceded_2627',
    'poss_won_att_3rd': 'poss_won_att_3rd_2627',
    'clean_sheet': 'clean_sheet_fotmob_2627',
    '_save_percentage': 'save_pct_2627',
    'saves': 'saves_per_90_2627',
    '_goals_prevented': 'goals_prevented_2627',
    'goals_conceded': 'goals_conceded_fotmob_2627',
    'fouls': 'fouls_2627',
    'yellow_card': 'yellow_cards_fotmob_2627',
    'red_card': 'red_cards_fotmob_2627'
}

def extract_endpoints_from_url(url):
    print(f"\n[FotMob Sync] Connessione a: {url}")
    html = ""
    try:
        cmd = ['curl.exe', '-s', '--compressed', url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15, encoding='utf-8', errors='ignore')
        if res.returncode == 0 and res.stdout.strip():
            html = res.stdout
    except Exception:
        pass

    if not html:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                html = r.text
        except Exception as e:
            print(f"[FotMob Sync] HTTP error su {url}: {e}")
            return None, {}
    
    try:
        idx = html.find('__NEXT_DATA__')
        if idx == -1:
            print("[FotMob Sync] Impossibile trovare __NEXT_DATA__ nella pagina.")
            return None, {}

        s = html[idx:]
        s_start = s.find('>') + 1
        s_end = s.find('</script>')
        data = json.loads(s[s_start:s_end])
        page_props = data.get('props', {}).get('pageProps', {})
        stats = page_props.get('stats', {})
        players_list = stats.get('players', [])
        
        endpoints = {}
        season_id = "36072" # default 2026/27
        for item in players_list:
            fetch_url = item.get('fetchAllUrl')
            if fetch_url:
                m = re.search(r'/season/(\d+)/([a-zA-Z0-9_\-]+)\.json', fetch_url)
                if m:
                    season_id = m.group(1)
                    stat_key = m.group(2)
                    endpoints[stat_key] = fetch_url
        
        return season_id, endpoints
    except Exception as e:
        print(f"[FotMob Sync] Errore estrazione endpoint: {e}")
        return None, {}

def download_single_stat(stat_name, fetch_url):
    # Try curl.exe first (rock solid on Windows)
    try:
        cmd = ['curl.exe', '-s', '--compressed', fetch_url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8, encoding='utf-8', errors='ignore')
        if res.returncode == 0 and res.stdout.strip():
            d = json.loads(res.stdout)
            top_lists = d.get('TopLists', [])
            if top_lists:
                return stat_name, top_lists[0].get('StatList', [])
    except Exception:
        pass

    # Fallback to requests
    try:
        r = requests.get(fetch_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            d = r.json()
            top_lists = d.get('TopLists', [])
            if top_lists:
                return stat_name, top_lists[0].get('StatList', [])
    except Exception as e:
        print(f"  [Errore download] {stat_name}: {e}")
    return stat_name, []

def fetch_all_fotmob_data(url=DEFAULT_URL):
    season_id, endpoints = extract_endpoints_from_url(url)
    if not season_id:
        season_id = "36072"
    
    # Se per qualche motivo endpoints non conteneva tutte le metriche, costruiamole
    for stat_key in METRICS_MAP.keys():
        if stat_key not in endpoints:
            endpoints[stat_key] = f"https://data.fotmob.com/stats/55/season/{season_id}/{stat_key}.json"

    print(f"[FotMob Sync] Stagione FotMob identificata: {season_id}")
    print(f"[FotMob Sync] Avvio scaricamento parallelo di {len(endpoints)} metriche...")

    t0 = time.time()
    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(download_single_stat, k, ep_url): k for k, ep_url in endpoints.items()}
        for future in as_completed(futures):
            stat_name, stat_list = future.result()
            results[stat_name] = stat_list

    elapsed = time.time() - t0
    print(f"[FotMob Sync] Scaricamento completato in {elapsed:.2f} secondi!")
    return results

def process_and_merge_stats(raw_results):
    # Raggruppa per participantId e participantName
    fotmob_players = {} # pid -> dict

    for stat_name, stat_list in raw_results.items():
        field_name = METRICS_MAP.get(stat_name, stat_name)
        for item in stat_list:
            pid = item.get('ParticiantId') or item.get('ParticipantId') or item.get('id')
            pname = item.get('ParticipantName') or item.get('name')
            team_name = item.get('TeamName') or item.get('teamName')
            stat_val = item.get('StatValue')
            sub_val = item.get('SubStatValue')
            mins = item.get('MinutesPlayed', 0)
            matches = item.get('MatchesPlayed', 0)
            rank = item.get('Rank')

            if not pid:
                continue

            if pid not in fotmob_players:
                fotmob_players[pid] = {
                    'id': pid,
                    'name': pname,
                    'team_name': team_name,
                    'minutes_played': mins,
                    'matches_played': matches,
                    'stats': {},
                    'ranks': {}
                }

            if mins and not fotmob_players[pid]['minutes_played']:
                fotmob_players[pid]['minutes_played'] = mins
            if matches and not fotmob_players[pid]['matches_played']:
                fotmob_players[pid]['matches_played'] = matches
            if team_name and not fotmob_players[pid]['team_name']:
                fotmob_players[pid]['team_name'] = team_name

            fotmob_players[pid]['stats'][field_name] = stat_val
            fotmob_players[pid]['stats'][f"{field_name}_sub"] = sub_val
            if rank:
                fotmob_players[pid]['ranks'][field_name] = rank

    # Salva JSON grezzo
    raw_json_path = os.path.join(OUT_DIR, "fotmob_seriea_2026_27_stats.json")
    with open(raw_json_path, 'w', encoding='utf-8') as f:
        json.dump(fotmob_players, f, indent=2, ensure_ascii=False)
    print(f"[FotMob Sync] Salvato archivio grezzo: {raw_json_path} ({len(fotmob_players)} calciatori censiti)")

    return fotmob_players

def update_processed_master(fotmob_players):
    master_path = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
    if not os.path.exists(master_path):
        master_path = os.path.join(ROOT_DIR, "processed_players_master.json")

    with open(master_path, 'r', encoding='utf-8') as f:
        master_players = json.load(f)

    # Carica alias noti
    alias_path = os.path.join(ROOT_DIR, "config", "player_aliases.json")
    aliases = {}
    if os.path.exists(alias_path):
        try:
            with open(alias_path, 'r', encoding='utf-8') as f:
                aliases = json.load(f)
        except Exception:
            pass

    # Crea indice di ricerca veloce per i giocatori FotMob
    fm_by_name = {}
    fm_by_clean = {}
    for pid, pdata in fotmob_players.items():
        name = pdata['name']
        fm_by_name[name.lower()] = pdata
        fm_by_clean[clean_text(name)] = pdata

    matched_count = 0
    updated_fields_count = 0

    for p in master_players:
        pname = p.get('name', '')
        pteam = p.get('team', '')
        clean_p = clean_text(pname)

        # 1. Check alias
        target_name = aliases.get(pname, pname)
        target_clean = clean_text(target_name)

        matched_fm = None
        if target_clean in fm_by_clean:
            matched_fm = fm_by_clean[target_clean]
        elif clean_p in fm_by_clean:
            matched_fm = fm_by_clean[clean_p]
        else:
            # Fuzzy / match_player_name
            for c_fm, fm_obj in fm_by_clean.items():
                if match_player_name(target_name, fm_obj['name']) or match_player_name(pname, fm_obj['name']):
                    matched_fm = fm_obj
                    break

        if matched_fm:
            matched_count += 1
            fm_stats = matched_fm.get('stats', {})

            # Mappa ciascun campo statistico
            for field, val in fm_stats.items():
                if val is not None and not field.endswith('_sub'):
                    # Preserva valori float/int
                    try:
                        fval = float(val) if '.' in str(val) else int(val)
                    except (ValueError, TypeError):
                        fval = val
                    p[field] = fval
                    updated_fields_count += 1

            # Mantieni compatibilità con le chiavi standard già usate nel fanta
            if 'xg_2627' in fm_stats and fm_stats['xg_2627'] is not None:
                p['xg_2627'] = float(fm_stats['xg_2627'])
            if 'xg90_2627' in fm_stats and fm_stats['xg90_2627'] is not None:
                p['xg90_2627'] = float(fm_stats['xg90_2627'])
            if 'xa_2627' in fm_stats and fm_stats['xa_2627'] is not None:
                p['xa_2627'] = float(fm_stats['xa_2627'])
            if 'xa90_2627' in fm_stats and fm_stats['xa90_2627'] is not None:
                p['xa90_2627'] = float(fm_stats['xa90_2627'])
            if 'rating_fotmob_2627' in fm_stats and fm_stats['rating_fotmob_2627'] is not None:
                p['rating_fotmob_2627'] = float(fm_stats['rating_fotmob_2627'])
            if 'goals_prevented_2627' in fm_stats and fm_stats['goals_prevented_2627'] is not None:
                p['goals_prevented_2627'] = float(fm_stats['goals_prevented_2627'])
            if 'saves_per_90_2627' in fm_stats and fm_stats['saves_per_90_2627'] is not None:
                p['saves_per_90_2627'] = float(fm_stats['saves_per_90_2627'])
            if 'clean_sheet_fotmob_2627' in fm_stats and fm_stats['clean_sheet_fotmob_2627'] is not None:
                p['clean_sheet_fotmob_2627'] = int(fm_stats['clean_sheet_fotmob_2627'])
            if 'save_pct_2627' in fm_stats and fm_stats['save_pct_2627'] is not None:
                p['save_pct_2627'] = float(fm_stats['save_pct_2627'])

            p['has_fotmob_stats'] = True

    # Salva il master aggiornato
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(master_players, f, indent=2, ensure_ascii=False)
    print(f"✓ Master aggiornato: {master_path}")
    print(f"  -> Calciatori master accoppiati con FotMob: {matched_count}/{len(master_players)}")

    root_master = os.path.join(ROOT_DIR, "processed_players_master.json")
    if os.path.exists(root_master) and root_master != master_path:
        with open(root_master, 'w', encoding='utf-8') as f:
            json.dump(master_players, f, indent=2, ensure_ascii=False)

def rebuild_dashboard():
    print("\n[FotMob Sync] Ricompilazione automatica Dashboard standalone...")
    from web.build_dashboard import build_standalone_dashboard
    build_standalone_dashboard()
    print("✓ Dashboard standalone e asset Android aggiornati con successo!")

def main():
    target_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print("==================================================================")
    print("      FANTAMASTER AI — SYNC RAPIDO STATISTICHE FOTMOB SERIE A     ")
    print("==================================================================")
    t_start = time.time()
    raw_results = fetch_all_fotmob_data(target_url)
    fotmob_players = process_and_merge_stats(raw_results)
    update_processed_master(fotmob_players)
    rebuild_dashboard()
    total_time = time.time() - t_start
    print("==================================================================")
    print(f"✓ AGGIORNAMENTO COMPLETATO IN {total_time:.1f} SECONDI!")
    print("==================================================================")

if __name__ == '__main__':
    main()
