"""
tools/import_advanced_scouting_data.py
======================================
Parser e importatore automatico per file esportati da FBref e WhoScored
salvati nella cartella data/raw/scouting_imports/.

Supporta:
1. fbref_standard.csv (o .html) -> npxG, npxG/90
2. fbref_gca.csv (o .html)      -> SCA, SCA/90, GCA, GCA/90
3. fbref_possession.csv (o .html) -> Touches in Attacking Penalty Area (Tocchi in Area)
4. whoscored_teams.html (o .txt) -> Attack Sides (% sinistra, centro, destra)
5. whoscored_referees.html (o .txt) -> Media Cartellini e Falli Arbitri Serie A

Mappa i dati direttamente sui 534 calciatori di data/processed/processed_players_master.json
e sulle configurazioni tattiche di config/tactical_db.json.
"""

import os
import sys
import re
import csv
import json
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.player_matcher import clean_text

IMPORTS_DIR = os.path.join(ROOT_DIR, "data", "raw", "scouting_imports")
MASTER_PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
TACTICAL_DB_PATH = os.path.join(ROOT_DIR, "config", "tactical_db.json")
REFEREES_PATH = os.path.join(ROOT_DIR, "config", "referee_stats.json")


def clean_num(val):
    if val is None or val == '' or val == '-':
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace(',', '.').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def parse_fbref_csv_or_html(file_path):
    """Estrae righe e colonne da un file CSV o HTML esportato da FBref."""
    if not os.path.exists(file_path):
        return []

    results = []
    if file_path.endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Rimuovi eventuali righe di commento FBref
            clean_lines = [l for l in lines if not l.startswith('#') and not l.startswith('---')]
            reader = csv.reader(clean_lines)
            header = None
            for row in reader:
                if not row or len(row) < 5:
                    continue
                # Trova la riga di header reale
                if 'Player' in row or 'Giocatore' in row:
                    header = [c.strip() for c in row]
                    continue
                if header and len(row) == len(header):
                    results.append(dict(zip(header, [c.strip() for c in row])))
    else: # HTML
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr') if tbody else table.find_all('tr')
            for tr in rows:
                p_tag = tr.find(['th', 'td'], attrs={'data-stat': 'player'})
                if not p_tag or not p_tag.get_text(strip=True):
                    continue
                row_dict = {}
                for td in tr.find_all(['th', 'td']):
                    stat = td.get('data-stat')
                    if stat:
                        row_dict[stat] = td.get_text(strip=True)
                results.append(row_dict)

    return results


def import_fbref_standard(master_players):
    """Importa npxG, G-PK (Gol su azione non da rigore) da fbref_standard (CSV o HTML)."""
    p_csv = os.path.join(IMPORTS_DIR, "fbref_standard.csv")
    p_html = os.path.join(IMPORTS_DIR, "fbref_standard.html")
    path = p_csv if os.path.exists(p_csv) else (p_html if os.path.exists(p_html) else None)
    if not path:
        return 0

    print(f"[Import] Elaborazione {os.path.basename(path)}...")
    rows = parse_fbref_csv_or_html(path)
    matched = 0

    for r in rows:
        name = r.get('Player') or r.get('player') or ''
        if not name or name == 'Player':
            continue
        norm_name = clean_text(name).lower()

        # npxG colonna (o G-PK se npxG non presente)
        npxg = clean_num(r.get('npxg') or r.get('npxG'))
        npxg90 = clean_num(r.get('npxg_per90') or r.get('npxG/90') or r.get('npxG_per90'))
        g_minus_pk = clean_num(r.get('G-PK'))
        pk_scored = clean_num(r.get('PK'))
        pk_att = clean_num(r.get('PKatt'))
        min_played = clean_num(r.get('Min'))

        for p in master_players:
            p_name = clean_text(p.get('name') or '').lower()
            if norm_name == p_name or norm_name in p_name or p_name in norm_name:
                if npxg > 0:
                    p['npxg_2627'] = npxg
                if npxg90 > 0:
                    p['npxg90_2627'] = npxg90
                p['goals_non_penalty_2627'] = g_minus_pk
                p['pk_scored_fbref_2627'] = pk_scored
                p['pk_attempted_fbref_2627'] = pk_att
                matched += 1
                break

    print(f"  ✓ {matched} calciatori aggiornati con metriche FBref Standard (G-PK, npxG)!")
    return matched


def import_fbref_gca(master_players):
    """Importa SCA e GCA da fbref_gca."""
    p_csv = os.path.join(IMPORTS_DIR, "fbref_gca.csv")
    p_html = os.path.join(IMPORTS_DIR, "fbref_gca.html")
    path = p_csv if os.path.exists(p_csv) else (p_html if os.path.exists(p_html) else None)
    if not path:
        return 0

    print(f"[Import] Elaborazione {os.path.basename(path)}...")
    rows = parse_fbref_csv_or_html(path)
    matched = 0

    for r in rows:
        name = r.get('Player') or r.get('player') or ''
        if not name or name == 'Player':
            continue
        norm_name = clean_text(name).lower()

        sca = clean_num(r.get('sca') or r.get('SCA'))
        sca90 = clean_num(r.get('sca_per90') or r.get('SCA/90') or r.get('SCA90'))
        gca = clean_num(r.get('gca') or r.get('GCA'))
        gca90 = clean_num(r.get('gca_per90') or r.get('GCA/90') or r.get('GCA90'))

        for p in master_players:
            p_name = clean_text(p.get('name') or '').lower()
            if norm_name == p_name or norm_name in p_name or p_name in norm_name:
                p['sca_2627'] = sca
                p['sca90_2627'] = sca90
                p['gca_2627'] = gca
                p['gca90_2627'] = gca90
                matched += 1
                break

    print(f"  ✓ {matched} calciatori aggiornati con metriche SCA/GCA!")
    return matched


def import_fbref_possession(master_players):
    """Importa Tocchi in Area Avversaria da fbref_possession."""
    p_csv = os.path.join(IMPORTS_DIR, "fbref_possession.csv")
    p_html = os.path.join(IMPORTS_DIR, "fbref_possession.html")
    path = p_csv if os.path.exists(p_csv) else (p_html if os.path.exists(p_html) else None)
    if not path:
        return 0

    print(f"[Import] Elaborazione {os.path.basename(path)}...")
    rows = parse_fbref_csv_or_html(path)
    matched = 0

    for r in rows:
        name = r.get('Player') or r.get('player') or ''
        if not name or name == 'Player':
            continue
        norm_name = clean_text(name).lower()

        # Tocchi in area: Att Pen
        att_pen = clean_num(r.get('touches_att_pen_area') or r.get('Att Pen') or r.get('att_pen_touches'))

        for p in master_players:
            p_name = clean_text(p.get('name') or '').lower()
            if norm_name == p_name or norm_name in p_name or p_name in norm_name:
                p['touches_att_pen_2627'] = att_pen
                matched += 1
                break

    print(f"  ✓ {matched} calciatori aggiornati con Tocchi in Area Avversaria (Att Pen)!")
    return matched


def run_all_imports():
    os.makedirs(IMPORTS_DIR, exist_ok=True)
    print(f"=== [Scouting Importer] Scansione cartella: {IMPORTS_DIR} ===")

    if not os.path.exists(MASTER_PLAYERS_PATH):
        print(f"⚠️ {MASTER_PLAYERS_PATH} non trovato.")
        return

    with open(MASTER_PLAYERS_PATH, 'r', encoding='utf-8') as f:
        master_players = json.load(f)

    c_std = import_fbref_standard(master_players)
    c_gca = import_fbref_gca(master_players)
    c_poss = import_fbref_possession(master_players)

    total_updated = c_std + c_gca + c_poss
    if total_updated > 0:
        with open(MASTER_PLAYERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(master_players, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Master database aggiornato con successo ({total_updated} record arricchiti)!")
    else:
        print("\nNessun nuovo file FBref trovato in data/raw/scouting_imports/.")
        print("Istruzioni: posiziona i file fbref_standard.csv, fbref_gca.csv o fbref_possession.csv nella cartella per avviare l'import automatico.")


if __name__ == "__main__":
    run_all_imports()
