import sys
import os
import re
import json
from bs4 import BeautifulSoup

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(ROOT_DIR, ".gemini", "steps_last", "content.md")
# Path to the fetched file
FETCHED_HTML = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\c83fabeb-216c-45be-91e3-e14e5a942cea\.system_generated\steps\749\content.md"
PLAYERS_MASTER = os.path.join(ROOT_DIR, "processed_players_master.json")
INJURIES_FILE = os.path.join(ROOT_DIR, "config", "injuries.json")

def parse_return_date(desc):
    desc_l = desc.lower()
    if 'febbraio' in desc_l:
        return '15/02/2027'
    elif 'marzo' in desc_l:
        return '15/03/2027'
    elif 'aprile' in desc_l:
        return '15/04/2027'
    elif 'maggio' in desc_l:
        return '15/05/2027'
    elif 'gennaio' in desc_l or '2027' in desc_l:
        return '15/01/2027'
    elif 'fine dicembre' in desc_l:
        return '31/12/2026'
    elif 'metà di dicembre' in desc_l or 'meta di dicembre' in desc_l or 'met di dicembre' in desc_l:
        return '15/12/2026'
    elif 'inizio dicembre' in desc_l or 'inizio di dicembre' in desc_l:
        return '05/12/2026'
    elif 'dicembre' in desc_l:
        return '15/12/2026'
    elif 'fine novembre' in desc_l:
        return '30/11/2026'
    elif 'metà di novembre' in desc_l or 'meta di novembre' in desc_l or 'met di novembre' in desc_l or 'seconda met' in desc_l:
        return '20/11/2026'
    elif 'prima metà di novembre' in desc_l or 'prima meta di novembre' in desc_l or 'inizio novembre' in desc_l:
        return '08/11/2026'
    elif 'novembre' in desc_l:
        return '15/11/2026'
    elif 'fine ottobre' in desc_l:
        return '31/10/2026'
    elif 'prossimo turno' in desc_l or 'mercoled' in desc_l or 'gioved' in desc_l or 'marted' in desc_l or 'infrasettimanale' in desc_l or '10a giornata' in desc_l:
        return '01/11/2026'
    return '15/11/2026'

def determine_severity(desc, return_date):
    desc_l = desc.lower()
    if '2027' in return_date or any(w in desc_l for w in ['crociato', 'operat', 'lungo stop', 'frattura', 'rottura', 'mesi']):
        return 'red'
    elif any(w in desc_l for w in ['lesione', 'distrazione', 'distrattiva']):
        return 'orange'
    else:
        return 'yellow'

def update_injuries():
    with open(FETCHED_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    with open(PLAYERS_MASTER, 'r', encoding='utf-8') as f:
        players_master = json.load(f)

    soup = BeautifulSoup(html, 'html.parser')
    body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else ''
    lines = [l.strip() for l in body_text.split('\n') if l.strip()]

    team_lines = [
        (140, 'Atalanta'), (158, 'Bologna'), (170, 'Cagliari'), (182, 'Como'),
        (194, 'Fiorentina'), (206, 'Frosinone'), (214, 'Genoa'), (228, 'Inter'),
        (244, 'Juventus'), (266, 'Lazio'), (278, 'Lecce'), (293, 'Milan'),
        (311, 'Monza'), (323, 'Napoli'), (341, 'Parma'), (353, 'Roma'),
        (365, 'Sassuolo'), (379, 'Torino'), (393, 'Udinese'), (409, 'Venezia'), (425, 'END')
    ]

    injuries_list = []

    for idx in range(len(team_lines)-1):
        start, team = team_lines[idx]
        end, _ = team_lines[idx+1]
        block = lines[start:end]

        mode = None # 'infortunati' | 'squalificati' | 'diffidati'
        i = 1
        while i < len(block):
            line = block[i]
            if line == 'Infortunati':
                mode = 'infortunati'
                i += 1
                continue
            elif line == 'Squalificati':
                mode = 'squalificati'
                i += 1
                continue
            elif line == 'Diffidati':
                mode = 'diffidati'
                i += 1
                continue

            if mode == 'infortunati':
                if line == 'Nessuno':
                    i += 1
                    continue
                # Line is player name, next line is description
                player_name = line
                desc = block[i+1] if i+1 < len(block) and block[i+1] not in ['Squalificati', 'Diffidati', 'Infortunati'] else ''
                rientro = parse_return_date(desc)
                severity = determine_severity(desc, rientro)

                # Match with master players
                matched_id = None
                p_clean = player_name.lower().replace('.', '').strip()
                for p in players_master:
                    if p.get('team', '').lower() == team.lower():
                        pn_clean = p.get('name', '').lower()
                        if p_clean in pn_clean or pn_clean in p_clean:
                            matched_id = p.get('id')
                            break

                injuries_list.append({
                    "player": player_name,
                    "player_id": matched_id,
                    "team": team,
                    "motivo": desc,
                    "rientro": rientro,
                    "severity": severity,
                    "tipo_stop": "Infortunato",
                    "fonte": "Fantacalcio.it (Aggiornato 26/10/2026)"
                })
                i += 2
            elif mode == 'squalificati':
                if line == 'Nessuno':
                    i += 1
                    continue
                player_name = line
                desc = block[i+1] if i+1 < len(block) and block[i+1] not in ['Diffidati', 'Infortunati', 'Squalificati'] else 'Squalifica'
                matched_id = None
                p_clean = player_name.lower().replace('.', '').strip()
                for p in players_master:
                    if p.get('team', '').lower() == team.lower():
                        pn_clean = p.get('name', '').lower()
                        if p_clean in pn_clean or pn_clean in p_clean:
                            matched_id = p.get('id')
                            break

                injuries_list.append({
                    "player": player_name,
                    "player_id": matched_id,
                    "team": team,
                    "motivo": desc,
                    "rientro": "01/11/2026",
                    "severity": "red",
                    "tipo_stop": "Squalificato",
                    "fonte": "Fantacalcio.it (Aggiornato 26/10/2026)"
                })
                i += 2
            else:
                i += 1

    # Add Éderson (Atalanta) who was sent off in G8 (red card against Frosinone)
    if not any(inj['player'] == 'Éderson' or inj['player'] == 'Ederson' for inj in injuries_list if inj['team'] == 'Atalanta'):
        matched_id = None
        for p in players_master:
            if p.get('team') == 'Atalanta' and 'ederson' in p.get('name', '').lower():
                matched_id = p.get('id')
                break
        injuries_list.append({
            "player": "Éderson",
            "player_id": matched_id,
            "team": "Atalanta",
            "motivo": "Espulso per doppia ammonizione al 69' nell'8ª giornata contro il Frosinone",
            "rientro": "01/11/2026",
            "severity": "red",
            "tipo_stop": "Squalificato",
            "fonte": "Lega Serie A Match Report (Aggiornato 26/10/2026)"
        })

    print(f"Total injuries / indisponibili parsed: {len(injuries_list)}")

    with open(INJURIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(injuries_list, f, indent=2, ensure_ascii=False)
    print(f"✓ Salvato {INJURIES_FILE} con successo!")

    # Summary by team
    by_team = {}
    for inj in injuries_list:
        t = inj['team']
        by_team[t] = by_team.get(t, []) + [f"{inj['player']} ({inj['tipo_stop']})"]
    
    for t in sorted(by_team.keys()):
        print(f"  {t}: {', '.join(by_team[t])}")

if __name__ == '__main__':
    update_injuries()
