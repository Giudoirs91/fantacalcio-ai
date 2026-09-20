import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.dependencies import get_data_store

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert "players_loaded" in data

def test_server_info():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "lan_ip" in data

def test_players_list():
    response = client.get("/api/players?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "players" in data
    assert len(data["players"]) <= 10
    assert data["page"] == 1

def test_players_filter_role():
    response = client.get("/api/players?role=A&page_size=5")
    assert response.status_code == 200
    data = response.json()
    for p in data["players"]:
        assert p["role"] == "A"

def test_players_search():
    store = get_data_store()
    if store.players:
        sample_player = store.players[0]
        name_sub = sample_player["name"][:3]
        response = client.get(f"/api/players?query={name_sub}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

def test_player_detail():
    store = get_data_store()
    if store.players:
        sample_player = store.players[0]
        pid = sample_player["id"]
        response = client.get(f"/api/players/{pid}")
        assert response.status_code == 200
        pdata = response.json()
        assert pdata["id"] == pid
        assert pdata["name"] == sample_player["name"]

def test_roles_summary():
    response = client.get("/api/players/roles-summary")
    assert response.status_code == 200
    data = response.json()
    assert "P" in data
    assert "D" in data
    assert "C" in data
    assert "A" in data
    assert "total" in data

def test_supported_modules():
    response = client.get("/api/lineup/supported-modules")
    assert response.status_code == 200
    data = response.json()
    assert "3-4-3" in data["modules"]
    assert "4-3-3" in data["modules"]

def test_lineup_recommend():
    store = get_data_store()
    # Costruisci una rosa di test con almeno 1 P, 4 D, 4 C, 3 A
    p_list = [p for p in store.players if p.get("role") == "P"][:2]
    d_list = [p for p in store.players if p.get("role") == "D"][:6]
    c_list = [p for p in store.players if p.get("role") == "C"][:6]
    a_list = [p for p in store.players if p.get("role") == "A"][:4]

    squad = p_list + d_list + c_list + a_list
    squad_ids = [p["id"] for p in squad]

    payload = {
        "player_ids": squad_ids,
        "formation": "auto",
        "use_defense_modifier": True,
        "risk_tolerance": "balanced"
    }
    response = client.post("/api/lineup/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["starters"]) == 11
    assert len(data["bench"]) >= 1
    assert "expected_team_score" in data
    assert "formation" in data

def test_gk_matrix():
    response = client.get("/api/stats/gk-matrix")
    assert response.status_code == 200
    data = response.json()
    assert "matrix" in data
    assert "best_pairs" in data

def test_teams_stats():
    response = client.get("/api/stats/teams")
    assert response.status_code == 200
    data = response.json()
    assert "teams" in data

def test_database_overview():
    response = client.get("/api/stats/database-overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_players" in data
    assert "roles_distribution" in data

def test_auction_bid_advice():
    store = get_data_store()
    if store.players:
        sample_player = store.players[0]
        payload = {
            "player_id": sample_player["id"],
            "current_budget": 300,
            "total_budget": 500,
            "league_size": 8
        }
        response = client.post("/api/auction/bid-advice", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == sample_player["id"]
        assert "target_price" in data
        assert "max_bid" in data
        assert "tier" in data

def test_auction_state_sync():
    # Test GET
    response = client.get("/api/auction/state")
    assert response.status_code == 200
    
    # Test POST
    test_state = {"session_name": "Test Auction 2026", "current_turn": 1}
    post_res = client.post("/api/auction/state", json=test_state)
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "ok"

def test_tactical_teams():
    response = client.get("/api/tactics/teams")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "teams" in data
    assert data["total"] >= 20

def test_tactical_team_details():
    response = client.get("/api/tactics/team/Atalanta")
    assert response.status_code == 200
    data = response.json()
    assert data["team"] == "Atalanta"
    assert "modulo" in data
    assert "lineup" in data
    assert "rigoristi" in data
    assert "ballottaggi" in data
    assert "roster" in data

def test_matchups_endpoints():
    res_diff = client.get("/api/matchups/difficulty-matrix")
    assert res_diff.status_code == 200
    
    res_team = client.get("/api/matchups/team/Inter")
    assert res_team.status_code == 200
    data = res_team.json()
    assert data["team"] == "Inter"
    assert "team_rating" in data

def test_html_views():
    # Root dashboard
    res_root = client.get("/")
    assert res_root.status_code in (200, 404)
    # Lite app
    res_lite = client.get("/lite")
    assert res_lite.status_code in (200, 404)

def test_lineup_injured_player_penalty():
    from src.api.routers.lineup import calculate_player_expected_score
    
    # Giocatore sano
    healthy_player = {"role": "A", "fm": 8.0, "mv": 6.5, "titolarita": 90, "is_injured": False}
    score_healthy = calculate_player_expected_score(healthy_player)
    assert score_healthy > 5.0
    
    # Giocatore infortunato
    injured_player = {"role": "A", "fm": 8.0, "mv": 6.5, "titolarita": 90, "is_injured": True, "giornate_perse": 5}
    score_injured = calculate_player_expected_score(injured_player)
    assert score_injured == 0.0

def test_auction_bid_advice_injured_discount():
    store = get_data_store()
    injured_players = [p for p in store.players if p.get("is_injured") and p.get("giornate_perse", 0) >= 4]
    if injured_players:
        sample = injured_players[0]
        payload = {
            "player_id": sample["id"],
            "current_budget": 500,
            "total_budget": 1000,
            "league_size": 8
        }
        res = client.post("/api/auction/bid-advice", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "Infortunato" in data["tier"]
        assert "RISCHIO" in data["risk_assessment"]


