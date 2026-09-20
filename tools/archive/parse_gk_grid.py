import pandas as pd

df = pd.read_excel('Griglia_Portieri_Fantacalcio_Stagione_2026-27.xlsx', header=None)

for idx in range(min(24, len(df))):
    row_vals = [str(x) for x in df.iloc[idx].values[:10]]
    print(f"Row {idx:2d}: {row_vals}")

print("Teams found:", len(teams), teams)

# Let's find all pairs (ordered by fewest missed home games / best incastro)
all_pairs = []
team_abbr_map = {
    'Ata': 'Atalanta', 'Bol': 'Bologna', 'Cag': 'Cagliari', 'Com': 'Como',
    'Fio': 'Fiorentina', 'Fro': 'Frosinone', 'Gen': 'Genoa', 'Int': 'Inter',
    'Juv': 'Juventus', 'Laz': 'Lazio', 'Lec': 'Lecce', 'Mil': 'Milan',
    'Mon': 'Monza', 'Nap': 'Napoli', 'Par': 'Parma', 'Rom': 'Roma',
    'Sas': 'Sassuolo', 'Tor': 'Torino', 'Udi': 'Udinese', 'Ven': 'Venezia'
}

seen = set()
for t1 in teams:
    for t2 in teams:
        if t1 != t2:
            pair_key = tuple(sorted([t1, t2]))
            if pair_key not in seen:
                seen.add(pair_key)
                diff = matrix[t1].get(t2)
                if diff is not None:
                    name1 = team_abbr_map.get(t1, t1)
                    name2 = team_abbr_map.get(t2, t2)
                    home_games = 38 - diff
                    pct = round((home_games / 38.0) * 100, 1)
                    all_pairs.append({
                        'abbrA': t1, 'abbrB': t2,
                        'teamA': name1, 'teamB': name2,
                        'diff': diff,
                        'home_games': home_games,
                        'pct': pct
                    })

all_pairs.sort(key=lambda x: (x['diff'], -x['home_games']))

print("\n=== TOP 25 INCASTRI PORTIERI SERIE A 2026/27 (UFFICIALI FANTACALCIO.IT) ===")
for p in all_pairs[:25]:
    print(f"{p['teamA']:12} + {p['teamB']:12} | Malus (Partite insieme fuori casa): {p['diff']:2d} | Gare in casa garantite: {p['home_games']}/38 ({p['pct']}%)")

with open('gk_pairs_official_2026_27.json', 'w', encoding='utf-8') as f:
    json.dump(all_pairs, f, indent=2)
