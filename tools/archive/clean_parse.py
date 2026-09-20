with open('full_tm_details_20_teams.txt', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Dividi per "TEAM: "
blocks = re.split(r'TEAM: ', content)

with open('clean_20_teams_parsed.txt', 'w', encoding='utf-8') as out:
    for b in blocks[1:]:
        header = b[:b.find('\n')].strip()
        body = b[b.find('\n'):].strip()
        out.write(f"=== {header} ===\n")
        for line in body.split('\n'):
            line = line.strip()
            if any(k in line for k in ["Movimenti", "Ballottaggi", "Rigoristi", "Punizioni", "In bilico", "Assenza", "Obiettivi", "Giovani"]):
                out.write(line + "\n")
        out.write("\n")

print("clean_20_teams_parsed.txt creato!")
