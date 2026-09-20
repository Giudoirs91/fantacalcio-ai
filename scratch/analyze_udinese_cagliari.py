import json

path = "data/raw/odds/udinesecagliari.json"
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

avv = d.get("avvenimentoFe", {})
info_agg = d.get("infoAggiuntivaMap", {})

print(f"=== QUOTE UDINESE - CAGLIARI (Codice: {avv.get('codiceAvvenimento')}) ===")
print("Totale mercati:", len(info_agg))

targets = [
    "1X2", "U/O 2.5", "U/O 1.5", "GOAL/NOGOAL", "1X2 + U/O 2.5", "1X2 + U/O 3.5",
    "DC + MULTIGOAL 1-3", "DC + MULTIGOAL 1-4", "DC + MULTIGOAL 2-4",
    "1X2 + MULTIGOAL 1-3", "U/O 2.5 + GG/NG", "1 TEMPO: 1X2 CORNER", "ESITO 1X2 CORNER",
    "1X2 CORNER", "1X2 TIRI IN PORTA", "1X2 TIRI TOTALI", "1X2 FALLI COMMESSI",
    "OSPITE SEGNA", "CASA SEGNA"
]

found = {}
for k, v in info_agg.items():
    desc = (v.get("descrizione") or v.get("shortDescription") or "").strip()
    for t in targets:
        if desc.upper() == t or (t in desc.upper() and len(desc) < 30):
            esiti = []
            for e in v.get("esitoList", []):
                q = (e.get("quota") or 0) / 100.0
                esiti.append(f"{e.get('descrizione')} @ {q:.2f}")
            if esiti and desc not in found:
                found[desc] = esiti
            break

for desc, esiti in list(found.items())[:25]:
    print(f"* [{desc}]")
    print("   " + " | ".join(esiti[:6]))
