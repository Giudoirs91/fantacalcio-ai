import json
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Carichiamo i prezzi reali pagati nella Lega Ferrovia
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
            clean = str(name).strip()
            # keep max or first price seen in real auction
            real_prices[clean.lower()] = int(cost)

print(f"Loaded {len(real_prices)} real auction prices from Lega Ferrovia.")

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    master = json.load(f)
master_dict = {p['name'].lower().strip(): p for p in master}

def get_real_price(name):
    clean = name.lower().strip()
    if clean in real_prices:
        return real_prices[clean]
    # Fallback to master if not in ferrovia
    p = master_dict.get(clean)
    if p:
        # Se è un portiere titolare big non presente:
        if p['role'] == 'P' and p['team'] in ['Napoli', 'Inter', 'Roma', 'Milan', 'Atalanta', 'Como']:
            return 95
        return p.get('prezzo_cons', 1)
    return 1

# Costruiamo 5 formazioni basate ESATTAMENTE sui prezzi reali della Lega Ferrovia:

squads = [
    {
        'id': 'squad_343',
        'name': "L'Armata Pesante — Lautaro Top Bomber & Tridente",
        'formation': '3-4-3',
        'archetype': "Super-Top Lautaro (415 CR) + Porta Allegri (103 CR) + Titolarissimi a 1 CR",
        'tagColor': '#f43f5e',
        'badge': "🔥 LAUTARO (415 CR) + PORTA NAPOLI (103 CR)",
        'coach_context': "Napoli di Massimiliano Allegri (4-3-3)",
        'gkStrategy': "🧤 <b>Blocco Ufficiale Napoli di Allegri (103 CR)</b>: Spesa reale d'asta: <b>Meret (101 CR)</b> + <b>Milinkovic-Savic V. (1 CR)</b> + <b>Contini (1 CR)</b>. Garanzia di solidità difensiva tipica delle squadre di Allegri.",
        'starters': {
            'P': ['Meret'],
            'D': ['Bellanova', 'Tavares N.', 'Gila'],
            'C': ['McTominay', 'Baturina', 'Calò', 'Bernabè'],
            'A': ['Martinez L.', 'Scamacca', 'Piccoli']
        },
        'bench': {
            'P': ['Milinkovic-Savic V.', 'Contini'],
            'D': ['Valeri', 'Gallo', 'Kabasele', 'Ostigard', 'Marcandalli'],
            'C': ['Busio', 'Fazzini', 'Thorstvedt', 'Perrone'],
            'A': ['Bowie', 'Kevin Carlos', 'Bonny']
        }
    },
    {
        'id': 'squad_433',
        'name': "La Fortezza Modificatore — Svilar (136 CR), Malen & Difesa d'Oro",
        'formation': '4-3-3',
        'archetype': "Porta Inviolata Gasperini (138 CR) + Malen (442 CR) + Modificatore +3/+6",
        'tagColor': '#38bdf8',
        'badge': "🛡️ SVILAR (136 CR) + MALEN BOMBER (442 CR)",
        'coach_context': "Roma di Gian Piero Gasperini (3-4-2-1)",
        'gkStrategy': "🧤 <b>Blocco Ufficiale Roma di Gasperini (138 CR)</b>: Spesa reale d'asta: <b>Svilar (136 CR)</b> + <b>Gollini (1 CR)</b> + <b>De Marzi (1 CR)</b>. La porta meno battuta del torneo, indispensabile per il modificatore di difesa.",
        'starters': {
            'P': ['Svilar'],
            'D': ['Bremer', 'Kalulu', 'Bellanova', 'Valeri'],
            'C': ['Baturina', 'Frattesi', 'Calò'],
            'A': ['Malen', 'Kean', 'Bowie']
        },
        'bench': {
            'P': ['Gollini', 'De Marzi'],
            'D': ['Gallo', 'Vasquez', 'Kabasele', 'Obert'],
            'C': ['Bernabè', 'Busio', 'Fazzini', 'Thorstvedt', 'Perrone'],
            'A': ['Kevin Carlos', 'Vitinha', 'Bonny']
        }
    },
    {
        'id': 'squad_4231',
        'name': "La Ragnatela dei Trequartisti — Calhanoglu, Baturina & Mastantuono",
        'formation': '4-2-3-1',
        'archetype': "Mediana Dominante (420+ CR) / Rigoristi & Tiratori / Douvikas Top",
        'tagColor': '#a855f7',
        'badge': "🪄 MEDIANA DEI SOGNI (420 CR) + DE GEA LOW-COST",
        'coach_context': "Como di Fabregas / Fiorentina di Grosso",
        'gkStrategy': "🧤 <b>Blocco Low-Cost Fiorentina (58 CR)</b>: Spesa reale d'asta: <b>De Gea (56 CR)</b> + <b>Christensen O. (1 CR)</b> + <b>Lezzerini (1 CR)</b>. Risparmiati oltre 70 CR rispetto a Svilar o Martinez per finanziare il centrocampo!",
        'starters': {
            'P': ['De Gea'],
            'D': ['Wesley', 'Bellanova', 'Tavares N.', 'Valeri'],
            'C': ['Calhanoglu', 'Baturina', 'Mastantuono', 'Barella', 'Calò'],
            'A': ['Douvikas']
        },
        'bench': {
            'P': ['Christensen O.', 'Lezzerini'],
            'D': ['Gallo', 'Vasquez', 'Kabasele', 'Ostigard'],
            'C': ['Bernabè', 'Busio', 'Fazzini'],
            'A': ['Kean', 'Bowie', 'Kevin Carlos', 'Vitinha', 'Bonny']
        }
    },
    {
        'id': 'squad_352',
        'name': "Il Tridente Equilibrato — Thuram, Kean & Scamacca",
        'formation': '3-5-2',
        'archetype': "Doppia Punta da 30+ Gol (Thuram 255 + Kean 79) + Griglia Portieri (86 CR)",
        'tagColor': '#10b981',
        'badge': "⚖️ THURAM (255 CR) + GRIGLIA PORTIERI REALE (86 CR)",
        'coach_context': "Inter di Cristian Chivu (3-5-2)",
        'gkStrategy': "🧤 <b>Griglia Portieri Reale Torino + Cagliari (86 CR)</b>: Spesa reale da Lega Ferrovia: <b>Perri (41 CR)</b> + <b>Caprile (39 CR)</b> + <b>Corvi (6 CR)</b>. 32 gare su 38 in casa senza dover pagare 130 CR per una big!",
        'starters': {
            'P': ['Perri'],
            'D': ['Wesley', 'Gila', 'Bellanova'],
            'C': ['McTominay', 'Baturina', 'Frattesi', 'Calò', 'Bernabè'],
            'A': ['Thuram', 'Scamacca']
        },
        'bench': {
            'P': ['Caprile', 'Corvi'],
            'D': ['Valeri', 'Gallo', 'Vasquez', 'Kabasele', 'Obert'],
            'C': ['Busio', 'Fazzini', 'Thorstvedt'],
            'A': ['Kean', 'Bowie', 'Kevin Carlos', 'Bonny']
        }
    },
    {
        'id': 'squad_3412',
        'name': "Moneyball Scientifico — Algoritmo Reale & 18 Titolari Veri",
        'formation': '3-4-1-2',
        'archetype': "Massima Efficienza xG/xA / Falcone (1 CR) & Vicario (77 CR) / Douvikas + Scamacca",
        'tagColor': '#eab308',
        'badge': "📊 EFFICIENZA PURA xG & RISPARMIO PORTA",
        'coach_context': "Juventus di Luciano Spalletti / Atalanta di Maurizio Sarri",
        'gkStrategy': "🧤 <b>Porta Juventus di Spalletti (79 CR)</b>: Spesa reale d'asta: <b>Vicario (77 CR)</b> + <b>Grabara (1 CR)</b> + <b>Falcone (1 CR)</b>. Solidità da big a meno di 80 crediti totali.",
        'starters': {
            'P': ['Vicario'],
            'D': ['Bremer', 'Wesley', 'Valeri'],
            'C': ['McTominay', 'Baturina', 'Mastantuono', 'Calò'],
            'A': ['Douvikas', 'Scamacca', 'Kean']
        },
        'bench': {
            'P': ['Grabara', 'Falcone'],
            'D': ['Bellanova', 'Gallo', 'Vasquez', 'Kabasele', 'Ostigard'],
            'C': ['Frattesi', 'Bernabè', 'Busio', 'Fazzini'],
            'A': ['Bowie', 'Kevin Carlos', 'Vitinha']
        }
    }
]

print("\n=== VERIFICA BUDGET E COERENZA SQUADRE ===")
for sq in squads:
    tot = 0
    counts = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    spend = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
    print(f"\n------------------------------------------------")
    print(f"SQUADRA: {sq['name']} ({sq['formation']})")
    print(f"------------------------------------------------")
    for r in ['P', 'D', 'C', 'A']:
        st_names = sq['starters'][r]
        bn_names = sq['bench'][r]
        for nm in st_names:
            cost = get_real_price(nm)
            counts[r] += 1
            spend[r] += cost
            tot += cost
            p = master_dict.get(nm.lower().strip(), {})
            team = p.get('team', '?')
            print(f"  [TIT] {r}: {nm} ({team}) -> {cost} CR")
        for nm in bn_names:
            cost = get_real_price(nm)
            counts[r] += 1
            spend[r] += cost
            tot += cost
            p = master_dict.get(nm.lower().strip(), {})
            team = p.get('team', '?')
            print(f"  [PAN] {r}: {nm} ({team}) -> {cost} CR")
    print(f"Counts: {counts} (Totale: {sum(counts.values())} calciatori)")
    print(f"Spesa Reparti: P:{spend['P']} CR ({round(spend['P']/tot*100)}%), D:{spend['D']} CR ({round(spend['D']/tot*100)}%), C:{spend['C']} CR ({round(spend['C']/tot*100)}%), A:{spend['A']} CR ({round(spend['A']/tot*100)}%)")
    print(f"TOTALE SPESA REALE: {tot} CR (Residuo: {1000 - tot} CR)")
