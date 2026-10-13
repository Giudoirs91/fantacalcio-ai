import os
import sys
import json
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
TACTICAL_DB_PATH = os.path.join(ROOT_DIR, "config", "tactical_db.json")
WHOSCORED_TEAMS_PATH = os.path.join(ROOT_DIR, "config", "whoscored_teams_2627.json")

def enrich_internal_and_tactical_metrics():
    print("=== [Scouting Importer] Calcolo metriche interne e arricchimento tattico ===")
    
    with open(MASTER_PLAYERS_PATH, 'r', encoding='utf-8') as f:
        master_players = json.load(f)
        
    # Carica WhoScored se presente
    whoscored_teams = {}
    if os.path.exists(WHOSCORED_TEAMS_PATH):
        with open(WHOSCORED_TEAMS_PATH, 'r', encoding='utf-8') as f:
            whoscored_teams = json.load(f)
            
    # Carica Tactical DB
    tactical_db = {}
    if os.path.exists(TACTICAL_DB_PATH):
        with open(TACTICAL_DB_PATH, 'r', encoding='utf-8') as f:
            tactical_db = json.load(f)
            
    # 1. Arricchisci Tactical DB con WhoScored
    for team, ws_data in whoscored_teams.items():
        if team in tactical_db:
            tactical_db[team]['whoscored_attack_sides'] = ws_data.get('attack_sides', {})
            tactical_db[team]['whoscored_action_zones'] = ws_data.get('action_zones', {})
            tactical_db[team]['whoscored_goal_situations'] = ws_data.get('goal_situations_pg', {})
            tactical_db[team]['whoscored_xg'] = ws_data.get('xg_non_penalty', {})
            
    with open(TACTICAL_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(tactical_db, f, indent=2, ensure_ascii=False)
    print("  ✓ Tactical DB aggiornato con le metriche WhoScored per le 20 squadre.")
    
    # 2. Calcola metriche derivate per ciascun giocatore
    enriched_count = 0
    for p in master_players:
        voti_list = p.get('voti_dettaglio_2627', [])
        if not voti_list:
            continue
            
        # A. Rolling Minutes (Ultime 3 giornate: G4, G5, G6)
        last_3_rounds = [4, 5, 6]
        rolling_mins = sum(v.get('minuti', 90) for v in voti_list if v.get('giornata') in last_3_rounds and v.get('voto') is not None)
        p['rolling_minutes_last3'] = rolling_mins
        
        # B. Split Prestazioni Casa vs Trasferta
        home_fvs = [v.get('fantavoto') for v in voti_list if v.get('is_home') is True and v.get('fantavoto') is not None]
        away_fvs = [v.get('fantavoto') for v in voti_list if v.get('is_home') is False and v.get('fantavoto') is not None]
        
        p['fm_casa_2627'] = round(float(np.mean(home_fvs)), 2) if home_fvs else None
        p['fm_trasferta_2627'] = round(float(np.mean(away_fvs)), 2) if away_fvs else None
        if p['fm_casa_2627'] is not None and p['fm_trasferta_2627'] is not None:
            p['delta_casa_trasferta'] = round(p['fm_casa_2627'] - p['fm_trasferta_2627'], 2)
        else:
            p['delta_casa_trasferta'] = 0.0
            
        # C. Fattore Subentro / Spaccapartita
        # Se ha almeno 1 presenza con bonus o voto alto partendo da subentrato
        sub_votes = [v for v in voti_list if v.get('is_starter') is False and v.get('fantavoto') is not None and v.get('fantavoto') >= 6.5]
        # D. Proxy SCA (Shot-Creating Actions) & Presenza in Area (Box Presence Index)
        # Sostituisce i dati mancanti di FBref combinando FotMob e Match Reports ufficiali
        chances = float(p.get('chances_created_2627') or 0)
        big_ch = float(p.get('big_chances_created_2627') or 0)
        dr = float(p.get('won_contest_2627') or 0)
        shots = float(p.get('total_scoring_att_2627') or (p.get('tiri_2627') or 0))
        sot = float(p.get('ontarget_scoring_att_2627') or (p.get('tiri_porta_2627') or 0))
        xg = float(p.get('xg_2627') or 0.0)
        poss_3rd = float(p.get('poss_won_att_3rd_2627') or 0)
        mins = float(p.get('minuti_2627') or (p.get('minuti_fotmob_2627') or 90))
        mins_90s = max(mins / 90.0, 0.5)

        # SCA Index: volume di azioni offensive che creano conclusioni per sé o per i compagni
        p['sca_index_2627'] = round(chances + (big_ch * 1.5) + (dr * 0.8), 1)
        p['sca90_index_2627'] = round(p['sca_index_2627'] / mins_90s, 2)

        # Box Presence Index (Tocchi in Area): volume tiri in area, pericolosità xG e recuperi avanzati
        p['box_presence_index_2627'] = round((shots * 1.5) + (sot * 1.0) + (xg * 2.0) + (poss_3rd * 1.2), 1)

        enriched_count += 1
        
    with open(MASTER_PLAYERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(master_players, f, indent=2, ensure_ascii=False)
        
    print(f"  ✓ Calcolate metriche interne (Rolling Mins, Split Casa/Trasferta, Spaccapartita, SCA/Box Index) per {enriched_count} calciatori!")

if __name__ == "__main__":
    enrich_internal_and_tactical_metrics()
