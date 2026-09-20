import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import unicodedata
from bs4 import BeautifulSoup

file_path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\968\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')
table = soup.find_all('table')[1]
rows = table.find_all('tr')

tm_injuries = []

for r in rows[1:]:
    tds = r.find_all('td')
    if len(tds) > 2:
        name = tds[1].get_text(strip=True)
        pos = tds[2].get_text(strip=True)
        
        # sample only one per matchday (step by 2)
        match_tds = [td for td in tds[3:] if 'afz' in td.get('class', [])]
        if not match_tds: match_tds = tds[4::2]
        
        real_injuries = []
        for g_idx, td in enumerate(match_tds):
            giornata = g_idx + 1
            # ONLY the red cross icon: span with class verletzt-table
            span_v = td.find('span', class_='verletzt-table')
            if span_v:
                title = span_v.get('title', '').strip()
                diag = title.split(' - ')[0] if ' - ' in title else title
                real_injuries.append((giornata, diag))
                
        tm_injuries.append({
            'name': name,
            'pos': pos,
            'injuries_count': len(real_injuries),
            'injuries': real_injuries
        })

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
    players_list = raw_data['players'] if isinstance(raw_data, dict) and 'players' in raw_data else raw_data

current_ata = [p for p in players_list if p.get('team') == 'Atalanta']

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower().replace(' ', '')

matched = []
for p in current_ata:
    pname = p['name']
    norm_p = norm(pname)
    rec = None
    
    if 'sulemana k' in pname.lower():
        rec = next((r for r in tm_injuries if 'kamaldeen' in r['name'].lower()), None)
    elif 'sulemana i' in pname.lower():
        rec = next((r for r in tm_injuries if 'ibrahim' in r['name'].lower()), None)
    elif 'ederson' in norm_p:
        rec = next((r for r in tm_injuries if 'ederson' in norm(r['name'])), None)
    elif 'pasalic' in norm_p:
        rec = next((r for r in tm_injuries if 'pasalic' in norm(r['name'])), None)
    elif 'samardzic' in norm_p:
        rec = next((r for r in tm_injuries if 'samardzic' in norm(r['name'])), None)
    elif 'krstovic' in norm_p:
        rec = next((r for r in tm_injuries if 'krstovic' in norm(r['name'])), None)
    else:
        for r in tm_injuries:
            norm_tm = norm(r['name'])
            if norm_p in norm_tm or norm_tm in norm_p:
                rec = r
                break
            p_tok = set(norm(t) for t in pname.split())
            tm_tok = set(norm(t) for t in r['name'].split())
            if len(p_tok.intersection(tm_tok)) >= 1 and (p_tok.intersection(tm_tok) != {'de'}):
                rec = r
                break

    if rec:
        matched.append({
            'fanta_name': pname,
            'tm_name': rec['name'],
            'role': p['role'],
            'ovr': p['ovr'],
            'inj_count': rec['injuries_count'],
            'injuries': rec['injuries']
        })
    else:
        matched.append({
            'fanta_name': pname,
            'tm_name': None,
            'role': p['role'],
            'ovr': p['ovr'],
            'inj_count': 0,
            'injuries': []
        })

matched.sort(key=lambda x: x['inj_count'], reverse=True)

print("=== CONTEGGIO ESATTO INFORTUNI (SOLO CROCE ROSSA) PER L'ATALANTA 25/26 ===")
for m in matched:
    print(f"[{m['role']}] {m['fanta_name']} (TM: {m['tm_name']}) -> {m['inj_count']} partite saltate per infortunio")
    if m['inj_count'] > 0:
        details = {}
        for g, d in m['injuries']:
            details.setdefault(d, []).append(g)
        for diag, days in details.items():
            days_str = ", ".join(f"G{d}" for d in days)
            print(f"    • {diag}: {len(days)} gare ({days_str})")
