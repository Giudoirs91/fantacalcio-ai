import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

targets = [
    'Meret', 'Vicario', 'Svilar',
    'Tavares N.', 'Bellanova', 'Bremer', 'Lucumì', 'Mancini', 'Dimarco', 'Kalulu', 'Hermoso',
    'Baturina', 'Bernardeschi', 'Calò', 'Adzic', 'Zaccagni', 'Rabiot', 'Mastantuono', 'Frattesi', 'Perrone', 'Busio',
    'Thuram', 'Scamacca', 'Ramos G.', 'Martinez L.', 'Bowie', 'Krstovic', 'Bonny', 'Camarda', 'Esposito F.P.'
]

for name in targets:
    p = next((x for x in players if x['name'].lower() == name.lower()), None)
    if p:
        sub_name = p.get('coppia_nome')
        sub = next((x for x in players if x['name'].lower() == (sub_name or '').lower() and x['team'] == p['team']), None)
        sub_prz = sub.get('prezzo_cons') if sub else '?'
        print(f"{p['name']} ({p['role']}, {p['team']}, Prz:{p.get('prezzo_cons')})  <===>  {sub_name} ({p.get('coppia_ruolo')}, Prz:{sub_prz}) [{p.get('coppia_tipo')}: {p.get('coppia_dettaglio')}]")
