import os
import sys
import re
import json
import pdfplumber
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from src.player_matcher import clean_text, match_player_name

REPORTS_DIR = os.path.join(ROOT_DIR, "data", "raw", "match report 26-27")
MATCHES_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_matches_g1_g2.json")
PLAYERS_CSV = os.path.join(ROOT_DIR, "data", "raw", "match_reports_players_g1_g2.csv")
TEAMS_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_teams.json")
TEAMS_CSV = os.path.join(ROOT_DIR, "data", "raw", "match_reports_teams.csv")
RANKINGS_PHYSICAL_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_rankings_physical.json")

def safe_int(val, default=0):
    if val is None or val == '' or pd.isna(val):
        return default
    try:
        clean = re.sub(r'[^\d\-]', '', str(val))
        return int(clean) if clean else default
    except Exception:
        return default

def safe_float(val, default=0.0):
    if val is None or val == '' or pd.isna(val):
        return default
    try:
        clean = str(val).replace('%', '').replace('m', '').replace(',', '.').strip()
        return float(clean)
    except Exception:
        return default

def find_page_by_keyword(pdf, keyword):
    for p in pdf.pages:
        txt = p.extract_text() or ""
        if keyword.lower() in txt.lower():
            return p
    return None

def parse_pdf_match_report(pdf_path):
    filename = os.path.basename(pdf_path)
    m_giornata = re.search(r'^(\d+)_', filename)
    giornata = int(m_giornata.group(1)) if m_giornata else 1

    with pdfplumber.open(pdf_path) as pdf:
        # Match info from page 2 (or page 1)
        p2 = pdf.pages[1] if len(pdf.pages) > 1 else pdf.pages[0]
        p2_text = p2.extract_text() or ""
        lines = [l.strip() for l in p2_text.split('\n') if l.strip()]

        home_team = "HOME"
        away_team = "AWAY"
        score_home = 0
        score_away = 0
        match_title = ""

        for line in lines[:10]:
            m = re.search(r'([A-Za-z\s]+?)\s+(\d+)\s*[-–]\s*(\d+)\s+([A-Za-z\s]+)', line)
            if m and not 'SERIE A' in line:
                home_team = m.group(1).strip().upper()
                score_home = int(m.group(2))
                score_away = int(m.group(3))
                away_team = m.group(4).strip().upper()
                match_title = f"{home_team} {score_home}-{score_away} {away_team}"
                break

        if not match_title:
            match_title = f"{home_team} {score_home}-{score_away} {away_team}"

        moduli = re.findall(r'\b(\d-\d-\d(?:-\d)?)\b', p2_text)

        match_info = {
            'filename': filename,
            'giornata': giornata,
            'match_title': match_title,
            'home_team': home_team,
            'away_team': away_team,
            'score_home': score_home,
            'score_away': score_away,
            'moduli': moduli
        }

        home_starters = set()
        away_starters = set()
        parts = p2_text.split('FORMAZIONI')
        if len(parts) > 1:
            form_txt = parts[1].split('A disposizione')[0]
            f_lines = [l.strip() for l in form_txt.split('\n') if l.strip()]
            for l in f_lines[1:12]: # 11 titolari
                m_h = re.match(r'^(\d+)\s+', l)
                m_a = re.search(r'\s+(\d+)$', l)
                if m_h: home_starters.add(int(m_h.group(1)))
                if m_a: away_starters.add(int(m_a.group(1)))

        # Page STATISTICHE GIOCATORE
        p_stat = find_page_by_keyword(pdf, "STATISTICHE GIOCATORE")
        if not p_stat:
            print(f"  [AVVISO] Pagina statistiche non trovata per {filename}")
            return match_info, []

        tables = p_stat.extract_tables()
        if len(tables) >= 3:
            team_tables = [
                (home_team, away_team, True, tables[1]),
                (away_team, home_team, False, tables[2])
            ]
        elif len(tables) == 2:
            team_tables = [
                (home_team, away_team, True, tables[0]),
                (away_team, home_team, False, tables[1])
            ]
        else:
            team_tables = []

        players = []
        for team, opp, is_home, tbl in team_tables:
            starters_set = home_starters if is_home else away_starters
            is_gk_section = True
            for row in tbl:
                if not row or len(row) < 3:
                    continue
                first_col = str(row[0]).strip() if row[0] else ''
                second_col = str(row[1]).strip() if row[1] else ''

                if 'GS' in row and 'PA' in row:
                    is_gk_section = True
                    continue
                if ('TP' in row or 'PT' in row or 'PC' in row) and ('G' in row):
                    is_gk_section = False
                    continue
                if not first_col.isdigit():
                    continue

                shirt_num = int(first_col)
                player_name = second_col.replace('\n', ' ').strip()
                mins_str = str(row[2]).strip() if len(row) > 2 else '0'
                mins = safe_int(mins_str)
                # Titolare reale (tra gli 11 al fischio d'inizio) vs Subentrato (dalla panchina)
                is_starter = (shirt_num in starters_set) if starters_set else (mins >= 50)

                if is_gk_section:
                    gs = safe_int(row[3]) if len(row) > 3 else 0
                    pa = safe_int(row[5]) if len(row) > 5 else 0
                    amm = safe_int(row[9]) if len(row) > 9 else 0
                    dam = safe_int(row[10]) if len(row) > 10 else 0
                    esp = safe_int(row[11]) if len(row) > 11 else 0
                    touches = safe_int(row[8]) if len(row) > 8 else 0

                    players.append({
                        'giornata': giornata,
                        'match_name': match_title,
                        'team': team,
                        'opponent': opp,
                        'is_home': is_home,
                        'shirt_num': shirt_num,
                        'player_name': player_name,
                        'role_gk': True,
                        'minutes': mins,
                        'is_starter': is_starter,
                        'goals': 0,
                        'own_goals': 0,
                        'assists': 0,
                        'total_shots': 0,
                        'shots_on_target': 0,
                        'woodworks': 0,
                        'key_passes': 0,
                        'chances_created': 0,
                        'touches_pg': touches,
                        'passes_completed': 0,
                        'pass_accuracy_pct': 0.0,
                        'forward_passes': 0,
                        'ball_recoveries': touches,
                        'fouls_drawn': 0,
                        'fouls_committed': 0,
                        'yellow_cards': amm,
                        'double_yellows': dam,
                        'red_cards': esp,
                        'goals_conceded': gs,
                        'saves': pa,
                        'clean_sheet': 1 if gs == 0 and mins >= 60 else 0,
                        'crosses': 0,
                        'dribbles': 0,
                        'passes_final_third': 0,
                        'km_distance': 0.0,
                        'km_jog': 0.0,
                        'km_run': 0.0,
                        'km_sprint': 0.0,
                        'sprint_speed_max': 0.0,
                        'run_speed_avg': 0.0
                    })
                else:
                    g = safe_int(row[3]) if len(row) > 3 else 0
                    aut = safe_int(row[4]) if len(row) > 4 else 0
                    t = safe_int(row[5]) if len(row) > 5 else 0
                    tp = safe_int(row[6]) if len(row) > 6 else 0
                    pt = safe_int(row[7]) if len(row) > 7 else 0
                    og = safe_int(row[8]) if len(row) > 8 else 0
                    fs = safe_int(row[9]) if len(row) > 9 else 0
                    pg = safe_int(row[10]) if len(row) > 10 else 0
                    as_v = safe_int(row[11]) if len(row) > 11 else 0
                    pc = safe_int(row[12]) if len(row) > 12 else 0
                    p = safe_int(row[13]) if len(row) > 13 else 0
                    p_pct = safe_float(row[14]) if len(row) > 14 else 0.0
                    pa = safe_int(row[15]) if len(row) > 15 else 0
                    r = safe_int(row[16]) if len(row) > 16 else 0
                    amm = safe_int(row[17]) if len(row) > 17 else 0
                    dam = safe_int(row[18]) if len(row) > 18 else 0
                    esp = safe_int(row[19]) if len(row) > 19 else 0

                    players.append({
                        'giornata': giornata,
                        'match_name': match_title,
                        'team': team,
                        'opponent': opp,
                        'is_home': is_home,
                        'shirt_num': shirt_num,
                        'player_name': player_name,
                        'role_gk': False,
                        'minutes': mins,
                        'is_starter': is_starter,
                        'goals': g,
                        'own_goals': aut,
                        'assists': as_v,
                        'total_shots': t,
                        'shots_on_target': tp,
                        'woodworks': pt,
                        'key_passes': pc,
                        'chances_created': og,
                        'touches_pg': pg,
                        'passes_completed': p,
                        'pass_accuracy_pct': p_pct,
                        'forward_passes': pa,
                        'ball_recoveries': r,
                        'fouls_drawn': fs,
                        'fouls_committed': 0,
                        'yellow_cards': amm,
                        'double_yellows': dam,
                        'red_cards': esp,
                        'goals_conceded': 0,
                        'saves': 0,
                        'clean_sheet': 0,
                        'crosses': 0,
                        'dribbles': 0,
                        'passes_final_third': 0,
                        'km_distance': 0.0,
                        'km_jog': 0.0,
                        'km_run': 0.0,
                        'km_sprint': 0.0,
                        'sprint_speed_max': 0.0,
                        'run_speed_avg': 0.0
                    })

        team_stats = parse_team_stats_from_pdf(pdf, match_info)
        rankings_data = enrich_rankings_and_physical(pdf, match_info, players, team_stats)
        return match_info, players, team_stats, rankings_data

def enrich_rankings_and_physical(pdf, match_info, players, team_stats):
    home_team = match_info['home_team']
    away_team = match_info['away_team']
    match_title = match_info['match_title']
    giornata = match_info['giornata']

    rankings_summary = {
        'giornata': giornata,
        'match_name': match_title,
        'home_team': home_team,
        'away_team': away_team,
        'rankings': {},
        'physical_players': {},
        'team_distance': {}
    }

    # 1. Pagina 5: Ranking Giocatori
    p5 = find_page_by_keyword(pdf, "STATISTICHE GIOCATORE")
    if p5:
        tbls = p5.extract_tables()
        if len(tbls) >= 4:
            t3 = tbls[3]
            def apply_ranking_block(data_rows, col_map):
                for r in data_rows:
                    for c_idx, stat_name in col_map.items():
                        if c_idx + 2 < len(r) and r[c_idx+1] and r[c_idx+2]:
                            p_team = str(r[c_idx+1]).strip()
                            raw_val = str(r[c_idx+2]).strip()
                            val = safe_int(raw_val)
                            m_p = re.match(r'^(.*?)\s+([A-Z]{3})$', p_team)
                            pname = m_p.group(1).strip() if m_p else p_team
                            rankings_summary['rankings'].setdefault(stat_name, []).append({'player': pname, 'value': val})
                            for p in players:
                                if match_player_name(clean_text(p['player_name']), clean_text(pname)):
                                    p[stat_name] = max(p.get(stat_name, 0), val)

            apply_ranking_block(t3[1:6], {6: 'passes_final_third'})
            apply_ranking_block(t3[7:12], {0: 'crosses', 9: 'dribbles'})

    # 2. Pagina 7: Performance Chilometriche-Velocistiche
    p7 = find_page_by_keyword(pdf, "Jog - Run - Sprint") or find_page_by_keyword(pdf, "Chilometriche")
    if p7:
        txt = p7.extract_text() or ''
        parts = txt.split('Jog - Run - Sprint')

        if len(parts) >= 3:
            p2 = parts[2].split('Velocità media in Run')[0]
            lines = [l.strip() for l in p2.split('\n') if l.strip()]
            for r_idx in [2, 6, 10, 14, 18]:
                if r_idx + 2 < len(lines):
                    m = re.match(r'^\d+\s+(.*?)\s+\d+\s+(.*)$', lines[r_idx])
                    tots = lines[r_idx+1].split()
                    splits = lines[r_idx+2].split()
                    if m and len(tots) >= 2 and len(splits) >= 6:
                        entries = [
                            (m.group(1).strip(), tots[0], splits[0], splits[1], splits[2], home_team),
                            (m.group(2).strip(), tots[1], splits[3], splits[4], splits[5], away_team)
                        ]
                        for pname, tot_v, j_v, r_v, s_v, t_name in entries:
                            tot_f = safe_float(tot_v)
                            j_f = safe_float(j_v)
                            r_f = safe_float(r_v)
                            s_f = safe_float(s_v)
                            rankings_summary['physical_players'][pname] = {
                                'team': t_name, 'km_distance': tot_f, 'km_jog': j_f, 'km_run': r_f, 'km_sprint': s_f
                            }
                            for p in players:
                                if match_player_name(clean_text(p['player_name']), clean_text(pname)):
                                    p['km_distance'] = tot_f
                                    p['km_jog'] = j_f
                                    p['km_run'] = r_f
                                    p['km_sprint'] = s_f

        lines_all = txt.split('\n')
        s_idx = next((i for i, l in enumerate(lines_all) if 'Velocità in Sprint' in l), None)
        if s_idx is not None:
            for l in lines_all[s_idx+1:s_idx+7]:
                m_sp = re.findall(r'(\d+)\s+([A-Z\.\s\u00C0-\u017F]+?)\s+([A-Z]{3})\s+([\d\.]+)', l)
                for rank, pname, t_code, sp_val in m_sp:
                    sp_f = safe_float(sp_val)
                    for p in players:
                        if match_player_name(clean_text(p['player_name']), clean_text(pname.strip())):
                            p['sprint_speed_max'] = max(p.get('sprint_speed_max', 0.0), sp_f)

        r_idx = next((i for i, l in enumerate(lines_all) if 'Velocità media in Run' in l), None)
        if r_idx is not None:
            for l in lines_all[r_idx+1:r_idx+7]:
                m_run = re.findall(r'(\d+)\s+([A-Z\.\s\u00C0-\u017F]+?)\s+([A-Z]{3})\s+([\d\.]+)', l)
                for rank, pname, t_code, r_val in m_run:
                    r_f = safe_float(r_val)
                    for p in players:
                        if match_player_name(clean_text(p['player_name']), clean_text(pname.strip())):
                            p['run_speed_avg'] = max(p.get('run_speed_avg', 0.0), r_f)

        if len(parts) >= 5 and len(team_stats) >= 2:
            m_h_dist = re.search(r'\(km\s+([\d\.]+)\s*\)', parts[3])
            m_a_dist = re.search(r'\(km\s+([\d\.]+)\s*\)', parts[4])
            lines_p4 = [l.strip() for l in parts[4].split('\n') if l.strip()]
            splits_line = lines_p4[1].split() if len(lines_p4) > 1 else []
            if m_h_dist and m_a_dist and len(splits_line) >= 6:
                h_dist = safe_float(m_h_dist.group(1))
                a_dist = safe_float(m_a_dist.group(1))
                team_stats[0]['team_distance_km'] = h_dist
                team_stats[0]['team_jog_km'] = safe_float(splits_line[0])
                team_stats[0]['team_run_km'] = safe_float(splits_line[1])
                team_stats[0]['team_sprint_km'] = safe_float(splits_line[2])

                team_stats[1]['team_distance_km'] = a_dist
                team_stats[1]['team_jog_km'] = safe_float(splits_line[3])
                team_stats[1]['team_run_km'] = safe_float(splits_line[4])
                team_stats[1]['team_sprint_km'] = safe_float(splits_line[5])

                rankings_summary['team_distance'] = {
                    home_team: {'total_km': h_dist, 'jog': safe_float(splits_line[0]), 'run': safe_float(splits_line[1]), 'sprint': safe_float(splits_line[2])},
                    away_team: {'total_km': a_dist, 'jog': safe_float(splits_line[3]), 'run': safe_float(splits_line[4]), 'sprint': safe_float(splits_line[5])}
                }

    return rankings_summary

def parse_team_stats_from_pdf(pdf, match_info):
    home = match_info['home_team']
    away = match_info['away_team']
    match_title = match_info['match_title']
    giornata = match_info['giornata']

    p_stat = find_page_by_keyword(pdf, "STATISTICHE SQUADRE") or find_page_by_keyword(pdf, "TEMPO DI GIOCO")
    if not p_stat:
        return []

    h_data = {
        'giornata': giornata,
        'match_name': match_title,
        'team': home,
        'opponent': away,
        'is_home': True,
        'goals_scored': match_info.get('score_home', 0),
        'goals_conceded': match_info.get('score_away', 0),
        'possession_pct': 50.0,
        'total_shots': 0,
        'shots_on_target': 0,
        'shots_in_box': 0,
        'woodworks': 0,
        'chances_created': 0,
        'key_passes': 0,
        'assists': 0,
        'fouls_committed': 0,
        'corners': 0,
        'crosses': '0/0',
        'dribbles': 0,
        'passes_completed': 0,
        'pass_accuracy_pct': 0.0,
        'passes_final_third': 0,
        'forward_passes': 0,
        'long_passes': 0,
        'saves': 0,
        'recoveries': 0,
        'team_distance_km': 0.0,
        'team_jog_km': 0.0,
        'team_run_km': 0.0,
        'team_sprint_km': 0.0
    }
    a_data = {
        'giornata': giornata,
        'match_name': match_title,
        'team': away,
        'opponent': home,
        'is_home': False,
        'goals_scored': match_info.get('score_away', 0),
        'goals_conceded': match_info.get('score_home', 0),
        'possession_pct': 50.0,
        'total_shots': 0,
        'shots_on_target': 0,
        'shots_in_box': 0,
        'woodworks': 0,
        'chances_created': 0,
        'key_passes': 0,
        'assists': 0,
        'fouls_committed': 0,
        'corners': 0,
        'crosses': '0/0',
        'dribbles': 0,
        'passes_completed': 0,
        'pass_accuracy_pct': 0.0,
        'passes_final_third': 0,
        'forward_passes': 0,
        'long_passes': 0,
        'saves': 0,
        'recoveries': 0,
        'team_distance_km': 0.0,
        'team_jog_km': 0.0,
        'team_run_km': 0.0,
        'team_sprint_km': 0.0
    }

    txt = p_stat.extract_text() or ''
    m_poss = re.search(r'([\d\.,]+)%\s+([\d\.,]+)%', txt)
    if m_poss:
        h_data['possession_pct'] = safe_float(m_poss.group(1))
        a_data['possession_pct'] = safe_float(m_poss.group(2))

    tbls = p_stat.extract_tables()
    for tbl in tbls:
        for r in tbl:
            if not r or len(r) < 2:
                continue
            first = str(r[0]).strip() if r[0] else ''
            away_val = str(r[2]).strip() if len(r) > 2 and r[2] else (str(r[1]).strip() if len(r) > 1 and r[1] else '')
            m_h = re.search(r'(\d+)\s*$', first)
            val_h = m_h.group(1) if m_h else ''
            label = re.sub(r'\s*\d+\s*$', '', first).strip().lower()

            if 'tiri in porta da area' in label:
                h_data['shots_in_box'] = safe_int(val_h)
                a_data['shots_in_box'] = safe_int(away_val)
            elif 'tiri in porta' in label:
                h_data['shots_on_target'] = safe_int(val_h)
                a_data['shots_on_target'] = safe_int(away_val)
            elif label == 'tiri':
                h_data['total_shots'] = safe_int(val_h)
                a_data['total_shots'] = safe_int(away_val)
            elif 'occasioni da gol' in label:
                h_data['chances_created'] = safe_int(val_h)
                a_data['chances_created'] = safe_int(away_val)
            elif 'passaggi chiave' in label:
                h_data['key_passes'] = safe_int(val_h)
                a_data['key_passes'] = safe_int(away_val)
            elif 'assist' in label:
                h_data['assists'] = safe_int(val_h)
                a_data['assists'] = safe_int(away_val)
            elif 'falli fatti' in label:
                h_data['fouls_committed'] = safe_int(val_h)
                a_data['fouls_committed'] = safe_int(away_val)
            elif 'corner' in label:
                h_data['corners'] = safe_int(val_h)
                a_data['corners'] = safe_int(away_val)
            elif 'cross' in label:
                m_c1 = re.search(r'(\d+/\d+)', first)
                m_c2 = re.search(r'(\d+/\d+)', away_val)
                if m_c1: h_data['crosses'] = m_c1.group(1)
                if m_c2: a_data['crosses'] = m_c2.group(1)
            elif 'dribbling' in label:
                h_data['dribbles'] = safe_int(val_h)
                a_data['dribbles'] = safe_int(away_val)
            elif 'passaggi riusciti in ultimo terzo' in label:
                h_data['passes_final_third'] = safe_int(val_h)
                a_data['passes_final_third'] = safe_int(away_val)
            elif 'palloni giocati in avanti' in label:
                h_data['forward_passes'] = safe_int(val_h)
                a_data['forward_passes'] = safe_int(away_val)
            elif 'passaggi lunghi' in label:
                h_data['long_passes'] = safe_int(val_h)
                a_data['long_passes'] = safe_int(away_val)
            elif 'passaggi riusciti' in label and 'tentati' not in label:
                h_data['passes_completed'] = safe_int(val_h)
                a_data['passes_completed'] = safe_int(away_val)
            elif 'passaggi riusciti/tentati' in label:
                h_data['pass_accuracy_pct'] = safe_float(val_h)
                a_data['pass_accuracy_pct'] = safe_float(away_val)
            elif 'parate' in label:
                h_data['saves'] = safe_int(r[1]) if len(r) > 1 and r[1] else safe_int(val_h)
                a_data['saves'] = safe_int(r[2]) if len(r) > 2 and r[2] else safe_int(away_val)
            elif 'recuperi' in label:
                h_data['recoveries'] = safe_int(r[1]) if len(r) > 1 and r[1] else safe_int(val_h)
                a_data['recoveries'] = safe_int(r[2]) if len(r) > 2 and r[2] else safe_int(away_val)
            elif 'pali' in label or 'traverse' in label:
                if 'traverse' in label:
                    if len(r) > 1 and r[1]: h_data['woodworks'] += safe_int(r[1])
                    if len(r) > 2 and r[2]: a_data['woodworks'] += safe_int(r[2])
                else:
                    if len(r) > 2 and r[2]: a_data['woodworks'] += safe_int(r[2])

    return [h_data, a_data]

def fix_g2_goalkeepers(df_g2):
    """
    Ripara le righe portiere della Giornata 2 dove per un bug storico
    il portiere (prima riga di ogni squadra) era stato salvato con role_gk=False,
    goals=GS e total_shots=PA.
    """
    df_fixed = df_g2.copy()
    for (match_name, team), group in df_fixed.groupby(['match_name', 'team']):
        # Correzione titolari G2: esattamente i primi 11 per minutaggio
        sorted_indices = group.sort_values(by='minutes', ascending=False).index
        starter_indices = set(sorted_indices[:11])
        for idx in group.index:
            df_fixed.loc[idx, 'is_starter'] = (idx in starter_indices)

        # Correzione portiere G2
        first_idx = group.index[0]
        row = df_fixed.loc[first_idx]
        if not row['role_gk']:
            gs = row['goals']
            pa = row['total_shots']
            mins = row['minutes']
            df_fixed.loc[first_idx, 'role_gk'] = True
            df_fixed.loc[first_idx, 'goals_conceded'] = gs
            df_fixed.loc[first_idx, 'saves'] = pa
            df_fixed.loc[first_idx, 'goals'] = 0
            df_fixed.loc[first_idx, 'assists'] = 0
            df_fixed.loc[first_idx, 'total_shots'] = 0
            df_fixed.loc[first_idx, 'shots_on_target'] = 0
            df_fixed.loc[first_idx, 'key_passes'] = 0
            df_fixed.loc[first_idx, 'clean_sheet'] = 1 if gs == 0 and mins >= 60 else 0
    return df_fixed

def sync_all_match_reports():
    print("=== [Sync Match Reports] Avvio parsing e sincronizzazione Match Reports ===")
    
    # 1. Trova tutti i PDF di match report presenti nella cartella (iniziano con numero_giornata_)
    pdf_files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf') and re.match(r'^\d+_', f)])
    print(f"Trovati {len(pdf_files)} file PDF in '{REPORTS_DIR}'.")

    parsed_matches = []
    parsed_players = []
    parsed_teams = []
    parsed_rankings = []

    for fname in pdf_files:
        pdf_path = os.path.join(REPORTS_DIR, fname)
        print(f"  Elaborazione: {fname}...")
        try:
            m_info, p_list, t_list, r_info = parse_pdf_match_report(pdf_path)
            parsed_matches.append(m_info)
            parsed_players.extend(p_list)
            parsed_teams.extend(t_list)
            parsed_rankings.append(r_info)
            print(f"    ✓ {m_info['match_title']} (G{m_info['giornata']}) -> {len(p_list)} calciatori, {len(t_list)} statistiche squadra.")
        except Exception as e:
            print(f"    [ERRORE] Errore nel parsing di {fname}: {e}")

    # 2. Carica partite e giocatori esistenti
    existing_matches = []
    if os.path.exists(MATCHES_JSON):
        with open(MATCHES_JSON, 'r', encoding='utf-8') as f:
            existing_matches = json.load(f)

    existing_df = pd.DataFrame()
    if os.path.exists(PLAYERS_CSV):
        existing_df = pd.read_csv(PLAYERS_CSV)

    # 3. Mantieni partite e giocatori esistenti non presenti nei PDF attuali (es. G2 riparando i portieri)
    parsed_match_keys = {(m['match_title'], m['giornata']) for m in parsed_matches}
    unparsed_existing_matches = [m for m in existing_matches if (m.get('match_title'), m.get('giornata')) not in parsed_match_keys]

    unparsed_players_dfs = []
    if not existing_df.empty and 'giornata' in existing_df.columns:
        unparsed_match_names = {m.get('match_title') for m in unparsed_existing_matches}
        unparsed_giornate = {m.get('giornata') for m in unparsed_existing_matches}
        for g_num in sorted(unparsed_giornate):
            df_g = existing_df[(existing_df['giornata'] == g_num) & (existing_df['match_name'].isin(unparsed_match_names))]
            if g_num == 2:
                df_g = fix_g2_goalkeepers(df_g)
                print(f"  ✓ Preservate e riparate {len(df_g)} righe della Giornata 2.")
            elif not df_g.empty:
                print(f"  ✓ Preservate {len(df_g)} righe storiche della Giornata {g_num}.")
            if not df_g.empty:
                unparsed_players_dfs.append(df_g)

    # 4. Unisci le partite evitando duplicati per match_title + giornata
    all_candidate_matches = list(parsed_matches) + unparsed_existing_matches
    final_matches = []
    seen_match_keys = set()
    for m in all_candidate_matches:
        key = (m['match_title'], m['giornata'])
        if key not in seen_match_keys:
            final_matches.append(m)
            seen_match_keys.add(key)

    # Ordina per giornata e partita
    final_matches.sort(key=lambda x: (x.get('giornata', 1), x.get('match_title', '')))

    # 5. Unisci il DataFrame dei giocatori
    df_new_parsed = pd.DataFrame(parsed_players)
    if unparsed_players_dfs:
        df_combined = pd.concat([df_new_parsed] + unparsed_players_dfs, ignore_index=True)
    else:
        df_combined = df_new_parsed

    # Assicura presenza di tutte le colonne metriche
    for col in ['crosses', 'dribbles', 'passes_final_third', 'own_goals']:
        if col not in df_combined.columns:
            df_combined[col] = 0
        df_combined[col] = df_combined[col].fillna(0).astype(int)
    for col in ['km_distance', 'km_jog', 'km_run', 'km_sprint', 'sprint_speed_max', 'run_speed_avg']:
        if col not in df_combined.columns:
            df_combined[col] = 0.0
        df_combined[col] = df_combined[col].fillna(0.0).astype(float)

    # Rimuovi eventuali duplicati esatti per (match_name, team, shirt_num, player_name, giornata)
    df_combined.drop_duplicates(subset=['match_name', 'team', 'shirt_num', 'player_name', 'giornata'], inplace=True)
    df_combined.sort_values(by=['giornata', 'match_name', 'team', 'role_gk', 'shirt_num'], ascending=[True, True, True, False, True], inplace=True)

    # 6. Salva MATCHES_JSON e PLAYERS_CSV
    with open(MATCHES_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_matches, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Salvato {MATCHES_JSON} ({len(final_matches)} partite totali).")

    df_combined.to_csv(PLAYERS_CSV, index=False, encoding='utf-8')
    print(f"✓ Salvato {PLAYERS_CSV} ({len(df_combined)} righe prestazione totali).")

    # 7. Salva TEAMS_JSON e TEAMS_CSV (Statistiche Ufficiali di Squadra)
    existing_teams = []
    if os.path.exists(TEAMS_JSON):
        try:
            with open(TEAMS_JSON, 'r', encoding='utf-8') as f:
                existing_teams = json.load(f)
        except Exception:
            pass

    parsed_team_keys = {(t['match_name'], t['team'], t['giornata']) for t in parsed_teams}
    final_teams = list(parsed_teams) + [t for t in existing_teams if (t.get('match_name'), t.get('team'), t.get('giornata')) not in parsed_team_keys]
    final_teams.sort(key=lambda x: (x.get('giornata', 1), x.get('match_name', ''), x.get('team', '')))

    if final_teams:
        df_teams = pd.DataFrame(final_teams)
        df_teams.drop_duplicates(subset=['match_name', 'team', 'giornata'], inplace=True)
        df_teams.sort_values(by=['giornata', 'match_name', 'team'], ascending=[True, True, True], inplace=True)
        with open(TEAMS_JSON, 'w', encoding='utf-8') as f:
            json.dump(final_teams, f, ensure_ascii=False, indent=2)
        df_teams.to_csv(TEAMS_CSV, index=False, encoding='utf-8')
        print(f"✓ Salvato {TEAMS_JSON} e {TEAMS_CSV} ({len(df_teams)} record statistici di squadra totali).")

    # 8. Salva RANKINGS_PHYSICAL_JSON (Ranking Dribbling, Cross, 3/4 e Performance Chilometriche)
    existing_rankings = []
    if os.path.exists(RANKINGS_PHYSICAL_JSON):
        try:
            with open(RANKINGS_PHYSICAL_JSON, 'r', encoding='utf-8') as f:
                existing_rankings = json.load(f)
        except Exception:
            pass

    parsed_ranking_keys = {(r['match_name'], r['giornata']) for r in parsed_rankings}
    final_rankings = list(parsed_rankings) + [r for r in existing_rankings if (r.get('match_name'), r.get('giornata')) not in parsed_ranking_keys]
    final_rankings.sort(key=lambda x: (x.get('giornata', 1), x.get('match_name', '')))

    if final_rankings:
        with open(RANKINGS_PHYSICAL_JSON, 'w', encoding='utf-8') as f:
            json.dump(final_rankings, f, ensure_ascii=False, indent=2)
        print(f"✓ Salvato {RANKINGS_PHYSICAL_JSON} ({len(final_rankings)} partite totali con ranking e metriche fisico-atletiche).")

    # Statistiche di riepilogo
    g_counts = df_combined['giornata'].value_counts().to_dict()
    print(f"Riepilogo presenze per giornata: {g_counts}")
    gk_count = len(df_combined[df_combined['role_gk'] == True])
    print(f"Portieri totali a referto: {gk_count} (validati)")

    return final_matches, df_combined

if __name__ == '__main__':
    sync_all_match_reports()
