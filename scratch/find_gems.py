import json

players = json.load(open('processed_players_master.json', encoding='utf-8'))

for role, max_p in [('A', 35), ('C', 20), ('D', 18), ('P', 15)]:
    print(f"\n=== TOP INSOSPETTABILI RUOLO {role} (Max Prezzo {max_p} CR) ===")
    subset = [p for p in players if p['role'] == role and p.get('prezzo_cons', 1) <= max_p and p.get('titolarita', 0) >= 50]
    
    def score_player(p):
        xg = p.get('xg90_2526', 0) or 0
        xa = p.get('xa90_2526', 0) or 0
        rat = p.get('rating_2526', 0) or 0
        oop = 1.3 if p.get('is_oop') else 1.0
        g26 = p.get('gol_2627', 0) or 0
        a26 = p.get('assist_2627', 0) or 0
        if role == 'A':
            return (xg * 2.5 + xa * 1.2 + rat * 0.4 + (g26 * 0.5)) * oop
        elif role == 'C':
            return (xg * 2.0 + xa * 2.0 + rat * 0.5 + (g26 * 0.6 + a26 * 0.4)) * oop
        elif role == 'D':
            return (xg * 1.5 + xa * 2.2 + rat * 0.8 + (a26 * 0.5)) * oop
        else:
            gp = p.get('goals_prevented_2526', 0) or 0
            cs = p.get('clean_sheets_2526', 0) or 0
            return rat + gp * 0.2 + cs * 0.1

    subset.sort(key=lambda x: -score_player(x))
    for p in subset[:8]:
        xg = p.get('xg90_2526', 0) or 0
        xa = p.get('xa90_2526', 0) or 0
        rat = p.get('rating_2526', 0) or 0
        g26 = p.get('gol_2627', 0) or 0
        a26 = p.get('assist_2627', 0) or 0
        print(f"{p['name']:18} | {p['team']:11} | {p['prezzo_cons']:2}CR | Tit {p['titolarita']}% | xG90 {xg:.2f} | xA90 {xa:.2f} | Rat {rat:.2f} | 26/27: {g26}G/{a26}A | Slot: {p.get('slot_fascia')}")
