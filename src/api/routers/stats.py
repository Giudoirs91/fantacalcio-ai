from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import DataStore, get_data_store
from ..schemas import GKMatrixResponse

router = APIRouter(prefix="/api/stats", tags=["Statistiche & Portieri"])

@router.get("/gk-matrix", response_model=GKMatrixResponse)
def get_gk_matrix(store: DataStore = Depends(get_data_store)):
    raw_data = store.gk_matrix
    matrix = raw_data.get("matrix", {})
    teams = sorted(list(matrix.keys())) if matrix else []

    # Calcola le migliori coppie di alternanza (minimo numero di sovrapposizioni trasferta/casa)
    best_pairs = []
    seen = set()

    for t1 in teams:
        for t2 in teams:
            if t1 >= t2:
                continue
            val = matrix.get(t1, {}).get(t2)
            if val is not None:
                pair_key = f"{t1}_{t2}"
                if pair_key not in seen:
                    seen.add(pair_key)
                    # Rating convenienza: meno sovrapposizioni ci sono, migliore è l'alternanza
                    best_pairs.append({
                        "team_a": t1,
                        "team_b": t2,
                        "malus_sovrapposizione": val,
                        "indice_alternanza": max(0, 38 - (val * 2)),
                        "consiglio": "Ottima coppia" if val <= 6 else ("Discreta" if val <= 10 else "Sconsigliata")
                    })

    best_pairs.sort(key=lambda x: x["malus_sovrapposizione"])

    return {
        "teams": teams,
        "best_pairs": best_pairs[:20],
        "matrix": matrix
    }

@router.get("/teams")
def get_teams_stats(store: DataStore = Depends(get_data_store)):
    team_data: Dict[str, Dict[str, Any]] = {}

    for p in store.players:
        tm = p.get("team", "Sconosciuta")
        if tm not in team_data:
            team_data[tm] = {
                "team": tm,
                "players_count": 0,
                "total_goals": 0,
                "total_assists": 0,
                "avg_mv": 0.0,
                "clean_sheets_gk": 0,
                "rating": store.team_ratings.get(tm, {})
            }
        
        td = team_data[tm]
        td["players_count"] += 1
        td["total_goals"] += (p.get("gol_2627") or p.get("gf") or 0)
        td["total_assists"] += (p.get("assist_2627") or p.get("ass") or 0)
        
        if p.get("role") == "P":
            td["clean_sheets_gk"] += (p.get("clean_sheets_2627") or 0)

    # Calcola medie
    team_list = list(team_data.values())
    team_list.sort(key=lambda x: x["total_goals"], reverse=True)
    return {"teams": team_list}

@router.get("/database-overview")
def get_db_overview(store: DataStore = Depends(get_data_store)):
    total = len(store.players)
    by_role = {"P": 0, "D": 0, "C": 0, "A": 0}
    with_2627_data = 0

    for p in store.players:
        r = p.get("role", "").upper()
        if r in by_role:
            by_role[r] += 1
        if p.get("has_data_2627"):
            with_2627_data += 1

    return {
        "total_players": total,
        "roles_distribution": by_role,
        "players_with_active_season_data": with_2627_data,
        "available_rounds": list(store.top_flop_data.keys()) if store.top_flop_data else [],
        "teams_tracked": len(store.gk_matrix.get("matrix", {}))
    }
