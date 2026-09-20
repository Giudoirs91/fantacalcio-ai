import json

files = {
    "Monza - Sassuolo": "data/raw/odds/36381-1650.json",
    "Bologna - Torino": "data/raw/odds/bolognatorino.json",
    "Udinese - Cagliari": "data/raw/odds/udinesecagliari.json",
    "Venezia - Lazio": "data/raw/odds/venezialazio.json"
}

for match_name, fpath in files.items():
    print(f"\n==========================================")
    print(f"MATCH: {match_name}")
    print(f"==========================================")
    with open(fpath, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    info = d.get("infoAggiuntivaMap", {})
    
    # 1. Cerca "almeno Y tiri in porta in entrambi i tempi"
    for v in info.values():
        desc = (v.get("descrizione") or "").strip()
        if "TIRI IN PORTA IN ENTRAMBI I TEMPI" in desc.upper():
            es = [(e.get("descrizione"), e.get("quota")/100) for e in v.get("esitoList", []) if e.get("descrizione") == "SI"]
            if es:
                print(f"  [TIRI/TEMPO] {desc} -> SI @ {es[0][1]}")
                
    # 2. Cerca 1X2 Tiri in porta e Falli
    for v in info.values():
        desc = (v.get("descrizione") or "").strip()
        if desc.upper() in ["1X2 TIRI IN PORTA", "1X2 FALLI COMMESSI INC.TS", "ARBITRO CONSULTA MONITOR VAR INCL. T.S.", "RIGORE BATTUTO + ARBITRO"]:
            es = [(e.get("descrizione"), e.get("quota")/100) for e in v.get("esitoList", [])]
            print(f"  [SPECIALE] {desc} -> {es}")

    # 3. Cerca Corner speciali
    for v in info.values():
        desc = (v.get("descrizione") or "").strip()
        if desc.upper() in ["CORNER PRIMI 10 MINUTI", "ALMENO 2 CORNER IN ENTRAMBI I TEMPI", "ALMENO 4 CORNER IN ENTRAMBI I TEMPI"]:
            es = [(e.get("descrizione"), e.get("quota")/100) for e in v.get("esitoList", []) if e.get("descrizione") == "SI"]
            if es:
                print(f"  [CORNER] {desc} -> SI @ {es[0][1]}")
