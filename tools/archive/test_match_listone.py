import pdfplumber
import os
import json
import pandas as pd
import re
import unicodedata

def clean_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()

# Carica Listone 2026/2027
df_listone = pd.read_excel("Agg_Quotazioni_Fantacalcio_Stagione_2026_27 (1).xlsx", skiprows=1)
# colonne: 'R', 'Nome', 'Squadra', 'FVM'
listone_map = {}
for _, row in df_listone.iterrows():
    p_name = str(row.get('Nome', '')).strip()
    p_role = str(row.get('R', 'C')).strip()
    p_team = str(row.get('Squadra', '')).strip()
    if p_name:
        listone_map[clean_text(p_name)] = {
            "name": p_name,
            "role": p_role,
            "team": p_team,
            "fvm": int(row.get('FVM', 1)) if pd.notna(row.get('FVM')) else 1
        }

print(f"Listone caricato con {len(listone_map)} calciatori.")
