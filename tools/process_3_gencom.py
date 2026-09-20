import os
import re
import sys
import json
import pdfplumber
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(ROOT_DIR, "data", "raw", "match report 26-27", "3_GENCOM_MatchReport_IT.pdf")
MATCHES_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_matches_g1_g2.json")
PLAYERS_CSV = os.path.join(ROOT_DIR, "data", "raw", "match_reports_players_g1_g2.csv")

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

def process_3_gencom():
    print(f"Loading {PDF_PATH}...")
    with pdfplumber.open(PDF_PATH) as pdf:
        filename = os.path.basename(PDF_PATH)
        
        # Giornata extraction
        m_giornata = re.search(r'^(\d+)_', filename)
        giornata = int(m_giornata.group(1)) if m_giornata else 3
        
        # Match info
        p2 = pdf.pages[1] if len(pdf.pages) > 1 else pdf.pages[0]
        p2_text = p2.extract_text() or ""
        lines = [l.strip() for l in p2_text.split('\n') if l.strip()]
        
        match_title = "GENOA 1-4 COMO"
        home_team = "GENOA"
        away_team = "COMO"
        score_home = 1
        score_away = 4
        
        for line in lines[:10]:
            m = re.search(r'([A-Za-z\s]+?)\s+(\d+)\s*[-–]\s*(\d+)\s+([A-Za-z\s]+)', line)
            if m and not 'SERIE A' in line:
                home_team = m.group(1).strip().upper()
                score_home = int(m.group(2))
                score_away = int(m.group(3))
                away_team = m.group(4).strip().upper()
                match_title = f"{home_team} {score_home}-{score_away} {away_team}"
                break
                
        moduli = re.findall(r'\b(\d-\d-\d(?:-\d)?)\b', p2_text)
        
        match_entry = {
            'filename': filename,
            'giornata': giornata,
            'match_title': match_title,
            'home_team': home_team,
            'away_team': away_team,
            'score_home': score_home,
            'score_away': score_away,
            'moduli': moduli
        }
        print("Extracted match entry:", match_entry)
        
        # Page 5 player stats
        p5 = find_page_by_keyword(pdf, "STATISTICHE GIOCATORE")
        tables = p5.extract_tables() if p5 else []
        
        team_tables = [
            (home_team, away_team, True, tables[1]),
            (away_team, home_team, False, tables[2])
        ]
        
        players = []
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
                    gs = safe_int(row[3]) if len(row) > 3 else 0
                    pa = safe_int(row[5]) if len(row) > 5 else 0
                    re_v = safe_int(row[7]) if len(row) > 7 else 0
                    amm = safe_int(row[9]) if len(row) > 9 else 0
                    dam = safe_int(row[10]) if len(row) > 10 else 0
                    esp = safe_int(row[11]) if len(row) > 11 else 0
                    
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
                        'ball_recoveries': safe_int(row[8]) if len(row) > 8 else 0,
                        'fouls_drawn': 0,
                        'fouls_committed': 0,
                        'yellow_cards': amm,
                        'double_yellows': dam,
                        'red_cards': esp,
                        'goals_conceded': gs,
                        'saves': pa,
                        'clean_sheet': 1 if gs == 0 and mins >= 60 else 0
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
                        'clean_sheet': 0
                    })
                    
        print(f"Extracted {len(players)} players.")
        
        # Update MATCHES_JSON
        if os.path.exists(MATCHES_JSON):
            with open(MATCHES_JSON, 'r', encoding='utf-8') as f:
                all_matches = json.load(f)
        else:
            all_matches = []
            
        # Check if already present
        exists_match = any(m.get('filename') == filename for m in all_matches)
        if not exists_match:
            all_matches.append(match_entry)
            with open(MATCHES_JSON, 'w', encoding='utf-8') as f:
                json.dump(all_matches, f, indent=2, ensure_ascii=False)
            print(f"Updated {MATCHES_JSON} (total matches: {len(all_matches)}).")
        else:
            print(f"Match {filename} already in {MATCHES_JSON}.")
            
        # Update PLAYERS_CSV
        if os.path.exists(PLAYERS_CSV):
            df_old = pd.read_csv(PLAYERS_CSV)
            # Remove any existing rows for this match to avoid duplicate
            df_filtered = df_old[~((df_old['match_name'] == match_title) & (df_old['giornata'] == giornata))]
            df_new = pd.concat([df_filtered, pd.DataFrame(players)], ignore_index=True)
        else:
            df_new = pd.DataFrame(players)
            
        df_new.to_csv(PLAYERS_CSV, index=False, encoding='utf-8')
        print(f"Updated {PLAYERS_CSV} (total player rows: {len(df_new)}).")

if __name__ == '__main__':
    process_3_gencom()
