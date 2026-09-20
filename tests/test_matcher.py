import unittest
from src.player_matcher import clean_text, resolve_player

class TestPlayerMatcher(unittest.TestCase):
    def setUp(self):
        self.lookup_sample = {
            "esposito f p": {"Nome": "Esposito F.P.", "Squadra": "Inter", "R": "A", "Gf": 8},
            "esposito se": {"Nome": "Esposito Se.", "Squadra": "Cagliari", "R": "A", "Gf": 5},
            "martinez l": {"Nome": "Martinez L.", "Squadra": "Inter", "R": "A", "Gf": 24},
            "martinez jo": {"Nome": "Martinez Jo.", "Squadra": "Inter", "R": "P", "Gf": 0},
            "pellegrini lo": {"Nome": "Pellegrini Lo.", "Squadra": "Roma", "R": "C", "Gf": 7},
            "pellegrino m": {"Nome": "Pellegrino M.", "Squadra": "Fiorentina", "R": "A", "Gf": 4},
        }

    def test_clean_text(self):
        self.assertEqual(clean_text("Nico Paz!"), "nico paz")
        self.assertEqual(clean_text("Lautaro Martínez"), "lautaro martinez")
        self.assertEqual(clean_text("De Ketelaere  "), "de ketelaere")

    def test_disambiguation_esposito(self):
        # Match Francesco Pio Esposito
        res_fp = resolve_player("esposito f p", "Inter", self.lookup_sample)
        self.assertIsNotNone(res_fp)
        self.assertEqual(res_fp["Nome"], "Esposito F.P.")

        # Match Sebastiano Esposito
        res_se = resolve_player("esposito se", "Cagliari", self.lookup_sample)
        self.assertIsNotNone(res_se)
        self.assertEqual(res_se["Nome"], "Esposito Se.")

    def test_disambiguation_martinez(self):
        # Lautaro Martinez vs Josep Martinez sia con nome puntato che esteso che singolo cognome
        res_lautaro = resolve_player("martinez l", "Inter", self.lookup_sample, role="A")
        self.assertIsNotNone(res_lautaro)
        self.assertEqual(res_lautaro["Nome"], "Martinez L.")

        res_lautaro_full = resolve_player("lautaro martinez", "Inter", self.lookup_sample, role="A")
        self.assertIsNotNone(res_lautaro_full)
        self.assertEqual(res_lautaro_full["Nome"], "Martinez L.")

        res_josep = resolve_player("josep martinez", "Inter", self.lookup_sample, role="P")
        self.assertIsNotNone(res_josep)
        self.assertEqual(res_josep["Nome"], "Martinez Jo.")

        # Con cognome singolo 'martinez', il ruolo 'A' vs 'P' deve discriminare
        res_mart_a = resolve_player("martinez", "Inter", self.lookup_sample, role="A")
        self.assertEqual(res_mart_a["Nome"], "Martinez L.")

        res_mart_p = resolve_player("martinez", "Inter", self.lookup_sample, role="P")
        self.assertEqual(res_mart_p["Nome"], "Martinez Jo.")

    def test_disambiguation_thuram(self):
        thuram_lookup = {
            "thuram": {"Nome": "Thuram", "Squadra": "Inter", "R": "A"},
            "thuram k": {"Nome": "Thuram K.", "Squadra": "Juventus", "R": "C"}
        }
        res_m = resolve_player("marcus thuram", "Inter", thuram_lookup, role="A")
        self.assertEqual(res_m["Nome"], "Thuram")

        res_k = resolve_player("khephren thuram", "Juventus", thuram_lookup, role="C")
        self.assertEqual(res_k["Nome"], "Thuram K.")

        # Cognome singolo thuram con squadra e ruolo
        self.assertEqual(resolve_player("thuram", "Inter", thuram_lookup, role="A")["Nome"], "Thuram")
        self.assertEqual(resolve_player("thuram", "Juventus", thuram_lookup, role="C")["Nome"], "Thuram K.")

    def test_no_false_positive_on_single_unmatched_token(self):
        # Token sconosciuto ma con cognome simile non deve matchare a caso
        res = resolve_player("esposito sconosciuto", "Lecce", self.lookup_sample)
        self.assertIsNone(res)

    def test_match_player_name(self):
        from src.player_matcher import match_player_name
        self.assertTrue(match_player_name("Paz N.", "Nico Paz"))
        self.assertTrue(match_player_name("Martinez L.", "Lautaro Martinez"))
        self.assertTrue(match_player_name("Tavares N.", "Nuno Tavares"))
        self.assertTrue(match_player_name("Gudmundsson A.", "Gudmundsson"))
        self.assertTrue(match_player_name("Kean", "Kean"))

if __name__ == "__main__":
    unittest.main()
