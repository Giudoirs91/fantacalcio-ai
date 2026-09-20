import os
import sys
import json
import pytest
import pandas as pd

# Add root dir to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.config_loader import get_injuries_history_db
from src.ml_dataset_generator import generate_ml_training_dataset
from tools.record_round import record_player_match_performance

def test_injuries_history_db_loading():
    """Verifica che il database storico infortuni sia caricato e contenga giocatori."""
    inj_db = get_injuries_history_db()
    assert isinstance(inj_db, dict), "Il database infortuni deve essere un dizionario"
    assert len(inj_db) > 0, "Il database infortuni non deve essere vuoto"
    
    # Flatten players if grouped by team
    sample_players = []
    for k, v in inj_db.items():
        if isinstance(v, dict):
            if "indice_fragilita_score" in v or "fragility_score" in v:
                sample_players.append((k, v))
            else:
                for p_name, p_obj in v.items():
                    if isinstance(p_obj, dict):
                        sample_players.append((p_name, p_obj))
                        
    assert len(sample_players) > 0, "Nessun giocatore trovato nel database infortuni"
    
    # Check data format for a sample of players
    for name, p_data in sample_players[:25]:
        score = p_data.get("indice_fragilita_score", p_data.get("fragility_score"))
        assert score is not None, f"Manca indice_fragilita_score per {name}"
        assert 0 <= float(score) <= 100, f"Fragility score fuori range (0-100) per {name}"
        assert "disponibilita_pct" in p_data, f"Manca disponibilita_pct per {name}"
        assert 0 <= float(p_data["disponibilita_pct"]) <= 100, f"Disponibilita pct fuori range per {name}"
        assert ("cronistoria_infortuni" in p_data or "cronistoria" in p_data), f"Manca cronistoria per {name}"

def test_processed_players_have_injury_fields():
    """Verifica che processed_players_master.json contenga i campi di fragilità e infortuni arricchiti."""
    master_path = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
    if not os.path.exists(master_path):
        pytest.skip("processed_players_master.json non ancora generato")
        
    with open(master_path, "r", encoding="utf-8") as f:
        master_players = json.load(f)
        
    assert len(master_players) > 0, "processed_players_master non deve essere vuoto"
    
    for p in master_players[:20]:
        assert "fragility_score" in p, f"Manca fragility_score nel master per {p.get('name')}"
        assert "fragility_tier" in p, f"Manca fragility_tier nel master per {p.get('name')}"
        assert "disponibilita_pct" in p, f"Manca disponibilita_pct nel master per {p.get('name')}"
        assert "consiglio_medico_ai" in p, f"Manca consiglio_medico_ai nel master per {p.get('name')}"
        assert "cronistoria_infortuni" in p, f"Manca cronistoria_infortuni nel master per {p.get('name')}"

def test_ml_dataset_generator():
    """Verifica la generazione del dataset per il training dei modelli AI."""
    df = generate_ml_training_dataset()
    assert isinstance(df, pd.DataFrame), "Il generatore ML deve restituire un DataFrame"
    assert len(df) > 0, "Il dataset ML non deve essere vuoto"
    
    required_features = ["fvm", "ovr", "fragility_score", "titolarita", "disponibilita_pct"]
    for col in required_features:
        assert col in df.columns, f"Colonna feature obbligatoria mancante: {col}"
        
    required_targets = ["target_fanta_media", "target_gol", "target_assist", "target_minuti", "target_roi_fvm"]
    for col in required_targets:
        assert col in df.columns, f"Colonna target obbligatoria mancante: {col}"

def test_record_player_match_performance():
    """Verifica il calcolo corretto di fantavoto e bonus per il tool di registrazione turno."""
    perf = record_player_match_performance(
        giornata=3,
        player_name="LAUTARO MARTINEZ",
        team="INTER",
        voto=7.5,
        gf=2,
        ass=1,
        amm=1,
        minuti=85,
        is_home=True,
        opponent="ROMA"
    )
    # Voto 7.5 + 2*3 (6) + 1 (1) - 0.5 (amm) = 14.0
    assert perf["voto"] == 7.5
    assert perf["fantavoto"] == 14.0
    assert "+6 (2G)" in perf["bonus_malus_str"]
    assert "+1 (1A)" in perf["bonus_malus_str"]
    assert "-0.5 (Amm)" in perf["bonus_malus_str"]
    assert perf["is_home"] is True
    assert perf["opponent"] == "ROMA"
