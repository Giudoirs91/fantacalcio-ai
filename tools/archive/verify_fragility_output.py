import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

print(f"Total players in master: {len(players)}")
frag_counts = {}
for p in players:
    f_val = p.get('fragilita_val', 'N/A')
    frag_counts[f_val] = frag_counts.get(f_val, 0) + 1

print("Fragility Breakdown across Serie A 2026/27:")
for k, v in frag_counts.items():
    print(f"  {k}: {v} giocatori")

sample_names = ['Martinez Jo.', 'Sommer', 'Dybala', 'Neres', 'Berardi', 'Pulisic', 'Zaniolo', 'Lukaku', 'Lautaro Martinez', 'Bremer', 'Calhanoglu', 'Zapata', 'Rrahmani', 'Bastoni', 'Bisseck', 'Provedel']
print("\n--- SAMPLE CALCIATORI (CONFRONTO LIVELLO FRAGILITÀ E PESO SU OVR) ---")
for s in sample_names:
    matches = [p for p in players if s.lower() in p['name'].lower()]
    for p in matches[:1]:
        print(f"{p['name']:20} | {p['team']:10} | {p['role']} | {p['fragilita_val']:8} | OVR: {p['ovr']:2d} | Prezzo: {p['prezzo_cons']:3d} CR | Advice: {p['ai_advice'][:28]:28} | Storico: {p.get('fragilita_dettaglio')}")
