import os
import json
import pandas as pd
from .player_matcher import clean_text

def safe_float(val, default=0.0):
    if pd.isna(val) or val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(str(val).replace(',', '.').strip())
    except Exception:
        return default

def safe_int(val, default=0):
    if pd.isna(val) or val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)
    try:
        return int(float(str(val).replace(',', '.').strip()))
    except Exception:
        return default

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_quotazioni(filepath=None):
    """
    Carica il listone quotazioni più recente disponibile nel workspace o in data/raw.
    """
    candidates = []
    if filepath:
        candidates.append(filepath)
        if not os.path.isabs(filepath):
            candidates.append(os.path.join(ROOT_DIR, filepath))

    base_names = [
        "Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx",
        "data/raw/Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx",
        "Agg_Quotazioni_Fantacalcio_Stagione_2026_27 (1).xlsx",
        "data/raw/Agg_Quotazioni_Fantacalcio_Stagione_2026_27 (1).xlsx",
        "Agg_Quotazioni_Fantacalcio_Stagione_2026_27.xlsx",
        "data/raw/Agg_Quotazioni_Fantacalcio_Stagione_2026_27.xlsx",
        "Quotazioni_Fantacalcio_Stagione_2026_27.xlsx",
        "data/raw/Quotazioni_Fantacalcio_Stagione_2026_27.xlsx"
    ]
    for b in base_names:
        candidates.append(b)
        candidates.append(os.path.join(ROOT_DIR, b))
    
    selected_path = None
    for cand in candidates:
        if cand and os.path.exists(cand):
            selected_path = cand
            break

    if not selected_path:
        raise FileNotFoundError("Nessun file Quotazioni Excel trovato nel workspace!")

    print(f"[StatsProcessor] Caricamento Quotazioni da: {selected_path}")
    df = pd.read_excel(selected_path, skiprows=1)
    df = df.dropna(subset=['Id', 'Nome', 'Squadra'])
    return df

def load_voti_storici(filepath=None):
    if not filepath:
        filepath = os.path.join(ROOT_DIR, "data", "raw", "voti 25-26", "Riepilogo_Stagionale_Voti_2025_26.csv")
    if not os.path.exists(filepath):
        alt_paths = [
            "data/raw/voti 25-26/Riepilogo_Stagionale_Voti_2025_26.csv",
            "voti 25-26/Riepilogo_Stagionale_Voti_2025_26.csv",
            os.path.join(ROOT_DIR, "voti 25-26", "Riepilogo_Stagionale_Voti_2025_26.csv")
        ]
        for ap in alt_paths:
            if os.path.exists(ap):
                filepath = ap
                break

    if not os.path.exists(filepath):
        print(f"[StatsProcessor] Warning: File voti non trovato: {filepath}")
        return {}

    try:
        df_voti = pd.read_csv(filepath, encoding='latin1', sep=None, engine='python')
        df_voti['clean_name'] = df_voti['Nome'].apply(clean_text)
        return {row['clean_name']: row.to_dict() for _, row in df_voti.iterrows()}
    except Exception as e:
        print(f"[StatsProcessor] Errore caricamento voti: {e}")
        return {}

def load_fotmob_stats(filepath=None):
    """
    Carica il dataset unificato 2025/2026 (Serie A + Top Campionati Esteri) indicizzato per Player ID e Clean Name.
    """
    if not filepath:
        filepath = os.path.join(ROOT_DIR, "data", "raw", "preview_all_518_players_stats_2025_26.csv")
    if not os.path.exists(filepath):
        alt_paths = [
            "data/raw/preview_all_518_players_stats_2025_26.csv",
            os.path.join(ROOT_DIR, "data", "raw", "fotmob_seriea_2025_26_clean.csv"),
            "data/raw/fotmob_seriea_2025_26_clean.csv"
        ]
        for ap in alt_paths:
            if os.path.exists(ap):
                filepath = ap
                break

    if not os.path.exists(filepath):
        print(f"[StatsProcessor] Warning: File statistiche 2025/26 non trovato: {filepath}")
        return {}

    try:
        df_stats = pd.read_csv(filepath)
        lookup = {}
        for _, row in df_stats.iterrows():
            r_dict = row.to_dict()
            if 'id' in r_dict and pd.notna(r_dict['id']):
                lookup[f"id_{int(r_dict['id'])}"] = r_dict
            if 'name' in r_dict and pd.notna(r_dict['name']):
                c_name = clean_text(str(r_dict['name']))
                lookup[c_name] = r_dict
        return lookup
    except Exception as e:
        print(f"[StatsProcessor] Errore caricamento statistiche 2025/26: {e}")
        return {}

def load_fotmob_2026_27_stats(filepath=None):
    """
    Carica le metriche avanzate FotMob ufficiali della Serie A 2026/2027 in corso
    (xG/90, xA/90, Big Chances Created, Chances Created, Rating, ecc.).
    """
    if not filepath:
        filepath = os.path.join(ROOT_DIR, "data", "raw", "fotmob_seriea_2026_27_stats.json")
    if not os.path.exists(filepath):
        alt = "data/raw/fotmob_seriea_2026_27_stats.json"
        if os.path.exists(alt):
            filepath = alt
        else:
            return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[StatsProcessor] Caricate metriche FotMob 2026/27 per {len(data)} calciatori.")
        return data
    except Exception as e:
        print(f"[StatsProcessor] Errore caricamento FotMob 2026/27: {e}")
        return {}

def load_fotmob_team_stats(filepath=None):
    """
    Carica le metriche essenziali di squadra FotMob 2026/2027
    (xG, xGA, Clean Sheets, Big Chances, Tocchi Area, Parate/partita, ecc.).
    """
    if not filepath:
        filepath = os.path.join(ROOT_DIR, "data", "raw", "fotmob_team_stats_2026_27.json")
    if not os.path.exists(filepath):
        alt = "data/raw/fotmob_team_stats_2026_27.json"
        if os.path.exists(alt):
            filepath = alt
        else:
            return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[StatsProcessor] Caricate statistiche FotMob di squadra per {len(data)} club.")
        return data
    except Exception as e:
        print(f"[StatsProcessor] Errore caricamento statistiche squadra: {e}")
        return {}

