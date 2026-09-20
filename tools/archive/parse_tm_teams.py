import re

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\6407e6e6-e258-4577-8610-5fc007ee1b1c\.system_generated\steps\104\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

teams_data = re.findall(r'## La probabile formazione dell[a\']*\s*([^\n\r]+?)\s*2026/27\s*\n(.*?)(?=\n## La probabile|\Z)', text, re.DOTALL)

print(f"Trovate {len(teams_data)} formazioni di club:\n")
for tname, body in teams_data:
    print(f"=== {tname.strip()} ===")
    lines = [l.strip() for l in body.split('\n') if l.strip()]
    for l in lines:
        if "Movimenti" in l or "Ballottaggi" in l or "Rigoristi" in l or "Punizioni" in l or "In bilico" in l:
            print("  " + l)
