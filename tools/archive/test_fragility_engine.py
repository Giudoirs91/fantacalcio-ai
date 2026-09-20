import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import json
import re

def clean_text(t):
    t = str(t).lower().strip()
    t = re.sub(r"['\".,-]", " ", t)
    return " ".join(t.split())

def test_fragility():
    df_inj = pd.read_csv('data/raw/infortuni_2025_26.csv')
    with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
        master = json.load(f)

    inj_records = []
    for _, row in df_inj.iterrows():
        name = str(row['Giocatore']).strip()
        team = str(row['Squadra']).strip()
        dur = str(row['Durata_Infortunio']).strip()
        dur_low = dur.lower()

        # Classificazione gravita/fragilita
        if any(w in dur_low for w in ['stagione finita', 'risoluzione', '2027', 'calvario', 'prolungato', 'crociato', 'ricorrenti']):
            level = 'ALTA'
            score = 3
            badge = 'alta'
            label = '🔴 Alta'
            pen_ovr = -2.8
            mult_prc = 0.80
        elif any(w in dur_low for w in ['assenze multiple', 'frequenti', 'novembre', 'ottobre', 'settembre', 'marzo', 'aprile', 'maggio', 'mesi']):
            level = 'ALTA'
            score = 3
            badge = 'alta'
            label = '🔴 Alta'
            pen_ovr = -2.2
            mult_prc = 0.85
        elif any(w in dur_low for w in ['stop brevi', 'gestione carichi', 'gestione dolore', 'rotazioni', '15 giorni', '9 giorni', '7 giorni', '19 giorni', 'temporaneo', 'da valutare', 'monitorate', 'recuperato']):
            level = 'MEDIA'
            score = 2
            badge = 'media'
            label = '🟡 Media'
            pen_ovr = -0.8
            mult_prc = 0.93
        else:
            level = 'MEDIA'
            score = 2
            badge = 'media'
            label = '🟡 Media'
            pen_ovr = -1.0
            mult_prc = 0.90

        inj_records.append({
            'name': name,
            'clean': clean_text(name),
            'team': team,
            'dur': dur,
            'level': level,
            'score': score,
            'badge': badge,
            'label': label,
            'pen_ovr': pen_ovr,
            'mult_prc': mult_prc
        })

    matched = 0
    for p in master:
        cp = clean_text(p['name'])
        found = None
        for inj in inj_records:
            if inj['clean'] == cp or (len(inj['clean']) > 4 and inj['clean'] in cp) or (len(cp) > 4 and cp in inj['clean']):
                found = inj
                break
        if found:
            matched += 1
            p['fragilita_val'] = found['label']
            p['fragilita_badge'] = found['badge']
            p['fragilita_score'] = found['score']
            p['fragilita_dettaglio'] = f"{found['dur']} (2025/26)"
        else:
            # Calcolo da presenze / titolarita
            presenze = p.get('presenze', 0)
            titolarita = p.get('titolarita', 0)
            if presenze <= 15 and p.get('fvm', 0) >= 15:
                p['fragilita_val'] = '🔴 Alta'
                p['fragilita_badge'] = 'alta'
                p['fragilita_score'] = 3
                p['fragilita_dettaglio'] = 'Presenze limitate (< 16 gare)'
            elif presenze <= 24 and p.get('fvm', 0) >= 10:
                p['fragilita_val'] = '🟡 Media'
                p['fragilita_badge'] = 'media'
                p['fragilita_score'] = 2
                p['fragilita_dettaglio'] = 'Impiego discontinuo (16-24 gare)'
            else:
                p['fragilita_val'] = '🟢 Bassa'
                p['fragilita_badge'] = 'bassa'
                p['fragilita_score'] = 1
                p['fragilita_dettaglio'] = 'Integro / Bassa incidenza infortuni'

    print(f"Matched {matched} players directly from CSV injury report.")
    levels = {}
    for p in master:
        levels[p['fragilita_val']] = levels.get(p['fragilita_val'], 0) + 1
    print("Final Master Fragility Levels:", levels)

if __name__ == '__main__':
    test_fragility()
