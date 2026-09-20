import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/gk_matrix_2026_27.json', encoding='utf-8') as f:
    gk_data = json.load(f)

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

team_gks = {}
for p in players:
    if p['role'] == 'P':
        t = p['team']
        if t not in team_gks:
            team_gks[t] = []
        team_gks[t].append(p)

for t in team_gks:
    team_gks[t].sort(key=lambda x: x.get('prezzo_cons', 1), reverse=True)

pairs = gk_data.get('pairs', [])
pairs.sort(key=lambda x: (x['diff'], x.get('teamA', '')))

print("=== MIGLIORI ACCOPPIAMENTI GRIGLIA PORTIERI (DISGIUNZIONI <= 5) ===")
low_cost_pairs = []
for p in pairs:
    t1 = p['teamA']
    t2 = p['teamB']
    diff = p['diff']
    
    gk1 = team_gks.get(t1, [{}])[0]
    gk2 = team_gks.get(t2, [{}])[0]
    
    cost1 = gk1.get('prezzo_cons', 10)
    cost2 = gk2.get('prezzo_cons', 10)
    
    tot_cost = cost1 + cost2 + 1
    if diff <= 6:
        low_cost_pairs.append({
            't1': t1, 'gk1': gk1.get('name'), 'c1': cost1,
            't2': t2, 'gk2': gk2.get('name'), 'c2': cost2,
            'diff': diff, 'home': p['home_games'], 'tot': tot_cost
        })

low_cost_pairs.sort(key=lambda x: (x['diff'], x['tot']))
for lp in low_cost_pairs[:30]:
    print(f"- {lp['t1']} ({lp['gk1']} {lp['c1']} CR) + {lp['t2']} ({lp['gk2']} {lp['c2']} CR) -> Diff: {lp['diff']} ({lp['home']}/38 in casa) | Totale Spesa: {lp['tot']} CR")
