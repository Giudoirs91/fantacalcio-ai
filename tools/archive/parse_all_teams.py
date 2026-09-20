import re

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\6407e6e6-e258-4577-8610-5fc007ee1b1c\.system_generated\steps\104\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Trova tutti i titoli ## La probabile formazione
matches = re.split(r'## La probabile formazione dell[ae\']* *', text)

with open('extracted_tm_lineups.txt', 'w', encoding='utf-8') as out:
    for m in matches[1:]:
        header_end = m.find('\n')
        team_name = m[:header_end].strip()
        body = m[header_end:].strip()
        out.write(f"==================================================\n")
        out.write(f"SQUADRA: {team_name}\n")
        out.write(f"==================================================\n")
        for line in body.split('\n'):
            line = line.strip()
            if any(k in line for k in ["Movimenti", "Ballottaggi", "Rigoristi", "Punizioni", "In bilico", "Assenza", "Obiettivi"]):
                out.write(f"{line}\n")
        out.write("\n")

print("Estratto con successo in 'extracted_tm_lineups.txt'!")
