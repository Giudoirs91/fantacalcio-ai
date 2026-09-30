import os
import json

def generate_html_story_rich():
    players_path = r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\processed\processed_players_master.json"
    dummy_data = []
    
    if os.path.exists(players_path):
        with open(players_path, 'r', encoding='utf-8') as f:
            all_players = json.load(f)
            best = {}
            for p in all_players:
                r = p.get('role')
                # Cerchiamo solo le vere scommesse/sleeper
                if p.get('is_sleeper', False):
                    # Troviamo il miglior sleeper per ruolo
                    p_xfm = p.get('xfm') or 0
                    best_xfm = best[r].get('xfm') or 0 if r in best else 0
                    if r not in best or p_xfm > best_xfm:
                        best[r] = p
            
            # Se non troviamo 4 sleepers, ripieghiamo sui migliori giocatori
            # con un alto Delta xFM (sottovalutati)
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
                    # Format data
                    dummy_data.append({
                        "role": b.get('role', role),
                        "name": b.get('name', 'Unknown'),
                        "team": b.get('team', 'Unknown'),
                        "ovr": b.get('ovr', 0),
                        "color_class": f"role-{role.lower()}",
                        "xfm": round(b.get('xfm', 0.0), 2),
                        "xg": round(b.get('delta_xfm', 0.0), 2), # Usiamo Delta xFM invece di xG per mostrare l'overperformance
                        "xa": round(b.get('fvm', 0.0), 1),       # Mostriamo la quotazione per far capire che costano poco
                        "titolarita": b.get('titolarita', 100)
                    })

    html_content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Instagram Story Preview - Rich Data</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
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
            background-color: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .story-container {{
            width: 1080px;
            height: 1920px;
            background-color: var(--bg-main);
            position: relative;
            transform: scale(0.4);
            transform-origin: top center;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            padding: 80px 60px;
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
            width: 800px;
            height: 800px;
            background: radial-gradient(circle, rgba(34, 197, 94, 0.15) 0%, transparent 60%);
            top: -200px;
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

        .header {{
            text-align: center;
            margin-bottom: 80px;
            margin-top: 40px;
        }}
        .logo {{
            font-family: 'Outfit', sans-serif;
            font-size: 55px;
            font-weight: 800;
            color: var(--accent-green);
            margin-bottom: 30px;
            letter-spacing: -1px;
            text-shadow: 0 0 20px rgba(34,197,94,0.4);
        }}
        .title {{
            font-family: 'Outfit', sans-serif;
            font-size: 80px;
            font-weight: 900;
            color: var(--text-primary);
            line-height: 1.1;
            text-transform: uppercase;
            letter-spacing: -2px;
        }}
        .subtitle {{
            font-size: 36px;
            color: var(--text-secondary);
            margin-top: 20px;
            font-weight: 500;
        }}

        .players-grid {{
            display: flex;
            flex-direction: column;
            gap: 45px;
        }}

        .player-card {{
            background: var(--bg-card);
            border: 2px solid var(--border-glass);
            border-radius: 32px;
            padding: 40px 50px;
            display: flex;
            align-items: center;
            backdrop-filter: blur(12px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }}
        
        .player-card::before {{
            content: '';
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 12px;
        }}
        .player-card.role-p::before {{ background: var(--role-p); }}
        .player-card.role-d::before {{ background: var(--role-d); }}
        .player-card.role-c::before {{ background: var(--role-c); }}
        .player-card.role-a::before {{ background: var(--role-a); }}

        .player-main {{
            flex: 1;
            margin-left: 20px;
        }}
        .player-name {{
            font-family: 'Outfit', sans-serif;
            font-size: 55px;
            font-weight: 800;
            color: var(--text-primary);
            margin-bottom: 10px;
            letter-spacing: -1px;
        }}
        .player-meta {{
            font-size: 32px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 20px;
            font-weight: 600;
            margin-bottom: 25px;
        }}
        .role-badge {{
            padding: 6px 20px;
            border-radius: 12px;
            font-weight: 800;
            color: #fff;
        }}
        .role-badge.role-p {{ background: var(--role-p); }}
        .role-badge.role-d {{ background: var(--role-d); }}
        .role-badge.role-c {{ background: var(--role-c); }}
        .role-badge.role-a {{ background: var(--role-a); }}

        /* Rich Data Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 20px;
        }}
        .stat-item {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}
        .stat-label {{
            font-size: 20px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 32px;
            font-weight: 800;
            color: var(--text-primary);
        }}
        .stat-value.highlight {{
            color: var(--accent-green);
        }}

        .player-ovr {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: rgba(0,0,0,0.5);
            border: 6px solid;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
            margin-left: 30px;
        }}
        .player-card.role-p .player-ovr {{ border-color: var(--role-p); box-shadow: 0 0 30px rgba(245,158,11,0.2); }}
        .player-card.role-d .player-ovr {{ border-color: var(--role-d); box-shadow: 0 0 30px rgba(16,185,129,0.2); }}
        .player-card.role-c .player-ovr {{ border-color: var(--role-c); box-shadow: 0 0 30px rgba(56,189,248,0.2); }}
        .player-card.role-a .player-ovr {{ border-color: var(--role-a); box-shadow: 0 0 30px rgba(244,63,94,0.2); }}

        .ovr-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 65px;
            font-weight: 900;
            color: var(--text-primary);
            line-height: 1;
        }}
        .ovr-label {{
            font-size: 20px;
            color: var(--text-secondary);
            font-weight: 700;
            letter-spacing: 2px;
        }}

        .footer {{
            margin-top: auto;
            margin-bottom: 40px;
            background: var(--accent-green);
            border-radius: 100px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(34,197,94,0.3);
        }}
        .footer-text {{
            font-family: 'Outfit', sans-serif;
            font-size: 40px;
            font-weight: 800;
            color: #000;
            text-transform: uppercase;
            letter-spacing: -1px;
        }}
    </style>
</head>
<body>
    <div class="story-container">
        <div class="glow-accent"></div>
        <div class="content">
            <div class="header">
                <div class="logo">⚽ Fanta Master AI</div>
                <div class="title">LE SCOMMESSE<br>DELL'ALGORITMO</div>
                <div class="subtitle">Giocatori sottovalutati da schierare subito</div>
            </div>
            
            <div class="players-grid">
"""
    for p in dummy_data:
        html_content += f"""
                <div class="player-card {p['color_class']}">
                    <div class="player-main">
                        <div class="player-name">{p['name'].upper()}</div>
                        <div class="player-meta">
                            <span class="role-badge {p['color_class']}">{p['role']}</span>
                            <span>{p['team'].upper()}</span>
                        </div>
                        
                        <!-- Extra Data (xFM, xG, xA, Titolarità) -->
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-label">xFM</span>
                                <span class="stat-value highlight">{p['xfm']}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Tit.</span>
                                <span class="stat-value">{p['titolarita']}%</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Δ xFM</span>
                                <span class="stat-value highlight">+{p['xg']}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Costo</span>
                                <span class="stat-value">{p['xa']}</span>
                            </div>
                        </div>

                    </div>
                    <div class="player-ovr">
                        <div class="ovr-value">{p['ovr']}</div>
                        <div class="ovr-label">OVR</div>
                    </div>
                </div>
"""

    html_content += """
            </div>
            
            <div class="footer">
                <div class="footer-text">SCOPRI TUTTI I DATI SU FANTAMASTERAI.IT</div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    out_path = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\b4ede5df-8782-4a51-b06d-3ff5ccc2c412\instagram_preview_website_style_rich.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generato {out_path}")

if __name__ == '__main__':
    generate_html_story_rich()
