import os
import sys
import socket
import uvicorn

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.api.main import app, get_lan_ip
from src.api.routers.auction import ConnectionManager, auction_manager as manager, state_file_path

def run_server(host: str = "0.0.0.0", port: int = 8000):
    lan_ip = get_lan_ip()
    print("\n" + "="*70)
    print("⚽  FANTA MASTER AI — REST API & LIVE SERVER 2.0")
    print("="*70)
    print(f"📖  Documentazione Swagger API: http://localhost:{port}/docs")
    print(f"💻  Browser su PC:             http://localhost:{port}")
    print(f"📱  App Android / Smartphone:  http://{lan_ip}:{port}")
    print(f"📡  WebSocket Live Sync:       ws://{lan_ip}:{port}/ws")
    print("="*70)
    print("💡  Endpoint REST disponibili per giocatori, formazioni, statistiche e asta!")
    print("Premi CTRL+C per arrestare il server.\n")

    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_server()
