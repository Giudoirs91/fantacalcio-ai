import os
import json
import socket
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import get_data_store
from .routers import players, lineup, stats, matchups, auction, tactics

def get_lan_ip() -> str:
    """Rileva l'IP locale della scheda di rete Wi-Fi / Ethernet"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-carica i dati all'avvio del server
    store = get_data_store()
    print(f"[API Server] Avviato con successo. Giocatori in memoria: {len(store.players)}")
    yield

app = FastAPI(
    title="Fanta Master AI API",
    description="Backend REST API e WebSocket per analisi predittiva, formazioni e asta del Fantacalcio Serie A",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware per permettere al frontend (React/Vite, PWA, mobile) di effettuare richieste
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusione dei Router Modulari
app.include_router(players.router)
app.include_router(lineup.router)
app.include_router(stats.router)
app.include_router(matchups.router)
app.include_router(auction.router)
app.include_router(tactics.router)

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
html_dashboard_path = os.path.join(root_dir, "Dashboard_Fanta_1000.html")
modern_index_path = os.path.join(root_dir, "web", "index.html")

@app.get("/api/health", tags=["Sistema"])
def health_check():
    store = get_data_store()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "players_loaded": len(store.players),
        "lan_ip": get_lan_ip()
    }

@app.get("/api/info", tags=["Sistema"])
def get_server_info():
    store = get_data_store()
    return {
        "app": "Fanta Master AI",
        "status": "online",
        "lan_ip": get_lan_ip(),
        "connected_clients": len(auction.auction_manager.active_connections),
        "players_count": len(store.players)
    }

# Endpoint WebSocket per sincronizzazione Real-Time
@app.websocket("/ws")
@app.websocket("/ws/auction")
async def websocket_endpoint(websocket: WebSocket):
    await auction.auction_manager.connect(websocket)
    # Invia immediatamente lo stato attuale al client appena connesso
    if auction.auction_manager.current_state:
        await websocket.send_text(json.dumps({
            "type": "INIT_STATE",
            "state": auction.auction_manager.current_state
        }))

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("type")

            if action == "STATE_UPDATE":
                new_state = payload.get("state", {})
                source_id = payload.get("source", "")
                await auction.auction_manager.broadcast_state(new_state, sender=websocket, source_id=source_id)

            elif action == "GET_STATE":
                req_league_id = payload.get("league_id") or payload.get("leagueId")
                target_state = auction.auction_manager.get_league_state(req_league_id)
                await websocket.send_text(json.dumps({
                    "type": "INIT_STATE",
                    "state": target_state
                }))

            elif action == "PING":
                await websocket.send_text(json.dumps({"type": "PONG"}))

    except WebSocketDisconnect:
        auction.auction_manager.disconnect(websocket)
        await auction.auction_manager.broadcast_peer_count()
    except Exception:
        auction.auction_manager.disconnect(websocket)
        await auction.auction_manager.broadcast_peer_count()

from fastapi.staticfiles import StaticFiles

static_dir = os.path.join(root_dir, "web", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve la Dashboard completa con tutti i 18 moduli su /
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def get_dashboard():
    if os.path.exists(html_dashboard_path):
        with open(html_dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return HTMLResponse("<h1>Dashboard non ancora compilata. Esegui 'python main.py --build'.</h1>", status_code=404)

# Serve la visuale leggera SPA su /lite
@app.get("/lite", response_class=HTMLResponse, include_in_schema=False)
async def get_lite_app():
    if os.path.exists(modern_index_path):
        with open(modern_index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return HTMLResponse("<h1>App Lite non trovata.</h1>", status_code=404)
