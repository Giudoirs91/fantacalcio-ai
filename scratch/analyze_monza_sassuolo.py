import json

path = "data/raw/odds/36381-1650.json"
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

avv = d.get("avvenimentoFe", {})
info_agg = d.get("infoAggiuntivaMap", {})

print(f"=== ANALISI VALUE BET PER {avv.get('descrizione')} ===")

interesting_markets = [
    "1X2", "U/O 2.5", "GOAL/NOGOAL", "1X2 + U/O 2.5", "1X2 + U/O 1.5",
    "U/O 2.5 + GG/NG", "DOPPIA CHANCE + U/O 2.5", "DOPPIA CHANCE + GOAL/NOGOAL",
    "MULTIGOAL", "ESITO 1 TEMPO 1X2", "1X2 CORNER", "U/O 8.5 CORNER", "U/O 9.5 CORNER",
    "RIGORE BATTUTO + ARBITRO", "1X2 FALLI COMMESSI"
]

results = []
for k, v in info_agg.items():
    desc = v.get("descrizione", "")
    for target in interesting_markets:
        if desc.upper() == target.upper() or (target in desc.upper() and len(desc) < 35):
            esiti = []
            for e in v.get("esitoList", []):
                q = (e.get("quota") or 0) / 100.0
                esiti.append(f"{e.get('descrizione')} @ {q:.2f}")
            if esiti:
                results.append((desc, esiti))
            break

for desc, esiti in results[:20]:
    print(f"\n* {desc}:")
    print("  " + " | ".join(esiti[:6]))
