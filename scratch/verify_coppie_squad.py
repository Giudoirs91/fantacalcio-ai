import json
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

def get_cost(name):
    clean = name.lower().strip()
    if clean in real_prices:
        return real_prices[clean]
    p = master_dict.get(clean)
    if p:
        return p.get('prezzo_cons', 1)
    return 1

# Squadra Blindata a Coppie Ufficiali:
# 1. Porta: Napoli di Allegri (Meret 101 + Milinkovic 1 + Contini 1) = 103 CR
# 2. Difesa: 4 Coppie di Squadra (Titolare + Riserva diretta):
#    - Coppia 1 (Atalanta di Sarri): Zappacosta (13 CR) + Bellanova (15 CR) = 28 CR
#    - Coppia 2 (Lazio di Gattuso): Tavares N. (33 CR) + Pedraza (1 CR) = 34 CR
#    - Coppia 3 (Juventus di Spalletti): Lucumì (26 CR) + Kelly L. (1 CR) = 27 CR
#    - Coppia 4 (Sassuolo di Aquilani): Obrador (5 CR) + Doig (1 CR) = 6 CR
#    Totale D: 95 CR
# 3. Centrocampo: 4 Coppie di Squadra (Titolare + Riserva diretta):
#    - Coppia 1 (Como di Fabregas): Baturina (136 CR) + Da Cunha (45 CR) = 181 CR
#    - Coppia 2 (Bologna di Tedesco): Bernardeschi (46 CR) + Odgaard (1 CR) = 47 CR
#    - Coppia 3 (Frosinone di Alvini): Calò (10 CR) + Grillitsch (1 CR) = 11 CR
#    - Coppia 4 (Sassuolo di Aquilani): Adzic (1 CR) + Thorstvedt (1 CR) = 2 CR
#    Totale C: 241 CR
# 4. Attacco: 3 Coppie di Squadra (Titolare + Riserva diretta):
#    - Coppia 1 (Inter di Chivu): Thuram (255 CR) + Bonny (1 CR) = 256 CR
#    - Coppia 2 (Atalanta di Sarri): Scamacca (137 CR) + Krstovic (61 CR) = 198 CR
#    - Coppia 3 (Sassuolo di Aquilani): Bowie (3 CR) + Esposito Se. (36 CR) = 39 CR
#    Totale A: 493 CR

coppie_squad = {
    'id': 'squad_coppie',
    'name': "La Corazzata a Coppie — Zero S.V. & Staffette Blindate",
    'formation': '3-4-3',
    'starters': {
        'P': ['Meret'],
        'D': ['Tavares N.', 'Bellanova', 'Lucumì'],
        'C': ['Baturina', 'Bernardeschi', 'Calò', 'Adzic'],
        'A': ['Thuram', 'Scamacca', 'Bowie']
    },
    'bench': {
        'P': ['Milinkovic-Savic V.', 'Contini'],
        'D': ['Pedraza', 'Zappacosta', 'Kelly L.', 'Obrador', 'Doig'],
        'C': ['Da Cunha', 'Odgaard', 'Grillitsch', 'Thorstvedt'],
        'A': ['Bonny', 'Krstovic', 'Esposito Se.']
    }
}

tot = 0
counts = {'P': 0, 'D': 0, 'C': 0, 'A': 0}
spend = {'P': 0, 'D': 0, 'C': 0, 'A': 0}

for r in ['P', 'D', 'C', 'A']:
    for n in coppie_squad['starters'][r]:
        c = get_cost(n)
        counts[r] += 1
        spend[r] += c
        tot += c
    for n in coppie_squad['bench'][r]:
        c = get_cost(n)
        counts[r] += 1
        spend[r] += c
        tot += c

print(f"\n=======================================================")
print(f"TOTALE ROSA A COPPIE: {tot} CR (Residuo: {1000 - tot} CR)")
print(f"Conteggio Slot: {counts} (Totale {sum(counts.values())} calciatori)")
print(f"Spesa Reparti: P={spend['P']} CR ({round(spend['P']/tot*100)}%), D={spend['D']} CR ({round(spend['D']/tot*100)}%), C={spend['C']} CR ({round(spend['C']/tot*100)}%), A={spend['A']} CR ({round(spend['A']/tot*100)}%)")
print(f"=======================================================")
