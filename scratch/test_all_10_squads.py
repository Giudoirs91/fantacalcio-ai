import json

with open('processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

real_prices = {
    'meret': 101, 'milinkovic-savic v.': 1, 'contini': 1,
    'svilar': 136, 'gollini': 1, 'de marzi': 1, 'bijlow': 5,
    'de gea': 56, 'christensen o.': 1, 'lezzerini': 1,
    'perri': 41, 'caprile': 39, 'corvi': 6,
    'vicario': 77, 'grabara': 1, 'falcone': 1,
    'martinez jo.': 120, 'provedel': 9, 'maignan': 93, 'carnesecchi': 96,
    'kalulu': 55, 'mancini': 50, 'bellanova': 15, 'tavares n.': 33, 'gila': 45,
    'bremer': 63, 'hermoso': 12, 'wesley': 67, 'rrahmani': 41, 'molina n.': 77, 'akanji': 57,
    'valeri': 1, 'gallo': 1, 'kabasele': 1, 'marcandalli': 1, 'ostigard': 1,
    'vasquez': 2, 'obert': 1, 'mina': 2, 'pedraza': 1, 'zappacosta': 13, 'lucumì': 26,
    'kelly l.': 1, 'obrador': 5, 'doig': 1, 'gatti': 1,
    'mctominay': 135, 'baturina': 136, 'calò': 10, 'bernabè': 2, 'vergara': 45, 'da cunha': 45, 'mckennie': 44,
    'frattesi': 69, 'koné m.': 33, 'calhanoglu': 137, 'mastantuono': 80, 'barella': 68, 'paz n.': 190,
    'bernardeschi': 46, 'odgaard': 1, 'grillitsch': 1, 'jones c.': 19,
    'zaniolo': 63, 'busio': 1, 'fazzini': 1, 'thorstvedt': 1, 'perrone': 1, 'adzic': 1, 'douglas luiz': 2,
    'martinez l.': 415, 'scamacca': 137, 'krstovic': 61, 'esposito se.': 36, 'raimondo': 30, 'bowie': 3, 'kevin carlos': 1, 'vitinha o.': 1,
    'malen': 442, 'kean': 79, 'bonny': 1, 'douvikas': 205, 'piccoli': 51, 'thuram': 255, 'soulé': 110,
    'kolo muani': 264, 'ramos g.': 237, 'camarda': 1,
    'rovella': 38, 'bastoni': 55, 'de bruyne': 115, 'dimarco': 90, 'orsolini': 110, 'zaccagni': 105,
    'dybala': 140, 'buongiorno': 45, 'lobotka': 35, 'conceicao': 45
}

def get_cost(p_name):
    clean = p_name.lower().strip()
    if clean in real_prices:
        return real_prices[clean]
    for p in players:
        if p['name'].lower() == clean or p['name'].lower().startswith(clean):
            return p.get('prezzo_cons', 1)
    return 1

# Calibrated 5 Mantra Squads:
squads = {
    # 1. Mantra 4-3-3: Lautaro (415) + Napoli Allegri (103) + Difesa Top
    "mantra_433": {
        "formation": "4-3-3",
        "starters": {
            "P": ["Meret"],
            "D": ["Bellanova", "Bremer", "Kalulu", "Tavares N."],
            "C": ["Koné M.", "Barella", "Calò"],
            "A": ["Conceicao", "Martinez L.", "Zaniolo"]
        },
        "bench": {
            "P": ["Milinkovic-Savic V.", "Contini"],
            "D": ["Valeri", "Gallo", "Hermoso", "Marcandalli"], # 4 starters + 4 bench = 8 D
            "C": ["Bernabè", "Busio", "Fazzini", "Thorstvedt", "Perrone"], # 3 starters + 5 bench = 8 C
            "A": ["Bowie", "Kevin Carlos", "Vitinha O."] # 3 starters + 3 bench = 6 A
        }
    },
    # 2. Mantra 4-2-3-1: Malen Bomber (442) + Nico Paz (190) + De Gea Low-Cost (58)
    "mantra_4231": {
        "formation": "4-2-3-1",
        "starters": {
            "P": ["De Gea"],
            "D": ["Bellanova", "Akanji", "Rrahmani", "Valeri"],
            "C": ["Koné M.", "Perrone"],
            "A": ["Vergara", "Paz N.", "Da Cunha", "Malen"]
        },
        "bench": {
            "P": ["Christensen O.", "Lezzerini"],
            "D": ["Gallo", "Vasquez", "Kabasele", "Obert"], # 4 starters + 4 bench = 8 D
            "C": ["Calò", "Bernabè", "Busio", "Fazzini", "Thorstvedt", "Adzic"], # 2 starters + 6 bench = 8 C
            "A": ["Kevin Carlos", "Vitinha O."] # 4 starters + 2 bench = 6 A
        }
    },
    # 3. Mantra 3-5-2: Thuram (255) + Scamacca (137) + McTominay (135) + De Gea (58)
    "mantra_352": {
        "formation": "3-5-2",
        "starters": {
            "P": ["De Gea"],
            "D": ["Bremer", "Bastoni", "Hermoso"],
            "C": ["Bellanova", "McTominay", "Lobotka", "Barella", "Tavares N."],
            "A": ["Thuram", "Scamacca"]
        },
        "bench": {
            "P": ["Christensen O.", "Lezzerini"],
            "D": ["Valeri", "Gallo", "Marcandalli", "Ostigard", "Kabasele"], # 3 starters + 5 bench = 8 D
            "C": ["Bernabè", "Busio", "Calò"], # 5 starters + 3 bench = 8 C
            "A": ["Raimondo", "Bowie", "Kevin Carlos", "Bonny"] # 2 starters + 4 bench = 6 A
        }
    },
    # 4. Mantra 3-4-2-1: De Bruyne (115) + Zaccagni (105) + Scamacca (137) + Griglia Torino/Cagliari (86)
    "mantra_3421": {
        "formation": "3-4-2-1",
        "starters": {
            "P": ["Perri"],
            "D": ["Kalulu", "Bremer", "Rrahmani"],
            "C": ["Bellanova", "Calhanoglu", "Koné M.", "Tavares N."],
            "A": ["De Bruyne", "Zaccagni", "Scamacca"]
        },
        "bench": {
            "P": ["Caprile", "Corvi"],
            "D": ["Valeri", "Gallo", "Hermoso", "Marcandalli", "Ostigard"], # 3 starters + 5 bench = 8 D
            "C": ["Calò", "Bernabè", "Busio", "Fazzini"], # 4 starters + 4 bench = 8 C
            "A": ["Kean", "Bowie", "Kevin Carlos"] # 3 starters + 3 bench = 6 A
        }
    },
    # 5. Mantra 4-3-1-2: Rombo D-Factor con Dybala (140) + Scamacca (137) + Nico Paz (190) + Svilar (136)
    "mantra_4312": {
        "formation": "4-3-1-2",
        "starters": {
            "P": ["Svilar"],
            "D": ["Bellanova", "Bremer", "Bastoni", "Tavares N."],
            "C": ["Rovella", "Barella", "Calò"],
            "A": ["Paz N.", "Dybala", "Scamacca"]
        },
        "bench": {
            "P": ["Gollini", "De Marzi"],
            "D": ["Valeri", "Gallo", "Marcandalli", "Kabasele"], # 4 starters + 4 bench = 8 D
            "C": ["Bernabè", "Busio", "Fazzini", "Thorstvedt", "Perrone"], # 3 starters + 5 bench = 8 C
            "A": ["Raimondo", "Bowie", "Kevin Carlos"] # 3 starters + 3 bench = 6 A
        }
    }
}

for sq_id, sq in squads.items():
    tot = 0
    p_counts = {}
    for r in ['P', 'D', 'C', 'A']:
        st = sq['starters'].get(r, [])
        bn = sq['bench'].get(r, [])
        all_r = st + bn
        p_counts[r] = len(all_r)
        for n in all_r:
            tot += get_cost(n)
    total_players = sum(p_counts.values())
    rem = 1000 - tot
    print(f"[{sq_id}] Total: {tot} CR | Rem: {rem} CR | Counts: {p_counts} (Total: {total_players})")
    assert total_players == 25, f"Error: expected 25 players, got {total_players}"
    assert p_counts['P'] == 3, "P must be 3"
    assert p_counts['D'] == 8, "D must be 8"
    assert p_counts['C'] == 8, "C must be 8"
    assert p_counts['A'] == 6, "A must be 6"
    assert tot <= 1000, f"Error: over budget by {tot - 1000}"
    assert rem >= 20, f"Error: buffer too low ({rem})"

print("\nALL 5 MANTRA SQUADS PASS VALIDATION!")
