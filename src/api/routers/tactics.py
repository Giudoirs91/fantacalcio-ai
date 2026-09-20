import os
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import DataStore, get_data_store

router = APIRouter(prefix="/api/tactics", tags=["Tattica & Probabili Formazioni 20 Club"])

@router.get("/teams")
def get_tactical_teams(store: DataStore = Depends(get_data_store)):
    """Restituisce l'elenco dei 20 club di Serie A con informazioni tattiche di base."""
    teams_summary = []
    for team_name, data in store.tactical_db.items():
        teams_summary.append({
            "team": team_name,
            "modulo": data.get("modulo", "4-3-3"),
            "allenatore": data.get("all", ""),
            "dif_stars": data.get("dif_stars", 3),
            "att_stars": data.get("att_stars", 3),
            "top": data.get("top", []),
            "sleeper": data.get("sleeper", []),
            "rigoristi": data.get("rigoristi", []),
            "oop_count": len(data.get("oop_players", []))
        })
    teams_summary.sort(key=lambda x: x["team"])
    return {"total": len(teams_summary), "teams": teams_summary}

@router.get("/team/{team_name}")
def get_team_tactical_details(
    team_name: str,
    store: DataStore = Depends(get_data_store)
):
    """Restituisce la formazione titolare, ballottaggi, calci piazzati e rosa completa di un club."""
    # Ricerca case-insensitive
    target_key = None
    for k in store.tactical_db:
        if k.lower() == team_name.lower():
            target_key = k
            break

    if not target_key:
        raise HTTPException(status_code=404, detail=f"Club '{team_name}' non trovato nel database tattico.")

    tac_data = store.tactical_db[target_key]

    # Arricchisci i giocatori della lineup con FVM, quotazione e ID dal master
    enriched_lineup = []
    for slot in tac_data.get("lineup", []):
        slot_copy = dict(slot)
        p_name = slot.get("name")
        # Cerca nel master
        match = next((p for p in store.players if p.get("team", "").lower() == target_key.lower() and p.get("name", "").lower() == p_name.lower()), None)
        if match:
            slot_copy["id"] = match.get("id")
            slot_copy["fvm"] = match.get("fvm")
            slot_copy["qta"] = match.get("qta")
            slot_copy["fm_2627"] = match.get("fm_2627")
        enriched_lineup.append(slot_copy)

    # Recupera tutti i giocatori del club
    club_players = [p for p in store.players if p.get("team", "").lower() == target_key.lower()]
    club_players.sort(key=lambda p: (
        {'P': 0, 'D': 1, 'C': 2, 'A': 3}.get(p.get("role"), 4),
        -(p.get("fvm") or 0)
    ))

    return {
        "team": target_key,
        "modulo": tac_data.get("modulo", "4-3-3"),
        "allenatore": tac_data.get("all", ""),
        "dif_stars": tac_data.get("dif_stars", 3),
        "att_stars": tac_data.get("att_stars", 3),
        "top": tac_data.get("top", []),
        "sleeper": tac_data.get("sleeper", []),
        "rigoristi": tac_data.get("rigoristi", []),
        "punizioni": tac_data.get("punizioni", []),
        "corner": tac_data.get("corner", []),
        "oop_players": tac_data.get("oop_players", []),
        "ballottaggi": tac_data.get("ballottaggi", []),
        "lineup": enriched_lineup,
        "roster": club_players
    }
