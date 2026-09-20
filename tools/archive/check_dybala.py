import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

targets = ['dybala', 'yildiz', 'kone i.', 'pessina', 'buongiorno', 'bah', 'berardi', 'zaniolo', 'pellegrini lo.']
for p in players:
    if any(t in p['name'].lower() for t in targets):
        print(f"{p['name']:18} | {p['integrita']:32} | {p['infortunio_status'][:40]:40} | OVR: {p['ovr']} | Prezzo: {p['prezzo_cons']:3d} CR | {p['ai_advice']}")

