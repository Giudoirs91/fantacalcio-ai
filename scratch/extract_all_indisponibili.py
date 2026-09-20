from bs4 import BeautifulSoup
import re

path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\867131f5-e3ac-404d-86be-6fad3b886bba\.system_generated\steps\267\content.md'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
team_cards = soup.find_all(class_='team-card')

all_injured = []
all_suspended = []

for tc in team_cards:
    team_el = tc.find(class_='team-name')
    team_name = team_el.get_text(strip=True) if team_el else "Unknown"
    
    cols = tc.find_all(class_='col')
    if not cols:
        continue
        
    # Col 1: Infortunati
    col_inj = cols[0]
    inj_lis = col_inj.find_all('li')
    for li in inj_lis:
        name_el = li.find(class_='item-name')
        desc_el = li.find(class_='item-description')
        if name_el:
            p_name = name_el.get_text(strip=True)
            desc = desc_el.get_text(strip=True) if desc_el else ""
            all_injured.append({
                'team': team_name,
                'name': p_name,
                'desc': desc
            })
            
    # Col 2: Squalificati & Diffidati
    if len(cols) > 1:
        col_susp = cols[1]
        # Look for squalificati list before diffidati header
        # Find squalificati header
        headers = col_susp.find_all('header')
        for h in headers:
            h_text = h.get_text(strip=True)
            if 'Squalificati' in h_text:
                # sibling list or empty message
                nxt = h.find_next_sibling()
                if nxt and nxt.name == 'ul':
                    for li in nxt.find_all('li'):
                        name_el = li.find(class_='item-name')
                        desc_el = li.find(class_='item-description')
                        if name_el:
                            all_suspended.append({
                                'team': team_name,
                                'name': name_el.get_text(strip=True),
                                'desc': desc_el.get_text(strip=True) if desc_el else ""
                            })

print(f"=== TOTALE INFORTUNATI ESTRATTI: {len(all_injured)} ===")
for inj in all_injured:
    print(f"[{inj['team']:12s}] {inj['name']:18s} -> {inj['desc']}")

print(f"\n=== TOTALE SQUALIFICATI ESTRATTI: {len(all_suspended)} ===")
for susp in all_suspended:
    print(f"[{susp['team']:12s}] {susp['name']:18s} -> {susp['desc']}")
