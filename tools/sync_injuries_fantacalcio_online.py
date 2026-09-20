import os
import sys
import re
import json
import unicodedata
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from src.valuation_engine import determine_advice_tag

URL = "https://www.fantacalcio-online.com/it/infortunati-serie-a"
LOCAL_BACKUP_HTML = os.path.join(ROOT_DIR, "data", "raw", "infortunati_fantacalcio_online.html")
PLAYERS_MASTER = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ROOT_MASTER = os.path.join(ROOT_DIR, "processed_players_master.json")

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

def fetch_html():
    print(f"-> [InjuriesSync] Download da {URL}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    req = urllib.request.Request(URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
            os.makedirs(os.path.dirname(LOCAL_BACKUP_HTML), exist_ok=True)
            with open(LOCAL_BACKUP_HTML, 'w', encoding='utf-8') as f:
                f.write(html)
            print("-> [InjuriesSync] Download completato con successo.")
            return html
    except Exception as e:
        print(f"-> [InjuriesSync] Avviso: Errore nel download live ({e}). Tento backup locale...")
        # Check brain step path or local backup
        brain_path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\5669a18c-ff6d-45d7-87f2-c433188ebe8a\.system_generated\steps\713\content.md'
        if os.path.exists(LOCAL_BACKUP_HTML):
            with open(LOCAL_BACKUP_HTML, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif os.path.exists(brain_path):
            with open(brain_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        raise e

def parse_injuries(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='infortunati_ufficiali')
    if not table:
        tables = soup.find_all('table')
        if tables:
            table = tables[0]
        else:
            raise ValueError("Tabella infortunati non trovata nell'HTML.")

    rows = table.find_all('tr')[1:]
    injuries = []
    for r in rows:
        tds = r.find_all('td')
        if len(tds) < 4:
            continue
        team = tds[0].get_text(strip=True)
        name = tds[1].get_text(" ", strip=True)
        motivo = tds[2].get_text(strip=True)
        rientro = tds[3].get_text(strip=True)
        fonte = tds[4].get_text(strip=True) if len(tds) > 4 else ""
        injuries.append({
            'team': team,
            'raw_name': name,
            'motivo': motivo,
            'rientro': rientro,
            'fonte': fonte
        })
    print(f"-> [InjuriesSync] Estratti {len(injuries)} infortuni ufficiali dalla tabella.")
    return injuries

def calculate_injury_metrics(motivo, rientro_str):
    m_lower = motivo.lower()
    r_date = None
    try:
        r_date = datetime.strptime(rientro_str, "%d/%m/%Y")
    except Exception:
        pass

    # Diagnosi gravi
    is_grave = any(kw in m_lower for kw in [
        'crociato', 'tendine d\'achille', 'rottura', 'operato', 'lussazione rotula',
        'frattura', 'ablazione', 'alto grado', '2027'
    ])

    if r_date:
        if r_date >= datetime(2027, 1, 1):
            severity = 'red'
            giornate_perse = 18
        elif r_date >= datetime(2026, 11, 1):
            severity = 'red'
            giornate_perse = 8
        elif r_date >= datetime(2026, 10, 10) or is_grave:
            severity = 'red'
            giornate_perse = 5
        elif r_date >= datetime(2026, 9, 20):
            severity = 'orange'
            giornate_perse = 2
        else:
            severity = 'orange'
            giornate_perse = 1
    else:
        if is_grave:
            severity = 'red'
            giornate_perse = 8
        else:
            severity = 'orange'
            giornate_perse = 2

    status_icon = "🔴" if severity == 'red' else "🟠"
    status_str = f"{status_icon} {motivo} (Rientro: {rientro_str})"

    return severity, giornate_perse, status_str

def sync_injuries():
    html = fetch_html()
    scraped_injuries = parse_injuries(html)

    with open(PLAYERS_MASTER, 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Reset infortuni per tutti i giocatori (per azzerare chi è guarito)
    # Conserviamo lo stato precedente per il log
    previously_injured = {p['id']: p for p in players if p.get('is_injured')}

    new_injured_ids = set()
    matched_log = []

    for item in scraped_injuries:
        team_orig = item['team']
        team_l = team_orig.lower().strip()
        raw_name = item['raw_name'].strip()

        matched_p = None
        override_key = (team_orig, raw_name)
        if override_key in NAME_OVERRIDES:
            target_name = NAME_OVERRIDES[override_key]
            for p in players:
                if p['name'].lower() == target_name.lower():
                    matched_p = p
                    break

        if not matched_p:
            clean_raw = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('utf-8')
            tokens = [t.lower() for t in re.split(r'[\s\.\-]+', clean_raw) if len(t) >= 2]

            # 1. Ricerca squadra esatta
            team_players = [p for p in players if team_l in p['team'].lower() or p['team'].lower() in team_l]
            for p in team_players:
                p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
                p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
                if tokens and tokens[0] in p_toks:
                    matched_p = p
                    break

            if not matched_p:
                for p in team_players:
                    p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
                    p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
                    if any(tok in p_toks for tok in tokens):
                        matched_p = p
                        break

            # 2. Ricerca globale se primo token >= 4 caratteri
            if not matched_p and tokens and len(tokens[0]) >= 4:
                for p in players:
                    p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
                    p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
                    if tokens[0] in p_toks:
                        matched_p = p
                        break

        if matched_p:
            pid = matched_p['id']
            new_injured_ids.add(pid)
            sev, g_perse, status_str = calculate_injury_metrics(item['motivo'], item['rientro'])

            matched_p['is_injured'] = True
            matched_p['infortunio_motivo'] = item['motivo']
            matched_p['infortunio_rientro'] = item['rientro']
            matched_p['infortunio_gravita'] = sev
            matched_p['giornate_perse_stimate'] = g_perse
            matched_p['infortunio_status'] = status_str

            matched_log.append({
                'name': matched_p['name'],
                'team': matched_p['team'],
                'rientro': item['rientro'],
                'motivo': item['motivo'],
                'gravita': sev
            })

    # Calciatori guariti / non più in lista infortuni
    recovered_count = 0
    for p in players:
        if p['id'] not in new_injured_ids:
            if p.get('is_injured'):
                recovered_count += 1
                p['is_injured'] = False
                p['infortunio_motivo'] = None
                p['infortunio_rientro'] = None
                p['infortunio_status'] = "Disponibile"
                p['infortunio_gravita'] = "green"
                p['giornate_perse_stimate'] = 0

        # Ricalcola consiglio AI per tutti
        advice, adv_type = determine_advice_tag(p)
        p['ai_advice'] = advice
        p['ai_advice_type'] = adv_type

    # Salva entrambi i file master
    with open(PLAYERS_MASTER, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    with open(ROOT_MASTER, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    print(f"\n=======================================================")
    print(f"✓ Sincronizzazione Infortuni Completata con Successo!")
    print(f"-> Totale infortuni ufficiali registrati: {len(new_injured_ids)}")
    print(f"-> Calciatori guariti / tornati disponibili: {recovered_count}")
    print(f"=======================================================\n")

    return matched_log

if __name__ == '__main__':
    sync_injuries()
