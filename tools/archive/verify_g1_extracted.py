import pandas as pd

df_p = pd.read_csv('data/raw/seriea_2026_27_giornata_1_players.csv')
df_t = pd.read_csv('data/raw/seriea_2026_27_giornata_1_teams.csv')

print("=== STATISTICHE GIORNATA 1 (2026/2027) ESTRATTE ===")
print(f"Totale Calciatori: {len(df_p)}")
print(f"Totale Squadre: {len(df_t)}")

print("\n--- Marcatori Giornata 1 ---")
scorers = df_p[df_p['goals'] > 0][['player_name', 'team', 'minutes', 'goals', 'assists', 'total_shots', 'shots_on_target', 'chances_created']]
for _, r in scorers.iterrows():
    pname = str(r['player_name']).encode('ascii', 'ignore').decode('ascii')
    print(f"  {pname:<18} ({r['team']:<10}) -> Min: {r['minutes']}' | Gol: {r['goals']} | Assist: {r['assists']} | Tiri (In Porta): {r['total_shots']}({r['shots_on_target']}) | Occasioni: {r['chances_created']}")

print("\n--- Statistiche Tattiche Squadre Giornata 1 ---")
for _, r in df_t.iterrows():
    print(f"  {r['team']:<12} -> Gol: {r['goals_scored']} | Tiri (In Area): {r['total_shots']}({r['shots_in_box']}) | Pericolosità: {r['danger_index_pct']}% | Baricentro: {r['baricentro_m']}m | Falli: {r['fouls_committed']}")
