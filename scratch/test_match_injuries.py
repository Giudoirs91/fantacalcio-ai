import json
import re
import sys
from bs4 import BeautifulSoup
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\5669a18c-ff6d-45d7-87f2-c433188ebe8a\.system_generated\steps\713\content.md', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table', id='infortunati_ufficiali')
rows = table.find_all('tr')[1:]

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    master_players = json.load(f)

print(f"Total rows in scraped table: {len(rows)}")
print(f"Master players: {len(master_players)}")

scraped = []
for r in rows:
    tds = r.find_all('td')
    if len(tds) < 4:
        continue
    team = tds[0].get_text(strip=True)
    # The player td often has surname in uppercase, name in lowercase:
    # e.g. HIEN Isak, or SULEMANA Kamaldeen
    p_text = tds[1].get_text(" ", strip=True)
    motivo = tds[2].get_text(strip=True)
    rientro = tds[3].get_text(strip=True)
    scraped.append({
        'team': team,
        'raw_name': p_text,
        'motivo': motivo,
        'rientro': rientro
    })

# Matching logic
matched = []
unmatched = []

for item in scraped:
    team_l = item['team'].lower().strip()
    raw_name = item['raw_name'].strip()
    
    # Extract tokens
    # e.g. "HIEN Isak" -> tokens: ["hien", "isak"]
    tokens = [t.lower() for t in re.split(r'[\s\.\-]+', raw_name) if len(t) >= 2]
    
    found = None
    # 1. Search in same team
    candidates_team = [p for p in master_players if team_l in p['team'].lower() or p['team'].lower() in team_l]
    
    # Exact surname match in team
    for p in candidates_team:
        p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p['name']) if len(t) >= 2]
        if any(tok in p_toks for tok in tokens):
            found = p
            break
            
    # 2. If not found in team, maybe transferred or team alias (e.g. Verona/Monza/Empoli/Genoa)
    if not found:
        for p in master_players:
            p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p['name']) if len(t) >= 3]
            # Match if first token (usually surname) matches
            if tokens and tokens[0] in p_toks:
                found = p
                break
                
    if found:
        matched.append((item, found))
    else:
        unmatched.append(item)

print(f"Matched: {len(matched)}")
print(f"Unmatched: {len(unmatched)}")

if unmatched:
    print("\n--- UNMATCHED ---")
    for u in unmatched:
        print(f"  {u['team']} - {u['raw_name']} (Motivo: {u['motivo'][:30]})")

print("\n--- MATCHED SAMPLES (first 10) ---")
for item, p in matched[:10]:
    print(f"  Scraped: [{item['team']}] {item['raw_name']} ({item['rientro']}) -> Master: [{p['team']}] {p['name']} (ID: {p['id']})")
