import os
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from ..dependencies import DataStore, get_data_store
from ..schemas import BidAdviceRequest, BidAdviceResponse

router = APIRouter(prefix="/api/auction", tags=["Asta Live & Sincronizzazione"])

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
state_file_path = os.path.join(root_dir, "data", "auction_state.json")

def get_state_file_path():
    try:
        import src.server as srv
        if hasattr(srv, "state_file_path") and srv.state_file_path:
            return srv.state_file_path
    except Exception:
        pass
    return state_file_path

# Gestione Connessioni WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.current_state: Dict[str, Any] = self.load_saved_state()
        self.leagues_state: Dict[str, Any] = self.current_state.get("_leagues", {}) if isinstance(self.current_state, dict) else {}

    def load_saved_state(self) -> Dict[str, Any]:
        fpath = get_state_file_path()
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                print(f"[AuctionManager] Errore lettura auction_state.json: {e}")
        return {}

    def get_league_state(self, league_id: Optional[str] = None) -> Dict[str, Any]:
        if league_id and league_id in self.leagues_state:
            return self.leagues_state[league_id]
        if league_id and isinstance(self.current_state, dict) and (self.current_state.get("leagueId") == league_id or self.current_state.get("id") == league_id):
            return self.current_state
        return self.current_state

    def save_state(self, state: Dict[str, Any]):
        try:
            if not isinstance(self.current_state, dict):
                self.current_state = {}
            if not isinstance(self.leagues_state, dict):
                self.leagues_state = {}
            
            league_id = state.get("leagueId") or state.get("id") or "league_default"
            self.leagues_state[league_id] = state
            
            self.current_state = dict(state)
            self.current_state["_leagues"] = self.leagues_state

            fpath = get_state_file_path()
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(self.current_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AuctionManager] Errore salvataggio auction_state.json: {e}")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.broadcast_peer_count()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_peer_count(self):
        count = len(self.active_connections)
        msg = json.dumps({"type": "PEERS_COUNT", "count": count})
        for conn in list(self.active_connections):
            try:
                await conn.send_text(msg)
            except Exception:
                pass

    async def broadcast_state(self, state: Dict[str, Any], sender: WebSocket = None, source_id: str = ""):
        self.save_state(state)
        msg = json.dumps({
            "type": "STATE_UPDATE",
            "state": state,
            "source": source_id
        })
        for conn in list(self.active_connections):
            if conn != sender:
                try:
                    await conn.send_text(msg)
                except Exception:
                    pass

auction_manager = ConnectionManager()

@router.get("/state")
def get_auction_state(league_id: Optional[str] = None):
    return auction_manager.get_league_state(league_id)

@router.post("/state")
async def update_auction_state(state: Dict[str, Any]):
    await auction_manager.broadcast_state(state, sender=None, source_id="REST_API")
    return {"status": "ok", "synced_to": len(auction_manager.active_connections)}

@router.post("/bid-advice", response_model=BidAdviceResponse)
def get_bid_advice(
    req: BidAdviceRequest,
    store: DataStore = Depends(get_data_store)
):
    player = store.get_player(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Giocatore {req.player_id} non trovato")

    role = player.get("role", "C")
    name = player.get("name", "")
    team = player.get("team", "")
    ovr = float(player.get("ovr", 65))
    is_injured = player.get("is_injured", False)
    giornate_perse = int(player.get("giornate_perse", 0))
    fragilita_badge = str(player.get("fragilita_badge", "bassa")).lower()
    
    # Prezzo consigliato calibrato dal modello quantitativo (base 1000 CR)
    base_prezzo_cons = float(player.get("prezzo_cons") or player.get("fvm_1000") or player.get("fvm", 10))
    base_max_bid = float(player.get("max_bid") or (base_prezzo_cons * 1.15))

    # Scaling budget proporzionale
    budget_scale = req.total_budget / 1000.0
    
    # Se il budget richiesto è 500 e abbiamo fvm_500 esatto
    if abs(req.total_budget - 500) < 50 and player.get("fvm_500"):
        target = float(player.get("fvm_500"))
        max_bid_raw = target * 1.15
    else:
        target = base_prezzo_cons * budget_scale
        max_bid_raw = base_max_bid * budget_scale

    # Impatto Infortunio / Fragilità
    if is_injured:
        if giornate_perse >= 10:
            target = max(1.0, target * 0.25)
            max_bid_raw = max(1.0, target * 1.10)
        elif giornate_perse >= 4:
            target = max(1.0, target * 0.60)
            max_bid_raw = max(1.0, target * 1.15)
        else:
            target = max(1.0, target * 0.85)

    target_price = max(1, int(round(target)))
    max_bid = min(req.current_budget, max(target_price, int(round(max_bid_raw))))
    max_bid = max(1, max_bid)

    # Assegnazione Tier e Valutazione del Rischio
    slot_fascia = player.get("slot_fascia") or f"{player.get('slot_num', 4)}° Slot"
    
    if is_injured and giornate_perse >= 10:
        tier = f"Infortunato Grave ({slot_fascia})"
        risk = "ALTO RISCHIO: Lunga degenza (stop prolungato). Evitare o prendere a 1 CR per il girone di ritorno."
    elif is_injured:
        tier = f"Infortunato ({slot_fascia})"
        risk = f"RISCHIO MODERATO: Stop previsto ({giornate_perse} giornate). Ottima opportunità per comprarlo a forte sconto."
    elif fragilita_badge == "alta":
        tier = f"Top Fragile ({slot_fascia})"
        risk = "RISCHIO FISICO: Giocatore propenso a stop frequenti. Acquistare SOLO in coppia con il compagno di reparto/sostituto."
    elif target_price >= int(round(120 * budget_scale)):
        tier = f"Top Assoluto ({slot_fascia})"
        risk = "INVESTIMENTO PRIMARIO: Pilastro della rosa, rilancia con decisione fino al Max Bid."
    elif target_price >= int(round(45 * budget_scale)):
        tier = f"Titolare di Lusso ({slot_fascia})"
        risk = "RENDIMENTO ELEVATO: Ottimo rapporto titolarità/bonus. Rilancia fino a prezzo congruo."
    elif target_price >= int(round(15 * budget_scale)):
        tier = f"Regolare / Copertura ({slot_fascia})"
        risk = "BUON RAPPORTO QUALITÀ/PREZZO: Evita corse al rialzo emotive oltre il Max Bid."
    else:
        tier = f"Scommessa / Low Cost ({slot_fascia})"
        risk = "LOW COST: Ideale per completamento rosa a 1 o pochi crediti."

    advice_tag = player.get("ai_advice") or player.get("consiglio") or ""
    advice_extra = f" [{advice_tag}]" if advice_tag else ""
    advice = f"Per {name} ({role} - {team}{advice_extra}), prezzo target calcolato: ~{target_price} CR. Offerta massima consigliata: {max_bid} CR."

    return BidAdviceResponse(
        player_id=req.player_id,
        name=name,
        role=role,
        team=team,
        target_price=target_price,
        max_bid=max_bid,
        tier=tier,
        risk_assessment=risk,
        advice=advice
    )
