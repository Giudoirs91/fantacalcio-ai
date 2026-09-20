import os
import sys
import json
import argparse
import datetime
from typing import Dict, List, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTI_JSON_PATH = os.path.join(ROOT_DIR, "data", "processed", "voti_fantacalcio_2026_27.json")
PLAYERS_MASTER_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
INJURIES_JSON_PATH = os.path.join(ROOT_DIR, "config", "injuries_history.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "data", "official_calendar_2026_27.json")

def load_json(path: str, default: Any = None):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRORE] Impossibile caricare {path}: {e}")
    return default if default is not None else {}

def save_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESSO] File salvato: {path}")

def record_player_match_performance(
    giornata: int,
    player_name: str,
    team: str,
    voto: float,
    gf: int = 0,
    ass: int = 0,
    amm: int = 0,
    esp: int = 0,
    gs: int = 0,
    rp: int = 0,
    rs: int = 0,
    au: int = 0,
    minuti: int = 90,
    is_home: bool = True,
    opponent: str = "",
    injury_event: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Registra la prestazione di un calciatore per una specifica giornata di Serie A
    e calcola il fantavoto ufficiale.
    """
    fantavoto = voto + (gf * 3) + (ass * 1) + (rp * 3) - (gs * 1) - (rs * 3) - (au * 2) - (amm * 0.5) - (esp * 1)
    fantavoto = round(fantavoto, 2)
    
    parts = []
    if gf > 0: parts.push(f"+{gf*3} ({gf}G)") if hasattr(parts, 'push') else parts.append(f"+{gf*3} ({gf}G)")
    if ass > 0: parts.append(f"+{ass} ({ass}A)")
    if rp > 0: parts.append(f"+{rp*3} (Rig.Par)")
    if gs > 0: parts.append(f"-{gs} ({gs}GS)")
    if rs > 0: parts.append(f"-{rs*3} (Rig.Sb)")
    if au > 0: parts.append(f"-{au*2} (Autogol)")
    if amm > 0: parts.append(f"-0.5 (Amm)")
    if esp > 0: parts.append(f"-1 (Esp)")
    bm_str = ", ".join(parts) if parts else "Nessun bonus"
    
    perf = {
        "giornata": giornata,
        "voto": voto,
        "fantavoto": fantavoto,
        "gf": gf,
        "ass": ass,
        "amm": amm,
        "esp": esp,
        "gs": gs,
        "rp": rp,
        "rs": rs,
        "au": au,
        "minuti": minuti,
        "is_home": is_home,
        "opponent": opponent,
        "match": f"{team} vs {opponent}" if is_home else f"{team} @ {opponent}",
        "bonus_malus_str": bm_str
    }
    
    # Se presente un infortunio nel corso della partita, lo registriamo
    if injury_event:
        record_injury_incident(player_name, team, injury_event, giornata)
        
    return perf

def record_injury_incident(player_name: str, team: str, injury_data: Dict[str, Any], giornata: int):
    """
    Aggiunge un evento di infortunio allo storico del database infortuni.
    """
    inj_db = load_json(INJURIES_JSON_PATH, default={"metadata": {}, "players": {}})
    if "players" not in inj_db:
        inj_db["players"] = {}
        
    p_key = player_name.upper().strip()
    if p_key not in inj_db["players"]:
        inj_db["players"][p_key] = {
            "player_id": None,
            "nome": player_name,
            "squadra": team,
            "fragility_score": 35,
            "fragility_tier": "🟢 Stabile (Basso Rischio)",
            "disponibilita_pct": 92.0,
            "partite_saltate_totali": 0,
            "giorni_stop_totali": 0,
            "recidive_muscolari": 0,
            "stato_attuale": "🩹 Infortunato",
            "rientro_stimato": injury_data.get("rientro_stimato", f"Giornata {giornata + 3}"),
            "motivo_attuale": injury_data.get("diagnosi", "Problema fisico"),
            "consiglio_medico_ai": "Infortunio recente sotto monitoraggio.",
            "cronistoria": []
        }
    
    p_obj = inj_db["players"][p_key]
    giorni = injury_data.get("giorni", 21)
    partite_perse = injury_data.get("partite_perse", 3)
    tipo = injury_data.get("tipo", "muscolare")
    
    p_obj["partite_saltate_totali"] += partite_perse
    p_obj["giorni_stop_totali"] += giorni
    if tipo.lower() == "muscolare":
        p_obj["recidive_muscolari"] += 1
    p_obj["stato_attuale"] = "🩹 Infortunato"
    p_obj["rientro_stimato"] = injury_data.get("rientro_stimato", f"Giornata {giornata + partite_perse}")
    p_obj["motivo_attuale"] = injury_data.get("diagnosi", "Infortunio muscolare")
    
    # Ricalcolo fragilità
    new_frag = min(100, p_obj["fragility_score"] + (partite_perse * 5) + (giorni // 10) + (10 if tipo == 'muscolare' else 5))
    p_obj["fragility_score"] = new_frag
    if new_frag >= 80:
        p_obj["fragility_tier"] = "🔴 Cristallo (Rischio Altissimo)"
    elif new_frag >= 60:
        p_obj["fragility_tier"] = "🟠 Fragile (Frequenti Stop)"
    elif new_frag >= 40:
        p_obj["fragility_tier"] = "🟡 Attenzione (Qualche Acciacco)"
    else:
        p_obj["fragility_tier"] = "🟢 Stabile (Basso Rischio)"
        
    p_obj["disponibilita_pct"] = max(40.0, round(100.0 - (p_obj["partite_saltate_totali"] / 114.0 * 100.0), 1))
    
    new_entry = {
        "stagione": "2026/27",
        "diagnosi": injury_data.get("diagnosi", "Lesione muscolare"),
        "tipo": tipo,
        "giorni": giorni,
        "partite_perse": partite_perse,
        "data_inizio": datetime.date.today().strftime("%Y-%m-%d"),
        "data_fine": (datetime.date.today() + datetime.timedelta(days=giorni)).strftime("%Y-%m-%d")
    }
    p_obj["cronistoria"].insert(0, new_entry)
    
    save_json(INJURIES_JSON_PATH, inj_db)
    print(f"[INFORTUNIO] Registrato nuovo infortunio per {player_name}: {injury_data.get('diagnosi')} (Fragilità aggiornata a {new_frag})")

def append_round_to_voti_db(giornata: int, round_records: List[Dict[str, Any]]):
    """
    Aggiunge o aggiorna i voti di una giornata nel file processed voti_fantacalcio_2026_27.json.
    """
    voti_db = load_json(VOTI_JSON_PATH, default={})
    
    count_updated = 0
    for rec in round_records:
        p_name = rec["nome"].strip().upper()
        if p_name not in voti_db:
            voti_db[p_name] = []
        
        # Rimuovi eventuale duplicato per la stessa giornata
        voti_db[p_name] = [v for v in voti_db[p_name] if v.get("giornata") != giornata]
        
        # Aggiungi nuova prestazione
        voti_db[p_name].append({
            "giornata": giornata,
            "voto": rec.get("voto", 6.0),
            "fantavoto": rec.get("fantavoto", rec.get("voto", 6.0)),
            "gf": rec.get("gf", 0),
            "ass": rec.get("ass", 0),
            "amm": rec.get("amm", 0),
            "esp": rec.get("esp", 0),
            "gs": rec.get("gs", 0),
            "rp": rec.get("rp", 0),
            "rs": rec.get("rs", 0),
            "au": rec.get("au", 0),
            "minuti": rec.get("minuti", 90),
            "is_home": rec.get("is_home", True),
            "opponent": rec.get("opponent", "-"),
            "match": rec.get("match", "-"),
            "bonus_malus_str": rec.get("bonus_malus_str", "-")
        })
        # Ordina per giornata
        voti_db[p_name].sort(key=lambda x: x.get("giornata", 0))
        count_updated += 1
        
    save_json(VOTI_JSON_PATH, voti_db)
    print(f"[ROUND ENGINE] Aggiornati {count_updated} voti per Giornata {giornata}.")

def main():
    parser = argparse.ArgumentParser(description="Tool per la registrazione dei turni settimanali di Serie A e aggiornamento ML")
    parser.add_argument("--giornata", type=int, help="Numero della giornata da registrare")
    parser.add_argument("--file", type=str, help="Percorso di un file JSON con le prestazioni del turno")
    parser.add_argument("--sync-pipeline", action="store_true", help="Esegue la pipeline di aggiornamento master e ML dataset")
    args = parser.parse_args()

    print("=" * 70)
    print("  FANTA MASTER AI — RECORD ROUND & INJURY INGESTION TOOL")
    print("=" * 70)

    if args.file and args.giornata:
        file_path = os.path.abspath(args.file)
        if os.path.exists(file_path):
            records = load_json(file_path, default=[])
            append_round_to_voti_db(args.giornata, records)
        else:
            print(f"[ERRORE] File non trovato: {file_path}")
            return
            
    if args.sync_pipeline:
        print("\n[PIPELINE] Avvio aggiornamento pipeline e dataset ML...")
        os.system("python main.py --pipeline")
        os.system("python src/ml_dataset_generator.py")
        print("[PIPELINE] Aggiornamento completato con successo.")

if __name__ == "__main__":
    main()
