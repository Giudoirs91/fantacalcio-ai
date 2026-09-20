import pdfplumber
import os
import re
import unicodedata
import pandas as pd

REPORT_DIR = "match report 26-27"
pdf_files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")])

df_listone = pd.read_excel("Agg_Quotazioni_Fantacalcio_Stagione_2026_27 (1).xlsx", skiprows=1)
listone_dict = {}
for _, row in df_listone.iterrows():
    name = str(row.get('Nome', '')).strip()
    role = str(row.get('R', '')).strip()
    team = str(row.get('Squadra', '')).strip()
    fvm = int(row.get('FVM', 1)) if pd.notna(row.get('FVM')) else 1
    if name:
        listone_dict[name.lower()] = {"name": name, "role": role, "team": team, "fvm": fvm}

def find_in_listone(raw_name, team_hint=None):
    raw_clean = re.sub(r'[^a-zA-Z\s]', '', unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('utf-8')).strip().lower()
    
    # 1. Exact match
    for k, v in listone_dict.items():
        k_clean = re.sub(r'[^a-zA-Z\s]', '', unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore').decode('utf-8')).strip().lower()
        if k_clean == raw_clean:
            return v
            
    # 2. Substring match
    candidates = []
    for k, v in listone_dict.items():
        k_clean = re.sub(r'[^a-zA-Z\s]', '', unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore').decode('utf-8')).strip().lower()
        if raw_clean in k_clean or k_clean in raw_clean:
            candidates.append(v)
            
    if candidates:
        if team_hint:
            for c in candidates:
                if c['team'].lower() == team_hint.lower():
                    return c
        return candidates[0]
    return None

for fname in pdf_files:
    fpath = os.path.join(REPORT_DIR, fname)
    with pdfplumber.open(fpath) as pdf:
        p2 = pdf.pages[1]
        text = p2.extract_text() or ""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Lineup starts after FORMAZIONI and ends before A disposizione
        in_lineup = False
        lineup_lines = []
        for l in lines:
            if "FORMAZIONI" in l:
                in_lineup = True
                continue
            if "A disposizione" in l:
                in_lineup = False
                break
            if in_lineup:
                lineup_lines.append(l)
                
        print(f"\n=======================================================")
        print(f"FILE: {fname}")
        for ll in lineup_lines[:15]:
            print("  ", ll.encode('ascii', 'ignore').decode('ascii'))
