import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

print("================================================================")
print("1. INFORTUNI PESANTI E FRAGILITÀ CRONICHE (DA EVITARE O SVALUTARE)")
print("================================================================")
fragili = [p for p in players if p.get('is_injured') or p.get('is_chronic_fragile') or p.get('fragilita_score', 0) >= 3]
for p in fragili[:15]:
    motivo = p.get('infortunio_motivo') or 'Storico infortuni elevato'
    status = p.get('infortunio_status') or 'Attivo ma fragile'
    print(f"- {p['name']} ({p['team']}, {p['role']}) | Costo: {p.get('prezzo_cons')} CR | Status: {status} | Motivo: {motivo}")

print("\n================================================================")
print("2. I BALLOTTAGGI PIÙ ROVENTI (MINUTI CONDIVISI / RISCHIO S.V.)")
print("================================================================")
ballottaggi = [p for p in players if p.get('is_in_ballottaggio') or 'ballottaggio' in str(p.get('titolarita_desc_2627')).lower() or 'subentrato' in str(p.get('titolarita_desc_2627')).lower()]
ballottaggi.sort(key=lambda x: x.get('prezzo_cons', 0), reverse=True)
for p in ballottaggi[:15]:
    print(f"- {p['name']} ({p['team']}, {p['role']}) | Costo: {p.get('prezzo_cons')} CR | Status: {p.get('titolarita_desc_2627')} | Fascia: {p.get('slot_fascia')}")

print("\n================================================================")
print("3. I GIOVANI / SLEEPER PRONTI ALL'ESPLOIT CHE NESSUNO HA NOTATO")
print("================================================================")
candidates = []
for p in players:
    price = p.get('prezzo_cons', 1)
    g = p.get('gol_2627', 0)
    a = p.get('assist_2627', 0)
    xg = p.get('xg_2627', 0.0) or 0.0
    xa = p.get('xa_2627', 0.0) or 0.0
    rating = p.get('rating_fotmob_2627', 0.0) or 0.0
    mins = p.get('minuti_2627', 0)
    ovr = p.get('ovr', 70)
    # under 35 credits
    if price <= 35 and (g >= 1 or a >= 1 or xg >= 0.4 or xa >= 0.3 or mins >= 180):
        score = g * 4 + a * 2.5 + xg * 3 + xa * 2 + (rating - 6.5) * 2 + (mins / 90) * 1.5
        candidates.append((score, p))

candidates.sort(key=lambda x: x[0], reverse=True)
for score, p in candidates[:15]:
    print(f"- {p['name']} ({p['team']}, {p['role']}) | Costo: {p.get('prezzo_cons')} CR (Listone: {p.get('qta')}) | Min: {p.get('minuti_2627')}' | G:{p.get('gol_2627')} A:{p.get('assist_2627')} xG:{p.get('xg_2627')} xA:{p.get('xa_2627')} | FotMob: {p.get('rating_fotmob_2627')} | Consiglio: {p.get('ai_advice')}")
