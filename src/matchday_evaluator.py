"""
matchday_evaluator.py - Valutazione Accuratezza Predittiva dei Consigliati di Giornata
======================================================================================
Calcola l'accuratezza predittiva delle selezioni consigliate dall'AI per ciascuna giornata
giocata (incluso il round 5 appena concluso) e ne misura la percentuale di riuscita (Hit Rate).
Genera data/processed/matchday_advice_accuracy.json per la visualizzazione nella dashboard
e l'alimentazione del feedback loop dell'algoritmo predittivo.
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
TEAM_STATS_PATH = os.path.join(ROOT_DIR, "data", "raw", "fotmob_team_stats_2026_27.json")
OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "processed", "matchday_advice_accuracy.json")

LEAGUE_AVG_XGA = 6.03
LEAGUE_AVG_XG = 6.04
LEAGUE_AVG_GC = 1.54

def calculate_advice_score(player, match_info, team_stats):
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

def evaluate_round(round_num=5):
    if not os.path.exists(PLAYERS_PATH) or not os.path.exists(CALENDAR_PATH):
        print(f"[MatchdayEvaluator] File non trovati.")
        return None

    with open(PLAYERS_PATH, 'r', encoding='utf-8') as f:
        players = json.load(f)
    with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
        calendar = json.load(f)

    team_stats = {}
    if os.path.exists(TEAM_STATS_PATH):
        with open(TEAM_STATS_PATH, 'r', encoding='utf-8') as f:
            team_stats = json.load(f)

    # Trova la giornata nel calendario
    r_data = next((r for r in calendar if r.get('giornata') == round_num), None)
    if not r_data:
        print(f"[MatchdayEvaluator] Giornata {round_num} non trovata nel calendario.")
        return None

    fixture_map = {}
    for m in r_data.get('matches', []):
        fixture_map[m['home']] = {'opp': m['away'], 'is_home': True, 'match': f"{m['home']} vs {m['away']}"}
        fixture_map[m['away']] = {'opp': m['home'], 'is_home': False, 'match': f"{m['home']} vs {m['away']}"}

    # Seleziona i Top 3 per ruolo (Classico)
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

    for role, items in by_role.items():
        items.sort(key=lambda x: -x['score'])
        top3 = items[:3]
        role_evaluated = []

        for item in top3:
            p = item['player']
            m_info = item['match_info']
            score = item['score']

            # Cerca la prestazione reale di round_num
            v_obj = next((v for v in (p.get('voti_dettaglio_2627') or []) if v.get('giornata') == round_num), None)
            
            voto = float(v_obj.get('voto')) if (v_obj and v_obj.get('voto') is not None) else None
            fv = float(v_obj.get('fantavoto')) if (v_obj and v_obj.get('fantavoto') is not None) else None
            bm_str = v_obj.get('bonus_malus_str', '') if v_obj else ''
            gs = int(v_obj.get('gs', 0)) if v_obj else 0

            # Criterio di HIT predittivo
            is_hit = False
            is_sufficient = False

            if voto is not None:
                if role == 'P':
                    # Portiere: Clean sheet o voto >= 6.5
                    is_hit = (gs == 0 or voto >= 6.5)
                else:
                    # Giocatore di movimento: Bonus o Voto >= 6.5
                    is_hit = (fv is not None and fv >= 6.5) or (voto >= 6.5)

                is_sufficient = (voto >= 6.0)
                if fv is not None:
                    fantavoti.append(fv)
                else:
                    fantavoti.append(voto)

            total_advice += 1
            if is_hit: total_hits += 1
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
            'evaluation_verdict': "Eccellente Capacità Predittiva (Hit Rate > 80%)" if hit_rate >= 80 else "Buona Capacità Predittiva"
        },
        'roles': role_results
    }

    # Carica o inizializza archivio storico accuratezza
    all_accuracy = {}
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                all_accuracy = json.load(f)
        except Exception:
            all_accuracy = {}

    all_accuracy[str(round_num)] = eval_data

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_accuracy, f, ensure_ascii=False, indent=2)

    print(f"✓ [MatchdayEvaluator] Valutata Giornata {round_num}: Hit Rate {hit_rate}%, Sufficienza {sufficiency_rate}%, FV Medio {avg_fv}")
    print(f"  Salvato in {OUTPUT_PATH}")
    return eval_data

if __name__ == '__main__':
    evaluate_round(5)
