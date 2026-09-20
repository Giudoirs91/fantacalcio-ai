with open('full_tm_details_20_teams.txt', 'r', encoding='utf-8') as f:
    text = f.read()

import re
teams_blocks = text.split("======================================================================")

for b in teams_blocks:
    if "TEAM:" in b:
        lines = [l.strip() for l in b.split('\n') if l.strip()]
        team_name = lines[0]
        details = [l for l in lines if any(k in l for k in ["Movimenti", "Ballottaggi", "Rigoristi", "Punizioni", "In bilico", "Assenza"])]
        print(f"\n>>> {team_name}")
        for d in details:
            print("  ", d)
