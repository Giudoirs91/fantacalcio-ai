import json

with open('processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

by_role = {'P': [], 'D': [], 'C': [], 'A': []}
for p in players:
    by_role[p['role']].append(p)

for r, r_players in by_role.items():
    r_players.sort(key=lambda x: (-x['ovr'], -x['prezzo_cons'], -x['fvm']))
    print(f"=== ROLE {r} (Total: {len(r_players)}) ===")
    for rank, pl in enumerate(r_players[:16], 1):
        slot_num = ((rank - 1) // 8) + 1
        name = pl['name']
        ovr = pl['ovr']
        prezzo = pl['prezzo_cons']
        team = pl['team']
        print(f"{rank:2d}. [{slot_num}° Slot {r}] {name:20} | OVR: {ovr:2d} | Prezzo: {prezzo:3d} CR | Team: {team}")
