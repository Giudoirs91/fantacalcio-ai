import json

files = {
    "Fiorentina - Napoli": "data/raw/odds/Fiorentinanapoli.json",
    "Bologna - Torino": "data/raw/odds/bolognatorino.json",
    "Udinese - Cagliari": "data/raw/odds/udinesecagliari.json",
    "Venezia - Lazio": "data/raw/odds/venezialazio.json",
    "Monza - Sassuolo": "data/raw/odds/36381-1650.json"
}

interesting_keywords = [
    "FUORIGIOCO", "SOSTITUZIONI", "TEMPO CON PIU", "VINCE ALMENO UN TEMPO",
    "SEGNA IN ENTRAMBI I TEMPI", "GOL NEL RECUPERO", "PALI/TRAVERSE",
    "AUTORETE", "RIGORE SI/NO", "FASCE MINUTI"
]

for match, fpath in files.items():
    print(f"\n==========================================")
    print(f"MATCH: {match}")
    print(f"==========================================")
    with open(fpath, "r", encoding="utf-8") as f:
        d = json.load(f)
    info = d.get("infoAggiuntivaMap", {})
    
    seen = set()
    for v in info.values():
        desc = (v.get("descrizione") or "").strip()
        for kw in interesting_keywords:
            if kw in desc.upper() and desc not in seen:
                seen.add(desc)
                es = [(e.get("descrizione"), round((e.get("quota") or 0)/100, 2)) for e in v.get("esitoList", [])]
                if es and len(desc) < 45:
                    print(f"  * {desc} -> {es[:4]}")
                break
