"""
ai_evaluator.py - Sistema di Autovalutazione e Apprendimento AI
================================================================
Implementa un feedback loop chiuso:
  T0  (Asta)       -> save_predictions_snapshot() -> config/ai_predictions_snapshot.json
  T+N (Giornata N) -> evaluate_predictions()       -> data/processed/ai_error_analysis.json
                                                   -> config/ai_bias_corrections.json
  Prossima run     -> valuation_engine applica     -> xFM piu preciso
                      bias_corrections

Le correzioni sono non-distruttive: se il file non esiste, tutto funziona come prima.
Le correzioni vengono applicate solo con >= MIN_ROUNDS_FOR_LEARNING giornate di dati reali.
"""

import os
import json
import math
from datetime import datetime
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

SNAPSHOT_PATH = os.path.join(CONFIG_DIR, "ai_predictions_snapshot.json")
CORRECTIONS_PATH = os.path.join(CONFIG_DIR, "ai_bias_corrections.json")
ERROR_ANALYSIS_PATH = os.path.join(PROCESSED_DIR, "ai_error_analysis.json")

MIN_ROUNDS_FOR_LEARNING = 5
MIN_SEGMENT_SIZE = 8
LEARNING_RATE = 0.5

ADVICE_THRESHOLDS = {
    "top":     lambda fm, pres, rounds: fm > 8.0 and pres >= rounds * 0.80,
    "leader":  lambda fm, pres, rounds: fm > 7.0 and pres >= rounds * 0.70,
    "buy":     lambda fm, pres, rounds: fm > 6.5 or pres >= rounds * 0.65,
    "sleeper": lambda fm, pres, rounds: fm > 7.0,
    "warning": lambda fm, pres, rounds: fm < 6.5 or pres < rounds * 0.60,
    "flop":    lambda fm, pres, rounds: fm < 6.0,
    "avoid":   lambda fm, pres, rounds: fm < 5.5 or pres < rounds * 0.40,
}


# -----------------------------------------------------------------
#  STEP 1: Salva Snapshot Predizioni T0
# -----------------------------------------------------------------

def save_predictions_snapshot(players, round_num=0, force=False):
    """
    Salva le predizioni dell'AI al momento dell'asta (round_num=0).
    Viene chiamato dalla pipeline solo se lo snapshot non esiste gia
    oppure se force=True.
    Returns True se salvato, False se gia esisteva.
    """
    if os.path.exists(SNAPSHOT_PATH) and not force:
        print(f"[AI Evaluator] Snapshot gia esistente -- skipping.")
        return False

    snapshot_fields = [
        "id", "name", "role", "mantra", "team",
        "fvm", "qta", "ovr", "prezzo_cons", "max_bid",
        "xfm", "delta_xfm",
        "ai_advice", "ai_advice_type",
        "fascia", "slot_num",
        "titolarita",
        "fragility_score", "fragility_tier", "fragilita_score",
        "disponibilita_pct", "is_injured", "is_chronic_fragile",
        "oop_tier", "is_oop",
        "is_rigorista_1", "is_punizioni",
        "is_top", "is_sleeper", "is_flop",
        "league_2526",
        "xg90_2627", "xa90_2627", "xg90_2526", "xa90_2526",
        "fm", "mv",
    ]

    snapshot = {
        "metadata": {
            "saved_at": datetime.now().isoformat(),
            "round_num": round_num,
            "n_players": len(players),
            "description": "Snapshot predizioni AI al momento dell'asta (T0)",
        },
        "players": [{k: p.get(k) for k in snapshot_fields} for p in players]
    }

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"[AI Evaluator] Snapshot T0 salvato: {len(players)} calciatori -> {SNAPSHOT_PATH}")
    return True


def load_predictions_snapshot():
    """Carica lo snapshot T0. Ritorna None se non esiste."""
    if not os.path.exists(SNAPSHOT_PATH):
        return None
    try:
        with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[AI Evaluator] Errore caricamento snapshot: {e}")
        return None


# -----------------------------------------------------------------
#  STEP 2: Valuta Predizioni vs Realta
# -----------------------------------------------------------------

def evaluate_predictions(players_current, round_num):
    """
    Confronta le predizioni T0 con i dati reali alla giornata round_num.
    Richiede almeno MIN_ROUNDS_FOR_LEARNING giornate di dati.
    Returns il dizionario di error analysis, o None se dati insufficienti.
    """
    if round_num < MIN_ROUNDS_FOR_LEARNING:
        print(f"[AI Evaluator] Dati insufficienti (G{round_num} < G{MIN_ROUNDS_FOR_LEARNING}) -- skip.")
        return None

    snapshot = load_predictions_snapshot()
    if snapshot is None:
        print("[AI Evaluator] Nessuno snapshot T0 trovato -- impossibile valutare.")
        return None

    snap_by_id = {str(p["id"]): p for p in snapshot["players"]}
    errors = []

    for p_cur in players_current:
        pid = str(p_cur.get("id", ""))
        p_snap = snap_by_id.get(pid)
        if p_snap is None:
            continue

        fm_actual = p_cur.get("fm_2627")
        presenze_actual = p_cur.get("presenze_2627", 0) or 0

        if not fm_actual or presenze_actual == 0:
            continue

        xfm_pred = p_snap.get("xfm") or p_snap.get("fm") or 6.0
        advice_type = p_snap.get("ai_advice_type", "")
        fragility_score_pred = p_snap.get("fragilita_score") or p_snap.get("fragility_score") or 1
        titolarita_pred = p_snap.get("titolarita") or 50

        xfm_error = round(float(xfm_pred) - float(fm_actual), 3)
        titolarita_actual_pct = (presenze_actual / round_num * 100) if round_num > 0 else 0
        titolarita_error = round(float(titolarita_pred) - titolarita_actual_pct, 2)

        advice_fn = ADVICE_THRESHOLDS.get(advice_type)
        advice_correct = advice_fn(float(fm_actual), presenze_actual, round_num) if advice_fn else None

        injury_occurred = presenze_actual < round_num * 0.5
        high_fragility_pred = fragility_score_pred >= 3 or bool(p_snap.get("is_chronic_fragile"))
        fragility_correct = (high_fragility_pred == injury_occurred)

        errors.append({
            "id": pid,
            "name": p_cur.get("name", ""),
            "role": p_snap.get("role", ""),
            "team": p_snap.get("team", ""),
            "league_2526": p_snap.get("league_2526", "Serie A"),
            "oop_tier": p_snap.get("oop_tier", ""),
            "slot_num": p_snap.get("slot_num", 5),
            "fascia": p_snap.get("fascia", ""),
            "fragility_score_pred": fragility_score_pred,
            "is_chronic_fragile_pred": bool(p_snap.get("is_chronic_fragile")),
            "high_fragility_pred": high_fragility_pred,
            "xfm_pred": float(xfm_pred),
            "fm_pred_ovr": p_snap.get("ovr", 70),
            "titolarita_pred": float(titolarita_pred),
            "advice_type_pred": advice_type,
            "fm_actual": float(fm_actual),
            "presenze_actual": presenze_actual,
            "titolarita_actual_pct": round(titolarita_actual_pct, 1),
            "injury_occurred": injury_occurred,
            "xfm_error": xfm_error,
            "abs_xfm_error": abs(xfm_error),
            "titolarita_error": titolarita_error,
            "advice_correct": advice_correct,
            "fragility_correct": fragility_correct,
        })

    if not errors:
        print("[AI Evaluator] Nessun giocatore valutabile trovato.")
        return None

    print(f"[AI Evaluator] Valutati {len(errors)} calciatori a G{round_num}.")
    error_analysis = analyze_error_patterns(errors, round_num)
    bias_corrections = compute_bias_corrections(error_analysis, round_num)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    _save_error_analysis(error_analysis, errors, round_num)
    _save_bias_corrections(bias_corrections)
    return error_analysis


# -----------------------------------------------------------------
#  STEP 3: Analizza Pattern di Errore
# -----------------------------------------------------------------

def analyze_error_patterns(errors, round_num):
    """Segmenta gli errori per categoria e calcola bias medi per segmento."""

    def _stats(values):
        if not values:
            return {"mean": 0.0, "mae": 0.0, "count": 0, "std": 0.0}
        n = len(values)
        mean = sum(values) / n
        mae = sum(abs(v) for v in values) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / n) if n > 1 else 0.0
        return {"mean": round(mean, 3), "mae": round(mae, 3), "count": n, "std": round(std, 3)}

    all_xfm_errors = [e["xfm_error"] for e in errors]
    all_tit_errors = [e["titolarita_error"] for e in errors]
    advice_results = [e["advice_correct"] for e in errors if e["advice_correct"] is not None]
    fragility_results = [e["fragility_correct"] for e in errors]

    global_stats = {
        "xfm": _stats(all_xfm_errors),
        "titolarita": _stats(all_tit_errors),
        "advice_accuracy": round(sum(advice_results) / len(advice_results), 3) if advice_results else 0.0,
        "fragility_hit_rate": round(sum(fragility_results) / len(fragility_results), 3) if fragility_results else 0.0,
        "n_players": len(errors),
        "round_num": round_num,
    }

    by_role = defaultdict(list)
    for e in errors:
        by_role[e["role"]].append(e["xfm_error"])
    role_stats = {r: _stats(v) for r, v in by_role.items()}

    by_league = defaultdict(list)
    for e in errors:
        by_league[e.get("league_2526") or "Serie A"].append(e["xfm_error"])
    league_stats = {lg: _stats(v) for lg, v in by_league.items() if len(v) >= 3}

    by_oop = defaultdict(list)
    for e in errors:
        by_oop[e.get("oop_tier") or "STANDARD"].append(e["xfm_error"])
    oop_stats = {t: _stats(v) for t, v in by_oop.items()}

    by_frag = defaultdict(list)
    for e in errors:
        fs = e.get("fragility_score_pred", 1)
        tier = "alta" if fs >= 3 else ("media" if fs >= 2 else "bassa")
        by_frag[tier].append(e["xfm_error"])
    fragility_stats = {t: _stats(v) for t, v in by_frag.items()}

    by_slot = defaultdict(list)
    for e in errors:
        slot = e.get("slot_num", 5)
        bracket = "1-2" if slot <= 2 else ("3-4" if slot <= 4 else "5+")
        by_slot[bracket].append(e["xfm_error"])
    slot_stats = {b: _stats(v) for b, v in by_slot.items()}

    by_advice_type = defaultdict(list)
    for e in errors:
        if e.get("advice_correct") is not None:
            by_advice_type[e["advice_type_pred"]].append(1 if e["advice_correct"] else 0)
    advice_accuracy_by_type = {
        at: {"accuracy": round(sum(vals)/len(vals), 3), "count": len(vals)}
        for at, vals in by_advice_type.items() if vals
    }

    worst = sorted(errors, key=lambda x: x["abs_xfm_error"], reverse=True)[:15]
    worst_predictions = [
        {"name": w["name"], "role": w["role"], "team": w["team"],
         "xfm_pred": w["xfm_pred"], "fm_actual": w["fm_actual"],
         "error": w["xfm_error"], "advice_type": w["advice_type_pred"],
         "advice_correct": w["advice_correct"]}
        for w in worst
    ]

    learning_notes = _generate_learning_notes(global_stats, role_stats, league_stats, oop_stats, fragility_stats)

    return {
        "analyzed_at": datetime.now().isoformat(),
        "round_num": round_num,
        "global": global_stats,
        "by_role": role_stats,
        "by_league": league_stats,
        "by_oop": oop_stats,
        "by_fragility": fragility_stats,
        "by_slot": slot_stats,
        "advice_accuracy": advice_accuracy_by_type,
        "worst_predictions": worst_predictions,
        "learning_notes": learning_notes,
    }


def _generate_learning_notes(global_stats, role_stats, league_stats, oop_stats, fragility_stats):
    notes = []
    bias = global_stats["xfm"]["mean"]
    if abs(bias) > 0.3:
        direction = "ottimista" if bias > 0 else "pessimista"
        notes.append(f"AI globalmente {direction}: bias medio xFM {bias:+.2f} FM")

    mae = global_stats["xfm"]["mae"]
    notes.append(f"Errore assoluto medio xFM: {mae:.2f} FM su {global_stats['n_players']} calciatori valutati")

    acc = global_stats.get("advice_accuracy", 0)
    if acc > 0:
        quality = "eccellente" if acc >= 0.85 else ("buona" if acc >= 0.70 else ("sufficiente" if acc >= 0.55 else "da migliorare"))
        notes.append(f"Accuratezza consigli AI: {acc:.0%} ({quality})")

    fhit = global_stats.get("fragility_hit_rate", 0)
    if fhit > 0:
        notes.append(f"Fragility Score: {fhit:.0%} delle fragility previste si sono verificate")

    for role, stats in role_stats.items():
        if stats["count"] >= MIN_SEGMENT_SIZE and abs(stats["mean"]) > 0.4:
            direction = "sovrastimati" if stats["mean"] > 0 else "sottostimati"
            notes.append(f"Ruolo {role}: {direction} di {abs(stats['mean']):.2f} FM in media")

    for league, stats in league_stats.items():
        if stats["count"] >= 3 and abs(stats["mean"]) > 0.5:
            direction = "sovrastimati" if stats["mean"] > 0 else "sottostimati"
            notes.append(f"Giocatori {league}: {direction} di {abs(stats['mean']):.2f} FM ({stats['count']} calciatori)")

    for tier, stats in oop_stats.items():
        if tier != "STANDARD" and stats["count"] >= 3 and abs(stats["mean"]) > 0.4:
            direction = "sovrastimati" if stats["mean"] > 0 else "sottostimati"
            notes.append(f"OOP {tier}: {direction} di {abs(stats['mean']):.2f} FM")

    for tier, stats in fragility_stats.items():
        if stats["count"] >= MIN_SEGMENT_SIZE and abs(stats["mean"]) > 0.5:
            direction = "sopravvalutati" if stats["mean"] > 0 else "sottovalutati"
            notes.append(f"Fragility {tier}: xFM {direction} di {abs(stats['mean']):.2f} FM")

    return notes


# -----------------------------------------------------------------
#  STEP 4: Calcola Correzioni Bias
# -----------------------------------------------------------------

def compute_bias_corrections(error_analysis, round_num):
    """
    Calcola i fattori correttivi da applicare alle predizioni future.
    Usa LEARNING_RATE per smorzare le correzioni ed evitare overcorrection.
    Un bias positivo (AI ottimista) -> correzione negativa.
    """
    by_role = error_analysis.get("by_role", {})
    by_league = error_analysis.get("by_league", {})
    by_oop = error_analysis.get("by_oop", {})
    by_frag = error_analysis.get("by_fragility", {})

    def _correction(bias_mean, count, lr=LEARNING_RATE):
        if count < MIN_SEGMENT_SIZE:
            return 0.0
        return round(-bias_mean * lr, 3)

    role_correction = {r: c for r, stats in by_role.items()
                       if (c := _correction(stats["mean"], stats["count"])) != 0.0}

    league_correction = {lg: c for lg, stats in by_league.items()
                         if (c := _correction(stats["mean"], stats["count"])) != 0.0}

    oop_correction = {t: c for t, stats in by_oop.items()
                      if t != "STANDARD" and (c := _correction(stats["mean"], stats["count"])) != 0.0}

    fragility_correction = {t: c for t, stats in by_frag.items()
                             if (c := _correction(stats["mean"], stats["count"])) != 0.0}

    advice_acc = {at: d["accuracy"] for at, d in error_analysis.get("advice_accuracy", {}).items()}
    global_stats = error_analysis.get("global", {})

    return {
        "generated_at": datetime.now().isoformat(),
        "rounds_analyzed": round_num,
        "n_players": global_stats.get("n_players", 0),
        "overall_mae": global_stats.get("xfm", {}).get("mae", 0.0),
        "overall_bias": global_stats.get("xfm", {}).get("mean", 0.0),
        "advice_accuracy_global": global_stats.get("advice_accuracy", 0.0),
        "fragility_hit_rate": global_stats.get("fragility_hit_rate", 0.0),
        "role_correction": role_correction,
        "league_correction": league_correction,
        "oop_correction": oop_correction,
        "fragility_correction": fragility_correction,
        "advice_accuracy_by_type": advice_acc,
        "learning_notes": error_analysis.get("learning_notes", []),
        "valid": round_num >= MIN_ROUNDS_FOR_LEARNING,
    }


# -----------------------------------------------------------------
#  STEP 5: Carica Correzioni (usato da valuation_engine)
# -----------------------------------------------------------------

def load_bias_corrections():
    """
    Carica le bias corrections dal file persistente.
    Ritorna un dizionario vuoto se il file non esiste o se non e valido.
    """
    if not os.path.exists(CORRECTIONS_PATH):
        return {}
    try:
        with open(CORRECTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data.get("valid", False):
            return {}
        return data
    except Exception as e:
        print(f"[AI Evaluator] Errore caricamento bias corrections: {e}")
        return {}


# -----------------------------------------------------------------
#  STEP 6: Applica Correzioni a xFM (usato da valuation_engine)
# -----------------------------------------------------------------

def apply_bias_correction_to_xfm(xfm, player, corrections):
    """
    Applica le correzioni bias apprese all'xFM di un singolo giocatore.

    Args:
        xfm: L'xFM calcolato prima della correzione
        player: Il dizionario del giocatore
        corrections: Le bias corrections caricate da load_bias_corrections()

    Returns:
        L'xFM corretto, arrotondato a 2 decimali.
    """
    if not corrections:
        return xfm

    total_correction = 0.0

    role = player.get("role", "")
    total_correction += corrections.get("role_correction", {}).get(role, 0.0)

    league = player.get("league_2526", "")
    total_correction += corrections.get("league_correction", {}).get(league, 0.0)

    oop_tier = player.get("oop_tier", "")
    if oop_tier:
        total_correction += corrections.get("oop_correction", {}).get(oop_tier, 0.0)

    fragilita = player.get("fragilita_score") or player.get("fragility_score") or 1
    frag_tier = "alta" if fragilita >= 3 else ("media" if fragilita >= 2 else "bassa")
    total_correction += corrections.get("fragility_correction", {}).get(frag_tier, 0.0)

    return round(xfm + total_correction, 2)


# -----------------------------------------------------------------
#  Helpers interni
# -----------------------------------------------------------------

def _save_error_analysis(error_analysis, errors, round_num):
    """Salva (o aggiorna) il file di analisi errori storico."""
    history = []
    if os.path.exists(ERROR_ANALYSIS_PATH):
        try:
            with open(ERROR_ANALYSIS_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
                history = existing.get("history", [])
        except Exception:
            pass

    history = [h for h in history if h.get("round_num") != round_num]
    history.append({
        "round_num": round_num,
        "analyzed_at": error_analysis["analyzed_at"],
        "global": error_analysis["global"],
        "by_role": error_analysis["by_role"],
        "by_league": error_analysis["by_league"],
        "by_oop": error_analysis["by_oop"],
        "by_fragility": error_analysis["by_fragility"],
        "by_slot": error_analysis["by_slot"],
        "advice_accuracy": error_analysis["advice_accuracy"],
        "worst_predictions": error_analysis["worst_predictions"],
        "learning_notes": error_analysis["learning_notes"],
    })

    output = {
        "last_updated": datetime.now().isoformat(),
        "snapshot_date": _get_snapshot_date(),
        "history": sorted(history, key=lambda x: x["round_num"]),
        "latest": error_analysis,
    }

    with open(ERROR_ANALYSIS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[AI Evaluator] Analisi errori salvata -> {ERROR_ANALYSIS_PATH}")


def _save_bias_corrections(corrections):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CORRECTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(corrections, f, ensure_ascii=False, indent=2)
    print(f"[AI Evaluator] Bias corrections salvate -> {CORRECTIONS_PATH}")


def _get_snapshot_date():
    snap = load_predictions_snapshot()
    if snap:
        return snap.get("metadata", {}).get("saved_at", "N/A")
    return "N/A"
