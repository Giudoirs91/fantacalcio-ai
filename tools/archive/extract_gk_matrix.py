import pandas as pd
import json

df = pd.read_excel('Griglia_Portieri_Fantacalcio_Stagione_2026-27.xlsx', header=None)

cols = [str(df.iloc[1, j]).strip() for j in range(1, 21)]

team_abbr_map = {
    'Ata': 'Atalanta', 'Bol': 'Bologna', 'Cag': 'Cagliari', 'Com': 'Como',
    'Fio': 'Fiorentina', 'Fro': 'Frosinone', 'Gen': 'Genoa', 'Int': 'Inter',
    'Juv': 'Juventus', 'Laz': 'Lazio', 'Lec': 'Lecce', 'Mil': 'Milan',
    'Mon': 'Monza', 'Nap': 'Napoli', 'Par': 'Parma', 'Rom': 'Roma',
    'Sas': 'Sassuolo', 'Tor': 'Torino', 'Udi': 'Udinese', 'Ven': 'Venezia'
}

matrix = {}
all_pairs = []
seen = set()

for i in range(2, 22):
    row = df.iloc[i].values
    t_abbr = str(row[0]).strip()
    t_name = team_abbr_map.get(t_abbr, t_abbr)
    matrix[t_name] = {}
    
    for j in range(1, 21):
        c_abbr = cols[j-1]
        c_name = team_abbr_map.get(c_abbr, c_abbr)
        val = row[j]
        try:
            val_int = int(val)
        except:
            val_int = None
        matrix[t_name][c_name] = val_int

        if t_name != c_name and val_int is not None:
            pair_key = tuple(sorted([t_name, c_name]))
            if pair_key not in seen:
                seen.add(pair_key)
                home_games = 38 - val_int
                pct = round((home_games / 38.0) * 100, 1)
                
                # Tag label
                if val_int == 0:
                    label = "Incrocio Perfetto 100% (38/38 in casa)"
                    tier = "perfect"
                elif val_int <= 4:
                    label = f"Alternanza Elite {pct}% (34+/38 in casa)"
                    tier = "elite"
                elif val_int <= 6:
                    label = f"Alternanza Ottimale {pct}% (32/38 in casa)"
                    tier = "optimal"
                elif val_int <= 8:
                    label = f"Alternanza Buona {pct}% (30/38 in casa)"
                    tier = "good"
                else:
                    label = f"Alternanza Sfavorevole ({pct}%)"
                    tier = "poor"

                all_pairs.append({
                    'teamA': t_name,
                    'teamB': c_name,
                    'abbrA': t_abbr,
                    'abbrB': c_abbr,
                    'diff': val_int,
                    'home_games': home_games,
                    'pct': pct,
                    'label': label,
                    'tier': tier
                })

all_pairs.sort(key=lambda x: (x['diff'], -x['home_games'], x['teamA']))

print("Total pairs extracted:", len(all_pairs))
print("\n=== TOP 30 INCASTRI UFFICIALI SERIE A 2026/27 ===")
for p in all_pairs[:30]:
    print(f"{p['teamA']:12} + {p['teamB']:12} | Diff: {p['diff']:2d} | In Casa: {p['home_games']}/38 ({p['pct']:4.1f}%) | {p['label']}")

with open('gk_matrix_2026_27.json', 'w', encoding='utf-8') as f:
    json.dump({
        'matrix': matrix,
        'pairs': all_pairs,
        'teams': list(team_abbr_map.values())
    }, f, ensure_ascii=False, indent=2)
print("Saved gk_matrix_2026_27.json successfully.")
