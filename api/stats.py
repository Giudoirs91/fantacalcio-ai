"""
api/stats.py — Vercel Serverless Function (Python)
====================================================
Mostra il riepilogo aggregato degli eventi anonimi raccolti.
Accessibile via GET /api/stats?key=fantamaster2026
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_DB = True
except ImportError:
    HAS_DB = False


def get_db_connection():
    if not HAS_DB:
        return None
    url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
    if not url:
        return None
    try:
        return psycopg2.connect(url)
    except Exception as e:
        print(f"[stats] Errore DB: {e}")
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        # Protezione minima opzionale
        admin_key = os.environ.get("ADMIN_KEY", "fantamaster2026")
        provided_key = query.get("key", [""])[0]

        if provided_key != admin_key:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Chiave admin non valida (?key=...)"}).encode("utf-8"))
            return

        conn = get_db_connection()
        if not conn:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "warning",
                "message": "Database non ancora collegato o non raggiungibile."
            }).encode("utf-8"))
            return

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Totale eventi
                cur.execute("SELECT COUNT(*) as totale FROM eventi_anonimi")
                totale = cur.fetchone()["totale"]

                # Pagine più viste
                cur.execute("""
                    SELECT pagina, COUNT(*) as visite 
                    FROM eventi_anonimi 
                    WHERE tipo = 'pageview' 
                    GROUP BY pagina 
                    ORDER BY visite DESC 
                    LIMIT 15
                """)
                top_pagine = cur.fetchall()

                # Click per ruolo
                cur.execute("""
                    SELECT ruolo, COUNT(*) as click 
                    FROM eventi_anonimi 
                    WHERE ruolo != '' 
                    GROUP BY ruolo 
                    ORDER BY click DESC
                """)
                top_ruoli = cur.fetchall()

                # Ultime attività
                cur.execute("""
                    SELECT tipo, ruolo, slot, pagina, sezione, ts 
                    FROM eventi_anonimi 
                    ORDER BY ts DESC 
                    LIMIT 20
                """)
                ultimi = cur.fetchall()

            conn.close()

            risultato = {
                "totale_eventi": totale,
                "top_pagine": [dict(r) for r in top_pagine],
                "top_ruoli": [dict(r) for r in top_ruoli],
                "ultimi_eventi": [dict(r) for r in ultimi]
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(risultato, default=str).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
