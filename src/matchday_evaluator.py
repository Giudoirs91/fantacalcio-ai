"""
matchday_evaluator.py - Valutazione Accuratezza Predittiva dei Consigliati di Giornata & Feedback Loop AI
========================================================================================================
1. Calcola l'accuratezza predittiva delle selezioni consigliate dall'AI per ciascuna giornata
   giocata e completata (Hit Rate %, Sufficienza %, Fantavoto Medio).
2. Esegue in BACKGROUND l'analisi degli errori (Miss Analysis) per apprendere dai bias:
   - Riconosce i motivi di errore (panchine impreviste, malus inaspettati, overperformance difensive).
   - Calibra le correzioni di ruolo e di squadra salvandole in config/ai_bias_corrections.json.
3. Genera data/processed/matchday_advice_accuracy.json che espone al frontend ESCLUSIVAMENTE la percentuale
   di riuscita a giornata completata (senza spoilerare formule o dettagli interni).
"""

import os
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
TEAM_STATS_PATH = os.path.join(ROOT_DIR, "data", "raw", "fotmob_team_stats_2026_27.json")
OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "processed", "matchday_advice_accuracy.json")
FEEDBACK_LOG_PATH = os.path.join(ROOT_DIR, "data", "processed", "matchday_learning_feedback.json")
BIAS_CORRECTIONS_PATH = os.path.join(ROOT_DIR, "config", "ai_bias_corrections.json")
EUROPEAN_CUPS_PATH = os.path.join(ROOT_DIR, "config", "european_cups.json")

LEAGUE_AVG_XGA = 6.03
LEAGUE_AVG_XG = 6.04
LEAGUE_AVG_GC = 1.54

_EUROPEAN_CUPS_CACHE = None

def _get_european_cups():
    global _EUROPEAN_CUPS_CACHE
    if _EUROPEAN_CUPS_CACHE is None:
        if os.path.exists(EUROPEAN_CUPS_PATH):
            try:
                with open(EUROPEAN_CUPS_PATH, 'r', encoding='utf-8') as f:
                    _EUROPEAN_CUPS_CACHE = json.load(f)
            except Exception:
                _EUROPEAN_CUPS_CACHE = {}
        else:
            _EUROPEAN_CUPS_CACHE = {}
    return _EUROPEAN_CUPS_CACHE


TEAM_RATINGS_PATH = os.path.join(ROOT_DIR, "config", "team_ratings.json")
_TEAM_RATINGS_CACHE = None

def _get_team_ratings():
    global _TEAM_RATINGS_CACHE
    if _TEAM_RATINGS_CACHE is None:
        if os.path.exists(TEAM_RATINGS_PATH):
            try:
                with open(TEAM_RATINGS_PATH, 'r', encoding='utf-8') as f:
                    _TEAM_RATINGS_CACHE = json.load(f)
            except Exception:
                _TEAM_RATINGS_CACHE = {}
        else:
            _TEAM_RATINGS_CACHE = {}
    return _TEAM_RATINGS_CACHE


def get_team_profile(team, team_stats):
    tr = _get_team_ratings().get(team, {'multiplier': 1.0, 'dif_stars': 3, 'att_stars': 3})
    st = team_stats.get(team, {})
    xg = float(st.get('xg_team') or LEAGUE_AVG_XG)
    xga = float(st.get('xga_team') or LEAGUE_AVG_XGA)
    gc = float(st.get('goals_conceded_match') or LEAGUE_AVG_GC)
    cs = float(st.get('clean_sheets') or 0)

    att_star_coeff = 0.55 + (tr.get('att_stars', 3) * 0.16)
    xg_coeff = xg / LEAGUE_AVG_XG
    att_power = (att_star_coeff * 0.60) + (xg_coeff * 0.40)

    dif_star_coeff = 1.65 - (tr.get('dif_stars', 3) * 0.19)
    xga_coeff = (xga / LEAGUE_AVG_XGA * 0.6) + (gc / LEAGUE_AVG_GC * 0.4)
    def_vuln = (dif_star_coeff * 0.50) + (xga_coeff * 0.50)

    return {
        'att_power': max(0.65, min(1.85, att_power)),
        'def_vuln': max(0.55, min(1.95, def_vuln)),
        'cs': cs,
        'gc': gc,
        'xg': xg,
        'xga': xga,
        'att_stars': tr.get('att_stars', 3),
        'dif_stars': tr.get('dif_stars', 3)
    }


def calculate_advice_score(player, match_info, team_stats):
    """Calcola il punteggio predittivo per un calciatore nella specifica giornata."""
    if not match_info or player.get('is_injured'):
        return -999.0
    tit = float(player.get('titolarita', 50))
    if tit < 50:
        return -500.0
    role = player.get('role', 'C')
    if role == 'P' and tit < 70:
        return -500.0

    team = player.get('team')
    opp = match_info.get('opp')
    is_home = match_info.get('is_home', True)

    my = get_team_profile(team, team_stats)
    opp_prof = get_team_profile(opp, team_stats)

    ovr = float(player.get('ovr', 75))
    fm = float(player.get('fm_2627') or player.get('fm') or 6.0)
    mv = float(player.get('mv_2627') or player.get('mv') or 6.0)
    xg90 = float(player.get('xg90_2627') or player.get('xg90') or 0.0)
    xa90 = float(player.get('xa90_2627') or player.get('xa90') or 0.0)
    gol = float(player.get('gol_2627') or 0.0)
    ass = float(player.get('assist_2627') or 0.0)

    rig_tier = int(player.get('rigorista_tier') or 0)
    piaz_tier = int(player.get('piazzati_tier') or 0)

    rig_bonus = 8.0 if rig_tier == 1 else (3.0 if rig_tier == 2 else (1.0 if rig_tier == 3 else 0.0))
    piaz_bonus = 4.5 if piaz_tier == 1 else (2.0 if piaz_tier == 2 else (0.5 if piaz_tier == 3 else 0.0))

    if role == 'P':
        score = 55.0 + (ovr * 0.12) + (fm * 2.0)
        score += (my['cs'] * 6.0) - (my['gc'] * 5.0) - (my['def_vuln'] * 8.0)
        if is_home: score += 7.0

        loc_mod = 0.85 if is_home else 1.15
        xgc_est = opp_prof['att_power'] * my['def_vuln'] * loc_mod

        if xgc_est > 0.95:
            score -= ((xgc_est - 0.95) ** 1.4) * 32.0
        else:
            score += ((0.95 - xgc_est) * 16.0)

        if opp_prof['att_stars'] >= 5:
            score -= 16.0
        elif opp_prof['att_stars'] == 4:
            score -= 7.0
        elif opp_prof['att_stars'] <= 2:
            score += 12.0

    elif role == 'D':
        score = 52.0 + (ovr * 0.16) + (fm * 2.8) + (mv * 2.2)
        loc_mod = 0.88 if is_home else 1.15
        def_stress = opp_prof['att_power'] * my['def_vuln'] * loc_mod

        if def_stress > 1.05:
            score -= ((def_stress - 1.05) ** 1.3) * 30.0
        else:
            score += ((1.05 - def_stress) * 14.0)

        if is_home: score += 4.0

        if player.get('is_oop'): score += 12.0
        if player.get('is_punizioni') or player.get('is_corner'): score += 6.0
        if rig_tier == 1: score += 14.0
        elif rig_tier == 2: score += 6.0
        if piaz_tier == 1: score += 4.0

        score += (xg90 * 18.0) + (xa90 * 16.0) + (min(gol, 2) * 2.5) + (min(ass, 2) * 2.0)

    else: # C e A
        score = 48.0 + (ovr * 0.18) + (fm * 3.2) + (mv * 2.0)
        loc_mod = 1.10 if is_home else 0.92
        opp_concession = opp_prof['def_vuln'] * loc_mod

        score += (opp_concession - 1.0) * 18.0
        if is_home: score += 5.0

        score += rig_bonus + piaz_bonus
        if player.get('is_oop'): score += 10.0

        score += (xg90 * opp_concession) * 22.0
        score += (xa90 * opp_concession) * 16.0
        score += (min(gol, 4) * 3.5) + (min(ass, 3) * 2.5)

    # Penalità stanchezza e allerta turnover Coppe Europee infrasettimanali
    round_num = match_info.get('round_num')
    if round_num and score > 0:
        euro_data = _get_european_cups()
        comps = euro_data.get('competitions', {})
        for comp_name, comp_info in comps.items():
            if team in comp_info.get('teams', []):
                pre = round_num in comp_info.get('matchdays_preceded_by_cup', [])
                post = round_num in comp_info.get('matchdays_followed_by_cup', [])
                if pre or post:
                    fatigue_pen = 3.5 if comp_info.get('impact_level') == 'HIGH' else 2.0
                    score -= fatigue_pen
                    break

    return round(score, 1)


def evaluate_round(round_num, players, calendar, team_stats):
    """Valuta retrospettivamente una specifica giornata disputata."""
    r_data = next((r for r in calendar if r.get('giornata') == round_num), None)
    if not r_data:
        return None

    fixture_map = {}
    for m in r_data.get('matches', []):
        fixture_map[m['home']] = {'opp': m['away'], 'is_home': True, 'match': f"{m['home']} vs {m['away']}", 'round_num': round_num}
        fixture_map[m['away']] = {'opp': m['home'], 'is_home': False, 'match': f"{m['home']} vs {m['away']}", 'round_num': round_num}

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

    role_results = {}
    total_advice = 0
    total_hits = 0
    total_sufficient = 0
    fantavoti = []
    miss_reasons = []

    for role, items in by_role.items():
        items.sort(key=lambda x: -x['score'])
        top3 = items[:3]
        role_evaluated = []

        for item in top3:
            p = item['player']
            m_info = item['match_info']
            score = item['score']

            v_obj = next((v for v in (p.get('voti_dettaglio_2627') or []) if v.get('giornata') == round_num), None)
            voto = float(v_obj.get('voto')) if (v_obj and v_obj.get('voto') is not None) else None
            fv = float(v_obj.get('fantavoto')) if (v_obj and v_obj.get('fantavoto') is not None) else None
            bm_str = v_obj.get('bonus_malus_str', '') if v_obj else ''
            gs = int(v_obj.get('gs', 0)) if v_obj else 0

            is_hit = False
            is_sufficient = False
            error_category = None

            if voto is not None:
                if role == 'P':
                    is_hit = (gs == 0 or voto >= 6.5)
                else:
                    is_hit = (fv is not None and fv >= 6.5) or (voto >= 6.5)

                is_sufficient = (voto >= 6.0)
                if fv is not None:
                    fantavoti.append(fv)
                else:
                    fantavoti.append(voto)

                if not is_hit:
                    if voto < 5.5:
                        error_category = "Prestazione gravemente insufficiente"
                    elif gs >= 2:
                        error_category = "Collasso difensivo di squadra"
                    elif fv is not None and fv < voto:
                        error_category = "Malus disciplinare decisivo"
                    else:
                        error_category = "Voto ordinario senza bonus (6.0)"
            else:
                error_category = "Panchina inattesa / Senza Voto (S.V.)"

            total_advice += 1
            if is_hit: 
                total_hits += 1
            else:
                miss_reasons.append({
                    'round': round_num,
                    'player': p.get('name'),
                    'team': p.get('team'),
                    'role': role,
                    'reason': error_category or "Sconosciuto"
                })

            if is_sufficient: total_sufficient += 1

            status_label = "HIT" if is_hit else ("SUFFICIENTE" if is_sufficient else "MISS")

            role_evaluated.append({
                'id': p.get('id'),
                'name': p.get('name'),
                'team': p.get('team'),
                'role': role,
                'ovr': p.get('ovr'),
                'match': m_info.get('match'),
                'opponent': m_info.get('opp'),
                'is_home': m_info.get('is_home'),
                'score_ai': score,
                'voto_reale': voto,
                'fantavoto_reale': fv,
                'bonus_malus': bm_str,
                'status': status_label,
                'is_hit': is_hit,
                'is_sufficient': is_sufficient
            })

        role_results[role] = role_evaluated

    hit_rate = round((total_hits / total_advice * 100), 1) if total_advice > 0 else 0.0
    sufficiency_rate = round((total_sufficient / total_advice * 100), 1) if total_advice > 0 else 0.0
    avg_fv = round(sum(fantavoti) / len(fantavoti), 2) if fantavoti else 0.0

    eval_data = {
        'round': round_num,
        'summary': {
            'total_consigliati': total_advice,
            'hits': total_hits,
            'hit_rate_pct': hit_rate,
            'sufficient': total_sufficient,
            'sufficiency_rate_pct': sufficiency_rate,
            'avg_fantavoto': avg_fv,
            'verdict_text': f"Accuratezza Predittiva: {hit_rate}% Hit Rate ({sufficiency_rate}% Sufficienze, FV Medio {avg_fv})"
        },
        'roles': role_results,
        'miss_reasons': miss_reasons
    }
    return eval_data


def run_learning_and_accuracy_evaluation():
    """
    Funzione principale del Feedback Loop:
    1. Scansiona tutte le giornate disputate (1..N).
    2. Calcola l'accuratezza predittiva per ogni turno.
    3. In background apprende dagli errori e aggiorna le bias corrections.
    4. Salva matchday_advice_accuracy.json per la visualizzazione all'utente a turno concluso.
    """
    if not os.path.exists(PLAYERS_PATH) or not os.path.exists(CALENDAR_PATH):
        print(f"[MatchdayEvaluator] File non trovati, skip.")
        return None

    with open(PLAYERS_PATH, 'r', encoding='utf-8') as f:
        players = json.load(f)
    with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
        calendar = json.load(f)

    team_stats = {}
    if os.path.exists(TEAM_STATS_PATH):
        with open(TEAM_STATS_PATH, 'r', encoding='utf-8') as f:
            team_stats = json.load(f)

    # Trova quali giornate sono state realmente giocate
    played_rounds = set()
    for p in players:
        for v in (p.get('voti_dettaglio_2627') or []):
            g = v.get('giornata')
            if g and v.get('voto') is not None:
                played_rounds.add(g)

    sorted_rounds = sorted(list(played_rounds))
    if not sorted_rounds:
        print("[MatchdayEvaluator] Nessuna giornata con voti trovata.")
        return None

    all_accuracy = {}
    all_misses = []
    total_all_advice = 0
    total_all_hits = 0
    role_hits = {'P': [0, 0], 'D': [0, 0], 'C': [0, 0], 'A': [0, 0]}

    for r in sorted_rounds:
        ev = evaluate_round(r, players, calendar, team_stats)
        if ev:
            all_accuracy[str(r)] = {
                'round': r,
                'summary': ev['summary'],
                'roles': ev['roles']
            }
            all_misses.extend(ev.get('miss_reasons', []))
            total_all_advice += ev['summary']['total_consigliati']
            total_all_hits += ev['summary']['hits']

            for role, list_r in ev['roles'].items():
                for p_eval in list_r:
                    role_hits[role][1] += 1
                    if p_eval['is_hit']:
                        role_hits[role][0] += 1

    overall_hit_rate = round((total_all_hits / total_all_advice * 100), 1) if total_all_advice > 0 else 0.0

    # Aggiungi metadati globali per la dashboard
    all_accuracy['meta'] = {
        'last_completed_round': max(sorted_rounds),
        'upcoming_round': max(sorted_rounds) + 1,
        'overall_hit_rate_pct': overall_hit_rate,
        'total_evaluated_advice': total_all_advice,
        'total_hits': total_all_hits,
        'evaluated_at': datetime.now().isoformat()
    }

    # Salva il file pubblico dell'accuratezza (letto dalla Dashboard / Frontend)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_accuracy, f, ensure_ascii=False, indent=2)

    # FEEDBACK LOOP IN BACKGROUND: APPRENDIMENTO DAGLI ERRORI
    # Categorizza i miss per apprendere
    learning_feedback = {
        "timestamp": datetime.now().isoformat(),
        "rounds_analyzed": sorted_rounds,
        "overall_hit_rate": overall_hit_rate,
        "role_hit_rates": {
            role: round((counts[0] / counts[1] * 100), 1) if counts[1] > 0 else 0.0
            for role, counts in role_hits.items()
        },
        "miss_count": len(all_misses),
        "misses_diagnostic": all_misses,
        "learned_bias_adjustments": {
            "comment": "Questi pesi vengono assorbiti in background dal motore predittivo",
            "titolarita_weight_boost": 1.15 if any("Panchina" in m['reason'] for m in all_misses) else 1.0,
            "fragile_defense_caution": 0.95 if any("Collasso" in m['reason'] for m in all_misses) else 1.0
        }
    }

    with open(FEEDBACK_LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(learning_feedback, f, ensure_ascii=False, indent=2)

    # Aggiorna anche config/ai_bias_corrections.json con l'hit rate dei consigliati
    if os.path.exists(BIAS_CORRECTIONS_PATH):
        try:
            with open(BIAS_CORRECTIONS_PATH, 'r', encoding='utf-8') as f:
                bias_data = json.load(f)
            bias_data["matchday_advice_accuracy_global"] = overall_hit_rate / 100.0
            bias_data["matchday_advice_by_role"] = {
                role: round((counts[0] / counts[1]), 3) if counts[1] > 0 else 0.0
                for role, counts in role_hits.items()
            }
            bias_data["last_matchday_learned"] = max(sorted_rounds)
            with open(BIAS_CORRECTIONS_PATH, 'w', encoding='utf-8') as f:
                json.dump(bias_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MatchdayEvaluator] Warning aggiornamento bias corrections: {e}")

    print(f"✓ [MatchdayEvaluator] Feedback Loop Completato su {len(sorted_rounds)} giornate (G1-G{max(sorted_rounds)}):")
    print(f"  Hit Rate Globale: {overall_hit_rate}% | Ruoli: {learning_feedback['role_hit_rates']}")
    print(f"  Accuracy salvata in: {OUTPUT_PATH}")
    print(f"  Diagnostica errori in: {FEEDBACK_LOG_PATH}")
    return all_accuracy


if __name__ == '__main__':
    run_learning_and_accuracy_evaluation()
