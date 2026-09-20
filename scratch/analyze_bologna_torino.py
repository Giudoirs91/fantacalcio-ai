import json

path = "data/raw/odds/bolognatorino.json"
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

avv = d.get("avvenimentoFe", {})
info_agg = d.get("infoAggiuntivaMap", {})

print(f"Match: {avv.get('descrizione')} | Codice: {avv.get('codiceAvvenimento')}")
print(f"Totale gruppi scommessa: {len(info_agg)}")

# Estraiamo mercati rilevanti
targets = [
    "1X2", "U/O 2.5", "U/O 1.5", "GOAL/NOGOAL", "1X2 + U/O 2.5", "1X2 + U/O 3.5",
    "DOPPIA CHANCE + U/O 2.5", "DOPPIA CHANCE + U/O 3.5", "DOPPIA CHANCE + GOAL/NOGOAL",
    "MULTIGOAL", "1X2 CORNER", "U/O 8.5 CORNER", "U/O 9.5 CORNER", "CASA: U/O CORNER", "OSPITE: U/O CORNER",
    "OSPITE SEGNA", "OSPITE: U/O", "1X2 TIRI IN PORTA", "1X2 TIRI TOTALI", "1X2 FALLI COMMESSI",
    "METODO DEL GOAL 1", "RIGORE BATTUTO + ARBITRO", "PARZIALE/FINALE"
]

found = {}
for k, v in info_agg.items():
    desc = (v.get("descrizione") or v.get("shortDescription") or "").strip()
    for t in targets:
        if desc.upper() == t or (t in desc.upper() and len(desc) < 35):
            esiti = []
            for e in v.get("esitoList", []):
                q = (e.get("quota") or 0) / 100.0
                esiti.append(f"{e.get('descrizione')} @ {q:.2f}")
            if esiti and desc not in found:
                found[desc] = esiti
            break

for desc, esiti in list(found.items())[:35]:
    print(f"* [{desc}]")
    print("   " + " | ".join(esiti[:6]))
