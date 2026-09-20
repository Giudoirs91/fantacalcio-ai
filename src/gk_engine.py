import os
import json
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEAM_ABBR_MAP = {
    'Ata': 'Atalanta', 'Bol': 'Bologna', 'Cag': 'Cagliari', 'Com': 'Como',
    'Fio': 'Fiorentina', 'Fro': 'Frosinone', 'Gen': 'Genoa', 'Int': 'Inter',
    'Juv': 'Juventus', 'Laz': 'Lazio', 'Lec': 'Lecce', 'Mil': 'Milan',
    'Mon': 'Monza', 'Nap': 'Napoli', 'Par': 'Parma', 'Rom': 'Roma',
    'Sas': 'Sassuolo', 'Tor': 'Torino', 'Udi': 'Udinese', 'Ven': 'Venezia'
}

def extract_gk_grid(filepath=None):
    if not filepath:
        filepath = os.path.join(ROOT_DIR, "Griglia_Portieri_Fantacalcio_Stagione_2026-27.xlsx")

    if not os.path.exists(filepath):
        candidates = [
            os.path.join(ROOT_DIR, "data", "raw", os.path.basename(filepath)),
            os.path.join("data", "raw", os.path.basename(filepath)),
            "Griglia_Portieri_Fantacalcio_Stagione_2026-27.xlsx"
        ]
        for c in candidates:
            if os.path.exists(c):
                filepath = c
                break

    if not os.path.exists(filepath):
        print(f"[GkEngine] Warning: Griglia portieri non trovata: {filepath}")
        return {'matrix': {}, 'pairs': [], 'teams': list(TEAM_ABBR_MAP.values())}

    df = pd.read_excel(filepath, header=None)
    cols = [str(df.iloc[1, j]).strip() for j in range(1, 21)]

    matrix = {}
    all_pairs = []
    seen = set()

    for i in range(2, 22):
        row = df.iloc[i].values
        t_abbr = str(row[0]).strip()
        t_name = TEAM_ABBR_MAP.get(t_abbr, t_abbr)
        matrix[t_name] = {}
        
        for j in range(1, 21):
            c_abbr = cols[j-1]
            c_name = TEAM_ABBR_MAP.get(c_abbr, c_abbr)
            val = row[j]
            try:
                val_int = int(val)
            except Exception:
                val_int = None
            matrix[t_name][c_name] = val_int

            if t_name != c_name and val_int is not None:
                pair_key = tuple(sorted([t_name, c_name]))
                if pair_key not in seen:
                    seen.add(pair_key)
                    home_games = 38 - val_int
                    pct = round((home_games / 38.0) * 100, 1)
                    
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

    return {
        'matrix': matrix,
        'pairs': all_pairs,
        'teams': list(TEAM_ABBR_MAP.values())
    }
