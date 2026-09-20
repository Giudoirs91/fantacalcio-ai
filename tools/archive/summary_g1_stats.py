import pandas as pd

df_p = pd.read_csv('data/raw/seriea_2026_27_giornata_1_players.csv')
df_t = pd.read_csv('data/raw/seriea_2026_27_giornata_1_teams.csv')

print("=== VERIFICA DATI ESTRATTI GIORNATA 1 (2026/2027) ===")
print(f"• Calciatori estratti: {len(df_p)}")
print(f"• Squadre estratte: {len(df_t)}")

print("\n--- TOP 8 TIRATORI GIORNATA 1 ---")
top_shooters = df_p.sort_values(by=['total_shots', 'shots_on_target'], ascending=False).head(8)
for _, r in top_shooters.iterrows():
    pname = str(r['player_name']).encode('ascii', 'ignore').decode('ascii')
    print(f"  {pname:<18} ({r['team']:<10}) -> Tiri: {r['total_shots']} (In porta: {r['shots_on_target']}) | Gol: {r['goals']} | Mins: {r['minutes']}'")

print("\n--- TOP 8 CREATORI DI OCCASIONI & PASSAGGI CHIAVE ---")
top_creators = df_p.sort_values(by=['chances_created', 'key_passes'], ascending=False).head(8)
for _, r in top_creators.iterrows():
    pname = str(r['player_name']).encode('ascii', 'ignore').decode('ascii')
    print(f"  {pname:<18} ({r['team']:<10}) -> Occasioni: {r['chances_created']} | Passaggi Chiave: {r['key_passes']} | Assist: {r['assists']}")

print("\n--- TOP 5 SQUADRE PER BARICENTRO PIÙ ALTO (PRESSING & SPINTA) ---")
top_bar = df_t.sort_values(by='baricentro_m', ascending=False).head(5)
for _, r in top_bar.iterrows():
    print(f"  {r['team']:<12} -> Baricentro: {r['baricentro_m']}m | Tiri in Area: {r['shots_in_box']} | Gol: {r['goals_scored']}")
