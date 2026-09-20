import os
import sys
import re
import time
import json
import unicodedata
import urllib.request
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_SQUADS_DIR = os.path.join(ROOT_DIR, "data", "raw", "tm_squads")
CACHE_INJURIES_DIR = os.path.join(ROOT_DIR, "data", "raw", "tm_injuries")
MASTER_PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ALIASES_PATH = os.path.join(ROOT_DIR, "config", "player_aliases.json")
INJURIES_HISTORY_PATH = os.path.join(ROOT_DIR, "config", "injuries_history.json")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

SERIE_A_TEAMS = {
    "Atalanta": 800,
    "Bologna": 1025,
    "Cagliari": 1390,
    "Como": 1047,
    "Fiorentina": 430,
    "Frosinone": 8970,
    "Genoa": 252,
    "Inter": 46,
    "Juventus": 506,
    "Lazio": 398,
    "Lecce": 1005,
    "Milan": 5,
    "Monza": 2919,
    "Napoli": 6195,
    "Parma": 130,
    "Roma": 12,
    "Sassuolo": 6574,
    "Torino": 416,
    "Udinese": 410,
    "Venezia": 607
}

def normalize_str(s):
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s.lower())
    return " ".join(s.split())

def load_aliases():
    if os.path.exists(ALIASES_PATH):
        try:
            with open(ALIASES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def classify_injury_type(motivo):
    m = (motivo or '').lower()
    if any(k in m for k in ['crociato', 'collaterale', 'menisco', 'legamento', 'caviglia', 'ginocchio', 'spalla', 'tendine', 'distorsione', 'anca']):
        return 'articolare'
    if any(k in m for k in ['bicipite', 'femorale', 'flessori', 'coscia', 'polpaccio', 'adduttore', 'stiramento', 'lesione', 'strappo', 'risentimento', 'muscol']):
        return 'muscolare'
    if any(k in m for k in ['frattura', 'trauma', 'scontro', 'lussazione', 'contusione', 'ematoma', 'facciale', 'zigomo']):
        return 'traumatico'
    if any(k in m for k in ['operat', 'intervento', 'chirurg', 'appendicite']):
        return 'chirurgico'
    return 'medico'

def calculate_fragility_index(partite_recenti, recidive, active_injury, has_cruciate):
    score = 5.0 # Base
    score += min(45.0, partite_recenti * 4.0)
    score += min(25.0, recidive * 12.0)
    if active_injury:
        score += 15.0
    if has_cruciate:
        score += 20.0
    
    score = min(100.0, max(0.0, score))
    
    if score <= 18:
        tier = 'ROCCIA'
        label = '🟢 Roccia (Massima Affidabilità)'
        badge = 'roccia'
    elif score <= 38:
        tier = 'STABILE'
        label = '🟢 Stabile (Fisiologico)'
        badge = 'stabile'
    elif score <= 62:
        tier = 'ATTENZIONE'
        label = '🟡 Attenzione (Soggetto a Stop)'
        badge = 'attenzione'
    elif score <= 82:
        tier = 'FRAGILE'
        label = '🔴 Fragile (Rischio Elevato)'
        badge = 'fragile'
    else:
        tier = 'CRISTALLO'
        label = '🚨 Cristallo (Altissimo Rischio)'
        badge = 'cristallo'
        
    return round(score, 1), tier, label, badge

def generate_medical_advice(tier, partite_tot, active_inj, recidive):
    if active_inj:
        return "Attualmente ai box per infortunio. Valutare con cautela la data stimata di rientro prima di acquistarlo all'asta."
    if tier == 'ROCCIA':
        return "Calciatore integro e solido. Storico infortuni pressocché nullo nelle ultime stagioni: affidabilità fisica massima."
    if tier == 'STABILE':
        return f"Tenuta atletica buona ({partite_tot} gare saltate negli ultimi 24 mesi). Gestibile senza particolari rischi o coppie obbligate."
    if tier == 'ATTENZIONE':
        rec_txt = f" con {recidive} stop muscolari" if recidive > 0 else ""
        return f"Attenzione: ha registrato {partite_tot} gare saltate{rec_txt}. Consigliata copertura economica in panchina."
    if tier == 'FRAGILE':
        rec_txt = f" e {recidive} ricadute muscolari" if recidive > 0 else ""
        return f"Profilo a rischio elevato ({partite_tot} partite saltate{rec_txt}). Fondamentale acquistare la sua riserva/coppia d'asta."
    return "Altissimo rischio infortuni o lungo degenza recente. Prezzo d'asta da svalutare fortemente e obbligo assoluto di copertura."

def fetch_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def get_team_squad_tm(team_name, tm_id):
    os.makedirs(CACHE_SQUADS_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_SQUADS_DIR, f"squad_{tm_id}.html")
    
    html = ""
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        url = f"https://www.transfermarkt.it/club/kader/verein/{tm_id}/saison_id/2026"
        print(f"  [Scrape] Squadra {team_name} da TM: {url}")
        try:
            html = fetch_url(url)
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(html)
            time.sleep(0.8)
        except Exception as e:
            print(f"  [Errore] Impossibile scaricare rosa {team_name}: {e}")
            return []
            
    soup = BeautifulSoup(html, 'html.parser')
    players = []
    seen_ids = set()
    for a in soup.find_all('a', href=re.compile(r'/profil/spieler/\d+')):
        href = a['href']
        name = a.get_text(strip=True)
        m = re.search(r'/spieler/(\d+)', href)
        if m:
            pid = m.group(1)
            if pid not in seen_ids and name:
                seen_ids.add(pid)
                slug_m = re.match(r'/([^/]+)/profil/spieler/', href)
                slug = slug_m.group(1) if slug_m else "profilo"
                players.append({
                    "tm_id": pid,
                    "tm_name": name,
                    "slug": slug,
                    "href": href
                })
    return players

def fetch_player_injuries(tm_id, tm_name, slug="profilo"):
    os.makedirs(CACHE_INJURIES_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_INJURIES_DIR, f"{tm_id}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
            
    url = f"https://www.transfermarkt.it/{slug}/verletzungen/spieler/{tm_id}"
    try:
        html = fetch_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='items')
        records = []
        if table and table.find('tbody'):
            for tr in table.find('tbody').find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) < 6:
                    continue
                stagione = tds[0].get_text(strip=True)
                motivo = tds[1].get_text(strip=True)
                da = tds[2].get_text(strip=True)
                fino_al = tds[3].get_text(strip=True)
                
                giorni_str = tds[4].get_text(strip=True)
                giorni_m = re.search(r'(\d+)', giorni_str)
                giorni = int(giorni_m.group(1)) if giorni_m else 0
                
                perse_str = tds[5].get_text(strip=True)
                perse_m = re.search(r'(\d+)', perse_str)
                partite_perse = int(perse_m.group(1)) if perse_m else 0
                
                is_active = ('bg_rot_20' in tds[0].get('class', []) or fino_al == '') and (stagione in ['26/27', '2026/27'])
                tipo = classify_injury_type(motivo)
                
                records.append({
                    'stagione': stagione,
                    'motivo': motivo,
                    'diagnosi': motivo,
                    'data_inizio': da,
                    'data_fine': fino_al if fino_al else 'In corso',
                    'giorni_stop': giorni,
                    'giorni': giorni,
                    'partite_perse': partite_perse,
                    'tipo': tipo,
                    'in_corso': is_active
                })
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        time.sleep(0.8)
        return records
    except Exception as e:
        print(f"    [Errore] Impossibile recuperare infortuni per {tm_name} ({tm_id}): {e}")
        return []

def match_fanta_to_tm(fanta_player, tm_squad, aliases, used_tm_ids=None):
    if used_tm_ids is None:
        used_tm_ids = set()
        
    f_name = fanta_player.get('name', '')
    f_norm = normalize_str(f_name)
    available_squad = [p for p in tm_squad if p['tm_id'] not in used_tm_ids]
    
    # 1. Alias check
    if f_norm in aliases:
        alias_target = normalize_str(aliases[f_norm])
        for tm_p in available_squad:
            if alias_target == normalize_str(tm_p['tm_name']) or alias_target in normalize_str(tm_p['tm_name']):
                return tm_p
                
    # 2. Exact match
    for tm_p in available_squad:
        tm_norm = normalize_str(tm_p['tm_name'])
        if f_norm == tm_norm:
            return tm_p
            
    # 3. Last name token match (e.g. "Maldini" -> "Daniel Maldini", "Felici" -> "Mattia Felici")
    f_tokens = f_norm.split()
    for tm_p in available_squad:
        tm_norm = normalize_str(tm_p['tm_name'])
        tm_tokens = tm_norm.split()
        if len(f_tokens) == 1:
            if f_tokens[0] in tm_tokens:
                return tm_p
        else:
            # Compound exact substring e.g. "Kevin Carlos" in "Kevin Carlos"
            if f_norm in tm_norm:
                return tm_p
            # Surname + Initial e.g. "Konè M." -> surname "kone" in tm_tokens AND initial 'm' matches first name
            surname = f_tokens[0]
            initials = f_tokens[1:]
            if surname in tm_tokens:
                # If there's an initial like 'm', check if any TM token starts with 'm'
                if all(any(t.startswith(init) for t in tm_tokens if t != surname) for init in initials):
                    return tm_p

    # 4. Longest token match (must be exact token, at least 4 chars)
    if f_tokens:
        main_token = max(f_tokens, key=len)
        if len(main_token) >= 4:
            for tm_p in available_squad:
                tm_tokens = normalize_str(tm_p['tm_name']).split()
                if main_token in tm_tokens:
                    return tm_p
                    
    return None

def process_team(team_name, tm_id, fanta_players, aliases, hist_db):
    print(f"\n==========================================")
    print(f" Elaborazione {team_name} (TM ID: {tm_id})")
    print(f"==========================================")
    
    tm_squad = get_team_squad_tm(team_name, tm_id)
    print(f"  Calciatori rosa TM trovati: {len(tm_squad)}")
    
    if team_name not in hist_db:
        hist_db[team_name] = {}
        
    team_fanta = [p for p in fanta_players if p.get('team') == team_name]
    print(f"  Calciatori Listone Fantacalcio: {len(team_fanta)}")
    
    matched_count = 0
    used_tm_ids = set()
    for p in team_fanta:
        p_name = p.get('name')
        p_id = p.get('id')
        p_role = p.get('role', 'C')
        
        tm_match = match_fanta_to_tm(p, tm_squad, aliases, used_tm_ids)
        if tm_match:
            matched_count += 1
            tm_pid = tm_match['tm_id']
            used_tm_ids.add(tm_pid)
            tm_pname = tm_match['tm_name']
            slug = tm_match['slug']
            
            injuries = fetch_player_injuries(tm_pid, tm_pname, slug)
            
            has_cruciate = any('crociato' in (inj.get('motivo') or '').lower() for inj in injuries)
            active_injury = any(inj.get('in_corso') for inj in injuries)
            
            recent_injuries = [inj for inj in injuries if inj.get('stagione') in ['26/27', '2026/27', '25/26', '2025/26', '24/25', '2024/25']]
            
            tot_partite_saltate = sum(inj.get('partite_perse', 0) for inj in recent_injuries)
            tot_giorni_stop = sum(inj.get('giorni_stop', 0) for inj in recent_injuries)
            
            muscle_count = sum(1 for inj in recent_injuries if inj.get('tipo') == 'muscolare')
            recidive = max(0, muscle_count - 1)
            
            score, tier, label, badge = calculate_fragility_index(
                tot_partite_saltate, recidive, active_injury, has_cruciate
            )
            
            disponibilita = max(10, min(100, round(((38 * 2 - tot_partite_saltate) / (38.0 * 2)) * 100, 1)))
            advice = generate_medical_advice(tier, tot_partite_saltate, active_injury, recidive)
            
            hist_db[team_name][p_name] = {
                'id': p_id,
                'tm_id': tm_pid,
                'tm_name': tm_pname,
                'name': p_name,
                'team': team_name,
                'ruolo': p_role,
                'partite_saltate_totali': tot_partite_saltate,
                'giorni_stop_totali': tot_giorni_stop,
                'disponibilita_pct': disponibilita,
                'recidive_muscolari': recidive,
                'indice_fragilita_score': score,
                'livello_fragilita': tier,
                'fragility_label': label,
                'fragility_badge': badge,
                'consiglio_medico_ai': advice,
                'infortunio_attivo': active_injury,
                'cronistoria_infortuni': injuries
            }
            
            active_badge = " [🔴 INFORTUNATO]" if active_injury else ""
            print(f"    ✓ {p_name:18} -> TM: {tm_pname:22} ({len(injuries)} stop, {tot_partite_saltate} partite, {tier}){active_badge}", flush=True)
        else:
            print(f"    ✗ {p_name:18} -> NON TROVATO IN ROSA TM", flush=True)
            
    print(f"  -> Match completati: {matched_count}/{len(team_fanta)} ({round(matched_count/max(1, len(team_fanta))*100, 1)}%)", flush=True)
    
    # Salva progressivamente ad ogni squadra completata
    with open(INJURIES_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(hist_db, f, ensure_ascii=False, indent=2)

def main():
    import argparse
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
    parser = argparse.ArgumentParser(description="Scrape accurate injury history from Transfermarkt")
    parser.add_argument("--team", type=str, help="Single team name to scrape (e.g. Cagliari, Roma)")
    parser.add_argument("--all", action="store_true", help="Scrape all 20 Serie A teams")
    args = parser.parse_args()
    
    if not os.path.exists(MASTER_PLAYERS_PATH):
        print(f"Errore: {MASTER_PLAYERS_PATH} non trovato.", flush=True)
        return
        
    with open(MASTER_PLAYERS_PATH, 'r', encoding='utf-8') as f:
        fanta_players = json.load(f)
        
    aliases = load_aliases()
    
    hist_db = {}
    if os.path.exists(INJURIES_HISTORY_PATH):
        try:
            with open(INJURIES_HISTORY_PATH, 'r', encoding='utf-8') as f:
                hist_db = json.load(f)
        except Exception:
            pass
            
    if args.team:
        team_name = args.team.capitalize()
        if team_name not in SERIE_A_TEAMS:
            print(f"Squadra '{team_name}' non valida. Scegli tra: {list(SERIE_A_TEAMS.keys())}", flush=True)
            return
        process_team(team_name, SERIE_A_TEAMS[team_name], fanta_players, aliases, hist_db)
    elif args.all:
        for t_name, t_id in SERIE_A_TEAMS.items():
            process_team(t_name, t_id, fanta_players, aliases, hist_db)
    else:
        print("Nessun argomento specificato. Esecuzione pilota su Cagliari:", flush=True)
        process_team("Cagliari", SERIE_A_TEAMS["Cagliari"], fanta_players, aliases, hist_db)
        
    with open(INJURIES_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(hist_db, f, ensure_ascii=False, indent=2)
    print(f"\n-> Database infortuni aggiornato salvato in: {INJURIES_HISTORY_PATH}", flush=True)

if __name__ == '__main__':
    main()
