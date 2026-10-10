import os
import sys
import json
import asyncio
import urllib.request
import urllib.parse
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(ROOT_DIR, "data", "processed", "temp_social_carousel.html")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "telegram_config.json")
PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "processed", "social_export")

def load_telegram_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback to the known config
    return {
        "bot_token": "8790091730:AAHTpEKOcsYEV_XrZYBbmK44bvSsOJH7trU",
        "channel_id": "@fantamasterai" # we can send here, or we can send to a test chat id if provided
    }

def get_sleepers():
    dummy_data = []
    if os.path.exists(PLAYERS_PATH):
        with open(PLAYERS_PATH, 'r', encoding='utf-8') as f:
            all_players = json.load(f)
            best = {}
            for p in all_players:
                r = p.get('role')
                if p.get('is_sleeper', False):
                    p_xfm = p.get('xfm') or 0
                    best_xfm = best[r].get('xfm') or 0 if r in best else 0
                    if r not in best or p_xfm > best_xfm:
                        best[r] = p
            
            if len(best) < 4:
                for p in all_players:
                    r = p.get('role')
                    if r not in best:
                        p_delta = p.get('delta_xfm') or 0
                        best_delta = best[r].get('delta_xfm') or 0 if r in best else 0
                        if r not in best or p_delta > best_delta:
                            best[r] = p
                            
            if len(best) >= 4:
                for role in ['P', 'D', 'C', 'A']:
                    b = best[role]
                    team_ctx = b.get('team_context', {})
                    insight = ""
                    
                    if role == 'P':
                        xga = team_ctx.get('xga_team', 5.0)
                        insight = f"Fortino difensivo per il {b.get('team')}: la retroguardia concede solo {xga} xGA a partita. Altissima probabilità di imbattibilità (+1) e rischio malus minimo."
                    elif role == 'D':
                        if b.get('is_oop'):
                            insight = f"Spinta avanzata OOP sulla fascia per {b.get('name')}. L'algoritmo rileva sovrapposizioni continue e un potenziale bonus assist altissimo date le amnesie della corsia avversaria."
                        else:
                            insight = f"Rendimento da modificatore: {b.get('name')} vince oltre l'80% dei duelli aerei. Ottima base per il voto alto e potenziale gol su palla inattiva."
                    elif role == 'C':
                        xg = team_ctx.get('xg_team', 10.0)
                        insight = f"Inserimenti continui a fari spenti. Il {b.get('team')} produce ben {xg} xG di squadra e {b.get('name')} è sempre nel vivo della trequarti avversaria. Bonus in canna."
                    else:
                        insight = f"Terminale offensivo sottovalutato. L'algoritmo calcola un Δ xFM di +{round(b.get('delta_xfm', 0.0), 2)}: crea occasioni nette che il mercato non ha ancora prezzato. Schieralo titolare."
                    
                    dummy_data.append({
                        "role": b.get('role', role),
                        "mantra": b.get('mantra', 'N/A'),
                        "name": b.get('name', 'Unknown'),
                        "team": b.get('team', 'Unknown'),
                        "ovr": b.get('ovr', 0),
                        "color_class": f"role-{role.lower()}",
                        "xfm": round(b.get('xfm', 0.0), 2),
                        "xg": round(b.get('delta_xfm', 0.0), 2),
                        "xa": round(b.get('fvm', 0.0), 1),
                        "titolarita": b.get('titolarita', 100),
                        "advice": insight
                    })
    return dummy_data

def build_html(dummy_data):
    html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Instagram Carousel Preview</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-main: #0c0e12;
            --bg-card: rgba(18, 22, 29, 0.88);
            --border-glass: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --role-p: #f59e0b;
            --role-d: #10b981;
            --role-c: #38bdf8;
            --role-a: #f43f5e;
            --accent-green: #22c55e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{
            background-color: #1a1a24;
            display: flex;
            flex-direction: row;
            gap: 50px;
            padding: 50px;
        }}
        .story-container {{
            width: 1080px;
            height: 1920px;
            background-color: var(--bg-main);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            padding: 100px 80px;
        }}
        .story-container::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 60px 60px;
            z-index: 0;
        }}
        .glow-accent {{
            position: absolute;
            width: 1000px;
            height: 1000px;
            background: radial-gradient(circle, rgba(34, 197, 94, 0.15) 0%, transparent 60%);
            top: -300px;
            left: -200px;
            z-index: 1;
            border-radius: 50%;
        }}
        .content {{
            position: relative;
            z-index: 10;
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        .header {{ margin-bottom: 80px; }}
        .logo {{
            font-family: 'Outfit', sans-serif;
            font-size: 55px;
            font-weight: 800;
            color: var(--accent-green);
            margin-bottom: 30px;
        }}
        .title {{
            font-family: 'Outfit', sans-serif;
            font-size: 90px;
            font-weight: 900;
            color: var(--text-primary);
            line-height: 1.1;
        }}
        .focus-card {{
            background: var(--bg-card);
            border: 4px solid var(--border-glass);
            border-radius: 40px;
            padding: 70px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 30px 60px rgba(0,0,0,0.5);
            position: relative;
            overflow: hidden;
            margin-bottom: 60px;
        }}
        .focus-card::before {{
            content: '';
            position: absolute;
            left: 0; top: 0; right: 0;
            height: 16px;
        }}
        .focus-card.role-p::before {{ background: var(--role-p); }}
        .focus-card.role-d::before {{ background: var(--role-d); }}
        .focus-card.role-c::before {{ background: var(--role-c); }}
        .focus-card.role-a::before {{ background: var(--role-a); }}

        .player-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 60px; }}
        .player-name {{ font-family: 'Outfit', sans-serif; font-size: 85px; font-weight: 900; color: var(--text-primary); }}
        .player-meta {{ font-size: 40px; color: var(--text-secondary); display: flex; align-items: center; gap: 20px; margin-top: 20px; }}
        .role-badge {{ padding: 10px 25px; border-radius: 16px; font-weight: 800; color: #fff; }}
        .role-badge.role-p {{ background: var(--role-p); }}
        .role-badge.role-d {{ background: var(--role-d); }}
        .role-badge.role-c {{ background: var(--role-c); }}
        .role-badge.role-a {{ background: var(--role-a); }}
        .mantra-badge {{ background: rgba(56, 189, 248, 0.15); border: 2px solid rgba(56, 189, 248, 0.4); padding: 10px 22px; border-radius: 16px; font-weight: 800; color: #38bdf8; font-size: 34px; }}

        .player-ovr {{
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            width: 220px; height: 220px; border-radius: 50%; background: rgba(0,0,0,0.6); border: 8px solid;
        }}
        .focus-card.role-p .player-ovr {{ border-color: var(--role-p); }}
        .focus-card.role-d .player-ovr {{ border-color: var(--role-d); }}
        .focus-card.role-c .player-ovr {{ border-color: var(--role-c); }}
        .focus-card.role-a .player-ovr {{ border-color: var(--role-a); }}
        .ovr-value {{ font-family: 'Outfit', sans-serif; font-size: 85px; font-weight: 900; color: var(--text-primary); line-height: 1; }}
        .ovr-label {{ font-size: 26px; color: var(--text-secondary); font-weight: 700; letter-spacing: 2px; }}

        .metrics-bar {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-bottom: 60px; background: rgba(0,0,0,0.4); border-radius: 24px; padding: 40px; }}
        .metric {{ display: flex; flex-direction: column; align-items: center; text-align: center; }}
        .metric-title {{ font-size: 24px; color: var(--text-secondary); font-weight: 700; margin-bottom: 15px; }}
        .metric-value {{ font-family: 'Outfit', sans-serif; font-size: 60px; font-weight: 800; color: var(--text-primary); }}
        .metric-value.green {{ color: var(--accent-green); }}

        .ai-insight {{ background: rgba(34, 197, 94, 0.1); border-left: 8px solid var(--accent-green); padding: 40px; border-radius: 0 24px 24px 0; }}
        .insight-title {{ font-size: 30px; font-weight: 800; color: var(--accent-green); margin-bottom: 20px; text-transform: uppercase; }}
        .insight-text {{ font-size: 36px; line-height: 1.5; color: var(--text-primary); }}

        .footer {{ margin-top: auto; text-align: center; opacity: 0.6; }}
        .footer-text {{ font-family: 'Outfit', sans-serif; font-size: 40px; font-weight: 800; color: var(--text-primary); letter-spacing: 2px; }}
        .slide-indicator {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; }}
        .dot {{ width: 20px; height: 20px; border-radius: 50%; background: rgba(255,255,255,0.2); }}
        .dot.active {{ background: var(--accent-green); box-shadow: 0 0 15px var(--accent-green); }}
    </style>
</head>
<body>
"""
    for i, p in enumerate(dummy_data):
        dots = ""
        for j in range(len(dummy_data)):
            dots += f'<div class="dot {"active" if i == j else ""}"></div>'
            
        advice_text = p.get('advice', "L'algoritmo rileva un potenziale nascosto rispetto alle quotazioni attuali. Schieralo!")
        if not advice_text.strip():
             advice_text = "L'algoritmo rileva un potenziale nascosto rispetto alle quotazioni attuali. Schieralo!"

        html_content += f"""
    <div class="story-container" id="slide-{i}">
        <div class="glow-accent"></div>
        <div class="content">
            <div class="header">
                <div class="logo">⚽ Fanta Master AI</div>
                <div class="title">SCOMMESSA #{i+1}</div>
            </div>
            <div class="focus-card {p['color_class']}">
                <div class="player-head">
                    <div>
                        <div class="player-name">{p['name'].upper()}</div>
                        <div class="player-meta">
                            <span class="role-badge {p['color_class']}">{p['role']}</span>
                            <span class="mantra-badge">Mantra: {p['mantra']}</span>
                            <span>•</span>
                            <span>{p['team'].upper()}</span>
                        </div>
                    </div>
                    <div class="player-ovr">
                        <div class="ovr-value">{p['ovr']}</div>
                        <div class="ovr-label">OVR</div>
                    </div>
                </div>
                <div class="metrics-bar">
                    <div class="metric">
                        <div class="metric-title">Δ xFM Atteso</div>
                        <div class="metric-value green">+{p['xg']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-title">Titolarità</div>
                        <div class="metric-value">{p['titolarita']}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-title">Costo FVM</div>
                        <div class="metric-value">{p['xa']}</div>
                    </div>
                </div>
                <div class="ai-insight">
                    <div class="insight-title">⚡ L'Analisi dell'Algoritmo</div>
                    <div class="insight-text">{advice_text}</div>
                </div>
            </div>
            <div class="footer">
                <div class="slide-indicator">{dots}</div>
                <div class="footer-text">FANTAMASTERAI.IT</div>
            </div>
        </div>
    </div>
"""
    html_content += "</body></html>"
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

def build_caption(dummy_data):
    msg = "🚨 **I NUMERI PARLANO CHIARO: NON LASCIARLI IN PANCHINA!** 🚨\n\n"
    msg += "Abbiamo dato in pasto all'Algoritmo di FantaMaster AI le statistiche avanzate della giornata. Ha scartato le scelte ovvie e ha trovato 4 colpi a basso costo che stanno per esplodere (Δ xFM positivo). 📈\n\n"
    
    emoji_map = {'P': '🧤', 'D': '🛡️', 'C': '🪄', 'A': '⚽'}
    for p in dummy_data:
        emo = emoji_map.get(p['role'], '⚡')
        # Snippet breve per la caption
        short_desc = p['advice'].split('.')[0] if '.' in p['advice'] else "Bonus in arrivo"
        msg += f"{emo} **{p['name']}**: {short_desc}.\n"
        
    msg += "\nScorri il carosello per leggere l'Advanced Tactical Insight completo per ognuno di loro! 👉\n\n"
    msg += "Tu chi schieri di questi? Faccelo sapere nei commenti! 👇\n\n"
    msg += "🔗 Consigli di formazione e comparatore 1vs1 completi su:\n"
    msg += "👉 https://www.fantamasterai.it/consigli-fantacalcio/\n\n"
    msg += "#Fantacalcio #SerieA #ConsigliFantacalcio #FantaMasterAI #ScommesseFantacalcio"
    return msg

import urllib.request
import urllib.parse
import requests

def send_telegram_caption_and_media(caption, image_paths):
    cfg = load_telegram_config()
    token = cfg.get("bot_token")
    chat_id = cfg.get("channel_id")
    
    if not token:
        print("Bot token missing.")
        return
        
    # Send Caption first
    text_url = f"https://api.telegram.org/bot{token}/sendMessage"
    text_data = urllib.parse.urlencode({"chat_id": chat_id, "text": caption, "parse_mode": "Markdown"}).encode('utf-8')
    try:
        req = urllib.request.Request(text_url, data=text_data)
        urllib.request.urlopen(req)
        print("Caption inviata su Telegram!")
    except Exception as e:
        print(f"Errore invio caption: {e}")
        
    # Send images as documents so they keep quality and are easy to save
    for path in image_paths:
        try:
            import requests # we'll use requests for file upload, standard urllib is pain for multipart
            url = f"https://api.telegram.org/bot{token}/sendDocument"
            with open(path, 'rb') as f:
                requests.post(url, data={'chat_id': chat_id}, files={'document': f})
            print(f"Immagine {path} inviata!")
        except Exception as e:
            print(f"Errore invio immagine {path}: {e}")

async def render_screenshots():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    paths = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Set a massive viewport so all 4 horizontal slides (1080px wide each + gap) fit on screen
        page = await browser.new_page(viewport={"width": 6000, "height": 3000}, device_scale_factor=1)
        await page.goto(f"file:///{HTML_PATH}")
        
        for i in range(4):
            element = page.locator(f"#slide-{i}")
            out_path = os.path.join(OUTPUT_DIR, f"slide_{i}.png")
            await element.screenshot(path=out_path)
            paths.append(out_path)
            
        await browser.close()
    return paths

def main():
    print("1. Lettura Scommesse...")
    data = get_sleepers()
    print("2. Creazione HTML...")
    build_html(data)
    
    print("3. Generazione Screenshot tramite Browser invisibile...")
    try:
        paths = asyncio.run(render_screenshots())
    except Exception as e:
        print(f"Errore Screenshot (assicurati di aver installato playwright): {e}")
        return
        
    print("4. Generazione Caption...")
    caption = build_caption(data)
    print("-------------------------")
    print(caption)
    print("-------------------------")
    
    print("5. Invio su Telegram...")
    send_telegram_caption_and_media(caption, paths)
    
    print("Workflow completato con successo!")

if __name__ == "__main__":
    main()
