import os
import json

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")

def load_json_config(filename, default=None):
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ConfigLoader] Errore caricamento {filename}: {e}")
        return default if default is not None else {}

def get_tactical_db():
    return load_json_config("tactical_db.json", default={})

def get_infortuni_storici_tm():
    return load_json_config("infortuni_storici_2025_26.json", default={})

def get_injuries_db():
    return load_json_config("injuries.json", default={})

def get_fragile_players():
    data = load_json_config("fragile_players.json", default=[])
    return set(data)

def get_team_ratings():
    return load_json_config("team_ratings.json", default={})

def get_league_settings():
    return load_json_config("league_settings.json", default={
        "num_teams": 8,
        "total_budget": 1000,
        "slots": {
            "P": {"max": 3, "budget_target_pct": 0.06},
            "D": {"max": 8, "budget_target_pct": 0.18},
            "C": {"max": 8, "budget_target_pct": 0.32},
            "A": {"max": 6, "budget_target_pct": 0.44}
        }
    })

def get_injuries_history_db():
    data = load_json_config("injuries_history.json", default=None)
    if data:
        return data
    return load_json_config("infortuni_storici_2025_26.json", default={})

def get_infortuni_2025_26():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(root_dir, "config", "infortuni_storici_2025_26.json")
    if not os.path.exists(json_path):
        return []
    
    try:
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
            
        records = []
        for team, players in db.items():
            for name, p in players.items():
                partite = p.get('partite_saltate', 0)
                
                # 1. BASSA GRAVITÀ (0 partite)
                if partite == 0:
                    level = 'BASSA'
                    score = 1
                    badge = 'bassa'
                    label = '🟢 Bassa'
                    pen_ovr = 0.0
                    mult_prc = 1.00
                # 2. MEDIA GRAVITÀ (1-6 partite)
                elif partite <= 6:
                    level = 'MEDIA'
                    score = 2
                    badge = 'media'
                    label = '🟡 Media'
                    pen_ovr = 1.0
                    mult_prc = 0.92
                # 3. ALTA GRAVITÀ (> 6 partite)
                else:
                    level = 'ALTA'
                    score = 3
                    badge = 'alta'
                    label = '🔴 Alta'
                    pen_ovr = 2.5
                    mult_prc = 0.82
                
                # Costruisci stringa descrittiva
                diagnosi_strs = [f"{d.get('motivo', 'Non specificato')} ({d.get('partite', 0)})" for d in p.get('diagnosi', [])]
                durata = " - ".join(diagnosi_strs) if diagnosi_strs else "Nessun infortunio rilevante"

                records.append({
                    'name': name,
                    'team': team,
                    'durata': durata,
                    'level': level,
                    'score': score,
                    'badge': badge,
                    'label': label,
                    'pen_ovr': pen_ovr,
                    'mult_prc': mult_prc
                })
        return records
    except Exception as e:
        print(f"[ConfigLoader] Errore caricamento infortuni 2025/26 JSON: {e}")
        return []

