import os
import re
import json
import pdfplumber
import pandas as pd

REPORT_DIR = "match report 26-27"
OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)

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

def extract_match_info(pdf):
    p2 = pdf.pages[1] if len(pdf.pages) > 1 else pdf.pages[0]
    p2_text = p2.extract_text() or ""
    lines = [l.strip() for l in p2_text.split('\n') if l.strip()]
    
    match_title = "Unknown Match"
    home_team = "Home"
    away_team = "Away"
    score_home = 0
    score_away = 0
    
    for line in lines[:10]:
        m = re.search(r'([A-Za-z\s]+?)\s+(\d+)\s*[-–]\s*(\d+)\s+([A-Za-z\s]+)', line)
        if m and not 'SERIE A' in line:
            home_team = m.group(1).strip().upper()
            score_home = int(m.group(2))
            score_away = int(m.group(3))
            away_team = m.group(4).strip().upper()
            match_title = f"{home_team} {score_home}-{score_away} {away_team}"
            break
            
    return {
        'match_title': match_title,
        'home_team': home_team,
        'away_team': away_team,
        'score_home': score_home,
        'score_away': score_away
    }

def parse_team_stats(pdf, match_info):
    home = match_info['home_team']
    away = match_info['away_team']
    
    team_records = {
        home: {
            'match_name': match_info['match_title'],
            'team': home,
            'opponent': away,
            'is_home': True,
            'goals_scored': match_info['score_home'],
            'goals_conceded': match_info['score_away'],
            'total_shots': 0,
            'shots_on_target': 0,
            'shots_in_box': 0,
            'chances_created': 0,
            'key_passes': 0,
            'assists': 0,
            'fouls_committed': 0,
            'corners': 0,
            'dribbles': 0,
            'passes_final_third': 0,
            'forward_passes': 0,
            'recoveries': 0,
            'danger_index_pct': 50.0,
            'baricentro_m': 50.0
        },
        away: {
            'match_name': match_info['match_title'],
            'team': away,
            'opponent': home,
            'is_home': False,
            'goals_scored': match_info['score_away'],
            'goals_conceded': match_info['score_home'],
            'total_shots': 0,
            'shots_on_target': 0,
            'shots_in_box': 0,
            'chances_created': 0,
            'key_passes': 0,
            'assists': 0,
            'fouls_committed': 0,
            'corners': 0,
            'dribbles': 0,
            'passes_final_third': 0,
            'forward_passes': 0,
            'recoveries': 0,
            'danger_index_pct': 50.0,
            'baricentro_m': 50.0
        }
    }
    
    p_stat = find_page_by_keyword(pdf, "STATISTICHE SQUADRE") or find_page_by_keyword(pdf, "TEMPO DI GIOCO")
    if p_stat:
        tables = p_stat.extract_tables()
        for t in tables:
            for row in t:
                if len(row) >= 3:
                    stat_name = str(row[0]).strip().lower() if row[0] else ''
                    val_h = str(row[1]).strip() if row[1] else ''
                    val_a = str(row[2]).strip() if row[2] else ''
                    
                    if 'tiri in porta da area' in stat_name:
                        team_records[home]['shots_in_box'] = safe_int(val_h)
                        team_records[away]['shots_in_box'] = safe_int(val_a)
                    elif 'tiri in porta' in stat_name:
                        team_records[home]['shots_on_target'] = safe_int(val_h)
                        team_records[away]['shots_on_target'] = safe_int(val_a)
                    elif 'tiri' in stat_name:
                        team_records[home]['total_shots'] = safe_int(val_h)
                        team_records[away]['total_shots'] = safe_int(val_a)
                    elif 'occasioni da gol' in stat_name:
                        team_records[home]['chances_created'] = safe_int(val_h)
                        team_records[away]['chances_created'] = safe_int(val_a)
                    elif 'passaggi chiave' in stat_name:
                        team_records[home]['key_passes'] = safe_int(val_h)
                        team_records[away]['key_passes'] = safe_int(val_a)
                    elif 'assist' in stat_name:
                        team_records[home]['assists'] = safe_int(val_h)
                        team_records[away]['assists'] = safe_int(val_a)
                    elif 'falli fatti' in stat_name:
                        team_records[home]['fouls_committed'] = safe_int(val_h)
                        team_records[away]['fouls_committed'] = safe_int(val_a)
                    elif 'corner' in stat_name:
                        team_records[home]['corners'] = safe_int(val_h)
                        team_records[away]['corners'] = safe_int(val_a)
                    elif 'dribbling' in stat_name:
                        team_records[home]['dribbles'] = safe_int(val_h)
                        team_records[away]['dribbles'] = safe_int(val_a)
                    elif 'passaggi riusciti in ultimo terzo' in stat_name:
                        team_records[home]['passes_final_third'] = safe_int(val_h)
                        team_records[away]['passes_final_third'] = safe_int(val_a)
                    elif 'palloni giocati in avanti' in stat_name:
                        team_records[home]['forward_passes'] = safe_int(val_h)
                        team_records[away]['forward_passes'] = safe_int(val_a)
                    elif 'recuperi' in stat_name:
                        team_records[home]['recoveries'] = safe_int(val_h)
                        team_records[away]['recoveries'] = safe_int(val_a)

    p_dang = find_page_by_keyword(pdf, "INDICATORI DI SQUADRA") or find_page_by_keyword(pdf, "PERICOLOSIT")
    if p_dang:
        p6_text = p_dang.extract_text() or ""
        m_dang = re.search(r'([\d\.,]+)%\s*PERICOLOSIT[A-Z\s]*?([\d\.,]+)%', p6_text)
        if m_dang:
            team_records[home]['danger_index_pct'] = safe_float(m_dang.group(1))
            team_records[away]['danger_index_pct'] = safe_float(m_dang.group(2))

    p_bari = find_page_by_keyword(pdf, "BARICENTRO")
    if p_bari:
        p9_text = p_bari.extract_text() or ""
        m_bari = re.findall(r'Baricentro\s*([\d\.,]+)m', p9_text)
        if len(m_bari) >= 2:
            team_records[home]['baricentro_m'] = safe_float(m_bari[0])
            team_records[away]['baricentro_m'] = safe_float(m_bari[1])

    return list(team_records.values())

def parse_player_stats(pdf, match_info):
    p5 = find_page_by_keyword(pdf, "STATISTICHE GIOCATORE")
    if not p5:
        return []
        
    tables = p5.extract_tables()
    players = []
    
    team_tables = []
    if len(tables) >= 3:
        team_tables = [
            (match_info['home_team'], match_info['away_team'], True, tables[1]),
            (match_info['away_team'], match_info['home_team'], False, tables[2])
        ]
    
    for team, opp, is_home, tbl in team_tables:
        is_gk_section = True
        for row in tbl:
            if not row or len(row) < 3:
                continue
            
            first_col = str(row[0]).strip() if row[0] else ''
            second_col = str(row[1]).strip() if row[1] else ''
            
            if 'MIN' in row or 'G' in row:
                is_gk_section = False
                continue
            
            if not first_col.isdigit():
                continue
                
            shirt_num = int(first_col)
            player_name = second_col.replace('\n', ' ').strip()
            mins_str = str(row[2]).strip() if len(row) > 2 else '0'
            mins = safe_int(mins_str)
            is_starter = (mins >= 45 or mins_str.endswith("'"))
            
            if is_gk_section:
                # Goalkeeper
                gs = safe_int(row[3]) if len(row) > 3 else 0
                pa = safe_int(row[5]) if len(row) > 5 else 0
                re_v = safe_int(row[7]) if len(row) > 7 else 0
                amm = safe_int(row[9]) if len(row) > 9 else 0
                dam = safe_int(row[10]) if len(row) > 10 else 0
                esp = safe_int(row[11]) if len(row) > 11 else 0
                
                players.append({
                    'match_name': match_info['match_title'],
                    'team': team,
                    'opponent': opp,
                    'is_home': is_home,
                    'shirt_num': shirt_num,
                    'player_name': player_name,
                    'role_gk': True,
                    'minutes': mins,
                    'is_starter': is_starter,
                    'goals': 0,
                    'assists': 0,
                    'total_shots': 0,
                    'shots_on_target': 0,
                    'woodworks': 0,
                    'key_passes': 0,
                    'chances_created': 0,
                    'touches_pg': safe_int(row[8]) if len(row) > 8 else 0,
                    'passes_completed': 0,
                    'pass_accuracy_pct': 0.0,
                    'forward_passes': 0,
                    'ball_recoveries': 0,
                    'fouls_drawn': 0,
                    'fouls_committed': 0,
                    'yellow_cards': amm,
                    'double_yellows': dam,
                    'red_cards': esp,
                    'goals_conceded': gs,
                    'saves': pa + re_v
                })
            else:
                # Outfield player
                g = safe_int(row[3]) if len(row) > 3 else 0
                t = safe_int(row[5]) if len(row) > 5 else 0
                tp = safe_int(row[6]) if len(row) > 6 else 0
                pt = safe_int(row[7]) if len(row) > 7 else 0
                og = safe_int(row[8]) if len(row) > 8 else 0
                fs = safe_int(row[9]) if len(row) > 9 else 0
                pg = safe_int(row[10]) if len(row) > 10 else 0
                ass = safe_int(row[11]) if len(row) > 11 else 0
                pc = safe_int(row[12]) if len(row) > 12 else 0
                p_comp = safe_int(row[13]) if len(row) > 13 else 0
                p_acc = safe_float(row[14]) if len(row) > 14 else 0.0
                pa_fwd = safe_int(row[15]) if len(row) > 15 else 0
                r_rec = safe_int(row[16]) if len(row) > 16 else 0
                amm = safe_int(row[17]) if len(row) > 17 else 0
                dam = safe_int(row[18]) if len(row) > 18 else 0
                esp = safe_int(row[19]) if len(row) > 19 else 0
                
                players.append({
                    'match_name': match_info['match_title'],
                    'team': team,
                    'opponent': opp,
                    'is_home': is_home,
                    'shirt_num': shirt_num,
                    'player_name': player_name,
                    'role_gk': False,
                    'minutes': mins,
                    'is_starter': is_starter,
                    'goals': g,
                    'assists': ass,
                    'total_shots': t,
                    'shots_on_target': tp,
                    'woodworks': pt,
                    'key_passes': pc,
                    'chances_created': og,
                    'touches_pg': pg,
                    'passes_completed': p_comp,
                    'pass_accuracy_pct': p_acc,
                    'forward_passes': pa_fwd,
                    'ball_recoveries': r_rec,
                    'fouls_drawn': fs,
                    'fouls_committed': 0,
                    'yellow_cards': amm,
                    'double_yellows': dam,
                    'red_cards': esp,
                    'goals_conceded': 0,
                    'saves': 0
                })

    return players

def process_all_match_reports():
    pdf_files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")])
    print(f"=== INIZIO PARSING {len(pdf_files)} MATCH REPORT GIORNATA 1 (2026/2027) ===")
    
    all_players = []
    all_teams = []
    
    for fname in pdf_files:
        fpath = os.path.join(REPORT_DIR, fname)
        try:
            with pdfplumber.open(fpath) as pdf:
                minfo = extract_match_info(pdf)
                print(f"-> Parsing: {minfo['match_title']} ({fname})...")
                
                p_stats = parse_player_stats(pdf, minfo)
                t_stats = parse_team_stats(pdf, minfo)
                
                all_players.extend(p_stats)
                all_teams.extend(t_stats)
        except Exception as e:
            print(f"  Errore su {fname}: {e}")
            
    df_players = pd.DataFrame(all_players)
    df_teams = pd.DataFrame(all_teams)
    
    players_csv = os.path.join(OUT_DIR, "seriea_2026_27_giornata_1_players.csv")
    players_json = os.path.join(OUT_DIR, "seriea_2026_27_giornata_1_players.json")
    teams_csv = os.path.join(OUT_DIR, "seriea_2026_27_giornata_1_teams.csv")
    teams_json = os.path.join(OUT_DIR, "seriea_2026_27_giornata_1_teams.json")
    
    df_players.to_csv(players_csv, index=False, encoding='utf-8')
    with open(players_json, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, ensure_ascii=False, indent=2)
        
    df_teams.to_csv(teams_csv, index=False, encoding='utf-8')
    with open(teams_json, 'w', encoding='utf-8') as f:
        json.dump(all_teams, f, ensure_ascii=False, indent=2)
        
    print(f"\n=======================================================")
    print(f"PARSING COMPLETATO CON SUCCESSO!")
    print(f"-> Totale Calciatori Estratti: {len(df_players)}")
    print(f"-> Totale Squadre Estratte: {len(df_teams)} (20 squadre)")
    print(f"-> File Giocatori CSV: {players_csv}")
    print(f"-> File Squadre CSV: {teams_csv}")
    print(f"=======================================================")

if __name__ == "__main__":
    process_all_match_reports()
