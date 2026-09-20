import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import unicodedata
from bs4 import BeautifulSoup
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.stats_processor import load_quotazioni
from tools.manage_injuries_database import parse_transfermarkt_html, update_team_injuries

file_path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1095\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

tm_players = parse_transfermarkt_html(html)

# Update database
update_team_injuries("Napoli", tm_players)

# Read generated json to print
config_path = os.path.join(ROOT_DIR, "config", "infortuni_storici_2025_26.json")
with open(config_path, "r", encoding="utf-8") as f:
    db = json.load(f)

napoli_db = db.get("Napoli", {})

print()
print("=== CONTEGGIO INFORTUNI NAPOLI 2025/2026 (SOLO GIOCATORI IN ROSA 26/27) ===")
print(f"Totale Calciatori in Rosa: {len(napoli_db)}")
print()

sorted_players = sorted(napoli_db.items(), key=lambda x: x[1]['partite_saltate'], reverse=True)

for name, p in sorted_players:
    print(f"[{p['ruolo']}] {name} (TM: {p['tm_matched_name']}) -> {p['partite_saltate']} partite saltate ({p['livello_fragilita']})")
    if p['diagnosi']:
        for d in p['diagnosi']:
            days_str = ", ".join(f"G{d_idx}" for d_idx in d['giornate'])
            print(f"    • {d['motivo']}: {d['partite']} gare ({days_str})")
