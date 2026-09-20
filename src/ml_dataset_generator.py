import os
import json
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYERS_MASTER_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
OUT_CSV_PATH = os.path.join(ROOT_DIR, "data", "processed", "ml_training_dataset.csv")
OUT_JSON_PATH = os.path.join(ROOT_DIR, "data", "processed", "ml_training_dataset.json")

def generate_ml_training_dataset():
    """
    Estrae e consolida tutte le feature pre-stagione (anagrafiche, storiche, fisiche, infortuni)
    e i target di rendimento effettivo (minuti, voti, gol, assist, fantamedia, ROI)
    per addestrare e validare modelli predittivi di Machine Learning.
    """
    if not os.path.exists(PLAYERS_MASTER_PATH):
        raise FileNotFoundError(f"File {PLAYERS_MASTER_PATH} non trovato. Esegui prima la pipeline.")

    with open(PLAYERS_MASTER_PATH, "r", encoding="utf-8") as f:
        players = json.load(f)

    rows = []
    for p in players:
        # Features di input pre-stagione
        role = p.get("role", "C")
        role_p = 1 if role == "P" else 0
        role_d = 1 if role == "D" else 0
        role_c = 1 if role == "C" else 0
        role_a = 1 if role == "A" else 0

        fvm = float(p.get("fvm", 1.0) or 1.0)
        qta = float(p.get("qta", 1.0) or 1.0)
        ovr = float(p.get("ovr", 70.0) or 70.0)
        prezzo_cons = float(p.get("prezzo_cons", 1.0) or 1.0)
        titolarita_pct = float(p.get("titolarita", 50.0) or 50.0)

        # Feature infortuni e affidabilità fisica
        fragility_score = float(p.get("fragility_score", 10.0) or 10.0)
        partite_saltate_tot = int(p.get("partite_saltate_totali", 0) or 0)
        giorni_stop_tot = int(p.get("giorni_stop_totali", 0) or 0)
        disponibilita_pct = float(p.get("disponibilita_pct", 100.0) or 100.0)
        recidive = int(p.get("recidive_muscolari", 0) or 0)
        is_injured = 1 if p.get("is_injured") else 0

        # Feature tattiche e storiche 2025/26
        is_rigorista = 1 if p.get("is_rigorista_1") or p.get("is_rigorista_2") else 0
        is_oop = 1 if p.get("is_oop") else 0
        mv_2526 = float(p.get("mv", 6.0) or 6.0)
        fm_2526 = float(p.get("fm", 6.0) or 6.0)
        xg90_2526 = float(p.get("xg90_2526", 0.0) or 0.0)
        xa90_2526 = float(p.get("xa90_2526", 0.0) or 0.0)
        rating_2526 = float(p.get("rating_2526", 6.5) or 6.5)
        presenze_2526 = int(p.get("presenze", 0) or 0)

        # Target reali stagione in corso (2026/27)
        presenze_2627 = int(p.get("presenze_2627", 0) or 0)
        starts_2627 = int(p.get("starts_2627", 0) or 0)
        minuti_2627 = int(p.get("minuti_2627", 0) or 0)
        gol_2627 = int(p.get("gol_2627", 0) or 0)
        assist_2627 = int(p.get("assist_2627", 0) or 0)
        mv_2627 = float(p.get("mv_2627", 0.0) or 0.0) if p.get("mv_2627") is not None else np.nan
        fm_2627 = float(p.get("fm_2627", 0.0) or 0.0) if p.get("fm_2627") is not None else np.nan
        tot_bonus_2627 = float(p.get("tot_bonus_2627", 0.0) or 0.0)
        tot_malus_2627 = float(p.get("tot_malus_2627", 0.0) or 0.0)
        xg90_2627 = float(p.get("xg90_2627", 0.0) or 0.0) if p.get("xg90_2627") is not None else np.nan
        xa90_2627 = float(p.get("xa90_2627", 0.0) or 0.0) if p.get("xa90_2627") is not None else np.nan

        # Target derivati
        # ROI Punti per Credito
        roi_fm_su_prezzo = round(fm_2627 / prezzo_cons, 4) if (not np.isnan(fm_2627) and fm_2627 > 0 and prezzo_cons > 0) else np.nan

        rows.append({
            "player_id": p.get("id"),
            "name": p.get("name"),
            "team": p.get("team"),
            "role": role,
            "role_P": role_p,
            "role_D": role_d,
            "role_C": role_c,
            "role_A": role_a,
            "fvm": fvm,
            "qta": qta,
            "ovr": ovr,
            "prezzo_cons": prezzo_cons,
            "titolarita_pct": titolarita_pct,
            "titolarita": titolarita_pct,
            "fragility_score": fragility_score,
            "partite_saltate_tot": partite_saltate_tot,
            "giorni_stop_tot": giorni_stop_tot,
            "disponibilita_pct": disponibilita_pct,
            "recidive_muscolari": recidive,
            "is_injured_initial": is_injured,
            "is_rigorista": is_rigorista,
            "is_oop": is_oop,
            "presenze_2526": presenze_2526,
            "mv_2526": mv_2526,
            "fm_2526": fm_2526,
            "xg90_2526": xg90_2526,
            "xa90_2526": xa90_2526,
            "rating_2526": rating_2526,
            # Target features per l'addestramento
            "presenze_2627": presenze_2627,
            "starts_2627": starts_2627,
            "minuti_2627": minuti_2627,
            "gol_2627": gol_2627,
            "assist_2627": assist_2627,
            "tot_bonus_2627": tot_bonus_2627,
            "tot_malus_2627": tot_malus_2627,
            "mv_2627": mv_2627,
            "fm_2627": fm_2627,
            "xg90_2627": xg90_2627,
            "xa90_2627": xa90_2627,
            "roi_fm_su_prezzo": roi_fm_su_prezzo,
            "target_fanta_media": fm_2627,
            "target_gol": gol_2627,
            "target_assist": assist_2627,
            "target_minuti": minuti_2627,
            "target_roi_fvm": roi_fm_su_prezzo
        })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CSV_PATH), exist_ok=True)
    df.to_csv(OUT_CSV_PATH, index=False, encoding="utf-8")
    
    with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"-> [MLDataset] Dataset di addestramento generato con successo: {len(df)} record.")
    print(f"   CSV:  {OUT_CSV_PATH}")
    print(f"   JSON: {OUT_JSON_PATH}")
    return df

if __name__ == "__main__":
    generate_ml_training_dataset()
