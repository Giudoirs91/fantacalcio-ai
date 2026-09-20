import re

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\6407e6e6-e258-4577-8610-5fc007ee1b1c\.system_generated\steps\104\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Trova tutti i blocchi
sections = re.split(r'## La probabile formazione dell?[aie\']* *', text)

with open('full_tm_details_20_teams.txt', 'w', encoding='utf-8') as out:
    for s in sections[1:]:
        out.write("======================================================================\n")
        lines = s.strip().split('\n')
        team_title = lines[0].strip()
        out.write(f"TEAM: {team_title}\n")
        out.write("======================================================================\n")
        for line in lines[1:]:
            out.write(line + "\n")
        out.write("\n\n")

print("Dettaglio completo salvato in full_tm_details_20_teams.txt")
