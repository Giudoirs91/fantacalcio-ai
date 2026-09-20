import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

xl = pd.ExcelFile('data/raw/voti 26-27/Voti_Fantacalcio_Stagione_2026_27_Giornata_4.xlsx')
sheet = 'Fantacalcio' if 'Fantacalcio' in xl.sheet_names else xl.sheet_names[0]
df_raw = pd.read_excel(xl, sheet_name=sheet, skiprows=5)

df = df_raw[pd.to_numeric(df_raw['Cod.'], errors='coerce').notna()].copy()
df['Voto_clean'] = pd.to_numeric(df['Voto'].astype(str).str.replace('*', '').str.replace(',', '.'), errors='coerce')

for col in ['Gf', 'Gs', 'Au', 'Amm', 'Esp', 'Ass']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

gf = df['Gf']
gs = df['Gs']
ass = df['Ass']
amm = df['Amm']
esp = df['Esp']
aut = df['Au']
df['FV_calc'] = df['Voto_clean'] + (gf * 3) - (gs * 1) + (ass * 1) - (amm * 0.5) - (esp * 1) - (aut * 2)

voted = df[df['Voto_clean'].notna()].copy()

print("=== TOP 15 UP (I MIGLIORI DELLA GIORNATA 4) ===")
top = voted.sort_values(by=['FV_calc', 'Voto_clean'], ascending=[False, False]).head(15)
for _, r in top.iterrows():
    print(f"+ {r['Nome']} ({r['Ruolo']}) | Voto: {r['Voto_clean']} | Fantavoto: {r['FV_calc']} (Gol: {int(r['Gf'])}, Assist: {int(r['Ass'])})")

print("\n=== TOP 15 DOWN (I PEGGIORI / FLOP DELLA GIORNATA 4) ===")
bot = voted.sort_values(by=['FV_calc', 'Voto_clean'], ascending=[True, True]).head(15)
for _, r in bot.iterrows():
    print(f"- {r['Nome']} ({r['Ruolo']}) | Voto: {r['Voto_clean']} | Fantavoto: {r['FV_calc']} (Gol Subiti: {int(r['Gs'])}, Amm: {int(r['Amm'])}, Esp: {int(r['Esp'])}, Aut: {int(r['Au'])})")

