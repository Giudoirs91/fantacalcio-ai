"""
tools/sync_injuries_fantacalcio_online.py
=========================================
Sincronizzazione Ufficiale Infortunati e Indisponibili Serie A da Fantacalcio-Online:
URL: https://www.fantacalcio-online.com/it/infortunati-serie-a

Estrae:
 - Tabella infortunati con Squadra, Calciatore, Motivo e Rientro previsto
 - Matching su processed_players_master.json
 - Calcolo gravità (red/orange) e giornate perse stimate
 - Aggiornamento data/processed/processed_players_master.json e processed_players_master.json
 - Aggiornamento config/injuries.json
 - Ricalcolo AI Advice
"""

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
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.valuation_engine import determine_advice_tag

URL = "https://www.fantacalcio-online.com/it/infortunati-serie-a"
LOCAL_BACKUP_HTML = os.path.join(ROOT_DIR, "data", "raw", "infortunati_fantacalcio_online.html")
PLAYERS_MASTER = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ROOT_MASTER = os.path.join(ROOT_DIR, "processed_players_master.json")
CONFIG_INJURIES = os.path.join(ROOT_DIR, "config", "injuries.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

SPECIAL_PLAYER_OVERRIDES = {
    ('Fiorentina', 'MANDRAGORA'): ('Mandragora', 'Torino'),
    ('Roma', 'KONE'): ('Konè M.', 'Roma'),
    ('Sassuolo', 'KONE'): ('Konè I.', 'Sassuolo'),
    ('Frosinone', 'KONE'): ('Kone B.', 'Frosinone'),
    ('Udinese', 'BAYO'): ('Bayo V.', 'Udinese'),
    ('Como', 'RODRIGUEZ'): ('Rodriguez Je.', 'Como'),
    ('Como', 'CHALOBAH'): ('Chalobah T.', 'Como'),
    ('Lecce', 'COULIBALY'): ('Coulibaly L.', 'Lecce'),
    ('Sassuolo', 'LEYSEN'): ('Leysen F.', 'Sassuolo'),
    ('Atalanta', 'KRISTENSEN'): ('Kristensen T.', 'Atalanta'),
    ('Juventus', 'THURAM'): ('Thuram K.', 'Juventus'),
    ('Juventus', 'GONZALEZ'): ('Gonzalez N.', 'Juventus'),
    ('Inter', 'MARTINEZ'): ('Martinez L.', 'Inter'),
}

def normalize_str(s):
    if not s:
        return ""
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

def load_calendar():
    calendar_dates = []
    if os.path.exists(CALENDAR_PATH):
        try:
            with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
                cal = json.load(f)
            for g in cal:
                g_num = g.get('giornata')
                d_str = g.get('date')
                if d_str:
                    try:
                        d_obj = datetime.strptime(d_str.strip(), "%d/%m/%Y")
                        calendar_dates.append((g_num, d_obj))
                    except Exception:
                        pass
        except Exception as e:
            print(f"[WARN] Impossibile caricare il calendario: {e}")
    calendar_dates.sort(key=lambda x: x[1])
    return calendar_dates

def fetch_html():
    content = None
    try:
        req = urllib.request.Request(URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                content = resp.read().decode('utf-8', errors='ignore')
                os.makedirs(os.path.dirname(LOCAL_BACKUP_HTML), exist_ok=True)
                with open(LOCAL_BACKUP_HTML, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Scaricata pagina online da {URL} ({len(content)} byte)")
    except Exception as e:
        print(f"[INFO] Connessione a {URL} fallita o timeout ({e}). Utilizzo backup locale.")
    
    if not content and os.path.exists(LOCAL_BACKUP_HTML):
        with open(LOCAL_BACKUP_HTML, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ Caricata pagina da backup locale ({len(content)} byte)")
    return content

def parse_injuries(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    if not table:
        raise ValueError("Nessuna tabella infortunati trovata in HTML.")

    rows = table.find_all('tr')
    extracted = []

    for r in rows[1:]:
        cols = [td.text.strip() for td in r.find_all('td')]
        if len(cols) >= 4:
            team = cols[0].strip()
            player = cols[1].strip()
            reason = cols[2].strip()
            ret_date = cols[3].strip()
            extracted.append({
                'team': team,
                'raw_player': player,
                'reason': reason,
                'return_date': ret_date
            })
    return extracted

def match_player_to_master(team_name, raw_name, players):
    parts = raw_name.split()
    surname = parts[0] if parts else ""
    double_surname = f"{parts[0]} {parts[1]}" if len(parts) > 2 and parts[1].isupper() else surname

    # 1. Overrides
    if (team_name, surname.upper()) in SPECIAL_PLAYER_OVERRIDES:
        t_name, t_team = SPECIAL_PLAYER_OVERRIDES[(team_name, surname.upper())]
        for p in players:
            if p['name'].lower() == t_name.lower() and p['team'].lower() == t_team.lower():
                return p

    norm_team = normalize_str(team_name)
    norm_player = normalize_str(raw_name)
    norm_surname = normalize_str(surname)
    norm_double = normalize_str(double_surname)

    team_candidates = [p for p in players if normalize_str(p.get('team') or '') == norm_team]

    # 2. Exact match in team
    for p in team_candidates:
        p_name = normalize_str(p.get('name') or '')
        if p_name == norm_surname or p_name == norm_double or p_name == norm_player:
            return p
        if p_name.startswith(norm_surname + " ") or p_name.startswith(norm_double + " "):
            return p

    # 3. Substring in team
    for p in team_candidates:
        p_name = normalize_str(p.get('name') or '')
        if norm_surname in p_name or p_name in norm_player:
            return p

    # 4. Global match fallback (e.g. transferred players)
    if len(norm_surname) >= 4:
        for p in players:
            p_name = normalize_str(p.get('name') or '')
            if p_name == norm_surname or p_name.startswith(norm_surname + " "):
                return p

    return None

def sync_fantacalcio_online_injuries():
    print("=== Sincronizzazione Infortunati da Fantacalcio-Online ===")
    html = fetch_html()
    if not html:
        print("[ERRORE] Impossibile recuperare i dati HTML.")
        return False

    raw_injuries = parse_injuries(html)
    print(f"Estratti {len(raw_injuries)} infortuni grezzi.")

    with open(PLAYERS_MASTER, 'r', encoding='utf-8') as f:
        players = json.load(f)

    calendar_dates = load_calendar()
    today = datetime.now()

    new_injured_ids = set()
    matched_injuries = []
    unmatched_injuries = []

    for item in raw_injuries:
        team = item['team']
        raw_player = item['raw_player']
        reason = item['reason']
        ret_date = item['return_date']

        p = match_player_to_master(team, raw_player, players)

        # Parse return date & calculate missed matchdays
        missed = 1
        is_grave = False
        try:
            r_dt = datetime.strptime(ret_date, "%d/%m/%Y")
            future_rounds = [rd for rd in calendar_dates if rd[1] >= today.replace(hour=0, minute=0)]
            missed = sum(1 for g, d in future_rounds if d <= r_dt)
            if missed == 0:
                missed = 1
        except Exception:
            pass

        r_lower = reason.lower()
        if any(kw in r_lower for kw in ['crociato', 'rottura', 'operat', 'frattura', 'menisco', 'lungo stop', '2027', 'dislocazione']):
            is_grave = True
            if missed < 4:
                missed = 4

        severity = 'red' if (missed >= 4 or is_grave) else 'orange'
        status_icon = "🔴" if severity == 'red' else "🟠"
        status_str = f"{status_icon} {reason} (Rientro: {ret_date})"
        fonte_str = "Fantacalcio-Online (Aggiornato 03/11/2026)"

        if p:
            pid = p['id']
            new_injured_ids.add(pid)
            p['is_injured'] = True
            p['infortunio_motivo'] = reason
            p['infortunio_rientro'] = ret_date
            p['infortunio_gravita'] = severity
            p['giornate_perse_stimate'] = missed
            p['infortunio_status'] = status_str

            matched_injuries.append({
                'player': p['name'],
                'player_id': pid,
                'team': p['team'],
                'motivo': reason,
                'rientro': ret_date,
                'severity': severity,
                'giornate_perse': missed,
                'tipo_stop': 'Infortunato',
                'fonte': fonte_str
            })
        else:
            unmatched_injuries.append({
                'player': raw_player,
                'player_id': None,
                'team': team,
                'motivo': reason,
                'rientro': ret_date,
                'severity': severity,
                'giornate_perse': missed,
                'tipo_stop': 'Infortunato',
                'fonte': fonte_str
            })

    # Calciatori precedentemente infortunati che ora sono guariti
    healed_count = 0
    for p in players:
        if p.get('is_injured') and p['id'] not in new_injured_ids:
            p['is_injured'] = False
            p['infortunio_motivo'] = None
            p['infortunio_rientro'] = None
            p['infortunio_status'] = "🟢 Disponibile"
            p['infortunio_gravita'] = "green"
            p['giornate_perse_stimate'] = 0
            healed_count += 1

        # Ricalcolo AI Advice
        advice, adv_type = determine_advice_tag(p)
        p['ai_advice'] = advice
        p['ai_advice_type'] = adv_type

    # Salva database master
    with open(PLAYERS_MASTER, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)
    with open(ROOT_MASTER, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    # Salva config/injuries.json
    all_injuries_list = matched_injuries + unmatched_injuries
    with open(CONFIG_INJURIES, 'w', encoding='utf-8') as f:
        json.dump(all_injuries_list, f, ensure_ascii=False, indent=2)

    print(f"✓ Sincronizzazione completata:")
    print(f"  - Infortunati attivi: {len(matched_injuries)} matchati (+ {len(unmatched_injuries)} non matchati)")
    print(f"  - Calciatori guariti / tornati disponibili: {healed_count}")
    print(f"  - Aggiornati: {PLAYERS_MASTER}, {ROOT_MASTER}, {CONFIG_INJURIES}")
    return True

if __name__ == '__main__':
    sync_fantacalcio_online_injuries()
