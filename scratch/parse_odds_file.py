import json

path = "data/raw/odds/36381-1650.json"
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

avv = d.get("avvenimentoFe", {})
print(f"=== {avv.get('descrizione')} ({avv.get('data')[:10]}) ===")

info_agg = d.get("infoAggiuntivaMap", {})
print(f"Totale gruppi quote: {len(info_agg)}")

# Raggruppiamo i mercati più famosi
categories_found = {}
all_odds_count = 0

for key, item in info_agg.items():
    desc = item.get("descrizione") or item.get("shortDescription") or "Senza nome"
    esiti = item.get("esitoList", [])
    if not esiti:
        continue
    
    odds_str_list = []
    for e in esiti:
        q_raw = e.get("quota")
        if q_raw and q_raw > 0:
            q_dec = q_raw / 100.0
            odds_str_list.append(f"{e.get('descrizione')} @ {q_dec:.2f}")
            all_odds_count += 1
            
    if desc not in categories_found:
        categories_found[desc] = []
    categories_found[desc].append(odds_str_list)

print(f"Totale quote/esiti analizzabili estratti: {all_odds_count} su {len(categories_found)} tipologie di scommessa!\n")

# Mostriamo alcuni mercati top che interessavano all'utente
top_interests = [
    "1X2", "U/O 2.5", "GOAL/NOGOAL", "DOPPIA CHANCE", "1X2 + U/O", "1X2 + GOAL/NOGOAL",
    "COMBO", "MULTIGOAL", "CORNER", "VAR", "RIGORE", "MARCATORE", "CARTELLIN"
]

print("--- ALCUNI DEI MERCATI CHIAVE DISPONIBILI NEL FILE ---")
displayed = 0
for cat, groups in categories_found.items():
    # Verifica se interessa
    if any(k.lower() in cat.lower() for k in top_interests) or displayed < 15:
        print(f"\n* [{cat}]")
        for g in groups[:2]:
            print("   " + " | ".join(g[:6]))
        displayed += 1
        if displayed >= 20:
            break
