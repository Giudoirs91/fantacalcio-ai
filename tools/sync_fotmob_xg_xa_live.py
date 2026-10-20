"""
tools/sync_fotmob_xg_xa_live.py
Aggiorna fotmob_seriea_2026_27_stats.json con i valori live ufficiali di xG + xA /90 da FotMob.
"""

import os
import sys
import json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\f1b14959-bc4e-4d22-af91-5ec94b749f95\.system_generated\steps\687\content.md"
JSON_PATH = os.path.join(ROOT_DIR, "data", "raw", "fotmob_seriea_2026_27_stats.json")
CSV_PATH = os.path.join(ROOT_DIR, "data", "raw", "fotmob_seriea_2026_27_stats.csv")

def sync():
    if not os.path.exists(HTML_PATH):
        print(f"File {HTML_PATH} non trovato.")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    idx = text.find('__NEXT_DATA__')
    if idx == -1:
        print("NEXT_DATA non trovato.")
        return
    s_start = text.find('>', idx) + 1
    s_end = text.find('</script>', s_start)
    data = json.loads(text[s_start:s_end])
    stats_data = data['props']['pageProps']['data']['statsData']

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        fm_db = json.load(f)

    updated_count = 0
    for item in stats_data:
        pid = str(item['id'])
        val = float(item['statValue']['value'])
        rank = int(item['rank'])

        if pid in fm_db:
            if 'stats' not in fm_db[pid]:
                fm_db[pid]['stats'] = {}
            if 'ranks' not in fm_db[pid]:
                fm_db[pid]['ranks'] = {}
            fm_db[pid]['stats']['xg_xa90_2627'] = val
            fm_db[pid]['ranks']['xg_xa90_rank'] = rank
            updated_count += 1

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(fm_db, f, indent=2, ensure_ascii=False)

    # Esporta anche in CSV
    rows = []
    for pid, pdata in fm_db.items():
        r = {
            'id': pdata.get('id', pid),
            'name': pdata.get('name', ''),
            'team_name': pdata.get('team_name', ''),
            'minutes_played': pdata.get('minutes_played', 0),
            'matches_played': pdata.get('matches_played', 0)
        }
        for sk, sv in pdata.get('stats', {}).items():
            r[sk] = sv
        for rk, rv in pdata.get('ranks', {}).items():
            r[rk] = rv
        rows.append(r)

    df = pd.DataFrame(rows)
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')

    print(f"✓ FotMob 2026/27 aggiornato con successo: {updated_count} calciatori sincronizzati con xG+xA/90!")
    print(f"  File salvati: {JSON_PATH} e {CSV_PATH}")

if __name__ == '__main__':
    sync()
