import os
import sys
import re
import json
import pdfplumber
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "raw", "match report 26-27")
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

        return match_info, players

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
    
    # 1. Trova tutti i PDF presenti nella cartella
    pdf_files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf')])
    print(f"Trovati {len(pdf_files)} file PDF in '{REPORTS_DIR}'.")

    parsed_matches = []
    parsed_players = []

    for fname in pdf_files:
        pdf_path = os.path.join(REPORTS_DIR, fname)
        print(f"  Elaborazione: {fname}...")
        try:
            m_info, p_list = parse_pdf_match_report(pdf_path)
            parsed_matches.append(m_info)
            parsed_players.extend(p_list)
            print(f"    ✓ {m_info['match_title']} (G{m_info['giornata']}) -> {len(p_list)} calciatori estratti.")
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

    # 3. Mantieni G2 dai dati storici (riparando i portieri)
    g2_matches = [m for m in existing_matches if m.get('giornata') == 2]
    g2_players_df = pd.DataFrame()
    if not existing_df.empty and 'giornata' in existing_df.columns:
        g2_players_raw = existing_df[existing_df['giornata'] == 2]
        if not g2_players_raw.empty:
            g2_players_df = fix_g2_goalkeepers(g2_players_raw)
            print(f"  ✓ Preservate e riparate {len(g2_players_df)} righe della Giornata 2 ({len(g2_matches)} partite).")

    # 4. Unisci le partite evitando duplicati per filename / match_title + giornata
    final_matches = []
    seen_match_keys = set()

    for m in parsed_matches:
        key = (m['match_title'], m['giornata'])
        if key not in seen_match_keys:
            final_matches.append(m)
            seen_match_keys.add(key)

    for m in g2_matches:
        key = (m['match_title'], m['giornata'])
        if key not in seen_match_keys:
            final_matches.append(m)
            seen_match_keys.add(key)

    # Ordina per giornata e partita
    final_matches.sort(key=lambda x: (x.get('giornata', 1), x.get('match_title', '')))

    # 5. Unisci il DataFrame dei giocatori
    df_new_parsed = pd.DataFrame(parsed_players)
    if not g2_players_df.empty:
        df_combined = pd.concat([df_new_parsed, g2_players_df], ignore_index=True)
    else:
        df_combined = df_new_parsed

    # Rimuovi eventuali duplicati esatti per (match_name, team, shirt_num, player_name, giornata)
    df_combined.drop_duplicates(subset=['match_name', 'team', 'shirt_num', 'player_name', 'giornata'], inplace=True)
    df_combined.sort_values(by=['giornata', 'match_name', 'team', 'role_gk', 'shirt_num'], ascending=[True, True, True, False, True], inplace=True)

    # 6. Salva MATCHES_JSON e PLAYERS_CSV
    with open(MATCHES_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_matches, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Salvato {MATCHES_JSON} ({len(final_matches)} partite totali).")

    df_combined.to_csv(PLAYERS_CSV, index=False, encoding='utf-8')
    print(f"✓ Salvato {PLAYERS_CSV} ({len(df_combined)} righe prestazione totali).")

    # Statistiche di riepilogo
    g_counts = df_combined['giornata'].value_counts().to_dict()
    print(f"Riepilogo presenze per giornata: {g_counts}")
    gk_count = len(df_combined[df_combined['role_gk'] == True])
    print(f"Portieri totali a referto: {gk_count} (validati)")

    return final_matches, df_combined

if __name__ == '__main__':
    sync_all_match_reports()
