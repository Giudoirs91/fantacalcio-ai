import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

gems = []
for p in players:
    g = p.get('gol_2627', 0)
    # Strictly EXCLUDE players with 2+ goals (the ones that already "rubato l'occhio")
    if g >= 2:
        continue
    
    price = p.get('prezzo_cons', 1)
    qta = p.get('qta', 1)
    mins = p.get('minuti_2627', 0)
    xg = p.get('xg_2627') or 0.0
    xa = p.get('xa_2627') or 0.0
    if not isinstance(xg, (int, float)): xg = 0.0
    if not isinstance(xa, (int, float)): xa = 0.0
    
    kp = p.get('key_passes_2627', 0)
    shots = p.get('tiri_2627', 0)
    shots_ot = p.get('tiri_porta_2627', 0)
    oop = p.get('is_oop', False)
    oop_val = p.get('oop_val', '')
    piaz = p.get('piazzati_val', '')
    rig = p.get('rigorista_val', '')
    ovr = p.get('ovr', 70)
    advice = p.get('ai_advice', '')
    team = p.get('team', '')
    role = p.get('role', '')
    name = p.get('name', '')
    
    # We want players who are cheap (price <= 25 or qta <= 13), have played at least 80 mins,
    # and have high underlying stats (xG, xA, shots, key passes, OOP)
    if mins >= 80 and (price <= 30 or qta <= 14):
        impact_score = (xg * 4.0) + (xa * 3.5) + (shots * 0.25) + (shots_ot * 0.5) + (kp * 0.4)
        if oop: impact_score += 1.5
        if piaz and piaz != '-': impact_score += 1.0
        
        gems.append({
            'name': name,
            'team': team,
            'role': role,
            'price': price,
            'qta': qta,
            'mins': mins,
            'g': g,
            'a': p.get('assist_2627', 0),
            'xg': round(xg, 2),
            'xa': round(xa, 2),
            'kp': kp,
            'shots': shots,
            'shots_ot': shots_ot,
            'oop_val': oop_val,
            'piaz': piaz,
            'rig': rig,
            'score': round(impact_score, 2),
            'advice': advice
        })

gems.sort(key=lambda x: x['score'], reverse=True)

print("=== LE VERE GEMME NASCOSTE (0 o 1 GOL, SOTTO RADAR, METRICHE AVANZATE ALTE) ===")
for g in gems[:25]:
    print(f"- {g['name']} ({g['team']}, {g['role']}): Qt.A {g['qta']} | Cons: {g['price']} CR | Min: {g['mins']}' | G:{g['g']} A:{g['a']} | xG:{g['xg']} xA:{g['xa']} | Tiri:{g['shots']} (In porta:{g['shots_ot']}) | KP:{g['kp']} | Score:{g['score']} | OOP:{g['oop_val']} | Piaz:{g['piaz']}")
