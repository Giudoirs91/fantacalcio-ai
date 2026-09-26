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

LEAGUE_AVG_XGA = 6.03
LEAGUE_AVG_XG = 6.04
LEAGUE_AVG_GC = 1.54


def calculate_advice_score(player, match_info, team_stats):
    """Calcola il punteggio predittivo per un calciatore nella specifica giornata."""
    if not match_info or player.get('is_injured'):
        return -999.0
    tit = float(player.get('titolarita', 50))
    if tit < 50:
        return -500.0

    team = player.get('team')
    opp = match_info.get('opp')
    is_home = match_info.get('is_home', True)
    role = player.get('role', 'C')

    ovr = float(player.get('ovr', 75))
    fm = float(player.get('fm_2627') or player.get('fm') or 6.0)
    mv = float(player.get('mv_2627') or player.get('mv') or 6.0)
    xg90 = float(player.get('xg90_2627') or player.get('xg90') or 0.0)
    xa90 = float(player.get('xa90_2627') or player.get('xa90') or 0.0)

    my_stats = team_stats.get(team, {})
    opp_stats = team_stats.get(opp, {})

    my_xga = float(my_stats.get('xga_team') or LEAGUE_AVG_XGA)
    my_gc = float(my_stats.get('goals_conceded_match') or LEAGUE_AVG_GC)
    my_cs = float(my_stats.get('clean_sheets') or 0)

    opp_xg = float(opp_stats.get('xg_team') or LEAGUE_AVG_XG)
    opp_xga = float(opp_stats.get('xga_team') or LEAGUE_AVG_XGA)
    opp_bc = float(opp_stats.get('big_chances') or 5.0)
    opp_box = float(opp_stats.get('touches_opp_box') or 80.0)

    if role == 'P':
        score = 65.0 + (ovr * 0.18) + (fm * 2.5)
        score += (my_cs * 8.0) - (my_gc * 6.0) - ((my_xga / LEAGUE_AVG_XGA) * 5.0)
        if is_home: score += 10.0
        xg_diff = opp_xg - LEAGUE_AVG_XG
        if xg_diff > 0:
            score -= (xg_diff ** 1.35) * 8.5
        else:
            score += abs(xg_diff) * 6.0
        score -= (opp_bc / 4.0) * 3.0
        return round(score, 1)

    elif role == 'D':
        score = 60.0 + (ovr * 0.22) + (fm * 3.5) + (mv * 3.0)
        box_diff = (opp_box - 80.0) / 20.0
        score -= box_diff * 4.0
        score += (opp_xga / LEAGUE_AVG_XGA) * 6.0
        if is_home: score += 5.0
        return round(score, 1)

    elif role == 'C':
        score = 55.0 + (ovr * 0.25) + (fm * 4.0) + (xg90 * 25.0) + (xa90 * 20.0)
        score += (opp_xga / LEAGUE_AVG_XGA) * 8.0
        if is_home: score += 6.0
        return round(score, 1)

    elif role == 'A':
        score = 50.0 + (ovr * 0.28) + (fm * 4.5) + (xg90 * 35.0) + (xa90 * 15.0)
        score += (opp_xga / LEAGUE_AVG_XGA) * 10.0
        if is_home: score += 7.0
        return round(score, 1)

    return 0.0


def evaluate_round(round_num, players, calendar, team_stats):
    """Valuta retrospettivamente una specifica giornata disputata."""
    r_data = next((r for r in calendar if r.get('giornata') == round_num), None)
    if not r_data:
        return None

    fixture_map = {}
    for m in r_data.get('matches', []):
        fixture_map[m['home']] = {'opp': m['away'], 'is_home': True, 'match': f"{m['home']} vs {m['away']}"}
        fixture_map[m['away']] = {'opp': m['home'], 'is_home': False, 'match': f"{m['home']} vs {m['away']}"}

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
