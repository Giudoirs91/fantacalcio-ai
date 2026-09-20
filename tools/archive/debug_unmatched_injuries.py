import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import json
import re
import unicodedata

def strip_accents(text):
    text = unicodedata.normalize('NFD', str(text))
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

def clean_text(t):
    t = strip_accents(str(t)).lower().strip()
    t = re.sub(r"['\".,-]", " ", t)
    return " ".join(t.split())

df_inj = pd.read_csv('data/raw/infortuni_2025_26.csv')
with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

master_lookup = {}
for p in master:
    c = clean_text(p['name'])
    master_lookup[c] = p
    tokens = c.split()
    if len(tokens) >= 2:
        # e.g. "pellegrini lo" -> last name "pellegrini"
        last = tokens[0]
        # map last name if unique
        if last not in master_lookup:
            master_lookup[last] = p

unmatched = []
matched = []
for _, row in df_inj.iterrows():
    name = str(row['Giocatore']).strip()
    cname = clean_text(name)
    team = str(row['Squadra']).strip()
    
    found = None
    if cname in master_lookup:
        found = master_lookup[cname]['name']
    else:
        tokens = cname.split()
        for mn, p in master_lookup.items():
            if all(t in mn for t in tokens) or all(t in cname for t in mn.split()):
                found = p['name']
                break
        if not found and len(tokens) >= 1:
            # check last token
            last_tok = tokens[-1]
            for mn, p in master_lookup.items():
                if last_tok in mn.split():
                    found = p['name']
                    break
    if found:
        matched.append((name, found))
    else:
        unmatched.append((name, team))

print(f"Total CSV items: {len(df_inj)}")
print(f"Matched: {len(matched)}")
print(f"Unmatched: {len(unmatched)}")
for u in unmatched:
    print("  Unmatched:", u)
