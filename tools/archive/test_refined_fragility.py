import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import json
import re
import unicodedata

def strip_accents(text):
    text = unicodedata.normalize('NFD', str(text))
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

def clean_text(t):
    t = strip_accents(str(t)).lower().strip()
    t = re.sub(r"['\".,-]", " ", t)
    return " ".join(t.split())

# Lista storica consolidata di giocatori strutturalmente fragili (Transfermarkt / Serie A)
HISTORICAL_FRAGILE = {
    "dybala", "pellegrini lo", "pellegrini", "berardi", "sensi", "pellegri", 
    "castrovilli", "chiesa", "scamacca", "spinazzola", "bennacer", "vlasic", 
    "florenzi", "messias", "douglas luiz", "calabria", "mina", "smalling", 
    "ismajli", "abraham", "alexis sanchez", "zaniolo", "zapata d", "zapata",
    "lukaku", "calhanoglu", "pulisic", "lobo", "lobotka", "rabiot"
}

def classify_injury_duration(dur_str):
    dur = dur_str.lower().strip()
    
    # 1. BASSA GRAVITÀ (Stop brevissimi, rientri immediati ad agosto/inizio stagione, recuperati)
    if any(w in dur for w in ['7 giorni', '9 giorni', '15 giorni', '19 giorni', 'recuperato', 'agosto 2026', 'settembre 2026', 'set 2026']):
        # Rientro a inizio stagione o stop sotto i 20 giorni -> Bassa fragilità
        return {
            'level': 'BASSA',
            'score': 1,
            'badge': 'bassa',
            'label': '🟢 Bassa',
            'pen_ovr': 0.0,
            'mult_prc': 1.00
        }
    
    # 2. ALTA GRAVITÀ (Stagione finita, crociato, tendini, fratture, 2027, calvari, assenze croniche multiple)
    if any(w in dur for w in [
        'stagione finita', 'risoluzione', '2027', 'calvario', 'prolungato', 
        'crociato', 'achille', 'frattura', 'ricorrenti', 'assenze multiple', 
        'frequenti stop', 'oltre 60 giorni', 'gennaio 2026'
    ]):
        return {
            'level': 'ALTA',
            'score': 3,
            'badge': 'alta',
            'label': '🔴 Alta',
            'pen_ovr': 2.5,
            'mult_prc': 0.82
        }

    # 3. MEDIA GRAVITÀ (Stop moderati di 1-2 mesi, rientri autunno/primavera 2026, gestione carichi/dolore)
    return {
        'level': 'MEDIA',
        'score': 2,
        'badge': 'media',
        'label': '🟡 Media',
        'pen_ovr': 1.0,
        'mult_prc': 0.92
    }

df_inj = pd.read_csv('data/raw/infortuni_2025_26.csv')
with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

for _, row in df_inj.iterrows():
    name = row['Giocatore']
    dur = row['Durata_Infortunio']
    cls = classify_injury_duration(dur)
    if name in ['Amir Rrahmani', 'Sam Beukema', 'Kevin De Bruyne', 'David Neres', 'Alessandro Bastoni', 'Mike Maignan', 'Christopher Nkunku', 'Christian Pulisic', 'Jayden Addai', 'Honest Ahanor']:
        print(f"CSV Check: {name:22} | {dur:35} | Level: {cls['label']}")

print("\n--- TEST ON MASTER PLAYERS ---")
test_names = ['Dybala', 'Neres', 'Maignan', 'Nkunku', 'Ahanor', 'Bastoni', 'Bisseck', 'Berardi', 'Pulisic', 'Bremer', 'Zaniolo', 'Rrahmani', 'Rrahmani Al.']
for t in test_names:
    for p in master:
        if p['name'].lower() == t.lower():
            print(f"Master: {p['name']:15} | Team: {p['team']:10} | Presenze 25/26: {p.get('presenze',0):2d}")
