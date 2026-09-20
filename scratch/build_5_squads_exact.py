import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

p_by_name = {p['name'].lower(): p for p in players}

def get_p(name, team=None):
    name_l = name.lower()
    for p in players:
        if name_l == p['name'].lower() or name_l in p['name'].lower():
            if team and team.lower() not in p['team'].lower():
                continue
            return p
    return None

def calc_squad(starters_dict, bench_dict):
    total = 0
    res = {'starters': {}, 'bench': {}, 'costs': {}}
    for r, names in starters_dict.items():
        res['starters'][r] = []
        for n in names:
            p = get_p(n)
            if not p:
                print(f"ERROR: player {n} not found!")
            else:
                cost = p.get('prezzo_cons', 1)
                total += cost
                res['starters'][r].append({'name': p['name'], 'role': p['role'], 'team': p['team'], 'cost': cost, 'ovr': p['ovr'], 'id': p['id']})
    for r, names in bench_dict.items():
        res['bench'][r] = []
        for n in names:
            p = get_p(n)
            if not p:
                print(f"ERROR: bench player {n} not found!")
            else:
                cost = p.get('prezzo_cons', 1)
                total += cost
                res['bench'][r].append({'name': p['name'], 'role': p['role'], 'team': p['team'], 'cost': cost, 'ovr': p['ovr'], 'id': p['id']})
    res['total_cost'] = total
    return res

# SQUAD 1: 3-4-3 (Tridente Pesante: 1 Top A + 1 Secondo Slot + 1 Terzo Slot + Quinti e Trequartisti)
# Budget target: ~995 CR
# P: De Gea (51) + 2 riserve a 1 = 53 CR
# D: Dimarco (158) + Spence (28) + Tavares (17) + 5 riserve da 1-4 CR (15 CR) = 218 CR
# C: McTominay (179) + Frattesi (73) + Gudmundsson (31) + Bernabè (23) + 4 riserve a 1-2 CR (8 CR) = 314 CR
# A: Martinez L. (379) + Pellegrino M. (51) + Dybala (133 - or Scamacca 179 if Kean) -> let's balance!

print("Testing Squad Building...")
s1_starters = {
    'P': ['De Gea'],
    'D': ['Dimarco', 'Spence', 'Tavares N.'],
    'C': ['Frattesi', 'McTominay', 'Gudmundsson A.', 'Bernabè'],
    'A': ['Martinez L.', 'Dybala', 'Pellegrino M.']
}
s1_bench = {
    'P': ['Terracciano', 'Martinelli'],
    'D': ['Doig', 'Bellanova', 'Zappa', 'Dorgu', 'Gila'],
    'C': ['Colpani', 'Ferguson', 'Frendrup', 'Nicolussi Caviglia'],
    'A': ['Bonny', 'Esposito F.P.', 'Neres']
}
res1 = calc_squad(s1_starters, s1_bench)
print("Squad 1 (3-4-3) Total Cost:", res1['total_cost'])
for r, plist in res1['starters'].items():
    print(f"  Starters {r}:", sum(p['cost'] for p in plist), "CR ->", [p['name'] + f" ({p['cost']})" for p in plist])
for r, plist in res1['bench'].items():
    print(f"  Bench {r}:", sum(p['cost'] for p in plist), "CR ->", [p['name'] + f" ({p['cost']})" for p in plist])
