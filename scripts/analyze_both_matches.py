import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Carica statistiche giocatori
with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Carica statistiche squadre
with open('data/raw/fotmob_team_stats_2026_27.json', 'r', encoding='utf-8') as f:
    teams_stats = json.load(f)

# Helper lookup
p_map = {}
for p in players:
    p_map[p['name'].lower()] = p

def analyze_match(json_path, home_team, away_team):
    with open(json_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    event_info = d.get('avvenimentoFe', {})
    event_desc = event_info.get('descrizione', f"{home_team} - {away_team}")
    
    print("\n" + "="*70)
    print(f"PARTITA: {event_desc.upper()}")
    print("="*70)
    
    # 1. Metriche statistiche squadre reali
    h_s = teams_stats.get(home_team, {})
    a_s = teams_stats.get(away_team, {})
    print(f"\n[DATI REALI SQUADRE G1-G8]")
    print(f"--- {home_team} ---")
    print(f"  xG: {h_s.get('xg_team')} (#{h_s.get('xg_team_rank')}) | xGA: {h_s.get('xga_team')} (#{h_s.get('xga_team_rank')})")
    print(f"  Gol Concessi/m: {h_s.get('goals_conceded_match')} | Clean sheets: {h_s.get('clean_sheets')}")
    print(f"  Big Chances: {h_s.get('big_chances')} | Touches opp box: {h_s.get('touches_opp_box')}")
    print(f"  Attacco: {h_s.get('attacco_label')} | Difesa: {h_s.get('difesa_label')}")
    
    print(f"--- {away_team} ---")
    print(f"  xG: {a_s.get('xg_team')} (#{a_s.get('xg_team_rank')}) | xGA: {a_s.get('xga_team')} (#{a_s.get('xga_team_rank')})")
    print(f"  Gol Concessi/m: {a_s.get('goals_conceded_match')} | Clean sheets: {a_s.get('clean_sheets')}")
    print(f"  Big Chances: {a_s.get('big_chances')} | Touches opp box: {a_s.get('touches_opp_box')}")
    print(f"  Attacco: {a_s.get('attacco_label')} | Difesa: {a_s.get('difesa_label')}")
    
    # 2. Estrai scommesse
    scommesse = d.get('scommessaMap', {})
    info_map = d.get('infoAggiuntivaMap', {})
    
    parsed_items = []
    for s_id, s_obj in scommesse.items():
        s_desc = s_obj.get('descrizione', '')
        for k_data in s_obj.get('infoAggiuntivaKeyDataList', []):
            info_key = k_data.get('key')
            info_item = info_map.get(info_key)
            if not info_item:
                continue
            item_desc = info_item.get('descrizione', '')
            soglia = info_item.get('soglia', '')
            for esito in info_item.get('esitoList', []):
                e_desc = esito.get('descrizione', '')
                q = (esito.get('quota') or 0) / 100.0
                if esito.get('stato') == 1 and q > 1.0:
                    parsed_items.append({
                        'scommessa': s_desc,
                        'item_desc': item_desc,
                        'soglia': soglia,
                        'esito': e_desc,
                        'quota': q
                    })
                    
    # Stampa Principali Mercati
    print(f"\n[PRINCIPALI MERCATI 1X2 - U/O - GG/NG]")
    for item in parsed_items:
        sc = item['scommessa'].upper()
        it = item['item_desc'].upper()
        es = item['esito'].upper()
        if sc in ['1X2 ESITO FINALE', 'ESITO FINALE 1X2', '1X2']:
            print(f"  1X2: {item['esito']} @ {item['quota']:.2f}")
        elif 'DOPPIA CHANCE' in sc and '1X2' not in sc:
            print(f"  Doppia Chance: {item['esito']} @ {item['quota']:.2f}")
        elif sc == 'UNDER / OVER' and ('2.5' in it or item['soglia'] == '2.5'):
            print(f"  Under/Over 2.5: {item['esito']} @ {item['quota']:.2f}")
        elif sc == 'UNDER / OVER' and ('1.5' in it or item['soglia'] == '1.5'):
            print(f"  Under/Over 1.5: {item['esito']} @ {item['quota']:.2f}")
        elif sc == 'UNDER / OVER' and ('3.5' in it or item['soglia'] == '3.5'):
            print(f"  Under/Over 3.5: {item['esito']} @ {item['quota']:.2f}")
        elif 'GOAL/NOGOAL' in sc or 'GOAL / NO GOAL' in sc:
            print(f"  Goal/NoGoal: {item['esito']} @ {item['quota']:.2f}")
        elif 'DRAW NO BET' in sc or 'RIMBORSO IN CASO DI PARITA' in sc:
            print(f"  Rimborso Parità (DNB): {item['esito']} @ {item['quota']:.2f}")

    # Tiri e Tiri in Porta Squadre
    print(f"\n[TIRI E TIRI IN PORTA SQUADRA]")
    for item in parsed_items:
        sc = item['scommessa'].upper()
        it = item['item_desc'].upper()
        if 'ENTRAMBE LE SQUADRE ALMENO' in sc and 'PORTA' in sc:
            print(f"  {item['item_desc']}: {item['esito']} @ {item['quota']:.2f}")
        elif 'TIRI IN PORTA' in sc and ('CASA' in sc or 'OSPITE' in sc or 'SQUADRA' in sc or '1T' in sc):
            if item['quota'] <= 3.20:
                print(f"  {item['scommessa']} - {item['item_desc']}: {item['esito']} @ {item['quota']:.2f}")
        elif 'TIRI TOTALI' in sc and ('CASA' in sc or 'OSPITE' in sc):
            if item['quota'] <= 2.50:
                print(f"  {item['scommessa']} - {item['item_desc']}: {item['esito']} @ {item['quota']:.2f}")

    # Giocatori: Tiri in porta e DUO Tiri
    print(f"\n[GIOCATORE TIRI IN PORTA & DUO]")
    for item in parsed_items:
        sc = item['scommessa'].upper()
        it = item['item_desc'].upper()
        if 'TIRI IN PORTA' in sc or 'TIRI IN PORTA' in it:
            if 'DUO' in sc or 'DUO' in it or 'GIOCATORE' in sc:
                if item['quota'] <= 3.50 and item['quota'] >= 1.25:
                    print(f"  {item['item_desc']} -> {item['esito']} @ {item['quota']:.2f}")

    # Falli e Cartellini
    print(f"\n[GIOCATORE FALLI & CARTELLINI]")
    for item in parsed_items:
        sc = item['scommessa'].upper()
        it = item['item_desc'].upper()
        if 'FALLI' in sc or 'FALLI' in it or 'CARTELLINO' in sc:
            if item['quota'] <= 3.50 and item['quota'] >= 1.30:
                print(f"  {item['scommessa']} | {item['item_desc']} -> {item['esito']} @ {item['quota']:.2f}")

    # Marcatori
    print(f"\n[MARCATORI / GOL O PALO]")
    for item in parsed_items:
        sc = item['scommessa'].upper()
        it = item['item_desc'].upper()
        if ('MARCATORE' in sc or 'GOL O PALO' in sc or 'GOL' in sc) and 'TEMPO' not in sc and '1°' not in sc:
            if 'DUO' in sc or 'SEGNA' in sc or 'MARCATORE' in sc:
                if item['quota'] <= 4.0 and item['quota'] >= 1.20:
                    print(f"  {item['item_desc']} -> {item['esito']} @ {item['quota']:.2f}")

analyze_match('data/raw/odds/sass-lazio.json', 'Sassuolo', 'Lazio')
analyze_match('data/raw/odds/roma-cagl.json', 'Roma', 'Cagliari')
