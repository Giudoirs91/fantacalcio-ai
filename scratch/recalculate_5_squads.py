import openpyxl
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

# Definizione delle 5 rose ricalcolate
# 1. 3-4-3: Lautaro + Scamacca + Piccoli | Mastantuono & Baturina | Blocco Napoli (Meret+Milinkovic+Contini)
# 2. 4-3-3: Malen + Kean + Bowie | Modificatore d'Oro (Bremer, Kalulu, Akanji, Mangas) | Blocco Roma (Svilar+Gollini+De Marzi)
# 3. 4-2-3-1: Centrocampo dei Sogni (Calhanoglu, Nico Paz, Baturina, Mastantuono, Barella) | Douvikas + Yeboah | Fiorentina Low Cost (De Gea+Christensen+Lezzerini = 21 CR)
# 4. 3-5-2: Thuram + Kean | Griglia Portieri Intelligente (Skorupski + Muric + 1 CR = 24 CR, risparmio 15 CR!) | McTominay, Baturina, Frattesi, Adzic, Douglas Luiz
# 5. 3-4-1-2: Moneyball Puro | Griglia Portieri Super-Low-Cost (Falcone + Corvi + 1 CR = 22 CR, 34/38 in casa!) | Douvikas, Scamacca, Bowie, Calò, Adzic, Mangas

squads = [
    {
        'id': 'squad_343',
        'name': "L'Armata Pesante — Lautaro Martinez & Tridente Bomber",
        'formation': '3-4-3',
        'starters': {
            'P': ['Meret'],
            'D': ['Dimarco', 'Tavares N.', 'Mangas'],
            'C': ['McTominay', 'Baturina', 'Mastantuono', 'Bernabè'],
            'A': ['Martinez L.', 'Scamacca', 'Piccoli']
        },
        'bench': {
            'P': ['Milinkovic-Savic V.', 'Contini'],
            'D': ['Kalulu', 'Bellanova', 'Patric', 'Chalobah T.', 'De Silvestri'],
            'C': ['Adzic', 'Douglas Luiz', 'Ferguson', 'Frendrup'],
            'A': ['Bowie', 'Yeboah J.', 'De Martis']
        }
    },
    {
        'id': 'squad_433',
        'name': 'La Fortezza Modificatore — Svilar & Malen Bomber',
        'formation': '4-3-3',
        'starters': {
            'P': ['Svilar'],
            'D': ['Kalulu', 'Bremer', 'Akanji', 'Mangas'],
            'C': ['Baturina', 'Mastantuono', 'Frattesi'],
            'A': ['Malen', 'Kean', 'Bowie']
        },
        'bench': {
            'P': ['Gollini', 'De Marzi'],
            'D': ['Tavares N.', 'Bellanova', 'Patric', 'De Silvestri'],
            'C': ['Bernabè', 'Adzic', 'Douglas Luiz', 'Ferguson', 'Frendrup'],
            'A': ['Yeboah J.', 'Piccoli', 'De Martis']
        }
    },
    {
        'id': 'squad_4231',
        'name': 'La Ragnatela dei Trequartisti — Calhanoglu & Nico Paz',
        'formation': '4-2-3-1',
        'starters': {
            'P': ['De Gea'],
            'D': ['Akanji', 'Tavares N.', 'Doig', 'Mangas'],
            'C': ['Calhanoglu', 'Paz N.', 'Baturina', 'Mastantuono', 'Barella'],
            'A': ['Douvikas']
        },
        'bench': {
            'P': ['Christensen O.', 'Lezzerini'],
            'D': ['Kalulu', 'Bellanova', 'Patric', 'De Silvestri'],
            'C': ['Bernabè', 'Adzic', 'Douglas Luiz'],
            'A': ['Bowie', 'Piccoli', 'Trepy', 'De Martis', 'Lisman']
        }
    },
    {
        'id': 'squad_352',
        'name': 'Il Tridente Equilibrato — Griglia Portieri & Doppia Punta',
        'formation': '3-5-2',
        'starters': {
            'P': ['Skorupski'],
            'D': ['Wesley', 'Akanji', 'Mangas'],
            'C': ['McTominay', 'Baturina', 'Mastantuono', 'Frattesi', 'Calò'],
            'A': ['Thuram', 'Kean']
        },
        'bench': {
            'P': ['Muric', 'De Marzi'],
            'D': ['Kalulu', 'Bellanova', 'Patric', 'Doig', 'De Silvestri'],
            'C': ['Adzic', 'Douglas Luiz', 'Ferguson'],
            'A': ['Bowie', 'Yeboah J.', 'Piccoli', 'Trepy']
        }
    },
    {
        'id': 'squad_3412',
        'name': 'Moneyball Scientifico — Griglia a 22 CR & Algoritmo xG',
        'formation': '3-4-1-2',
        'starters': {
            'P': ['Falcone'],
            'D': ['Dimarco', 'Bremer', 'Mangas'],
            'C': ['McTominay', 'Baturina', 'Mastantuono', 'Calò'],
            'A': ['Douvikas', 'Scamacca', 'Bowie']
        },
        'bench': {
            'P': ['Corvi', 'De Marzi'],
            'D': ['Kalulu', 'Bellanova', 'Patric', 'Doig', 'De Silvestri'],
            'C': ['Frattesi', 'Bernabè', 'Adzic', 'Douglas Luiz'],
            'A': ['Yeboah J.', 'Adams C.', 'Piccoli']
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
            if not p: missing.append((n, r))
            else:
                counts[r] += 1
                spend[r] += p['price']
                tot += p['price']
        for n in sq['bench'][r]:
            p = get_p(n, r)
            if not p: missing.append((n, r))
            else:
                counts[r] += 1
                spend[r] += p['price']
                tot += p['price']
    print(f"Missing: {missing}")
    print(f"Counts: {counts} (Total: {sum(counts.values())})")
    print(f"Spend: P:{spend['P']}, D:{spend['D']}, C:{spend['C']}, A:{spend['A']}")
    print(f"TOTAL: {tot} CR (Residuo su 1000: {1000 - tot} CR)\n")
