"""
api/track.py — Vercel Serverless Function (Python)
====================================================
Raccoglie eventi comportamentali anonimi dal frontend.
- Nessun IP salvato, nessun cookie, nessun dato personale -> GDPR-safe al 100%
- Salva su Vercel Postgres (POSTGRES_URL o DATABASE_URL)
- Compatibile con il runtime standard Vercel Python (BaseHTTPRequestHandler)
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from datetime import datetime

try:
    import psycopg2
    HAS_DB = True
except ImportError:
    HAS_DB = False


def get_db_connection():
    if not HAS_DB:
        return None
    # Vercel Postgres imposta POSTGRES_URL o DATABASE_URL
    url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
    if not url:
        return None
    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        print(f"[track] Errore connessione DB: {e}")
        return None


def init_db(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS eventi_anonimi (
                    id BIGSERIAL PRIMARY KEY,
                    tipo VARCHAR(64) NOT NULL,
                    ruolo VARCHAR(8),
                    slot VARCHAR(32),
                    pagina VARCHAR(256),
                    sezione VARCHAR(64),
                    ts TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_eventi_tipo ON eventi_anonimi(tipo);
                CREATE INDEX IF NOT EXISTS idx_eventi_pagina ON eventi_anonimi(pagina);
                CREATE INDEX IF NOT EXISTS idx_eventi_ts ON eventi_anonimi(ts);
            """)
        conn.commit()
    except Exception as e:
        print(f"[track] Errore init table: {e}")
        conn.rollback()


class handler(BaseHTTPRequestHandler):
    """Handler standard ufficiale Vercel Python Serverless"""

    def _set_cors_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors_headers(200)

    def do_GET(self):
        """Health check endpoint"""
        self._set_cors_headers(200)
        self.wfile.write(json.dumps({"status": "ok", "db_connected": HAS_DB}).encode("utf-8"))

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._set_cors_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
            return

        evento = {
            "tipo": str(data.get("tipo", "view_pagina"))[:64],
            "ruolo": str(data.get("ruolo", ""))[:8],
            "slot": str(data.get("slot", ""))[:32],
            "pagina": str(data.get("pagina", ""))[:256],
            "sezione": str(data.get("sezione", ""))[:64],
            "ts": datetime.utcnow().isoformat()
        }

        conn = get_db_connection()
        if conn:
            try:
                init_db(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO eventi_anonimi (tipo, ruolo, slot, pagina, sezione, ts) VALUES (%s, %s, %s, %s, %s, %s)",
                        (evento["tipo"], evento["ruolo"], evento["slot"], evento["pagina"], evento["sezione"], evento["ts"])
                    )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[track] DB insert error: {e}")
        else:
            print(f"[track] Evento registrato (log console): {evento}")

        self._set_cors_headers(200)
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
