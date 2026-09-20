import json

def test_multi_league_isolation_concept():
    default_state = {
        "slots": {"P": {"players": []}, "D": {"players": []}, "C": {"players": []}, "A": {"players": []}},
        "rivals": {"R1": {"players": [], "spent": 0}},
        "favorites": [],
        "takenByOthers": []
    }
    
    # Crea Lega 1
    league1 = json.loads(json.dumps(default_state))
    league1["id"] = "league_1"
    league1["name"] = "Lega Amici"
    league1["slots"]["A"]["players"].append({"id": 101, "name": "Lautaro", "paidPrice": 250})
    league1["favorites"].append(101)
    
    # Crea Lega 2 (nuova)
    league2 = json.loads(json.dumps(default_state))
    league2["id"] = "league_2"
    league2["name"] = "Lega Colleghi"
    league2["slots"]["A"]["players"].append({"id": 202, "name": "Vlahovic", "paidPrice": 180})
    league2["favorites"].append(202)
    
    # Verifica che la modifica in Lega 2 non tocchi Lega 1
    assert len(league1["slots"]["A"]["players"]) == 1
    assert league1["slots"]["A"]["players"][0]["name"] == "Lautaro"
    assert len(league2["slots"]["A"]["players"]) == 1
    assert league2["slots"]["A"]["players"][0]["name"] == "Vlahovic"
    assert 202 not in league1["favorites"]
    assert 101 not in league2["favorites"]

if __name__ == "__main__":
    test_multi_league_isolation_concept()
    print("Test isolamento leghe superato con successo!")
