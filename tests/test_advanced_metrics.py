import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.advanced_metrics import (
    compute_floor_and_ceiling,
    compute_sub_impact_metrics,
    compute_matchup_vulnerability,
    evaluate_trade
)

def test_floor_and_ceiling():
    sample_p = {
        "name": "Lautaro Martinez",
        "role": "A",
        "ovr": 92,
        "mv": 6.8,
        "fm": 8.5,
        "xfm": 8.2,
        "xg_2627": 2.5,
        "titolarita": 95,
        "is_rigorista_1": True,
        "fragility_tier": "ROCCIA"
    }
    res = compute_floor_and_ceiling(sample_p)
    assert "floor" in res
    assert "ceiling" in res
    assert res["floor"] <= res["ceiling"]
    assert res["spread"] >= 0
    assert res["volatility_label"] in ["BASSA", "MEDIA", "ALTA", "ESPLOSIVA"]

def test_sub_impact_metrics():
    starter = {"role": "A", "titolarita": 90, "ovr": 88}
    bench = {"role": "A", "titolarita": 25, "ovr": 65, "fvm": 2}
    res_starter = compute_sub_impact_metrics(starter)
    res_bench = compute_sub_impact_metrics(bench)
    assert res_starter["sub_vote_prob"] >= 85
    assert res_bench["sub_vote_prob"] <= 30

def test_matchup_vulnerability():
    cal = [{"giornata": 6, "matches": [{"home": "INTER", "away": "LECCE"}]}]
    team_stats = {"LECCE": {"xga_team_rank": 18, "goals_conceded_match_rank": 17}}
    player = {"team": "INTER", "role": "A", "ovr": 90}
    res = compute_matchup_vulnerability(player, cal, team_stats, current_round=6)
    assert res["opponent"] == "LECCE"
    assert res["vulnerability_score"] >= 65

def test_trade_evaluator():
    give = [{"name": "P1", "role": "A", "xfm": 8.0, "titolarita": 90, "fragility_tier": "ROCCIA", "fvm": 60, "floor": 5.5, "ceiling": 12.0}]
    rec = [{"name": "P2", "role": "A", "xfm": 6.2, "titolarita": 50, "fragility_tier": "CRISTALLO", "fvm": 20, "floor": 5.0, "ceiling": 8.0}]
    res = evaluate_trade(give, rec, remaining_rounds=33)
    assert res["delta_points"] < 0
    assert "SCAMBIO SCONSIGLIATO" in res["verdict"] or "RIFIUTA" in res["verdict"]
