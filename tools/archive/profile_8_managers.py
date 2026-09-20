import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('data/processed/league_rosters_2025_26.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Exclude NELLOS OLD BOYS
teams_8 = {k: v for k, v in data.items() if 'NELLO' not in k.upper()}

print(f"Analyzing {len(teams_8)} active teams:")
for tname, t in teams_8.items():
    print(f"\n==================== {tname.upper()} ====================")
    print(f"Spesi: {t['total_spent']} CR | Avanzati: {t['budget_cell']} CR")
    print(f"Ripartizione: P: {t['role_spent']['P']} ({t['role_spent']['P']/t['total_spent']*100:.1f}%), "
          f"D: {t['role_spent']['D']} ({t['role_spent']['D']/t['total_spent']*100:.1f}%), "
          f"C: {t['role_spent']['C']} ({t['role_spent']['C']/t['total_spent']*100:.1f}%), "
          f"A: {t['role_spent']['A']} ({t['role_spent']['A']/t['total_spent']*100:.1f}%)")
    
    by_role = {'P': [], 'D': [], 'C': [], 'A': []}
    for p in t['players']:
        by_role[p['role']].append(p)
        
    for r in ['P', 'D', 'C', 'A']:
        p_list = sorted(by_role[r], key=lambda x: x['price'], reverse=True)
        print(f"  Reparto {r}: " + ", ".join([f"{x['name']} ({x['price']:.0f})" for x in p_list]))
