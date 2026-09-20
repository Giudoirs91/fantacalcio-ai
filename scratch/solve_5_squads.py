import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Group players by role
by_role = {'P': [], 'D': [], 'C': [], 'A': []}
for p in players:
    by_role[p['role']].append(p)

for r in by_role:
    by_role[r].sort(key=lambda x: -x['prezzo_cons'])

# 1-credit & low cost bench players
p_bench_low = [p for p in by_role['P'] if p['prezzo_cons'] <= 2 and p['titolarita'] >= 20][:10]
d_bench_low = [p for p in by_role['D'] if p['prezzo_cons'] <= 2 and p['titolarita'] >= 40][:15]
c_bench_low = [p for p in by_role['C'] if p['prezzo_cons'] <= 2 and p['titolarita'] >= 40][:15]
a_bench_low = [p for p in by_role['A'] if p['prezzo_cons'] <= 2][:15]

print("Low cost pools ready.")

def create_squad_payload(id_key, name, formation, archetype, tagColor, badge, strategy, whyRivals, starters_names, bench_names):
    starters_p = []
    bench_p = []
    total_cost = 0
    
    starters_by_r = {'P': [], 'D': [], 'C': [], 'A': []}
    bench_by_r = {'P': [], 'D': [], 'C': [], 'A': []}
    
    for full_n in starters_names:
        found = None
        for p in players:
            if p['name'] == full_n or p['name'].lower() == full_n.lower():
                found = p
                break
        if not found:
            # substring
            for p in players:
                if full_n.lower() in p['name'].lower():
                    found = p
                    break
        if not found:
            raise Exception(f"Starter not found: {full_n}")
        starters_p.append(found)
        starters_by_r[found['role']].append(found['name'])
        total_cost += found['prezzo_cons']
        
    for full_n in bench_names:
        found = None
        for p in players:
            if p['name'] == full_n or p['name'].lower() == full_n.lower():
                found = p
                break
        if not found:
            for p in players:
                if full_n.lower() in p['name'].lower():
                    found = p
                    break
        if not found:
            raise Exception(f"Bench not found: {full_n}")
        bench_p.append(found)
        bench_by_r[found['role']].append(found['name'])
        total_cost += found['prezzo_cons']
        
    return {
        'id': id_key,
        'name': name,
        'formation': formation,
        'archetype': archetype,
        'tagColor': tagColor,
        'badge': badge,
        'budgetSpent': total_cost,
        'budgetRemaining': 1000 - total_cost,
        'projectedBonusPerMatch': '+17.8 Bonus / G',
        'starters': starters_by_r,
        'bench': bench_by_r,
        'strategyDescription': strategy,
        'whyBeatsRivals': whyRivals
    }

# =========================================================================
# SQUAD 1: 3-4-3 (Tridente Top + Mediana da Bonus)
# Target Cost: ~995 CR
# Starters:
# P (1): De Gea (51)
# D (3): Spence (28), Akanji (29), Tavares N. (17) -> Tot D = 74 CR
# C (4): McTominay (179), Frattesi (73), Gudmundsson A. (31), Bernabè (23) -> Tot C = 306 CR
# A (3): Martinez L. (379), Scamacca (179), Pellegrino M. (51) -> Tot A = 609 CR (wait: 51+74+306+609 = 1040, let's adjust!)
# If A: Martinez L. (379), Pellegrino M. (51), Kean (230) -> Tot A = 660 CR -> with cheaper C:
# Let's calibrate exact combinations!
# =========================================================================

# Helper to find exact combinations:
def find_composition():
    # SQUAD 1: 3-4-3 (Lautaro Top Bomber 379 CR + Scamacca 179 CR + Colombo 41 CR / Pellegrino 51 CR)
    # P: Meret (43) + Caprile (1) + Contini (1) = 45 CR
    # D: Spence (28), Akanji (29), Tavares (17) [Tot 74] + 5 riserve (Doig 7, Bellanova 8, Zappa 2, Gila 17, Patric 1) [35 CR] = 109 CR
    # C: McTominay (179), Gudmundsson (31), Bernabè (23), Colpani (19) [Tot 252] + 4 riserve a 1-2 CR (Ferguson 10, Frendrup 6, Payero 2, Gaetano 1) [19 CR] = 271 CR
    # A: Martinez L. (379), Scamacca (179), Pellegrino M. (51) [Tot 609] + 3 riserve a 1 CR (Bonny 9, Neres 12, Doumbia/Piccoli 1) [22 CR] -> Let's compute:
    # 45 + 109 + 271 + (379 + 179 + 51 + 9 + 12 + 1) = 45 + 109 + 271 + 631 = 1056 -> slight over by 56 CR.
    # Replace Scamacca (179) with Kean (230)? No, Kean is higher.
    # What about: Martinez L. (379) + Pinamonti / Pellegrino / Piccoli / Dia?
    pass

