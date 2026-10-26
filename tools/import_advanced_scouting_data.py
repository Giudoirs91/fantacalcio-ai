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

from src.player_matcher import clean_text, match_player_name

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
    """Estrae righe e colonne da un file CSV o HTML esportato da FBref con disambiguazione per 90."""
    if not os.path.exists(file_path):
        return []

    results = []
    if file_path.endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [l for l in f.readlines() if not l.startswith('#') and not l.startswith('---')]
            reader = csv.reader(lines)
            all_rows = [r for r in reader if r and len(r) >= 5]
            if len(all_rows) < 2:
                return []
            
            # Check if row 0 has super headers like 'Per 90 Minutes'
            super_header = all_rows[0]
            sub_header = all_rows[1]
            if 'Player' in sub_header or 'Giocatore' in sub_header:
                header = []
                seen = {}
                for sup, sub in zip(super_header, sub_header):
                    sub_clean = sub.strip()
                    sup_clean = sup.strip() if sup else ''
                    if 'Per 90' in sup_clean or seen.get(sub_clean, 0) > 0:
                        col_name = f"{sub_clean}_per90"
                    else:
                        col_name = sub_clean
                    seen[sub_clean] = seen.get(sub_clean, 0) + 1
                    header.append(col_name)
                data_rows = all_rows[2:]
            else:
                # Single header row
                header = [c.strip() for c in all_rows[0]]
                data_rows = all_rows[1:]

            for row in data_rows:
                if len(row) == len(header):
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
    """Importa presenze, minutaggi, gol non su rigore (G-PK), rigori e metriche per90 da standard_stats.csv o fbref_standard."""
    candidates = [
        os.path.join(IMPORTS_DIR, "standard_stats.csv"),
        os.path.join(IMPORTS_DIR, "fbref_standard.csv"),
        os.path.join(IMPORTS_DIR, "stats_serie_a_7g.csv"),
        os.path.join(IMPORTS_DIR, "fbref_standard.html")
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
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
        g_pk_per90 = clean_num(r.get('G-PK_per90'))
        ga_per90 = clean_num(r.get('G+A_per90') or r.get('G+A-PK_per90'))
        mp_val = clean_num(r.get('MP'))
        starts_val = clean_num(r.get('Starts'))

        for p in master_players:
            p_name = p.get('name') or ''
            clean_pn = clean_text(p_name).lower()
            if norm_name == clean_pn or norm_name in clean_pn or clean_pn in norm_name or match_player_name(p_name, name):
                if npxg > 0:
                    p['npxg_2627'] = npxg
                if npxg90 > 0:
                    p['npxg90_2627'] = npxg90
                p['goals_non_penalty_2627'] = g_minus_pk
                p['pk_scored_fbref_2627'] = pk_scored
                p['pk_attempted_fbref_2627'] = pk_att
                if g_pk_per90 > 0:
                    p['g_minus_pk_per90_2627'] = g_pk_per90
                if ga_per90 > 0:
                    p['g_plus_a_per90_2627'] = ga_per90
                p['mp_fbref_2627'] = mp_val
                p['starts_fbref_2627'] = starts_val
                p['mins_fbref_2627'] = min_played
                matched += 1
                break

    print(f"  ✓ {matched} calciatori aggiornati con metriche FBref Standard (G-PK, npxG, Per90) da {os.path.basename(path)}!")
    return matched


def import_fbref_miscellaneous(master_players):
    """Importa Cross, Intercetti, Tackle vinti, Falli, Fuorigioco, Rigori concessi/procurati, Autogol da stats_miscellanous.csv."""
    candidates = [
        os.path.join(IMPORTS_DIR, "stats_miscellanous.csv"),
        os.path.join(IMPORTS_DIR, "fbref_miscellaneous.csv"),
        os.path.join(IMPORTS_DIR, "fbref_miscellaneous.html")
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
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

        crs = clean_num(r.get('Crs'))
        interc = clean_num(r.get('Int'))
        tklw = clean_num(r.get('TklW'))
        fls = clean_num(r.get('Fls'))
        fld = clean_num(r.get('Fld'))
        off = clean_num(r.get('Off'))
        pkwon = clean_num(r.get('PKwon'))
        pkcon = clean_num(r.get('PKcon'))
        og = clean_num(r.get('OG'))
        crd2y = clean_num(r.get('2CrdY'))

        for p in master_players:
            p_name = p.get('name') or ''
            clean_pn = clean_text(p_name).lower()
            if norm_name == clean_pn or norm_name in clean_pn or clean_pn in norm_name or match_player_name(p_name, name):
                p['crosses_fbref_2627'] = crs
                p['interceptions_fbref_2627'] = interc
                p['tackles_won_fbref_2627'] = tklw
                p['fouls_committed_fbref_2627'] = fls
                p['fouls_drawn_fbref_2627'] = fld
                p['offsides_fbref_2627'] = off
                p['penalties_won_fbref_2627'] = pkwon
                p['penalties_conceded_fbref_2627'] = pkcon
                p['autogol_fbref_2627'] = og
                p['double_yellow_fbref_2627'] = crd2y
                matched += 1
                break

    print(f"  ✓ {matched} calciatori aggiornati con metriche FBref Miscellaneous (Cross, Intercetti, Tackle, Rigori, Autogol)!")
    return matched


def import_fbref_shooting(master_players):
    """Importa Tiri totali, Tiri in porta, % precisione tiro, Tiri/90 da Player_Shooting.csv."""
    candidates = [
        os.path.join(IMPORTS_DIR, "Player_Shooting.csv"),
        os.path.join(IMPORTS_DIR, "fbref_shooting.csv"),
        os.path.join(IMPORTS_DIR, "fbref_shooting.html")
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
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

        sh = clean_num(r.get('Sh'))
        sot = clean_num(r.get('SoT'))
        sot_pct = clean_num(r.get('SoT%'))
        sh90 = clean_num(r.get('Sh/90') or r.get('Sh_per90'))
        sot90 = clean_num(r.get('SoT/90') or r.get('SoT_per90'))
        g_sh = clean_num(r.get('G/Sh'))
        g_sot = clean_num(r.get('G/SoT'))

        for p in master_players:
            p_name = p.get('name') or ''
            clean_pn = clean_text(p_name).lower()
            if norm_name == clean_pn or norm_name in clean_pn or clean_pn in norm_name or match_player_name(p_name, name):
                p['shots_fbref_2627'] = sh
                p['shots_on_target_fbref_2627'] = sot
                p['shots_on_target_pct_fbref_2627'] = sot_pct
                p['shots_per90_fbref_2627'] = sh90
                p['shots_on_target_per90_fbref_2627'] = sot90
                p['goals_per_shot_fbref_2627'] = g_sh
                p['goals_per_sot_fbref_2627'] = g_sot
                matched += 1
                break

    print(f"  ✓ {matched} calciatori aggiornati con metriche FBref Shooting (Tiri, Tiri specchio, SoT%, Sh/90)!")
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
            p_name = p.get('name') or ''
            clean_pn = clean_text(p_name).lower()
            if norm_name == clean_pn or norm_name in clean_pn or clean_pn in norm_name or match_player_name(p_name, name):
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
            p_name = p.get('name') or ''
            clean_pn = clean_text(p_name).lower()
            if norm_name == clean_pn or norm_name in clean_pn or clean_pn in norm_name or match_player_name(p_name, name):
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
    c_misc = import_fbref_miscellaneous(master_players)
    c_shoot = import_fbref_shooting(master_players)
    c_gca = import_fbref_gca(master_players)
    c_poss = import_fbref_possession(master_players)

    total_updated = c_std + c_misc + c_shoot + c_gca + c_poss
    if total_updated > 0:
        with open(MASTER_PLAYERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(master_players, f, indent=2, ensure_ascii=False)
        root_path = os.path.join(ROOT_DIR, "processed_players_master.json")
        with open(root_path, 'w', encoding='utf-8') as f:
            json.dump(master_players, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Master database aggiornato con successo ({total_updated} record arricchiti su entrambi i file)!")
    else:
        print("\nNessun nuovo file FBref trovato in data/raw/scouting_imports/.")
        print("Istruzioni: posiziona i file fbref_standard.csv, stats_miscellanous.csv, Player_Shooting.csv nella cartella per avviare l'import automatico.")


if __name__ == "__main__":
    run_all_imports()
