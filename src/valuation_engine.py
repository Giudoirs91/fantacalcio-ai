import numpy as np
from .player_matcher import clean_text

# ── AI Evaluator bias corrections (lazy-loaded singleton) ────────────────────
# Loaded once per pipeline run; empty dict = no corrections (first season or < G5)
_bias_corrections_cache = None

def _get_bias_corrections():
    """Lazy-loads bias corrections from ai_evaluator. Returns {} if unavailable."""
    global _bias_corrections_cache
    if _bias_corrections_cache is None:
        try:
            from .ai_evaluator import load_bias_corrections
            _bias_corrections_cache = load_bias_corrections()
            if _bias_corrections_cache:
                rounds = _bias_corrections_cache.get('rounds_analyzed', 0)
                mae = _bias_corrections_cache.get('overall_mae', 0)
                print(f"[Valuation Engine] Bias corrections caricate (G{rounds}, MAE={mae:.2f})")
        except Exception:
            _bias_corrections_cache = {}
    return _bias_corrections_cache
# ────────────────────────────────────────────────────────────────────────

def calcola_impatto_infortunio(rientro_str):
    """
    Stima giornate perse considerando la sosta nazionali (20 Set - 10 Ott 2026).
    Ritorna: (giornate_perse, penalita_ovr, moltiplicatore_prezzo)
    """
    if not rientro_str:
        return 0, 0.0, 1.0
    try:
        parts = rientro_str.split('/')
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        
        if year >= 2027:
            if month >= 5: return 35, 16.0, 0.10 # Stagione finita
            elif month >= 3: return 26, 12.0, 0.20
            else: return 19, 9.0, 0.35 # Rientro Gennaio/Febbraio
            
        # Anno 2026
        if month == 12: return 13, 6.0, 0.50 # Dicembre
        elif month == 11: return 10, 4.5, 0.60 # Novembre
        elif month == 10:
            if day <= 12: return 4, 1.8, 0.80 # Rientro subito dopo sosta
            else: return 6, 2.8, 0.70 # Fine Ottobre
        elif month == 9:
            if day <= 7: return 1, 0.5, 0.95
            elif day <= 15: return 2, 0.8, 0.90
            else: return 3, 1.2, 0.85 # Metà/fine Settembre
        else: # Agosto 2026
            return 0, 0.0, 1.0 # Disponibile già per 1ª/2ª giornata
    except Exception:
        return 0, 0.0, 1.0

def compute_continuous_ovr_and_price(role, fvm, is_in_11, team_mult=1.0):
    """
    Modello matematico continuo ad alta risoluzione senza saturazioni.
    """
    fvm = max(1.0, float(fvm))
    
    if role == 'P':
        ovr = 50.0 + (fvm / 65.0) * 38.0 + (1.5 if is_in_11 else 0)
        prezzo_cons = max(1, int(round((fvm / 65.0) * 75 * (0.9 + 0.1 * team_mult))))
    elif role == 'D':
        if fvm >= 150:
            ovr = 95.0 + (fvm - 150) / 150.0 * 1.5
            prezzo_cons = int(round(105 + (fvm - 150) * 0.40))
        elif fvm >= 70:
            ovr = 87.0 + (fvm - 70) / 80.0 * 6.0
            prezzo_cons = int(round(50 + (fvm - 70) * 0.70))
        elif fvm >= 30:
            ovr = 78.0 + (fvm - 30) / 40.0 * 8.0
            prezzo_cons = int(round(15 + (fvm - 30) * 0.60))
        elif fvm >= 15:
            ovr = 70.0 + (fvm - 15) / 15.0 * 7.0
            prezzo_cons = int(round(5 + (fvm - 15) * 0.65))
        else:
            ovr = max(48.0, 50.0 + (fvm / 15.0) * 19.0)
            prezzo_cons = max(1, int(round(1 + (fvm / 15.0) * 3)))
    elif role == 'C':
        if fvm >= 220:
            ovr = 94.0 + (fvm - 220) / 30.0 * 2.0
            prezzo_cons = int(round(140 + (fvm - 220) * 0.8))
        elif fvm >= 140:
            ovr = 89.0 + (fvm - 140) / 80.0 * 4.5
            prezzo_cons = int(round(90 + (fvm - 140) * 0.6))
        elif fvm >= 80:
            ovr = 81.0 + (fvm - 80) / 60.0 * 7.0
            prezzo_cons = int(round(50 + (fvm - 80) * 0.65))
        elif fvm >= 45:
            ovr = 73.0 + (fvm - 45) / 35.0 * 7.0
            prezzo_cons = int(round(20 + (fvm - 45) * 0.85))
        elif fvm >= 20:
            ovr = 65.0 + (fvm - 20) / 25.0 * 7.0
            prezzo_cons = int(round(7 + (fvm - 20) * 0.52))
        else:
            ovr = max(48.0, 50.0 + (fvm / 20.0) * 14.0)
            prezzo_cons = max(1, int(round(1 + (fvm / 20.0) * 5)))
    else: # 'A'
        if fvm >= 400:
            ovr = 96.0 + min(2.0, (fvm - 400) / 300.0 * 2.0)
            prezzo_cons = int(round(430 + (fvm - 400) * 0.35))
        elif fvm >= 250:
            ovr = 91.0 + (fvm - 250) / 150.0 * 5.0
            prezzo_cons = int(round(250 + (fvm - 250) * 1.20))
        elif fvm >= 150:
            ovr = 85.0 + (fvm - 150) / 100.0 * 6.0
            prezzo_cons = int(round(145 + (fvm - 150) * 1.05))
        elif fvm >= 70:
            ovr = 77.0 + (fvm - 70) / 80.0 * 8.0
            prezzo_cons = int(round(60 + (fvm - 70) * 1.05))
        elif fvm >= 25:
            ovr = 67.0 + (fvm - 25) / 45.0 * 10.0
            prezzo_cons = int(round(15 + (fvm - 25) * 1.0))
        else:
            ovr = max(48.0, 50.0 + (fvm / 25.0) * 17.0)
            prezzo_cons = max(1, int(round(1 + (fvm / 25.0) * 10)))

    # Applicazione leggera team multiplier sull'OVR
    ovr += (team_mult - 1.0) * 2.0

    return ovr, prezzo_cons

def determine_advice_tag(p):
    """
    Determina il consiglio AI strategico e la classe CSS basandosi sulla combinazione
    multidimensionale di:
    - Titolarità % e status negli 11 / Ballottaggi
    - Slot d'asta (1° Slot fino a Riserva)
    - Indice di Fragilità Fisica e Infortunio attuale
    - Ruolo Fuori Ruolo (OOP con gerarchia ORO / ARGENTO / BRONZO)
    - Status Rigorista (1°, 2°, 3°) e Tiratore di Piazzati
    - Fantamedia (FM) e Media Voto (MV) 2025/2026
    - OVR e Prezzo Consigliato (CR)
    - Cautela sulle prime 2 giornate 2026/2027 (usate come bonus o sleeper alert)
    """
    ovr = p.get('ovr', 50)
    role = p.get('role', '')
    prezzo_cons = p.get('prezzo_cons', 1)
    slot_num = p.get('slot_num', 5)
    titolarita = p.get('titolarita', 50)
    is_in_11 = p.get('is_in_11', False)
    is_in_ballottaggio = p.get('is_in_ballottaggio', False)
    
    is_injured = p.get('is_injured', False)
    giornate_perse = p.get('giornate_perse', 0)
    fragilita_score = p.get('fragilita_score', 1)  # 1=bassa, 2=media, 3=alta
    fragilita_badge = p.get('fragilita_badge', 'bassa')
    is_chronic_fragile = p.get('is_chronic_fragile', False)
    
    oop_tier = p.get('oop_tier', '')  # ORO, ARGENTO, BRONZO
    is_oop = p.get('is_oop', False)
    
    is_rigorista_1 = p.get('is_rigorista_1', False)
    is_rigorista_2 = p.get('is_rigorista_2', False)
    is_punizioni = p.get('is_punizioni', False)
    is_corner = p.get('is_corner', False)
    
    is_top = p.get('is_top', False)
    is_sleeper = p.get('is_sleeper', False)
    is_flop = p.get('is_flop', False)
    
    fm_2526 = p.get('fm', 0.0)
    mv_2526 = p.get('mv', 0.0)
    
    # Dati 2026/27 (con prudenza)
    has_data_2627 = p.get('has_data_2627', False)
    gol_2627 = p.get('gol_2627', 0)
    assist_2627 = p.get('assist_2627', 0)
    presenze_2627 = p.get('presenze_2627', 0)

    # 1. INFORTUNI GRAVI / LUNGA DEGENZA (Priorità 1 Assoluta)
    motivo_inf = str(p.get('infortunio_motivo', '')).lower()
    if is_injured and (giornate_perse >= 10 or 'mesi' in motivo_inf or 'crociato' in motivo_inf or 'operazione' in motivo_inf):
        return "⛔ LUNGA DEGENZA (EVITARE)", "avoid"
    if is_injured and titolarita < 40:
        return "⚠️ INFORTUNATO (NON COMPRARE)", "avoid"
    if is_injured and (slot_num <= 2 or ovr >= 82):
        return "⚠️ INFORTUNATO (TOP DA SCONTO)", "warning"
    if is_injured:
        return "⚠️ INFORTUNATO (ATTENDERE RIENTRO)", "warning"

    # 2. TOP PLAYER ASSOLUTI (1° Slot / OVR 90+)
    if ovr >= 92 or (slot_num == 1 and (ovr >= 88 or fm_2526 >= 7.8)):
        if is_rigorista_1:
            return "👑 1° RIGORISTA & TOP ASSOLUTO", "top"
        if (fragilita_score >= 3 or fragilita_badge == 'alta' or is_chronic_fragile):
            return "👑 TOP DI REPARTO (CON COPERTURA)", "top"
        return "👑 TOP PLAYER ASSOLUTO", "top"

    # 3. TOP DI VETRO (Fortissimo ma con storico infortuni gravoso)
    if (fragilita_score >= 3 or fragilita_badge == 'alta' or is_chronic_fragile) and (slot_num <= 2 or ovr >= 82):
        return "⚠️ TOP DI VETRO (CON COPERTURA)", "warning"

    # 4. FLOP PREVISTI & REGRESSIONE GRAVE (Priorità su bonus minori)
    if is_flop:
        return "⚠️ POSSIBILE FLOP (SOPRAVVALUTATO)", "flop"

    # 5. FUORI RUOLO D'ORO (Super King Power: Quinti a tutta fascia e Ali d'attacco quotate C)
    if oop_tier == 'ORO':
        if role == 'D':
            if slot_num <= 2 or is_in_11 or titolarita >= 75:
                return "🥇 SUPER QUINTO A 3 (ORO PURO)", "buy"
            return "🥇 QUINTO D'ORO (DA PRENDERE)", "buy"
        elif role == 'C':
            if slot_num <= 2 or is_in_11 or titolarita >= 75:
                return "🥇 ALA/SECONDA PUNTA (TOP OOP)", "buy"
            return "🥇 ESTERNO D'ATTACCO OOP", "buy"

    # 6. FUORI RUOLO D'ARGENTO (Trequartisti d'incursione C e Terzini di spinta D)
    if oop_tier == 'ARGENTO':
        if role == 'C':
            if slot_num <= 3 or titolarita >= 75:
                return "🥈 TREQUARTISTA D'INCURSIONE (OOP)", "buy"
            return "🥈 TREQUARTISTA INSERIMENTI", "buy"
        elif role == 'D':
            return "🥈 TERZINO DI SPINTA (OOP)", "buy"

    # 7. RIGORISTI DI SQUADRA
    if is_rigorista_1:
        if role in ['D', 'C']:
            return "🎯 RIGORISTA & BONUS MAN (+3)", "leader"
        if titolarita >= 75:
            return "🎯 1° RIGORISTA DI SQUADRA", "leader"

    # 8. SPECIALISTI PIAZZATI & LEADER
    if (is_punizioni and is_corner) and titolarita >= 75 and (slot_num <= 4 or ovr >= 74):
        return "🚀 SPECIALISTA PIAZZATI & ASSIST", "buy"

    if is_top or (slot_num == 2 and titolarita >= 75):
        return "⭐ 2° SLOT / TITOLARE DI LUSSO", "leader"

    # 9. SLEEPER & SCOMMESSE CONFERMATE
    if is_sleeper or (has_data_2627 and (gol_2627 >= 1 or assist_2627 >= 1) and prezzo_cons <= 15 and titolarita >= 65 and presenze_2627 >= 2):
        return "🔥 SCOMMESSA / SLEEPER", "sleeper"

    # 10. FUORI RUOLO BRONZO (Riserve con ruolo offensivo a 1 credito)
    if oop_tier == 'BRONZO':
        return "🥉 RISERVA D'ORO A 1 CR", "sleeper"

    # 10b. SUPER-SUB / JOLLY DA VOTO (Presenza garantita a gara in corso con voto/minutaggio)
    if presenze_2627 >= 3 and titolarita < 65 and not is_injured:
        if (p.get('gol_2627', 0) >= 1 or p.get('assist_2627', 0) >= 1 or p.get('mv_2627', 0) >= 6.0):
            return "⚡ SUPER-SUB / JOLLY DA VOTO", "supersub"

    # 11. OTTIMI TITOLARI & MODIFICATORE DIFESA / LOW COST
    if slot_num == 3 and titolarita >= 80:
        return "💎 OTTIMO 3° SLOT TITOLARE", "buy"

    if role == 'D' and titolarita >= 80 and prezzo_cons <= 10 and (mv_2526 >= 6.05 or ovr >= 70):
        return "🛡️ LOW COST DA MODIFICATORE", "lowcost"

    if role == 'C' and titolarita >= 80 and prezzo_cons <= 10:
        return "🛡️ TITOLARE LOW COST DA VOTO", "lowcost"

    if titolarita >= 85 and is_in_11:
        return "🔒 TITOLARISSIMO DA VOTO", "titolarissimo"

    # 12. BALLOTTAGGI & ROTAZIONI
    if is_in_ballottaggio or (titolarita >= 55 and titolarita < 78):
        return "🔄 ROTAZIONE / BALLOTTAGGIO", "rotation"

    # 13. PANCHINARI & SCARTI
    if titolarita >= 35 and titolarita < 55:
        return "🪑 RISERVA DA SLOT 1 CR", "lowcost"

    if ovr <= 52 or titolarita < 35 or p.get('fvm', 1) <= 1:
        return "⛔ DA EVITARE / RISERVA", "avoid"

    if titolarita >= 70:
        return "🔒 TITOLARE DA VOTO", "titolarissimo"

    return "🔄 ROTAZIONE", "rotation"

def assign_slots_and_fasce(players_list, num_teams=8):
    """
    Assegna gli slot (1°-8° Slot per 8 squadre) e le fasce di mercato.
    """
    by_role = {'P': [], 'D': [], 'C': [], 'A': []}
    for p in players_list:
        by_role[p['role']].append(p)

    max_slots_role = {'P': 3, 'D': 8, 'C': 8, 'A': 6}

    for r, r_players in by_role.items():
        r_players.sort(key=lambda x: (-x['ovr'], -x['prezzo_cons'], -x['fvm']))
        max_s = max_slots_role[r]
        for rank, pl in enumerate(r_players, 1):
            slot_num = ((rank - 1) // num_teams) + 1
            pl['slot_num'] = slot_num
            if slot_num <= max_s:
                pl['slot_fascia'] = f"{slot_num}° Slot {r}"
            else:
                pl['slot_fascia'] = f"Riserva {r}"

    players_list.sort(key=lambda x: (x['role'], x['slot_num'], -x['ovr'], -x['prezzo_cons']))
    return players_list

def calibrate_budget_prices(players_list, league_settings):
    """
    Calibra rigorosamente i prezzi consigliati (prezzo_cons) e max_bid affinché la somma
    dei calciatori necessari a completare tutte le rose (es. 200 calciatori per 8 squadre)
    rispecchi esattamente il montepremi totale di lega (es. 8000 CR per 8 squadre x 1000 CR)
    e i target percentuali per reparto definiti in league_settings.json.
    """
    num_teams = league_settings.get("num_teams", 8)
    total_budget_per_team = league_settings.get("total_budget", 1000)
    total_league_budget = num_teams * total_budget_per_team
    slots_cfg = league_settings.get("slots", {
        "P": {"max": 3, "budget_target_pct": 0.07},
        "D": {"max": 8, "budget_target_pct": 0.11},
        "C": {"max": 8, "budget_target_pct": 0.22},
        "A": {"max": 6, "budget_target_pct": 0.60}
    })

    role_targets = {
        'P': int(round(total_league_budget * slots_cfg.get('P', {}).get('budget_target_pct', 0.07))),
        'D': int(round(total_league_budget * slots_cfg.get('D', {}).get('budget_target_pct', 0.11))),
        'C': int(round(total_league_budget * slots_cfg.get('C', {}).get('budget_target_pct', 0.22))),
        'A': int(round(total_league_budget * slots_cfg.get('A', {}).get('budget_target_pct', 0.60)))
    }
    
    # Bilanciamento esatto su total_league_budget
    diff_tot = total_league_budget - sum(role_targets.values())
    if diff_tot != 0:
        role_targets['A'] += diff_tot

    role_caps = {'P': 95, 'D': 125, 'C': 185, 'A': 680}
    max_slots_role = {'P': slots_cfg.get('P', {}).get('max', 3),
                      'D': slots_cfg.get('D', {}).get('max', 8),
                      'C': slots_cfg.get('C', {}).get('max', 8),
                      'A': slots_cfg.get('A', {}).get('max', 6)}

    by_role = {'P': [], 'D': [], 'C': [], 'A': []}
    for p in players_list:
        by_role[p['role']].append(p)

    for r, r_players in by_role.items():
        r_players.sort(key=lambda x: (-x['ovr'], -x['prezzo_cons'], -x['fvm']))
        k_draftable = num_teams * max_slots_role[r]
        target = role_targets[r]
        cap = role_caps[r]

        top_p = r_players[:k_draftable]
        bench_p = r_players[k_draftable:]

        for p in bench_p:
            p['prezzo_cons'] = 1
            p['max_bid'] = 2

        # Ponderazione calibrata su 5 aste reali (legge di potenza per evidenziare i top di reparto)
        scores = []
        for p in top_p:
            ovr_excess = max(1.0, float(p['ovr'] - 55))
            p_raw = max(1.0, float(p['prezzo_cons']))
            if r == 'A':
                score = (p_raw ** 1.20) * (ovr_excess ** 0.45)
            elif r == 'D':
                score = (p_raw ** 1.20) * (ovr_excess ** 0.45)
            elif r == 'C':
                score = (p_raw ** 1.10) * (ovr_excess ** 0.40)
            else: # 'P'
                score = (p_raw ** 1.02) * (ovr_excess ** 0.35)
            scores.append(score)

        sum_scores = sum(scores) if sum(scores) > 0 else 1.0
        discretionary = max(0, target - k_draftable)

        for i, p in enumerate(top_p):
            alloc = 1 + int(round(discretionary * (scores[i] / sum_scores)))
            p['prezzo_cons'] = min(cap, max(1, alloc))

        # Aggiustamento fine del delta di arrotondamento
        diff = target - sum(p['prezzo_cons'] for p in top_p)
        attempts = 0
        while diff != 0 and attempts < len(top_p) * 2:
            idx = attempts % len(top_p)
            if diff > 0:
                if top_p[idx]['prezzo_cons'] < cap:
                    top_p[idx]['prezzo_cons'] += 1
                    diff -= 1
            elif diff < 0:
                rev_idx = -(idx + 1)
                if top_p[rev_idx]['prezzo_cons'] > 1:
                    top_p[rev_idx]['prezzo_cons'] -= 1
                    diff += 1
            attempts += 1

        for p in top_p:
            p['max_bid'] = min(int(round(cap * 1.15)), max(p['prezzo_cons'] + 1, int(round(p['prezzo_cons'] * 1.15))))

    # Riordina finale
    players_list.sort(key=lambda x: (x['role'], x.get('slot_num', 1), -x['ovr'], -x['prezzo_cons']))
    return players_list


def calculate_xfm(p):
    """
    Calcola l'Expected FantaMedia (xFM) e il Delta di Performance (FM - xFM).
    Se le bias corrections sono disponibili (da G5 in poi), le applica per migliorare
    la precisione della predizione basandosi sugli errori delle stagioni precedenti.
    Restituisce (xfm, delta_xfm) arrotondati a 2 decimali.
    """
    has_2627 = bool(p.get('has_data_2627') and (p.get('presenze_2627') or 0) > 0)
    presenze = float(p.get('presenze_2627') or p.get('presenze') or 1)
    if presenze <= 0:
        presenze = 1.0
    
    mv = p.get('mv_2627') if (has_2627 and p.get('mv_2627') is not None) else p.get('mv', 6.0)
    mv = float(mv) if (mv is not None and mv > 0) else 6.0
        
    real_fm = p.get('fm_2627') if (has_2627 and p.get('fm_2627') is not None) else p.get('fm', mv)
    real_fm = float(real_fm) if (real_fm is not None and real_fm > 0) else mv

    role = p.get('role', 'C')
    if role == 'P':
        gs = float(p.get('gol_subiti_2627') or p.get('gs') or 0.0)
        cs = float(p.get('clean_sheets_2627') or p.get('clean_sheets_2526') or 0.0)
        xfm_base = round(float(mv - (gs / presenze) + (cs * 0.5 / presenze)), 2)
    else:
        if has_2627:
            xg = p.get('xg_2627')
            if xg is None:
                xg90 = float(p.get('xg90_2627') or 0.0)
                mins = float(p.get('minuti_2627') or 90.0)
                xg = xg90 * (mins / 90.0)
            xa = p.get('xa_2627')
            if xa is None:
                xa90 = float(p.get('xa90_2627') or 0.0)
                mins = float(p.get('minuti_2627') or 90.0)
                xa = xa90 * (mins / 90.0)
            amm = float(p.get('amm_2627') or 0.0)
            esp = float(p.get('esp_2627') or 0.0)
        else:
            xg = p.get('xg_2526')
            if xg is None:
                xg90 = float(p.get('xg90_2526') or 0.0)
                mins = float(p.get('mins_2526') or 900.0)
                xg = xg90 * (mins / 90.0)
            xa = p.get('xa_2526')
            if xa is None:
                xa90 = float(p.get('xa90_2526') or 0.0)
                mins = float(p.get('mins_2526') or 900.0)
                xa = xa90 * (mins / 90.0)
            amm = float(p.get('amm') or 0.0)
            esp = float(p.get('esp') or 0.0)

        xg = float(xg or 0.0)
        xa = float(xa or 0.0)
        malus = amm * 0.5 + esp * 1.0

        # Finishing / Shot Placement Index (xGOT vs xG per valutare la qualità delle conclusioni)
        xgot = p.get('xgot_2627') if p.get('xgot_2627') is not None else p.get('xgot_2526')
        shot_placement_mult = 1.0
        if role in ['A', 'C'] and xgot is not None and xg >= 0.8:
            try:
                raw_ratio = float(xgot) / float(xg)
                # Clampa delicatamente il moltiplicatore tra 0.90 (tiratore poco cinico) e 1.10 (finisher chirurgico)
                shot_placement_mult = max(0.90, min(1.10, raw_ratio))
            except (ZeroDivisionError, ValueError):
                shot_placement_mult = 1.0

        bonus_attesi = (xg * shot_placement_mult * 3.0) + (xa * 1.0)
        xfm_base = round(float(mv + ((bonus_attesi - malus) / presenze)), 2)

    # ── Applica bias corrections apprese dall'AI Evaluator (non-distruttive) ────────
    corrections = _get_bias_corrections()
    if corrections:
        try:
            from .ai_evaluator import apply_bias_correction_to_xfm
            xfm = apply_bias_correction_to_xfm(xfm_base, p, corrections)
        except Exception:
            xfm = xfm_base
    else:
        xfm = xfm_base
    # ────────────────────────────────────────────────────────────────────────

    delta = round(float(real_fm - xfm), 2)
    return xfm, delta
