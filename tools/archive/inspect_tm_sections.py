import re

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\6407e6e6-e258-4577-8610-5fc007ee1b1c\.system_generated\steps\104\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Trova tutti i titoli h2
h2_matches = re.findall(r'## (.*?)\n', text)
print("=== TITOLI H2 TROVATI NELL'ARTICOLO TRANSFERMARKT ===")
for h in h2_matches:
    print(h)
