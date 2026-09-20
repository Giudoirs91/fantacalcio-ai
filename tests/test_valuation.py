import unittest
from src.valuation_engine import compute_continuous_ovr_and_price, calcola_impatto_infortunio

class TestValuationEngine(unittest.TestCase):
    def test_continuous_price_monotonicity(self):
        # Verifica che a FVM più alto corrisponda OVR e Prezzo non decrescente
        for role in ['P', 'D', 'C', 'A']:
            prev_ovr = 0
            prev_price = 0
            for fvm in range(1, 400, 10):
                ovr, price = compute_continuous_ovr_and_price(role, fvm, is_in_11=True)
                self.assertGreaterEqual(ovr, prev_ovr, f"OVR non monotono per {role} a FVM {fvm}")
                self.assertGreaterEqual(price, prev_price, f"Prezzo non monotono per {role} a FVM {fvm}")
                self.assertGreaterEqual(price, 1)
                prev_ovr = ovr
                prev_price = price

    def test_injury_impact(self):
        # Infortunio a Maggio 2027 (stagione finita)
        giornate, pen_ovr, mult_prc = calcola_impatto_infortunio("15/05/2027")
        self.assertEqual(giornate, 35)
        self.assertAlmostEqual(mult_prc, 0.10)

        # Infortunio lieve (Agosto 2026)
        giornate, pen_ovr, mult_prc = calcola_impatto_infortunio("28/08/2026")
        self.assertEqual(giornate, 0)
        self.assertEqual(mult_prc, 1.0)

    def test_budget_calibration_exact_sum(self):
        from src.valuation_engine import calibrate_budget_prices
        # Crea un mock di 300 giocatori (30 P, 90 D, 90 C, 90 A)
        sample_players = []
        pid = 1
        for role, count in [('P', 30), ('D', 90), ('C', 90), ('A', 90)]:
            for i in range(count):
                sample_players.append({
                    'id': pid,
                    'name': f"Player_{pid}",
                    'role': role,
                    'ovr': max(50, 95 - i),
                    'prezzo_cons': max(1, 150 - i * 2),
                    'fvm': max(1, 100 - i)
                })
                pid += 1

        settings = {
            "num_teams": 8,
            "total_budget": 1000,
            "slots": {
                "P": {"max": 3, "budget_target_pct": 0.06},
                "D": {"max": 8, "budget_target_pct": 0.18},
                "C": {"max": 8, "budget_target_pct": 0.32},
                "A": {"max": 6, "budget_target_pct": 0.44}
            }
        }

        calibrated = calibrate_budget_prices(sample_players, settings)

        # Calcola la somma dei primi 200 slot (24 P, 64 D, 64 C, 48 A)
        counts = {'P': 24, 'D': 64, 'C': 64, 'A': 48}
        targets = {'P': 480, 'D': 1440, 'C': 2560, 'A': 3520}

        by_role = {'P': [], 'D': [], 'C': [], 'A': []}
        for p in calibrated:
            by_role[p['role']].append(p)

        total_drafted = 0
        for r, k in counts.items():
            top = by_role[r][:k]
            role_sum = sum(p['prezzo_cons'] for p in top)
            self.assertEqual(role_sum, targets[r], f"Budget target non rispettato per ruolo {r}")
            total_drafted += role_sum

        self.assertEqual(total_drafted, 8000, "Somma totale dei 200 slot deve essere esattamente 8000 CR")

    def test_advice_tag_hierarchy(self):
        from src.valuation_engine import determine_advice_tag
        
        # Giocatore con flop flag: deve prioritizzare l'allerta flop rispetto a rigorista
        p_flop_rigorista = {
            "name": "Flop Player",
            "role": "A",
            "ovr": 72,
            "slot_num": 3,
            "titolarita": 80,
            "is_flop": True,
            "is_rigorista_1": True,
            "is_injured": False
        }
        tag, tag_type = determine_advice_tag(p_flop_rigorista)
        self.assertIn("FLOP", tag)
        self.assertEqual(tag_type, "flop")

        # Giocatore top assoluto sano
        p_top = {
            "name": "Super Top",
            "role": "A",
            "ovr": 94,
            "slot_num": 1,
            "titolarita": 95,
            "is_rigorista_1": True,
            "is_injured": False
        }
        tag_top, tag_type_top = determine_advice_tag(p_top)
        self.assertIn("TOP", tag_top)
        self.assertEqual(tag_type_top, "top")

if __name__ == "__main__":
    unittest.main()

