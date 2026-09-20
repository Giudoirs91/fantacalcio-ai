import json

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

has_q = [p for p in players if p.get('diff_q') is not None]
rising = sorted(has_q, key=lambda x: -x.get('diff_q', 0))[:20]
falling = sorted(has_q, key=lambda x: x.get('diff_q', 0))[:20]

print("=== I GIOCATORI CHE SONO SALITI DI QUOTAZIONE / SLOT (TOP RISERS) ===")
for p in rising:
    name = p['name']
    role = p.get('role', '-')
    team = p.get('team', '-')
    dq = p.get('diff_q', 0)
    mv = p.get('mv_2627', 0)
    fm = p.get('fm_2627', 0)
    g = p.get('gol_2627', 0)
    a = p.get('assist_2627', 0)
    slot = p.get('slot_fascia', '-')
    advice = p.get('ai_advice_type', '-')
    print(f"{name:<18} | {role:<2} | {team:<12} | DiffQ: {dq:+4.1f} | MV: {mv:.2f} | FM: {fm:.2f} | G:{g} A:{a} | {slot} | {advice}")

print("\n=== I GIOCATORI CHE SONO SCESI DI QUOTAZIONE / ALLARME SLOT (TOP FALLERS) ===")
for p in falling:
    name = p['name']
    role = p.get('role', '-')
    team = p.get('team', '-')
    dq = p.get('diff_q', 0)
    mv = p.get('mv_2627', 0)
    fm = p.get('fm_2627', 0)
    g = p.get('gol_2627', 0)
    slot = p.get('slot_fascia', '-')
    advice = p.get('ai_advice_type', '-')
    print(f"{name:<18} | {role:<2} | {team:<12} | DiffQ: {dq:+4.1f} | MV: {mv:.2f} | FM: {fm:.2f} | G:{g} | {slot} | {advice}")
