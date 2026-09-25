import json
import os

def audit_dataset():
    path = "data/processed/processed_players_master.json"
    if not os.path.exists(path):
        print("Data file not found!")
        return

    with open(path, "r", encoding="utf-8") as f:
        players = json.load(f)

    print(f"Total players loaded: {len(players)}")

    issues = []
    anomalies = []

    # Check rule violations
    for p in players:
        name = p.get("name", "Unknown")
        team = p.get("team", "Unknown")
        role = p.get("role", "Unknown")
        tit = p.get("titolarita")
        ovr = p.get("ovr")
        prezzo = p.get("prezzo_cons", 0)
        max_bid = p.get("max_bid", 0)
        fvm = p.get("fvm", 0)
        xfm = p.get("xfm")
        delta = p.get("delta_xfm")
        fm_2627 = p.get("fm_2627")
        mv_2627 = p.get("mv_2627")

        if tit is None or not (0 <= tit <= 100):
            issues.append(f"{name} ({team}): titolarita non valida ({tit})")
        if ovr is None or not (45 <= ovr <= 98):
            issues.append(f"{name} ({team}): ovr non valido ({ovr})")
        if max_bid < prezzo and prezzo > 1:
            issues.append(f"{name} ({team}): max_bid ({max_bid}) < prezzo_cons ({prezzo})")
        
        # Check delta xfm consistency: delta should roughly equal fm - xfm
        if fm_2627 is not None and xfm is not None and delta is not None:
            expected_delta = round(fm_2627 - xfm, 2)
            if abs(expected_delta - delta) > 0.15:
                anomalies.append(f"{name} ({team}): delta_xfm incongruente: registrato {delta} vs calcolato {expected_delta} (FM {fm_2627} - xFM {xfm})")

        # Check goalkeeper prices: is there any goalkeeper with absurd price?
        if role == 'P' and prezzo > 200:
            anomalies.append(f"{name} ({team}): prezzo portiere anomalo ({prezzo} CR)")

        # Check reserve players with high prices
        if tit is not None and tit < 30 and prezzo > 40:
            anomalies.append(f"{name} ({team}): riserva (tit {tit}%) con prezzo elevato ({prezzo} CR)")

        # Check slot_fascia vs prezzo
        slot = p.get("slot_fascia", "")
        if "1° Slot" in slot and prezzo < 15 and role in ['A', 'C']:
            anomalies.append(f"{name} ({team}): 1° Slot con prezzo troppo basso ({prezzo} CR)")

    print(f"\n--- REGOLE BASE VIOLATE: {len(issues)} ---")
    for iss in issues[:15]:
        print("  -", iss)

    print(f"\n--- ANOMALIE DI VALUTAZIONE/DATI: {len(anomalies)} ---")
    for an in anomalies[:15]:
        print("  -", an)

    # Check tactical db consistency
    tactical_path = "config/tactical_db.json"
    if os.path.exists(tactical_path):
        with open(tactical_path, "r", encoding="utf-8") as f:
            tactical = json.load(f)
        print(f"\n--- SQUADRE TATTICHE VERIFICATE: {len(tactical)}/20 ---")
        teams_in_players = set(p.get("team") for p in players)
        for t in teams_in_players:
            if t not in tactical:
                print(f"  - Squadra {t} non presente in tactical_db.json!")

if __name__ == "__main__":
    audit_dataset()
