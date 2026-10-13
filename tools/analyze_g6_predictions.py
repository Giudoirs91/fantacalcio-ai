import os
import sys
import re
import json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT_DIR, "data", "raw", "match_reports_players_g1_g2.csv")
MASTER_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
TEAM_STATS_PATH = os.path.join(ROOT_DIR, "data", "raw", "fotmob_team_stats_2026_27.json")

def main():
    df = pd.read_csv(CSV_PATH)
    g6_df = df[df['giornata'] == 6]

    with open(MASTER_PATH, 'r', encoding='utf-8') as f:
        players = json.load(f)

    with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
        calendar = json.load(f)

    with open(TEAM_STATS_PATH, 'r', encoding='utf-8') as f:
        team_stats = json.load(f)

    print(f"=== ANALISI GIORNATA 6: {len(g6_df['match_name'].unique())} PARTITE CONCLUSE ===")
    
    # 1. Eventi salienti dell'ultima partita aggiunta
    new_matches = ['TORINO 2-1 UDINESE']
    print("\n" + "="*60)
    print("DETTAGLIO NUOVA PARTITA AGGIUNTA (TORINO - UDINESE):")
    print("="*60)
    
    for m in new_matches:
        sub = g6_df[g6_df['match_name'] == m]
        if sub.empty:
            print(f"Partita {m} non trovata.")
            continue
        print(f"\n>>> {m} <<<")
        # Marcatori
        scorers = sub[sub['goals'] > 0]
        for _, r in scorers.iterrows():
            print(f"  ⚽ GOL: {r['player_name']} ({r['team']}) - Minuti: {r['minutes']}' (Titolare: {bool(r['is_starter'])})")
        # Assist
        assisters = sub[sub['assists'] > 0]
        for _, r in assisters.iterrows():
            print(f"  🅰️ ASSIST: {r['player_name']} ({r['team']}) - Minuti: {r['minutes']}' (Titolare: {bool(r['is_starter'])})")
        # Sanzioni
        cards = sub[(sub['yellow_cards'] > 0) | (sub['red_cards'] > 0)]
        for _, r in cards.iterrows():
            c_str = []
            if r['yellow_cards'] > 0: c_str.append(f"{int(r['yellow_cards'])} Giallo/i")
            if r['red_cards'] > 0: c_str.append("ROSSO DIRETTO")
            print(f"  🟨/🟥 CARTELLINO: {r['player_name']} ({r['team']}) - {', '.join(c_str)}")
        # Top performance per tiri / key passes
        impact = sub[(sub['total_shots'] >= 3) | (sub['key_passes'] >= 3)]
        for _, r in impact.iterrows():
            print(f"  ⚡ PERICOLOSITÀ: {r['player_name']} ({r['team']}) - Tiri: {r['total_shots']}, Key Pass: {r['key_passes']}")

    # 2. Verifica Predittiva dell'Algoritmo sui Consigliati G6
    # Importiamo calculate_advice_score da matchday_evaluator
    sys.path.append(os.path.join(ROOT_DIR, "src"))
    from matchday_evaluator import calculate_advice_score

    r6_data = next((r for r in calendar if r.get('giornata') == 6), None)
    fixture_map = {}
    if r6_data:
        for m in r6_data.get('matches', []):
            fixture_map[m['home']] = {'opp': m['away'], 'is_home': True, 'match': f"{m['home']} vs {m['away']}", 'round_num': 6}
            fixture_map[m['away']] = {'opp': m['home'], 'is_home': False, 'match': f"{m['home']} vs {m['away']}", 'round_num': 6}

    by_role = {'P': [], 'D': [], 'C': [], 'A': []}
    for p in players:
        team = p.get('team')
        m_info = fixture_map.get(team)
        if m_info:
            score = calculate_advice_score(p, m_info, team_stats)
            if score > 0:
                by_role[p.get('role', 'C')].append({
                    'score': score,
                    'player': p,
                    'match_info': m_info
                })

    print("\n" + "="*60)
    print("VERIFICA PREDIZIONI AI (TOP CONSIGLIATI) SULLE 10 PARTITE G6 (TURNO COMPLETO):")
    print("="*60)

    import unicodedata
    def clean_str(s):
        if not s: return ""
        norm = unicodedata.normalize('NFKD', str(s))
        ascii_str = norm.encode('ASCII', 'ignore').decode('utf-8')
        return re.sub(r'[^A-Z0-9\s]', '', ascii_str.upper()).strip()

    # Dizionario rapido calciatore -> stats G6 dal match report
    mr_dict = {}
    for _, r in g6_df.iterrows():
        c_name = clean_str(r['player_name'])
        t_clean = clean_str(r['team'])
        mr_dict[(t_clean, c_name)] = r.to_dict()
        # Per cognome
        tokens = c_name.split()
        if tokens:
            mr_dict[(t_clean, tokens[-1])] = r.to_dict()
            if len(tokens) > 1:
                mr_dict[(t_clean, tokens[0])] = r.to_dict()

    evaluation_results = []
    
    for role, items in by_role.items():
        items.sort(key=lambda x: -x['score'])
        top_candidates = items[:5] # Guardiamo i primi 5 per ogni ruolo
        print(f"\n--- RUOLO: {role} (Top 5 Consigliati Algoritmo) ---")
        for item in top_candidates:
            p = item['player']
            raw_name = p.get('name', '')
            c_name = clean_str(raw_name)
            team = p.get('team', '')
            t_clean = clean_str(team)
            score = item['score']
            m_info = item['match_info']

            # Match nel report
            matched_row = mr_dict.get((t_clean, c_name))
            if not matched_row:
                tokens = c_name.split()
                if tokens:
                    matched_row = mr_dict.get((t_clean, tokens[-1])) or mr_dict.get((t_clean, tokens[0]))

            if matched_row is None:
                # Cerca per match parziale nel team
                for (t_k, n_k), v in mr_dict.items():
                    if t_k == t_clean:
                        if n_k in c_name or c_name in n_k:
                            matched_row = v
                            break

            if matched_row:
                mins = matched_row.get('minutes', 0)
                tit = bool(matched_row.get('is_starter', 0))
                gl = matched_row.get('goals', 0)
                asst = matched_row.get('assists', 0)
                shots = matched_row.get('total_shots', 0)
                sot = matched_row.get('shots_on_target', 0)
                kp = matched_row.get('key_passes', 0)
                yc = matched_row.get('yellow_cards', 0)
                rc = matched_row.get('red_cards', 0)
                gc = matched_row.get('goals_conceded', 0)
                cs = matched_row.get('clean_sheet', 0)

                # Criterio Hit per Match Report (in attesa di voti ufficiali):
                # P: Clean sheet o max 1 gol subito con parate
                # D: Clean sheet, bonus, o almeno 70 min senza cartellini e con buona prestazione
                # C/A: Gol, Assist, o alta pericolosità (>=2 tiri in porta / >=2 key pass)
                is_hit = False
                diagnostic = ""
                
                if role == 'P':
                    if cs == 1:
                        is_hit = True
                        diagnostic = "HIT: Clean sheet mantenuto"
                    elif gc == 1:
                        is_hit = True
                        diagnostic = "HIT: Solo 1 gol subito, partita solida"
                    else:
                        is_hit = False
                        diagnostic = f"MISS: {gc} gol subiti"

                elif role == 'D':
                    if gl > 0 or asst > 0:
                        is_hit = True
                        diagnostic = f"HIT TOP: Bonus difensivo ({gl}G, {asst}A)"
                    elif cs == 1 and yc == 0 and rc == 0:
                        is_hit = True
                        diagnostic = "HIT: Clean sheet di reparto, zero malus"
                    elif rc > 0:
                        is_hit = False
                        diagnostic = "MISS: Espulsione (Malus grave)"
                    elif gc <= 1 and yc == 0:
                        is_hit = True
                        diagnostic = "HIT: Sufficienza piena (1 solo gol subito, pulito)"
                    else:
                        is_hit = False
                        diagnostic = f"MISS: {gc} gol subiti / prestazione sofferta"

                else: # C o A
                    if gl > 0 or asst > 0:
                        is_hit = True
                        diagnostic = f"HIT TOP: Decisivo ({gl}G, {asst}A)"
                    elif (sot >= 2 or kp >= 2) and rc == 0:
                        is_hit = True
                        diagnostic = f"HIT: Molto attivo/pericoloso ({sot} tiri porta, {kp} key pass)"
                    elif rc > 0:
                        is_hit = False
                        diagnostic = "MISS CRITICO: Espulsione diretta"
                    elif mins < 45:
                        is_hit = False
                        diagnostic = f"MISS TURNOVER: Solo {mins}' giocati"
                    else:
                        is_hit = False
                        diagnostic = f"MISS: Sterile offensivamente ({shots} tiri, {kp} key pass in {mins}')"

                status_icon = "✅" if is_hit else "❌"
                print(f"  {status_icon} {p.get('name')} ({team}) | Score AI: {score} | Min: {mins}' (Tit: {tit}) | {diagnostic}")
                evaluation_results.append({
                    'player': p.get('name'),
                    'role': role,
                    'team': team,
                    'score_ai': score,
                    'is_hit': is_hit,
                    'diagnostic': diagnostic
                })
            else:
                print(f"  ❓ {p.get('name')} ({team}) - Non sceso in campo / non a referto")
                evaluation_results.append({
                    'player': p.get('name'),
                    'role': role,
                    'team': team,
                    'score_ai': score,
                    'is_hit': False,
                    'diagnostic': "MISS: Non ha giocato (Tribuna o non impiegato)"
                })

    # Calcolo Hit Rate complessivo
    hits = [r for r in evaluation_results if r['is_hit']]
    misses = [r for r in evaluation_results if not r['is_hit']]
    total = len(evaluation_results)
    hr = (len(hits) / total * 100) if total > 0 else 0

    print("\n" + "="*60)
    print(f"RIASSUNTO ACCURATEZZA PREDITTIVA G6 (su {total} calciatori analizzati):")
    print(f"HIT RATE: {hr:.1f}% ({len(hits)} / {total})")
    print(f"MISSES: {len(misses)} / {total}")
    print("="*60)

    print("\n" + "="*60)
    print("TUTTI I CALCIATORI CON BONUS (GOL / ASSIST) IN G6 (10 PARTITE - TURNO COMPLETO):")
    print("="*60)
    bonus_df = g6_df[(g6_df['goals'] > 0) | (g6_df['assists'] > 0)].copy()
    bonus_df.sort_values(by=['goals', 'assists'], ascending=False, inplace=True)
    for _, r in bonus_df.iterrows():
        t = r['team']
        pname = r['player_name']
        g = int(r['goals'])
        a = int(r['assists'])
        mins = int(r['minutes'])
        tit = "Titolare" if r['is_starter'] else "Subentrato"
        print(f"  ⭐ {pname:<22} ({t:<9}) | Gol: {g} | Assist: {a} | Min: {mins}' ({tit})")


if __name__ == '__main__':
    main()
