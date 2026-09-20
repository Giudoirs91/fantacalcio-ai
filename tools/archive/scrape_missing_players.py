import csv
import json
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.manage_injuries_database import parse_transfermarkt_html, norm

CSV_INPUT = os.path.join(ROOT_DIR, "data", "raw", "giocatori_non_matchati.csv")
CSV_OUTPUT = os.path.join(ROOT_DIR, "data", "raw", "giocatori_ancora_non_matchati.csv")
DB_PATH = os.path.join(ROOT_DIR, "config", "infortuni_storici_2025_26.json")

def search_player(name):
    query = urllib.parse.quote(name)
    url = f"https://www.transfermarkt.it/schnellsuche/ergebnis/schnellsuche?query={query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', class_='items')
            if not table:
                return None
            first_row = table.find('tbody').find('tr')
            if not first_row:
                return None
            link_tag = first_row.find('td', class_='hauptlink')
            if link_tag and link_tag.find('a'):
                href = link_tag.find('a')['href']
                tm_name = link_tag.find('a').get('title', name)
                if '/profil/' in href:
                    inj_url = 'https://www.transfermarkt.it' + href.replace('/profil/', '/verletzungen/')
                    return inj_url, tm_name
    except Exception as e:
        print(f"Errore ricerca {name}: {e}")
    return None

def fetch_injuries(inj_url):
    req = urllib.request.Request(inj_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            infortuni = []
            table_div = soup.find('div', class_='responsive-table')
            if table_div:
                table = table_div.find('table')
                if table and table.find('tbody'):
                    for row in table.find('tbody').find_all('tr'):
                        cols = row.find_all('td')
                        if len(cols) >= 6:
                            stagione = cols[0].get_text(strip=True)
                            if stagione == '25/26':
                                infortuni.append({
                                    "motivo": cols[1].get_text(strip=True),
                                    "dal": cols[2].get_text(strip=True),
                                    "al": cols[3].get_text(strip=True),
                                    "giorni": cols[4].get_text(strip=True),
                                    "partite": cols[5].get_text(strip=True) or "0"
                                })
            return infortuni
    except Exception as e:
        print(f"Errore recupero infortuni {inj_url}: {e}")
    return None

def update_db(db, listone_team, listone_name, tm_name, tm_team, infortuni):
    if listone_team not in db:
        db[listone_team] = {}
    if listone_name not in db[listone_team]:
        print(f"WARNING: {listone_name} non trovato in db[{listone_team}].")
        return False
        
    p = db[listone_team][listone_name]
    p['tm_matched_name'] = tm_name
    p['squadra_tm_2526'] = tm_team
    p['diagnosi'] = []
    partite_tot = 0
    
    for inf in infortuni:
        try:
            pt = int(inf['partite'].replace('-', '0'))
        except:
            pt = 0
        if pt > 0:
            p['diagnosi'].append({
                "motivo": inf['motivo'],
                "partite": pt,
                "giornate": []
            })
            partite_tot += pt

    p['partite_saltate'] = partite_tot
    p['giornate_saltate'] = []
    
    if p['partite_saltate'] == 0:
        p['livello_fragilita'] = "🟢 Bassa"
    elif p['partite_saltate'] <= 6:
        p['livello_fragilita'] = "🟡 Media"
    else:
        p['livello_fragilita'] = "🔴 Alta"
        
    return True

def run():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    unmatched = []
    with open(CSV_INPUT, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            unmatched.append(row)
            
    print(f"Trovati {len(unmatched)} giocatori da cercare.")
    
    ancora_non_matchati = []
    
    for i, row in enumerate(unmatched):
        team = row['Squadra Listone']
        name = row['Nome Listone']
        
        # Prova a prendere dal file se l'utente l'ha compilato
        user_tm_name = row.get('Nome Transfermarkt', '').strip()
        user_tm_team = row.get('Squadra Transfermarkt (25/26)', '').strip()
        
        search_term = user_tm_name if user_tm_name else name
        
        print(f"[{i+1}/{len(unmatched)}] Cerco {search_term} ({team})...")
        res = search_player(search_term)
        if not res:
            print(f"  -> NESSUN RISULTATO TROVATO!")
            ancora_non_matchati.append(row)
            time.sleep(1)
            continue
            
        inj_url, tm_name = res
        print(f"  -> Trovato: {tm_name} | {inj_url}")
        infortuni = fetch_injuries(inj_url)
        if infortuni is None:
            print(f"  -> ERRORE recupero pagina infortuni.")
            ancora_non_matchati.append(row)
            time.sleep(1)
            continue
            
        tm_team = user_tm_team if user_tm_team else team
        success = update_db(db, team, name, tm_name, tm_team, infortuni)
        if success:
            print(f"  -> Matchato e aggiornato!")
        else:
            ancora_non_matchati.append(row)
            
        time.sleep(1) # delay

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
    print(f"\nSalvati i progressi nel database globale.")
    
    if ancora_non_matchati:
        with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ancora_non_matchati[0].keys())
            writer.writeheader()
            for r in ancora_non_matchati:
                writer.writerow(r)
        print(f"Rimangono {len(ancora_non_matchati)} giocatori non matchati. Salvati in {CSV_OUTPUT}")
    else:
        print("Tutti i giocatori sono stati matchati con successo!")

if __name__ == '__main__':
    run()
