"""
advanced_metrics.py - Motore Statistico Avanzato Fanta Master AI
Implementa le 4 metriche avanzate predittive per la Serie A 2026/27:
1. Floor vs Ceiling (Rischio/Rendimento & Volatilità Fantavoto)
2. Matchup Vulnerability (Incrocio Tattico Asimmetrico difese avversarie)
3. Trade Evaluator AI (Valutatore Matematico di Scambi)
4. Indice di Impatto da Subentro (Super-Sub & Probabilità Voto)
"""

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
        tactical_profile = "🚀 Boom or Bust (Ceiling Esplosivo)"
        tactical_advice = f"Floor {floor} / Ceiling {ceiling}: da schierare quando hai bisogno di bonus pesanti per vincere la giornata."
    elif spread <= 4.2:
        volatility_label = "BASSA"
        tactical_profile = "🛡️ Floor Sicuro (Roccia Costante)"
        tactical_advice = f"Floor {floor} / Ceiling {ceiling}: eccellente certezza di rendimento e modificatore, pochissimi rischi di insufficienza."
    else:
        volatility_label = "MEDIA"
        tactical_profile = "⚖️ Rendimento Bilanciato"
        tactical_advice = f"Floor {floor} / Ceiling {ceiling}: solido equilibrio tra sufficienza garantita e buone chance di bonus."

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


def compute_matchup_vulnerability(player, calendar_data, team_stats_dict, current_round=6):
    """
    Calcola l'incrocio tattico asimmetrico per la prossima giornata (G6).
    Identifica le vulnerabilità specifiche della difesa avversaria.
    """
    team_name = player.get("team", "").upper().strip()
    role = player.get("role", "C")
    
    # Trova partita turno 6
    next_match = None
    if calendar_data:
        r_obj = next((r for r in calendar_data if r.get('giornata') == current_round), None)
        if r_obj and r_obj.get('matches'):
            for m in r_obj['matches']:
                h = (m.get('home') or '').upper().strip()
                a = (m.get('away') or '').upper().strip()
                if h == team_name:
                    next_match = {'opponent': m.get('away'), 'is_home': True, 'match_str': f"{m.get('home')} vs {m.get('away')}"}
                    break
                elif a == team_name:
                    next_match = {'opponent': m.get('home'), 'is_home': False, 'match_str': f"{m.get('away')} @ {m.get('home')}"}
                    break

    if not next_match:
        return {
            "opponent": "N/D",
            "is_home": True,
            "match_str": "Partita di campionato",
            "vulnerability_score": 50,
            "vulnerability_badge": "🟢 MATCHUP NORMALE",
            "favorable_traits": [],
            "matchup_advice": "Incrocio tattico equilibrato per la prossima giornata."
        }

    opp_name = next_match['opponent']
    opp_stats = team_stats_dict.get(opp_name, {}) if isinstance(team_stats_dict, dict) else {}

    # Metriche difensive avversario
    xga_rank = int(opp_stats.get("xga_team_rank") or 10) # 1 = miglior difesa, 20 = peggior difesa
    goals_conceded_rank = int(opp_stats.get("goals_conceded_match_rank") or 10)
    clean_sheets = int(opp_stats.get("clean_sheets") or 1)
    difesa_tier = opp_stats.get("difesa_tier", "average")
    
    # Calcolo vulnerabilità (0-100, 100 = difesa colabrodo)
    # Più il rank è alto (verso 20), più la difesa è vulnerabile
    raw_vuln = (xga_rank * 3.0) + (goals_conceded_rank * 2.0)
    if not next_match['is_home']:
        raw_vuln -= 8 # Fuori casa è leggermente più ostica
    else:
        raw_vuln += 8 # In casa si beneficia del fattore campo

    vuln_score = int(np.clip(raw_vuln, 15, 95))
    favorable_traits = []

    if vuln_score >= 70:
        vuln_badge = "🔥 DIFESA VULNERABILE"
        if role in ['A', 'C']:
            favorable_traits.append("💥 Reparto rivale ad alta concessione tiri (xGA alto)")
        else:
            favorable_traits.append("🛡️ Alta probabilità di Clean Sheet difensivo")
    elif vuln_score <= 35:
        vuln_badge = "🧱 MURO DIFENSIVO"
        favorable_traits.append("⚠️ Difesa avversaria ermetica (Basso tasso gol subiti)")
    else:
        vuln_badge = "⚖️ MATCHUP EQUILIBRATO"

    # Tratti specifici
    if player.get("is_rigorista_1") or player.get("is_punizioni"):
        if goals_conceded_rank >= 12:
            favorable_traits.append("🎯 Specialista Piazzati: avversario incline a falli in area/limite")

    if player.get("is_oop") and role in ['D', 'C']:
        favorable_traits.append("⚡ Spinta offensiva: la corsia avversaria concede spazio")

    matchup_advice = f"Matchday G{current_round} ({next_match['match_str']}): "
    if vuln_score >= 70:
        matchup_advice += f"La difesa del {opp_name} presenta gravi falle tattiche. Schierabilità caldamente consigliata (+15% indice atteso)."
    elif vuln_score <= 35:
        matchup_advice += f"Incrocio severo contro il {opp_name}, tra le difese più solide della Serie A. Schierare con prudenza."
    else:
        matchup_advice += f"Gara bilanciata contro il {opp_name}, fattori individuali determinanti."

    return {
        "opponent": opp_name,
        "is_home": next_match['is_home'],
        "match_str": next_match['match_str'],
        "vulnerability_score": vuln_score,
        "vulnerability_badge": vuln_badge,
        "favorable_traits": favorable_traits,
        "matchup_advice": matchup_advice
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
