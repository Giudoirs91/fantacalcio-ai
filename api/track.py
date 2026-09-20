"""
api/track.py — Vercel Serverless Function (Python)
====================================================
Raccoglie eventi comportamentali anonimi dal frontend.
- Nessun IP salvato, nessun cookie, nessun dato personale → GDPR-safe
- Salva su Vercel Postgres (o Supabase) tramite variabile d'ambiente DATABASE_URL
- Se DATABASE_URL non è configurato, logga solo in console (sviluppo locale)
"""

import json
import os
from datetime import datetime

try:
    import psycopg2
    HAS_DB = True
except ImportError:
    HAS_DB = False


def handler(request):
    """Handler Vercel per POST /api/track"""

    # CORS headers per chiamate dal frontend
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    # Preflight OPTIONS
    if request.method == "OPTIONS":
        return Response("", status=200, headers=cors_headers)

    if request.method != "POST":
        return Response(json.dumps({"error": "Method not allowed"}), status=405, headers=cors_headers)

    try:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        data = json.loads(body)
    except Exception:
        return Response(json.dumps({"error": "Invalid JSON"}), status=400, headers=cors_headers)

    # Estrai solo i campi anonimi consentiti (whitelist esplicita)
    evento = {
        "tipo":      str(data.get("tipo", ""))[:64],        # es. "click_calciatore", "view_pagina"
        "ruolo":     str(data.get("ruolo", ""))[:4],        # es. "A", "C", "D", "P"
        "slot":      str(data.get("slot", ""))[:32],        # es. "1° Slot A"
        "pagina":    str(data.get("pagina", ""))[:256],     # es. "/calciatore/lautaro-martinez"
        "sezione":   str(data.get("sezione", ""))[:64],     # es. "scheda", "dashboard", "portieri"
        "ts":        datetime.utcnow().isoformat()          # timestamp server (mai client-side)
        # ⛔ NESSUN IP — NESSUN USER AGENT — NESSUN COOKIE
    }

    # Salva su DB se configurato
    db_url = os.environ.get("DATABASE_URL")
    if db_url and HAS_DB:
        try:
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS eventi_anonimi (
                    id SERIAL PRIMARY KEY,
                    tipo VARCHAR(64),
                    ruolo VARCHAR(4),
                    slot VARCHAR(32),
                    pagina VARCHAR(256),
                    sezione VARCHAR(64),
                    ts TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute(
                "INSERT INTO eventi_anonimi (tipo, ruolo, slot, pagina, sezione, ts) VALUES (%s, %s, %s, %s, %s, %s)",
                (evento["tipo"], evento["ruolo"], evento["slot"], evento["pagina"], evento["sezione"], evento["ts"])
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[track] DB error: {e}")
    else:
        # Sviluppo locale: logga solo in console
        print(f"[track] Evento (no DB): {evento}")

    return Response(json.dumps({"ok": True}), status=200, headers=cors_headers)


class Response:
    """Minimal response wrapper compatibile con Vercel Python runtime."""
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status_code = status
        self.headers = headers or {}
