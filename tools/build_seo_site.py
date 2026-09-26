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

def minify_css(css: str) -> str:
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([\{\}\:\;\,\>])\s*', r'\1', css)
    css = re.sub(r';\}', '}', css)
    return css.strip()

def minify_js(js: str) -> str:
    lines = []
    for line in js.splitlines():
        s = line.strip()
        if not s or s.startswith('//'):
            continue
        lines.append(line)
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'/\*[\s\S]*?\*/', '', cleaned)
    return cleaned

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
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Breadcrumbs */
.breadcrumbs {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #64748b;
    padding: 20px 0 14px 0;
    font-weight: 600;
}
.breadcrumbs a {
    color: #94a3b8;
    text-decoration: none;
    transition: color 0.2s ease;
}
.breadcrumbs a:hover {
    color: #38bdf8;
}
.breadcrumbs-sep {
    color: #475569;
}
.breadcrumbs-cur {
    color: #f8fafc;
}

/* Hero Section */
.pillar-hero {
    background: radial-gradient(120% 140% at 50% -20%, rgba(56, 189, 248, 0.16) 0%, rgba(15, 23, 42, 0.8) 100%), rgba(18, 22, 29, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}
.pillar-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 8%;
    right: 8%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.8), transparent);
}
.pillar-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #38bdf8;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
}
.pillar-title {
    font-family: 'Outfit', system-ui, -apple-system, sans-serif;
    font-size: 27px;
    font-weight: 900;
    color: #fff;
    margin: 0 0 8px 0;
    letter-spacing: -0.4px;
    line-height: 1.25;
}
.pillar-desc {
    font-size: 14.5px;
    color: #94a3b8;
    margin: 0;
    max-width: 840px;
    line-height: 1.6;
}

/* KPI Metric Cards Grid */
.pillar-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 14px;
    margin-bottom: 22px;
}
.pillar-kpi-card {
    background: rgba(18, 22, 29, 0.85);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
.pillar-kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
}
.pillar-kpi-icon {
    font-size: 24px;
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.pillar-kpi-num {
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #fff;
    line-height: 1.1;
}
.pillar-kpi-label {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 2px;
}

/* Interactive Filter Bar */
.pillar-controls-bar {
    background: rgba(18, 22, 29, 0.92);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}
.pillar-search-wrapper {
    flex: 1;
    min-width: 240px;
    position: relative;
}
.pillar-search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    color: #64748b;
    pointer-events: none;
}
.pillar-search-input {
    width: 100%;
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 10px 14px 10px 38px;
    color: #fff;
    font-size: 13.5px;
    font-family: inherit;
    outline: none;
    transition: all 0.2s ease;
    box-sizing: border-box;
}
.pillar-search-input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.25);
    background: rgba(0, 0, 0, 0.65);
}
.pillar-search-input::placeholder {
    color: #64748b;
}

.pillar-select {
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 10px 14px;
    color: #e2e8f0;
    font-size: 13px;
    font-family: inherit;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s;
}
.pillar-select:focus {
    border-color: #38bdf8;
}

.pillar-chips-group {
    display: flex;
    align-items: center;
    gap: 6px;
    overflow-x: auto;
}
.pillar-filter-chip {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94a3b8;
    padding: 7px 13px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}
.pillar-filter-chip:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.1);
}
.pillar-filter-chip.active {
    background: rgba(56, 189, 248, 0.2);
    border-color: #38bdf8;
    color: #38bdf8;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
}

/* Glass Table Card */
.pillar-table-card {
    background: rgba(18, 22, 29, 0.85);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    margin-bottom: 24px;
}
.table-responsive {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.table-responsive::-webkit-scrollbar {
    height: 6px;
}
.table-responsive::-webkit-scrollbar-track {
    background: rgba(12, 14, 18, 0.6);
}
.table-responsive::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.16);
    border-radius: 8px;
}

/* Ultra Modern Table */
.seo-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: inherit;
    text-align: left;
}
.seo-table th {
    background: rgba(12, 15, 22, 0.96);
    color: #94a3b8;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 12px 14px;
    border-bottom: 2px solid rgba(255, 255, 255, 0.08);
    white-space: nowrap;
}
.seo-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
    font-size: 13px;
    color: #e2e8f0;
    white-space: nowrap;
}
.seo-table tbody tr {
    transition: background-color 0.15s ease;
}
.seo-table tbody tr:hover {
    background: rgba(56, 189, 248, 0.04);
}
.seo-table tbody tr:last-child td {
    border-bottom: none;
}

/* Cell Elements */
.cell-player-box {
    display: flex;
    align-items: center;
    gap: 10px;
    white-space: nowrap;
}
.player-role-avatar {
    width: 32px;
    height: 32px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 11.5px;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}
.role-P { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
.role-D { background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
.role-C { background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
.role-A { background: rgba(244, 63, 94, 0.18); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4); }

.player-main-name {
    font-weight: 800;
    font-size: 13.5px;
    color: #fff;
    text-decoration: none !important;
    transition: color 0.15s ease;
    display: block;
    line-height: 1.25;
    white-space: nowrap;
}
.player-main-name:hover {
    color: #38bdf8;
    text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
}
.player-meta-sub {
    font-size: 11px;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 2px;
    white-space: nowrap;
}
.team-tag {
    color: #cbd5e1;
    font-weight: 600;
}
.meta-dot {
    color: #475569;
}

/* Diagnosis Cell */
.diagnosis-badge {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    color: #f1f5f9;
    font-weight: 500;
    font-size: 12.5px;
    white-space: normal !important;
    line-height: 1.35;
    max-width: 440px;
}
.diagnosis-icon {
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 1px;
}

/* Return Date Badge */
.return-date-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #fbbf24;
    padding: 4px 9px;
    border-radius: 7px;
    font-weight: 800;
    font-size: 12px;
    white-space: nowrap;
}

/* Fragility Chips */
.fragility-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 9px;
    border-radius: 7px;
    font-size: 10.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.tier-CRISTALLO {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.18), rgba(185, 28, 28, 0.28));
    border: 1px solid #ef4444;
    color: #fca5a5;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.25);
}
.tier-FRAGILE {
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.18), rgba(194, 65, 12, 0.28));
    border: 1px solid #f97316;
    color: #fdba74;
}
.tier-ATTENZIONE {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.18), rgba(180, 83, 9, 0.28));
    border: 1px solid #f59e0b;
    color: #fde047;
}
.tier-STABILE {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(4, 120, 87, 0.28));
    border: 1px solid #10b981;
    color: #6ee7b7;
}

/* Action Button */
.btn-detail-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #38bdf8;
    padding: 5px 12px;
    border-radius: 7px;
    font-size: 11.5px;
    font-weight: 700;
    text-decoration: none !important;
    transition: all 0.2s ease;
    white-space: nowrap;
}
.btn-detail-link:hover {
    background: #38bdf8;
    color: #0b0f19;
    border-color: #38bdf8;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.45);
    transform: translateX(2px);
}

/* Rigoristi Tactical Design System */
.team-tactical-header {
    display: flex;
    align-items: center;
    gap: 10px;
    white-space: nowrap;
}
.team-badge-circle {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
    border: 1px solid rgba(255, 255, 255, 0.14);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 11.5px;
    color: #fff;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}
.team-name-bold {
    font-weight: 800;
    font-size: 14px;
    color: #fff;
    line-height: 1.2;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
}
.team-coach-sub {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 2px;
    white-space: nowrap;
}
.tactical-formation-chip {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #38bdf8;
    font-size: 10.5px;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 5px;
    white-space: nowrap;
    display: inline-block;
    letter-spacing: 0.3px;
}

.takers-flow {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: nowrap;
    white-space: nowrap;
}
.taker-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 7px;
    font-size: 11.5px;
    font-weight: 700;
    white-space: nowrap;
    flex-shrink: 0;
}
.taker-1 {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.3));
    border: 1px solid #fbbf24;
    color: #fbbf24;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
}
.taker-2 {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #f1f5f9;
}
.taker-3 {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94a3b8;
}

.setpiece-tag-group {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    white-space: nowrap;
    gap: 5px;
}
.setpiece-tag {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #cbd5e1;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
}
.setpiece-tag.corner-tag {
    background: rgba(168, 85, 247, 0.1);
    border-color: rgba(168, 85, 247, 0.3);
    color: #c084fc;
}

/* Griglia Portieri Matrix Badges */
.gk-badge-perfect {
    background: rgba(16, 185, 129, 0.16);
    border: 1px solid #10b981;
    color: #34d399;
    padding: 3px 8px;
    border-radius: 7px;
    font-weight: 800;
    font-size: 11.5px;
    white-space: nowrap;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}
.gk-badge-elite {
    background: rgba(56, 189, 248, 0.14);
    border: 1px solid #38bdf8;
    color: #38bdf8;
    padding: 3px 8px;
    border-radius: 7px;
    font-weight: 700;
    font-size: 11.5px;
    white-space: nowrap;
}
.gk-badge-optimal {
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid #f59e0b;
    color: #fbbf24;
    padding: 3px 8px;
    border-radius: 7px;
    font-weight: 700;
    font-size: 11.5px;
    white-space: nowrap;
}

/* Expandable Injury Rows (Desktop & Smartwatch/Mobile) */
.mobile-only {
    display: none !important;
}
.desktop-only {
    display: table-cell;
}

.btn-expand-toggle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: #38bdf8;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 10px;
    padding: 0;
    transition: all 0.2s ease;
}
.btn-expand-toggle:hover {
    background: rgba(56, 189, 248, 0.25);
    border-color: #38bdf8;
    color: #fff;
    transform: scale(1.08);
}
.btn-expand-toggle.expanded .chevron-arrow {
    transform: rotate(180deg);
}
.chevron-arrow {
    display: inline-block;
    transition: transform 0.25s ease;
    line-height: 1;
}

.injury-row {
    cursor: pointer;
}
.injury-drawer-row td {
    background: rgba(14, 18, 27, 0.98);
    padding: 12px 14px !important;
    border-bottom: 2px solid rgba(56, 189, 248, 0.25) !important;
    white-space: normal !important;
}
.injury-drawer-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.drawer-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
}
.drawer-lbl {
    font-weight: 800;
    color: #94a3b8;
    white-space: nowrap;
    min-width: 82px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.drawer-val {
    color: #f1f5f9;
    font-size: 12.5px;
    line-height: 1.45;
}
.drawer-footer {
    margin-top: 6px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* Injuries Table Specific Column Layout */
#injuriesTable {
    width: 100%;
    table-layout: auto;
}
#injuriesTable th.col-player, #injuriesTable td.col-player {
    width: 25%;
    min-width: 160px;
    white-space: nowrap;
}
#injuriesTable th.col-date, #injuriesTable td.col-date {
    width: 18%;
    min-width: 130px;
    white-space: nowrap;
}
#injuriesTable th.col-diag, #injuriesTable td.col-diag {
    width: 38%;
    min-width: 200px;
    white-space: normal !important;
}
#injuriesTable th.col-tier, #injuriesTable td.col-tier {
    width: 11%;
    min-width: 85px;
    white-space: nowrap;
}
#injuriesTable th.col-action, #injuriesTable td.col-action {
    width: 8%;
    min-width: 65px;
    white-space: nowrap;
}

/* Griglia Portieri Column Layout */
#gkTable {
    width: 100%;
}
#gkTable th, #gkTable td {
    white-space: nowrap;
}

/* Smartwatch & Mobile Media Query */
@media (max-width: 768px) {
    .desktop-only {
        display: none !important;
    }
    .mobile-only {
        display: inline-flex !important;
    }
    tr.mobile-only {
        display: table-row !important;
    }
    .seo-table th, .seo-table td {
        padding: 9px 8px;
    }
    .return-date-pill {
        padding: 4px 8px;
        font-size: 11.5px;
        font-weight: 800;
    }
    .cell-player-box {
        gap: 6px;
    }
    .player-role-avatar {
        width: 26px;
        height: 26px;
        font-size: 10px;
        border-radius: 7px;
    }
    .player-main-name {
        font-size: 12.5px;
    }
    .player-meta-sub {
        font-size: 10px;
    }
    .pillar-controls-bar {
        padding: 10px 12px;
    }
    .pillar-search-wrapper {
        min-width: 100%;
    }

    /* Rigoristi Smartphone Card Layout */
    #rigoristiTable thead {
        display: none !important;
    }
    #rigoristiTable, #rigoristiTable tbody, #rigoristiTable tr.tactic-row, #rigoristiTable tr.tactic-row td {
        display: block !important;
        width: 100% !important;
        box-sizing: border-box;
    }
    #rigoristiTable tr.tactic-row {
        background: rgba(18, 22, 29, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        margin-bottom: 14px;
        padding: 12px 14px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }
    #rigoristiTable tr.tactic-row td {
        padding: 6px 0 !important;
        border: none !important;
        white-space: normal !important;
    }
    #rigoristiTable tr.tactic-row td:first-child {
        padding-bottom: 8px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        margin-bottom: 6px;
    }
    .mobile-tactic-field {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .mobile-tactic-label {
        font-size: 10.5px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    #rigoristiTable .takers-flow, #rigoristiTable .setpiece-tag-group {
        flex-wrap: wrap !important;
        gap: 5px !important;
        white-space: normal !important;
    }

    /* Griglia Portieri Smartphone Layout */
    #gkTable th.desktop-only, #gkTable td.desktop-only {
        display: none !important;
    }
    #gkTable td {
        padding: 10px 8px !important;
    }
}

/* Call to action & footer */
.pillar-cta-box {
    background: radial-gradient(120% 120% at 50% 0%, rgba(56, 189, 248, 0.18) 0%, rgba(18, 22, 29, 0.95) 100%);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 18px;
    padding: 32px 24px;
    text-align: center;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
    margin: 36px 0 24px 0;
}
.pillar-cta-box h3 {
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 900;
    color: #fff;
    margin: 0 0 8px 0;
}
.pillar-cta-box p {
    font-size: 14px;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto 20px auto;
    line-height: 1.5;
}
.btn-cta-main {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
    color: #fff;
    font-weight: 800;
    font-size: 14px;
    padding: 12px 26px;
    border-radius: 10px;
    text-decoration: none !important;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.4);
    transition: all 0.2s ease;
}
.btn-cta-main:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 28px rgba(6, 182, 212, 0.6);
}

.site-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 24px 0;
    margin-top: 40px;
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
}

/* Team Page Pitch & Hero Styling */
.pitch-club-quick-bar a.club-quick-btn {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    color: #94a3b8;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-decoration: none;
    transition: all 0.18s ease;
    white-space: nowrap;
}
.pitch-club-quick-bar a.club-quick-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.25);
}
.pitch-club-quick-bar a.club-quick-btn.active {
    color: #fff;
    background: linear-gradient(135deg, #0284c7, #2563eb);
    border-color: rgba(56, 189, 248, 0.5);
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.4);
}
.team-hero-banner {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(18, 22, 29, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.team-hero-title {
    font-size: 28px;
    font-weight: 900;
    color: #fff;
    letter-spacing: -0.5px;
    margin: 0;
}
.team-meta-pills {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    margin-top: 8px;
}
.team-stat-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 11.5px;
    font-weight: 700;
    color: #cbd5e1;
}

"""
    return minify_css(base_dashboard_css + "\n" + extra_seo_css)

def render_unified_header(rel_path=""):
    return f"""
    <!-- Unified App Header -->
    <header class="app-header-unified">
        <div class="header-main-row">
            <!-- LEFT: BRANDING & HOME -->
            <div class="header-left">
                <a href="{rel_path}" class="brand-badge" style="text-decoration:none;" title="Fanta Master AI — Portale Statistico Serie A 2026/27">
                    <span class="brand-icon">⚡</span>
                    <div>
                        <div class="brand-title">FANTA MASTER AI</div>
                        <div class="brand-sub">Portale Statistico</div>
                    </div>
                </a>

            </div>

            <!-- CENTER: DIRECT & INTUITIVE NAVIGATION -->
            <nav class="header-nav-groups">
                <!-- 1. LISTONE CALCIATORI -->
                <a href="{rel_path}" class="nav-direct-btn" title="Tabellone &amp; Listone Calciatori">
                    <span>📋</span> Listone Calciatori
                </a>

                <!-- 2. STATISTICHE SERIE A -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupTactics">
                        <span>📈</span> Statistiche Serie A <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}statistiche-serie-a/" class="dropdown-item">📊 Statistiche Serie A &amp; xG</a>
                        <a href="{rel_path}top-flop/" class="dropdown-item">⚡ Top &amp; Flop di Giornata</a>
                        <a href="{rel_path}football-analytics/" class="dropdown-item">📈 Matrice &amp; Scatter Analytics</a>
                        <a href="{rel_path}probabili-formazioni/" class="dropdown-item">⚽ Campo 2D &amp; Schemi Club</a>
                        <a href="{rel_path}confronto-calciatori/" class="dropdown-item">⚔️ Matchup 1vs1 Calciatori</a>
                        <a href="{rel_path}griglia-portieri/" class="dropdown-item">🧤 Griglia Portieri 38/38</a>
                    </div>
                </div>

                <!-- 3. AI & CONSIGLI -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAi">
                        <span>🧠</span> AI &amp; Consigli <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}consigli-fantacalcio/" class="dropdown-item">🎯 Chi Schierare Prossima Giornata</a>
                        <a href="{rel_path}chi-schiero/" class="dropdown-item">⚔️ Tool "Chi Schiero?" (Ballottaggi 1vs1)</a>
                        <a href="{rel_path}top-11-ai/" class="dropdown-item">🧠 5 Squadre Perfette AI</a>
                        <a href="{rel_path}scommesse-talenti/" class="dropdown-item">🔮 Gemme &amp; Sleeper AI</a>
                        <div class="dropdown-divider"></div>
                        <a href="{rel_path}infortunati-serie-a/" class="dropdown-item">🩺 Infortunati &amp; Tempi di Recupero</a>
                        <a href="{rel_path}rigoristi-serie-a/" class="dropdown-item">🎯 Rigoristi &amp; Calci Piazzati</a>
                    </div>
                </div>
            </nav>

            <!-- RIGHT: LIVE STATUS & APP LAUNCH -->
            <div class="header-right">
                <a href="{rel_path}" class="header-squad-pill" style="text-decoration:none;" title="Apri Dashboard &amp; Rosa">
                    <span style="font-size:13px;">📋</span>
                    <span class="pill-credits">Dashboard Live</span>
                </a>
            </div>
        </div>
        <!-- MOBILE SUBNAV -->
        <nav class="mobile-subnav">
            <a href="{rel_path}">📊 Listone</a>
            <a href="{rel_path}consigli-fantacalcio/">🎯 Consigli</a>
            <a href="{rel_path}top-flop/">⚡ Top/Flop</a>
            <a href="{rel_path}infortunati-serie-a/">🩺 Infortuni</a>
            <a href="{rel_path}rigoristi-serie-a/">🎯 Rigoristi</a>
            <a href="{rel_path}griglia-portieri/">🧤 Portieri</a>
        </nav>
    </header>
    """

def render_unified_footer(rel_path=""):
    return f"""
    <!-- ==================== FOOTER & LEGAL DISCLAIMER ==================== -->
    <footer class="app-site-footer">
        <div class="footer-inner">
            <div class="footer-top-grid">
                <div class="footer-brand-col">
                    <div class="footer-brand">
                        <span class="footer-logo-badge">⚽ Fanta Master AI</span>
                        <span class="footer-season-badge">Serie A 2026/27</span>
                    </div>
                    <p class="footer-tagline">
                        Il portale statistico avanzato per il Fantacalcio: expected metrics (xG, xA, xFM), algoritmi predittivi per l'asta e ottimizzatore formazioni 2D con intelligenza artificiale.
                    </p>
                    <div class="footer-contact-item">
                        <span class="footer-contact-icon">✉️</span>
                        <span>Supporto &amp; Contatti: <a href="mailto:info@fantamasterai.it" class="footer-link-highlight">info@fantamasterai.it</a></span>
                    </div>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Navigazione Portale</div>
                    <ul class="footer-nav-list">
                        <li><a href="{rel_path}" class="footer-link">🏟️ Formazione &amp; Asta AI</a></li>
                        <li><a href="{rel_path}consigli-fantacalcio/" class="footer-link">🎯 Consigli di Giornata</a></li>
                        <li><a href="{rel_path}probabili-formazioni/" class="footer-link">⚽ Probabili Formazioni 2D</a></li>
                        <li><a href="{rel_path}top-flop/" class="footer-link">⭐ Top &amp; Flop Settimanali</a></li>
                        <li><a href="{rel_path}football-analytics/" class="footer-link">📊 Scatter Matrix xG &amp; xA</a></li>
                    </ul>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Strumenti Tattici</div>
                    <ul class="footer-nav-list">
                        <li><a href="{rel_path}rigoristi-serie-a/" class="footer-link">🎯 Tabella Rigoristi &amp; Tiratori</a></li>
                        <li><a href="{rel_path}griglia-portieri/" class="footer-link">🧤 Griglia Portieri 38 Turni</a></li>
                        <li><a href="{rel_path}infortunati-serie-a/" class="footer-link">🏥 Report Infortunati &amp; Rientri</a></li>
                        <li><a href="{rel_path}scommesse-talenti/" class="footer-link">💎 Talenti Low-Cost</a></li>
                        <li><a href="{rel_path}confronto-calciatori/" class="footer-link">⚔️ Head-to-Head 1vs1</a></li>
                    </ul>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Note Legali &amp; Privacy</div>
                    <ul class="footer-nav-list">
                        <li><a href="{rel_path}privacy-policy/" class="footer-link" id="footer-privacy-link">🔒 Privacy Policy (GDPR)</a></li>
                        <li><span class="footer-status-pill">🛡️ Privacy by Design</span></li>
                        <li><span class="footer-status-pill">🚫 Zero Cookie Traccianti</span></li>
                        <li><span class="footer-status-pill">📊 Solo Dati Aggregati</span></li>
                    </ul>
                </div>
            </div>

            <div class="footer-disclaimer-box">
                <div class="disclaimer-title">
                    <span>⚖️ Disclaimer Legale sui Marchi e Diritto d'Autore (Fair Use)</span>
                </div>
                <p class="disclaimer-text">
                    <strong>Fanta Master AI</strong> (<code>fantamasterai.it</code>) è un progetto editoriale e scientifico-statistico indipendente. Il sito <strong>non è affiliato, sponsorizzato, approvato o collegato</strong> in alcun modo alla <strong>Lega Nazionale Professionisti Serie A</strong>, alla <strong>FIGC</strong> o ai marchi commerciali registrati <em>Fantacalcio®</em> o <em>FantaMaster</em>. Tutti i nomi di calciatori, allenatori, squadre, stadi e competizioni sportive sono impiegati esclusivamente per finalità illustrative, statistiche, di cronaca e di legittima critica sportiva ai sensi della normativa vigente sul diritto d'autore (Fair Use e diritto di cronaca). Tutti i marchi registrati citati appartengono ai rispettivi legittimi titolari.
                </p>
                <p class="disclaimer-text" style="margin-top: 8px;">
                    <strong>Informativa Privacy by Design (Linee Guida Garante Privacy 10/06/2021):</strong> Questo sito rispetta rigorosamente la privacy degli utenti. Non viene effettuata alcuna raccolta o profilazione di dati personali identificativi; gli indirizzi IP non vengono memorizzati; non sono installati cookie traccianti o di terze parti a fini commerciali. Ai sensi delle normative comunitarie (Regolamento UE 2016/679 - GDPR) e delle Linee Guida del Garante per la Protezione dei Dati Personali in materia di cookie e altri strumenti di tracciamento del 10 giugno 2021, la piattaforma è esente dall'obbligo di somministrazione preventiva del banner cookie di consenso in quanto tratta unicamente metriche di utilizzo anonime e aggregate di natura tecnica e statistica.
                </p>
            </div>

            <div class="footer-bottom-bar">
                <div class="footer-copy">
                    &copy; 2026/2027 <strong>Fanta Master AI</strong> — <code>fantamasterai.it</code>. Tutti i diritti riservati.
                </div>
                <div class="footer-bottom-links">
                    <a href="{rel_path}privacy-policy/" class="footer-bottom-link">Privacy Policy</a>
                    <span class="footer-sep">•</span>
                    <a href="mailto:info@fantamasterai.it" class="footer-bottom-link">info@fantamasterai.it</a>
                </div>
            </div>
        </div>
    </footer>
    """


from tools.seo_player_template import generate_player_page

def generate_injuries_pillar(players, injuries_db):
    active_players = [p for p in players if p.get("is_injured")]
    
    # Parser per timestamp data rientro (DD/MM/YYYY -> YYYYMMDD)
    def parse_return_info(player):
        d_str = str(player.get("infortunio_rientro") or "").strip()
        m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', d_str)
        if m:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            ts = year * 10000 + month * 100 + day
            return ts, d_str
        return 99991231, d_str or "Da definire"

    # Ordinamento iniziale: data di rientro più vicina in cima
    active_players.sort(key=lambda p: (parse_return_info(p)[0], p.get("name", "")))
    
    total_injured = len(active_players)
    muscular_count = sum(1 for p in active_players if any(w in p.get("infortunio_motivo", "").lower() for w in ["muscol", "bicipite", "adduttore", "flessore", "polpaccio", "affaticamento", "coscia"]))
    fragile_count = sum(1 for p in active_players if p.get("fragility_tier") in ["CRISTALLO", "FRAGILE"])
    all_teams = sorted(list(set(p.get("team") for p in active_players if p.get("team"))))
    
    rows = ""
    for idx, p in enumerate(active_players):
        name = p.get("name", "")
        team = p.get("team", "")
        role = p.get("role", "C")
        motivo = p.get("infortunio_motivo", "Infortunio")
        tier = p.get("fragility_tier", "STABILE")
        
        team_inj = injuries_db.get(team, {})
        hist_entry = team_inj.get(name, {})
        full_name = hist_entry.get("tm_name", name)
        slug = slugify(full_name)
        
        ts, rientro_display = parse_return_info(p)
        safe_id = f"{slug}-{p.get('id', idx)}"
        
        rows += f"""
        <tr class="injury-row" id="row-{safe_id}" data-id="{safe_id}" data-date-ts="{ts}" data-date-str="{clean_html(rientro_display)}" data-name="{clean_html(full_name.lower())}" data-team="{clean_html(team.lower())}" data-role="{role}" data-tier="{tier}" onclick="onRowClick('{safe_id}', event)">
            <td class="col-player">
                <div class="cell-player-box">
                    <div class="player-role-avatar role-{role}">{role}</div>
                    <div>
                        <a href="../calciatore/{slug}/" class="player-main-name">{clean_html(full_name)}</a>
                        <div class="player-meta-sub">
                            <span class="team-tag">{clean_html(team)}</span>
                            <span class="meta-dot">&bull;</span>
                            <span>Ruolo {role}</span>
                        </div>
                    </div>
                </div>
            </td>
            <td class="col-date">
                <span class="return-date-pill">📅 {clean_html(rientro_display)}</span>
            </td>
            <td class="col-diag desktop-only">
                <div class="diagnosis-badge">
                    <span class="diagnosis-icon">🩺</span>
                    <span>{clean_html(motivo)}</span>
                </div>
            </td>
            <td class="col-tier desktop-only">
                <span class="fragility-chip tier-{tier}">{tier}</span>
            </td>
            <td class="col-action" style="text-align:center;">
                <!-- Desktop button -->
                <a href="../calciatore/{slug}/" class="btn-detail-link desktop-only">Scheda &rarr;</a>
                <!-- Mobile / Smartwatch expand chevron -->
                <button type="button" class="btn-expand-toggle mobile-only" id="btn-toggle-{safe_id}" onclick="toggleInjuryDetail('{safe_id}', event)" aria-label="Espandi dettagli infortunio">
                    <span class="chevron-arrow">▼</span>
                </button>
            </td>
        </tr>
        <!-- Accordion Drawer (Smartwatch & Mobile) -->
        <tr class="injury-drawer-row mobile-only" id="drawer-{safe_id}" style="display:none;">
            <td colspan="3">
                <div class="injury-drawer-content">
                    <div class="drawer-item">
                        <span class="drawer-lbl">🩺 Diagnosi:</span>
                        <span class="drawer-val">{clean_html(motivo)}</span>
                    </div>
                    <div class="drawer-item">
                        <span class="drawer-lbl">⚠️ Fragilità:</span>
                        <span class="fragility-chip tier-{tier}">{tier}</span>
                    </div>
                    <div class="drawer-item drawer-footer">
                        <a href="../calciatore/{slug}/" class="btn-detail-link" style="width:100%;justify-content:center;">Vedi Scheda Calciatore &rarr;</a>
                    </div>
                </div>
            </td>
        </tr>
        """
        
    team_options = "".join([f'<option value="{clean_html(t.lower())}">{clean_html(t)}</option>' for t in all_teams])

    meta_title = "Infortunati Serie A 2026/27: Tabella Tempi di Recupero & Rientri | Fanta Master AI"
    meta_desc = "Tabella sempre aggiornata di tutti i calciatori infortunati in Serie A 2026/27: diagnosi medica, tempi di recupero stimati, data di rientro e consigli per l'asta Fantacalcio."
    page_url = f"{BASE_URL}/infortunati-serie-a/"

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/seo.css">
</head>
<body>
{render_unified_header('../')}

    <main class="site-container">
        <nav class="breadcrumbs">
            <a href="../">Home</a> <span class="breadcrumbs-sep">/</span> <span class="breadcrumbs-cur">Infortunati Serie A</span>
        </nav>

        <!-- HERO HEADER -->
        <section class="pillar-hero">
            <div class="pillar-tag">🩺 MONITORAGGIO CLINICO SERIE A 2026/27</div>
            <h1 class="pillar-title">Infortunati Serie A: Tempi di Recupero &amp; Rientri</h1>
            <p class="pillar-desc">
                Bollettini medici ufficiali e verificati in tempo reale: diagnosi cliniche dettagliate, tempi di recupero stimati e indice di fragilità per gestire al meglio formazioni, asta e scambi.
            </p>
        </section>

        <!-- KPI SUMMARY METRICS -->
        <section class="pillar-kpi-grid">
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#f43f5e;">🔴</div>
                <div>
                    <div class="pillar-kpi-num">{total_injured}</div>
                    <div class="pillar-kpi-label">Infortunati Attivi</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#fbbf24;">⚡</div>
                <div>
                    <div class="pillar-kpi-num">{muscular_count}</div>
                    <div class="pillar-kpi-label">Lesioni Muscolari</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#f97316;">⚠️</div>
                <div>
                    <div class="pillar-kpi-num">{fragile_count}</div>
                    <div class="pillar-kpi-label">Fragili / Cristallo</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#38bdf8;">🛡️</div>
                <div>
                    <div class="pillar-kpi-num">G5</div>
                    <div class="pillar-kpi-label">Dati Aggiornati Live</div>
                </div>
            </div>
        </section>

        <!-- LIVE FILTER CONTROLS BAR -->
        <div class="pillar-controls-bar">
            <div class="pillar-search-wrapper">
                <span class="pillar-search-icon">🔍</span>
                <input type="text" id="injurySearch" class="pillar-search-input" placeholder="Cerca calciatore, club o tipo di infortunio..." oninput="filterInjuries()">
            </div>
            <select id="injuryTeamFilter" class="pillar-select" onchange="filterInjuries()">
                <option value="all">Tutti i Club</option>
                {team_options}
            </select>
            <div class="pillar-chips-group">
                <button type="button" class="pillar-filter-chip active" data-role="ALL" onclick="setRoleFilter('ALL', this)">TUTTI</button>
                <button type="button" class="pillar-filter-chip" data-role="P" onclick="setRoleFilter('P', this)">🧤 P</button>
                <button type="button" class="pillar-filter-chip" data-role="D" onclick="setRoleFilter('D', this)">🛡️ D</button>
                <button type="button" class="pillar-filter-chip" data-role="C" onclick="setRoleFilter('C', this)">🪄 C</button>
                <button type="button" class="pillar-filter-chip" data-role="A" onclick="setRoleFilter('A', this)">⚡ A</button>
                <button type="button" class="pillar-filter-chip active" id="sortReturnBtn" onclick="toggleSortReturnDate()" title="Inverti ordinamento per data di rientro">📅 Rientro: Più Vicini ▲</button>
            </div>
        </div>

        <!-- GLASS TABLE -->
        <section class="pillar-table-card">
            <div class="table-responsive">
                <table class="seo-table" id="injuriesTable">
                    <thead>
                        <tr>
                            <th class="col-player">Calciatore &amp; Ruolo</th>
                            <th class="col-date" onclick="toggleSortReturnDate()" style="cursor:pointer;" title="Clicca per invertire l'ordinamento per data di rientro">
                                Rientro Stimato <span id="sortDateIcon" style="color:#fbbf24;margin-left:4px;">▲</span>
                            </th>
                            <th class="col-diag desktop-only">Diagnosi Infortunio</th>
                            <th class="col-tier desktop-only">Fragilità Clinica</th>
                            <th class="col-action" style="text-align:center;">
                                <span class="desktop-only">Scheda</span>
                                <span class="mobile-only">Info</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- CTA BOX -->
        <section class="pillar-cta-box">
            <h3>Non farti cogliere impreparato all'Asta o agli Scambi!</h3>
            <p>L'algoritmo predittivo di Fanta Master AI calcola la svalutazione esatta del prezzo d'asta in crediti (CR) per ogni infortunato e suggerisce i migliori sostituti in rosa.</p>
            <a href="../" class="btn-cta-main">Vai alla Dashboard Live 🚀</a>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Portale Statistico Ufficiale Serie A</p>
        </div>
    </footer>

    <script>
        let currentRole = 'ALL';
        let currentSortDir = 'asc';

        function toggleSortReturnDate() {{
            currentSortDir = (currentSortDir === 'asc') ? 'desc' : 'asc';
            updateSortUi();
            sortRowsByDate();
        }}

        function updateSortUi() {{
            const icon = document.getElementById('sortDateIcon');
            if (icon) {{
                icon.textContent = (currentSortDir === 'asc') ? '▲' : '▼';
            }}
            const btn = document.getElementById('sortReturnBtn');
            if (btn) {{
                btn.textContent = (currentSortDir === 'asc') ? '📅 Rientro: Più Vicini ▲' : '📅 Rientro: Più Lontani ▼';
            }}
        }}

        function sortRowsByDate() {{
            const tbody = document.querySelector('#injuriesTable tbody');
            const mainRows = Array.from(tbody.querySelectorAll('tr.injury-row'));

            mainRows.sort((a, b) => {{
                const tsA = parseInt(a.getAttribute('data-date-ts') || '99991231', 10);
                const tsB = parseInt(b.getAttribute('data-date-ts') || '99991231', 10);
                if (tsA !== tsB) {{
                    return currentSortDir === 'asc' ? tsA - tsB : tsB - tsA;
                }}
                const nameA = a.getAttribute('data-name') || '';
                const nameB = b.getAttribute('data-name') || '';
                return nameA.localeCompare(nameB);
            }});

            mainRows.forEach(row => {{
                const id = row.getAttribute('data-id');
                const drawer = document.getElementById('drawer-' + id);
                tbody.appendChild(row);
                if (drawer) tbody.appendChild(drawer);
            }});
        }}

        function toggleInjuryDetail(id, event) {{
            if (event) event.stopPropagation();
            const drawer = document.getElementById('drawer-' + id);
            const btn = document.getElementById('btn-toggle-' + id);
            if (!drawer) return;

            const isHidden = (drawer.style.display === 'none' || !drawer.style.display);
            drawer.style.display = isHidden ? 'table-row' : 'none';
            if (btn) {{
                if (isHidden) {{
                    btn.classList.add('expanded');
                }} else {{
                    btn.classList.remove('expanded');
                }}
            }}
        }}

        function onRowClick(id, event) {{
            if (event.target.tagName.toLowerCase() === 'a' || event.target.closest('a')) return;
            if (window.innerWidth <= 640) {{
                toggleInjuryDetail(id, event);
            }}
        }}

        function setRoleFilter(role, btn) {{
            currentRole = role;
            document.querySelectorAll('.pillar-chips-group .pillar-filter-chip').forEach(b => {{
                if (b.hasAttribute('data-role')) b.classList.remove('active');
            }});
            if (btn) btn.classList.add('active');
            filterInjuries();
        }}

        function filterInjuries() {{
            const search = (document.getElementById('injurySearch').value || '').toLowerCase().trim();
            const team = document.getElementById('injuryTeamFilter').value;
            const mainRows = document.querySelectorAll('#injuriesTable tbody tr.injury-row');

            mainRows.forEach(tr => {{
                const id = tr.getAttribute('data-id');
                const drawer = document.getElementById('drawer-' + id);
                const rName = tr.getAttribute('data-name') || '';
                const rTeam = tr.getAttribute('data-team') || '';
                const rRole = tr.getAttribute('data-role') || '';

                const matchesSearch = !search || rName.includes(search) || rTeam.includes(search);
                const matchesTeam = team === 'all' || rTeam === team;
                const matchesRole = currentRole === 'ALL' || rRole === currentRole;

                if (matchesSearch && matchesTeam && matchesRole) {{
                    tr.style.display = '';
                }} else {{
                    tr.style.display = 'none';
                    if (drawer) drawer.style.display = 'none';
                }}
            }});
        }}
    </script>
    {render_unified_footer("../")}
    <script src="../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def generate_rigoristi_pillar(tactical_db):
    total_teams = len(tactical_db)
    rows = ""
    for team, data in sorted(tactical_db.items()):
        all_coach = data.get("all", "Allenatore")
        modulo = data.get("modulo", "4-3-3")
        rigoristi = data.get("rigoristi", [])
        punizioni = data.get("punizioni", [])
        corner = data.get("corner", [])
        
        takers_html = ""
        for i, r in enumerate(rigoristi[:3]):
            rank_class = f"taker-{i+1}"
            rank_medal = "🥇" if i == 0 else ("🥈" if i == 1 else "🥉")
            takers_html += f'<span class="taker-badge {rank_class}">{rank_medal} {clean_html(r)}</span> '
        if not takers_html:
            takers_html = '<span style="color:#64748b;font-size:12px;">Non specificato</span>'
            
        pun_html = "".join([f'<span class="setpiece-tag">🪄 {clean_html(p)}</span>' for p in punizioni]) if punizioni else '<span style="color:#64748b;font-size:12px;">-</span>'
        cor_html = "".join([f'<span class="setpiece-tag corner-tag">🚩 {clean_html(c)}</span>' for c in corner]) if corner else '<span style="color:#64748b;font-size:12px;">-</span>'
        
        team_short = team[:3].upper()
        search_data = f"{team.lower()} {all_coach.lower()} {modulo.lower()} {' '.join(rigoristi).lower()} {' '.join(punizioni).lower()}"
        
        rows += f"""
        <tr class="tactic-row" data-search="{clean_html(search_data)}">
            <td>
                <div class="team-tactical-header">
                    <div class="team-badge-circle">{team_short}</div>
                    <div>
                        <div class="team-name-bold">{clean_html(team)} <span class="tactical-formation-chip">{clean_html(modulo)}</span></div>
                        <div class="team-coach-sub">All. {clean_html(all_coach)}</div>
                    </div>
                </div>
            </td>
            <td>
                <div class="mobile-tactic-field">
                    <span class="mobile-tactic-label mobile-only">🎯 Rigoristi:</span>
                    <div class="takers-flow">{takers_html}</div>
                </div>
            </td>
            <td>
                <div class="mobile-tactic-field">
                    <span class="mobile-tactic-label mobile-only">🪄 Punizioni:</span>
                    <div class="setpiece-tag-group">{pun_html}</div>
                </div>
            </td>
            <td>
                <div class="mobile-tactic-field">
                    <span class="mobile-tactic-label mobile-only">🚩 Corner:</span>
                    <div class="setpiece-tag-group">{cor_html}</div>
                </div>
            </td>
        </tr>
        """
        
    meta_title = "Rigoristi Serie A 2026/27: Tabella Gerarchie Rigori, Punizioni e Corner | Fanta Master AI"
    meta_desc = "Tutti i rigoristi ufficiali della Serie A 2026/27 club per club: primo, secondo e terzo tiratore dal dischetto, specialisti delle punizioni e battitori di corner."
    page_url = f"{BASE_URL}/rigoristi-serie-a/"

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/seo.css">
</head>
<body>
{render_unified_header('../')}

    <main class="site-container">
        <nav class="breadcrumbs">
            <a href="../">Home</a> <span class="breadcrumbs-sep">/</span> <span class="breadcrumbs-cur">Rigoristi Serie A</span>
        </nav>

        <!-- HERO HEADER -->
        <section class="pillar-hero">
            <div class="pillar-tag">🎯 GERARCHIE TATTICHE UFFICIALI SERIE A 2026/27</div>
            <h1 class="pillar-title">Rigoristi Serie A: Gerarchie Rigori, Punizioni e Corner</h1>
            <p class="pillar-desc">
                La guida tattica definitiva per tutti i 20 club di Serie A: primo, secondo e terzo rigorista designato, tiratori di punizioni dirette e specialisti dei corner per fare la differenza al Fantacalcio.
            </p>
        </section>

        <!-- KPI SUMMARY METRICS -->
        <section class="pillar-kpi-grid">
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#38bdf8;">🏟️</div>
                <div>
                    <div class="pillar-kpi-num">{total_teams}</div>
                    <div class="pillar-kpi-label">Club Monitorati</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#fbbf24;">🎯</div>
                <div>
                    <div class="pillar-kpi-num">20</div>
                    <div class="pillar-kpi-label">1° Tiratori Designati</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#34d399;">🪄</div>
                <div>
                    <div class="pillar-kpi-num">60+</div>
                    <div class="pillar-kpi-label">Tiratori di Punizioni</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#c084fc;">🚩</div>
                <div>
                    <div class="pillar-kpi-num">50+</div>
                    <div class="pillar-kpi-label">Battitori di Corner</div>
                </div>
            </div>
        </section>

        <!-- SEARCH BAR -->
        <div class="pillar-controls-bar">
            <div class="pillar-search-wrapper">
                <span class="pillar-search-icon">🔍</span>
                <input type="text" id="rigoristiSearch" class="pillar-search-input" placeholder="Cerca squadra, rigorista, tiratore o allenatore..." oninput="filterRigoristi()">
            </div>
        </div>

        <!-- GLASS TABLE -->
        <section class="pillar-table-card">
            <div class="table-responsive">
                <table class="seo-table" id="rigoristiTable">
                    <thead>
                        <tr>
                            <th>Squadra &amp; Modulo</th>
                            <th>Gerarchia Rigoristi (1°, 2°, 3°)</th>
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

        <!-- CTA BOX -->
        <section class="pillar-cta-box">
            <h3>Cerchi tiratori infallibili per la tua Rosa?</h3>
            <p>Nella nostra Dashboard trovi l'indice xFM dei rigoristi, le percentuali di conversione dal dischetto e l'impatto sul budget per ciascun calciatore.</p>
            <a href="../" class="btn-cta-main">Esplora il Listone Live 🚀</a>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Rigoristi e Tattica Ufficiale Serie A</p>
        </div>
    </footer>

    <script>
        function filterRigoristi() {{
            const search = (document.getElementById('rigoristiSearch').value || '').toLowerCase().trim();
            const rows = document.querySelectorAll('#rigoristiTable tbody tr');

            rows.forEach(tr => {{
                const s = tr.getAttribute('data-search') || '';
                if (!search || s.includes(search)) {{
                    tr.style.display = '';
                }} else {{
                    tr.style.display = 'none';
                }}
            }});
        }}
    </script>
    {render_unified_footer("../")}
    <script src="../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def generate_gk_pillar(gk_matrix_data):
    meta_title = "Griglia Portieri Fantacalcio 2026/27: Tabella Incroci Casa e Trasferta | Fanta Master AI"
    meta_desc = "Calcola le migliori coppie di portieri per l'asta del Fantacalcio 2026/27: tabella incroci perfetta casa e trasferta per non subire mai due trasferte consecutive."
    page_url = f"{BASE_URL}/griglia-portieri/"
    
    pairs = gk_matrix_data.get("pairs", [])
    teams = gk_matrix_data.get("teams", [])
    total_pairs = len(pairs)
    total_teams = len(teams)
    perf_count = sum(1 for p in pairs if p.get("diff", 0) == 0)
    elite_count = sum(1 for p in pairs if p.get("diff", 0) <= 3)
    
    team_options = "".join([f'<option value="{clean_html(t.lower())}">{clean_html(t)}</option>' for t in sorted(teams)])
    
    rows = ""
    for p in pairs:
        t1 = p.get("teamA", "")
        t2 = p.get("teamB", "")
        diff = p.get("diff", 0)
        home = p.get("home_games", 0)
        pct = p.get("pct", 0.0)
        label = p.get("label", "")
        tier = p.get("tier", "good")
        
        if diff == 0:
            conflict_badge = '<span class="gk-badge-perfect">⭐ 0 Contemporaneità (100% Casa)</span>'
            tier_badge = '<span class="fragility-chip tier-STABILE" style="color:#34d399;border-color:#10b981;background:rgba(16,185,129,0.18);">PERFETTO</span>'
        elif diff <= 3:
            conflict_badge = f'<span class="gk-badge-elite">🔥 {diff} Contemporaneità</span>'
            tier_badge = '<span class="fragility-chip tier-ATTENZIONE" style="color:#38bdf8;border-color:#38bdf8;background:rgba(56,189,248,0.18);">ELITE</span>'
        elif diff <= 5:
            conflict_badge = f'<span class="gk-badge-optimal">✅ {diff} Contemporaneità</span>'
            tier_badge = '<span class="fragility-chip" style="color:#fbbf24;border:1px solid #f59e0b;background:rgba(245,158,11,0.15);">OTTIMALE</span>'
        else:
            conflict_badge = f'<span style="color:#94a3b8;font-size:12px;font-weight:600;">{diff} Contemporaneità</span>'
            tier_badge = '<span class="fragility-chip" style="color:#94a3b8;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);">STANDARD</span>'
            
        pct_color = "#34d399" if pct >= 95 else ("#38bdf8" if pct >= 85 else ("#fbbf24" if pct >= 75 else "#94a3b8"))
        search_str = f"{t1.lower()} {t2.lower()} {tier.lower()}"
        
        rows += f"""
        <tr class="gk-row" data-search="{clean_html(search_str)}" data-team1="{clean_html(t1.lower())}" data-team2="{clean_html(t2.lower())}" data-diff="{diff}" data-tier="{tier}">
            <td>
                <div style="display:flex;align-items:center;gap:10px;white-space:nowrap;">
                    <div class="team-badge-circle" style="color:#38bdf8;">🧤</div>
                    <div style="white-space:nowrap;">
                        <strong style="color:#fff;font-size:14px;">{clean_html(t1)}</strong>
                        <span style="color:#64748b;margin:0 4px;font-weight:800;">+</span>
                        <strong style="color:#fff;font-size:14px;">{clean_html(t2)}</strong>
                    </div>
                </div>
            </td>
            <td class="desktop-only" style="text-align:center;white-space:nowrap;">
                <span style="font-weight:800;color:#fff;font-size:13.5px;">{home}</span><span style="color:#64748b;font-size:11px;">/38</span>
            </td>
            <td style="text-align:center;white-space:nowrap;">
                {conflict_badge}
                <div class="mobile-only" style="margin-top:3px;font-size:11px;color:#94a3b8;font-weight:700;">{home}/38 in casa</div>
            </td>
            <td style="text-align:center;white-space:nowrap;">
                <span style="color:{pct_color};font-weight:900;font-size:14px;font-family:'Outfit',sans-serif;">{pct:.1f}%</span>
            </td>
            <td class="desktop-only" style="text-align:center;white-space:nowrap;">
                {tier_badge}
            </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/seo.css">
</head>
<body>
{render_unified_header('../')}

    <main class="site-container">
        <nav class="breadcrumbs">
            <a href="../">Home</a> <span class="breadcrumbs-sep">/</span> <span class="breadcrumbs-cur">Griglia Portieri Serie A</span>
        </nav>

        <!-- HERO HEADER -->
        <section class="pillar-hero">
            <div class="pillar-tag">🧤 STRATEGIA ASTA ESTREMI DIFENSORI 2026/27</div>
            <h1 class="pillar-title">Griglia Portieri: Tabella Incroci Casa e Trasferta</h1>
            <p class="pillar-desc">
                La matrice matematica a 38 giornate per costruire la coppia di portieri ideale: minimizza le partite difficili e assicurati di avere sempre un portiere che gioca tra le mura amiche.
            </p>
        </section>

        <!-- KPI SUMMARY METRICS -->
        <section class="pillar-kpi-grid">
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#fbbf24;">🧤</div>
                <div>
                    <div class="pillar-kpi-num">{total_teams}</div>
                    <div class="pillar-kpi-label">Club Monitorati</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#34d399;">🔄</div>
                <div>
                    <div class="pillar-kpi-num">38</div>
                    <div class="pillar-kpi-label">Giornate Calcolate</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#38bdf8;">🏆</div>
                <div>
                    <div class="pillar-kpi-num">{total_pairs}</div>
                    <div class="pillar-kpi-label">Incroci Matematici</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#a855f7;">⭐</div>
                <div>
                    <div class="pillar-kpi-num">{perf_count}</div>
                    <div class="pillar-kpi-label">Coppie Perfette (0)</div>
                </div>
            </div>
        </section>

        <!-- CONTROLS BAR -->
        <div class="pillar-controls-bar">
            <div class="pillar-search-wrapper">
                <span class="pillar-search-icon">🔍</span>
                <input type="text" id="gkSearch" class="pillar-search-input" placeholder="Cerca club (es. Inter, Milan, Juventus, Napoli...)" oninput="filterGkPairs()">
            </div>
            <select id="gkClubSelect" class="pillar-select" onchange="filterGkPairs()">
                <option value="all">Tutti i Club (190 coppie)</option>
                {team_options}
            </select>
            <div class="pillar-chips-group">
                <button type="button" class="pillar-filter-chip active" data-tier="ALL" onclick="setGkTier('ALL', this)">TUTTI (190)</button>
                <button type="button" class="pillar-filter-chip" data-tier="PERFECT" onclick="setGkTier('PERFECT', this)">⭐ PERFETTI (0)</button>
                <button type="button" class="pillar-filter-chip" data-tier="ELITE" onclick="setGkTier('ELITE', this)">🔥 ELITE (&le;3)</button>
                <button type="button" class="pillar-filter-chip" data-tier="OPTIMAL" onclick="setGkTier('OPTIMAL', this)">✅ OTTIMALI (&le;5)</button>
            </div>
        </div>

        <!-- GLASS TABLE -->
        <section class="pillar-table-card">
            <div class="table-responsive">
                <table class="seo-table" id="gkTable">
                    <thead>
                        <tr>
                            <th>Coppia di Club</th>
                            <th class="desktop-only" style="text-align:center;">Gare Casa Coperte</th>
                            <th style="text-align:center;">Contemporaneità Trasferta</th>
                            <th style="text-align:center;">Alternanza Casa %</th>
                            <th class="desktop-only" style="text-align:center;">Giudizio Algoritmo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- CTA BOX -->
        <section class="pillar-cta-box">
            <h3>Vuoi calcolare l'incrocio personalizzato per 3 portieri?</h3>
            <p>Accedi alla Griglia Portieri interattiva della nostra Dashboard con la matrice completa 38 su 38 e il simulatore di spesa all'asta.</p>
            <a href="../" class="btn-cta-main">Vai alla Dashboard Live 🚀</a>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Algoritmo Incroci Portieri Serie A</p>
        </div>
    </footer>

    <script>
        let currentGkTier = 'ALL';

        function setGkTier(tier, btn) {{
            currentGkTier = tier;
            document.querySelectorAll('.pillar-chips-group .pillar-filter-chip').forEach(b => {{
                if (b.hasAttribute('data-tier')) b.classList.remove('active');
            }});
            if (btn) btn.classList.add('active');
            filterGkPairs();
        }}

        function filterGkPairs() {{
            const search = (document.getElementById('gkSearch').value || '').toLowerCase().trim();
            const club = (document.getElementById('gkClubSelect').value || 'all').toLowerCase();
            const rows = document.querySelectorAll('#gkTable tbody tr.gk-row');

            rows.forEach(tr => {{
                const s = tr.getAttribute('data-search') || '';
                const t1 = tr.getAttribute('data-team1') || '';
                const t2 = tr.getAttribute('data-team2') || '';
                const diff = parseInt(tr.getAttribute('data-diff') || '99', 10);

                const matchesSearch = !search || s.includes(search);
                const matchesClub = club === 'all' || t1 === club || t2 === club;
                
                let matchesTier = true;
                if (currentGkTier === 'PERFECT') matchesTier = (diff === 0);
                else if (currentGkTier === 'ELITE') matchesTier = (diff <= 3);
                else if (currentGkTier === 'OPTIMAL') matchesTier = (diff <= 5);

                if (matchesSearch && matchesClub && matchesTier) {{
                    tr.style.display = '';
                }} else {{
                    tr.style.display = 'none';
                }}
            }});
        }}
    </script>
    {render_unified_footer("../")}
    <script src="../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def get_pitch_band(pos, modulo):
    if not pos:
        return 'pitchMed'
    pos = str(pos).upper()
    if pos in ['P', 'POR']:
        return 'pitchPor'
    if pos.startswith('PC') or pos.startswith('PUN') or pos.startswith('ATT') or pos in ['SS', 'SP', 'A']:
        return 'pitchAtt'
    if pos.startswith('TRQ'):
        return 'pitchTrq'
    if pos in ['AD', 'AS']:
        if modulo and ('4-3-3' in modulo or '3-4-3' in modulo):
            return 'pitchAtt'
        return 'pitchTrq'
    if pos in ['TD', 'TS', 'D'] or pos.startswith('DC') or pos.startswith('BRAC'):
        return 'pitchDef'
    if pos in ['ED', 'ES', 'MED', 'CC', 'REG', 'C'] or pos.startswith('MED') or pos.startswith('CC') or pos.startswith('MEZ'):
        return 'pitchMed'
    return 'pitchMed'

def get_ovr_tier_class(ovr):
    try:
        ovr = int(ovr)
    except:
        ovr = 70
    if ovr >= 92: return 'ovr-tier-elite'
    if ovr >= 87: return 'ovr-tier-top'
    if ovr >= 82: return 'ovr-tier-high'
    if ovr >= 77: return 'ovr-tier-good'
    if ovr >= 72: return 'ovr-tier-mid'
    if ovr >= 66: return 'ovr-tier-low'
    return 'ovr-tier-bench'

def get_substitute_info(starter, team_data, team_players):
    sub_name = starter.get("sub_name")
    if sub_name:
        return sub_name, starter.get("sub_role", starter.get("role", "C"))
    
    s_name = (starter.get("name") or "").lower()
    for b in team_data.get("ballottaggi", []):
        bp = (b.get("player") or "").lower()
        if bp and (bp in s_name or s_name in bp):
            m = re.match(r'^([^(/\n]+)', b.get("vs", ""))
            if m:
                return m.group(1).strip(), starter.get("role", "C")
    
    st = starter.get("status", "")
    m = re.search(r'vs\s+([^(/\n]+)', st, re.I)
    if m:
        return m.group(1).strip(), starter.get("role", "C")
        
    return None, None

def generate_team_page(team_name, team_data, team_players, all_teams, injuries_db, base_url="https://fantamasterai.it"):
    team_slug = slugify(team_name)
    modulo = team_data.get("modulo", "3-5-2")
    mister = team_data.get("all", "Mister")
    dif_stars = int(team_data.get("dif_stars", 3))
    att_stars = int(team_data.get("att_stars", 3))
    top_players = team_data.get("top", [])
    sleeper_players = team_data.get("sleeper", [])
    
    meta_title = f"Probabili Formazioni {team_name} 2026/27: Titolari, Ballottaggi e Rigoristi | Fanta Master AI"
    meta_desc = f"Probabile formazione {team_name} 2026/27 aggiornata: modulo {modulo}, 11 titolare con percentuali, ballottaggi di reparto, rigoristi e rosa completa per il Fantacalcio."
    page_url = f"{base_url}/probabili-formazioni/{team_slug}/"
    
    # 1. Quick Bar 20 Club
    quick_bar_html = "".join([
        f'<a href="../{slugify(tm)}/" class="club-quick-btn {"active" if tm.lower() == team_name.lower() else ""}">{clean_html(tm)}</a>'
        for tm in sorted(all_teams)
    ])
    
    # 2. Player matching helper
    player_by_name_map = {}
    for p in team_players:
        player_by_name_map[p.get("name", "").lower()] = p
        
    def find_p(name):
        if not name: return None
        nl = name.lower().strip()
        if nl in player_by_name_map:
            return player_by_name_map[nl]
        for k, v in player_by_name_map.items():
            if k in nl or nl in k:
                return v
        return None

    # 3. 11 Titolari su Campo 2D
    bands = {'pitchAtt': [], 'pitchTrq': [], 'pitchMed': [], 'pitchDef': [], 'pitchPor': []}
    lineup = team_data.get("lineup", [])
    for st in lineup:
        st_name = st.get("name", "")
        st_role = st.get("role", "C")
        pos_lbl = st.get("pos_label", st.get("pos", ""))
        pct = int(st.get("pct", 70))
        band_id = get_pitch_band(st.get("pos"), modulo)
        
        match_p = find_p(st_name)
        p_slug = slugify(match_p.get("name", st_name)) if match_p else slugify(st_name)
        ovr = match_p.get("ovr", 72) if match_p else 72
        ovr_cls = get_ovr_tier_class(ovr)
        
        sub_name, sub_role = get_substitute_info(st, team_data, team_players)
        tit_color = "#4ade80" if pct >= 80 else ("#fbbf24" if pct >= 60 else "#f87171")
        
        node_html = f"""
        <div class="pitch-player-node">
            <div class="pitch-card">
                <div class="pitch-card-header">
                    <span class="pitch-role-badge {st_role}">{st_role}</span>
                    <span class="pitch-pos-label">{clean_html(pos_lbl)}</span>
                    <span class="pitch-ovr-tag {ovr_cls}">{ovr}</span>
                </div>
                <a href="../../calciatore/{p_slug}/" class="pitch-player-name" title="Vedi Scheda {clean_html(st_name)}">{clean_html(st_name)}</a>
                <div class="pitch-card-sub" style="margin-top:4px;display:flex;align-items:center;justify-content:center;gap:4px;flex-wrap:wrap;">
                    <span style="font-size:10px;font-weight:800;color:{tit_color};">{pct}% Tit</span>
                    {f'<span class="sub-vs-tag" style="font-size:9.5px;color:var(--text-muted);" title="Staffetta con {clean_html(sub_name)}">🔄 vs {clean_html(sub_name)}</span>' if sub_name else ''}
                </div>
            </div>
        </div>
        """
        bands[band_id].append(node_html)

    # 4. Ballottaggi
    ballottaggi_html = ""
    ball_list = team_data.get("ballottaggi", [])
    if ball_list:
        for b in ball_list:
            bp = clean_html(b.get("player", ""))
            pct = int(b.get("pct", 50))
            vs_txt = clean_html(b.get("vs", ""))
            ballottaggi_html += f"""
            <div class="ballottaggio-item" style="padding:9px 12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;font-size:12.5px;font-weight:700;">
                    <span style="color:#fff;">{bp} <b style="color:var(--accent-cyan);">{pct}%</b></span>
                    <span style="color:var(--text-muted);font-size:11.5px;">vs {vs_txt}</span>
                </div>
                <div style="height:5px;background:rgba(255,255,255,0.08);border-radius:3px;margin-top:6px;overflow:hidden;">
                    <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#0284c7,#38bdf8);border-radius:3px;"></div>
                </div>
            </div>
            """
    else:
        ballottaggi_html = '<div style="color:var(--text-muted);font-size:12px;padding:8px 0;">Nessun ballottaggio serrato segnalato: gerarchie definite.</div>'

    # 5. Piazzati & Tiratori
    rigs = team_data.get("rigoristi", [])
    puns = team_data.get("punizioni", [])
    cors = team_data.get("corner", [])
    
    def render_set_piece_list(arr, icon):
        if not arr: return '<span style="color:var(--text-muted);font-size:12px;">-</span>'
        return " &bull; ".join([f'<b>{i+1}° {clean_html(name)}</b>' for i, name in enumerate(arr[:3])])

    # 6. Infortunati del club
    team_injuries = [p for p in team_players if p.get("is_injured")]
    injuries_html = ""
    if team_injuries:
        for p in team_injuries:
            p_slug = slugify(p.get("name", ""))
            injuries_html += f"""
            <div style="display:flex;align-items:center;justify-content:space-between;padding:7px 10px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);border-radius:8px;margin-bottom:6px;">
                <div>
                    <a href="../../calciatore/{p_slug}/" style="font-weight:700;color:#f87171;text-decoration:none;font-size:12.5px;">🩹 {clean_html(p.get('name'))}</a>
                    <div style="font-size:11px;color:var(--text-secondary);">{clean_html(p.get('infortunio_motivo', 'Infortunio'))}</div>
                </div>
                <span style="font-size:11.5px;font-weight:800;color:#fbbf24;">Rientro: {clean_html(p.get('infortunio_rientro', 'TBD'))}</span>
            </div>
            """
    else:
        injuries_html = '<div style="color:#4ade80;font-size:12px;font-weight:700;padding:6px 0;">🟢 Infermeria vuota: tutta la rosa a disposizione!</div>'

    # 7. Tabella Rosa Completa del Club
    roster_rows = ""
    sorted_squad = sorted(team_players, key=lambda x: (
        {'P': 1, 'D': 2, 'C': 3, 'A': 4}.get(x.get('role', 'C'), 5),
        -(x.get('ovr') or 0)
    ))
    for p in sorted_squad:
        p_slug = slugify(p.get("name", ""))
        ovr_val = p.get("ovr", 70)
        ovr_cls = get_ovr_tier_class(ovr_val)
        r = p.get("role", "C")
        tit = p.get("titolarita", 50)
        tit_c = "#4ade80" if tit >= 80 else ("#fbbf24" if tit >= 60 else "#f87171")
        mv = f"{float(p.get('mv_2627')):.2f}" if p.get('mv_2627') else "-"
        fm = f"{float(p.get('fm_2627')):.2f}" if p.get('fm_2627') else "-"
        xfm = f"{float(p.get('xfm')):.2f}" if p.get('xfm') is not None else "-"
        ga = f"{p.get('gol_subiti_2627', 0)} GS" if r == 'P' else f"{p.get('gol_2627', 0)}G / {p.get('assist_2627', 0)}A"
        
        status_tag = ""
        if p.get("is_injured"):
            status_tag = f'<span style="color:#f87171;font-size:11px;font-weight:700;">🩹 {clean_html(p.get("infortunio_rientro", "Inf."))}</span>'
        elif p.get("is_rigorista_1"):
            status_tag = '<span style="color:#fbbf24;font-size:11px;font-weight:700;">👑 Rigorista</span>'
        elif tit >= 85:
            status_tag = '<span style="color:#4ade80;font-size:11px;font-weight:700;">Titolare</span>'
        else:
            status_tag = f'<span style="color:var(--text-muted);font-size:11px;">{tit}% Tit</span>'
            
        roster_rows += f"""
        <tr>
            <td style="text-align:center;"><span class="ovr-pill {ovr_cls}">{ovr_val}</span></td>
            <td style="text-align:center;"><span class="role-badge {r}">{r}</span></td>
            <td>
                <a href="../../calciatore/{p_slug}/" class="player-name-link" style="font-weight:700;color:#fff;text-decoration:none;">{clean_html(p.get('name'))}</a>
                {f'<span class="mantra-sub-txt" style="margin-left:6px;font-size:10px;color:var(--text-muted);">{p.get("mantra")}</span>' if p.get("mantra") else ''}
            </td>
            <td style="text-align:center;font-weight:800;color:var(--accent-gold);">{p.get('fvm', 1)}</td>
            <td style="text-align:center;font-weight:700;color:{tit_c};">{tit}%</td>
            <td style="text-align:center;">{mv}</td>
            <td style="text-align:center;font-weight:700;color:#38bdf8;">{fm}</td>
            <td style="text-align:center;color:var(--accent-cyan);font-weight:700;">{xfm}</td>
            <td style="text-align:center;">{ga}</td>
            <td style="text-align:center;">{status_tag}</td>
            <td style="text-align:center;"><a href="../../calciatore/{p_slug}/" class="btn-clean-action" style="font-size:11px;padding:3px 8px;text-decoration:none;">Scheda &rarr;</a></td>
        </tr>
        """

    # 8. FAQ Schema
    faq_schema = [
        {
            "@type": "Question",
            "name": f"Qual è la probabile formazione del {team_name} nel 2026/27?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Il {team_name} di mister {mister} scende in campo con il modulo {modulo}. Gli 11 titolari principali sono: {', '.join([st.get('name', '') for st in lineup])}."
            }
        },
        {
            "@type": "Question",
            "name": f"Chi è il primo rigorista del {team_name}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Le gerarchie dal dischetto del {team_name} vedono come 1° rigorista {rigs[0] if rigs else 'da definire'}{', seguito da ' + rigs[1] if len(rigs)>1 else ''}{' e ' + rigs[2] if len(rigs)>2 else ''}."
            }
        },
        {
            "@type": "Question",
            "name": f"Quali sono i ballottaggi aperti nel {team_name} per la prossima giornata?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"I ballottaggi più caldi nel {team_name} includono: {'; '.join([b.get('player','') + ' vs ' + b.get('vs','') for b in ball_list[:3]]) if ball_list else 'nessun ballottaggio critico' }."
            }
        }
    ]

    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SportsTeam",
                "name": team_name,
                "sport": "Soccer",
                "coach": {
                    "@type": "Person",
                    "name": mister
                },
                "member": [
                    {"@type": "Person", "name": p.get("name"), "jobTitle": p.get("role")}
                    for p in team_players[:15]
                ]
            },
            {
                "@type": "FAQPage",
                "mainEntity": faq_schema
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Probabili Formazioni Serie A", "item": f"{base_url}/probabili-formazioni/"},
                    {"@type": "ListItem", "position": 3, "name": team_name, "item": page_url}
                ]
            }
        ]
    }

    top_badges = "".join([f'<span class="badge-tag gold" style="font-size:11px;">👑 {clean_html(t)}</span>' for t in top_players[:3]])
    sleeper_badges = "".join([f'<span class="badge-tag cyan" style="font-size:11px;">🔮 {clean_html(s)}</span>' for s in sleeper_players[:3]])

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="icon" type="image/x-icon" href="../../favicon.ico">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{clean_html(meta_title)}">
    <meta property="og:description" content="{clean_html(meta_desc)}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Fanta Master AI">
    
    <!-- CSS Completo Dashboard -->
    <link rel="stylesheet" href="../../css/seo.css">
    
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {json.dumps(schema_data, ensure_ascii=False, indent=2)}
    </script>
</head>
<body>
    {render_unified_header('../../')}

    <main class="site-container" style="padding-top:16px;">
        <nav class="breadcrumbs">
            <a href="../../">Home</a> <span>/</span> 
            <a href="../../probabili-formazioni/">Probabili Formazioni</a> <span>/</span> 
            <span style="color:#fff;">{clean_html(team_name)}</span>
        </nav>

        <!-- Hero Club Banner -->
        <div class="team-hero-banner">
            <div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:32px;">⚽</span>
                    <div>
                        <h1 class="team-hero-title">Probabile Formazione {clean_html(team_name)}</h1>
                        <div style="font-size:12.5px;color:var(--text-secondary);margin-top:2px;">Titolari, Modulo {clean_html(modulo)}, Ballottaggi, Rigoristi e Rosa Serie A 2026/27</div>
                    </div>
                </div>
                <div class="team-meta-pills">
                    <span class="team-stat-badge" style="color:var(--accent-cyan);border-color:rgba(56,189,248,0.35);background:rgba(56,189,248,0.08);">📋 Modulo: <b>{clean_html(modulo)}</b></span>
                    <span class="team-stat-badge">👔 Allenatore: <b>{clean_html(mister)}</b></span>
                    <span class="team-stat-badge">🛡️ Difesa: <b>{'⭐' * dif_stars}</b></span>
                    <span class="team-stat-badge">⚡ Attacco: <b>{'⭐' * att_stars}</b></span>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-start;">
                <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:700;">Consigli Fantacalcio AI:</div>
                <div style="display:flex;gap:6px;flex-wrap:wrap;">
                    {top_badges}
                    {sleeper_badges}
                </div>
            </div>
        </div>

        <!-- Selettore Rapido 20 Club Serie A -->
        <div style="margin-bottom:20px;">
            <div style="font-size:11px;font-weight:800;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Seleziona un Club di Serie A:</div>
            <div class="pitch-club-quick-bar">
                {quick_bar_html}
            </div>
        </div>

        <!-- Campo 2D & Griglia Tattica Laterale -->
        <div class="pitch-container-wrapper">
            <div class="pitch-field-container">
                <div class="pitch-field">
                    <div class="pitch-markings">
                        <div class="pitch-center-circle"></div>
                        <div class="pitch-half-line"></div>
                        <div class="pitch-penalty-area top"></div>
                        <div class="pitch-goal-area top"></div>
                        <div class="pitch-penalty-spot top"></div>
                        <div class="pitch-penalty-area bottom"></div>
                        <div class="pitch-goal-area bottom"></div>
                        <div class="pitch-penalty-spot bottom"></div>
                    </div>

                    <div class="pitch-band" id="pitchAtt">{''.join(bands['pitchAtt'])}</div>
                    {f'<div class="pitch-band" id="pitchTrq">{"".join(bands["pitchTrq"])}</div>' if bands['pitchTrq'] else ''}
                    <div class="pitch-band" id="pitchMed">{''.join(bands['pitchMed'])}</div>
                    <div class="pitch-band" id="pitchDef">{''.join(bands['pitchDef'])}</div>
                    <div class="pitch-band" id="pitchPor">{''.join(bands['pitchPor'])}</div>
                </div>
            </div>

            <!-- Griglia Laterale: Ballottaggi, Piazzati, Infortunati -->
            <div class="pitch-side-grid">
                <!-- Ballottaggi -->
                <div class="tactics-card">
                    <div class="tactics-card-header">
                        <span style="font-size:16px;">🔄</span>
                        <h4>Ballottaggi &amp; Percentuali Titolari</h4>
                    </div>
                    <div style="padding-top:4px;">
                        {ballottaggi_html}
                    </div>
                </div>

                <!-- Tiratori Piazzati -->
                <div class="tactics-card">
                    <div class="tactics-card-header">
                        <span style="font-size:16px;">🎯</span>
                        <h4>Tiratori Ufficiali Calci Piazzati</h4>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:8px;padding-top:6px;">
                        <div class="tactics-meta-row">
                            <span class="lbl">👑 Rigoristi:</span>
                            <span class="val">{render_set_piece_list(rigs, '👑')}</span>
                        </div>
                        <div class="tactics-meta-row">
                            <span class="lbl">👟 Punizioni:</span>
                            <span class="val">{render_set_piece_list(puns, '👟')}</span>
                        </div>
                        <div class="tactics-meta-row">
                            <span class="lbl">🚩 Calci d&#39;Angolo:</span>
                            <span class="val">{render_set_piece_list(cors, '🚩')}</span>
                        </div>
                    </div>
                </div>

                <!-- Infortunati -->
                <div class="tactics-card">
                    <div class="tactics-card-header">
                        <span style="font-size:16px;">🩹</span>
                        <h4>Infermeria &amp; Indisponibili {clean_html(team_name)}</h4>
                    </div>
                    <div style="padding-top:6px;">
                        {injuries_html}
                    </div>
                </div>
            </div>
        </div>

        <!-- Tabella Rosa Completa del Club -->
        <section style="margin-top:34px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
                <div>
                    <h3 style="margin:0;font-size:18px;font-weight:900;color:#fff;">Rosa Completa {clean_html(team_name)} 2026/27</h3>
                    <div style="font-size:12px;color:var(--text-secondary);">Statistiche ufficiali, Overall OVR, Fanta Valore di Mercato e FantaMedie</div>
                </div>
                <span style="font-size:12px;font-weight:700;color:var(--text-muted);">{len(team_players)} Calciatori in Rosa</span>
            </div>

            <div class="table-wrapper">
                <table class="fanta-table clean-table">
                    <thead>
                        <tr>
                            <th style="width:48px;text-align:center;">OVR</th>
                            <th style="width:36px;text-align:center;">R</th>
                            <th>Calciatore &amp; Mantra</th>
                            <th style="text-align:center;">FVM</th>
                            <th style="text-align:center;">Tit.%</th>
                            <th style="text-align:center;">MV</th>
                            <th style="text-align:center;">FM</th>
                            <th style="text-align:center;">xFM</th>
                            <th style="text-align:center;">Gol/Ass</th>
                            <th style="text-align:center;">Status</th>
                            <th style="text-align:center;">Scheda</th>
                        </tr>
                    </thead>
                    <tbody>
                        {roster_rows}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Domande Frequenti (FAQ) -->
        <section style="margin-top:35px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:22px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <span style="font-size:22px;">❓</span>
                <h3 style="margin:0;font-size:17px;font-weight:900;color:#fff;">Domande Frequenti Formazione {clean_html(team_name)}</h3>
            </div>
            <div style="display:flex;flex-direction:column;gap:12px;">
                <div style="padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;">
                    <b style="color:var(--accent-cyan);font-size:13.5px;">Qual è la probabile formazione del {clean_html(team_name)} nel 2026/27?</b>
                    <p style="margin:6px 0 0 0;font-size:12.5px;color:var(--text-secondary);line-height:1.45;">Il {clean_html(team_name)} di mister {clean_html(mister)} gioca con il modulo {clean_html(modulo)}. Gli 11 titolari tipo includono {', '.join([st.get('name', '') for st in lineup[:7]])} e compagni.</p>
                </div>
                <div style="padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;">
                    <b style="color:var(--accent-gold);font-size:13.5px;">Chi è il primo rigorista del {clean_html(team_name)}?</b>
                    <p style="margin:6px 0 0 0;font-size:12.5px;color:var(--text-secondary);line-height:1.45;">Il tiratore principale designato dal dischetto è <b>{clean_html(rigs[0] if rigs else 'da definire')}</b>{', con ' + clean_html(rigs[1]) if len(rigs) > 1 else ''} come prima alternativa.</p>
                </div>
                <div style="padding:12px 14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;">
                    <b style="color:#38bdf8;font-size:13.5px;">Quali sono i ballottaggi più caldi nel {clean_html(team_name)}?</b>
                    <p style="margin:6px 0 0 0;font-size:12.5px;color:var(--text-secondary);line-height:1.45;">Le maglie contese di questa giornata riguardano soprattutto: {'; '.join([b.get('player','') + ' vs ' + b.get('vs','') for b in ball_list[:3]]) if ball_list else 'gerarchie stabili con titolari definiti'}.</p>
                </div>
            </div>
        </section>

        <!-- CTA Box Interlink -->
        <section class="pillar-cta-box" style="margin-top:30px;">
            <h3>Strumenti Tattici &amp; Guida Asta 2026/27</h3>
            <p>Confronta i calciatori del {clean_html(team_name)} con tutti i profili della Serie A, calcola le alternanze portieri e scopri i valori previsti dall&#39;algoritmo predittivo.</p>
            <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:14px;">
                <a href="../../griglia-portieri/" class="btn-clean-action" style="text-decoration:none;">🧤 Griglia Portieri</a>
                <a href="../../rigoristi-serie-a/" class="btn-clean-action" style="text-decoration:none;">🎯 Rigoristi Serie A</a>
                <a href="../../infortunati-serie-a/" class="btn-clean-action" style="text-decoration:none;">🩺 Infortunati &amp; Rientri</a>
                <a href="../../consigli-fantacalcio/" class="btn-cta-main" style="text-decoration:none;">🎯 Consigli di Giornata</a>
            </div>
        </section>
    </main>

    {render_unified_footer("../../")}
    <script src="../../js/tracker.js" defer></script>
</body>
</html>
"""
    return html

def generate_privacy_policy_page():
    meta_title = "Privacy Policy & Informativa Cookie | Fanta Master AI — Serie A 2026/27"
    meta_desc = "Informativa estesa sul trattamento dei dati personali e cookie policy di Fanta Master AI: architettura Privacy by Design, nessun tracciamento invasivo, conformità GDPR."
    page_url = f"{BASE_URL}/privacy-policy/"

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/seo.css">
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "{clean_html(meta_title)}",
        "description": "{clean_html(meta_desc)}",
        "url": "{page_url}"
    }}
    </script>
</head>
<body>
    {render_unified_header("../")}

    <main class="seo-container" style="max-width: 900px; margin: 24px auto; padding: 0 16px;">
        <nav class="breadcrumb-bar" style="margin-bottom: 20px;">
            <a href="../" class="breadcrumb-link">🏠 Home</a>
            <span class="breadcrumb-sep">/</span>
            <span class="breadcrumb-current">Privacy Policy &amp; Cookie</span>
        </nav>

        <div style="background: rgba(18, 24, 38, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 18px; margin-bottom: 24px;">
                <div>
                    <h1 style="font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 800; color: #fff; margin: 0 0 6px 0;">
                        🔒 Privacy Policy &amp; Cookie Policy
                    </h1>
                    <div style="color: var(--text-secondary); font-size: 13px;">
                        Fanta Master AI (<code>fantamasterai.it</code>) &bull; Stagione Serie A 2026/27
                    </div>
                </div>
                <span class="brand-badge" style="background: rgba(34, 197, 94, 0.15); border-color: rgba(34, 197, 94, 0.4); color: #4ade80; font-size: 12px; font-weight: 700;">
                    ✓ Conforme GDPR &amp; Garante Privacy
                </span>
            </div>

            <div style="display: flex; flex-direction: column; gap: 24px; line-height: 1.7; font-size: 13.5px; color: #cbd5e1;">
                
                <section>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 8px 0;">
                        1. Titolare del Trattamento &amp; Contatti
                    </h2>
                    <p style="margin: 0;">
                        Il titolare del trattamento dei dati statistici del portale <strong>Fanta Master AI</strong> (accessibile via <code>https://fantamasterai.it</code>) è il team editoriale e di sviluppo scientifico della piattaforma. Per qualunque informazione, richiesta di chiarimento o segnalazione relativa alle prassi di tutela della privacy, è possibile contattare l'amministrazione tramite l'indirizzo email ufficiale: <a href="mailto:info@fantamasterai.it" style="color: #38bdf8; font-weight: 600; text-decoration: none;">info@fantamasterai.it</a>.
                    </p>
                </section>

                <section>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 8px 0;">
                        2. Principio di Privacy by Design &amp; by Default (GDPR Reg. UE 2016/679)
                    </h2>
                    <p style="margin: 0 0 8px 0;">
                        La piattaforma Fanta Master AI è stata concepita e architettata seguendo i più rigorosi principi di <em>Privacy by Design</em> e <em>Privacy by Default</em> sanciti dall'art. 25 del Regolamento UE 2016/679 (GDPR):
                    </p>
                    <ul style="padding-left: 20px; margin: 0; display: flex; flex-direction: column; gap: 6px;">
                        <li><strong>Nessun obbligo di registrazione:</strong> l'accesso a tutte le funzionalità (consultazione listone calciatori, metriche xG/xA/xFM, ottimizzatore di formazione 2D, griglia portieri e assistente asta) è completamente libero, anonimo e non richiede la creazione di credenziali o account.</li>
                        <li><strong>Nessuna raccolta di dati identificativi diretti:</strong> il portale non memorizza né tratta nomi, cognomi, numeri telefonici, residenze o indirizzi e-mail dell'utente.</li>
                        <li><strong>Nessuna conservazione di indirizzi IP:</strong> le chiamate di rete ai servizi serverless e alla CDN globale non persistono gli indirizzi IP dei visitatori nei database dell'applicazione.</li>
                    </ul>
                </section>

                <section>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 8px 0;">
                        3. Esenzione dal Cookie Banner Preventivo (Linee Guida Garante Privacy 10/06/2021)
                    </h2>
                    <p style="margin: 0 0 8px 0;">
                        In piena ottemperanza all'articolo 122 del D.Lgs. 196/2003 (Codice Privacy) e alle <em>Linee Guida del Garante per la Protezione dei Dati Personali in materia di cookie e altri strumenti di tracciamento del 10 giugno 2021 (doc. web n. 9677876)</em>, si dichiara che:
                    </p>
                    <ul style="padding-left: 20px; margin: 0; display: flex; flex-direction: column; gap: 6px;">
                        <li>Il sito <strong>NON utilizza cookie di profilazione pubblicitaria</strong>, né traccianti di terze parti finalizzati alla categorizzazione dei visitatori a scopi di marketing o retargeting commerciale.</li>
                        <li>Le uniche tecnologie impiegate sono <strong>cookie tecnici strettamente necessari</strong> al funzionamento dell'infrastruttura di rete (CDN Vercel) o strumenti analitici proprietari con IP anonimizzato e finalità limitata all'elaborazione statistica aggregata della piattaforma.</li>
                        <li>Ai sensi del quadro normativo vigente, <strong>non sussiste l'obbligo di somministrazione preventiva del banner cookie di consenso (cookie wall)</strong>, né la necessità di richiedere autorizzazioni all'utente prima della navigazione.</li>
                    </ul>
                </section>

                <section>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 8px 0;">
                        4. Dati Salvati in Locale nel Browser (Storage Locale)
                    </h2>
                    <p style="margin: 0;">
                        Quando configuri la tua rosa, imposti il budget dell'asta, selezioni calciatori preferiti o personalizzi le impostazioni tattiche, tali informazioni vengono conservate unicamente sul tuo dispositivo tramite la memoria locale del browser (<code>localStorage</code>). Questi dati <strong>non vengono inviati o salvati sui nostri server</strong> e rimangono sotto il tuo esclusivo controllo. Puoi cancellarli in qualsiasi istante svuotando i dati di navigazione o la cache del browser.
                    </p>
                </section>

                <section>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 8px 0;">
                        5. Disclaimer Legale sui Marchi e Fair Use Editoriale
                    </h2>
                    <p style="margin: 0;">
                        Fanta Master AI è un progetto editoriale e statistico indipendente. Non è in alcun modo sponsorizzato, affiliato o supportato da Lega Serie A, FIGC o testate editoriali titolari di marchi commerciali registrati (tra cui Fantacalcio® e FantaMaster). Tutti i marchi, loghi societari, nomi di club, atleti e competizioni citati sul portale appartengono ai rispettivi proprietari e sono impiegati ai soli fini di legittimo esercizio del diritto di cronaca, statistica e critica sportiva (Fair Use).
                    </p>
                </section>

                <section>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 8px 0;">
                        6. Esercizio dei Diritti dell'Interessato (GDPR Artt. 15-22)
                    </h2>
                    <p style="margin: 0;">
                        Poiché il sito non raccoglie dati personali identificativi, non conserva log persistenti riconducibili a singole identità naturali né gestisce account utente, l'utente esercita pienamente la propria autodeterminazione cancellando autonomamente la memoria cache locale del proprio browser. Per qualsiasi quesito o comunicazione istituzionale, è possibile scrivere a <a href="mailto:info@fantamasterai.it" style="color: #38bdf8; font-weight: 600; text-decoration: none;">info@fantamasterai.it</a>.
                    </p>
                </section>

                <div style="margin-top: 12px; display: flex; justify-content: center;">
                    <a href="../" class="btn-primary" style="padding: 10px 22px; font-size: 13px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px;">
                        <span>← Torna alla Dashboard Interattiva</span>
                    </a>
                </div>

            </div>
        </div>
    </main>

    {render_unified_footer("../")}
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
                src_f = os.path.join(web_js_dir, f)
                dst_f = os.path.join(js_dir, f)
                if f.endswith(".min.js"):
                    shutil.copy(src_f, dst_f)
                else:
                    with open(src_f, "r", encoding="utf-8") as js_in:
                        js_code = js_in.read()
                    with open(dst_f, "w", encoding="utf-8") as js_out:
                        js_out.write(minify_js(js_code))

    # 2b. Copia l'applicazione interattiva principale in dist/app.html e dist/index.html
    dash_content = ""
    if os.path.exists(DASHBOARD_HTML_PATH):
        with open(DASHBOARD_HTML_PATH, "r", encoding="utf-8") as f:
            dash_content = f.read()
        last_body_idx = dash_content.rfind("</body>")
        if last_body_idx != -1 and "/js/tracker.js" not in dash_content:
            dash_content = dash_content[:last_body_idx] + '    <script src="/js/tracker.js" defer></script>\n' + dash_content[last_body_idx:]
        with open(os.path.join(DIST_DIR, "app.html"), "w", encoding="utf-8") as f:
            f.write(dash_content)
        with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(dash_content)
        print("  ✓ App interattiva clonata con tracker in dist/app.html e dist/index.html")

    # 2c. Genera pagine dedicate Clean URL per ogni sezione della Dashboard
    SECTIONS_METADATA = [
        {
            "route": "top-flop",
            "tab": "top_flop",
            "title": "Top & Flop 5ª Giornata Serie A 2026/27 | Pagelle e Statistiche | Fanta Master AI",
            "desc": "I migliori e peggiori calciatori della 5ª giornata di Serie A 2026/27: voti ufficiali, FantaMedia, bonus, malus e analisi algoritmica Fanta Master AI.",
            "keywords": "top flop serie a, pagelle fantacalcio 5 giornata, voti fantacalcio, migliori fantacalcio 5 giornata"
        },
        {
            "route": "consigli-fantacalcio",
            "tab": "matchday_advice",
            "title": "Consigli Fantacalcio 6ª Giornata Serie A | Chi Schierare | Fanta Master AI",
            "desc": "Chi schierare nella 6ª giornata di Serie A: indici di schierabilità, titolarità, verifiche predittive e consigli ruolo per ruolo con intelligenza artificiale.",
            "keywords": "consigli fantacalcio 6 giornata, chi schierare 6 giornata, formazioni consigliate fantacalcio"
        },
        {
            "route": "chi-schiero",
            "tab": "chi_schiero",
            "title": "Chi Schiero? Comparatore 1vs1 Ballottaggi Fantacalcio | Fanta Master AI",
            "desc": "Risolvi i tuoi dubbi di formazione per la prossima giornata: confronto testa a testa, xFM, facilità del calendario, xGA difesa rivale e verdetto percentuale immediato.",
            "keywords": "chi schiero, chi schierare fantacalcio, ballottaggi fantacalcio, comparatore 1vs1 fantacalcio, consigli formazione serie a"
        },
        {
            "route": "football-analytics",
            "tab": "matrix",
            "title": "Football Analytics Serie A | Scatter Matrix xG, xA e Performance | Fanta Master AI",
            "desc": "Analisi avanzata e matrici di dispersione dei calciatori di Serie A: Expected Goals (xG), Expected Assists (xA), overperformance e metriche avanzate di rendimento.",
            "keywords": "football analytics serie a, scatter matrix fantacalcio, expected goals serie a, metriche avanzate fantacalcio"
        },
        {
            "route": "statistiche-serie-a",
            "tab": "stats",
            "title": "Statistiche Calciatori Serie A 2026/27 Avanzate & xG | Fanta Master AI",
            "desc": "Tabella completa con tutte le statistiche della Serie A 2026/27: presenze, minuti, gol, assist, ammonizioni, espulsioni, xG, xA e FantaMedia.",
            "keywords": "statistiche serie a 2026 2027, numeri fantacalcio, fantamedia calciatori, assist gol serie a"
        },
        {
            "route": "probabili-formazioni",
            "tab": "pitch",
            "title": "Probabili Formazioni Serie A 2026/27 & Ballottaggi 2D | Fanta Master AI",
            "desc": "Probabili formazioni delle 20 squadre di Serie A su campo tattico 2D interattivo, schemi dei club e percentuali di titolarità aggiornate.",
            "keywords": "probabili formazioni serie a, formazioni fantacalcio, titolari ballottaggi serie a, campo 2d formazioni"
        },
        {
            "route": "confronto-calciatori",
            "tab": "matchup",
            "title": "Confronto Calciatori Head-to-Head Serie A | Fanta Master AI",
            "desc": "Confronta testa a testa due calciatori di Serie A: statistiche incrociate, overall (OVR), radar chart, xG, rendimento e metriche predittive.",
            "keywords": "confronto calciatori fantacalcio, testa a testa calciatori, matchup 1vs1 serie a"
        },
        {
            "route": "top-11-ai",
            "tab": "ai_squads",
            "title": "5 Squadre Perfette AI (In Ricalibrazione Algoritmica) | Fanta Master AI",
            "desc": "Modulo di generazione 5 rose ideali in fase di riaddestramento. Consulta i consigli di giornata, il tabellone e le statistiche predittive Fanta Master AI.",
            "keywords": "top 11 fantacalcio, squadra ideale fantacalcio, 5 squadre perfette ai, consigli asta fantacalcio"
        },
        {
            "route": "scommesse-talenti",
            "tab": "gems",
            "title": "Talenti Nascosti & Scommesse Low-Cost Serie A | Fanta Master AI",
            "desc": "Scopri i talenti emergenti, le gemme nascoste e le scommesse a basso costo consigliate dall'algoritmo predittivo per il tuo Fantacalcio.",
            "keywords": "scommesse fantacalcio, talenti nascosti serie a, gemme fantacalcio, sleeper fantacalcio"
        }
    ]

    sitemap_urls = [
        f"{BASE_URL}/",
        f"{BASE_URL}/privacy-policy/",
        f"{BASE_URL}/infortunati-serie-a/",
        f"{BASE_URL}/rigoristi-serie-a/",
        f"{BASE_URL}/griglia-portieri/"
    ]

    if dash_content:
        for sec in SECTIONS_METADATA:
            route = sec["route"]
            tab = sec["tab"]
            title = sec["title"]
            desc = sec["desc"]
            sec_dir = os.path.join(DIST_DIR, route)
            os.makedirs(sec_dir, exist_ok=True)
            
            sec_html = dash_content
            sec_html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', sec_html, flags=re.DOTALL)
            sec_html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{desc}">', sec_html)
            head_inject = f"""    <link rel="canonical" href="{BASE_URL}/{route}/">\n    <script>window.INITIAL_TAB = '{tab}';</script>\n</head>"""
            sec_html = sec_html.replace('</head>', head_inject)
            
            with open(os.path.join(sec_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(sec_html)
            sitemap_urls.append(f"{BASE_URL}/{route}/")
            print(f"  ✓ Generata pagina Clean URL: dist/{route}/index.html")

    # 2d. Copia i dati JSON elaborati in dist/data per endpoint e fetch
    dist_data_dir = os.path.join(DIST_DIR, "data")
    os.makedirs(dist_data_dir, exist_ok=True)
    for json_name in ["processed_players_master.json", "top_flop_rounds.json", "gk_matrix_2026_27.json"]:
        src_json = os.path.join(ROOT_DIR, "data", "processed", json_name)
        if not os.path.exists(src_json):
            src_json = os.path.join(ROOT_DIR, json_name)
        if os.path.exists(src_json):
            shutil.copy(src_json, os.path.join(dist_data_dir, json_name))
    print("  ✓ Dati JSON elaborati copiati in dist/data/")

    # 3. Genera le 532 pagine calciatore complete
    calciatori_dir = os.path.join(DIST_DIR, "calciatore")
    os.makedirs(calciatori_dir, exist_ok=True)
    
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

    print(f"  ✓ Generate {player_count} schede calciatore complete di grafica, Radar SVG, Metriche Avanzate e Infortuni!")

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

    # 4b. Genera 20 Pagine Dedicate Club & Probabili Formazioni (Cluster Squadra)
    all_teams_list = sorted(list(tactical_db.keys()))
    team_count = 0
    for team_name, t_data in sorted(tactical_db.items()):
        t_slug = slugify(team_name)
        t_players = [p for p in players if (p.get("team") or "").lower() == team_name.lower()]
        t_html = generate_team_page(team_name, t_data, t_players, all_teams_list, injuries_db, BASE_URL)
        
        t_dir = os.path.join(DIST_DIR, "probabili-formazioni", t_slug)
        os.makedirs(t_dir, exist_ok=True)
        with open(os.path.join(t_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(t_html)
            
        sitemap_urls.append(f"{BASE_URL}/probabili-formazioni/{t_slug}/")
        team_count += 1
    print(f"  ✓ Generate {team_count} pagine squadra complete con Campo 2D, Titolari, Ballottaggi e Rosa in dist/probabili-formazioni/<squadra>/")

    # 4c. Genera Pagina Privacy Policy Ufficiale & GDPR
    priv_dir = os.path.join(DIST_DIR, "privacy-policy")
    os.makedirs(priv_dir, exist_ok=True)
    with open(os.path.join(priv_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(generate_privacy_policy_page())
    print("  ✓ Generata pagina Pillar: dist/privacy-policy/index.html")

    # 5. Genera Sitemap XML
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sitemap_urls:
        prio = "1.0" if url.endswith("/") and len(url.split("/")) == 4 else ("0.9" if ("serie-a" in url or "probabili-formazioni" in url) else "0.8")
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
