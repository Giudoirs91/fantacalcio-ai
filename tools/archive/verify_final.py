import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

print("=== VERIFICA PORTIERI (METRICHE DEDICATE 25/26) ===")
gks = [p for p in players if p['role'] == 'P' and p['has_data_2526']][:6]
for p in gks:
    print(f"{p['name']:<18} ({p['team']:<10}) -> Rating: {p['rating_2526']} | Salvati: {p['goals_prevented_2526']} | CleanSheets: {p['clean_sheets_2526']} | GS: {p['gs']} | Minuti: {p['mins_2526']}")

print("\n=== VERIFICA GIOCATORI DI MOVIMENTO DA ALTRI CAMPIONATI ===")
foreign = [p for p in players if p['league_2526'] != 'Serie A' and p['has_data_2526']][:6]
for p in foreign:
    print(f"{p['name']:<18} ({p['team']:<10} - {p['league_2526']:<14}) -> xG/90: {p['xg90_2526']} | xGOT: {p['xgot_2526']} | xA/90: {p['xa90_2526']} | Gol/Ass: {p['gf']}/{p['ass']} | Mins: {p['mins_2526']}")
