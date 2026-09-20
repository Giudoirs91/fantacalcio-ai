from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Giocatori Schemas ---
class VotoDettaglio(BaseModel):
    giornata: int
    match: Optional[str] = None
    opponent: Optional[str] = None
    is_home: Optional[bool] = None
    voto: Optional[float] = None
    fantavoto: Optional[float] = None
    gf: Optional[int] = 0
    gs: Optional[int] = 0
    ass: Optional[int] = 0
    amm: Optional[int] = 0
    esp: Optional[int] = 0
    bonus_malus_str: Optional[str] = None

class PlayerBase(BaseModel):
    id: int
    name: str
    role: str
    mantra: Optional[str] = None
    team: str
    fvm: Optional[float] = 0.0
    qta: Optional[float] = 0.0
    diff_q: Optional[float] = 0.0
    presenze: Optional[int] = 0
    mv: Optional[float] = 0.0
    fm: Optional[float] = 0.0
    gf: Optional[int] = 0
    gs: Optional[int] = 0
    ass: Optional[int] = 0
    titolarita: Optional[int] = 0
    has_data_2627: Optional[bool] = False
    presenze_2627: Optional[int] = 0
    minuti_2627: Optional[int] = 0
    gol_2627: Optional[int] = 0
    assist_2627: Optional[int] = 0
    mv_2627: Optional[float] = 0.0
    fm_2627: Optional[float] = 0.0
    xfm: Optional[float] = None
    delta_xfm: Optional[float] = None
    prezzo_consigliato: Optional[int] = None
    ovr_score: Optional[float] = None
    tier: Optional[str] = None
    infortunato: Optional[bool] = False
    info_infortunio: Optional[str] = None

class PlayerDetail(PlayerBase):
    voti_dettaglio_2627: Optional[List[Dict[str, Any]]] = []
    advanced_stats: Optional[Dict[str, Any]] = {}
    next_matches: Optional[List[Dict[str, Any]]] = []

class PlayerListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    players: List[Dict[str, Any]]

# --- Lineup & Recommendation Schemas ---
class LineupRequest(BaseModel):
    player_ids: List[int] = Field(..., description="Lista ID dei giocatori presenti in rosa")
    formation: Optional[str] = Field("auto", description="Modulo preferito es. '3-4-3', '4-3-3', '3-5-2' o 'auto'")
    use_defense_modifier: Optional[bool] = Field(True, description="Se True, favorisce il modificatore difesa")
    risk_tolerance: Optional[str] = Field("balanced", description="'conservative', 'balanced', 'aggressive'")

class LineupPlayer(BaseModel):
    id: int
    name: str
    role: str
    team: str
    expected_score: float
    starter: bool
    bench_order: Optional[int] = None
    reason: Optional[str] = None

class LineupResponse(BaseModel):
    formation: str
    expected_team_score: float
    starters: List[LineupPlayer]
    bench: List[LineupPlayer]
    defense_modifier_bonus_expected: Optional[float] = 0.0
    tactical_notes: List[str] = []

# --- Matchup Schemas ---
class MatchupDetail(BaseModel):
    home_team: str
    away_team: str
    home_difficulty: float
    away_difficulty: float
    prediction_home_goals: Optional[float] = None
    prediction_away_goals: Optional[float] = None
    recommended_roles_home: Optional[List[str]] = []
    recommended_roles_away: Optional[List[str]] = []

class RoundMatchupsResponse(BaseModel):
    round_number: int
    matchups: List[Dict[str, Any]]

# --- Stats Schemas ---
class GKMatrixResponse(BaseModel):
    teams: List[str]
    best_pairs: List[Dict[str, Any]]
    matrix: Dict[str, Dict[str, Optional[int]]]

class TeamStat(BaseModel):
    team: str
    goals_scored: int
    goals_conceded: int
    clean_sheets: int
    avg_fantamedia: float
    attack_rating: float
    defense_rating: float

# --- Auction Schemas ---
class BidAdviceRequest(BaseModel):
    player_id: int
    current_budget: int
    total_budget: int = 500
    remaining_slots: Dict[str, int] = Field(default_factory=dict)
    league_size: int = 8

class BidAdviceResponse(BaseModel):
    player_id: int
    name: str
    role: str
    team: str
    target_price: int
    max_bid: int
    tier: str
    risk_assessment: str
    advice: str
