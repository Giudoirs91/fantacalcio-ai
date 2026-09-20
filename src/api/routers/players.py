from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from ..dependencies import DataStore, get_data_store
from ..schemas import PlayerListResponse, PlayerDetail

router = APIRouter(prefix="/api/players", tags=["Giocatori"])

@router.get("", response_model=PlayerListResponse)
def list_players(
    query: Optional[str] = Query(None, description="Cerca per nome o squadra"),
    role: Optional[str] = Query(None, description="Filtra per ruolo: P, D, C, A"),
    team: Optional[str] = Query(None, description="Filtra per squadra"),
    min_qta: Optional[float] = Query(None, description="Quotazione minima"),
    max_qta: Optional[float] = Query(None, description="Quotazione massima"),
    min_fm: Optional[float] = Query(None, description="FantaMedia minima"),
    sort_by: str = Query("fvm", description="Campo di ordinamento: fvm, qta, fm, fm_2627, titolarita"),
    order: str = Query("desc", description="'asc' o 'desc'"),
    page: int = Query(1, ge=1, description="Numero di pagina"),
    page_size: int = Query(50, ge=1, le=500, description="Elementi per pagina"),
    store: DataStore = Depends(get_data_store)
):
    descending = (order.lower() == "desc")
    all_matched = store.search_players(
        query=query,
        role=role,
        team=team,
        min_qta=min_qta,
        max_qta=max_qta,
        min_fm=min_fm,
        sort_by=sort_by,
        descending=descending
    )
    
    total = len(all_matched)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_players = all_matched[start_idx:end_idx]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "players": paginated_players
    }

@router.get("/roles-summary")
def get_roles_summary(store: DataStore = Depends(get_data_store)):
    summary = {"P": 0, "D": 0, "C": 0, "A": 0, "total": len(store.players)}
    for p in store.players:
        r = p.get("role", "").upper()
        if r in summary:
            summary[r] += 1
    return summary

@router.get("/top-flop")
def get_top_flop(
    round_num: Optional[int] = Query(None, description="Numero di giornata (1-38)"),
    store: DataStore = Depends(get_data_store)
):
    if not store.top_flop_data:
        return {"status": "no_data", "rounds": {}}
    
    if round_num is not None:
        key = str(round_num)
        if key in store.top_flop_data:
            return {key: store.top_flop_data[key]}
        else:
            raise HTTPException(status_code=404, detail=f"Nessun dato top/flop per giornata {round_num}")
            
    return store.top_flop_data

@router.get("/{player_id}", response_model=Dict[str, Any])
def get_player_details(
    player_id: int,
    store: DataStore = Depends(get_data_store)
):
    player = store.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Giocatore con ID {player_id} non trovato")
    return player
