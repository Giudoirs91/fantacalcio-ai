import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
ps = json.load(open('processed_players_master.json', encoding='utf-8'))

print("=== VERIFICA DISTINZIONE: TITOLARI vs SUBENTRATI vs PANCHINARI ===")

# Esempio Inter
print("\n--- INTER ---")
inter_players = [p for p in ps if p['team'] == 'Inter' and (p.get('presenze_2627', 0) > 0 or p.get('is_in_11'))]
inter_players.sort(key=lambda x: (x.get('starts_2627', 0), x.get('presenze_2627', 0)), reverse=True)
for p in inter_players[:12]:
    print(f"• {p['name']:18} | Starts: {p.get('starts_2627', 0)} | Pres: {p.get('presenze_2627', 0)} | Dicitura: {p.get('titolarita_desc_2627', ''):18} | Minuti: {p.get('minuti_2627', 0)}' | Titolarità: {p.get('titolarita')}%")

# Esempio Napoli
print("\n--- NAPOLI ---")
napoli_players = [p for p in ps if p['team'] == 'Napoli' and (p.get('presenze_2627', 0) > 0 or p.get('is_in_11'))]
napoli_players.sort(key=lambda x: (x.get('starts_2627', 0), x.get('presenze_2627', 0)), reverse=True)
for p in napoli_players[:12]:
    print(f"• {p['name']:18} | Starts: {p.get('starts_2627', 0)} | Pres: {p.get('presenze_2627', 0)} | Dicitura: {p.get('titolarita_desc_2627', ''):18} | Minuti: {p.get('minuti_2627', 0)}' | Titolarità: {p.get('titolarita')}%")

# Esempio Como
print("\n--- COMO ---")
como_players = [p for p in ps if p['team'] == 'Como' and (p.get('presenze_2627', 0) > 0 or p.get('is_in_11'))]
como_players.sort(key=lambda x: (x.get('starts_2627', 0), x.get('presenze_2627', 0)), reverse=True)
for p in como_players[:12]:
    print(f"• {p['name']:18} | Starts: {p.get('starts_2627', 0)} | Pres: {p.get('presenze_2627', 0)} | Dicitura: {p.get('titolarita_desc_2627', ''):18} | Minuti: {p.get('minuti_2627', 0)}' | Titolarità: {p.get('titolarita')}%")
