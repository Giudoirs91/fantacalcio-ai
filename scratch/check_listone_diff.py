import json
import pandas as pd

old_data = json.load(open('processed_players_master.json', encoding='utf-8'))
old_players = {p['id']: p for p in old_data}

df = pd.read_excel('data/raw/Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1).dropna(subset=['Id', 'Nome', 'Squadra'])
new_ids = set(df['Id'].astype(int))
old_ids = set(old_players.keys())

added_ids = new_ids - old_ids
removed_ids = old_ids - new_ids

print(f"=== GIOCATORI AGGIUNTI ({len(added_ids)}) ===")
for pid in added_ids:
    r = df[df['Id'] == pid].iloc[0]
    print(f"+ ID: {pid:4d} | Ruolo: {r['R']:2s} ({r['RM']:4s}) | {r['Nome']:18s} | Squadra: {r['Squadra']:12s} | Qt.A: {r['Qt.A']:2.0f} | FVM: {r['FVM']:3.0f}")

print(f"\n=== GIOCATORI RIMOSSI ({len(removed_ids)}) ===")
for pid in removed_ids:
    p = old_players[pid]
    print(f"- ID: {pid:4d} | Ruolo: {p.get('ruolo', ''):2s} | {p.get('nome', ''):18s} | Squadra: {p.get('squadra', ''):12s} | FVM prec: {p.get('fvm', 0)}")

# Check quotation and FVM changes among existing players
qta_changes = []
fvm_changes = []

for _, r in df.iterrows():
    pid = int(r['Id'])
    if pid in old_players:
        old_p = old_players[pid]
        old_qta = old_p.get('quotazione_attuale', 0)
        new_qta = float(r['Qt.A'])
        if old_qta != new_qta:
            qta_changes.append((r['Nome'], r['Squadra'], old_qta, new_qta, new_qta - old_qta))
            
        old_fvm = old_p.get('fvm') or old_p.get('fvm_1000') or 0
        new_fvm = float(r['FVM'])
        if old_fvm != new_fvm:
            fvm_changes.append((r['Nome'], r['Squadra'], old_fvm, new_fvm, new_fvm - old_fvm))

print(f"\n=== VARIAZIONI QUOTAZIONE ATTUALE (Qt.A) ({len(qta_changes)} giocatori) ===")
for item in sorted(qta_changes, key=lambda x: abs(x[4]), reverse=True)[:15]:
    print(f"  {item[0]:18s} ({item[1]:10s}): da {item[2]:2.0f} a {item[3]:2.0f} (diff: {item[4]:+2.0f})")

print(f"\n=== VARIAZIONI FVM (1000) ({len(fvm_changes)} giocatori) ===")
for item in sorted(fvm_changes, key=lambda x: abs(x[4]), reverse=True)[:15]:
    print(f"  {item[0]:18s} ({item[1]:10s}): da {item[2]:3.0f} a {item[3]:3.0f} (diff: {item[4]:+3.0f})")
