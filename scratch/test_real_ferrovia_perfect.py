import json
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('config/tactical_db.json', encoding='utf-8') as f:
    tactical_db = json.load(f)

coaches = {t: d.get('all') for t, d in tactical_db.items()}

wb = openpyxl.load_workbook('data/raw/lega-ferrovia-rosters-1788691861822.xlsx', data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

header = rows[0]
teams = [(header[i], i) for i in range(0, len(header), 3) if header[i]]

real_prices = {}
for r in rows[1:]:
    for t_name, col_idx in teams:
        name = r[col_idx]
        cost = r[col_idx + 1]
        if name and cost is not None:
            clean = str(name).strip().lower()
            if clean not in real_prices:
                real_prices[clean] = int(cost)

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    master = json.load(f)
master_dict = {p['name'].lower().strip(): p for p in master}

def get_price(name, role):
    clean = name.lower().strip()
    if clean in real_prices:
        return real_prices[clean]
    p = master_dict.get(clean)
    if p:
        return p.get('prezzo_cons', 1)
    return 1

squads = [
    {
        'id': 'squad_343',
        'name': "L'Armata Pesante — Lautaro Top Bomber & Napoli di Allegri",
        'formation': '3-4-3',
        'coach_context': "Napoli di Massimiliano Allegri (4-3-3)",
        'gkStrategy': "🧤 <b>Blocco Ufficiale Napoli di Allegri (103 CR)</b>: Spesa reale d'asta: <b>Meret (101 CR)</b> + <b>Milinkovic-Savic V. (1 CR)</b> + <b>Contini (1 CR)</b>. Garanzia della proverbiale solidità difensiva delle squadre di Allegri.",
        'starters': {
            'P': ['Meret'],
            'D': ['Kalulu', 'Mancini', 'Bellanova'],
            'C': ['Vergara', 'Da Cunha', 'McKennie', 'Calò'],
            'A': ['Martinez L.', 'Scamacca', 'Raimondo']
        },
        'bench': {
            'P': ['Milinkovic-Savic V.', 'Contini'],
            'D': ['Valeri', 'Gallo', 'Kabasele', 'Marcandalli', 'Ostigard'],
            'C': ['Bernabè', 'Busio', 'Fazzini', 'Thorstvedt'],
            'A': ['Bowie', 'Kevin Carlos', 'Vitinha O.']
        }
    },
    {
        'id': 'squad_433',
        'name': "La Fortezza Modificatore — Svilar, Roma di Gasperini & Malen",
        'formation': '4-3-3',
        'coach_context': "Roma di Gian Piero Gasperini (3-4-2-1)",
        'gkStrategy': "🧤 <b>Blocco Ufficiale Roma di Gasperini (138 CR)</b>: Spesa reale d'asta: <b>Svilar (136 CR)</b> + <b>Gollini (1 CR)</b> + <b>De Marzi (1 CR)</b>. La porta meno battuta del campionato, pilastro insostituibile per incamerare +3/+6 di modificatore.",
        'starters': {
            'P': ['Svilar'],
            'D': ['Bremer', 'Kalulu', 'Bellanova', 'Hermoso'],
            'C': ['Mastantuono', 'Frattesi', 'Koné M.'],
            'A': ['Malen', 'Kean', 'Bowie']
        },
        'bench': {
            'P': ['Gollini', 'De Marzi'],
            'D': ['Valeri', 'Gallo', 'Vasquez', 'Obert'],
            'C': ['Calò', 'Bernabè', 'Busio', 'Fazzini', 'Perrone'],
            'A': ['Kevin Carlos', 'Bonny', 'Vitinha O.']
        }
    },
    {
        'id': 'squad_4231',
        'name': "La Ragnatela dei Trequartisti — Calhanoglu, Nico Paz & Mastantuono",
        'formation': '4-2-3-1',
        'coach_context': "Como di Fabregas / Fiorentina di Grosso",
        'gkStrategy': "🧤 <b>Blocco Low-Cost Fiorentina di Grosso (58 CR)</b>: Spesa reale d'asta: <b>De Gea (56 CR)</b> + <b>Christensen O. (1 CR)</b> + <b>Lezzerini (1 CR)</b>. Risparmiati oltre 80 CR rispetto a Svilar per allestire una mediana mostruosa da 480 CR!",
        'starters': {
            'P': ['De Gea'],
            'D': ['Akanji', 'Tavares N.', 'Bellanova', 'Valeri'],
            'C': ['Paz N.', 'Calhanoglu', 'Mastantuono', 'Barella', 'Calò'],
            'A': ['Douvikas']
        },
        'bench': {
            'P': ['Christensen O.', 'Lezzerini'],
            'D': ['Gallo', 'Vasquez', 'Kabasele', 'Ostigard'],
            'C': ['Bernabè', 'Busio', 'Fazzini'],
            'A': ['Kean', 'Bowie', 'Kevin Carlos', 'Bonny', 'Vitinha O.']
        }
    },
    {
        'id': 'squad_352',
        'name': "Il Tridente Equilibrato — Griglia Portieri Reale, Thuram & Kean",
        'formation': '3-5-2',
        'coach_context': "Inter di Cristian Chivu / Torino di Abate / Cagliari di Pisacane",
        'gkStrategy': "🧤 <b>Griglia Portieri Reale Torino + Cagliari (86 CR)</b>: Spesa reale da Lega Ferrovia: <b>Perri (41 CR)</b> + <b>Caprile (39 CR)</b> + <b>Corvi (6 CR)</b>. 32 gare su 38 in casa senza strapagare 130 CR una big!",
        'starters': {
            'P': ['Perri'],
            'D': ['Wesley', 'Rrahmani', 'Bellanova'],
            'C': ['McTominay', 'Baturina', 'Zaniolo', 'Calò', 'Bernabè'],
            'A': ['Thuram', 'Kean']
        },
        'bench': {
            'P': ['Caprile', 'Corvi'],
            'D': ['Valeri', 'Gallo', 'Vasquez', 'Mina', 'Obert'],
            'C': ['Busio', 'Fazzini', 'Thorstvedt'],
            'A': ['Soulé', 'Bowie', 'Kevin Carlos', 'Bonny']
        }
    },
    {
        'id': 'squad_3412',
        'name': "Moneyball Scientifico — Vicario (Juve di Spalletti) & Kolo Muani",
        'formation': '3-4-1-2',
        'coach_context': "Juventus di Luciano Spalletti / Atalanta di Maurizio Sarri",
        'gkStrategy': "🧤 <b>Porta Juventus di Spalletti (79 CR)</b>: Spesa reale d'asta: <b>Vicario (77 CR)</b> + <b>Grabara (1 CR)</b> + <b>Falcone (1 CR)</b>. Porta solida da big a meno di 80 crediti totali.",
        'starters': {
            'P': ['Vicario'],
            'D': ['Bremer', 'Molina N.', 'Valeri'],
            'C': ['Baturina', 'Frattesi', 'Mastantuono', 'Calò'],
            'A': ['Kolo Muani', 'Scamacca', 'Bowie']
        },
        'bench': {
            'P': ['Grabara', 'Falcone'],
            'D': ['Bellanova', 'Gallo', 'Kabasele', 'Ostigard', 'Marcandalli'],
            'C': ['Bernabè', 'Adzic', 'Busio', 'Douglas Luiz'],
            'A': ['Kevin Carlos', 'Bonny', 'Vitinha O.']
        }
    }
]

for sq in squads:
    tot = 0
    counts = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    spend = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    for r in ['P', 'D', 'C', 'A']:
        for n in sq['starters'][r]:
            cost = get_price(n, r)
            counts[r] += 1
            spend[r] += cost
            tot += cost
        for n in sq['bench'][r]:
            cost = get_price(n, r)
            counts[r] += 1
            spend[r] += cost
            tot += cost
    print(f"\n{sq['id']}: {sq['name']} ({sq['formation']})")
    print(f"Counts: {counts} (Total {sum(counts.values())})")
    print(f"Spesa: P={spend['P']}, D={spend['D']}, C={spend['C']}, A={spend['A']}")
    print(f"TOTAL: {tot} CR (Residuo: {1000 - tot} CR)")
