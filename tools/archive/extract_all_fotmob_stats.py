import os
import re
import json
import time
import urllib.request
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_page_data(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not m:
        raise ValueError(f"No __NEXT_DATA__ found in {url}")
    return json.loads(m.group(1))['props']['pageProps']['data']

def extract_all():
    base_url = "https://www.fotmob.com/it/leagues/55/stats/season/27044/players/"
    initial_stat = "expected_goals"
    
    print(f"Fetching initial page: {base_url + initial_stat} ...")
    init_data = fetch_page_data(base_url + initial_stat)
    
    stats_list = init_data.get('statsList', [])
    print(f"-> Trovate {len(stats_list)} categorie statistiche disponibili su FotMob Serie A 2025/26!\n")

    players_dict = {} # pid -> { 'name': ..., 'team': ..., 'position': ..., 'stats': {} }

    for idx, stat_meta in enumerate(stats_list, 1):
        stat_name = stat_meta['name']
        stat_title = stat_meta.get('title', stat_name)
        category = stat_meta.get('category', 'Other')
        
        stat_url = f"{base_url}{stat_name}"
        print(f"[{idx}/{len(stats_list)}] Scraping: {category} -> {stat_title} ({stat_name})...")
        
        try:
            if idx == 1:
                page_data = init_data
            else:
                page_data = fetch_page_data(stat_url)
                time.sleep(0.3) # rispetto rate limit

            rows = page_data.get('statsData', [])
            for r in rows:
                pid = r['id']
                pname = r['name']
                team = r.get('teamName', r.get('teamId', ''))
                pos = r.get('position', '')
                stat_val = r.get('statValue')
                substat_val = r.get('substatValue') # spesso partite giocate o minuti
                
                if pid not in players_dict:
                    players_dict[pid] = {
                        'id': pid,
                        'name': pname,
                        'team': team,
                        'position': pos,
                        'matches_played': substat_val
                    }
                else:
                    if not players_dict[pid]['team'] and team:
                        players_dict[pid]['team'] = team
                    if not players_dict[pid]['position'] and pos:
                        players_dict[pid]['position'] = pos
                
                # Salvataggio valore statistico
                players_dict[pid][stat_name] = stat_val

        except Exception as e:
            print(f"  [!] Errore su {stat_name}: {e}")

    # Creazione DataFrame
    df = pd.DataFrame(list(players_dict.values()))
    
    # Riordina colonne principali
    cols_order = ['id', 'name', 'team', 'position', 'matches_played']
    other_cols = [c for c in df.columns if c not in cols_order]
    df = df[cols_order + other_cols]

    os.makedirs("data/raw", exist_ok=True)
    csv_out = "data/raw/fotmob_seriea_2025_26_stats.csv"
    json_out = "data/raw/fotmob_seriea_2025_26_stats.json"

    df.to_csv(csv_out, index=False, encoding='utf-8')
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(list(players_dict.values()), f, ensure_ascii=False, indent=2)

    print(f"\n=======================================================")
    print(f"ESTRAZIONE COMPLETATA CON SUCCESSO!")
    print(f"-> Totale Calciatori estratti: {len(df)}")
    print(f"-> Totale Metriche avanzate: {len(df.columns) - 5}")
    print(f"-> File CSV salvato: {csv_out}")
    print(f"-> File JSON salvato: {json_out}")
    print(f"=======================================================")

    return df

if __name__ == "__main__":
    extract_all()
