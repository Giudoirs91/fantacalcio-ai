"""
advanced_metrics.py - Motore Statistico Avanzato Fanta Master AI
Implementa le 4 metriche avanzate predittive per la Serie A 2026/27:
1. Floor vs Ceiling (Rischio/Rendimento & Volatilità Fantavoto)
2. Matchup Vulnerability (Incrocio Tattico Asimmetrico difese avversarie)
3. Trade Evaluator AI (Valutatore Matematico di Scambi)
4. Indice di Impatto da Subentro (Super-Sub & Probabilità Voto)
"""

import os
import json
import math
import numpy as np

def compute_floor_and_ceiling(player):
    """
    Calcola il Floor (voto minimo atteso in partita difficile/senza bonus)
    e il Ceiling (massimo potenziale esplosivo con bonus multipli).
    """
    role = player.get("role", "C")
    mv = float(player.get("mv_2627") or player.get("mv") or 6.0)
    fm = float(player.get("fm_2627") or player.get("fm") or 6.0)
    xfm = float(player.get("xfm") or fm or 6.0)
    
    # Dati statistici 26/27 e 25/26
    xg = float(player.get("xg_2627") or player.get("xg90_2526") or 0.0)
    xa = float(player.get("xa_2627") or player.get("xa90_2526") or 0.0)
    shots = float(player.get("tiri_2627") or player.get("shots90_2526") or 0.0)
    
    is_rig = bool(player.get("is_rigorista_1") or player.get("is_rigorista_2"))
    is_piazzati = bool(player.get("is_punizioni") or player.get("is_corner"))
    is_oop = bool(player.get("is_oop"))
    
    # Amm / Malus trend
    amm_count = float(player.get("amm_2627") or player.get("amm") or 0)
    presenze = max(1, float(player.get("partite_voto_2627") or player.get("presenze") or 1))
    amm_rate = min(0.6, amm_count / presenze)
    
    # 1. CALCOLO FLOOR (Rendimento minimo in giornata no / senza bonus)
    if role == 'P':
        # Per i portieri il floor dipende dai gol subiti attesi
        gs_match = float(player.get("team_context", {}).get("goals_conceded_match_team") or 1.1)
        floor = max(3.5, round(mv - (gs_match * 0.7) - (amm_rate * 0.5), 1))
    elif role == 'D':
        # Difensore: regolarità contratti, malus e cartellini
        floor = max(4.5, round(mv - 0.35 - (amm_rate * 0.6), 1))
    elif role == 'C':
        # Centrocampista
        floor = max(4.8, round(mv - 0.40 - (amm_rate * 0.5), 1))
    else: # 'A'
        # Attaccante a secco: spesso voto 5.0 o 5.5
        floor = max(5.0, round(mv - 0.55 - (amm_rate * 0.4), 1))
        
    # 2. CALCOLO CEILING (Potenziale esplosivo massimo in giornata di grazia)
    if role == 'P':
        # Clean sheet (+1) + parate decisive (+0.5/1.0) + potenziale rigore parato (+3)
        ceiling = min(10.0, round(mv + 1.0 + (0.5 if mv >= 6.3 else 0.0), 1))
    elif role == 'D':
        # Difensore goleador / assistman (es. Dimarco, Wesley)
        bonus_up = 3.0 if (xg >= 0.08 or is_oop) else (1.5 if xa >= 0.08 else 0.5)
        cs_bonus = 1.0 # Modificatore difesa
        ceiling = min(13.0, round(mv + bonus_up + cs_bonus, 1))
    elif role == 'C':
        # Centrocampista con gol + assist o rigore
        rig_boost = 3.0 if is_rig else 0.0
        att_boost = 3.0 if (xg >= 0.15 or is_oop) else (1.5 if is_piazzati else 1.0)
        ceiling = min(15.5, round(mv + rig_boost + att_boost + 0.5, 1))
    else: # 'A'
        # Attaccante: doppietta / tripletta + assist
        multi_goal = 6.0 if xfm >= 7.8 else 3.0
        rig_boost = 3.0 if is_rig else 0.0
        ceiling = min(18.0, round(mv + multi_goal + rig_boost + (1.0 if xa >= 0.15 else 0.0), 1))

    # Garanzia Floor <= Ceiling
    ceiling = max(floor + 1.5, ceiling)
    spread = round(ceiling - floor, 1)

    # 3. PROFILAZIONE E VOLATILITÀ
    if spread >= 7.0:
        volatility_label = "ESPLOSIVA"
        tactical_profile = "🚀 Alto Potenziale (Exploit Bonus)"
        tactical_advice = f"Base minima {floor} / Potenziale max {ceiling}: da schierare quando hai bisogno di bonus pesanti per vincere la giornata."
    elif spread <= 4.2:
        volatility_label = "BASSA"
        tactical_profile = "🛡️ Base Solida (Rendimento Costante)"
        tactical_advice = f"Base minima {floor} / Potenziale max {ceiling}: eccellente certezza di rendimento e modificatore, pochissimi rischi di insufficienza."
    else:
        volatility_label = "MEDIA"
        tactical_profile = "⚖️ Rendimento Bilanciato"
        tactical_advice = f"Base minima {floor} / Potenziale max {ceiling}: solido equilibrio tra sufficienza garantita e buone chance di bonus."

    return {
        "floor": floor,
        "ceiling": ceiling,
        "spread": spread,
        "volatility_label": volatility_label,
        "tactical_profile": tactical_profile,
        "tactical_advice": tactical_advice
    }


def compute_sub_impact_metrics(player, tactical_db=None):
    """
    Calcola l'Indice di Impatto da Subentro (Super-Sub) e la probabilità di voto
    nel caso in cui il calciatore non parta negli 11 titolari.
    """
    titolarita = int(player.get("titolarita") or 50)
    presenze_2627 = int(player.get("presenze_2627") or 0)
    starts_2627 = int(player.get("starts_2627") or 0)
    fvm = float(player.get("fvm") or 1.0)
    ovr = int(player.get("ovr") or 70)
    role = player.get("role", "C")
    is_injured = bool(player.get("is_injured"))

    # Sostituzioni effettive rilevate nel 2026/27
    subs_on_count = max(0, presenze_2627 - starts_2627)
    
    # 1. PROBABILITÀ DI VOTO SE IN PANCHINA (sub_vote_prob)
    if is_injured:
        sub_vote_prob = 5
        sub_badge = "🩺 INFORTUNATO"
        sub_verdict = "Attualmente indisponibile per infortunio."
    elif titolarita >= 85:
        # Titolare quasi fisso: se per caso va in panca (turnover), entra quasi al 100%
        sub_vote_prob = 92
        sub_badge = "👑 TITOLARE FISSO"
        sub_verdict = "Titolare indiscusso. In caso di turnover parte quasi sempre primo cambio al 60'."
    elif titolarita >= 65:
        # Ballottaggio frequente
        sub_vote_prob = 84
        sub_badge = "⚡ SUPER-SUB ORO"
        sub_verdict = "Staffetta costante: entra a voto in oltre l'80% delle gare da panchinaro."
    elif titolarita >= 40:
        # Rotazione tipica (12°-14° uomo)
        sub_vote_prob = 72
        sub_badge = "🔄 ROTAZIONE SICURA"
        sub_verdict = "Primo cambio designato del reparto: buon minutaggio garantito nella ripresa."
    elif fvm >= 15 or ovr >= 74:
        # Giocatore di qualità relegato in panchina (es. vice-top)
        sub_vote_prob = 55
        sub_badge = "⚠️ JOLLY A RISCHIO"
        sub_verdict = "Ingresso legato all'inerzia della gara. Coprirsi con un titolare fisso."
    else:
        # Riserva profonda
        sub_vote_prob = 22
        sub_badge = "❌ RISCHIO S.V."
        sub_verdict = "Minutaggio ridotto ai margini delle rotazioni, alto rischio Senza Voto."

    # 2. INDICE DI IMPATTO BONUS DA SUBENTRATO (sub_impact_score 0-100)
    # Misura la pericolosità nei 25-30 minuti finali contro difese stanche
    base_impact = 40
    if role == 'A':
        base_impact += 25
    elif role == 'C':
        base_impact += 15
    elif role == 'D':
        base_impact += 5
        
    if player.get("is_oop"):
        base_impact += 10
    if float(player.get("xg_2627") or 0.0) >= 0.15:
        base_impact += 15
    if ovr >= 80:
        base_impact += 10

    sub_impact_score = min(98, max(15, base_impact))

    return {
        "sub_vote_prob": sub_vote_prob,
        "sub_impact_score": sub_impact_score,
        "subs_on_count": subs_on_count,
        "super_sub_badge": sub_badge,
        "sub_verdict": sub_verdict
    }


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHED_TACTICAL_DB = None
_CACHED_POSITIONAL_STATS = None

def _get_tactical_db():
    global _CACHED_TACTICAL_DB
    if _CACHED_TACTICAL_DB is None:
        p = os.path.join(ROOT_DIR, "config", "tactical_db.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    _CACHED_TACTICAL_DB = json.load(f)
            except Exception:
                _CACHED_TACTICAL_DB = {}
        else:
            _CACHED_TACTICAL_DB = {}
    return _CACHED_TACTICAL_DB

def _get_positional_stats():
    global _CACHED_POSITIONAL_STATS
    if _CACHED_POSITIONAL_STATS is None:
        p = os.path.join(ROOT_DIR, "config", "team_positional_stats.json")
        if not os.path.exists(p):
            p = os.path.join(ROOT_DIR, "config", "whoscored_teams_2627.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    _CACHED_POSITIONAL_STATS = json.load(f)
            except Exception:
                _CACHED_POSITIONAL_STATS = {}
        else:
            _CACHED_POSITIONAL_STATS = {}
    return _CACHED_POSITIONAL_STATS


def compute_matchup_vulnerability(player, calendar_data, team_stats_dict, current_round=8, tactical_db=None, positional_stats_dict=None, players_master=None):
    """
    Calcola l'incrocio tattico asimmetrico per la prossima giornata (G8):
    1. Flank Duel: incrocio corsia d'attacco del giocatore (% volume di squadra)
       con la debolezza specifica del terzino/braccetto rivale (Media Voto, falli, titolarità).
    2. Zone di Campo: distribuzione conclusioni (6 yard box, penalty area, tiri da fuori)
       incrociate con la percentuale di tempo in cui l'avversario è schiacciato nel proprio terzo.
    3. Vulnerability Score & Badge di Corsia / Reparto.
    """
    team_name = (player.get("team") or "").strip()
    role = player.get("role", "C")
    pname = player.get("name", "Giocatore")
    
    if tactical_db is None:
        tactical_db = _get_tactical_db()
    if positional_stats_dict is None:
        positional_stats_dict = _get_positional_stats()

    # Trova partita turno indicato nel calendario (default G8)
    next_match = None
    if calendar_data:
        r_obj = next((r for r in calendar_data if r.get('giornata') == current_round), None)
        if not r_obj:
            r_obj = next((r for r in calendar_data if r.get('matches')), None)
            
        if r_obj and r_obj.get('matches'):
            for m in r_obj['matches']:
                h = (m.get('home') or '').strip()
                a = (m.get('away') or '').strip()
                if h.upper() == team_name.upper():
                    next_match = {'opponent': a, 'is_home': True, 'match_str': f"{h} vs {a}"}
                    break
                elif a.upper() == team_name.upper():
                    next_match = {'opponent': h, 'is_home': False, 'match_str': f"{a} @ {h}"}
                    break

    if not next_match:
        return {
            "opponent": "N/D",
            "is_home": True,
            "match_str": f"Partita G{current_round}",
            "vulnerability_score": 50,
            "vulnerability_badge": "🟢 MATCHUP NORMALE",
            "favorable_traits": [],
            "matchup_advice": "Incrocio tattico equilibrato per la prossima giornata.",
            "flank_matchup": {},
            "zone_stats": {}
        }

    opp_name = next_match['opponent']
    opp_stats = team_stats_dict.get(opp_name, {}) if isinstance(team_stats_dict, dict) else {}
    
    # -------------------------------------------------------------
    # 1. DETERMINAZIONE CORSIA D'ATTACCO DEL GIOCATORE
    # -------------------------------------------------------------
    pitch_pos = (player.get("pitch_pos") or "").upper().strip()
    pos_label = (player.get("pos_label") or "").strip()
    mantra = (player.get("mantra_role") or "").strip()

    if pitch_pos in ['AS', 'ES', 'TS', 'CS', 'SS'] or any(k in pos_label.upper() for k in ['SINISTRA', 'SX']) or pos_label.upper().endswith(' S'):
        side_code = 'LEFT'
        side_label = 'Corsia Sinistra'
    elif pitch_pos in ['AD', 'ED', 'TD', 'CD'] or any(k in pos_label.upper() for k in ['DESTRA', 'DX']) or pos_label.upper().endswith(' D'):
        side_code = 'RIGHT'
        side_label = 'Corsia Destra'
    else:
        side_code = 'CENTER'
        side_label = 'Corridoio Centrale'

    if side_code == 'CENTER' and ('W' in mantra or 'E' in mantra):
        if 'TS' in pos_label or 'SX' in pos_label:
            side_code = 'LEFT'
            side_label = 'Corsia Sinistra'
        elif 'TD' in pos_label or 'DX' in pos_label:
            side_code = 'RIGHT'
            side_label = 'Corsia Destra'

    # -------------------------------------------------------------
    # 2. INCIDENZA OFFENSIVA DELLA CORSIA (IMAGE 1: ATTACK SIDES)
    # -------------------------------------------------------------
    my_pos = positional_stats_dict.get(team_name, {})
    att_sides = my_pos.get('attack_sides', {})
    
    left_pct = int(att_sides.get('left_pct', 35))
    middle_pct = int(att_sides.get('middle_pct', 28))
    right_pct = int(att_sides.get('right_pct', 37))
    
    if side_code == 'LEFT':
        flank_attack_pct = left_pct
    elif side_code == 'RIGHT':
        flank_attack_pct = right_pct
    else:
        flank_attack_pct = middle_pct

    # -------------------------------------------------------------
    # 3. INCROCIO CON IL DIFENSORE AVVERSARIO DIRETTO
    # -------------------------------------------------------------
    # Regola Tattica: chi attacca a SINISTRA affronta il terzino/braccetto DESTRO avversario (TD, ED, DC_D).
    # Chi attacca a DESTRA affronta il terzino/braccetto SINISTRO avversario (TS, ES, DC_S).
    # Chi attacca al CENTRO affronta i centrali (DC, DC_C).
    opp_lineup = tactical_db.get(opp_name, {}).get('lineup', [])
    opp_def_entry = None

    if side_code == 'LEFT':
        target_roles = ['TD', 'ED', 'DC_D']
        opp_def_entry = next((lp for lp in opp_lineup if lp.get('pos') in target_roles), None)
    elif side_code == 'RIGHT':
        target_roles = ['TS', 'ES', 'DC_S']
        opp_def_entry = next((lp for lp in opp_lineup if lp.get('pos') in target_roles), None)
    else:
        target_roles = ['DC', 'DC_C', 'DC_D', 'DC_S']
        opp_def_entry = next((lp for lp in opp_lineup if lp.get('pos') in target_roles), None)

    if not opp_def_entry and opp_lineup:
        opp_def_entry = next((lp for lp in opp_lineup if lp.get('role') == 'D'), opp_lineup[0])

    opp_def_name = opp_def_entry.get('name', f"Difensore del {opp_name}") if opp_def_entry else f"Difensore del {opp_name}"
    opp_def_role_label = opp_def_entry.get('pos_label', 'Difensore') if opp_def_entry else 'Difensore'
    opp_def_pos = opp_def_entry.get('pos', 'D') if opp_def_entry else 'D'
    opp_def_sub = opp_def_entry.get('sub_name', '') if opp_def_entry else ''

    # Cerca statistiche reali del difensore rivale
    def_mv = 5.95
    def_fm = 5.90
    def_fouls = 0
    def_tit = 80
    if players_master and isinstance(players_master, list):
        clean_target = opp_def_name.strip().lower()
        matched_def = next((p for p in players_master if p.get('name', '').strip().lower() == clean_target or clean_target in p.get('name', '').strip().lower()), None)
        if matched_def:
            def_mv = round(float(matched_def.get('mv_2627') or matched_def.get('mv') or 5.95), 2)
            def_fm = round(float(matched_def.get('fm_2627') or matched_def.get('fm') or 5.90), 2)
            def_fouls = int(matched_def.get('fouls_2627') or 0)
            def_tit = int(matched_def.get('titolarita') or 80)

    # Valutazione debolezza terzino/braccetto rivale
    if def_mv < 5.85 or def_tit < 60:
        def_weakness = 'ALTA'
        def_weakness_badge = '⚠️ DEFENSOR VULNERABILE'
        def_desc = f"{opp_def_name} ({opp_def_role_label}, MV {def_mv}) soffre in 1vs1 e tenuta"
    elif def_mv <= 6.10:
        def_weakness = 'MEDIA'
        def_weakness_badge = '⚖️ TENUTA MEDIA'
        def_desc = f"{opp_def_name} ({opp_def_role_label}, MV {def_mv}) garantisce rendimento ordinato"
    else:
        def_weakness = 'BASSA'
        def_weakness_badge = '🧱 MURO DIFENSIVO'
        def_desc = f"{opp_def_name} ({opp_def_role_label}, MV {def_mv}) solido e attento"

    # -------------------------------------------------------------
    # 4. ZONE DI CAMPO PER TIRI E AZIONI OFFENSIVE (IMAGES 2, 3, 4)
    # -------------------------------------------------------------
    opp_pos = positional_stats_dict.get(opp_name, {})
    opp_act = opp_pos.get('action_zones', {})
    opp_own_third_pct = int(opp_act.get('own_third_pct', 28))
    opp_opp_third_pct = int(opp_act.get('opposition_third_pct', 29))

    shots_zones_pg = my_pos.get('shots_zones_pg', {})
    team_shots_total_pg = float(shots_zones_pg.get('total', 14.0))
    team_shots_oob_pg = float(shots_zones_pg.get('out_of_box', 4.5))
    team_shots_6y_pg = float(shots_zones_pg.get('six_yard_box', 1.1))
    team_shots_pa_pg = float(shots_zones_pg.get('penalty_area', 8.4))

    shot_zones_pct = my_pos.get('shot_zones_pct', {})
    six_yard_pct = int(shot_zones_pct.get('six_yard_box_pct', 8))
    penalty_area_pct = int(shot_zones_pct.get('penalty_area_pct', 58))
    outside_box_pct = int(shot_zones_pct.get('outside_box_pct', 34))
    in_box_pct = six_yard_pct + penalty_area_pct

    if opp_own_third_pct >= 31:
        zone_summary_note = f"Il {opp_name} trascorre il {opp_own_third_pct}% della gara schiacciato nella propria 3/4: baricentro basso che concede costante pressione e palloni in area."
    else:
        zone_summary_note = f"Il {opp_name} difende compatto ({opp_own_third_pct}% nel terzo difensivo): gara aperta a duelli sulle corsie e ripartenze."

    # -------------------------------------------------------------
    # 5. CALCOLO FLANK ADVANTAGE SCORE & MATCHUP VULNERABILITY
    # -------------------------------------------------------------
    base_flank_score = 50.0
    flank_vol_delta = (flank_attack_pct - 33.0) * 1.4
    base_flank_score += flank_vol_delta

    if def_weakness == 'ALTA':
        base_flank_score += 15.0
    elif def_weakness == 'MEDIA':
        base_flank_score += 3.0
    else:
        base_flank_score -= 10.0

    base_flank_score += (opp_own_third_pct - 28.0) * 1.1

    if next_match['is_home']:
        base_flank_score += 4.0
    else:
        base_flank_score -= 4.0

    dribbles = float(player.get('dribbles_2627') or player.get('won_contest_2627') or 0)
    chances = float(player.get('chances_created_2627') or 0)
    box_idx = float(player.get('box_presence_index_2627') or 0)
    if dribbles >= 4 or chances >= 6 or box_idx >= 8.0:
        base_flank_score += 4.5

    flank_score = int(np.clip(round(base_flank_score), 15, 95))

    if flank_score >= 72:
        flank_badge = "🚀 DOMINIO CORSIA (Mismatch Favorevole)"
    elif flank_score >= 56:
        flank_badge = "⚔️ DUELLO FAVOREVOLE"
    elif flank_score >= 42:
        flank_badge = "⚖️ TEST EQUILIBRATO"
    else:
        flank_badge = "🛡️ CORSIA BLINDATA"

    xga_rank = int(opp_stats.get("xga_team_rank") or 10)
    goals_conceded_rank = int(opp_stats.get("goals_conceded_match_rank") or 10)
    raw_vuln = (xga_rank * 3.0) + (goals_conceded_rank * 2.0)
    if not next_match['is_home']:
        raw_vuln -= 8
    else:
        raw_vuln += 8
    vuln_score = int(np.clip(raw_vuln, 15, 95))

    if vuln_score >= 70:
        vuln_badge = "🔥 DIFESA VULNERABILE"
    elif vuln_score <= 35:
        vuln_badge = "🧱 MURO DIFENSIVO"
    else:
        vuln_badge = "⚖️ MATCHUP EQUILIBRATO"

    favorable_traits = []
    if flank_attack_pct >= 38:
        favorable_traits.append(f"⚡ Corsia Primaria: {flank_attack_pct}% del volume offensivo su questo lato")
    if def_weakness == 'ALTA':
        favorable_traits.append(f"🎯 Target Tattico: {opp_def_name} punto debole rivale (MV {def_mv})")
    elif def_weakness == 'BASSA':
        favorable_traits.append(f"🛡️ Duello Fisico: scontro diretto contro {opp_def_name} (MV {def_mv})")
        
    if opp_own_third_pct >= 31:
        favorable_traits.append(f"🏰 Pressione Continua: rivale rintanato nella propria trequarti ({opp_own_third_pct}%)")
    if in_box_pct >= 66:
        favorable_traits.append(f"💥 Concretizzazione in Area ({in_box_pct}% delle conclusioni nei 16m)")
    elif outside_box_pct >= 38:
        favorable_traits.append(f"🎯 Pericolo dal Limite: {outside_box_pct}% conclusioni da fuori area")

    matchup_advice = (
        f"Matchday G{current_round} ({next_match['match_str']}): {pname} opera su {side_label} ({flank_attack_pct}% degli attacchi squadra). "
        f"Incrocio diretto con {opp_def_name} ({opp_def_role_label}, MV {def_mv}). {def_desc}. {zone_summary_note}"
    )

    return {
        "opponent": opp_name,
        "is_home": next_match['is_home'],
        "match_str": next_match['match_str'],
        "current_round": current_round,
        "vulnerability_score": vuln_score,
        "vulnerability_badge": vuln_badge,
        "favorable_traits": favorable_traits,
        "matchup_advice": matchup_advice,
        "flank_matchup": {
            "side_code": side_code,
            "side_label": side_label,
            "flank_attack_pct": flank_attack_pct,
            "opp_defender_name": opp_def_name,
            "opp_defender_role": opp_def_role_label,
            "opp_defender_pos": opp_def_pos,
            "opp_defender_mv": def_mv,
            "opp_defender_fm": def_fm,
            "opp_defender_weakness": def_weakness,
            "opp_defender_weakness_badge": def_weakness_badge,
            "flank_score": flank_score,
            "flank_badge": flank_badge,
            "flank_desc": def_desc
        },
        "zone_stats": {
            "team_shots_total_pg": team_shots_total_pg,
            "six_yard_box_pct": six_yard_pct,
            "penalty_area_pct": penalty_area_pct,
            "outside_box_pct": outside_box_pct,
            "in_box_pct": in_box_pct,
            "opp_own_third_pct": opp_own_third_pct,
            "opp_mid_third_pct": int(opp_act.get('middle_third_pct', 43)),
            "opp_opp_third_pct": opp_opp_third_pct,
            "zone_summary_note": zone_summary_note
        }
    }


def evaluate_trade(players_out_list, players_in_list, remaining_rounds=33):
    """
    Trade Evaluator AI:
    Valuta uno scambio multi-calciatore (1vs1, 2vs2, 3vs3).
    Calcola:
    - Delta punti attesi (xPoints) da qui alla 38ª giornata
    - Delta valore d'asta FVM (crediti)
    - Shift di fragilità clinica
    - Verdetto sintetico e motivazione analitica
    """
    def calc_bundle_points(p_list):
        tot_pts = 0.0
        tot_fvm = 0.0
        fragility_penalty = 0.0
        for p in p_list:
            xfm = float(p.get("xfm") or p.get("fm_2627") or p.get("fm") or 6.0)
            tit = float(p.get("titolarita") or 60) / 100.0
            tier = p.get("fragility_tier", "ROCCIA")
            
            # Penalità rischio infortunio
            inj_rate = 0.02
            if tier == "CRISTALLO": inj_rate = 0.28
            elif tier == "FRAGILE": inj_rate = 0.16
            elif tier == "ATTENZIONE": inj_rate = 0.08
            
            p_pts = xfm * tit * remaining_rounds * (1.0 - inj_rate)
            tot_pts += p_pts
            tot_fvm += float(p.get("fvm") or 1.0)
            fragility_penalty += inj_rate

        return tot_pts, tot_fvm, fragility_penalty

    pts_out, fvm_out, frag_out = calc_bundle_points(players_out_list)
    pts_in, fvm_in, frag_in = calc_bundle_points(players_in_list)

    delta_pts = round(pts_in - pts_out, 1)
    delta_fvm = round(fvm_in - fvm_out, 1)

    # Verdetto
    if delta_pts >= 12.0:
        verdict = "🚀 SCAMBIO DA ACCETTARE SUBITO"
        verdict_color = "#10b981"
        explanation = f"Guadagno massiccio di ben +{delta_pts} punti attesi nel corso del campionato e plusvalenza di +{delta_fvm} crediti FVM. L'algoritmo approva pienamente."
    elif delta_pts >= 4.0:
        verdict = "✅ SCAMBIO FAVOREVOLE"
        verdict_color = "#34d399"
        explanation = f"Guadagni un vantaggio netto di +{delta_pts} punti totali con un migliore indice di titolarità e resa xFM della combinazione ricevuta."
    elif delta_pts >= -3.5:
        verdict = "⚖️ SCAMBIO EQUILIBRATO"
        verdict_color = "#38bdf8"
        explanation = f"Operazione sostanzialmente alla pari (delta {delta_pts:+0.1f} pt). Valuta in base alle esigenze dei reparti della tua rosa."
    elif delta_pts >= -10.0:
        verdict = "⚠️ SCAMBIO SCONSIGLIATO"
        verdict_color = "#f59e0b"
        explanation = f"Perdi circa {abs(delta_pts)} punti stimati. I giocatori che cedi offrono garanzie di voto e xFM superiori."
    else:
        verdict = "❌ RIFIUTA CATEGORICAMENTE"
        verdict_color = "#ef4444"
        explanation = f"Svalutazione pesante della tua rosa (-{abs(delta_pts)} punti attesi). La controparte ci guadagna nettamente."

    if frag_in > frag_out + 0.15:
        explanation += " ⚠️ ATTENZIONE: Aumenti sensibilmente il rischio clinico medio della tua rosa (calciatori fragili in entrata)."

    return {
        "delta_points": delta_pts,
        "delta_fvm": delta_fvm,
        "points_given": round(pts_out, 1),
        "points_received": round(pts_in, 1),
        "verdict": verdict,
        "verdict_color": verdict_color,
        "explanation": explanation
    }
