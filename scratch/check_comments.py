import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('data/processed/top_flop_rounds.json', encoding='utf-8'))
for r in [4, 3, 2, 1]:
    print(f'*** GIORNATA {r} ***')
    print('TOP 3:')
    for p in data[str(r)]['top'][:3]:
        print(f"  {p['name']} ({p['role']} - {p['team']}) Voto: {p['voto']} | FV: {p['fantavoto']}")
        print(f"    Commento: {p['commento']}")
    print('FLOP 3:')
    for p in data[str(r)]['flop'][:3]:
        print(f"  {p['name']} ({p['role']} - {p['team']}) Voto: {p['voto']} | FV: {p['fantavoto']}")
        print(f"    Commento: {p['commento']}")
