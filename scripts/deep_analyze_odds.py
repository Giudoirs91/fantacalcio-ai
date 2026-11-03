import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Carica giocatori e statistiche squadra
with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

with open('data/raw/fotmob_team_stats_2026_27.json', 'r', encoding='utf-8') as f:
    teams_stats = json.load(f)

# Helper lookup giocatori per squadra
players_by_team = {}
for p in players:
    sq = p.get('squadra')
    if sq not in players_by_team:
        players_by_team[sq] = []
    players_by_team[sq].append(p)

def get_match_odds(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    event_info = d.get('avvenimentoFe', {})
    desc_event = event_info.get('descrizione', 'Sconosciuto')
    
    scommesse = d.get('scommessaMap', {})
    info_map = d.get('infoAggiuntivaMap', {})
    
    extracted = []
    for s_id, s_obj in scommesse.items():
        s_desc = s_obj.get('descrizione', '')
        for k_data in s_obj.get('infoAggiuntivaKeyDataList', []):
            info_key = k_data.get('key')
            info_item = info_map.get(info_key)
            if not info_item:
                continue
            sub_desc = info_item.get('descrizione', '')
            soglia = info_item.get('soglia', '')
            for esito in info_item.get('esitoList', []):
                e_desc = esito.get('descrizione', '')
                q = (esito.get('quota') or 0) / 100.0
                stato = esito.get('stato')
                if stato == 1 and q > 1.0: # attivo
                    extracted.append({
                        'scommessa': s_desc,
                        'sub_desc': sub_desc,
                        'soglia': soglia,
                        'esito': e_desc,
                        'quota': q
                    })
    return desc_event, extracted

for match_file, home, away in [
    ('data/raw/odds/sass-lazio.json', 'Sassuolo', 'Lazio'),
    ('data/raw/odds/roma-cagl.json', 'Roma', 'Cagliari')
]:
    event_name, odds = get_match_odds(match_file)
    print(f"\n=======================================================")
    print(f"ANALISI COMPLETA: {event_name}")
    print(f"=======================================================")
    
    # Stampa stats squadre
    print(f"\n--- METRICHE SQUADRE (G1-G8) ---")
    h_stat = teams_stats.get(home, {})
    a_stat = teams_stats.get(away, {})
    print(f"{home}:")
    print(f"  xG: {h_stat.get('xg_team')} (rank {h_stat.get('xg_team_rank')}) | xGA: {h_stat.get('xga_team')} (rank {h_stat.get('xga_team_rank')})")
    print(f"  Gol Subiti/match: {h_stat.get('goals_conceded_match')} | Clean Sheets: {h_stat.get('clean_sheets')}")
    print(f"  Big Chances create: {h_stat.get('big_chances')} | Touches opp box: {h_stat.get('touches_opp_box')}")
    print(f"  Attacco Tier: {h_stat.get('attacco_label')} | Difesa Tier: {h_stat.get('difesa_label')}")
    
    print(f"{away}:")
    print(f"  xG: {a_stat.get('xg_team')} (rank {a_stat.get('xg_team_rank')}) | xGA: {a_stat.get('xga_team')} (rank {a_stat.get('xga_team_rank')})")
    print(f"  Gol Subiti/match: {a_stat.get('goals_conceded_match')} | Clean Sheets: {a_stat.get('clean_sheets')}")
    print(f"  Big Chances create: {a_stat.get('big_chances')} | Touches opp box: {a_stat.get('touches_opp_box')}")
    print(f"  Attacco Tier: {a_stat.get('attacco_label')} | Difesa Tier: {a_stat.get('difesa_label')}")

    # Cerca mercati chiave:
    print(f"\n--- QUOTE PRINCIPALI MERCATO ---")
    for o in odds:
        s = o['scommessa'].upper()
        sub = o['sub_desc'].upper()
        e = o['esito'].upper()
        # Esito finale 1X2
        if s in ['ESITO FINALE 1X2', '1X2 FINALE', '1X2']:
            print(f"  [1X2] {o['esito']} @ {o['quota']:.2f}")
        elif 'DOPPIA CHANCE' in s and '1X2' not in s:
            if o['quota'] < 3.0:
                print(f"  [DC] {o['esito']} @ {o['quota']:.2f}")
        elif s == 'UNDER / OVER' or s == 'U/O' or 'UNDER/OVER 2.5' in s or ('UNDER' in s and '2.5' in sub):
            if '2.5' in sub or o['soglia'] == '2.5':
                print(f"  [U/O 2.5] {o['esito']} @ {o['quota']:.2f}")
        elif s in ['GOAL / NO GOAL', 'GOAL/NOGOAL', 'GOAL/NO GOAL']:
            print(f"  [GG/NG] {o['esito']} @ {o['quota']:.2f}")
            
    # Cerca Tiri in porta e DUO
    print(f"\n--- QUOTE TIRI E TIRI IN PORTA (DUO / SPECIALI / SQUADRA) ---")
    for o in odds:
        s = o['scommessa'].upper()
        sub = o['sub_desc'].upper()
        e = o['esito'].upper()
        if 'TIR' in s or 'TIR' in sub or 'DUO' in s or 'DUO' in sub:
            # Stampa le più interessanti (soglia ragionevole)
            if any(term in s or term in sub for term in ['PORTA', 'DUO', 'TIRI TOTALI']):
                if o['quota'] <= 3.5:
                    print(f"  [{o['scommessa']} - {o['sub_desc']}] {o['esito']} @ {o['quota']:.2f}")

    # Cerca Marcatori principali
    print(f"\n--- MARCATORI ---")
    for o in odds:
        s = o['scommessa'].upper()
        sub = o['sub_desc'].upper()
        e = o['esito'].upper()
        if 'MARCATORE' in s and 'TEMPO' not in s and '1°' not in s and 'DUO' not in s:
            if o['quota'] <= 4.5:
                print(f"  [MARCATORE SI] {o['esito']} @ {o['quota']:.2f}")
