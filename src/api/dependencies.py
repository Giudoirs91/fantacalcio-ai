import os
import json
from typing import Dict, List, Any, Optional

class DataStore:
    _instance = None

    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = os.path.join(self.root_dir, "data")
        self.config_dir = os.path.join(self.root_dir, "config")
        
        self.players: List[Dict[str, Any]] = []
        self.players_by_id: Dict[int, Dict[str, Any]] = {}
        self.gk_matrix: Dict[str, Any] = {}
        self.top_flop_data: Dict[str, Any] = {}
        self.team_ratings: Dict[str, Any] = {}
        self.tactical_db: Dict[str, Any] = {}
        
        self.load_all()

    @classmethod
    def get_instance(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = DataStore()
        return cls._instance

    def load_all(self):
        # 1. Carica Master Players
        players_path = os.path.join(self.data_dir, "processed", "processed_players_master.json")
        if not os.path.exists(players_path):
            players_path = os.path.join(self.root_dir, "processed_players_master.json")
            
        if os.path.exists(players_path):
            try:
                with open(players_path, "r", encoding="utf-8") as f:
                    self.players = json.load(f)
                    self.players_by_id = {p.get("id"): p for p in self.players if p.get("id") is not None}
                print(f"[DataStore] Caricati {len(self.players)} giocatori in memoria.")
            except Exception as e:
                print(f"[DataStore] Errore caricamento players: {e}")

        # 2. Carica GK Matrix
        gk_path = os.path.join(self.data_dir, "processed", "gk_matrix_2026_27.json")
        if not os.path.exists(gk_path):
            gk_path = os.path.join(self.root_dir, "gk_matrix_2026_27.json")
        if os.path.exists(gk_path):
            try:
                with open(gk_path, "r", encoding="utf-8") as f:
                    self.gk_matrix = json.load(f)
            except Exception as e:
                print(f"[DataStore] Errore caricamento GK Matrix: {e}")

        # 3. Carica Top / Flop
        top_flop_path = os.path.join(self.data_dir, "processed", "top_flop_rounds.json")
        if os.path.exists(top_flop_path):
            try:
                with open(top_flop_path, "r", encoding="utf-8") as f:
                    self.top_flop_data = json.load(f)
            except Exception as e:
                print(f"[DataStore] Errore caricamento Top/Flop: {e}")

        # 4. Carica Team Ratings & Tactical DB
        tr_path = os.path.join(self.config_dir, "team_ratings.json")
        if os.path.exists(tr_path):
            try:
                with open(tr_path, "r", encoding="utf-8") as f:
                    self.team_ratings = json.load(f)
            except Exception as e:
                print(f"[DataStore] Errore team ratings: {e}")

        tac_path = os.path.join(self.config_dir, "tactical_db.json")
        if os.path.exists(tac_path):
            try:
                with open(tac_path, "r", encoding="utf-8") as f:
                    self.tactical_db = json.load(f)
            except Exception as e:
                print(f"[DataStore] Errore tactical DB: {e}")

    def get_player(self, player_id: int) -> Optional[Dict[str, Any]]:
        return self.players_by_id.get(player_id)

    def search_players(
        self,
        query: Optional[str] = None,
        role: Optional[str] = None,
        team: Optional[str] = None,
        min_qta: Optional[float] = None,
        max_qta: Optional[float] = None,
        min_fm: Optional[float] = None,
        sort_by: str = "fvm",
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        results = self.players

        if query:
            q = query.lower().strip()
            results = [p for p in results if q in p.get("name", "").lower() or q in p.get("team", "").lower()]

        if role:
            r = role.upper().strip()
            results = [p for p in results if p.get("role", "").upper() == r]

        if team:
            t = team.lower().strip()
            results = [p for p in results if p.get("team", "").lower() == t]

        if min_qta is not None:
            results = [p for p in results if (p.get("qta") or 0) >= min_qta]

        if max_qta is not None:
            results = [p for p in results if (p.get("qta") or 0) <= max_qta]

        if min_fm is not None:
            results = [p for p in results if (p.get("fm_2627") or p.get("fm") or 0) >= min_fm]

        # Sorting
        def sort_key(p):
            val = p.get(sort_by)
            if val is None:
                return -999999 if descending else 999999
            return val

        results = sorted(results, key=sort_key, reverse=descending)
        return results

def get_data_store() -> DataStore:
    return DataStore.get_instance()
