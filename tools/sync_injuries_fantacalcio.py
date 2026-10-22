"""
tools/sync_injuries_fantacalcio.py
==================================
Sincronizzazione Ufficiale Infortunati e Indisponibili Serie A da Fantacalcio.it:
URL: https://www.fantacalcio.it/indisponibili-serie-a

Estrae:
 - Infortunati con diagnosi clinica, stima rientro (DD/MM/YYYY) e gravità (red/orange)
 - Squalificati e Diffidati
 - Aggiorna data/processed/processed_players_master.json e processed_players_master.json
 - Aggiorna config/injuries.json
 - Ricalcola ai_advice per ogni calciatore
"""

import os
import sys
import re
import json
import unicodedata
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.valuation_engine import determine_advice_tag

URL = "https://www.fantacalcio.it/indisponibili-serie-a"
LOCAL_BACKUP_HTML = os.path.join(ROOT_DIR, "data", "raw", "infortunati_fantacalcio_it.html")
PLAYERS_MASTER = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ROOT_MASTER = os.path.join(ROOT_DIR, "processed_players_master.json")
CONFIG_INJURIES = os.path.join(ROOT_DIR, "config", "injuries.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

NAME_OVERRIDES = {
    ('Atalanta', 'Sulemana K.'): 'Sulemana K.',
    ('Sassuolo', 'Konè I.'): 'Konè I.',
    ('Sassuolo', 'Kone I.'): 'Konè I.',
    ('Roma', 'Konè M.'): 'Konè M.',
    ('Roma', 'Kone M.'): 'Konè M.',
    ('Roma', 'Pellegrini Lo.'): 'Pellegrini Lo.',
    ('Cagliari', 'Idrissi R.'): 'Idrissi R.',
    ('Juventus', 'Thuram K.'): 'Thuram K.',
    ('Inter', 'Jones C.'): 'Jones C.',
    ('Inter', 'Martinez L.'): 'Martinez L.',
    ('Como', 'Rodriguez Je.'): 'Rodriguez Je.',
    ('Como', 'Chalobah T.'): 'Chalobah T.',
    ('Lecce', 'Coulibaly L.'): 'Coulibaly L.',
    ('Lecce', 'Berisha M.'): 'Berisha M.',
    ('Napoli', 'Santos A.'): 'Santos A.',
    ('Sassuolo', 'Leysen F.'): 'Leysen F.',
    ('Torino', 'Rodriguez R.'): 'Rodriguez R.',
    ('Udinese', 'Bayo V.'): 'Bayo V.',
    ('Venezia', 'Correia T.'): 'Correia T.',
    ('Lazio', 'Gudmundsson A.'): 'Gudmundsson A.'
}

def load_calendar_dates():
    if os.path.exists(CALENDAR_PATH):
        try:
            with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
                cal = json.load(f)
            dates = []
            for r in cal:
                d_str = r.get('date')
                if d_str:
                    try:
                        dates.append((r['giornata'], datetime.strptime(d_str, "%d/%m/%Y")))
                    except Exception:
                        pass
            dates.sort(key=lambda x: x[0])
            return dates
        except Exception:
            pass
    return []

CALENDAR_DATES = load_calendar_dates()

def fetch_html():
    print(f"-> [InjuriesSync] Download live da {URL}...")
    try:
        res = subprocess.run(
            ['curl.exe', '-s', '-L', '-A', HEADERS['User-Agent'], URL],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=15
        )
        if res.returncode == 0 and len(res.stdout) > 2000:
            os.makedirs(os.path.dirname(LOCAL_BACKUP_HTML), exist_ok=True)
            with open(LOCAL_BACKUP_HTML, 'w', encoding='utf-8') as f:
                f.write(res.stdout)
            print(f"-> [InjuriesSync] Download completato ({len(res.stdout)} bytes).")
            return res.stdout
    except Exception as e:
        print(f"-> [InjuriesSync] Avviso: curl live fallito ({e}). Tento backup locale...")

    if os.path.exists(LOCAL_BACKUP_HTML):
        with open(LOCAL_BACKUP_HTML, 'r', encoding='utf-8', errors='ignore') as f:
            print("-> [InjuriesSync] Caricato da backup locale.")
            return f.read()

    raise RuntimeError("Impossibile scaricare o reperire la pagina indisponibili di Fantacalcio.it.")

def clean_motivo(desc):
    d = desc.replace('&agrave;', 'à').replace('&egrave;', 'è').replace('&igrave;', 'ì').replace('&ograve;', 'ò').replace('&ugrave;', 'ù').replace('&nbsp;', ' ')
    d = re.sub(r'\s+', ' ', d).strip()
    
    medical_patterns = [
        r'(rottura del legamento crociato(?: anteriore)?)',
        r'(lesione al crociato(?: anteriore)?)',
        r'(lesione del legamento crociato(?: anteriore)?)',
        r'(infortunio al legamento crociato(?: al ginocchio)?)',
        r'(rottura di tibia e perone)',
        r'(rottura del menisco(?: esterno| interno)?)',
        r'(lussazione della rotula(?: del ginocchio)?)',
        r'(lussazione alla spalla(?: sinistra| destra)?)',
        r'(frattura della falange della mano(?: destra| sinistra)?)',
        r'(frattura a un dito del piede)',
        r'(frattura della base del V metatarso[^\,\.]+)',
        r'(fascite plantare)',
        r'(appendicite acuta[^\,\.]*)',
        r'(lesione distrattiva di medio grado[^\,\.]+)',
        r'(lesione di alto grado[^\,\.]+)',
        r'(lesione di medio-alto grado[^\,\.]+)',
        r'(lesione di medio grado[^\,\.]+)',
        r'(lesione di primo grado[^\,\.]+)',
        r'(lesione di basso grado[^\,\.]+)',
        r'(lesione di grado moderato[^\,\.]+)',
        r'(lesione muscolare di secondo grado[^\,\.]+)',
        r'(lesione muscolare di medio grado[^\,\.]+)',
        r'(lesione muscolare di primo grado[^\,\.]+)',
        r'(lesione muscolare di basso grado[^\,\.]+)',
        r'(lesione muscolare al[^\,\.]+)',
        r'(lesione del flessore[^\,\.]+)',
        r'(lesione del tendine[^\,\.]+)',
        r'(lesione tendinea di basso grado[^\,\.]+)',
        r'(distrazione muscolare di basso grado[^\,\.]+)',
        r'(distrazione muscolare al[^\,\.]+)',
        r'(distrazione di basso grado[^\,\.]+)',
        r'(distrazione intratendinea[^\,\.]+)',
        r'(distrazione della muscolatura[^\,\.]+)',
        r'(risentimento miofasciale[^\,\.]+)',
        r'(risentimento muscolare ai flessori[^\,\.]+)',
        r'(risentimento muscolare al[^\,\.]+)',
        r'(risentimento agli adduttori[^\,\.]+)',
        r'(sindrome retto-adduttoria)',
        r'(sindrome femoro-rotulea[^\,\.]*)',
        r'(sovraccarico funzionale dell\'addome)',
        r'(sovraccarico muscolare alla gamba)',
        r'(affaticamento muscolare all\'adduttore)',
        r'(fastidio muscolare alla gamba)',
        r'(guaio muscolare al[^\,\.]+)',
        r'(guaio muscolare alla gamba)',
        r'(problema alla caviglia destra e operata)',
        r'(problema alla caviglia)',
        r'(problema alla spalla destra)',
        r'(problema al tendine della coscia destra)',
        r'(problema al ginocchio)',
        r'(problema all\'anca sinistra)',
        r'(problema alla schiena)',
        r'(problema al piede)',
        r'(operato al tendine rotuleo)',
        r'(operato al menisco del ginocchio destro)',
        r'(guaio alla spalla che ha richiesto l\'intervento chirurgico)'
    ]
    
    for p in medical_patterns:
        m = re.search(p, d, re.IGNORECASE)
        if m:
            res = m.group(1).strip()
            return res[:1].upper() + res[1:]
            
    # Heuristic: cerca dopo 'vittima di', 'a causa di', 'frenato da', 'per'
    patterns_gen = [
        r'(?:vittima di|a causa di|per una|per un|operato per|operato di|frenato da|alle prese con)\s+([^,\.]+)',
        r'(?:rimediato|evidenziato|lamentato)\s+([^,\.]+)'
    ]
    for p in patterns_gen:
        m = re.search(p, d, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            cand = re.sub(r'^(una|un|il|la|lo|dalla|dall\'|dei|degli|del)\s+', '', cand, flags=re.IGNORECASE)
            if len(cand) > 6 and not any(bad in cand.lower() for bad in ['cambio', 'gara', 'partita', 'nazionale']):
                return cand[:1].upper() + cand[1:]

    # Fallback su prima frase
    cand = d.split('.')[0]
    cand = re.sub(r'^(il|l\'|la|lo)\s+\w+\s+(KO|out|fermo|costretto|ai box|operato|assente|non convocato)\s+(a|in|per|da)?\s*', '', cand, flags=re.IGNORECASE)
    cand = cand.strip()
    return cand[:1].upper() + cand[1:]

def parse_injury_metrics(desc, ref_date=None):
    if ref_date is None:
        ref_date = datetime(2026, 10, 22)

    d_clean = desc.replace('&agrave;', 'à').replace('&egrave;', 'è').replace('&igrave;', 'ì').replace('&ograve;', 'ò').replace('&ugrave;', 'ù').replace('&nbsp;', ' ')
    d_clean = re.sub(r'\s+', ' ', d_clean).strip()
    d_lower = d_clean.lower()

    # Stima data rientro
    rientro_date = '25/10/2026'

    if any(k in d_lower for k in ['da aprile', 'fine aprile', 'nel mese di aprile']):
        rientro_date = '18/04/2027'
    elif any(k in d_lower for k in ['da marzo', 'fine marzo', 'nel mese di marzo', 'marzo']):
        rientro_date = '14/03/2027'
    elif any(k in d_lower for k in ['fine febbraio', 'da febbraio', 'febbraio inoltrato', 'febbraio']):
        rientro_date = '28/02/2027'
    elif any(k in d_lower for k in ['fine gennaio', 'da gennaio', 'metà gennaio', 'gennaio']):
        rientro_date = '31/01/2027'
    elif any(k in d_lower for k in ['fine di dicembre', 'fine dicembre', 'da fine dicembre']):
        rientro_date = '20/12/2026'
    elif any(k in d_lower for k in ['metà di dicembre', 'metà dicembre']):
        rientro_date = '13/12/2026'
    elif any(k in d_lower for k in ['inizio dicembre', 'inizio di dicembre', 'da dicembre', 'dicembre']):
        rientro_date = '06/12/2026'
    elif any(k in d_lower for k in ['seconda metà di novembre', 'dalla metà di novembre', 'metà di novembre', 'metà novembre', 'da metà novembre']):
        rientro_date = '22/11/2026'
    elif any(k in d_lower for k in ['prima metà di novembre', 'inizio di novembre', 'inizio novembre', 'da inizio novembre', 'a inizio novembre']):
        rientro_date = '08/11/2026'
    elif any(k in d_lower for k in ['fine di ottobre', 'fine ottobre', 'da fine ottobre']):
        rientro_date = '29/10/2026'
    elif any(k in d_lower for k in ['seconda metà di ottobre', 'metà ottobre']):
        rientro_date = '25/10/2026'
    elif any(k in d_lower for k in ['8a giornata', '8ª giornata', 'venerdì', 'sabato', 'domenica', 'prossimo turno']):
        if any(neg in d_lower for neg in ['out', 'non ci sarà', 'assente', 'non sarà a disposizione', 'forfait', 'non convocato']):
            rientro_date = '29/10/2026'
        else:
            rientro_date = '25/10/2026'
    elif any(k in d_lower for k in ['tempi da valutare', 'da monitorare', 'da stabilire', 'condizioni da valutare']):
        rientro_date = '01/11/2026'

    is_grave = any(kw in d_lower for kw in [
        'crociato', 'tendine d\'achille', 'rottura', 'operat', 'lussazione rotula',
        'frattura', 'alto grado', 'lungo stop', '2027', 'marzo', 'aprile', 'febbraio'
    ])

    r_dt = datetime.strptime(rientro_date, '%d/%m/%Y')
    future_rounds = [rd for rd in CALENDAR_DATES if rd[1] >= ref_date.replace(hour=0, minute=0)]
    missed = sum(1 for g, d in future_rounds if d <= r_dt)
    if missed == 0:
        missed = 1
    if is_grave and missed < 5:
        missed = 5

    severity = 'red' if (missed >= 4 or is_grave) else 'orange'
    giornate_perse = missed

    motivo = clean_motivo(d_clean)
    status_icon = "🔴" if severity == 'red' else "🟠"
    status_str = f"{status_icon} {motivo} (Rientro: {rientro_date})"

    return motivo, rientro_date, severity, giornate_perse, status_str

def parse_fantacalcio_indisponibili(html):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', class_='team-card')
    if not cards:
        raise ValueError("Nessuna team-card trovata nella pagina di Fantacalcio.it.")

    extracted_injuries = []
    disciplinary = []

    for card in cards:
        team_name_el = card.find('span', class_='team-name')
        team_name = team_name_el.get_text(strip=True) if team_name_el else 'Unknown'
        
        cols = card.find_all('div', class_='col')
        for col in cols:
            for h in col.find_all('header'):
                h_text = h.get_text(strip=True)
                
                # Infortunati
                if 'Infortunati' in h_text:
                    nxt = h.find_next_sibling()
                    if nxt and nxt.name == 'ul':
                        for li in nxt.find_all('li', recursive=False):
                            name_el = li.find('strong', class_='item-name')
                            desc_el = li.find('div', class_='item-description')
                            pname = name_el.get_text(strip=True) if name_el else ''
                            desc = desc_el.get_text(' ', strip=True) if desc_el else ''
                            if pname:
                                extracted_injuries.append({
                                    'team': team_name,
                                    'raw_name': pname,
                                    'desc': desc
                                })

                # Squalificati / Diffidati
                elif 'Squalificati' in h_text or 'Diffidati' in h_text:
                    is_squal = 'Squalificati' in h_text
                    nxt = h.find_next_sibling()
                    if nxt and nxt.name == 'ul':
                        for li in nxt.find_all('li', recursive=False):
                            pname = li.get_text(' ', strip=True)
                            if pname:
                                disciplinary.append({
                                    'team': team_name,
                                    'raw_name': pname,
                                    'type': 'Squalificato' if is_squal else 'Diffidato'
                                })

    print(f"-> [InjuriesSync] Estratti {len(extracted_injuries)} infortunati e {len(disciplinary)} disciplinari (squalificati/diffidati).")
    return extracted_injuries, disciplinary

def sync_injuries():
    print("=" * 65)
    print("⚡ [FantaMasterAI] Avvio Sincronizzazione Infortuni Fantacalcio.it")
    print(f"   Data esecuzione: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 65)

    html = fetch_html()
    extracted_injuries, disciplinary = parse_fantacalcio_indisponibili(html)

    with open(PLAYERS_MASTER, 'r', encoding='utf-8') as f:
        players = json.load(f)

    previously_injured = {p['id']: p for p in players if p.get('is_injured')}
    print(f"-> Calciatori precedentemente infortunati nel master: {len(previously_injured)}")

    new_injured_ids = set()
    matched_log = []
    unmatched_log = []

    for item in extracted_injuries:
        team_orig = item['team']
        team_l = team_orig.lower().strip()
        raw_name = item['raw_name'].strip()
        desc = item['desc']

        motivo, rientro_str, sev, g_perse, status_str = parse_injury_metrics(desc)

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

            # 2. Ricerca globale
            if not matched_p and tokens and len(tokens[0]) >= 4:
                for p in players:
                    p_clean = unicodedata.normalize('NFKD', p['name']).encode('ASCII', 'ignore').decode('utf-8')
                    p_toks = [t.lower() for t in re.split(r'[\s\.\-]+', p_clean) if len(t) >= 2]
                    if tokens[0] in p_toks:
                        matched_p = p
                        break

        fonte_str = "Fantacalcio.it (Aggiornato 22/10/2026)"

        if matched_p:
            pid = matched_p['id']
            new_injured_ids.add(pid)

            matched_p['is_injured'] = True
            matched_p['infortunio_motivo'] = motivo
            matched_p['infortunio_rientro'] = rientro_str
            matched_p['infortunio_gravita'] = sev
            matched_p['giornate_perse_stimate'] = g_perse
            matched_p['infortunio_status'] = status_str

            matched_log.append({
                'id': pid,
                'name': matched_p['name'],
                'team': matched_p['team'],
                'rientro': rientro_str,
                'motivo': motivo,
                'gravita': sev,
                'giornate_perse': g_perse,
                'status_str': status_str,
                'fonte': fonte_str
            })
        else:
            unmatched_log.append({
                'id': None,
                'name': raw_name,
                'team': team_orig,
                'rientro': rientro_str,
                'motivo': motivo,
                'gravita': sev,
                'giornate_perse': g_perse,
                'status_str': status_str,
                'fonte': fonte_str
            })

    # Calciatori guariti
    recovered_players = []
    for p in players:
        if p['id'] not in new_injured_ids:
            if p.get('is_injured'):
                p['is_injured'] = False
                p['infortunio_motivo'] = None
                p['infortunio_rientro'] = None
                p['infortunio_status'] = "🟢 Disponibile"
                p['infortunio_gravita'] = "green"
                p['giornate_perse_stimate'] = 0
                recovered_players.append(p)

        # Ricalcolo AI Advice
        advice, adv_type = determine_advice_tag(p)
        p['ai_advice'] = advice
        p['ai_advice_type'] = adv_type

    # Salva entrambi i file master
    with open(PLAYERS_MASTER, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    with open(ROOT_MASTER, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    # Salva config/injuries.json
    config_injuries = []
    for item in matched_log + unmatched_log:
        config_injuries.append({
            "player": item['name'],
            "player_id": item['id'],
            "team": item['team'],
            "motivo": item['motivo'],
            "rientro": item['rientro'],
            "severity": item['gravita'],
            "tipo_stop": "Infortunato",
            "fonte": item['fonte']
        })

    with open(CONFIG_INJURIES, 'w', encoding='utf-8') as f:
        json.dump(config_injuries, f, ensure_ascii=False, indent=2)

    print(f"\n=======================================================")
    print(f"✓ Sincronizzazione Infortuni Fantacalcio.it Completata!")
    print(f"-> Totale infortuni ufficiali registrati: {len(config_injuries)}")
    print(f"-> Calciatori master associati: {len(matched_log)} (Non associati: {len(unmatched_log)})")
    print(f"-> Calciatori guariti tornati disponibili: {len(recovered_players)}")
    for rec in recovered_players:
        print(f"   🟢 {rec['name']} ({rec['team']}) è tornato disponibile!")
    print(f"=======================================================\n")

    return matched_log, unmatched_log, recovered_players, disciplinary

if __name__ == '__main__':
    sync_injuries()
