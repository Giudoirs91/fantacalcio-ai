import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.server import ConnectionManager, get_lan_ip

def test_connection_manager_state(tmp_path, monkeypatch):
    test_state_file = tmp_path / "test_auction_state.json"
    import src.server as srv
    monkeypatch.setattr(srv, "state_file_path", str(test_state_file))

    mgr = ConnectionManager()
    assert mgr.current_state == {}

    sample_state = {
        "budgetTotal": 1000,
        "budgetSpent": 150,
        "favorites": [101, 102],
        "slots": {"P": {"max": 3, "players": []}}
    }
    mgr.save_state(sample_state)

    assert os.path.exists(str(test_state_file))
    with open(str(test_state_file), "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["budgetSpent"] == 150
    assert loaded["favorites"] == [101, 102]

def test_get_lan_ip():
    ip = get_lan_ip()
    assert isinstance(ip, str)
    assert len(ip.split(".")) == 4
