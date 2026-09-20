import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
from bs4 import BeautifulSoup
import pandas as pd
from src.player_matcher import clean_text, match_player_name

html_path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\867131f5-e3ac-404d-86be-6fad3b886bba\.system_generated\steps\267\content.md'
with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Load players from listone
df_listone = pd.read_excel('data/raw/Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1).dropna(subset=['Id', 'Nome', 'Squadra'])

players_by_team = {}
for _, r in df_listone.iterrows():
    t = str(r['Squadra']).strip()
    if t not in players_by_team:
        players_by_team[t] = []
    players_by_team[t].append({
        'id': int(r['Id']),
        'name': str(r['Nome']).strip(),
        'clean_name': clean_text(str(r['Nome'])),
        'role': str(r['R']).strip(),
        'team': t
    })

# Team name normalization
team_aliases = {
    'Inter': 'Inter',
    'Juventus': 'Juventus',
    'Milan': 'Milan',
    'Napoli': 'Napoli',
    'Roma': 'Roma',
    'Lazio': 'Lazio',
    'Atalanta': 'Atalanta',
    'Bologna': 'Bologna',
    'Fiorentina': 'Fiorentina',
    'Torino': 'Torino',
    'Monza': 'Monza',
    'Genoa': 'Genoa',
    'Lecce': 'Lecce',
    'Udinese': 'Udinese',
    'Cagliari': 'Cagliari',
    'Verona': 'Verona',
    'Como': 'Como',
    'Parma': 'Parma',
    'Venezia': 'Venezia',
    'Sassuolo': 'Sassuolo',
    'Frosinone': 'Frosinone',
    'Empoli': 'Empoli'
}

raw_injuries = []
team_cards = soup.find_all(class_='team-card')
for tc in team_cards:
    t_el = tc.find(class_='team-name')
    if not t_el:
        continue
    raw_team = t_el.get_text(strip=True)
    norm_team = team_aliases.get(raw_team, raw_team)
    
    cols = tc.find_all(class_='col')
    if not cols:
        continue
    
    for li in cols[0].find_all('li'):
        name_el = li.find(class_='item-name')
        desc_el = li.find(class_='item-description')
        if name_el:
            p_name = name_el.get_text(strip=True)
            p_desc = desc_el.get_text(strip=True) if desc_el else ""
            raw_injuries.append({
                'team': norm_team,
                'name': p_name,
                'desc': p_desc
            })

print(f"Estratti {len(raw_injuries)} infortuni grezzi da fantacalcio.it.")

def estimate_rientro_and_severity(desc):
    d_lower = desc.lower()
    
    # Check severity
    # Long term keywords:
    long_terms = ['crociato', 'intervento', 'operato', 'rottura', 'frattura', 'mesi', 'tre mesi', 'due mesi', 'gennaio', 'dicembre', 'novembre', 'lungo stop', 'lesione di alto grado', 'lesione di secondo grado', 'aritmia']
    is_long = any(lt in d_lower for lt in long_terms)
    
    # Return date parsing
    rientro_str = "TBD"
    if 'metà settembre' in d_lower or 'seconda metà di settembre' in d_lower or 'metà di settembre' in d_lower:
        rientro_str = "20/09/2026"
    elif 'fine settembre' in d_lower:
        rientro_str = "28/09/2026"
    elif 'inizio ottobre' in d_lower or "dall'inizio di ottobre" in d_lower or "dall'inizio ottobre" in d_lower or "da inizio ottobre" in d_lower:
        rientro_str = "04/10/2026"
    elif 'metà ottobre' in d_lower or 'prima metà di ottobre' in d_lower or 'metà di ottobre' in d_lower:
        rientro_str = "18/10/2026"
    elif 'fine ottobre' in d_lower or 'da fine ottobre' in d_lower:
        rientro_str = "25/10/2026"
    elif 'novembre' in d_lower:
        if 'fine novembre' in d_lower:
            rientro_str = "29/11/2026"
        else:
            rientro_str = "08/11/2026"
    elif 'dicembre' in d_lower:
        rientro_str = "15/12/2026"
    elif 'gennaio' in d_lower:
        rientro_str = "10/01/2027"
    elif '4a giornata' in d_lower or '4a di campionato' in d_lower:
        rientro_str = "15/09/2026"
    elif 'prossimo turno' in d_lower or 'dalla prossima' in d_lower or 'da valutare' in d_lower:
        rientro_str = "15/09/2026"

    # Match exact date like "11/10/2026"
    m_date = re.search(r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b', desc)
    if m_date:
        rientro_str = m_date.group(1)

    severity = "red" if is_long else "orange"
    tipo_stop = "Lunga Degenza" if is_long else "Prossimo al Rientro"
    
    return rientro_str, severity, tipo_stop

matched_injuries = []
unmatched = []

for inj in raw_injuries:
    t = inj['team']
    p_name = inj['name']
    c_name = clean_text(p_name)
    desc = inj['desc']
    
    # Candidate list in team
    cands = players_by_team.get(t, [])
    
    matched_cand = None
    # 1. Exact clean match
    for cand in cands:
        if cand['clean_name'] == c_name:
            matched_cand = cand
            break
            
    # 2. Token match
    if not matched_cand:
        for cand in cands:
            if c_name in cand['clean_name'] or cand['clean_name'] in c_name:
                matched_cand = cand
                break
                
    # 3. Last name token match
    if not matched_cand:
        tokens = c_name.split()
        for cand in cands:
            cand_tokens = cand['clean_name'].split()
            if tokens and cand_tokens and tokens[0] == cand_tokens[0]:
                matched_cand = cand
                break
                
    # 4. Global match across all teams if transferred
    if not matched_cand:
        for all_t, t_cands in players_by_team.items():
            for cand in t_cands:
                if cand['clean_name'] == c_name:
                    matched_cand = cand
                    break
            if matched_cand:
                break

    rientro, severity, tipo_stop = estimate_rientro_and_severity(desc)
    
    if matched_cand:
        matched_injuries.append({
            "player": matched_cand['name'],
            "player_id": matched_cand['id'],
            "team": matched_cand['team'],
            "motivo": desc,
            "rientro": rientro,
            "severity": severity,
            "tipo_stop": tipo_stop,
            "fonte": "fantacalcio.it"
        })
    else:
        unmatched.append(inj)

print(f"\n✓ Calciatori infortunati matchati con successo nel listone: {len(matched_injuries)}")
if unmatched:
    print(f"⚠️ Calciatori non matchati nel listone ({len(unmatched)}):")
    for u in unmatched:
        print(f"   - [{u['team']}] {u['name']}")

print("\nEsempi infortuni pronti per config/injuries.json:")
for rec in matched_injuries[:10]:
    print(f"  [{rec['team']:10s}] {rec['player']:16s} (ID: {rec['player_id']:4d}) -> Rientro: {rec['rientro']} | {rec['severity']} | {rec['motivo'][:60]}...")

# Check if we should update config/injuries.json
with open('config/injuries.json', 'w', encoding='utf-8') as f:
    json.dump(matched_injuries, f, ensure_ascii=False, indent=2)

print(f"\n✓ Salvato config/injuries.json con {len(matched_injuries)} infortuni ufficiali aggiornati!")
