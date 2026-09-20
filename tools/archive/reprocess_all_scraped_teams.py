import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.manage_injuries_database import process_scraped_team, init_full_database, CONFIG_PATH

# 1. Reset/Init full database for all 523 players
print("1. Inizializzazione Database Globale...")
db = init_full_database()
with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"✓ Creato DB con {sum(len(v) for v in db.values())} calciatori su {len(db)} squadre.")

# Mappa step delle squadre scrapate finora
scraped_steps = [
    ("Atalanta", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\968\content.md"),
    ("Inter", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1055\content.md"),
    ("Napoli", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1095\content.md"),
    ("Roma", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1107\content.md"),
    ("Como", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1123\content.md"),
    ("Juventus", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1151\content.md"),
    ("Bologna", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1171\content.md"),
    ("Lazio", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1201\content.md"),
    ("Udinese", r"C:\Users\dorsi\.gemini\antigravity-ide\brain\a80fdade-57e7-4a13-bef6-e735ff50b036\.system_generated\steps\1241\content.md"),
    ("Sassuolo", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\sassuolo_tm.html"),
    ("Torino", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\torino_tm.html"),
    ("Parma", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\parma_tm.html"),
    ("Cagliari", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\cagliari_tm.html"),
    ("Fiorentina", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\fiorentina_tm.html"),
    ("Genoa", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\genoa_tm.html"),
    ("Lecce", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\lecce_tm.html"),
    ("Venezia", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\venezia_tm.html"),
    ("Frosinone", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\frosinone_tm.html"),
    ("Monza", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\monza_tm.html"),
    ("Milan", r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\raw\milan_tm.html"),
]

for team_name, step_path in scraped_steps:
    if os.path.exists(step_path):
        with open(step_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        print(f"\nElaborazione {team_name}...")
        log = process_scraped_team(team_name, html)
        if team_name == "Bologna":
            bologna_log = log

# Stampa report specifico per Bologna (e per i trasferiti da Bologna ad altre squadre)
print("\n" + "="*70)
print("=== REPORT INFORTUNI BOLOGNA 2025/2026 (MATCHATI SUL LISTONE 2026/27) ===")
print("="*70)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    full_db = json.load(f)

# Giocatori attualmente al Bologna
bologna_players = full_db.get("Bologna", {})
sorted_bol = sorted(bologna_players.items(), key=lambda x: x[1]['partite_saltate'], reverse=True)

print(f"\n[ROSA BOLOGNA 2026/27 - {len(bologna_players)} Calciatori]")
for name, p in sorted_bol:
    status = f"{p['partite_saltate']} partite saltate ({p['livello_fragilita']})"
    print(f"• [{p['ruolo']}] {name} (TM: {p['tm_matched_name']}) -> {status}")
    if p['diagnosi']:
        for d in p['diagnosi']:
            days = ", ".join(f"G{g}" for g in d['giornate'])
            print(f"    - {d['motivo']}: {d['partite']} gare ({days})")

# Giocatori che nel 25/26 erano al Bologna ma ora sono in altre squadre di Serie A
print("\n[EX BOLOGNA 25/26 TRASFERITI IN ALTRE SQUADRE SERIE A 26/27]")
for team, squad in full_db.items():
    if team == "Bologna": continue
    for pname, p in squad.items():
        if p.get('squadra_tm_2526') == "Bologna":
            print(f"• [{p['ruolo']}] {pname} (Oggi al {team}) -> {p['partite_saltate']} partite saltate (TM: {p['tm_matched_name']})")
