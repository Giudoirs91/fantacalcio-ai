import os
import sys
import json
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
PROCESSED_FILE = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
CONFIG_FILE = os.path.join(ROOT_DIR, "config", "league_settings.json")

def recalibrate_dataset():
    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        players = json.load(f)

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        league_settings = json.load(f)

    num_teams = league_settings.get("num_teams", 8)

    print(f"Caricati {len(players)} calciatori. Inizio ricalibrazione basata su prime 3 giornate e infortuni...")

    # Mappa prima delle modifiche per confronto
    before_map = {p['name']: (p.get('slot_fascia'), p.get('slot_num'), p.get('ovr'), p.get('prezzo_cons'), p.get('fvm')) for p in players}

    for p in players:
        role = p['role']
        ovr = float(p.get('ovr', 60))
        fvm = float(p.get('fvm', 10))
        prezzo_cons = float(p.get('prezzo_cons', 5))

        # --- 1. IMPATTO REALE 2026/27 (PRIME 3 GIORNATE) ---
        p26 = p.get('presenze_2627', 0)
        s26 = p.get('starts_2627', 0)
        g26 = p.get('gol_2627', 0)
        a26 = p.get('assist_2627', 0)
        fm26 = p.get('fm_2627')
        mv26 = p.get('mv_2627')
        dq = float(p.get('diff_q', 0) or 0)

        perf_boost = 0.0
        fvm_mult = 1.0

        if p26 > 0:
            # Impatto gol e assist
            if role == 'A':
                perf_boost += g26 * 1.8 + a26 * 1.0
            elif role == 'C':
                perf_boost += g26 * 2.5 + a26 * 1.5
            elif role == 'D':
                perf_boost += g26 * 3.5 + a26 * 2.0
            elif role == 'P':
                cs26 = p.get('clean_sheets_2627', 0)
                perf_boost += cs26 * 1.5

            # Impatto Fantamedia
            if fm26 is not None and p26 >= 2:
                if fm26 >= 8.5:
                    perf_boost += 3.5
                    fvm_mult += 0.35
                elif fm26 >= 7.5:
                    perf_boost += 2.0
                    fvm_mult += 0.20
                elif fm26 >= 6.8:
                    perf_boost += 1.0
                    fvm_mult += 0.10
                elif fm26 <= 5.3:
                    perf_boost -= 2.5
                    fvm_mult -= 0.20
                elif fm26 <= 5.8:
                    perf_boost -= 1.2
                    fvm_mult -= 0.10

            # Trend di mercato reale (diff_q)
            perf_boost += dq * 0.8
            fvm_mult += dq * 0.05

            # Titolarità conquistata sul campo
            if s26 >= 3:
                perf_boost += 1.5
            elif s26 == 0 and p26 > 0:
                perf_boost -= 0.8 # Solo subentrante

        elif p.get('is_in_11', False) and not p.get('is_injured', False):
            # Titolare presunto che non ha giocato nemmeno 1 minuto
            perf_boost -= 2.0
            fvm_mult -= 0.15

        # --- 2. IMPATTO INFORTUNI REALI (DEPREZZAMENTO E DECLASSAMENTO SLOT) ---
        is_inj = p.get('is_injured', False)
        gp = p.get('giornate_perse', 0)
        motivo = str(p.get('infortunio_motivo', '')).lower()
        rientro = str(p.get('infortunio_rientro', '')).lower()

        inj_penalty = 0.0
        if is_inj:
            if gp >= 15 or 'crociato' in motivo or 'mesi' in motivo or '2027' in rientro:
                # Infortunio gravissimo (es. Scamacca)
                inj_penalty = 14.0
                fvm_mult *= 0.25
                p['is_flop'] = True
            elif gp >= 8 or 'novembre' in rientro or 'dicembre' in rientro:
                # Infortunio medio-lungo (2-3 mesi)
                inj_penalty = 8.0
                fvm_mult *= 0.50
            elif gp >= 4 or 'ottobre' in rientro:
                # Infortunio medio (1 mese)
                inj_penalty = 4.0
                fvm_mult *= 0.75
            else:
                # Stop breve (rientro settembre)
                inj_penalty = 1.5
                fvm_mult *= 0.90

        # Fragilità cronica
        if p.get('is_chronic_fragile', False) or p.get('fragilita_score', 1) >= 3:
            inj_penalty += 1.5
            fvm_mult *= 0.92

        # Applica modifiche
        new_ovr = np.clip(ovr + perf_boost - inj_penalty, 45.0, 98.0)
        new_fvm = max(1.0, fvm * max(0.15, fvm_mult))

        p['ovr'] = int(round(new_ovr))
        p['fantascore'] = round(new_ovr, 1)
        p['fvm'] = round(new_fvm, 1)

    # --- 3. RIASSEGNAZIONE SLOT E FASCE (1°-8° Slot su 8 squadre) ---
    by_role = {'P': [], 'D': [], 'C': [], 'A': []}
    for p in players:
        by_role[p['role']].append(p)

    max_slots_role = {'P': 3, 'D': 8, 'C': 8, 'A': 6}

    for r, r_players in by_role.items():
        # Ordina per il nuovo OVR e FVM ricalcolati
        r_players.sort(key=lambda x: (-x['ovr'], -x['fvm'], -float(x.get('fm_2627') or 0)))
        max_s = max_slots_role[r]

        for rank, pl in enumerate(r_players, 1):
            slot_num = ((rank - 1) // num_teams) + 1
            pl['slot_num'] = slot_num
            if slot_num <= max_s:
                pl['slot_fascia'] = f"{slot_num}° Slot {r}"
            else:
                pl['slot_fascia'] = f"Riserva {r}"

            # Fascia descrittiva
            ovr_val = pl['ovr']
            if ovr_val >= 92: pl['fascia'] = "1ª Fascia (Top Assoluto)"
            elif ovr_val >= 84: pl['fascia'] = "2ª Fascia (Semi-Top / Titolare di Lusso)"
            elif ovr_val >= 75: pl['fascia'] = "3ª Fascia (Ottimo Titolare)"
            elif ovr_val >= 68: pl['fascia'] = "4ª Fascia (Scommessa / Copertura)"
            else: pl['fascia'] = "5ª Fascia (Low Cost / Slot 1 Credito)"

    # --- 4. RICALIBRAZIONE RIGOROSA PREZZI CONSIGLIATI (MONTEPREMI 8000 CR) ---
    total_league_budget = num_teams * league_settings.get("total_budget", 1000)
    slots_cfg = league_settings.get("slots", {
        "P": {"max": 3, "budget_target_pct": 0.07},
        "D": {"max": 8, "budget_target_pct": 0.11},
        "C": {"max": 8, "budget_target_pct": 0.22},
        "A": {"max": 6, "budget_target_pct": 0.60}
    })

    role_targets = {
        'P': int(round(total_league_budget * slots_cfg.get('P', {}).get('budget_target_pct', 0.06))),
        'D': int(round(total_league_budget * slots_cfg.get('D', {}).get('budget_target_pct', 0.18))),
        'C': int(round(total_league_budget * slots_cfg.get('C', {}).get('budget_target_pct', 0.32))),
        'A': int(round(total_league_budget * slots_cfg.get('A', {}).get('budget_target_pct', 0.44)))
    }
    diff_tot = total_league_budget - sum(role_targets.values())
    if diff_tot != 0:
        role_targets['A'] += diff_tot

    role_caps = {'P': 55, 'D': 85, 'C': 210, 'A': 360}

    for r, r_players in by_role.items():
        k_draftable = num_teams * max_slots_role[r]
        target = role_targets[r]
        cap = role_caps[r]

        top_p = r_players[:k_draftable]
        bench_p = r_players[k_draftable:]

        for p in bench_p:
            p['prezzo_cons'] = 1
            p['max_bid'] = 2

        scores = []
        for p in top_p:
            ovr_excess = max(1.0, float(p['ovr'] - 52))
            fvm_val = max(1.0, float(p['fvm']))
            if r == 'D':
                score = (fvm_val ** 0.85) * (ovr_excess ** 0.5)
            elif r == 'P':
                score = (fvm_val ** 0.90) * (ovr_excess ** 0.4)
            else:
                score = (fvm_val ** 0.95) * (ovr_excess ** 0.3)
            scores.append(score)

        sum_scores = sum(scores) if sum(scores) > 0 else 1.0
        discretionary = max(0, target - k_draftable)

        for i, p in enumerate(top_p):
            alloc = 1 + int(round(discretionary * (scores[i] / sum_scores)))
            p['prezzo_cons'] = min(cap, max(1, alloc))

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

    # --- 5. RICALCOLO ADVICE AI ---
    from src.valuation_engine import determine_advice_tag
    for p in players:
        advice, advice_type = determine_advice_tag(p)
        p["ai_advice"] = advice
        p["ai_advice_type"] = advice_type
        p["consiglio"] = advice

    # Riordino finale
    players.sort(key=lambda x: (x['role'], x.get('slot_num', 1), -x['ovr'], -x['prezzo_cons']))

    # Salva file
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=2, ensure_ascii=False)

    root_processed = os.path.join(ROOT_DIR, "processed_players_master.json")
    if os.path.exists(root_processed):
        with open(root_processed, 'w', encoding='utf-8') as f:
            json.dump(players, f, indent=2, ensure_ascii=False)

    print("Salvataggio completato con successo!")

    # Stampa alcuni confronti chiave
    print("\n=== VERIFICA CONFRONTO PRIMA VS DOPO ===")
    test_names = ['Kamara H.', 'Raimondo', 'Frattesi', 'Cissè A.', 'Malen', 'Scamacca', 'Kolo Muani', 'Varela G.', 'De Gea', 'Lautaro']
    for tn in test_names:
        for p in players:
            if tn.lower() in p['name'].lower():
                b_fascia, b_num, b_ovr, b_cons, b_fvm = before_map.get(p['name'], ('-', 0, 0, 0, 0))
                print(f"{p['name']:<16} | VECCHIO: {b_fascia:<12} (OVR {b_ovr}, Cons {b_cons} CR) -> NUOVO: {p['slot_fascia']:<12} (OVR {p['ovr']}, Cons {p['prezzo_cons']} CR) [Advice: {p['ai_advice_type']}]")
                break

if __name__ == '__main__':
    recalibrate_dataset()
