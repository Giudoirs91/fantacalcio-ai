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
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #f1f5f9;
    font-weight: 600;
    font-size: 12.5px;
    white-space: nowrap;
}
.diagnosis-icon {
    font-size: 14px;
    flex-shrink: 0;
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
"""
    return base_dashboard_css + "\n" + extra_seo_css

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

                <a href="{rel_path}" class="nav-btn-icon" style="text-decoration:none;" title="Torna al Listone &amp; Statistiche">
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
                        <a href="{rel_path}statistiche-serie-a/" class="dropdown-item">📊 Statistiche Serie A &amp; xG</a>
                        <a href="{rel_path}" class="dropdown-item">📋 Tabellone &amp; Listone Calciatori</a>
                        <a href="{rel_path}top-flop/" class="dropdown-item">⚡ Top &amp; Flop di Giornata</a>
                        <a href="{rel_path}football-analytics/" class="dropdown-item">📈 Matrice &amp; Scatter Analytics</a>
                        <a href="{rel_path}probabili-formazioni/" class="dropdown-item">⚽ Campo 2D &amp; Schemi Club</a>
                        <a href="{rel_path}confronto-calciatori/" class="dropdown-item">⚔️ Matchup 1vs1</a>
                        <a href="{rel_path}griglia-portieri/" class="dropdown-item">🧤 Griglia Portieri 38/38</a>
                    </div>
                </div>

                <!-- 2. AI & CONSIGLI -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAi">
                        <span>🧠</span> AI &amp; Consigli <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}consigli-fantacalcio/" class="dropdown-item">🎯 Chi Schierare Prossima Giornata</a>
                        <a href="{rel_path}top-11-ai/" class="dropdown-item">🧠 5 Squadre Perfette AI</a>
                        <a href="{rel_path}scommesse-talenti/" class="dropdown-item">🔮 Gemme &amp; Sleeper AI</a>
                        <div class="dropdown-divider"></div>
                        <a href="{rel_path}infortunati-serie-a/" class="dropdown-item">🩺 Infortunati &amp; Tempi di Recupero</a>
                        <a href="{rel_path}rigoristi-serie-a/" class="dropdown-item">🎯 Rigoristi &amp; Calci Piazzati</a>
                    </div>
                </div>

                <!-- 3. ASTA & MERCATO -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAuction">
                        <span>📊</span> Asta &amp; Mercato <span class="coming-soon-pill">In Arrivo</span> <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="{rel_path}" class="dropdown-item">📋 Tabellone &amp; Listone Completo</a>
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


from tools.seo_player_template import generate_player_page

def generate_injuries_pillar(players, injuries_db):
    active_players = [p for p in players if p.get("is_injured")]
    
    # Ordina cronologicamente per data di rientro (DD/MM/YYYY)
    def parse_return_date(player):
        d_str = str(player.get("infortunio_rientro") or "").strip()
        m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', d_str)
        if m:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return (year, month, day)
        return (9999, 12, 31)

    active_players.sort(key=lambda p: (parse_return_date(p), p.get("name", "")))
    
    total_injured = len(active_players)
    muscular_count = sum(1 for p in active_players if any(w in p.get("infortunio_motivo", "").lower() for w in ["muscol", "bicipite", "adduttore", "flessore", "polpaccio", "affaticamento", "coscia"]))
    fragile_count = sum(1 for p in active_players if p.get("fragility_tier") in ["CRISTALLO", "FRAGILE"])
    all_teams = sorted(list(set(p.get("team") for p in active_players if p.get("team"))))
    
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
        
        rows += f"""
        <tr class="injury-row" data-name="{clean_html(full_name.lower())}" data-team="{clean_html(team.lower())}" data-role="{role}" data-tier="{tier}">
            <td>
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
            <td>
                <div class="diagnosis-badge">
                    <span class="diagnosis-icon">🩺</span>
                    <span>{clean_html(motivo)}</span>
                </div>
            </td>
            <td>
                <span class="return-date-pill">📅 {clean_html(rientro)}</span>
            </td>
            <td>
                <span class="fragility-chip tier-{tier}">{tier}</span>
            </td>
            <td>
                <a href="../calciatore/{slug}/" class="btn-detail-link">Scheda &rarr;</a>
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
            </div>
        </div>

        <!-- GLASS TABLE -->
        <section class="pillar-table-card">
            <div class="table-responsive">
                <table class="seo-table" id="injuriesTable">
                    <thead>
                        <tr>
                            <th>Calciatore &amp; Ruolo</th>
                            <th>Diagnosi Infortunio</th>
                            <th>Rientro Stimato</th>
                            <th>Fragilità Clinica</th>
                            <th>Dettagli</th>
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
        function setRoleFilter(role, btn) {{
            currentRole = role;
            document.querySelectorAll('.pillar-filter-chip').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            filterInjuries();
        }}

        function filterInjuries() {{
            const search = (document.getElementById('injurySearch').value || '').toLowerCase().trim();
            const team = document.getElementById('injuryTeamFilter').value;
            const rows = document.querySelectorAll('#injuriesTable tbody tr');

            rows.forEach(tr => {{
                const rName = tr.getAttribute('data-name') || '';
                const rTeam = tr.getAttribute('data-team') || '';
                const rRole = tr.getAttribute('data-role') || '';
                const rTier = tr.getAttribute('data-tier') || '';

                const matchesSearch = !search || rName.includes(search) || rTeam.includes(search);
                const matchesTeam = team === 'all' || rTeam === team;
                const matchesRole = currentRole === 'ALL' || rRole === currentRole;

                if (matchesSearch && matchesTeam && matchesRole) {{
                    tr.style.display = '';
                }} else {{
                    tr.style.display = 'none';
                }}
            }});
        }}
    </script>
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
                <div class="takers-flow">{takers_html}</div>
            </td>
            <td>
                <div class="setpiece-tag-group">{pun_html}</div>
            </td>
            <td>
                <div class="setpiece-tag-group">{cor_html}</div>
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
    for c in couples[:30]:
        t1 = c.get("team1", "")
        t2 = c.get("team2", "")
        score = c.get("score", 0)
        conflicts = c.get("conflicts", 0)
        
        conflict_badge = f'<span style="background:rgba(16,185,129,0.15);border:1px solid #10b981;color:#34d399;padding:4px 10px;border-radius:8px;font-weight:800;font-size:12px;">⭐ {conflicts} contemporaneità</span>' if conflicts <= 1 else f'<span style="background:rgba(245,158,11,0.15);border:1px solid #f59e0b;color:#fbbf24;padding:4px 10px;border-radius:8px;font-weight:700;font-size:12px;">{conflicts} contemporaneità</span>'
        
        rows += f"""
        <tr>
            <td>
                <div style="display:flex;align-items:center;gap:10px;">
                    <div class="team-badge-circle" style="color:#38bdf8;">🧤</div>
                    <div>
                        <strong style="color:#fff;font-size:14.5px;">{clean_html(t1)}</strong>
                        <span style="color:#64748b;margin:0 6px;">+</span>
                        <strong style="color:#fff;font-size:14.5px;">{clean_html(t2)}</strong>
                    </div>
                </div>
            </td>
            <td style="text-align:center;">{conflict_badge}</td>
            <td style="text-align:center;"><span style="color:#38bdf8;font-weight:900;font-size:15px;font-family:'Outfit',sans-serif;">{score} pt</span></td>
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
                    <div class="pillar-kpi-num">20</div>
                    <div class="pillar-kpi-label">Portieri Titolari</div>
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
                    <div class="pillar-kpi-num">Top 30</div>
                    <div class="pillar-kpi-label">Incroci Consigliati</div>
                </div>
            </div>
            <div class="pillar-kpi-card">
                <div class="pillar-kpi-icon" style="color:#a855f7;">🛡️</div>
                <div>
                    <div class="pillar-kpi-num">0-1</div>
                    <div class="pillar-kpi-label">Minime Sovrapposizioni</div>
                </div>
            </div>
        </section>

        <!-- GLASS TABLE -->
        <section class="pillar-table-card">
            <div class="table-responsive">
                <table class="seo-table">
                    <thead>
                        <tr>
                            <th>Coppia di Club</th>
                            <th style="text-align:center;">Gare Contemporanee Trasferta</th>
                            <th style="text-align:center;">Indice Efficacia Incrocio</th>
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
            <a href="../griglia-portieri/" class="btn-cta-main">Apri la Griglia Interattiva 🚀</a>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Algoritmo Incroci Portieri Serie A</p>
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
            "route": "football-analytics",
            "tab": "matrix",
            "title": "Football Analytics Serie A | Scatter Matrix xG, xA e Performance | Fanta Master AI",
            "desc": "Analisi avanzata e matrici di dispersione dei calciatori di Serie A: Expected Goals (xG), Expected Assists (xA), overperformance e statistiche FotMob.",
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
            "title": "Top 11 AI & 5 Squadre Perfette Fantacalcio | Fanta Master AI",
            "desc": "Le formazioni ideali generate dall'algoritmo predittivo per ogni budget e strategia d'asta: Top Player, Low Cost, Equilibrata, Giovani Talenti.",
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
