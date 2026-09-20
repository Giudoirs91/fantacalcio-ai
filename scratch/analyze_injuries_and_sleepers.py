import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

print("=== INJURED / FRAGILE PLAYERS (REAL STATUS != Available) ===")
inj = [p for p in players if p.get('is_injured') or (p.get('infortunio_status') and 'disponibile' not in str(p.get('infortunio_status')).lower())]
print(f"Total injured/doubtful: {len(inj)}")
for p in inj[:25]:
    print(f"- {p['name']} ({p['team']}, {p['role']}): Motivo: {p.get('infortunio_motivo')} | Status: {p.get('infortunio_status')} | Severity: {p.get('infortunio_severity')} | Rientro: {p.get('infortunio_rientro')}")

print("\n=== TOP BALLOTTAGGI (RUN-OFFS / MINS COMPETITION) ===")
ballottaggi = [p for p in players if 'ballottaggio' in str(p.get('titolarita_desc_2627', '')).lower() or 'rotazione' in str(p.get('titolarita_desc_2627', '')).lower() or 'subentrato' in str(p.get('titolarita_desc_2627', '')).lower()]
for p in ballottaggi[:20]:
    print(f"- {p['name']} ({p['team']}, {p['role']}): {p.get('titolarita_desc_2627')}")

print("\n=== TOP SLEEPERS / EXPLOIT CANDIDATES (COST <= 35 CR, HIGH IMPACT IN G1-G3) ===")
sleepers = []
for p in players:
    mr = p.get('match_reports_2627', {})
    mins = mr.get('minutes', 0)
    goals = mr.get('goals', 0)
    assists = mr.get('assists', 0)
    price = p.get('prezzo_cons', 1)
    ovr = p.get('ovr', 70)
    rating = mr.get('rating', 0)
    if price <= 45 and (goals >= 1 or assists >= 1 or mins >= 180):
        sleepers.append({
            'name': p['name'],
            'team': p['team'],
            'role': p['role'],
            'price': price,
            'ovr': ovr,
            'mins': mins,
            'goals': goals,
            'assists': assists,
            'desc': p.get('titolarita_desc_2627', ''),
            'adv': p.get('ai_advice', '')
        })

sleepers.sort(key=lambda x: (x['goals']*5 + x['assists']*3 + (x['mins']/90)*1.5 + (x['ovr']-70)*0.5), reverse=True)
for s in sleepers[:25]:
    print(f"- {s['name']} ({s['team']}, {s['role']}): Prezzo {s['price']} CR | OVR {s['ovr']} | Min: {s['mins']}' | G:{s['goals']} A:{s['assists']} | Tit: {s['desc']}")
