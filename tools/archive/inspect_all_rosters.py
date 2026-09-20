import json

with open('all_20_teams_roster_2026_27.json', 'r', encoding='utf-8') as f:
    rosters = json.load(f)

with open('listone_rosters_utf8.txt', 'w', encoding='utf-8') as out:
    for team, players in rosters.items():
        out.write(f"\n=======================================================\n")
        out.write(f"SQUADRA LISTONE 2026_27: {team} ({len(players)} giocatori)\n")
        out.write(f"=======================================================\n")
        for role in ['P', 'D', 'C', 'A']:
            r_players = [p for p in players if p['role'] == role]
            names_fvm = [f"{p['name']} (FVM {int(p['fvm'])}, Qt {int(p['qta'])})" for p in r_players]
            out.write(f"  [{role}]: {', '.join(names_fvm)}\n")

print("listone_rosters_utf8.txt creato con successo!")
