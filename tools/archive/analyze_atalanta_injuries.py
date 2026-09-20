import sys
sys.stdout.reconfigure(encoding='utf-8')
import unicodedata
from bs4 import BeautifulSoup
import json

file_path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\968\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Load our 2026/27 master listone
with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
    players_list = raw_data['players'] if isinstance(raw_data, dict) and 'players' in raw_data else raw_data

current_atalanta_players = [p for p in players_list if p.get('team') == 'Atalanta']

soup = BeautifulSoup(content, 'html.parser')
table = soup.find_all('table')[1]
rows = table.find_all('tr')

tm_records = []

for r in rows[1:]:
    tds = r.find_all('td')
    if len(tds) > 2:
        name = tds[1].get_text(strip=True)
        pos = tds[2].get_text(strip=True)
        
        match_tds = [td for td in tds[3:] if 'afz' in td.get('class', [])]
        if not match_tds:
            match_tds = tds[4::2]
        
        injuries_by_type = {}
        total_missed_injury = 0
        total_missed_suspension = 0
        total_not_called = 0
        
        for g_idx, td in enumerate(match_tds):
            giornata = g_idx + 1
            classes = td.get('class', [])
            
            span_v = td.find('span', class_='verletzt-table')
            if span_v or 'ausfallzeiten_v' in classes or any('rot' in c for c in classes):
                total_missed_injury += 1
                reason = span_v.get('title', '').strip() if span_v else 'Infortunio non specificato'
                base_reason = reason.split(' - ')[0] if ' - ' in reason else reason
                if not base_reason:
                    base_reason = 'Infortunio non specificato'
                if base_reason not in injuries_by_type:
                    injuries_by_type[base_reason] = []
                injuries_by_type[base_reason].append(giornata)
            elif 'ausfallzeiten_g' in classes or 'ausfallzeiten_r' in classes or any('gelb' in c for c in classes):
                total_missed_suspension += 1
            elif 'ausfallzeiten_k' in classes:
                total_not_called += 1
                
        tm_records.append({
            'name': name,
            'pos': pos,
            'missed_injury': total_missed_injury,
            'injuries_detail': injuries_by_type,
            'missed_suspension': total_missed_suspension,
            'total_matchdays': len(match_tds)
        })

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower().replace(' ', '')

# Match with current listone
matched_results = []
for p in current_atalanta_players:
    pname = p['name']
    norm_p = norm(pname)
    matched_rec = None
    
    # Specific disambiguation
    if 'sulemana k' in pname.lower():
        matched_rec = next((r for r in tm_records if 'kamaldeen' in r['name'].lower()), None)
    elif 'sulemana i' in pname.lower():
        matched_rec = next((r for r in tm_records if 'ibrahim' in r['name'].lower()), None)
    elif 'ederson' in norm_p:
        matched_rec = next((r for r in tm_records if 'ederson' in norm(r['name'])), None)
    elif 'pasalic' in norm_p:
        matched_rec = next((r for r in tm_records if 'pasalic' in norm(r['name'])), None)
    elif 'samardzic' in norm_p:
        matched_rec = next((r for r in tm_records if 'samardzic' in norm(r['name'])), None)
    elif 'krstovic' in norm_p:
        matched_rec = next((r for r in tm_records if 'krstovic' in norm(r['name'])), None)
    else:
        for rec in tm_records:
            norm_tm = norm(rec['name'])
            if norm_p in norm_tm or norm_tm in norm_p:
                matched_rec = rec
                break
            p_tok = set(norm(t) for t in pname.split())
            tm_tok = set(norm(t) for t in rec['name'].split())
            if len(p_tok.intersection(tm_tok)) >= 1 and (p_tok.intersection(tm_tok) != {'de'}):
                matched_rec = rec
                break

    if matched_rec:
        matched_results.append({
            'in_tm': True,
            'fanta_name': pname,
            'tm_name': matched_rec['name'],
            'role': p['role'],
            'ovr': p['ovr'],
            'missed_injury': matched_rec['missed_injury'],
            'injuries_detail': matched_rec['injuries_detail']
        })
    else:
        matched_results.append({
            'in_tm': False,
            'fanta_name': pname,
            'tm_name': 'N/D (Nuovo arrivo / Altro club 25/26)',
            'role': p['role'],
            'ovr': p['ovr'],
            'missed_injury': 0,
            'injuries_detail': {}
        })

matched_results.sort(key=lambda x: x['missed_injury'], reverse=True)

print("=== ANALISI ATALANTA 2026/2027 vs INFORTUNI TRANSFERMARKT 2025/2026 ===")
print(f"Totale Giocatori Atalanta nel Listone 26/27: {len(matched_results)}")
print()

for r in matched_results:
    if r['in_tm']:
        if r['missed_injury'] >= 10:
            frag_label = "🔴 ALTA FRAGILITÀ (>= 10 partite saltate)"
        elif r['missed_injury'] >= 4:
            frag_label = "🟡 MEDIA FRAGILITÀ (4-9 partite saltate)"
        else:
            frag_label = "🟢 BASSA / AFFIDABILE (0-3 partite saltate)"
            
        print(f"[{r['role']}] {r['fanta_name']} (TM: {r['tm_name']}) - OVR: {r['ovr']}")
        print(f"   Partite saltate per infortunio nel 25/26: {r['missed_injury']}/38 -> {frag_label}")
        if r['injuries_detail']:
            for inj_name, days in r['injuries_detail'].items():
                print(f"   • {inj_name}: {len(days)} giornate (G{days[0]}-G{days[-1]})")
        else:
            print("   • Nessun infortunio registrato nel 2025/26 (38/38 convocato/disponibile)")
    else:
        print(f"[{r['role']}] {r['fanta_name']} - OVR: {r['ovr']}")
        print("   Non militava nell'Atalanta nel 2025/26 (Acquisto estivo / Estero / Altra squadra)")
    print()
