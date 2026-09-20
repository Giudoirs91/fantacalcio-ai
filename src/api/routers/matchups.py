import os
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from ..dependencies import DataStore, get_data_store

router = APIRouter(prefix="/api/matchups", tags=["Matchups & Calendario"])

def load_official_calendar() -> List[Dict[str, Any]]:
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    cal_path = os.path.join(root_dir, "data", "processed", "calendario_serie_a_2026_27.json")
    if not os.path.exists(cal_path):
        cal_path = os.path.join(root_dir, "config", "calendario_serie_a_2026_27.json")
    if os.path.exists(cal_path):
        try:
            with open(cal_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

OFFICIAL_CALENDAR = load_official_calendar()

def calculate_fdr(opponent: str, is_home: bool, team_ratings: Dict[str, Any]) -> int:
    """
    Calcola il Fixture Difficulty Rating (FDR da 1=facile a 5=molto difficile).
    """
    opp_cap = opponent.capitalize()
    opp_rating = team_ratings.get(opp_cap, {})
    tier = opp_rating.get("tier", "Mid")
    
    # Tier mapping: S=5, A=4, B=3, C=2, D=1
    tier_scores = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "Top": 5, "Mid": 3, "Low": 2}
    base = tier_scores.get(tier, 3)
    
    # Casa/Trasferta mod
    if not is_home:
        base += 0.5
    else:
        base -= 0.5
        
    return max(1, min(5, int(round(base))))

@router.get("/calendar")
def get_calendar(giornata: Optional[int] = Query(None, description="Filtra per giornata specifica (1-38)")):
    """Restituisce il calendario ufficiale della Serie A 2026/27 (tutte le 38 giornate o una specifica)."""
    cal = OFFICIAL_CALENDAR if OFFICIAL_CALENDAR else load_official_calendar()
    if giornata is not None:
        found = next((g for g in cal if g.get("giornata") == giornata), None)
        if not found:
            raise HTTPException(status_code=404, detail=f"Giornata {giornata} non trovata.")
        return found
    return {"total_rounds": len(cal), "rounds": cal}

@router.get("/team/{team_name}")
def get_team_schedule(
    team_name: str,
    store: DataStore = Depends(get_data_store)
):
    team_players = [p for p in store.players if p.get("team", "").lower() == team_name.lower()]
    if not team_players:
        raise HTTPException(status_code=404, detail=f"Squadra '{team_name}' non trovata.")

    cal = OFFICIAL_CALENDAR if OFFICIAL_CALENDAR else load_official_calendar()
    team_clean = team_name.lower()

    # Estrai tutte le 38 partite della squadra dal calendario ufficiale
    schedule_38 = []
    for g in cal:
        g_num = g.get("giornata")
        g_date = g.get("date", "")
        for m in g.get("matches", []):
            h = m.get("home", "")
            a = m.get("away", "")
            if h.lower() == team_clean:
                fdr = calculate_fdr(a, True, store.team_ratings)
                schedule_38.append({
                    "giornata": g_num,
                    "date": g_date,
                    "opponent": a,
                    "is_home": True,
                    "fdr": fdr,
                    "match_label": f"{h} vs {a}"
                })
                break
            elif a.lower() == team_clean:
                fdr = calculate_fdr(h, False, store.team_ratings)
                schedule_38.append({
                    "giornata": g_num,
                    "date": g_date,
                    "opponent": h,
                    "is_home": False,
                    "fdr": fdr,
                    "match_label": f"{h} vs {a}"
                })
                break

    # Rileva giornata corrente (es. dopo G4)
    sample_player = next((p for p in team_players if p.get("voti_dettaglio_2627")), None)
    played_rounds = len(sample_player["voti_dettaglio_2627"]) if sample_player and sample_player.get("voti_dettaglio_2627") else 4
    
    upcoming = [m for m in schedule_38 if m["giornata"] > played_rounds][:5]
    avg_fdr_next5 = round(sum(m["fdr"] for m in upcoming) / len(upcoming), 2) if upcoming else 3.0

    rating = store.team_ratings.get(team_name.capitalize(), {})

    return {
        "team": team_name.capitalize(),
        "team_rating": rating,
        "played_rounds": played_rounds,
        "upcoming_matches": upcoming,
        "avg_fdr_next_5": avg_fdr_next5,
        "full_schedule_count": len(schedule_38),
        "schedule": schedule_38
    }

@router.get("/difficulty-matrix")
def get_difficulty_matrix(store: DataStore = Depends(get_data_store)):
    """Restituisce il rating di forza/difficoltà di tutte le 20 squadre con FDR relativo."""
    cal = OFFICIAL_CALENDAR if OFFICIAL_CALENDAR else load_official_calendar()
    teams = list(store.team_ratings.keys())
    
    overview = {}
    for tm in teams:
        tm_matches = []
        for g in cal:
            g_num = g.get("giornata")
            for m in g.get("matches", []):
                h, a = m.get("home", ""), m.get("away", "")
                if h.lower() == tm.lower():
                    tm_matches.append({"giornata": g_num, "opponent": a, "is_home": True, "fdr": calculate_fdr(a, True, store.team_ratings)})
                elif a.lower() == tm.lower():
                    tm_matches.append({"giornata": g_num, "opponent": h, "is_home": False, "fdr": calculate_fdr(h, False, store.team_ratings)})
        
        # Prossime 5 partite (dalla G5 in poi)
        next_5 = [m for m in tm_matches if m["giornata"] >= 5][:5]
        avg_fdr = round(sum(m["fdr"] for m in next_5) / len(next_5), 2) if next_5 else 3.0
        
        overview[tm] = {
            "rating": store.team_ratings.get(tm, {}),
            "next_5_matches": next_5,
            "avg_fdr_next_5": avg_fdr,
            "difficulty_label": "Favorevole" if avg_fdr <= 2.4 else ("Ostico" if avg_fdr >= 3.6 else "Equilibrato")
        }

    return {
        "teams_fdr": overview,
        "team_ratings": store.team_ratings
    }
