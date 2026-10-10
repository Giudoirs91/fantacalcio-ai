"""
create_and_send_stats_post.py - Generatore Card Grafica & Post Telegram Statistiche Avanzate
=================================================================================================
Estrae dal database master i migliori calciatori per:
- xG/90 (Gol Attesi)
- xA/90 (Assist Attesi)
- Δ xFM (Overperformance / Potenziale Esplosivo)

Genera una card grafica Instagram/Telegram HD 1080x1350 ed invia il post ufficiale su Telegram.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

HTML_OUT = os.path.join(ROOT_DIR, "data", "processed", "temp_stats_instagram.html")
IMG_OUT = os.path.join(ROOT_DIR, "data", "processed", "social_export", "statistiche_avanzate_instagram_1080x1350.png")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "telegram_config.json")
PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")


def load_top_advanced_stats():
    if not os.path.exists(PLAYERS_PATH):
        print(f"Warning: master players file not found: {PLAYERS_PATH}")
        return [], [], []

    with open(PLAYERS_PATH, 'r', encoding='utf-8') as f:
        players = json.load(f)

    # Filter & Sort Top xG/90
    by_xg = sorted([p for p in players if p.get('xg90_2627') or p.get('xg90')], 
                   key=lambda x: (x.get('xg90_2627') or x.get('xg90') or 0), reverse=True)[:4]

    # Filter & Sort Top xA/90
    by_xa = sorted([p for p in players if p.get('xa90_2627') or p.get('xa90')], 
                   key=lambda x: (x.get('xa90_2627') or x.get('xa90') or 0), reverse=True)[:4]

    # Filter & Sort Top Δ xFM
    by_delta = sorted([p for p in players if p.get('delta_xfm')], 
                      key=lambda x: x.get('delta_xfm', 0), reverse=True)[:4]

    return by_xg, by_xa, by_delta


def generate_html(by_xg, by_xa, by_delta):
    def make_rows_xg(items):
        rows = ""
        for idx, p in enumerate(items, 1):
            val = p.get('xg90_2627') or p.get('xg90') or 0
            mantra = p.get('mantra', 'N/A')
            rows += f"""
            <div class="stat-row">
                <div class="rank">{idx}</div>
                <div class="player-info">
                    <div class="player-name-row">
                        <span class="p-name">{p['name'].upper()}</span>
                        <span class="mantra-tag">Mantra: {mantra}</span>
                    </div>
                    <div class="p-team">{p['team'].upper()} • {p['role']}</div>
                </div>
                <div class="stat-badge cyan">{val:.2f} <span class="stat-unit">xG/90</span></div>
            </div>
            """
        return rows

    def make_rows_xa(items):
        rows = ""
        for idx, p in enumerate(items, 1):
            val = p.get('xa90_2627') or p.get('xa90') or 0
            mantra = p.get('mantra', 'N/A')
            rows += f"""
            <div class="stat-row">
                <div class="rank">{idx}</div>
                <div class="player-info">
                    <div class="player-name-row">
                        <span class="p-name">{p['name'].upper()}</span>
                        <span class="mantra-tag">Mantra: {mantra}</span>
                    </div>
                    <div class="p-team">{p['team'].upper()} • {p['role']}</div>
                </div>
                <div class="stat-badge purple">{val:.2f} <span class="stat-unit">xA/90</span></div>
            </div>
            """
        return rows

    def make_rows_delta(items):
        rows = ""
        for idx, p in enumerate(items, 1):
            val = p.get('delta_xfm', 0)
            mantra = p.get('mantra', 'N/A')
            rows += f"""
            <div class="stat-row">
                <div class="rank">{idx}</div>
                <div class="player-info">
                    <div class="player-name-row">
                        <span class="p-name">{p['name'].upper()}</span>
                        <span class="mantra-tag">Mantra: {mantra}</span>
                    </div>
                    <div class="p-team">{p['team'].upper()} • OVR {p.get('ovr', 0)}</div>
                </div>
                <div class="stat-badge green">+{val:.2f} <span class="stat-unit">Δ xFM</span></div>
            </div>
            """
        return rows

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Statistiche Avanzate Serie A</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Outfit:wght@600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }}
        body {{
            background-color: #05070a;
            width: 1080px;
            height: 1350px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        .canvas {{
            width: 1080px;
            height: 1350px;
            background: radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.12) 0%, transparent 45%),
                        radial-gradient(circle at 20% 80%, rgba(168, 85, 247, 0.12) 0%, transparent 45%),
                        linear-gradient(180deg, #0a0d14 0%, #05070a 100%);
            position: relative;
            padding: 50px 55px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .canvas::before {{
            content: '';
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
        }}

        /* Header */
        .header {{ position: relative; z-index: 10; display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
        .brand {{ font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 900; color: #38bdf8; letter-spacing: 1px; display: flex; align-items: center; gap: 12px; }}
        .brand-dot {{ width: 12px; height: 12px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 12px #38bdf8; }}
        .top-tag {{ background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.35); padding: 8px 20px; border-radius: 99px; color: #c084fc; font-weight: 800; font-size: 15px; letter-spacing: 1.5px; text-transform: uppercase; }}

        .title-block {{ margin-bottom: 30px; }}
        .main-title {{ font-family: 'Outfit', sans-serif; font-size: 48px; font-weight: 900; color: #f8fafc; line-height: 1.15; }}
        .main-subtitle {{ font-size: 20px; color: #94a3b8; margin-top: 6px; font-weight: 500; }}

        /* Sections Grid */
        .sections-container {{ display: flex; flex-direction: column; gap: 24px; position: relative; z-index: 10; flex-grow: 1; }}

        .section-card {{
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 22px 26px;
            backdrop-filter: blur(12px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }}

        .section-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 12px; }}
        .section-icon {{ font-size: 24px; }}
        .section-title {{ font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 800; color: #f1f5f9; letter-spacing: 0.5px; }}

        /* Stat Row */
        .stat-row {{ display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed rgba(255,255,255,0.04); }}
        .stat-row:last-child {{ border-bottom: none; }}

        .rank {{ font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 900; color: #64748b; width: 28px; }}
        .player-info {{ flex-grow: 1; margin-left: 10px; }}
        .player-name-row {{ display: flex; align-items: center; gap: 10px; }}
        .p-name {{ font-weight: 800; font-size: 20px; color: #f8fafc; }}
        .mantra-tag {{ background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); color: #38bdf8; font-size: 13px; font-weight: 700; padding: 3px 10px; border-radius: 8px; }}
        .p-team {{ font-size: 14px; color: #94a3b8; font-weight: 600; margin-top: 3px; }}

        .stat-badge {{ font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 800; padding: 6px 16px; border-radius: 12px; text-align: right; min-width: 130px; }}
        .stat-badge.cyan {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .stat-badge.purple {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }}
        .stat-badge.green {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }}
        .stat-unit {{ font-size: 13px; font-weight: 600; opacity: 0.8; margin-left: 4px; }}

        /* Footer */
        .footer {{
            position: relative;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 16px 28px;
            margin-top: 20px;
        }}
        .footer-url {{ font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 800; color: #38bdf8; letter-spacing: 1px; }}
        .footer-badge {{ font-size: 14px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }}
    </style>
</head>
<body>
    <div class="canvas">
        <div class="header">
            <div class="brand"><div class="brand-dot"></div> FANTA MASTER AI</div>
            <div class="top-tag">SERIE A ADVANCED DATA</div>
        </div>

        <div class="title-block">
            <div class="main-title">STATISTICHE AVANZATE & METRICHE XG</div>
            <div class="main-subtitle">Analisi predittiva sui calciatori con il potenziale più alto della Serie A</div>
        </div>

        <div class="sections-container">
            <!-- Section 1: xG/90 -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🎯</span>
                    <span class="section-title">TOP PERICOLOSITÀ OFFENSIVA (GOL ATTESI xG / 90 MIN)</span>
                </div>
                {make_rows_xg(by_xg)}
            </div>

            <!-- Section 2: xA/90 -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🪄</span>
                    <span class="section-title">TOP RIFINITORI & VISIONE DI GIOCO (ASSIST ATTESI xA / 90 MIN)</span>
                </div>
                {make_rows_xa(by_xa)}
            </div>

            <!-- Section 3: Δ xFM -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">📈</span>
                    <span class="section-title">HIGHEST Δ xFM (POTENZIALE NASCOSTO & SCOMMESSE EXPLOSIVE)</span>
                </div>
                {make_rows_delta(by_delta)}
            </div>
        </div>

        <div class="footer">
            <div class="footer-url">fantamasterai.it/statistiche-serie-a/</div>
            <div class="footer-badge">Database Algoritmo Live</div>
        </div>
    </div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(HTML_OUT), exist_ok=True)
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ HTML Statistiche Avanzate generato: {HTML_OUT}")


def render_image():
    os.makedirs(os.path.dirname(IMG_OUT), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        page.goto(f"file:///{HTML_OUT}")
        page.screenshot(path=IMG_OUT)
        browser.close()
    print(f"✓ Screenshot Statistiche Avanzate 1080x1350 esportato: {IMG_OUT}")
    return IMG_OUT


def build_telegram_caption(by_xg, by_xa, by_delta):
    caption = """📊 STATISTICHE AVANZATE SERIE A: I NUMERI CHE FANNO SBAVARE OGNI FANTALLENATORE! 🤤🔥

L'algoritmo predittivo di FantaMaster AI ha analizzato migliaia di eventi in campo (xG, xA, Key Passes, Duelli vinti e Δ xFM). Ecco chi produce di più in Serie A ed è pronto a regalarvi valanghe di bonus! 👇

🎯 TOP GOL ATTESI (xG / 90 MINUTI):
"""
    for p in by_xg:
        val = p.get('xg90_2627') or p.get('xg90') or 0
        mantra = p.get('mantra', 'N/A')
        caption += f"• {p['name']} ({p['team']}) — {val:.2f} xG/90 [Mantra: {mantra}]\n"

    caption += "\n🪄 TOP ASSIST ATTESI (xA / 90 MINUTI):\n"
    for p in by_xa:
        val = p.get('xa90_2627') or p.get('xa90') or 0
        mantra = p.get('mantra', 'N/A')
        caption += f"• {p['name']} ({p['team']}) — {val:.2f} xA/90 [Mantra: {mantra}]\n"

    caption += "\n📈 POTENZIALE ESPLOSIVO (HIGHEST Δ xFM):\n"
    for p in by_delta:
        val = p.get('delta_xfm', 0)
        mantra = p.get('mantra', 'N/A')
        caption += f"• {p['name']} ({p['team']}) — +{val:.2f} Δ xFM (OVR {p.get('ovr', 0)}) [Mantra: {mantra}]\n"

    caption += """
💡 COME USARE QUESTI DATI:
I calciatori con elevati xG/90 e xA/90 ma che finora hanno portato meno bonus del dovuto sono gli "Sfortunati di lusso": scambiateli o prendeteli subito prima che si sblocchino!

🌐 DATABASE STATISTICHE COMPLETO E COMPARATORE LIVE:
Esplora tutte le metriche avanzate di Serie A su:
👉 https://www.fantamasterai.it/statistiche-serie-a/

#Fantacalcio #StatisticheFantacalcio #SerieA #xG #xA #FantaMasterAI #StatisticheSerieA #Mantra"""
    return caption


def send_to_telegram(image_path, caption):
    if not os.path.exists(CONFIG_PATH):
        print(f"Config Telegram non trovata in {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    token = cfg.get("bot_token")
    chat_id = cfg.get("channel_id")

    if not token or not chat_id:
        print("Bot token o channel ID mancante.")
        return

    print(f"-> Invio al canale Telegram {chat_id}...")

    # 1. Invia la foto HD
    url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
    caption_short = "📊 *STATISTICHE AVANZATE SERIE A (xG, xA & Δ xFM)* 🔥\n\nTutti i numeri predittivi per dominare al fantacalcio!"

    import requests
    with open(image_path, "rb") as img_file:
        res_photo = requests.post(url_photo, data={
            "chat_id": chat_id,
            "caption": caption_short,
            "parse_mode": "Markdown"
        }, files={"photo": img_file})
    print("✓ Risultato invio Foto Telegram:", res_photo.status_code, res_photo.json().get("ok"))

    # 2. Invia il testo completo
    url_msg = f"https://api.telegram.org/bot{token}/sendMessage"
    res_msg = requests.post(url_msg, data={
        "chat_id": chat_id,
        "text": caption,
        "disable_web_page_preview": True
    })
    print("✓ Risultato invio Testo Telegram:", res_msg.status_code, res_msg.json().get("ok"))


def main():
    print("=== [Advanced Stats Publisher] Avvio Generazione Post Statistiche Avanzate ===")
    by_xg, by_xa, by_delta = load_top_advanced_stats()
    generate_html(by_xg, by_xa, by_delta)
    img_path = render_image()
    caption = build_telegram_caption(by_xg, by_xa, by_delta)
    send_to_telegram(img_path, caption)
    print("=== [Advanced Stats Publisher] Post Statistiche pubblicato con successo! ===")


if __name__ == "__main__":
    main()
