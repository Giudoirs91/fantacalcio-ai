import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import pandas as pd

df = pd.read_csv("data/raw/match_reports_players_g1_g2.csv")
with open("data/raw/match_reports_matches_g1_g2.json", "r", encoding="utf-8") as f:
    matches = json.load(f)

print(f"=== TOTALE MATCH REPORT ELABORATI: {len(matches)} ===")
for m in matches:
    print(f"G{m['giornata']}: {m['match_title']} | Moduli: {m.get('moduli', [])}")

print(f"\n=== TOTALE GIOCATORI A REFERTO: {len(df)} righe ===")
print("\nTop Marcatori G1+G2:")
marcatori = df[df['goals'] > 0].groupby(['team', 'player_name'])['goals'].sum().reset_index().sort_values(by='goals', ascending=False)
print(marcatori.head(15).to_string(index=False))

print("\nTop Assistman G1+G2:")
assistmen = df[df['assists'] > 0].groupby(['team', 'player_name'])['assists'].sum().reset_index().sort_values(by='assists', ascending=False)
print(assistmen.head(15).to_string(index=False))
