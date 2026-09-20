import openpyxl
import json

wb = openpyxl.load_workbook('data/raw/Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx', data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

listone_players = {}
for r in rows[2:]:
    if r[3] is not None:
        name = str(r[3]).strip()
        role = str(r[1]).strip()
        team = str(r[4]).strip()
        qt = int(r[5]) if r[5] is not None else 1
        listone_players[(name.lower(), role)] = {'name': name, 'role': role, 'team': team, 'qt': qt}

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    master = json.load(f)
master_dict = {(p['name'].lower().strip(), p['role']): p for p in master}

def get_p(name, role):
    key = (name.lower().strip(), role)
    if key in listone_players:
        lp = listone_players[key]
        mp = master_dict.get(key, {})
        return {
            'name': lp['name'],
            'role': lp['role'],
            'team': lp['team'],
            'price': mp.get('prezzo_cons', lp['qt']),
            'ovr': mp.get('ovr', 75)
        }
    for (k_name, k_role), lp in listone_players.items():
        if k_role == role and (name.lower() in k_name or k_name in name.lower()):
            mp = master_dict.get((k_name, k_role), {})
            return {
                'name': lp['name'],
                'role': lp['role'],
                'team': lp['team'],
                'price': mp.get('prezzo_cons', lp['qt']),
                'ovr': mp.get('ovr', 75)
            }
    return None

squads = [
    {
        'id': 'squad_343',
        'name': "L'Armata Pesante — Lautaro Martinez & Tridente Top",
        'formation': '3-4-3',
        'starters': {
            'P': ['Meret'],
            'D': ['Dimarco', 'Tavares N.', 'Kalulu'],
            'C': ['McTominay', 'Baturina', 'Bernabè', 'Colpani'],
            'A': ['Martinez L.', 'Scamacca', 'Piccoli']
        },
        'bench': {
            'P': ['Milinkovic-Savic V.', 'Contini'],
            'D': ['Bellanova', 'Gila', 'Chalobah T.', 'Patric', 'De Silvestri'],
            'C': ['Frendrup', 'Ferguson', 'Deiola', 'Zarraga'],
            'A': ['Diao', 'Raimondo', 'De Martis']
        }
    },
    {
        'id': 'squad_433',
        'name': 'La Fortezza Modificatore — Svilar & Malen Bomber',
        'formation': '4-3-3',
        'starters': {
            'P': ['Svilar'],
            'D': ['Kalulu', 'Bremer', 'Akanji', 'Rrahmani'],
            'C': ['Baturina', 'Frattesi', 'Bernabè'],
            'A': ['Malen', 'Kean', 'Raimondo']
        },
        'bench': {
            'P': ['Gollini', 'De Marzi'],
            'D': ['Tavares N.', 'Bellanova', 'Patric', 'De Silvestri'],
            'C': ['Colpani', 'Ferguson', 'Frendrup', 'Deiola', 'Zarraga'],
            'A': ['Piccoli', 'Trepy', 'De Martis']
        }
    },
    {
        'id': 'squad_4231',
        'name': 'La Ragnatela dei Trequartisti — Calhanoglu & Nico Paz',
        'formation': '4-2-3-1',
        'starters': {
            'P': ['De Gea'],
            'D': ['Akanji', 'Kalulu', 'Tavares N.', 'Doig'],
            'C': ['Calhanoglu', 'Paz N.', 'Baturina', 'Barella', 'Bernabè'],
            'A': ['Douvikas']
        },
        'bench': {
            'P': ['Christensen O.', 'Lezzerini'],
            'D': ['Bellanova', 'Patric', 'Chalobah T.', 'De Silvestri'],
            'C': ['Colpani', 'Ferguson', 'Frendrup'],
            'A': ['Diao', 'Adams C.', 'Piccoli', 'Trepy', 'De Martis']
        }
    },
    {
        'id': 'squad_352',
        'name': 'Il Tridente Equilibrato — Marcus Thuram & Moise Kean',
        'formation': '3-5-2',
        'starters': {
            'P': ['Maignan'],
            'D': ['Wesley', 'Akanji', 'Tavares N.'],
            'C': ['McTominay', 'Baturina', 'Frattesi', 'Bernabè', 'Colpani'],
            'A': ['Thuram', 'Kean']
        },
        'bench': {
            'P': ['Terracciano', 'Torriani'],
            'D': ['Bellanova', 'Gila', 'Patric', 'Doig', 'De Silvestri'],
            'C': ['Ferguson', 'Frendrup', 'Deiola'],
            'A': ['Diao', 'Raimondo', 'Piccoli', 'Trepy']
        }
    },
    {
        'id': 'squad_3412',
        'name': 'Moneyball Scientifico — Algoritmo xG/xA & Titolari Reali',
        'formation': '3-4-1-2',
        'starters': {
            'P': ['Carnesecchi'],
            'D': ['Dimarco', 'Bremer', 'Tavares N.'],
            'C': ['McTominay', 'Baturina', 'Frattesi', 'Bernabè'],
            'A': ['Douvikas', 'Scamacca', 'Raimondo']
        },
        'bench': {
            'P': ['Sportiello', 'De Marzi'],
            'D': ['Kalulu', 'Bellanova', 'Patric', 'Doig', 'De Silvestri'],
            'C': ['Colpani', 'Ferguson', 'Frendrup', 'Deiola'],
            'A': ['Diao', 'Adams C.', 'Piccoli']
        }
    }
]

for sq in squads:
    tot = 0
    missing = []
    print(f"=== {sq['id']} - {sq['name']} ===")
    counts = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    spend = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    for r in ['P', 'D', 'C', 'A']:
        for n in sq['starters'][r]:
            p = get_p(n, r)
            if not p:
                missing.append((n, r))
            else:
                counts[r] += 1
                spend[r] += p['price']
                tot += p['price']
        for n in sq['bench'][r]:
            p = get_p(n, r)
            if not p:
                missing.append((n, r))
            else:
                counts[r] += 1
                spend[r] += p['price']
                tot += p['price']
    print(f"Missing: {missing}")
    print(f"Counts: {counts} (Total: {sum(counts.values())})")
    print(f"Spend: P:{spend['P']}, D:{spend['D']}, C:{spend['C']}, A:{spend['A']}")
    print(f"TOTAL: {tot} CR (Residuo: {1000 - tot} CR)\n")
