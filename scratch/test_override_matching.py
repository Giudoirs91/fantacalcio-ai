import os
import sys
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\5669a18c-ff6d-45d7-87f2-c433188ebe8a\.system_generated\steps\713\content.md'
PLAYERS_MASTER = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ROOT_MASTER = os.path.join(ROOT_DIR, "processed_players_master.json")

with open(HTML_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table', id='infortunati_ufficiali')
rows = table.find_all('tr')[1:]

with open(PLAYERS_MASTER, 'r', encoding='utf-8') as f:
    players = json.load(f)

# Specific manual alias overrides for tricky names
NAME_OVERRIDES = {
    ('Atalanta', 'SULEMANA Ibrahim'): 'Sulemana I.',
    ('Sassuolo', 'SULEMANA Ibrahim'): 'Sulemana I.',
    ('Venezia', 'FRANJIć Bartol'): 'Franjic',
    ('Venezia', 'FRANJIC Bartol'): 'Franjic',
    ('Sassuolo', 'CANDE Fali'): 'Candè',
    ('Sassuolo', 'KONE Ismaël'): 'Konè I.',
    ('Roma', 'PELLEGRINI Lorenzo'): 'Pellegrini Lo.',
    ('Fiorentina', 'OULAI Christ Ravynel Inao'): 'Oulai',
    ('Napoli', 'GIOVANE Santana do Nascimento'): 'Giovane',
    ('Napoli', 'ANGUISSA André Zambo'): 'Anguissa',
    ('Napoli', 'SANTOS Alisson'): 'Santos A.',
    ('Parma', 'NICOLUSSI CAVIGLIA Hans'): 'Nicolussi Caviglia',
}

scraped_entries = []
for r in rows:
    tds = r.find_all('td')
    if len(tds) < 4:
        continue
    team = tds[0].get_text(strip=True)
    p_name = tds[1].get_text(" ", strip=True)
    motivo = tds[2].get_text(strip=True)
    rientro = tds[3].get_text(strip=True)
    scraped_entries.append({
        'team': team,
        'raw_name': p_name,
        'motivo': motivo,
        'rientro': rientro
    })

matched_map = {} # player_id -> injury_info
matched_count = 0

for item in scraped_entries:
    team_orig = item['team']
    team_l = team_orig.lower().strip()
    raw_name = item['raw_name'].strip()
    
    # Check overrides first
    override_key = (team_orig, raw_name)
    matched_player = None
    
    if override_key in NAME_OVERRIDES:
        target_name = NAME_OVERRIDES[override_key]
        for p in players:
            if p['name'].lower() == target_name.lower():
                matched_player = p
                break
                
    if not matched_player:
        # Normalize accents and tokenize
        import unicodedata
        clean_raw = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('utf-8')
        tokens = [t.lower() for t in re.split(r'[\s\.\-]+', clean_raw) if len(t) >= 2]
        
        # 1. Search in same team
        team_players = [p for p in players if team_l in p['team'].lower() or p['team'].lower() in team_l]
        
        # Exact match of full surname token (tokens[0])
        for p in team_players:
            p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
            p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
            if tokens and tokens[0] in p_toks:
                matched_player = p
                break
                
        # If not, check if any token matches
        if not matched_player:
            for p in team_players:
                p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
                p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
                if any(tok in p_toks for tok in tokens):
                    matched_player = p
                    break
                    
        # 2. Search across entire listone if first token >= 4 chars
        if not matched_player and tokens and len(tokens[0]) >= 4:
            for p in players:
                p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
                p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
                if tokens[0] in p_toks:
                    matched_player = p
                    break

    if matched_player:
        matched_map[matched_player['id']] = {
            'player': matched_player,
            'motivo': item['motivo'],
            'rientro': item['rientro'],
            'raw_name': item['raw_name'],
            'team_scraped': item['team']
        }
        matched_count += 1
    else:
        print(f"Non matchato (primavera/estero/non in listone): [{item['team']}] {item['raw_name']}")

print(f"\nTotale infortuni scraped: {len(scraped_entries)}")
print(f"Matchati con calciatori del Listone Serie A: {len(matched_map)}")
