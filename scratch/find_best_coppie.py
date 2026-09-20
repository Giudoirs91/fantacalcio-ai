import json
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
players_path = os.path.join(root_dir, 'data', 'processed', 'processed_players_master.json')

with open(players_path, 'r', encoding='utf-8') as f:
    players = json.load(f)

coppie_by_role = {'P': [], 'D': [], 'C': [], 'A': []}
seen_pairs = set()

for p in players:
    if p.get('is_in_11') and p.get('coppia_nome') != '-' and p.get('coppia_ruolo') == p.get('role'):
        sub = next((x for x in players if x['name'] == p['coppia_nome'] and x['team'] == p['team']), None)
        if sub:
            pair_key = tuple(sorted([p['id'], sub['id']]))
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                coppie_by_role[p['role']].append((p, sub))

for r in ['P', 'D', 'C', 'A']:
    print(f"\n=== RUOLO {r} (Top coppie per FVM/OVR titolare) ===")
    sorted_pairs = sorted(coppie_by_role[r], key=lambda x: (x[0].get('ovr', 0) + x[0].get('fvm', 0)), reverse=True)
    for tit, sub in sorted_pairs[:12]:
        print(f"{tit['name']} ({tit['team']}, OVR:{tit.get('ovr')}, FVM:{tit.get('fvm')}, Prz:{tit.get('prezzo_cons')}) <---> {sub['name']} (OVR:{sub.get('ovr')}, FVM:{sub.get('fvm')}, Prz:{sub.get('prezzo_cons')}) | Tipo: {tit.get('coppia_tipo')} | Det: {tit.get('coppia_dettaglio')}")
