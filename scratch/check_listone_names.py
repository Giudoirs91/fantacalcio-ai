import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('data/raw/Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1)
for q in ['Pellegri', 'Israel', 'Cande', 'Bah', 'Nuredini']:
    m = df[df['Nome'].str.contains(q, case=False, na=False)]
    if not m.empty:
        print(f"Found in listone for {q}:")
        print(m[['Id', 'R', 'Nome', 'Squadra']])
    else:
        print(f"NOT in listone: {q}")
