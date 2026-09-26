import os
import re
import json
import numpy as np
import pandas as pd

from .config_loader import (
    get_tactical_db, get_injuries_db, get_fragile_players, get_infortuni_2025_26,
    get_injuries_history_db, get_team_ratings, get_league_settings
)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from .player_matcher import clean_text, resolve_player, match_player_name
from .stats_processor import (
    load_quotazioni, load_voti_storici, load_fotmob_stats, load_fotmob_2026_27_stats, 
    load_fotmob_team_stats, safe_float, safe_int
)
from .match_reports_processor import load_and_aggregate_match_reports
from .voti_processor import load_voti_2026_27
from .valuation_engine import (
    calcola_impatto_infortunio, compute_continuous_ovr_and_price, 
    determine_advice_tag, assign_slots_and_fasce, calibrate_budget_prices,
    calculate_xfm
)
from .gk_engine import extract_gk_grid
from .ai_evaluator import save_predictions_snapshot, evaluate_predictions

def compute_substitute_pairings(processed_players, tactical_db, reports_csv):
    """
    Associa a ogni giocatore il suo sostituto naturale / compagno di staffetta e viceversa.
    Sfrutta 1) Tactical DB (ballottaggi & lineup), 2) Match Reports (sostituzioni effettive),
    3) Gerarchia Portieri (1° <-> 2° portiere), 4) Fallback di reparto per titolari rimasti scoperti.
    """
    from collections import defaultdict
    team_players = defaultdict(list)
    for p in processed_players:
        team_players[p['team']].append(p)
        
    sub_pairs_count = defaultdict(int)
    if reports_csv and os.path.exists(reports_csv):
        try:
            df_rep = pd.read_csv(reports_csv)
            for (g, m, t), grp in df_rep.groupby(['giornata', 'match_name', 'team']):
                starters_off = grp[(grp['is_starter'] == True) & (grp['minutes'] < grp['minutes'].max())]
                subs_on = grp[(grp['is_starter'] == False) & (grp['minutes'] > 0)]
                max_m = grp['minutes'].max()
                matched = set()
                for _, sub in subs_on.iterrows():
                    sub_m = sub['minutes']
                    for _, starter in starters_off.iterrows():
                        if starter['player_name'] in matched:
                            continue
                        if abs((starter['minutes'] + sub_m) - max_m) <= 1:
                            sub_pairs_count[(str(t).upper(), str(starter['player_name']).upper(), str(sub['player_name']).upper())] += 1
                            matched.add(starter['player_name'])
                            break
        except Exception as e:
            print(f"[Pipeline] Errore estrazione sostituzioni da report: {e}")

    pairings = {}

    for team_name, t_players in team_players.items():
        t_tac = tactical_db.get(team_name, {}) if tactical_db else {}
        ballottaggi = t_tac.get('ballottaggi', [])
        
        # 1. Portieri: 1° Portiere <-> 2° Portiere
        gks = [p for p in t_players if p['role'] == 'P']
        gks.sort(key=lambda x: (x.get('titolarita', 0), x.get('fvm', 0), x.get('ovr', 0)), reverse=True)
        if len(gks) >= 2:
            p1, p2 = gks[0], gks[1]
            pairings[p1['id']] = {
                'coppia_nome': p2['name'],
                'coppia_id': p2['id'],
                'coppia_ruolo': 'P',
                'coppia_tipo': 'RISERVA',
                'coppia_dettaglio': f"2° Portiere ({p2['name']})"
            }
            pairings[p2['id']] = {
                'coppia_nome': p1['name'],
                'coppia_id': p1['id'],
                'coppia_ruolo': 'P',
                'coppia_tipo': 'TITOLARE',
                'coppia_dettaglio': f"Vice di {p1['name']}"
            }
            if len(gks) >= 3:
                p3 = gks[2]
                pairings[p3['id']] = {
                    'coppia_nome': p1['name'],
                    'coppia_id': p1['id'],
                    'coppia_ruolo': 'P',
                    'coppia_tipo': 'TITOLARE',
                    'coppia_dettaglio': f"3° Portiere ({p1['name']})"
                }

        # 2. Ballottaggi espliciti da Tactical DB
        for b in ballottaggi:
            p_name = b.get('player', '')
            p_pct = b.get('pct', 50)
            vs_str = b.get('vs', '')
            
            p_obj = next((p for p in t_players if match_player_name(p['name'], p_name)), None)
            if not p_obj or p_obj['role'] == 'P':
                continue
                
            vs_matches = re.findall(r'([A-Za-z\s\.\'\-]+?)\s*\((\d+)%\)', vs_str)
            if vs_matches:
                for rival_name, rival_pct in vs_matches:
                    rival_name = rival_name.strip()
                    rival_pct = int(rival_pct)
                    
                    r_obj = next((p for p in t_players if match_player_name(p['name'], rival_name)), None)
                    if not r_obj or r_obj['role'] == 'P':
                        continue
                    
                    is_hybrid = (r_obj['role'] != p_obj['role'])
                    
                    tipo = 'BALLOTTAGGIO'
                    if p_pct >= 65:
                        tipo = 'TITOLARE'   # alta % = è lui il titolare
                    elif p_pct <= 35:
                        tipo = 'RISERVA'    # bassa % = è la riserva
                    
                    r_tipo = 'TITOLARE' if tipo == 'RISERVA' else ('RISERVA' if tipo == 'TITOLARE' else 'BALLOTTAGGIO')
                    
                    if is_hybrid:
                        det_p = f"Staffetta/Ballottaggio reale {p_pct}% vs {rival_pct}% ({r_obj['name']}). ⚠️ Asimmetria Classic: {p_obj['name']} è {p_obj['role']}, {r_obj['name']} è {r_obj['role']} (stessa corsia/zona in campo)"
                        det_r = f"Staffetta/Ballottaggio reale {rival_pct}% vs {p_pct}% ({p_obj['name']}). ⚠️ Asimmetria Classic: {r_obj['name']} è {r_obj['role']}, {p_obj['name']} è {p_obj['role']} (stessa corsia/zona in campo)"
                    else:
                        det_p = f"{p_pct}% vs {rival_pct}% ({r_obj['name']})"
                        det_r = f"{rival_pct}% vs {p_pct}% ({p_obj['name']})"
                    
                    if p_obj['id'] not in pairings:
                        pairings[p_obj['id']] = {
                            'coppia_nome': r_obj['name'],
                            'coppia_id': r_obj['id'],
                            'coppia_ruolo': r_obj['role'],
                            'coppia_tipo': tipo,
                            'coppia_dettaglio': det_p,
                            'coppia_ibrida': is_hybrid
                        }
                    
                    if r_obj['id'] not in pairings:
                        pairings[r_obj['id']] = {
                            'coppia_nome': p_obj['name'],
                            'coppia_id': p_obj['id'],
                            'coppia_ruolo': p_obj['role'],
                            'coppia_tipo': r_tipo,
                            'coppia_dettaglio': det_r,
                            'coppia_ibrida': is_hybrid
                        }
                    break

        # 3. Lineup esplicite da Tactical DB (per ruoli/corsie con sub_name indicato)
        lineup_slots = t_tac.get('lineup', [])
        for slot in lineup_slots:
            st_name = slot.get('name')
            sb_name = slot.get('sub_name')
            pos_label = slot.get('pos_label') or slot.get('pos') or 'Corsia'
            if not st_name or not sb_name:
                continue
            st_obj = next((p for p in t_players if match_player_name(p['name'], st_name)), None)
            sb_obj = next((p for p in t_players if match_player_name(p['name'], sb_name)), None)
            if not st_obj or not sb_obj or st_obj['role'] == 'P' or sb_obj['role'] == 'P':
                continue
            
            # Assegna al titolare se non ha ancora una coppia assegnata
            if st_obj['id'] not in pairings:
                is_hybrid = (st_obj['role'] != sb_obj['role'])
                if is_hybrid:
                    det_st = f"Alternativa tattica: {sb_obj['name']} ({pos_label}). ⚠️ Ruoli Classic differenti: {st_obj['role']} vs {sb_obj['role']}"
                else:
                    det_st = f"Alternativa diretta: {sb_obj['name']} ({pos_label})"

                pairings[st_obj['id']] = {
                    'coppia_nome': sb_obj['name'],
                    'coppia_id': sb_obj['id'],
                    'coppia_ruolo': sb_obj['role'],
                    'coppia_tipo': 'TITOLARE',
                    'coppia_dettaglio': det_st,
                    'coppia_ibrida': is_hybrid
                }

                # La riserva può coprire più titolari (es. Carlos Augusto per Bastoni e Dimarco, Soulé per Dybala e Mora)
                if sb_obj['id'] not in pairings:
                    det_sb = f"Subentra a {st_obj['name']} ({pos_label})"
                    if is_hybrid:
                        det_sb += f". ⚠️ Ruoli Classic differenti: {sb_obj['role']} vs {st_obj['role']}"
                    pairings[sb_obj['id']] = {
                        'coppia_nome': st_obj['name'],
                        'coppia_id': st_obj['id'],
                        'coppia_ruolo': st_obj['role'],
                        'coppia_tipo': 'RISERVA',
                        'coppia_dettaglio': det_sb,
                        'coppia_ibrida': is_hybrid
                    }
                else:
                    prev = pairings[sb_obj['id']]
                    if st_obj['name'] not in prev['coppia_nome']:
                        prev['coppia_nome'] = f"{prev['coppia_nome']} / {st_obj['name']}"
                        prev['coppia_dettaglio'] = f"Jolly di reparto: copre sia {prev['coppia_nome']}"

        # 4. Match Reports: Staffette reali dai cambi effettivi
        team_upper = team_name.upper()
        for (t_up, st_name, sb_name), count in sorted(sub_pairs_count.items(), key=lambda x: x[1], reverse=True):
            if t_up != team_upper and team_upper not in t_up and t_up not in team_upper:
                continue
            st_obj = next((p for p in t_players if match_player_name(p['name'], st_name)), None)
            sb_obj = next((p for p in t_players if match_player_name(p['name'], sb_name)), None)
            if not st_obj or not sb_obj or st_obj['role'] == 'P' or sb_obj['role'] == 'P':
                continue
            
            if st_obj['id'] not in pairings and sb_obj['id'] not in pairings:
                is_hybrid = (st_obj['role'] != sb_obj['role'])
                if is_hybrid:
                    st_mantra = set((st_obj.get('mantra') or '').split(';'))
                    sb_mantra = set((sb_obj.get('mantra') or '').split(';'))
                    # Solo se condividono almeno una posizione al Mantra (es. entrambi E, entrambi W)
                    if not st_mantra.intersection(sb_mantra):
                        continue
                    det_st = f"Staffetta ({count} cambi). ⚠️ Ruoli Classic differenti: {st_obj['role']} vs {sb_obj['role']} (stessa posizione in campo)"
                    det_sb = f"Subentra a {st_obj['name']} ({count} cambi). ⚠️ Ruoli Classic differenti: {sb_obj['role']} vs {st_obj['role']}"
                else:
                    det_st = f"Staffetta ({count} cambi)"
                    det_sb = f"Subentra a {st_obj['name']}"

                pairings[st_obj['id']] = {
                    'coppia_nome': sb_obj['name'],
                    'coppia_id': sb_obj['id'],
                    'coppia_ruolo': sb_obj['role'],
                    'coppia_tipo': 'STAFFETTA',
                    'coppia_dettaglio': det_st,
                    'coppia_ibrida': is_hybrid
                }
                pairings[sb_obj['id']] = {
                    'coppia_nome': st_obj['name'],
                    'coppia_id': st_obj['id'],
                    'coppia_ruolo': st_obj['role'],
                    'coppia_tipo': 'TITOLARE',
                    'coppia_dettaglio': det_sb,
                    'coppia_ibrida': is_hybrid
                }

        # 5. Fallback per titolari dell'11 ancora senza sostituto: assegna riserva compatibile
        starters_unmapped = [p for p in t_players if p.get('is_in_11') and p['id'] not in pairings and p['role'] != 'P']
        bench_candidates = [p for p in t_players if not p.get('is_in_11') and p['role'] != 'P']
        bench_candidates.sort(key=lambda x: (x.get('fvm', 0), x.get('ovr', 0)), reverse=True)
        
        used_bench = set(p['coppia_id'] for p in pairings.values() if p.get('coppia_id'))
        for st in starters_unmapped:
            st_mantra = set((st.get('mantra') or '').split(';'))
            best_candidate = None
            
            # Priorità 1: stesso ruolo Fantacalcio + affinità Mantra esatta (es. Pc per Pc, Dc per Dc, E per E)
            for b in bench_candidates:
                if b['role'] == st['role'] and b['id'] not in used_bench:
                    b_mantra = set((b.get('mantra') or '').split(';'))
                    if st_mantra.intersection(b_mantra):
                        best_candidate = b
                        break
            
            # Priorità 2: stesso ruolo Classic MA compatibile a livello tattico
            # NON accoppiare MAI un centrale puro (Dc senza E) con un esterno a tutta fascia (E senza Dc)
            if not best_candidate:
                is_st_cb = ('Dc' in st_mantra or 'B' in st_mantra) and ('E' not in st_mantra and 'W' not in st_mantra)
                is_st_wing = ('E' in st_mantra or 'W' in st_mantra) and ('Dc' not in st_mantra)
                
                for b in bench_candidates:
                    if b['role'] == st['role'] and b['id'] not in used_bench:
                        b_mantra = set((b.get('mantra') or '').split(';'))
                        is_b_cb = ('Dc' in b_mantra or 'B' in b_mantra) and ('E' not in b_mantra and 'W' not in b_mantra)
                        is_b_wing = ('E' in b_mantra or 'W' in b_mantra) and ('Dc' not in b_mantra)
                        
                        # Incompatibilità netta
                        if is_st_cb and is_b_wing:
                            continue
                        if is_st_wing and is_b_cb:
                            continue
                            
                        best_candidate = b
                        break
            
            # Priorità 3: se tutte le riserve sono già abbinate, condividi la migliore riserva compatibile di reparto
            if not best_candidate:
                for b in bench_candidates:
                    if b['role'] == st['role']:
                        b_mantra = set((b.get('mantra') or '').split(';'))
                        if st_mantra.intersection(b_mantra):
                            best_candidate = b
                            break

            if best_candidate:
                used_bench.add(best_candidate['id'])
                pairings[st['id']] = {
                    'coppia_nome': best_candidate['name'],
                    'coppia_id': best_candidate['id'],
                    'coppia_ruolo': best_candidate['role'],
                    'coppia_tipo': 'RISERVA',
                    'coppia_dettaglio': f"Alternativa di reparto ({best_candidate['name']})",
                    'coppia_ibrida': False
                }
                if best_candidate['id'] not in pairings:
                    pairings[best_candidate['id']] = {
                        'coppia_nome': st['name'],
                        'coppia_id': st['id'],
                        'coppia_ruolo': st['role'],
                        'coppia_tipo': 'TITOLARE',
                        'coppia_dettaglio': f"Copertura di {st['name']}",
                        'coppia_ibrida': False
                    }

    # Assegna i campi a ogni giocatore
    for p in processed_players:
        pair = pairings.get(p['id'])
        if pair:
            p['coppia_nome'] = pair['coppia_nome']
            p['coppia_id'] = pair['coppia_id']
            p['coppia_ruolo'] = pair['coppia_ruolo']
            p['coppia_tipo'] = pair['coppia_tipo']
            p['coppia_dettaglio'] = pair['coppia_dettaglio']
            p['coppia_ibrida'] = bool(pair.get('coppia_ibrida') or (pair['coppia_ruolo'] != p['role']))
        else:
            p['coppia_nome'] = '-'
            p['coppia_id'] = None
            p['coppia_ruolo'] = '-'
            p['coppia_tipo'] = '-'
            p['coppia_dettaglio'] = 'Nessuna alternativa diretta'
            p['coppia_ibrida'] = False

    print(f"-> Mappatura Coppie/Sostituti completata: {len(pairings)}/{len(processed_players)} calciatori associati.")
    return processed_players

def compute_predictive_titolarita(
    clean_pname,
    team,
    rep_data,
    n_team_matches,
    is_injured,
    infortunio_info,
    titolarita_tactical,
    titolarita_storica,
    is_in_11,
    is_new_arrival,
    fvm
):
    """
    Calcolo quantitativo predittivo della titolarità (0.0 - 1.0) suddiviso in 3 metriche ponderate:
    - Ultime 3 giornate: peso 50% (gerarchia attuale dell'allenatore)
    - Giornate 4-8 all'indietro: peso 35% (continuità di medio periodo nella stagione)
    - Resto della stagione / Storico: peso 15% (àncora statistica anti-rumore)
    
    Protezione assoluta per infortuni (esclusi dal demerito tecnico) e zero division safety.
    """
    n_matches = max(1, int(n_team_matches or 5))
    
    # Se il giocatore fa parte dell'11 titolare del club, prior può riflettere lo storico
    # Se NON fa parte dell'11 titolare (es. riserva Giovane nel Napoli con FVM 7), prior NON può eccedere titolarita_tactical
    if is_in_11:
        prior = titolarita_storica if (titolarita_storica and titolarita_storica > 0 and titolarita_storica <= 1.0) else titolarita_tactical
    else:
        prior = min(titolarita_tactical, titolarita_storica if (titolarita_storica and titolarita_storica > 0) else titolarita_tactical)
    prior = min(1.0, max(0.0, float(prior or 0.35)))

    # Caso 1: Giocatore infortunato senza presenze 26/27 (es. Thuram K., Konè I., Buongiorno, Walukiewicz)
    has_rep = bool(rep_data and rep_data.get('presenze_2627', 0) > 0)
    if is_injured and not has_rep:
        rientro = infortunio_info.get("rientro", "Infortunato") if infortunio_info else "Infortunato"
        severity = infortunio_info.get("severity", "") if infortunio_info else ""
        tipo_stop = infortunio_info.get("tipo_stop", "") if infortunio_info else ""
        motivo = infortunio_info.get("motivo", "") if infortunio_info else ""
        
        # Rilevamento Lunga Degenza (Evitare) / Stop grave oltre 45 giorni o nel 2027
        is_long_term = (
            severity == 'red' or 
            'LUNGA DEGENZA' in tipo_stop.upper() or 
            '2027' in rientro or 
            'crociato' in motivo.lower() or 
            'frattura' in motivo.lower()
        )
        
        if is_long_term:
            # Per il fantacalcio la disponibilità immediata a breve termine è 0%!
            tit_teorica = int(round((titolarita_tactical if is_in_11 else prior) * 100))
            desc = f"Indisponibile (Lunga degenza: {rientro})"
            dettaglio = f"Indisponibile per grave infortunio (rientro previsto: {rientro}). Titolarità tecnica teorica a regime: {tit_teorica}%"
            return 0.0, desc, 0, 0, tit_teorica, dettaglio
        else:
            # Infortunio temporaneo a breve termine (rientro imminente, es. Buongiorno o Walukiewicz)
            if is_in_11:
                tit_val = max(titolarita_tactical, 0.85)
            else:
                tit_val = min(titolarita_tactical, 0.35)
            tit_val = min(1.0, max(0.0, round(tit_val, 2)))
            pct = int(round(tit_val * 100))
            status_label = "Titolare" if is_in_11 else "Riserva"
            desc = f"{status_label} (Ai box - rientro {rientro})"
            dettaglio = f"Titolarità a regime: {pct}% (Temporaneamente indisponibile per infortunio - rientro: {rientro})"
            return tit_val, desc, pct, pct, int(round(prior * 100)), dettaglio

    # Caso 2: Nuovo acquisto annunciato a fine mercato o svincolato
    if is_new_arrival:
        tit_val = min(1.0, max(0.0, round(titolarita_tactical, 2)))
        pct = int(round(tit_val * 100))
        desc = f"Nuovo Acquisto ({pct}% Tit)"
        dettaglio = f"Nuovo Acquisto: stimato da gerarchia tattica al {pct}%"
        return tit_val, desc, pct, pct, int(round(prior * 100)), dettaglio

    # Caso 3: Presenza nei report di gara 2026/27
    if rep_data:
        starts = int(rep_data.get('titolarita_count_2627', 0))
        presenze = int(rep_data.get('presenze_2627', 0))
        subs = max(0, presenze - starts)
        history = rep_data.get('history_by_round', {})

        # Titolarissimo assoluto 100% (es. 5 su 5 dall'inizio)
        if starts >= n_matches:
            tit_val = 1.0
            desc = f"{starts}/{n_matches} Titolare (100%)"
            dettaglio = (
                f"Titolarità Assoluta: 100% ({starts}/{n_matches} dal 1' minuto)\n"
                f"• Ultime 3 giornate: 100% (peso 50%)\n"
                f"• Giornate 4-8: 100% (peso 35%)\n"
                f"• Storico/Àncora: {int(round(prior*100))}% (peso 15%)"
            )
            return 1.0, desc, 100, 100, int(round(prior * 100)), dettaglio

        # Suddivisione rigorosa nelle 3 Fasce Temporali:
        # Fascia 1: Ultime 3 giornate (es. se n_matches=5, sono G3, G4, G5)
        last_3_rounds = [g for g in range(max(1, n_matches - 2), n_matches + 1)]
        # Fascia 2: Giornate 4-8 all'indietro (es. G1 e G2)
        mid_rounds = [g for g in range(max(1, n_matches - 7), max(1, n_matches - 2))]
        # Fascia 3: Storico 2025/26 / Prior Tattico

        def eval_round(g):
            if g in history:
                h = history[g]
                if h.get('is_starter', False):
                    return 1.0
                mins = int(h.get('minutes', 0))
                return 0.60 if mins >= 25 else (0.35 if mins > 0 else 0.0)
            else:
                if is_injured and g >= max(1, n_matches - 1):
                    return None # Non penalizzare se assente per infortunio
                return 0.0

        # Punteggio Blocco 1: Ultime 3 giornate
        v1_list = [eval_round(g) for g in last_3_rounds]
        v1_valid = [v for v in v1_list if v is not None]
        t_ultime3 = (sum(v1_valid) / max(1, len(v1_valid))) if v1_valid else prior

        # Punteggio Blocco 2: Giornate 4-8 all'indietro
        v2_list = [eval_round(g) for g in mid_rounds]
        v2_valid = [v for v in v2_list if v is not None]
        t_mid = (sum(v2_valid) / max(1, len(v2_valid))) if v2_valid else prior

        # Punteggio Blocco 3: Storico / Àncora
        t_storico = prior

        # Ponderazione quantitativa esatta:
        # Ultime 3 giornate: 50%
        # Giornate 4-8: 35%
        # Resto/Storico: 15%
        if len(mid_rounds) > 0:
            w_u3, w_mid, w_hist = 0.50, 0.35, 0.15
        else:
            w_u3, w_mid, w_hist = 0.65, 0.00, 0.35

        tit_raw = (w_u3 * t_ultime3) + (w_mid * t_mid) + (w_hist * t_storico)

        # Regola di salvaguardia per riserve senza presenze e non infortunate
        if starts == 0 and subs == 0 and not is_injured:
            desc = f"0/{n_matches} Presenze (Riserva)"
            dettaglio = f"Titolarità: 0% (0 presenze su {n_matches} partite disputate)"
            return 0.0, desc, 0, 0, int(round(prior * 100)), dettaglio

        if starts >= 4 and is_in_11:
            tit_raw = max(tit_raw, 0.82)

        tit_val = min(1.0, max(0.0, round(tit_raw, 2)))
        pct = int(round(tit_val * 100))
        u3_pct = int(round(t_ultime3 * 100))
        mid_pct = int(round(t_mid * 100))
        hist_pct = int(round(t_storico * 100))

        if starts == n_matches:
            desc = f"{starts}/{n_matches} Titolare (100%)"
        elif starts > 0:
            sub_part = f" + {subs} Sub" if subs > 0 else ""
            desc = f"{starts}/{n_matches} Tit{sub_part} ({pct}%)"
        elif subs > 0:
            desc = f"{subs}/{n_matches} Subentrato ({pct}%)"
        else:
            desc = f"0/{n_matches} Presenze ({pct}%)"

        dettaglio = (
            f"Titolarità Predittiva: {pct}%\n"
            f"• Ultime 3 giornate: {u3_pct}% (peso {int(w_u3*100)}%)\n"
            f"• Giornate 4-8: {mid_pct}% (peso {int(w_mid*100)}%)\n"
            f"• Storico/Àncora: {hist_pct}% (peso {int(w_hist*100)}%)"
        )
        return tit_val, desc, u3_pct, mid_pct, hist_pct, dettaglio

    # Caso 4: Nessuna presenza a referto
    if is_injured:
        tit_val = titolarita_tactical if is_in_11 else 0.20
        pct = int(round(tit_val * 100))
        return tit_val, f"Indisponibile ({pct}%)", pct, pct, int(round(prior * 100)), f"Indisponibile per infortunio ({pct}%)"

    return 0.0, f"0/{n_matches} Presenze (Riserva)", 0, 0, int(round(prior * 100)), f"0/{n_matches} Presenze"

def run_master_pipeline():
    print("=== [Pipeline] AVVIO FANTA MASTER AI (DATI REALI 2025/2026 FOTMOB + G1/G2 2026/27) ===")
    
    # 1. Carica configurazioni
    tactical_db = get_tactical_db()
    injury_db = get_injuries_db()
    fragile_players = get_fragile_players()
    infortuni_2025_26 = get_infortuni_2025_26()
    injuries_history_db = get_injuries_history_db()
    team_ratings = get_team_ratings()
    league_settings = get_league_settings()

    # Prepara lookup rapido e normalizzato per infortuni 2025/26
    infortuni_lookup = {}
    for rec in infortuni_2025_26:
        c = clean_text(rec['name'])
        infortuni_lookup[c] = rec
        tokens = c.split()
        if len(tokens) >= 2:
            last = tokens[-1]
            if last not in infortuni_lookup and len(last) > 3:
                infortuni_lookup[last] = rec

    # 2. Carica listone 2026/27, voti storici, statistiche avanzate FotMob 2025/26 e Match Report G1+G2 2026/27
    df_quot = load_quotazioni()
    voti_lookup = load_voti_storici()
    fotmob_lookup = load_fotmob_stats()
    match_reports_lookup = load_and_aggregate_match_reports()
    voti_2627_lookup = load_voti_2026_27()
    fotmob_2627_lookup = load_fotmob_2026_27_stats()
    team_stats_lookup = load_fotmob_team_stats()

    alias_path = os.path.join(ROOT_DIR, "config", "player_aliases.json")
    aliases = {}
    if os.path.exists(alias_path):
        try:
            with open(alias_path, 'r', encoding='utf-8') as f:
                aliases = json.load(f)
        except Exception:
            pass

    fotmob_2627_by_clean = {}
    if isinstance(fotmob_2627_lookup, dict):
        for fm_id, fm_item in fotmob_2627_lookup.items():
            if isinstance(fm_item, dict):
                nm = fm_item.get('name', '')
                if nm:
                    fotmob_2627_by_clean[clean_text(nm)] = fm_item

    team_matches_map = {}
    reports_csv = os.path.join(ROOT_DIR, "data", "raw", "match_reports_players_g1_g2.csv")
    if os.path.exists(reports_csv):
        df_rep_raw = pd.read_csv(reports_csv)
        for t_name, grp in df_rep_raw.groupby('team'):
            team_matches_map[t_name.upper()] = int(grp['match_name'].nunique())

    # Carica Calendario Ufficiale Serie A 2026/27 per arricchire voti_dettaglio
    cal_file = os.path.join(ROOT_DIR, "data", "processed", "calendario_serie_a_2026_27.json")
    if not os.path.exists(cal_file):
        cal_file = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
    cal_lookup = {}
    if os.path.exists(cal_file):
        try:
            with open(cal_file, 'r', encoding='utf-8') as f:
                cal_data = json.load(f)
            for round_obj in cal_data:
                g = round_obj.get('giornata')
                for m in round_obj.get('matches', []):
                    h = m.get('home', '').upper().strip()
                    a = m.get('away', '').upper().strip()
                    h_cap = m.get('home', '').strip()
                    a_cap = m.get('away', '').strip()
                    if g and h and a:
                        cal_lookup[(g, h)] = {
                            'opponent': a_cap,
                            'is_home': True,
                            'match': f"{h_cap} vs {a_cap}"
                        }
                        cal_lookup[(g, a)] = {
                            'opponent': h_cap,
                            'is_home': False,
                            'match': f"{a_cap} @ {h_cap}"
                        }
        except Exception as e:
            print(f"[Pipeline] Errore caricamento calendario: {e}")

    print(f"-> Quotazioni 2026/27 caricate: {len(df_quot)} calciatori.")
    print(f"-> Database Storico 2025/26: {len(voti_lookup)} Voti Fanta, {len(fotmob_lookup)} Statistiche Avanzate FotMob.")
    print(f"-> Match Report Ufficiali 2026/27: {len(match_reports_lookup)} calciatori a referto.")
    print(f"-> Voti Ufficiali Fantacalcio.it 2026/27: {len(voti_2627_lookup)} chiavi indicizzate.")
    print(f"-> Metriche Avanzate FotMob 2026/27: {len(fotmob_2627_by_clean)} calciatori indicizzati.")
    print(f"-> Metriche di Squadra FotMob 2026/27: {len(team_stats_lookup)} club indicizzati.")
    print(f"-> Calendario Ufficiale Serie A: {len(cal_lookup)} match indicizzati.")

    processed_players = []

    matched_fotmob_count = 0

    for _, q in df_quot.iterrows():
        pid = int(q['Id'])
        raw_name = str(q['Nome']).strip()
        clean_pname = clean_text(raw_name)
        role = str(q['R']).strip().upper()
        mantra_role = str(q['RM']).strip()
        team = str(q['Squadra']).strip()
        fvm = safe_float(q.get('FVM'), 1.0)
        qta = safe_float(q.get('Qt.A'), 1.0)
        diff_q = safe_float(q.get('Diff.'), 0.0)

        # Risoluzione anagrafica voti 2025/26
        v_data = resolve_player(clean_pname, team, voti_lookup, role=role)
        
        presenze = 0
        mv_raw = 0.0
        fm_raw = 0.0
        gf = 0
        rf = 0
        ass = 0
        gs = 0
        amm = 0
        esp = 0
        diff_bm = 0.0
        titolarita_storica = 0.0

        if v_data:
            presenze = safe_int(v_data.get('Partite_a_Voto', 0))
            mv_raw = safe_float(v_data.get('Media_Voto_MV', 0))
            fm_raw = safe_float(v_data.get('FantaMedia_FM', 0))
            gf = safe_int(v_data.get('Gf', 0))
            rf = safe_int(v_data.get('Rf', 0))
            ass = safe_int(v_data.get('Ass', 0))
            gs = safe_int(v_data.get('Gs', 0))
            amm = safe_int(v_data.get('Amm', 0))
            esp = safe_int(v_data.get('Esp', 0))
            titolarita_storica = safe_float(v_data.get('Perc_Titolarita', 0)) / 100.0
            diff_bm = (gf * 3.0 + ass * 1.0) - (gs * 1.0 + amm * 0.5 + esp * 1.0)

        # Risoluzione anagrafica FotMob Statistiche Avanzate 2025/26
        fb_data = fotmob_lookup.get(f"id_{pid}") or resolve_player(clean_pname, team, fotmob_lookup, role=role)
        
        has_data_2526 = False
        league_2526 = "Nuovo 26/27"
        xg_2526 = None
        xg90_2526 = None
        xgot_2526 = None
        xa_2526 = None
        xa90_2526 = None
        xg_xa90_2526 = None
        rating_2526 = None
        mins_2526 = None
        tkl_int90_2526 = None
        shots90_2526 = None
        big_chances_created_2526 = None
        key_passes_2526 = None
        goals_prevented_2526 = None
        clean_sheets_2526 = None
        save_pct_2526 = None

        if fb_data and (fb_data.get('has_data_2526') is True or fb_data.get('mins_played') or fb_data.get('mins_2526')):
            has_data_2526 = True
            matched_fotmob_count += 1
            league_2526 = fb_data.get('league_2526', fb_data.get('league', 'Serie A'))
            mins_2526 = safe_int(fb_data.get('mins_2526', fb_data.get('mins_played')), 0)
            rating_val = safe_float(fb_data.get('rating_2526', fb_data.get('rating')), 0.0)
            rating_2526 = round(rating_val, 2) if rating_val > 0 else None
            
            xg_val = safe_float(fb_data.get('xg_2526', fb_data.get('expected_goals')))
            xg_2526 = round(xg_val, 2) if xg_val is not None else 0.0
            
            xg90_val = safe_float(fb_data.get('xg90_2526', fb_data.get('expected_goals_per_90')))
            xg90_2526 = round(xg90_val, 2) if xg90_val is not None else 0.0
            
            xgot_val = safe_float(fb_data.get('xgot_2526', fb_data.get('expected_goalsontarget')))
            xgot_2526 = round(xgot_val, 2) if xgot_val is not None else 0.0
            
            xa_val = safe_float(fb_data.get('xa_2526', fb_data.get('expected_assists')))
            xa_2526 = round(xa_val, 2) if xa_val is not None else 0.0
            
            xa90_val = safe_float(fb_data.get('xa90_2526', fb_data.get('expected_assists_per_90')))
            xa90_2526 = round(xa90_val, 2) if xa90_val is not None else 0.0
            
            xg_xa_val = safe_float(fb_data.get('xg_xa90_2526', fb_data.get('_expected_goals_and_expected_assists_per_90')))
            xg_xa90_2526 = round(xg_xa_val, 2) if xg_xa_val is not None else (xg90_2526 + xa90_2526)
            
            shots_val = safe_float(fb_data.get('shots90_2526', fb_data.get('total_scoring_att')))
            shots90_2526 = round(shots_val, 2) if shots_val is not None else 0.0
            
            tkl_val = safe_float(fb_data.get('total_tackle'), 0.0)
            int_val = safe_float(fb_data.get('interception'), 0.0)
            tkl_int_direct = safe_float(fb_data.get('tkl_int90_2526'))
            tkl_int90_2526 = round(tkl_int_direct if tkl_int_direct > 0 else (tkl_val + int_val), 2)
            
            big_chances_created_2526 = safe_int(fb_data.get('big_chances_created_2526', fb_data.get('big_chance_created')), 0)
            key_passes_2526 = safe_int(fb_data.get('key_passes_2526', fb_data.get('total_att_assist')), 0)
            
            if role == 'P':
                goals_prev_val = safe_float(fb_data.get('goals_prevented_2526', fb_data.get('_goals_prevented')))
                goals_prevented_2526 = round(goals_prev_val, 2) if goals_prev_val is not None else 0.0
                clean_sheets_2526 = safe_int(fb_data.get('clean_sheets_2526', fb_data.get('clean_sheet')), 0)
                save_pct_2526 = round(safe_float(fb_data.get('save_pct_2526', fb_data.get('_save_percentage')), 0.0), 1)

        # Informazioni Tattiche Club 2026/2027
        tactical_info = tactical_db.get(team, {})
        rigoristi = tactical_info.get("rigoristi", [])
        punizioni = tactical_info.get("punizioni", [])
        corner = tactical_info.get("corner", [])
        top_list = tactical_info.get("top", [])
        sleeper_list = tactical_info.get("sleeper", [])
        flop_list = tactical_info.get("flop", [])
        lineup = tactical_info.get("lineup", [])

        is_rigorista_1 = any(match_player_name(clean_pname, r) for r in rigoristi[:1])
        is_rigorista_2 = any(match_player_name(clean_pname, r) for r in rigoristi[1:2])
        is_rigorista_3 = any(match_player_name(clean_pname, r) for r in rigoristi[2:])
        is_corner = any(match_player_name(clean_pname, c) for c in corner)
        is_punizioni = any(match_player_name(clean_pname, p) for p in punizioni)

        is_in_11 = False
        is_oop = False
        fpp_fpn = "NONE"
        pos_label = ""
        oop_type = ""
        oop_desc = ""
        pitch_pos = ""
        for lp in lineup:
            if match_player_name(clean_pname, lp.get('name', '')):
                is_in_11 = True
                pitch_pos = lp.get('pos', '')
                pos_label = lp.get('pos_label', '')
                is_oop = lp.get('oop', False)
                fpp_fpn = lp.get('fpp_fpn', 'NONE')
                if fpp_fpn == 'NONE' and is_oop:
                    fpp_fpn = 'FPP'
                oop_type = lp.get('oop_type', '')
                oop_desc = lp.get('oop_desc', '')
                break

        # Check additional oop_players (per calciatori in ballottaggio/rotazione ma Fuori Ruolo)
        oop_list = tactical_info.get("oop_players", [])
        for op in oop_list:
            if match_player_name(clean_pname, op.get('name', '')):
                is_oop = True
                fpp_fpn = op.get('fpp_fpn', 'FPP')
                pos_label = op.get('pos_label', pos_label)
                oop_type = op.get('oop_type', 'FPP_C_IN_A')
                oop_desc = op.get('oop_desc', '')
                if not pitch_pos:
                    pitch_pos = op.get('pos', '')
                break

        is_top = any(match_player_name(clean_pname, t) for t in top_list)
        is_sleeper = any(match_player_name(clean_pname, s) for s in sleeper_list)
        is_flop = any(match_player_name(clean_pname, f) for f in flop_list)

        # Check explicit ballottaggi list
        is_in_ballottaggio = False
        titolarita_desc_2627 = ""
        titolarita_tactical = 0.50
        ballottaggi_list = tactical_info.get("ballottaggi", [])
        for b in ballottaggi_list:
            if match_player_name(clean_pname, b.get('player', '')):
                is_in_ballottaggio = True
                titolarita_tactical = round(b.get('pct', 50) / 100.0, 2)
                titolarita_desc_2627 = f"Ballottaggio {b.get('pct')}% vs {b.get('vs', '')}"
                break

        if not is_in_ballottaggio:
            if is_in_11: 
                titolarita_tactical = 0.92
            elif fvm >= 50: 
                titolarita_tactical = 0.65
            elif fvm >= 20: 
                titolarita_tactical = 0.45
            elif fvm >= 8:
                titolarita_tactical = 0.35
            else:
                titolarita_tactical = 0.25

        # ---------------------------------------------------------------------
        # VERIFICA INFORTUNIO ATTUALE 2026/27 (DB INFORTUNI)
        # ---------------------------------------------------------------------
        is_injured = False
        infortunio_info_matched = None
        infortunio_motivo = ""
        infortunio_rientro = ""
        infortunio_status = "🟢 Disponibile"
        infortunio_severity = ""
        infortunio_tipo_stop = ""
        giornate_perse = 0

        inj_list = injury_db if isinstance(injury_db, list) else list(injury_db.values())
        for inj_info in inj_list:
            inj_name = inj_info.get("player", inj_info.get("name", ""))
            inj_team = inj_info.get("team", inj_info.get("squadra", ""))
            name_match = match_player_name(clean_pname, inj_name)
            team_match = (inj_team.lower() in team.lower() or team.lower() in inj_team.lower()) if inj_team else True
            inj_pid = inj_info.get("player_id")
            if (inj_pid and inj_pid == pid) or (name_match and team_match):
                is_injured = True
                infortunio_info_matched = inj_info
                infortunio_motivo = inj_info.get("motivo", "")
                infortunio_rientro = inj_info.get("rientro", "")
                infortunio_severity = inj_info.get("severity", "orange")
                infortunio_tipo_stop = inj_info.get("tipo_stop", "Infortunato")
                emoji_inj = "🟠" if infortunio_severity == "orange" else "🔴"
                infortunio_status = f"{emoji_inj} {infortunio_tipo_stop} (Rientro: {infortunio_rientro} - {infortunio_motivo})"
                break

        # ---------------------------------------------------------------------
        # DATI REALI SERIE A 2026/2027 (MATCH REPORT UFFICIALI 5 GIORNATE)
        # ---------------------------------------------------------------------
        rep_key = f"{clean_pname}_{team.lower()}"
        rep_data = match_reports_lookup.get(rep_key)
        if not rep_data:
            for k, r_val in match_reports_lookup.items():
                k_pname, k_team = k.split('_', 1) if '_' in k else (k, '')
                if (team.lower() in k_team or k_team in team.lower() or not k_team or not team) and match_player_name(clean_pname, k_pname):
                    rep_data = r_val
                    break

        has_data_2627 = False
        presenze_2627 = 0
        starts_2627 = 0
        minuti_2627 = 0
        gol_2627 = 0
        assist_2627 = 0
        tiri_2627 = 0
        tiri_porta_2627 = 0
        key_passes_2627 = 0
        recuperi_2627 = 0
        falli_subiti_2627 = 0
        amm_2627 = 0
        esp_2627 = 0
        clean_sheets_2627 = 0
        parate_2627 = 0
        gol_subiti_2627 = 0
        n_team_matches = team_matches_map.get(team.upper(), 5)

        is_new_arrival = (clean_pname == 'alaba' or pid == 59016 or 'alaba' in raw_name.lower())

        if rep_data:
            has_data_2627 = True
            presenze_2627 = rep_data['presenze_2627']
            starts_2627 = rep_data['titolarita_count_2627']
            minuti_2627 = rep_data['minuti_2627']
            gol_2627 = rep_data['gol_2627']
            assist_2627 = rep_data['assist_2627']
            tiri_2627 = rep_data['tiri_2627']
            tiri_porta_2627 = rep_data['tiri_porta_2627']
            key_passes_2627 = rep_data['key_passes_2627']
            recuperi_2627 = rep_data['recuperi_2627']
            falli_subiti_2627 = rep_data['falli_subiti_2627']
            amm_2627 = rep_data['ammonizioni_2627']
            esp_2627 = rep_data['espulsioni_2627']
            clean_sheets_2627 = rep_data['clean_sheets_2627']
            parate_2627 = rep_data['parate_2627']
            gol_subiti_2627 = rep_data['gol_subiti_2627']

        # CALCOLO DINAMICO E PREDITTIVO DELLA TITOLARITA' (3 FASCE PONDERATE)
        titolarita, titolarita_desc_2627, tit_u3, tit_mid, tit_hist, tit_dettaglio = compute_predictive_titolarita(
            clean_pname=clean_pname,
            team=team,
            rep_data=rep_data,
            n_team_matches=n_team_matches,
            is_injured=is_injured,
            infortunio_info=infortunio_info_matched,
            titolarita_tactical=titolarita_tactical,
            titolarita_storica=titolarita_storica,
            is_in_11=is_in_11,
            is_new_arrival=is_new_arrival,
            fvm=fvm
        )

        # ---------------------------------------------------------------------
        # SISTEMA DI CLASSIFICAZIONE OOP MANTRA (ORO, ARGENTO, BRONZO)
        # ---------------------------------------------------------------------
        three_def_teams = {'Inter', 'Roma', 'Milan', 'Genoa', 'Monza', 'Torino', 'Udinese', 'Venezia'}
        mantra_subroles = set(mantra_role.split(';')) if mantra_role else set()
        oop_tier = ""

        # 1. Difensori D con 'E' (Quinti a tutta fascia)
        if role == 'D' and 'E' in mantra_subroles:
            is_oop = True
            fpp_fpn = 'FPP'
            oop_type = 'FPP_D_IN_C'
            if team in three_def_teams:
                if is_in_11 or titolarita >= 0.50:
                    oop_tier = "ORO"
                    if not oop_desc: oop_desc = "🥇 Super King Power (Quinto difesa a 3)"
                else:
                    oop_tier = "BRONZO"
                    if not oop_desc: oop_desc = "🥉 Riserva Quinto difesa a 3"
            else:
                if is_in_11 or titolarita >= 0.50:
                    oop_tier = "ARGENTO"
                    if not oop_desc: oop_desc = "🥈 Terzino di spinta (E)"
                else:
                    oop_tier = "BRONZO"
                    if not oop_desc: oop_desc = "🥉 Terzino di rotazione (E)"

        # 2. Centrocampisti C con 'A' o 'W' (Tier 1: Ali d'attacco e Seconde Punte)
        elif role == 'C' and ('A' in mantra_subroles or 'W' in mantra_subroles):
            is_oop = True
            fpp_fpn = 'FPP'
            oop_type = 'FPP_C_IN_A'
            if is_in_11 or titolarita >= 0.50:
                oop_tier = "ORO"
                if not oop_desc: oop_desc = "🥇 Top OOP: Ala/Seconda Punta d'attacco"
            else:
                oop_tier = "BRONZO"
                if not oop_desc: oop_desc = "🥉 Ala/Attaccante di rotazione"

        # 3. Centrocampisti C con 'T' (Tier 2: Trequartisti d'incursione)
        elif role == 'C' and 'T' in mantra_subroles:
            is_oop = True
            fpp_fpn = 'FPP'
            oop_type = 'FPP_C_IN_A'
            if is_in_11 or titolarita >= 0.50:
                oop_tier = "ARGENTO"
                if not oop_desc: oop_desc = "🥈 Trequartista d'incursione (T)"
            else:
                oop_tier = "BRONZO"
                if not oop_desc: oop_desc = "🥉 Trequartista di riserva (T)"
        
        elif is_oop:
            if not oop_tier:
                oop_tier = "ORO" if is_in_11 else "BRONZO"

        t_mult = team_ratings.get(team, {}).get("multiplier", 1.0) if isinstance(team_ratings.get(team), dict) else team_ratings.get(team, 1.0)

        # Calcolo OVR e Prezzo Base
        effective_in_11 = (is_in_11 and (starts_2627 >= 1 or is_new_arrival)) or (titolarita >= 0.60)
        ovr, prezzo_cons = compute_continuous_ovr_and_price(role, fvm, effective_in_11, team_mult=t_mult)

        # Leggero boost predittivo se ha metriche 25/26 eccezionali
        if has_data_2526:
            if xg90_2526 and xg90_2526 >= 0.45: ovr += 0.8
            if xa90_2526 and xa90_2526 >= 0.25: ovr += 0.6
            if rating_2526 and rating_2526 >= 7.20: ovr += 0.6

        # ---------------------------------------------------------------------
        # BONUS TATTICI STRATEGICI (Rigoristi, Prima Punta PC, Fuori Ruolo, Piazzati)
        # ---------------------------------------------------------------------
        if is_rigorista_1:
            ovr += 3.5 # 1° Rigorista garantisce +3 bonus e gol pesanti
            prezzo_cons = int(round(prezzo_cons * 1.25 + 3))
        elif is_rigorista_2:
            ovr += 1.5
            prezzo_cons = int(round(prezzo_cons * 1.10 + 1))
        elif is_rigorista_3:
            ovr += 0.5

        # Prima Punta / Centravanti di riferimento negli 11 titolari
        if is_in_11 and pitch_pos in ['PC', 'PUN', 'PC_C', 'ATT', 'SP']:
            ovr += 2.0
            prezzo_cons = int(round(prezzo_cons * 1.15 + 2))

        # Calciatore Fuori Ruolo Positivo (FPP / OOP)
        if is_oop or fpp_fpn == 'FPP':
            if oop_tier == "ORO":
                ovr += 3.0
                prezzo_cons = int(round(prezzo_cons * 1.25 + 3))
            elif oop_tier == "ARGENTO":
                ovr += 2.0
                prezzo_cons = int(round(prezzo_cons * 1.15 + 2))
            else:
                ovr += 1.2
                prezzo_cons = int(round(prezzo_cons * 1.08 + 1))

        if is_punizioni: ovr += 1.0
        if is_corner: ovr += 0.5

        if is_top: ovr += 1.5
        if is_sleeper: ovr += 0.8
        if is_flop: ovr -= 2.0

        # Boost per rendimento reale 2026/2027 (gol, assist, clean sheet sul campo)
        if rep_data:
            if gol_2627 > 0:
                ovr += min(2.5, gol_2627 * 0.5)
                prezzo_cons = int(round(prezzo_cons + min(25, gol_2627 * 5)))
            if assist_2627 > 0:
                ovr += min(1.2, assist_2627 * 0.3)
                prezzo_cons = int(round(prezzo_cons + min(12, assist_2627 * 3)))
            if clean_sheets_2627 > 0 and role == 'P':
                ovr += min(1.0, clean_sheets_2627 * 0.5)
                prezzo_cons = int(round(prezzo_cons + 3))
        else:
            # Nessuna presenza nei match report: se doveva essere titolare nell'11 e non è nuovo acquisto, segnale di perdita del posto
            if is_in_11 and not is_new_arrival and n_team_matches >= 2:
                ovr -= 0.6

        # Lookup Voti Ufficiali Fantacalcio.it 2026/27
        v2627_entry = voti_2627_lookup.get(f"cod_{pid}") or voti_2627_lookup.get(clean_pname)
        partite_voto_2627 = v2627_entry.get('partite_a_voto', 0) if v2627_entry else 0
        mv_2627 = v2627_entry['media_voto_2627'] if (v2627_entry and v2627_entry['partite_a_voto'] > 0) else None
        fm_2627 = v2627_entry['fantamedia_2627'] if (v2627_entry and v2627_entry['partite_a_voto'] > 0) else None
        voti_dettaglio_2627 = []
        if v2627_entry and v2627_entry.get('voti_dettaglio'):
            for vd in v2627_entry['voti_dettaglio']:
                vd_copy = dict(vd)
                g_num = vd_copy.get('giornata')
                m_info = cal_lookup.get((g_num, team.upper().strip()), {})
                vd_copy['opponent'] = m_info.get('opponent', vd_copy.get('opponent', '-'))
                vd_copy['is_home'] = m_info.get('is_home', vd_copy.get('is_home', True))
                vd_copy['match'] = m_info.get('match', vd_copy.get('match', f"vs {vd_copy['opponent']}"))
                voti_dettaglio_2627.append(vd_copy)
        tot_bonus_2627 = v2627_entry.get('tot_bonus_2627', 0.0) if v2627_entry else 0.0
        tot_malus_2627 = v2627_entry.get('tot_malus_2627', 0.0) if v2627_entry else 0.0
        if not tot_bonus_2627 and (gol_2627 > 0 or assist_2627 > 0):
            tot_bonus_2627 = round((gol_2627 * 3.0) + (assist_2627 * 1.0), 2)
        if not tot_malus_2627 and (gol_subiti_2627 > 0 or amm_2627 > 0 or esp_2627 > 0):
            tot_malus_2627 = round((gol_subiti_2627 * 1.0) + (amm_2627 * 0.5) + (esp_2627 * 1.0), 2)

        # Lookup Metriche Avanzate FotMob 2026/27 (xG/90, xA/90, Big Chances, ecc.)
        target_name = aliases.get(raw_name, raw_name)
        target_clean = clean_text(target_name)

        fm26_entry = None
        if target_clean in fotmob_2627_by_clean:
            fm26_entry = fotmob_2627_by_clean[target_clean]
        elif clean_pname in fotmob_2627_by_clean:
            fm26_entry = fotmob_2627_by_clean[clean_pname]
        else:
            for c_fm, fm_obj in fotmob_2627_by_clean.items():
                if match_player_name(target_name, fm_obj.get('name', '')) or match_player_name(raw_name, fm_obj.get('name', '')):
                    fm_t = fm_obj.get('team_name', '')
                    if not fm_t or not team or team.lower() in fm_t.lower() or fm_t.lower() in team.lower():
                        fm26_entry = fm_obj
                        break

        fm26_stats = {}
        if fm26_entry:
            fm26_stats = fm26_entry.get('stats', {}) or fm26_entry.get('stats_2627', {})

        xg_2627 = safe_float(fm26_stats.get('xg_2627', fm26_stats.get('expected_goals'))) if (fm26_stats.get('xg_2627') is not None or fm26_stats.get('expected_goals') is not None) else None
        xg90_2627 = safe_float(fm26_stats.get('xg90_2627', fm26_stats.get('expected_goals_per_90'))) if (fm26_stats.get('xg90_2627') is not None or fm26_stats.get('expected_goals_per_90') is not None) else None
        xa_2627 = safe_float(fm26_stats.get('xa_2627', fm26_stats.get('expected_assists'))) if (fm26_stats.get('xa_2627') is not None or fm26_stats.get('expected_assists') is not None) else None
        xa90_2627 = safe_float(fm26_stats.get('xa90_2627', fm26_stats.get('expected_assists_per_90'))) if (fm26_stats.get('xa90_2627') is not None or fm26_stats.get('expected_assists_per_90') is not None) else None
        xgot_2627 = safe_float(fm26_stats.get('xgot_2627', fm26_stats.get('expected_goalsontarget'))) if (fm26_stats.get('xgot_2627') is not None or fm26_stats.get('expected_goalsontarget') is not None) else None
        big_chances_created_2627 = safe_int(fm26_stats.get('big_chances_created_2627', fm26_stats.get('big_chance_created'))) if (fm26_stats.get('big_chances_created_2627') is not None or fm26_stats.get('big_chance_created') is not None) else None
        chances_created_2627 = safe_int(fm26_stats.get('chances_created_2627', fm26_stats.get('total_att_assist'))) if (fm26_stats.get('chances_created_2627') is not None or fm26_stats.get('total_att_assist') is not None) else None
        rating_fotmob_2627 = safe_float(fm26_stats.get('rating_fotmob_2627', fm26_stats.get('rating'))) if (fm26_stats.get('rating_fotmob_2627') is not None or fm26_stats.get('rating') is not None) else None
        total_scoring_att_2627 = safe_float(fm26_stats.get('total_scoring_att_2627', fm26_stats.get('total_scoring_att'))) if (fm26_stats.get('total_scoring_att_2627') is not None or fm26_stats.get('total_scoring_att') is not None) else None
        ontarget_scoring_att_2627 = safe_float(fm26_stats.get('ontarget_scoring_att_2627', fm26_stats.get('ontarget_scoring_att'))) if (fm26_stats.get('ontarget_scoring_att_2627') is not None or fm26_stats.get('ontarget_scoring_att') is not None) else None
        won_contest_2627 = safe_float(fm26_stats.get('won_contest_2627', fm26_stats.get('won_contest'))) if (fm26_stats.get('won_contest_2627') is not None or fm26_stats.get('won_contest') is not None) else None
        big_chance_missed_2627 = safe_int(fm26_stats.get('big_chance_missed_2627', fm26_stats.get('big_chance_missed'))) if (fm26_stats.get('big_chance_missed_2627') is not None or fm26_stats.get('big_chance_missed') is not None) else None
        poss_won_att_3rd_2627 = safe_float(fm26_stats.get('poss_won_att_3rd_2627', fm26_stats.get('poss_won_att_3rd'))) if (fm26_stats.get('poss_won_att_3rd_2627') is not None or fm26_stats.get('poss_won_att_3rd') is not None) else None
        goals_conceded_fotmob_2627 = safe_int(fm26_stats.get('goals_conceded_fotmob_2627', fm26_stats.get('goals_conceded'))) if (fm26_stats.get('goals_conceded_fotmob_2627') is not None or fm26_stats.get('goals_conceded') is not None) else None
        save_pct_2627 = safe_float(fm26_stats.get('save_pct_2627', fm26_stats.get('_save_percentage'))) if (fm26_stats.get('save_pct_2627') is not None or fm26_stats.get('_save_percentage') is not None) else None
        clean_sheet_fotmob_2627 = safe_int(fm26_stats.get('clean_sheet_fotmob_2627', fm26_stats.get('clean_sheet'))) if (fm26_stats.get('clean_sheet_fotmob_2627') is not None or fm26_stats.get('clean_sheet') is not None) else None
        total_tackle_2627 = safe_float(fm26_stats.get('total_tackle_2627', fm26_stats.get('total_tackle'))) if (fm26_stats.get('total_tackle_2627') is not None or fm26_stats.get('total_tackle') is not None) else None
        defensive_contributions_2627 = safe_float(fm26_stats.get('defensive_contributions_2627', fm26_stats.get('defensive_contributions'))) if (fm26_stats.get('defensive_contributions_2627') is not None or fm26_stats.get('defensive_contributions') is not None) else None
        ball_recovery_fotmob_2627 = safe_float(fm26_stats.get('ball_recovery_fotmob_2627', fm26_stats.get('ball_recovery'))) if (fm26_stats.get('ball_recovery_fotmob_2627') is not None or fm26_stats.get('ball_recovery') is not None) else None
        goals_prevented_2627 = safe_float(fm26_stats.get('goals_prevented_2627', fm26_stats.get('_goals_prevented'))) if (fm26_stats.get('goals_prevented_2627') is not None or fm26_stats.get('_goals_prevented') is not None) else None
        minuti_fotmob_2627 = safe_int(fm26_stats.get('minuti_fotmob_2627', fm26_entry.get('minutes_played') if fm26_entry else 0))
        fouls_2627 = safe_float(fm26_stats.get('fouls_2627', fm26_stats.get('fouls'))) if (fm26_stats.get('fouls_2627') is not None or fm26_stats.get('fouls') is not None) else None

        # Lookup Statistiche Squadra FotMob 2026/27 (Ecosistema Tattico)
        t_stats = team_stats_lookup.get(team, {})
        team_context = {
            "attacco_label": t_stats.get("attacco_label", "Attacco Medio"),
            "attacco_tier": t_stats.get("attacco_tier", "medium"),
            "difesa_label": t_stats.get("difesa_label", "Difesa Media"),
            "difesa_tier": t_stats.get("difesa_tier", "medium"),
            "xg_team": safe_float(t_stats.get("xg_team")),
            "xg_team_rank": safe_int(t_stats.get("xg_team_rank")),
            "xga_team": safe_float(t_stats.get("xga_team")),
            "xga_team_rank": safe_int(t_stats.get("xga_team_rank")),
            "clean_sheets_team": safe_int(t_stats.get("clean_sheets")),
            "big_chances_team": safe_int(t_stats.get("big_chances")),
            "touches_opp_box_team": safe_int(t_stats.get("touches_opp_box")),
            "corners_team": safe_int(t_stats.get("corners")),
            "saves_per_match_team": safe_float(t_stats.get("saves_per_match")),
            "goals_conceded_match_team": safe_float(t_stats.get("goals_conceded_match"))
        }

        # Impatto Scientifico Ecosistema di Squadra sull'OVR
        # Attaccanti e Centrocampisti beneficiano della mole offensiva (xG/Big Chances)
        if role in ['A', 'C']:
            att_tier = team_context["attacco_tier"]
            if att_tier == "top":
                ovr += 1.2
            elif att_tier == "good":
                ovr += 0.5
            elif att_tier == "risk":
                ovr -= 1.0

        # Portieri e Difensori beneficiano della solidità difensiva (xGA/Clean Sheets)
        elif role in ['P', 'D']:
            def_tier = team_context["difesa_tier"]
            if def_tier == "top":
                ovr += 1.5
            elif def_tier == "good":
                ovr += 0.6
            elif def_tier == "risk":
                ovr -= 1.2

        # ---------------------------------------------------------------------
        # CALIBRAZIONE OVR SU RENDIMENTO REALE STAGIONE 2026/27 (5 GIORNATE)
        # ---------------------------------------------------------------------
        if partite_voto_2627 >= 2 and fm_2627 is not None:
            # Grado di confidenza proporzionale al numero di giornate disputate (fino a 5/5)
            confidence = min(1.0, partite_voto_2627 / 5.0)
            target_baseline_fm = fm_raw if (fm_raw and fm_raw > 0) else 6.0
            fm_delta = fm_2627 - target_baseline_fm
            # Calibrazione: +1.0 di fantamedia su 5 gare = fino a +2.0 OVR
            ovr += float(np.clip(fm_delta * 0.75 * confidence, -3.0, 3.0))

            # Valutazione Rating FotMob ufficiale 2026/27
            if rating_fotmob_2627 and rating_fotmob_2627 > 0:
                if rating_fotmob_2627 >= 7.30:
                    ovr += 0.8 * confidence
                elif rating_fotmob_2627 >= 7.05:
                    ovr += 0.4 * confidence
                elif rating_fotmob_2627 < 6.20:
                    ovr -= 0.6 * confidence
        elif n_team_matches >= 4 and presenze_2627 == 0 and not is_injured and not is_new_arrival:
            # Calciatore integro ma mai impiegato dopo 5 giornate
            ovr -= 1.0

        # ---------------------------------------------------------------------
        # CALCOLO FRAGILITÀ FISICA & SEMAFORO (CON PESO SULL'OVERALL FINALE)
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # STORICO INFORTUNI & INDICE DI FRAGILITÀ FISICA MULTI-ANNO
        # ---------------------------------------------------------------------
        hist_entry = None
        t_hist = injuries_history_db.get(team, {}) if isinstance(injuries_history_db, dict) else {}
        for h_k, h_v in t_hist.items():
            if (h_v.get('id') and h_v.get('id') == pid) or match_player_name(clean_pname, h_k):
                hist_entry = h_v
                break
        if not hist_entry and isinstance(injuries_history_db, dict):
            for t_k, t_dict in injuries_history_db.items():
                if isinstance(t_dict, dict):
                    for h_k, h_v in t_dict.items():
                        if isinstance(h_v, dict) and ((h_v.get('id') and h_v.get('id') == pid) or match_player_name(clean_pname, h_k)):
                            hist_entry = h_v
                            break
                if hist_entry:
                    break

        if hist_entry:
            fragilita_val = hist_entry.get('fragility_label', '🟢 Bassa')
            fragilita_badge = hist_entry.get('fragility_badge', 'bassa')
            fragilita_score = hist_entry.get('indice_fragilita_score', 10.0)
            fragility_tier = hist_entry.get('livello_fragilita', 'ROCCIA')
            partite_saltate_totali = hist_entry.get('partite_saltate_totali', 0)
            giorni_stop_totali = hist_entry.get('giorni_stop_totali', 0)
            disponibilita_pct = hist_entry.get('disponibilita_pct', 100.0)
            recidive_muscolari = hist_entry.get('recidive_muscolari', 0)
            consiglio_medico_ai = hist_entry.get('consiglio_medico_ai', '')
            cronistoria_infortuni = hist_entry.get('cronistoria_infortuni', [])
            fragilita_dettaglio = f"{partite_saltate_totali} gare saltate • Disp. {disponibilita_pct}%"
            integrita = f"{fragilita_val} ({disponibilita_pct}% disp.)"
            integrita_badge = fragilita_badge
            is_chronic_fragile = (fragility_tier in ['FRAGILE', 'CRISTALLO'])
            
            # Penalità ponderata su OVR e Prezzo
            if fragility_tier == 'CRISTALLO':
                ovr -= 3.5
                prezzo_cons = max(1, int(round(prezzo_cons * 0.75)))
            elif fragility_tier == 'FRAGILE':
                ovr -= 2.0
                prezzo_cons = max(1, int(round(prezzo_cons * 0.85)))
            elif fragility_tier == 'ATTENZIONE':
                ovr -= 0.8
                prezzo_cons = max(1, int(round(prezzo_cons * 0.94)))
        else:
            fragilita_val = "🟢 Roccia (Massima Affidabilità)"
            fragilita_badge = "roccia"
            fragilita_score = 5.0
            fragility_tier = "ROCCIA"
            partite_saltate_totali = 0
            giorni_stop_totali = 0
            disponibilita_pct = 100.0
            recidive_muscolari = 0
            consiglio_medico_ai = "Calciatore integro e solido. Nessun problema muscolare ricorrente negli ultimi 24 mesi: affidabilità fisica massima."
            cronistoria_infortuni = []
            fragilita_dettaglio = "Nessun infortunio registrato (100% disponibilità)"
            integrita = "🟢 Affidabile (100% disp.)"
            integrita_badge = "roccia"
            is_chronic_fragile = False
            if presenze >= 30:
                ovr += 0.5 # Piccolo bonus continuità per titolarità completa

        # Applicazione penalità infortunio attuale 2026/27 (se infortunato)
        if is_injured:
            giornate_perse, pen_ovr, mult_prc = calcola_impatto_infortunio(infortunio_rientro)
            ovr -= pen_ovr
            prezzo_cons = max(1, int(round(prezzo_cons * mult_prc)))

        # Tetto massimo credibile per budget asta 1000 CR
        if role == 'P':
            prezzo_cons = min(75, prezzo_cons)
        elif role == 'D':
            prezzo_cons = min(170, prezzo_cons)
        elif role == 'C':
            prezzo_cons = min(260, prezzo_cons)
        else: # 'A'
            prezzo_cons = min(440, prezzo_cons)

        value_ovr = int(np.clip(round(ovr), 45, 98))

        # Max Bid calcolato sul prezzo effettivo con tetto massimo
        max_bid = int(round(prezzo_cons * 1.15))
        if role == 'P': max_bid = min(88, max_bid)
        elif role == 'D': max_bid = min(195, max_bid)
        elif role == 'C': max_bid = min(295, max_bid)
        else: max_bid = min(480, max_bid)

        # Rigorista & Piazzati
        if is_rigorista_1: rigorista_val = "1° Rigorista"
        elif is_rigorista_2: rigorista_val = "2° Rigorista"
        elif is_rigorista_3: rigorista_val = "3° Rigorista"
        else: rigorista_val = "-"

        if is_punizioni and is_corner: piazzati_val = "🎯 Corner & Punizioni"
        elif is_punizioni: piazzati_val = "🎯 Punizioni"
        elif is_corner: piazzati_val = "🎯 Corner"
        else: piazzati_val = "-"

        # OOP tag sintetico con gerarchia medaglie (ORO, ARGENTO, BRONZO)
        if is_oop or fpp_fpn == 'FPP':
            if oop_tier == "ORO":
                if role == 'D':
                    oop_val = "🥇 ORO • Quinto a 3"
                else:
                    oop_val = "🥇 ORO • Ala/Seconda Punta"
            elif oop_tier == "ARGENTO":
                if role == 'D':
                    oop_val = "🥈 ARGENTO • Terzino E"
                else:
                    oop_val = "🥈 ARGENTO • Trequartista"
            elif oop_tier == "BRONZO":
                if role == 'D':
                    oop_val = "🥉 BRONZO • Riserva Quinto"
                else:
                    oop_val = "🥉 BRONZO • Riserva T/W/A"
            elif pos_label:
                oop_val = f"⭐ {pos_label}"
            else:
                oop_val = "⭐ Avanzato"
        elif fpp_fpn == 'FPN':
            oop_val = "⚠️ Arretrato"
        else:
            oop_val = "-"

        if value_ovr >= 92: fascia = "1ª Fascia (Top Assoluto)"
        elif value_ovr >= 84: fascia = "2ª Fascia (Semi-Top / Titolare di Lusso)"
        elif value_ovr >= 75: fascia = "3ª Fascia (Ottimo Titolare)"
        elif value_ovr >= 68: fascia = "4ª Fascia (Scommessa / Copertura)"
        else: fascia = "5ª Fascia (Low Cost / Slot 1 Credito)"

        temp_record = {
            "id": pid,
            "name": raw_name,
            "role": role,
            "mantra": mantra_role,
            "team": team,
            "fvm": fvm,
            "qta": qta,
            "diff_q": diff_q,
            "presenze": presenze,
            "mv": round(mv_raw, 2),
            "fm": round(fm_raw, 2),
            "gf": gf,
            "rf": rf,
            "ass": ass,
            "gs": gs,
            "amm": amm,
            "esp": esp,
            "diff_bm": round(diff_bm, 1),
            "titolarita": int(round(titolarita * 100)),
            "titolarita_ultime3": tit_u3,
            "titolarita_mid": tit_mid,
            "titolarita_storico": tit_hist,
            "titolarita_dettaglio": tit_dettaglio,
            
            # --- METRICHE REALI 2026/2027 (G1 + G2 MATCH REPORTS) ---
            "has_data_2627": has_data_2627,
            "presenze_2627": presenze_2627,
            "starts_2627": starts_2627,
            "titolarita_desc_2627": titolarita_desc_2627,
            "minuti_2627": minuti_2627,
            "gol_2627": gol_2627,
            "assist_2627": assist_2627,
            "tiri_2627": tiri_2627,
            "tiri_porta_2627": tiri_porta_2627,
            "key_passes_2627": key_passes_2627,
            "recuperi_2627": recuperi_2627,
            "falli_subiti_2627": falli_subiti_2627,
            "amm_2627": amm_2627,
            "esp_2627": esp_2627,
            "clean_sheets_2627": clean_sheets_2627,
            "parate_2627": parate_2627,
            "gol_subiti_2627": gol_subiti_2627,
            "mv_2627": mv_2627,
            "fm_2627": fm_2627,
            "tot_bonus_2627": tot_bonus_2627,
            "tot_malus_2627": tot_malus_2627,
            "partite_voto_2627": partite_voto_2627,
            "voti_dettaglio_2627": voti_dettaglio_2627,

            # --- METRICHE AVANZATE REALI 2026/2027 (FOTMOB) ---
            "xg_2627": xg_2627,
            "xg90_2627": xg90_2627,
            "xa_2627": xa_2627,
            "xa90_2627": xa90_2627,
            "xgot_2627": xgot_2627,
            "big_chances_created_2627": big_chances_created_2627,
            "chances_created_2627": chances_created_2627,
            "rating_live_2627": rating_fotmob_2627,
            "total_scoring_att_2627": total_scoring_att_2627,
            "ontarget_scoring_att_2627": ontarget_scoring_att_2627,
            "won_contest_2627": won_contest_2627,
            "big_chance_missed_2627": big_chance_missed_2627,
            "poss_won_att_3rd_2627": poss_won_att_3rd_2627,
            "goals_conceded_stat_2627": goals_conceded_fotmob_2627,
            "save_pct_2627": save_pct_2627,
            "clean_sheet_stat_2627": clean_sheet_fotmob_2627,
            "total_tackle_2627": total_tackle_2627,
            "defensive_contributions_2627": defensive_contributions_2627,
            "ball_recovery_stat_2627": ball_recovery_fotmob_2627,
            "goals_prevented_2627": goals_prevented_2627,
            "minuti_stat_2627": minuti_fotmob_2627,
            "fouls_2627": fouls_2627,

            # --- METRICHE AVANZATE REALI 2025/2026 ---
            "has_data_2526": has_data_2526,
            "league_2526": league_2526,
            "xg_2526": xg_2526,
            "xg90_2526": xg90_2526,
            "xgot_2526": xgot_2526,
            "xa_2526": xa_2526,
            "xa90_2526": xa90_2526,
            "xg_xa90_2526": xg_xa90_2526,
            "rating_2526": rating_2526,
            "mins_2526": mins_2526,
            "tkl_int90_2526": tkl_int90_2526,
            "shots90_2526": shots90_2526,
            "big_chances_created_2526": big_chances_created_2526,
            "key_passes_2526": key_passes_2526,
            "goals_prevented_2526": goals_prevented_2526,
            "clean_sheets_2526": clean_sheets_2526,
            "save_pct_2526": save_pct_2526,
            
            # Campi legacy per retrocompatibilità
            "xg90": xg90_2526 if xg90_2526 is not None else 0.0,
            "xa90": xa90_2526 if xa90_2526 is not None else 0.0,
            "sh90": shots90_2526 if shots90_2526 is not None else 0.0,
            "kp90": key_passes_2526 if key_passes_2526 is not None else 0.0,
            "tkl_int90": tkl_int90_2526 if tkl_int90_2526 is not None else 0.0,

            "fantascore": round(ovr, 1),
            "ovr": value_ovr,
            "prezzo_cons": prezzo_cons,
            "max_bid": max_bid,
            "fascia": fascia,
            "slot_fascia": "",
            "slot_num": 1,
            "integrita": integrita,
            "integrita_badge": integrita_badge,
            "fragilita_val": fragilita_val,
            "fragilita_badge": fragilita_badge,
            "fragilita_score": fragilita_score,
            "fragility_score": fragilita_score,
            "fragilita_dettaglio": fragilita_dettaglio,
            "fragility_tier": fragility_tier,
            "partite_saltate_totali": partite_saltate_totali,
            "giorni_stop_totali": giorni_stop_totali,
            "disponibilita_pct": disponibilita_pct,
            "recidive_muscolari": recidive_muscolari,
            "consiglio_medico_ai": consiglio_medico_ai,
            "cronistoria_infortuni": cronistoria_infortuni,
            "is_injured": is_injured,
            "giornate_perse": giornate_perse,
            "is_chronic_fragile": is_chronic_fragile,
            "infortunio_status": infortunio_status,
            "infortunio_motivo": infortunio_motivo,
            "infortunio_rientro": infortunio_rientro,
            "infortunio_severity": infortunio_severity,
            "infortunio_tipo_stop": infortunio_tipo_stop,
            "rigorista_val": rigorista_val,
            "piazzati_val": piazzati_val,
            "oop_val": oop_val,
            "is_rigorista_1": is_rigorista_1,
            "is_rigorista_2": is_rigorista_2,
            "is_rigorista_3": is_rigorista_3,
            "is_punizioni": is_punizioni,
            "is_corner": is_corner,
            "is_oop": is_oop,
            "fpp_fpn": fpp_fpn,
            "pos_label": pos_label,
            "oop_type": oop_type,
            "oop_desc": oop_desc,
            "oop_tier": oop_tier,
            "is_in_11": is_in_11,
            "is_in_ballottaggio": is_in_ballottaggio,
            "pitch_pos": pitch_pos,
            "is_top": is_top,
            "is_sleeper": is_sleeper,
            "is_flop": is_flop,

            # --- ECOSISTEMA SQUADRA (FOTMOB 2026/27) ---
            "team_context": team_context
        }

        xfm_val, delta_xfm_val = calculate_xfm(temp_record)
        temp_record["xfm"] = xfm_val
        temp_record["delta_xfm"] = delta_xfm_val

        processed_players.append(temp_record)

    # Assegna Slotting Definitivo (1°-8° Slot per 8 squadre)
    num_teams = league_settings.get("num_teams", 8)
    processed_players = assign_slots_and_fasce(processed_players, num_teams=num_teams)

    # Calibrazione Economica Rigorosa Budget di Lega (8000 CR per 8 squadre)
    processed_players = calibrate_budget_prices(processed_players, league_settings)

    # Ricalcola Advice AI con Tutte le Metriche e gli Slot Assegnati
    for p in processed_players:
        advice, advice_type = determine_advice_tag(p)
        p["ai_advice"] = advice
        p["ai_advice_type"] = advice_type
        p["consiglio"] = advice

    # Associa a ogni calciatore il suo sostituto naturale / compagno di staffetta e viceversa
    processed_players = compute_substitute_pairings(processed_players, tactical_db, reports_csv)

    # Calcola Griglia Portieri
    gk_data = extract_gk_grid()

    # Salva Output
    proc_dir = os.path.join(ROOT_DIR, "data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    
    out_master_proc = os.path.join(proc_dir, "processed_players_master.json")
    out_gk_proc = os.path.join(proc_dir, "gk_matrix_2026_27.json")
    out_master_root = os.path.join(ROOT_DIR, "processed_players_master.json")
    out_gk_root = os.path.join(ROOT_DIR, "gk_matrix_2026_27.json")

    with open(out_master_proc, "w", encoding="utf-8") as f:
        json.dump(processed_players, f, ensure_ascii=False, indent=2)

    with open(out_gk_proc, "w", encoding="utf-8") as f:
        json.dump(gk_data, f, ensure_ascii=False, indent=2)

    with open(out_master_root, "w", encoding="utf-8") as f:
        json.dump(processed_players, f, ensure_ascii=False, indent=2)

    with open(out_gk_root, "w", encoding="utf-8") as f:
        json.dump(gk_data, f, ensure_ascii=False, indent=2)

    print(f"-> Matchati con FotMob 2025/26: {matched_fotmob_count}/{len(processed_players)} calciatori.")
    print(f"-> Pipeline completata con successo ({len(processed_players)} calciatori processati).")

    # ── AI Evaluator: snapshot T0 o valutazione in-season ──────────────────
    # Rileva la giornata corrente dal massimo voto disponibile
    current_round = 0
    for p in processed_players:
        for v in (p.get('voti_dettaglio_2627') or []):
            g = v.get('giornata', 0)
            if g and g > current_round:
                current_round = g

    # Assicura che lo snapshot T0 sia inizializzato se assente
    save_predictions_snapshot(processed_players, round_num=0)

    if current_round >= 5:
        # T+N: valuta predizioni e aggiorna bias corrections
        evaluate_predictions(processed_players, round_num=current_round)
        try:
            from src.matchday_evaluator import run_learning_and_accuracy_evaluation
            run_learning_and_accuracy_evaluation()
        except Exception as e:
            print(f"[Pipeline] Warning matchday learning evaluation: {e}")
    elif current_round > 0:
        print(f"[AI Evaluator] G{current_round}: dati ancora insufficienti per valutazione (min G5).")
    # ────────────────────────────────────────────────────────────────────────

    return processed_players, gk_data

if __name__ == '__main__':
    run_master_pipeline()

