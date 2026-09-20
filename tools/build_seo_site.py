import os
import sys
import re
import json
import math
import shutil
import unicodedata
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
DIST_DIR = os.path.join(ROOT_DIR, "dist")

MASTER_PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
INJURIES_HISTORY_PATH = os.path.join(ROOT_DIR, "config", "injuries_history.json")
TACTICAL_DB_PATH = os.path.join(ROOT_DIR, "config", "tactical_db.json")
GK_MATRIX_PATH = os.path.join(ROOT_DIR, "data", "processed", "gk_matrix_2026_27.json")
DASHBOARD_HTML_PATH = os.path.join(ROOT_DIR, "Dashboard_Fanta_1000.html")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
CALENDAR_DATA = []
if os.path.exists(CALENDAR_PATH):
    try:
        with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
            CALENDAR_DATA = json.load(f)
    except Exception as e:
        print(f"Warning loading calendar: {e}")


BASE_URL = "https://fantamasterai.it"

def slugify(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def clean_html(text):
    if not text:
        return ""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def generate_radar_chart_svg(player):
    role = player.get("role", "C")
    
    # Valori calcolati o stimati
    if role == 'P':
        axes = [
            {'label': '% Parate', 'pct': min(98, max(25, int(float(player.get('save_pct_2627') or 74)))), 'raw': f"{player.get('save_pct_2627') or 74}%"},
            {'label': 'Gol Evitati', 'pct': min(95, max(20, int(50 + float(player.get('goals_prevented_2627') or 0.8) * 15))), 'raw': f"{player.get('goals_prevented_2627') or '+0.8'}"},
            {'label': 'Clean Sheets', 'pct': min(95, max(30, int(float(player.get('clean_sheets_2627') or 1) * 35))), 'raw': f"{player.get('clean_sheets_2627') or 1} CS"},
            {'label': 'Media Voto', 'pct': min(96, max(35, int((float(player.get('mv_2627') or player.get('mv') or 6.1) - 5.5) * 60))), 'raw': f"{float(player.get('mv_2627') or player.get('mv') or 6.1):.2f}"},
            {'label': 'Presa / Uscite', 'pct': 72, 'raw': '78%'},
            {'label': 'FantaMedia', 'pct': min(98, max(30, int((float(player.get('fm_2627') or player.get('fm') or 5.5) - 4.5) * 45))), 'raw': f"{float(player.get('fm_2627') or player.get('fm') or 5.5):.2f}"}
        ]
    elif role == 'D':
        axes = [
            {'label': 'Duelli Vinti %', 'pct': min(95, max(35, int(float(player.get('duels_won_pct_2627') or 64)))), 'raw': f"{player.get('duels_won_pct_2627') or 64}%"},
            {'label': 'Palle Recuperate', 'pct': min(96, max(30, int(float(player.get('recuperi_2627') or 14) * 5))), 'raw': f"{player.get('recuperi_2627') or 14}"},
            {'label': 'Intercettazioni', 'pct': 74, 'raw': '1.8/90'},
            {'label': 'Proiezione Offensiva', 'pct': min(92, max(20, int((float(player.get('xg_2627') or player.get('xg_2526') or 0.2) + float(player.get('xa_2627') or 0.1)) * 40))), 'raw': f"{float(player.get('xg_2627') or 0.2):.2f} xG"},
            {'label': 'Disciplina', 'pct': min(95, max(40, 95 - int(float(player.get('amm_2627') or 0) * 15))), 'raw': f"{player.get('amm_2627') or 0} Amm"},
            {'label': 'Media Voto (MV)', 'pct': min(98, max(30, int((float(player.get('mv_2627') or player.get('mv') or 6.0) - 5.5) * 60))), 'raw': f"{float(player.get('mv_2627') or player.get('mv') or 6.0):.2f}"}
        ]
    elif role == 'C':
        axes = [
            {'label': 'Rifinitura (xA/90)', 'pct': min(96, max(25, int(float(player.get('xa90_2627') or player.get('xa90_2526') or 0.18) * 300))), 'raw': f"{player.get('xa90_2627') or 0.18}"},
            {'label': 'Finalizzazione (xG)', 'pct': min(95, max(20, int(float(player.get('xg_2627') or player.get('xg_2526') or 0.25) * 45))), 'raw': f"{player.get('xg_2627') or 0.25}"},
            {'label': 'Grandi Occasioni', 'pct': min(94, max(25, int(float(player.get('big_chances_created_2627') or 2) * 22))), 'raw': f"{player.get('big_chances_created_2627') or 2}"},
            {'label': 'Palle Recuperate', 'pct': min(95, max(30, int(float(player.get('recuperi_2627') or 12) * 5))), 'raw': f"{player.get('recuperi_2627') or 12}"},
            {'label': '1vs1 & Dribbling', 'pct': min(96, max(30, int(float(player.get('won_contest_2627') or 1.2) * 45))), 'raw': f"{player.get('won_contest_2627') or 1.2}/90"},
            {'label': 'FantaMedia (FM)', 'pct': min(98, max(30, int((float(player.get('fm_2627') or player.get('fm') or 6.2) - 5.5) * 45))), 'raw': f"{float(player.get('fm_2627') or player.get('fm') or 6.2):.2f}"}
        ]
    else: # Attaccanti
        axes = [
            {'label': 'Finalizzazione (xG/90)', 'pct': min(98, max(30, int(float(player.get('xg90_2627') or player.get('xg90_2526') or 0.45) * 160))), 'raw': f"{player.get('xg90_2627') or 0.45}"},
            {'label': 'Pericolosita (xGOT)', 'pct': min(98, max(30, int(float(player.get('xgot_2627') or 1.2) * 50))), 'raw': f"{player.get('xgot_2627') or 1.2}"},
            {'label': 'Rifinitura (xA/90)', 'pct': min(95, max(20, int(float(player.get('xa90_2627') or player.get('xa90_2526') or 0.15) * 350))), 'raw': f"{player.get('xa90_2627') or 0.15}"},
            {'label': 'Grandi Occasioni', 'pct': min(96, max(30, int(float(player.get('big_chances_created_2627') or 2) * 25))), 'raw': f"{player.get('big_chances_created_2627') or 2}"},
            {'label': '1vs1 & Dribbling', 'pct': min(96, max(30, int(float(player.get('won_contest_2627') or 1.5) * 42))), 'raw': f"{player.get('won_contest_2627') or 1.5}/90"},
            {'label': 'FantaMedia (FM)', 'pct': min(99, max(35, int((float(player.get('fm_2627') or player.get('fm') or 6.8) - 5.5) * 40))), 'raw': f"{float(player.get('fm_2627') or player.get('fm') or 6.8):.2f}"}
        ]

    size = 350
    center = size / 2
    radius = 95
    num = len(axes)
    step = (math.pi * 2) / num

    circles = ''
    for level in [0.25, 0.50, 0.75, 1.0]:
        pts = [f"{center + radius * level * math.cos(i * step - math.pi / 2):.1f},{center + radius * level * math.sin(i * step - math.pi / 2):.1f}" for i in range(num)]
        stroke_dash = 'stroke-dasharray="3,3"' if level == 0.5 else ''
        circles += f'<polygon points="{" ".join(pts)}" fill="none" stroke="rgba(255,255,255,{0.18 if level == 0.5 else 0.08})" stroke-width="1" {stroke_dash} />'

    poly_pts = []
    lines = ''
    labels = ''
    for i, a in enumerate(axes):
        angle = i * step - math.pi / 2
        lines += f'<line x1="{center}" y1="{center}" x2="{center + radius * math.cos(angle):.1f}" y2="{center + radius * math.sin(angle):.1f}" stroke="rgba(255,255,255,0.12)" stroke-width="1" />'
        
        pct_clamped = max(15, min(96, a['pct']))
        r = (radius * pct_clamped) / 100
        poly_pts.append(f"{center + r * math.cos(angle):.1f},{center + r * math.sin(angle):.1f}")

        label_r = radius + 22
        lx = center + label_r * math.cos(angle)
        ly = center + label_r * math.sin(angle)
        anchor = 'start' if math.cos(angle) > 0.3 else ('end' if math.cos(angle) < -0.3 else 'middle')
        labels += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="#cbd5e1" font-size="9" font-weight="700">{a["label"]}</text>'
        labels += f'<text x="{lx:.1f}" y="{ly + 11:.1f}" text-anchor="{anchor}" fill="#38bdf8" font-size="9.5" font-weight="800">P{a["pct"]} <tspan fill="#94a3b8" font-size="8">({a["raw"]})</tspan></text>'

    role_colors = {'P': '#f59e0b', 'D': '#10b981', 'C': '#38bdf8', 'A': '#f43f5e'}
    poly_color = role_colors.get(role, '#38bdf8')

    poly = f'<polygon points="{" ".join(poly_pts)}" fill="{poly_color}" fill-opacity="0.25" stroke="{poly_color}" stroke-width="2.5" />'
    svg = f"""<svg viewBox="0 0 {size} 320" style="width:100%;max-width:350px;display:block;margin:0 auto;">{circles}{lines}{poly}{labels}</svg>"""
    return svg

def generate_seo_css():
    # Carica la base CSS completa di dashboard.css per riutilizzare tutte le classi del player modal
    css_path = os.path.join(ROOT_DIR, "web", "css", "dashboard.css")
    base_dashboard_css = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            base_dashboard_css = f.read()

    extra_seo_css = """
/* SEO Specific Page Wrappers */
body {
    background-color: #0b0f19 !important;
    color: #f8fafc;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.55;
    padding-bottom: 60px;
}

/* Unified App Header Styles across all pages */
.app-header-unified {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: rgba(12, 14, 18, 0.96);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    width: 100%;
    box-sizing: border-box;
}

.header-main-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 18px;
    gap: 16px;
    max-width: 1200px;
    margin: 0 auto;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 6px 12px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.brand-badge:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(245, 158, 11, 0.4);
    box-shadow: 0 0 16px rgba(245, 158, 11, 0.15);
}

.brand-icon {
    font-size: 16px;
}

.brand-title {
    font-family: system-ui, -apple-system, sans-serif;
    font-weight: 900;
    font-size: 13.5px;
    color: #fff;
    letter-spacing: 0.5px;
}

.brand-sub {
    font-size: 10px;
    font-weight: 800;
    color: #f59e0b;
    margin-left: 3px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.nav-btn-icon {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #cbd5e1;
    padding: 6px 11px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.nav-btn-icon:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #fff;
}

.header-nav-groups {
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-dropdown {
    position: relative;
}

.nav-group-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #cbd5e1;
    padding: 7px 13px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
}

.nav-group-btn:hover, .nav-group-btn.active {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.22);
    color: #fff;
}

.nav-dropdown-menu {
    display: none;
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    min-width: 250px;
    background: rgba(18, 22, 29, 0.98);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.85);
    z-index: 10000;
}

.nav-dropdown:hover .nav-dropdown-menu,
.nav-dropdown:focus-within .nav-dropdown-menu {
    display: block;
}

.nav-dropdown-menu a, .nav-dropdown-menu .dropdown-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    color: #cbd5e1;
    text-decoration: none;
    font-size: 12px;
    font-weight: 600;
    border-radius: 7px;
    transition: all 0.15s ease;
    white-space: nowrap;
}

.nav-dropdown-menu a:hover, .nav-dropdown-menu .dropdown-item:hover {
    background: rgba(0, 242, 254, 0.12);
    color: #00f2fe;
}

.nav-dropdown-menu .dropdown-header {
    padding: 6px 12px 4px 12px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.5px;
}

.nav-dropdown-menu .dropdown-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 5px 0;
}

.coming-soon-pill {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: #fbbf24;
    font-size: 9px;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 9999px;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    margin-left: 6px;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

.header-squad-pill {
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(0, 242, 254, 0.06);
    border: 1px solid rgba(0, 242, 254, 0.25);
    padding: 6px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.header-squad-pill:hover {
    border-color: #00f2fe;
    background: rgba(0, 242, 254, 0.15);
}

.pill-credits {
    font-size: 12.5px;
    font-weight: 800;
    color: #00f2fe;
}

.mobile-subnav {
    display: none;
}

@media (max-width: 820px) {
    .header-nav-groups { display: none !important; }
    .header-main-row { padding: 6px 12px !important; }
    .mobile-subnav {
        display: flex !important;
        background: rgba(15, 23, 42, 0.98);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 6px 10px;
        gap: 8px;
        overflow-x: auto;
        white-space: nowrap;
    }
    .mobile-subnav a {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #cbd5e1;
        text-decoration: none;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .mobile-subnav a:hover, .mobile-subnav a.active {
        background: rgba(56, 189, 248, 0.2);
        border-color: rgba(56, 189, 248, 0.5);
        color: #38bdf8;
    }
}

.site-container {
    max-width: 1140px;
    margin: 0 auto;
    padding: 0 16px;
}

/* Tabs Navigation in SEO Page */
.seo-tab-nav {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 20px 0 16px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
    overflow-x: auto;
}
.seo-tab-btn {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #94a3b8;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.seo-tab-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.08);
}
.seo-tab-btn.active {
    background: rgba(56, 189, 248, 0.15);
    border-color: rgba(56, 189, 248, 0.4);
    color: #38bdf8;
}

.seo-tab-pane {
    display: block;
    margin-bottom: 24px;
}

/* Breadcrumbs */
.breadcrumbs {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    color: #94a3b8;
    padding: 16px 0 6px 0;
}
.breadcrumbs a { color: #94a3b8; text-decoration: none; }
.breadcrumbs a:hover { color: #38bdf8; }

/* Tactical set piece chips */
.tactical-piece-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 14px 16px;
}
.tactical-piece-card h4 {
    font-size: 12px;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.cta-banner {
    background: linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(6, 182, 212, 0.25) 100%);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    padding: 28px;
    text-align: center;
    margin: 32px 0 20px 0;
}
.cta-banner h2 { font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 8px; }
.cta-banner p { font-size: 14px; color: #cbd5e1; margin-bottom: 18px; max-width: 640px; margin-left: auto; margin-right: auto; }

.site-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 24px 0;
    margin-top: 40px;
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
}
"""
    return base_dashboard_css + "\n" + extra_seo_css

def render_unified_header(rel_path=""):
    return f"""
    <!-- Unified App Header -->
    <header class="app-header-unified">
        <div class="header-main-row">
            <!-- LEFT: BRANDING & HOME -->
            <div class="header-left">
                <a href="{rel_path}index.html" class="brand-badge" style="text-decoration:none;" title="Fanta Master AI — Portale Statistico Serie A 2026/27">
                    <span class="brand-icon">⚡</span>
                    <div>
                        <div class="brand-title">FANTA MASTER AI</div>
                        <div class="brand-sub">Portale Statistico</div>
                    </div>
                </a>

                <a href="{rel_path}index.html" class="nav-btn-icon" style="text-decoration:none;" title="Torna al Listone &amp; Statistiche">
                    🏠 Listone
                </a>
            </div>

            <!-- CENTER: DROPDOWNS -->
            <nav class="header-nav-groups">
                <!-- 1. STATISTICHE & LISTONE -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupTactics">
                        <span>📈</span> Statistiche &amp; Listone <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}index.html" class="dropdown-item">📊 Statistiche Serie A &amp; xG</a>
                        <a href="{rel_path}index.html" class="dropdown-item">📋 Tabellone &amp; Listone Calciatori</a>
                        <a href="{rel_path}griglia-portieri/index.html" class="dropdown-item">🧤 Griglia Portieri 38/38</a>
                    </div>
                </div>

                <!-- 2. AI & CONSIGLI -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAi">
                        <span>🧠</span> AI &amp; Consigli <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}infortunati-serie-a/index.html" class="dropdown-item">🩺 Infortunati &amp; Tempi di Recupero</a>
                        <a href="{rel_path}rigoristi-serie-a/index.html" class="dropdown-item">🎯 Rigoristi &amp; Calci Piazzati</a>
                        <div class="dropdown-divider"></div>
                        <a href="{rel_path}index.html" class="dropdown-item">🎯 Chi Schierare Prossima Giornata</a>
                        <a href="{rel_path}index.html" class="dropdown-item">🧠 5 Squadre Perfette AI</a>
                        <a href="{rel_path}index.html" class="dropdown-item">🔮 Gemme &amp; Sleeper AI</a>
                    </div>
                </div>

                <!-- 3. ASTA & MERCATO -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAuction">
                        <span>📊</span> Asta &amp; Mercato <span class="coming-soon-pill">In Arrivo</span> <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}index.html" class="dropdown-item">📋 Tabellone &amp; Listone Completo</a>
                    </div>
                </div>
            </nav>

            <!-- RIGHT: LIVE STATUS & APP LAUNCH -->
            <div class="header-right">
                <a href="{rel_path}index.html" class="header-squad-pill" style="text-decoration:none;" title="Apri Dashboard &amp; Rosa">
                    <span style="font-size:13px;">📋</span>
                    <span class="pill-credits">Dashboard Live</span>
                </a>
            </div>
        </div>
        <!-- MOBILE SUBNAV -->
        <nav class="mobile-subnav">
            <a href="{rel_path}index.html">📊 Listone</a>
            <a href="{rel_path}infortunati-serie-a/index.html">🩺 Infortuni</a>
            <a href="{rel_path}rigoristi-serie-a/index.html">🎯 Rigoristi</a>
            <a href="{rel_path}griglia-portieri/index.html">🧤 Portieri</a>
        </nav>
    </header>
    """


from tools.seo_player_template import generate_player_page

def generate_injuries_pillar(players, injuries_db):
    active_players = [p for p in players if p.get("is_injured")]
    
    rows = ""
    for p in active_players:
        name = p.get("name", "")
        team = p.get("team", "")
        role = p.get("role", "C")
        motivo = p.get("infortunio_motivo", "Infortunio")
        rientro = p.get("infortunio_rientro", "Da definire")
        tier = p.get("fragility_tier", "STABILE")
        
        team_inj = injuries_db.get(team, {})
        hist_entry = team_inj.get(name, {})
        full_name = hist_entry.get("tm_name", name)
        slug = slugify(full_name)
        
        tier_color = "#f87171" if tier in ["CRISTALLO", "FRAGILE"] else ("#fbbf24" if tier == "ATTENZIONE" else "#34d399")
        
        rows += f"""
        <tr>
            <td>
                <a href="../calciatore/{slug}/index.html" style="font-weight:700;color:#fff;">{clean_html(full_name)}</a>
                <div style="font-size:11px;color:#94a3b8;">{clean_html(team)} &bull; {role}</div>
            </td>
            <td><strong style="color:#fff;">{clean_html(motivo)}</strong></td>
            <td style="color:#fbbf24;font-weight:700;">{clean_html(rientro)}</td>
            <td><span class="injury-tier-chip" style="border:1px solid {tier_color};color:{tier_color};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:800;">{tier}</span></td>
            <td>
                <a href="../calciatore/{slug}/index.html" class="btn-launch-app" style="padding:4px 10px;font-size:11px;">Scheda Completa &rarr;</a>
            </td>
        </tr>
        """
        
    meta_title = "Infortunati Serie A 2026/27: Tabella Tempi di Recupero & Rientri | Fanta Master AI"
    meta_desc = "Tabella sempre aggiornata di tutti i calciatori infortunati in Serie A 2026/27: diagnosi medica, tempi di recupero stimati, data di rientro e consigli per l'asta Fantacalcio."
    page_url = f"{BASE_URL}/infortunati-serie-a/"

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="stylesheet" href="../css/seo.css">
</head>
<body>
{render_unified_header('../')}

    <main class="site-container">
        <nav class="breadcrumbs">
            <a href="../index.html">Home</a> <span>/</span> <span style="color:#fff;">Infortunati Serie A</span>
        </nav>

        <section class="player-hero-card" style="display:block;">
            <h1 style="font-size:24px;font-weight:800;color:#fff;margin-bottom:6px;">Infortunati Serie A 2026/27: Tabella Tempi di Recupero & Rientri</h1>
            <p style="font-size:13.5px;color:#cbd5e1;">
                Monitoraggio clinico in tempo reale di tutti i calciatori attualmente indisponibili nei 20 club di Serie A, verificato con Transfermarkt e bollettini medici.
            </p>
        </section>

        <section class="content-section" style="background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px;">
            <div class="table-responsive">
                <table class="seo-table">
                    <thead>
                        <tr>
                            <th>Calciatore</th>
                            <th>Diagnosi Infortunio</th>
                            <th>Rientro Stimato</th>
                            <th>Fragilità</th>
                            <th>Dettagli</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>

        <section class="cta-banner">
            <h2>Non farti cogliere impreparato all'Asta!</h2>
            <p>Utilizza l'algoritmo predittivo di Fanta Master AI per calcolare la penalità esatta sul prezzo d'asta per ogni infortunato.</p>
            <a href="../app.html" class="btn-launch-app" style="font-size:14px;padding:10px 22px;">Vai alla Dashboard Live 🚀</a>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Storico Infortuni Ufficiale Serie A</p>
        </div>
    </footer>
    <script src="../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def generate_rigoristi_pillar(tactical_db):
    rows = ""
    for team, data in sorted(tactical_db.items()):
        all_coach = data.get("all", "Allenatore")
        modulo = data.get("modulo", "4-3-3")
        rigoristi = data.get("rigoristi", [])
        punizioni = data.get("punizioni", [])
        corner = data.get("corner", [])
        
        rig_str = ", ".join([f"<strong style='color:#fbbf24;'>{r}</strong>" if i == 0 else r for i, r in enumerate(rigoristi)]) if rigoristi else "Non specificato"
        pun_str = ", ".join(punizioni) if punizioni else "-"
        cor_str = ", ".join(corner) if corner else "-"
        
        rows += f"""
        <tr>
            <td><strong style="font-size:14px;color:#fff;">{clean_html(team)}</strong><br><small style="color:#94a3b8;">{clean_html(all_coach)} ({modulo})</small></td>
            <td><span>{rig_str}</span></td>
            <td><span style="color:#cbd5e1;">{clean_html(pun_str)}</span></td>
            <td><span style="color:#94a3b8;">{clean_html(cor_str)}</span></td>
        </tr>
        """
        
    meta_title = "Rigoristi Serie A 2026/27: Tabella Gerarchie Rigori, Punizioni e Corner | Fanta Master AI"
    meta_desc = "Tutti i rigoristi ufficiali della Serie A 2026/27 club per club: primo, secondo e terzo tiratore dal dischetto, specialisti delle punizioni e battitori di corner."
    page_url = f"{BASE_URL}/rigoristi-serie-a/"

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="stylesheet" href="../css/seo.css">
</head>
<body>
{render_unified_header('../')}

    <main class="site-container">
        <nav class="breadcrumbs">
            <a href="../index.html">Home</a> <span>/</span> <span style="color:#fff;">Rigoristi Serie A</span>
        </nav>

        <section class="player-hero-card" style="display:block;">
            <h1 style="font-size:24px;font-weight:800;color:#fff;margin-bottom:6px;">Rigoristi Serie A 2026/27: Gerarchie Rigori e Calci Piazzati</h1>
            <p style="font-size:13.5px;color:#cbd5e1;">
                La guida definitiva ai tiratori dal dischetto e specialisti da fermo di tutte le 20 squadre di Serie A per l'asta del Fantacalcio.
            </p>
        </section>

        <section class="content-section" style="background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px;">
            <div class="table-responsive">
                <table class="seo-table">
                    <thead>
                        <tr>
                            <th>Squadra & Allenatore</th>
                            <th>Rigoristi Designati (1°, 2°, 3°)</th>
                            <th>Specialisti Punizioni</th>
                            <th>Battitori Corner</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Rigoristi Ufficiali Serie A</p>
        </div>
    </footer>
    <script src="../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def generate_gk_pillar(gk_matrix_data):
    meta_title = "Griglia Portieri Fantacalcio 2026/27: Tabella Incroci Casa e Trasferta | Fanta Master AI"
    meta_desc = "Calcola le migliori coppie di portieri per l'asta del Fantacalcio 2026/27: tabella incroci perfetta casa e trasferta per non subire mai due trasferte consecutive."
    page_url = f"{BASE_URL}/griglia-portieri/"
    
    couples = gk_matrix_data.get("couples", [])
    rows = ""
    for c in couples[:25]:
        t1 = c.get("team1")
        t2 = c.get("team2")
        score = c.get("score", 0)
        conflicts = c.get("conflicts", 0)
        rows += f"""
        <tr>
            <td><strong style="color:#fff;">{clean_html(t1)}</strong> + <strong style="color:#fff;">{clean_html(t2)}</strong></td>
            <td style="color:#10b981;font-weight:800;text-align:center;">{conflicts} contemporaneità</td>
            <td style="text-align:center;"><span style="color:#38bdf8;font-weight:700;">{score} pt</span></td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="stylesheet" href="../css/seo.css">
</head>
<body>
{render_unified_header('../')}

    <main class="site-container">
        <nav class="breadcrumbs">
            <a href="../index.html">Home</a> <span>/</span> <span style="color:#fff;">Griglia Portieri Serie A</span>
        </nav>

        <section class="player-hero-card" style="display:block;">
            <h1 style="font-size:24px;font-weight:800;color:#fff;margin-bottom:6px;">Griglia Portieri Fantacalcio 2026/27: Migliori Incroci Calendario</h1>
            <p style="font-size:13.5px;color:#cbd5e1;">
                La matrice completa di alternanza casa/trasferta a 38 giornate per costruire la coppia di portieri a minor numero di gol subiti.
            </p>
        </section>

        <section class="content-section" style="background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:20px;">
            <h2 class="section-title" style="font-size:16px;font-weight:800;color:#fff;margin-bottom:12px;">🏆 Top Incroci Perfetti (0 o 1 sola contemporaneità fuori casa)</h2>
            <div class="table-responsive">
                <table class="seo-table">
                    <thead>
                        <tr>
                            <th>Accoppiata Squadre</th>
                            <th style="text-align:center;">Gare Contemporanee</th>
                            <th style="text-align:center;">Punteggio Incrocio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Griglia Portieri Serie A</p>
        </div>
    </footer>
    <script src="../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def build_all():
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"=== [SEO Site Builder] Avvio Generazione Pagine Statiche Google ===")
    
    # 1. Crea dist pulita
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)
    
    css_dir = os.path.join(DIST_DIR, "css")
    os.makedirs(css_dir, exist_ok=True)
    with open(os.path.join(css_dir, "seo.css"), "w", encoding="utf-8") as f:
        f.write(generate_seo_css())
        
    # Carica Dati
    with open(MASTER_PLAYERS_PATH, "r", encoding="utf-8") as f:
        players = json.load(f)
    with open(INJURIES_HISTORY_PATH, "r", encoding="utf-8") as f:
        injuries_db = json.load(f)
    with open(TACTICAL_DB_PATH, "r", encoding="utf-8") as f:
        tactical_db = json.load(f)
    with open(GK_MATRIX_PATH, "r", encoding="utf-8") as f:
        gk_matrix_data = json.load(f)

    # 2. Copia JS e asset
    js_dir = os.path.join(DIST_DIR, "js")
    os.makedirs(js_dir, exist_ok=True)
    web_js_dir = os.path.join(ROOT_DIR, "web", "js")
    if os.path.exists(web_js_dir):
        for f in os.listdir(web_js_dir):
            if f.endswith(".js"):
                shutil.copy(os.path.join(web_js_dir, f), os.path.join(js_dir, f))

    # 2b. Copia l'applicazione interattiva principale in dist/app.html e dist/index.html
    if os.path.exists(DASHBOARD_HTML_PATH):
        with open(DASHBOARD_HTML_PATH, "r", encoding="utf-8") as f:
            dash_content = f.read()
        if "</body" in dash_content:
            dash_content = dash_content.replace("</body>", '    <script src="/js/tracker.js" defer></script>\n</body>')
        with open(os.path.join(DIST_DIR, "app.html"), "w", encoding="utf-8") as f:
            f.write(dash_content)
        with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(dash_content)
        print("  ✓ App interattiva clonata con tracker in dist/app.html e dist/index.html")

    # 3. Genera le 532 pagine calciatore complete
    calciatori_dir = os.path.join(DIST_DIR, "calciatore")
    os.makedirs(calciatori_dir, exist_ok=True)
    
    sitemap_urls = [
        f"{BASE_URL}/",
        f"{BASE_URL}/app.html",
        f"{BASE_URL}/infortunati-serie-a/",
        f"{BASE_URL}/rigoristi-serie-a/",
        f"{BASE_URL}/griglia-portieri/"
    ]
    
    player_count = 0
    seen_slugs = set()
    for p in players:
        slug, p_html = generate_player_page(p, injuries_db, tactical_db, CALENDAR_DATA, BASE_URL)
        if not slug or slug in seen_slugs:
            slug = f"{slug}-{p.get('id')}"
        seen_slugs.add(slug)
        
        p_dir = os.path.join(calciatori_dir, slug)
        os.makedirs(p_dir, exist_ok=True)
        with open(os.path.join(p_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(p_html)
            
        sitemap_urls.append(f"{BASE_URL}/calciatore/{slug}/")
        player_count += 1

    print(f"  ✓ Generate {player_count} schede calciatore complete di grafica, Radar SVG, FotMob e Infortuni!")

    # 4. Genera Pagine Pillar
    inj_dir = os.path.join(DIST_DIR, "infortunati-serie-a")
    os.makedirs(inj_dir, exist_ok=True)
    with open(os.path.join(inj_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_injuries_pillar(players, injuries_db))
    print("  ✓ Generata pagina Pillar: dist/infortunati-serie-a/index.html")

    rig_dir = os.path.join(DIST_DIR, "rigoristi-serie-a")
    os.makedirs(rig_dir, exist_ok=True)
    with open(os.path.join(rig_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_rigoristi_pillar(tactical_db))
    print("  ✓ Generata pagina Pillar: dist/rigoristi-serie-a/index.html")

    gk_dir = os.path.join(DIST_DIR, "griglia-portieri")
    os.makedirs(gk_dir, exist_ok=True)
    with open(os.path.join(gk_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_gk_pillar(gk_matrix_data))
    print("  ✓ Generata pagina Pillar: dist/griglia-portieri/index.html")

    # 5. Genera Sitemap XML
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sitemap_urls:
        prio = "1.0" if url.endswith("/") and len(url.split("/")) == 4 else ("0.9" if "serie-a" in url else "0.8")
        sitemap_xml += f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{prio}</priority>
  </url>\n"""
    sitemap_xml += '</urlset>\n'

    with open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print(f"  ✓ Sitemap XML generata con {len(sitemap_urls)} URL in dist/sitemap.xml")

    # 6. Genera Robots.txt
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /data/
Disallow: /config/
Disallow: /src/
Disallow: /tools/
Disallow: /tests/

Sitemap: {BASE_URL}/sitemap.xml
"""
    with open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt)
    print("  ✓ Robots.txt generato in dist/robots.txt")

    print(f"\n-> Build SEO e Grafica Completa terminata in dist/!")

if __name__ == '__main__':
    build_all()
