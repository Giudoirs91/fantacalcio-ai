import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

print(f"=== VERIFICA LISTONE AGGIORNATO (TOTALE: {len(players)} CALCIATORI) ===")
print("Esempi di calciatori:")
for p in players[:8]:
    print(f"  {p['name']:<18} ({p['team']:<10} - {p['role']}) | OVR: {p['ovr']} | Prezzo Cons: {p['prezzo_cons']} CR | Slot: {p['slot_fascia']} | Dati 25/26: {p['has_data_2526']}")

print("\nConteggio per Ruolo:")
roles = {}
for p in players:
    roles[p['role']] = roles.get(p['role'], 0) + 1
for r, cnt in roles.items():
    print(f"  Ruolo {r}: {cnt} calciatori")
