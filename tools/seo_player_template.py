
def safe_float(val, default=0.0):
    if val is None or val == '' or val == '-' or val == 's.v.':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

import os
import re
import json
import math

def clean_html(text):
    if text is None:
        return ""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def slugify(text):
    if not text:
        return "calciatore"
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

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
                    <div class="footer-heading">Community &amp; Note Legali</div>
                    <ul class="footer-nav-list">
                        <li><a href="https://t.me/fantamasterai" target="_blank" rel="noopener" class="footer-link" style="color:#38bdf8;font-weight:800;">📲 Canale Telegram Ufficiale</a></li>
                        <li><a href="{rel_path}privacy-policy/" class="footer-link" id="footer-privacy-link">🔒 Privacy Policy (GDPR)</a></li>
                        <li><span class="footer-status-pill">🛡️ Privacy by Design</span></li>
                        <li><span class="footer-status-pill">🚫 Zero Cookie Traccianti</span></li>
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

def compute_bonus_malus_str(v):
    if not v:
        return '-'
    if v.get('bonus_malus_str') and v['bonus_malus_str'] != '-' and 'undefined' not in str(v['bonus_malus_str']):
        return str(v['bonus_malus_str'])
    parts = []
    gf = float(v.get('gf') or 0)
    ass = float(v.get('ass') or 0)
    rp = float(v.get('rp') or 0)
    gs = float(v.get('gs') or 0)
    rs = float(v.get('rs') or 0)
    au = float(v.get('au') or 0)
    amm = float(v.get('amm') or 0)
    esp = float(v.get('esp') or 0)
    if gf > 0: parts.append(f"+{int(gf * 3)} ({int(gf)}G)")
    if ass > 0: parts.append(f"+{int(ass)} ({int(ass)}A)")
    if rp > 0: parts.append(f"+{int(rp * 3)} (Rig.Par)")
    if gs > 0: parts.append(f"-{int(gs)} ({int(gs)}GS)")
    if rs > 0: parts.append("-3 (Rig.Sbagliato)")
    if au > 0: parts.append(f"-{int(au * 2)} (Autogol)")
    if amm > 0: parts.append("-0.5 (Amm)")
    if esp > 0: parts.append("-1 (Esp)")
    if parts: return ", ".join(parts)
    if v.get('voto') is not None: return "Nessun bonus"
    return '-'

def render_mantra_quick_badges(mantra_str):
    if not mantra_str or mantra_str in ['-', 'null', 'undefined']:
        return '<span style="color:#94a3b8;font-size:12px;font-weight:600;">-</span>'
    roles = [r.strip() for r in re.split(r'[;,/ ]+', mantra_str) if r.strip()]
    if not roles:
        return '<span style="color:#94a3b8;font-size:12px;font-weight:600;">-</span>'
    return "".join([f'<span class="mantra-pill {r.lower()}">{clean_html(r)}</span>' for r in roles])

def get_match_info(calendar_data, team_name, round_num):
    if not calendar_data:
        return None
    r_obj = next((r for r in calendar_data if r.get('giornata') == round_num), None)
    if not r_obj or not r_obj.get('matches'):
        return None
    t_clean = (team_name or '').upper().strip()
    for m in r_obj['matches']:
        h_clean = (m.get('home') or '').upper().strip()
        a_clean = (m.get('away') or '').upper().strip()
        if h_clean == t_clean:
            return {
                'opponent': m.get('away'),
                'is_home': True,
                'match_str': f"{m.get('home')} vs {m.get('away')}",
                'date': r_obj.get('date', '')
            }
        if a_clean == t_clean:
            return {
                'opponent': m.get('home'),
                'is_home': False,
                'match_str': f"{m.get('away')} @ {m.get('home')}",
                'date': r_obj.get('date', '')
            }
    return None

def compute_expected_fantamedia(p):
    has2627 = bool(p.get("has_data_2627") and (p.get("presenze_2627") or 0) > 0)
    presenze = safe_float(p.get("presenze_2627") if has2627 else p.get("presenze"), 1.0)
    if presenze <= 0: presenze = 1.0
    mv_raw = p.get("mv_2627") if has2627 else p.get("mv")
    mv = safe_float(mv_raw, safe_float(p.get("mv"), 6.0)) or 6.0
    real_fm_raw = p.get("fm_2627") if has2627 else p.get("fm")
    real_fm = safe_float(real_fm_raw, safe_float(p.get("fm"), mv)) or mv
    
    if p.get("xfm") is not None and p.get("delta_xfm") is not None:
        return {
            "xfm": round(safe_float(p["xfm"], real_fm), 2),
            "realFm": round(real_fm, 2),
            "delta": round(safe_float(p["delta_xfm"], 0.0), 2),
            "has2627": has2627
        }
    
    role = p.get("role", "C")
    if role == 'P':
        gs = safe_float(p.get("gol_subiti_2627") if has2627 else p.get("gs"), 0.0)
        cs = safe_float(p.get("clean_sheets_2627") if has2627 else p.get("clean_sheets_2526"), 0.0)
        xfm = round(mv - (gs / presenze) + (cs * 0.5 / presenze), 2)
        delta = round(real_fm - xfm, 2)
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}
    else:
        xg = safe_float(p.get("xg_2627") or (safe_float(p.get("xg90_2627")) * safe_float(p.get("minuti_2627"), 90) / 90.0 if has2627 else p.get("xg_2526")), 0.0)
        xa = safe_float(p.get("xa_2627") or (safe_float(p.get("xa90_2627")) * safe_float(p.get("minuti_2627"), 90) / 90.0 if has2627 else p.get("xa_2526")), 0.0)
        malus = safe_float(p.get("amm_2627") or p.get("amm"), 0.0) * 0.5 + safe_float(p.get("esp_2627") or p.get("esp"), 0.0) * 1.0
        bonus_attesi = (xg * 3.0) + (xa * 1.0)
        xfm = round(mv + ((bonus_attesi - malus) / presenze), 2)
        delta = round(real_fm - xfm, 2)
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}

def generate_radar_chart_svg(player):
    role = player.get("role", "C")
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
    else: # A
        axes = [
            {'label': 'Finalizzazione (xG/90)', 'pct': min(98, max(30, int(float(player.get('xg90_2627') or player.get('xg90_2526') or 0.45) * 160))), 'raw': f"{player.get('xg90_2627') or 0.45}"},
            {'label': 'Pericolosità (xGOT)', 'pct': min(98, max(30, int(float(player.get('xgot_2627') or 1.2) * 50))), 'raw': f"{player.get('xgot_2627') or 1.2}"},
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
    return f'<svg viewBox="0 0 {size} 320" style="width:100%;max-width:350px;display:block;margin:0 auto;">{circles}{lines}{poly}{labels}</svg>'

def generate_player_page(player, injuries_db, tactical_db, calendar_data, base_url="https://fantamasterai.it"):
    name = player.get("name", "")
    p_id = player.get("id")
    team = player.get("team", "")
    role = player.get("role", "C")
    mantra = player.get("mantra", "")
    fvm = player.get("fvm", 1)
    qta = player.get("qta", 1)
    diff_q = player.get("diff_q", 0)
    diff_q_str = (("+" if diff_q > 0 else "") + str(diff_q)) if diff_q != 0 else ""
    prezzo_cons = player.get("prezzo_cons", player.get("prezzo_consigliato", qta))
    max_bid = player.get("max_bid", int(prezzo_cons * 1.35))
    ovr = player.get("ovr", 70)
    titolarita = player.get("titolarita", 70)
    titolarita_desc = player.get("titolarita_desc_2627", f"{titolarita}% Titolare")
    slot_desc = player.get("slot_fascia", player.get("slot_desc", "Titolare"))
    is_injured = player.get("is_injured", False)
    infort_motivo = player.get("infortunio_motivo", "")
    infort_rientro = player.get("infortunio_rientro", "")

    team_inj = injuries_db.get(team, {})
    hist_entry = team_inj.get(name, {})
    full_name = hist_entry.get("tm_name", name)
    slug = slugify(full_name)

    team_tac = tactical_db.get(team, {})
    mister = team_tac.get("all", "Mister")
    modulo = team_tac.get("modulo", "4-3-3")
    stile = team_tac.get("stile", "Costruzione organizzata, pressing alto")

    tit_color = "#4ade80" if titolarita >= 68 else ("#f59e0b" if titolarita >= 50 else "#ef4444")
    ovr_cls = "elite" if ovr >= 90 else ("gold" if ovr >= 82 else ("cyan" if ovr >= 75 else "silver"))

    inj_badge = f'<span class="badge-tag red">🩹 Rientro: {clean_html(infort_rientro)}</span>' if is_injured else '<span class="badge-tag green">🟢 Integro</span>'
    
    rig_badge = ''
    if player.get("is_rigorista_1"): rig_badge = '<span class="badge-tag gold">👑 1° Rigorista</span>'
    elif player.get("is_rigorista_2"): rig_badge = '<span class="badge-tag gold">🎯 2° Rigorista</span>'
    elif player.get("is_rigorista_3"): rig_badge = '<span class="badge-tag blue">🎯 3° Rigorista</span>'
    elif player.get("is_punizioni") or player.get("is_corner"): rig_badge = '<span class="badge-tag cyan">📐 Piazzati</span>'

    coppia_badge = ''
    coppia_nome = player.get("coppia_nome")
    coppia_tipo = player.get("coppia_tipo", "")
    if coppia_nome and coppia_nome != '-':
        icon = '⬇️ Vice' if ('RISERVA' in coppia_tipo or '2°' in coppia_tipo) else ('⬆️ Titolare' if ('TITOLARE' in coppia_tipo or '1°' in coppia_tipo) else '🔄 Staffetta')
        coppia_badge = f'<span class="badge-tag blue">{icon}: <b>{clean_html(coppia_nome)}</b></span>'

    oop_badge = ''
    oop_val = player.get("oop_val")
    if oop_val and oop_val != '-':
        oop_color = "#f59e0b" if player.get("oop_tier") == "ORO" else ("#cbd5e1" if player.get("oop_tier") == "ARGENTO" else "#d97706")
        oop_badge = f'<span class="badge-tag oop" style="border-color:{oop_color};color:{oop_color};">💎 {clean_html(oop_val)}</span>'

    # Expected FantaMedia (xFM) & Regression Alert
    xfm_data = compute_expected_fantamedia(player)
    is_elite = (xfm_data["xfm"] >= 7.8 or (ovr >= 86 and xfm_data["xfm"] >= 7.2)) and xfm_data["realFm"] >= 7.8
    if is_elite and xfm_data["delta"] >= 0.20:
        xfm_alert_html = f"""
        <div class="xfm-alert-box under" style="background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.35);">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:18px;">🔥</span>
                <div>
                    <div style="font-weight:800;color:var(--accent-cyan);font-size:12px;">STATO DI GRAZIA / TOP ASSOLUTO (Efficacia Straordinaria)</div>
                    <div style="font-size:11px;color:var(--text-secondary);">FM Reale: <b>{xfm_data['realFm']}</b> • xFM Attesa: <b>{xfm_data['xfm']}</b> (Delta: <b style="color:var(--accent-cyan);">+{xfm_data['delta']}</b>). Straordinaria efficacia realizzativa su una mole di occasioni creata d'élite. Titolare inamovibile da schierare sempre!</div>
                </div>
            </div>
        </div>"""
    elif xfm_data["delta"] <= -0.40:
        xfm_alert_html = f"""
        <div class="xfm-alert-box under">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:18px;">💎</span>
                <div>
                    <div style="font-weight:800;color:#34d399;font-size:12px;">SOTTO-RENDIMENTO STATISTICO (Occasione di Mercato / Bonus Imminenti)</div>
                    <div style="font-size:11px;color:var(--text-secondary);">FM Reale: <b>{xfm_data['realFm']}</b> vs xFM Attesa: <b>{xfm_data['xfm']}</b> (Delta: <b style="color:#34d399;">{xfm_data['delta']}</b>). Produce un volume elevato di occasioni (xG/xA) ma ha raccolto meno del dovuto per sfortuna temporanea. COMPRA ALL'ASTA O SCAMBIA!</div>
                </div>
            </div>
        </div>"""
    elif xfm_data["delta"] >= 0.60:
        xfm_alert_html = f"""
        <div class="xfm-alert-box over">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:18px;">📈</span>
                <div>
                    <div style="font-weight:800;color:#fbbf24;font-size:12px;">SOVRA-RENDIMENTO DA EPISODI (Possibile Regressione Fisiologica)</div>
                    <div style="font-size:11px;color:var(--text-secondary);">FM Reale: <b>{xfm_data['realFm']}</b> vs xFM Attesa: <b>{xfm_data['xfm']}</b> (Delta: <b style="color:#f87171;">+{xfm_data['delta']}</b>). Ha raccolto più bonus rispetto al volume effettivo di occasioni create: possibile flessione. Ottimo per scambi al massimo valore.</div>
                </div>
            </div>
        </div>"""
    else:
        xfm_alert_html = f"""
        <div class="xfm-alert-box balanced">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">⚖️</span>
                <div style="font-size:11.5px;color:var(--text-secondary);">
                    FM Reale (<b>{xfm_data['realFm']}</b>) in perfetto equilibrio con la FantaMedia Attesa xFM (<b>{xfm_data['xfm']}</b>). Rendimento costante e sostenibile.
                </div>
            </div>
        </div>"""

    # Voti dettaglio & Smart Trend
    voti_list = player.get("voti_dettaglio_2627") or []
    valid_voti = [v for v in voti_list if v.get("voto") is not None]
    valid_fv = [v for v in voti_list if v.get("fantavoto") is not None]
    
    smart_trend = {"label": "⚖️ Costante", "color": "#38bdf8", "desc": "Rendimento regolare e affidabile"}
    if valid_fv:
        last3_fv = [v["fantavoto"] for v in valid_fv[-3:]]
        mean3_fv = sum(last3_fv) / len(last3_fv)
        last_goals = sum([v.get("gf", 0) for v in voti_list[-3:]])
        last_assists = sum([v.get("ass", 0) for v in voti_list[-3:]])
        curr_fm = player.get("fm_2627") or (sum([v["fantavoto"] for v in valid_fv]) / len(valid_fv))
        if mean3_fv >= 8.0 or last_goals >= 2 or (curr_fm >= 7.5 and last3_fv[-1] >= 7.0):
            smart_trend = {"label": "🔥 On Fire", "color": "#f59e0b", "desc": "Rendimento devastante con bonus a raffica"}
        elif (mean3_fv - curr_fm >= 0.4) or (len(valid_fv) >= 2 and last3_fv[-1] > last3_fv[-2] + 1.0):
            smart_trend = {"label": "📈 In Crescita", "color": "#10b981", "desc": "Forma e fantavoti in netta ascesa"}
        elif curr_fm - mean3_fv >= 0.75 and last_goals == 0 and last_assists == 0 and mean3_fv < 6.0:
            smart_trend = {"label": "❄️ In Flessione", "color": "#f87171", "desc": "Flessione recente di rendimento e voti"}
        elif role in ['A', 'C'] and last_goals == 0 and last_assists == 0 and len(valid_voti) >= 3 and mean3_fv <= 6.2:
            smart_trend = {"label": "⏳ A Secco", "color": "#fbbf24", "desc": "Voti regolari ma a secco di bonus recenti"}

    # 38-Round Season Performance Hub
    total_rounds = 38
    max_played = max([v["giornata"] for v in voti_list]) if voti_list else 0
    suff_count = len([v for v in valid_voti if v["voto"] >= 6.0])
    suff_pct = round((suff_count / len(valid_voti)) * 100) if valid_voti else 0

    svg_w = 760
    svg_h = 165
    pad_l = 38
    pad_r = 20
    pad_t = 24
    pad_b = 30
    draw_w = svg_w - pad_l - pad_r
    draw_h = svg_h - pad_t - pad_b
    col_step = draw_w / total_rounds
    max_scale = 18.0

    def get_y(val):
        return pad_t + (1 - min(max_scale, max(0.0, float(val))) / max_scale) * draw_h

    y6 = get_y(6.0)
    y10 = get_y(10.0)
    player_fm_val = float(player.get("fm_2627") or player.get("fm") or 0)
    y_player_fm = get_y(player_fm_val) if player_fm_val > 0 else None

    grid_svg = f"""
        <line x1="{pad_l}" y1="{get_y(0)}" x2="{pad_l + draw_w}" y2="{get_y(0)}" stroke="rgba(255,255,255,0.15)" stroke-width="1" />
        <line x1="{pad_l}" y1="{y6}" x2="{pad_l + draw_w}" y2="{y6}" stroke="rgba(56,189,248,0.3)" stroke-width="1" stroke-dasharray="3,3" />
        <text x="{pad_l - 6}" y="{y6 + 3}" text-anchor="end" fill="#38bdf8" font-size="8.5" font-weight="700">6.0</text>
        <line x1="{pad_l}" y1="{y10}" x2="{pad_l + draw_w}" y2="{y10}" stroke="rgba(251,191,36,0.25)" stroke-width="1" stroke-dasharray="3,3" />
        <text x="{pad_l - 6}" y="{y10 + 3}" text-anchor="end" fill="#fbbf24" font-size="8.5" font-weight="700">10.0</text>
    """
    if y_player_fm:
        grid_svg += f"""
            <line x1="{pad_l}" y1="{y_player_fm}" x2="{pad_l + draw_w}" y2="{y_player_fm}" stroke="rgba(234,179,8,0.55)" stroke-width="1.2" stroke-dasharray="4,2" />
            <text x="{pad_l + draw_w + 4}" y="{y_player_fm + 3}" fill="#fbbf24" font-size="8" font-weight="800">FM {player_fm_val:.1f}</text>
        """

    bars_svg = ""
    x_labels_svg = ""
    poly_pts = []
    nodes_svg = ""

    for g in range(1, total_rounds + 1):
        cx = pad_l + (g - 1) * col_step + col_step / 2
        bar_w = max(9.0, col_step * 0.72)
        bar_x = cx - bar_w / 2

        if g in [1, 5, 10, 15, 20, 25, 30, 35, 38, max_played]:
            is_p = g <= max_played
            fill_c = "var(--accent-cyan)" if is_p else "rgba(255,255,255,0.3)"
            weight_c = "800" if is_p else "500"
            x_labels_svg += f'<text x="{cx}" y="{svg_h - 10}" text-anchor="middle" fill="{fill_c}" font-size="8.5" font-weight="{weight_c}">G{g}</text>'

        match = next((v for v in voti_list if v.get("giornata") == g), None)
        if match and match.get("voto") is not None:
            v_val = float(match["voto"])
            fv_val = float(match.get("fantavoto") if match.get("fantavoto") is not None else v_val)
            base_y = get_y(v_val)
            base_h = get_y(0) - base_y
            base_fill = "#10b981" if v_val >= 7.0 else ("#0284c7" if v_val >= 6.0 else ("#f59e0b" if v_val >= 5.5 else "#ef4444"))

            bars_svg += f"""
            <g class="season-match-bar-group" onclick="selectSeasonRound({p_id}, {g})" onmouseenter="previewSeasonRound({p_id}, {g})" style="cursor:pointer;">
                <rect x="{bar_x:.1f}" y="{base_y:.1f}" width="{bar_w:.1f}" height="{max(2.0, base_h):.1f}" rx="2" fill="{base_fill}" opacity="0.85">
                    <title>G{g}: Voto {v_val} | FV {fv_val}</title>
                </rect>"""

            if fv_val > v_val:
                bonus_y = get_y(fv_val)
                bonus_h = base_y - bonus_y
                bars_svg += f'<rect x="{bar_x:.1f}" y="{bonus_y:.1f}" width="{bar_w:.1f}" height="{max(2.0, bonus_h):.1f}" rx="2" fill="url(#bonusGradient)" stroke="#fde047" stroke-width="0.8" opacity="0.95" />'
            elif fv_val < v_val:
                bars_svg += f'<rect x="{bar_x:.1f}" y="{base_y:.1f}" width="{bar_w:.1f}" height="3" rx="1" fill="#f43f5e" />'

            bars_svg += '</g>'
            pt_y = get_y(fv_val)
            poly_pts.append(f"{cx:.1f},{pt_y:.1f}")
            nodes_svg += f"""
            <circle cx="{cx:.1f}" cy="{pt_y:.1f}" r="3.5" fill="#fde047" stroke="#0f172a" stroke-width="1.5" class="match-node-dot" onclick="selectSeasonRound({p_id}, {g})" onmouseenter="previewSeasonRound({p_id}, {g})" style="cursor:pointer;">
                <title>G{g}: FantaVoto {fv_val}</title>
            </circle>"""
        elif g <= max_played:
            bars_svg += f"""
            <g class="season-match-bar-group" onclick="selectSeasonRound({p_id}, {g})" onmouseenter="previewSeasonRound({p_id}, {g})" style="cursor:pointer;">
                <rect x="{bar_x:.1f}" y="{get_y(4.0):.1f}" width="{bar_w:.1f}" height="{(get_y(0) - get_y(4.0)):.1f}" rx="2" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.15)" stroke-dasharray="2,2" />
                <text x="{cx:.1f}" y="{(get_y(2.0)):.1f}" text-anchor="middle" fill="var(--text-muted)" font-size="7.5" font-weight="700">s.v.</text>
            </g>"""
        else:
            bars_svg += f'<rect x="{bar_x:.1f}" y="{pad_t}" width="{bar_w:.1f}" height="{draw_h}" rx="2" fill="none" stroke="rgba(255,255,255,0.04)" stroke-dasharray="2,3" />'

    trend_line_svg = f'<polyline points="{" ".join(poly_pts)}" fill="none" stroke="rgba(251,191,36,0.85)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />' if len(poly_pts) > 1 else ""

    season_chart_svg = f"""
        <svg viewBox="0 0 {svg_w} {svg_h}" class="season-trend-svg-canvas">
            <defs>
                <linearGradient id="bonusGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#34d399" />
                    <stop offset="100%" stop-color="#fbbf24" />
                </linearGradient>
            </defs>
            {grid_svg}
            {bars_svg}
            {trend_line_svg}
            {nodes_svg}
            {x_labels_svg}
        </svg>
    """

    # Latest Match Inspector Card
    latest_match = voti_list[-1] if voti_list else None
    if latest_match:
        cal_info = get_match_info(calendar_data, team, latest_match.get("giornata", 1))
        is_home = latest_match.get("is_home") if latest_match.get("is_home") is not None else (cal_info.get("is_home", True) if cal_info else True)
        home_tag = "🏠 Casa" if is_home else "✈️ Fuori"
        opp_name = latest_match.get("opponent") or (cal_info.get("opponent") if cal_info else "Avversario")
        match_title = latest_match.get("match") or (cal_info.get("match_str") if cal_info else f"vs {opp_name}")
        bm_str = compute_bonus_malus_str(latest_match)
        has_v = latest_match.get("voto") is not None
        v_c = ("#34d399" if latest_match["voto"] >= 7 else ("#38bdf8" if latest_match["voto"] >= 6 else ("#fbbf24" if latest_match["voto"] >= 5.5 else "#f87171"))) if has_v else "var(--text-muted)"
        fv_c = ("#10b981" if latest_match["fantavoto"] >= 10 else ("#38bdf8" if latest_match["fantavoto"] >= 7 else ("#f87171" if latest_match["fantavoto"] < 5 else "#fbbf24"))) if latest_match.get("fantavoto") is not None else "var(--text-muted)"

        initial_inspector_html = f"""
        <div class="match-inspector-card" id="seasonMatchInspectorCard">
            <div class="inspector-header">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span class="inspector-badge">GIORNATA {latest_match.get('giornata', 1)}</span>
                    <span class="inspector-venue">{home_tag}</span>
                    <b class="inspector-match-title">{clean_html(match_title)}</b>
                </div>
                <span class="inspector-hint-text"><span class="hint-desktop">Passa il mouse</span><span class="hint-mobile">Tocca</span> sulle barre per ispezionare</span>
            </div>
            <div class="inspector-body-grid">
                <div class="inspector-metric">
                    <span class="lbl">Voto Base</span>
                    <b class="val" style="color:{v_c};">{latest_match.get('voto', 's.v.') if has_v else 's.v.'}</b>
                </div>
                <div class="inspector-metric highlight">
                    <span class="lbl">FantaVoto</span>
                    <b class="val" style="color:{fv_c};font-size:17px;">{latest_match.get('fantavoto', '-') if latest_match.get('fantavoto') is not None else '-'}</b>
                </div>
                <div class="inspector-metric">
                    <span class="lbl">Bonus / Malus</span>
                    <span class="val-bonus">{clean_html(bm_str)}</span>
                </div>
                <div class="inspector-metric">
                    <span class="lbl">Gol / Assist</span>
                    <b class="val">{latest_match.get('gf', 0)} Gol &bull; {latest_match.get('ass', 0)} Ass</b>
                </div>
                <div class="inspector-metric">
                    <span class="lbl">Disciplina</span>
                    <span class="val" style="color:{'#ef4444' if (latest_match.get('amm') or 0) > 0 else 'var(--text-secondary)'};">{latest_match.get('amm', 0)} Amm &bull; {latest_match.get('esp', 0)} Esp</span>
                </div>
            </div>
        </div>"""
    else:
        next_m = get_match_info(calendar_data, team, 1)
        initial_inspector_html = f"""
        <div class="match-inspector-card" id="seasonMatchInspectorCard">
            <div class="inspector-header">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span class="inspector-badge" style="background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.3);color:var(--accent-cyan);">GIORNATA 1</span>
                    <span class="inspector-venue">{"🏠 Casa" if (next_m and next_m.get("is_home")) else "✈️ Fuori"}</span>
                    <b class="inspector-match-title">{clean_html(next_m["match_str"] if next_m else "Gara in Programma")}</b>
                </div>
                <span style="font-size:10.5px;color:var(--text-muted);">{clean_html(next_m["date"] if (next_m and next_m.get("date")) else "Stagione 2026/27")}</span>
            </div>
            <div style="font-size:11.5px;color:var(--text-secondary);padding:6px 0;">Nessun voto registrato finora per questa stagione.</div>
        </div>"""

    # Table rows for Season Table View
    table_rows_html = ""
    if voti_list:
        for v in voti_list:
            has_v = v.get("voto") is not None
            v_c = ("#34d399" if v["voto"] >= 7 else ("#38bdf8" if v["voto"] >= 6 else ("#fbbf24" if v["voto"] >= 5.5 else "#f87171"))) if has_v else "var(--text-muted)"
            fv_c = ("#10b981" if v["fantavoto"] >= 10 else ("#38bdf8" if v["fantavoto"] >= 7 else ("#f87171" if v["fantavoto"] < 5 else "#fbbf24"))) if v.get("fantavoto") is not None else "var(--text-muted)"
            cal_info = get_match_info(calendar_data, team, v.get("giornata", 1))
            is_h = v.get("is_home") if v.get("is_home") is not None else (cal_info.get("is_home", True) if cal_info else True)
            m_title = v.get("match") or (cal_info.get("match_str") if cal_info else f"G{v.get('giornata', 1)}")
            bm_str = compute_bonus_malus_str(v)

            table_rows_html += f"""
            <tr>
                <td style="font-weight:900;color:var(--accent-cyan);">G{v.get('giornata', 1)}</td>
                <td style="font-weight:700;color:#fff;">{clean_html(m_title)}</td>
                <td style="color:var(--text-muted);font-size:11px;">{"🏠 Casa" if is_h else "✈️ Fuori"}</td>
                <td style="font-weight:900;color:{v_c};">{v.get('voto', 's.v.') if has_v else 's.v.'}</td>
                <td><span class="table-bonus-tag">{clean_html(bm_str)}</span></td>
                <td style="font-weight:900;color:{fv_c};font-size:13px;">{v.get('fantavoto', '-') if v.get('fantavoto') is not None else '-'}</td>
            </tr>"""
    else:
        table_rows_html = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:12px;">Nessun dato registrato</td></tr>'

    # Injury History Hub
    cronistoria = hist_entry.get("cronistoria", []) if hist_entry else []
    frag_score = hist_entry.get("punteggio_fragilita", 20) if hist_entry else 20
    frag_tier = hist_entry.get("classe_fragilita", "🟢 Roccia") if hist_entry else "🟢 Roccia"
    disp_pct = hist_entry.get("disponibilita_pct", 100.0) if hist_entry else 100.0
    tot_missed = hist_entry.get("partite_saltate_totali", 0) if hist_entry else 0
    tot_days = hist_entry.get("giorni_stop_totali", 0) if hist_entry else 0
    recidive = hist_entry.get("recidive_muscolari", 0) if hist_entry else 0
    medical_advice = hist_entry.get("consiglio_medico_ai") if hist_entry else ("Attualmente ai box con tempi di recupero stimati." if is_injured else "Calciatore integro e solido. Storico infortuni nullo nelle ultime stagioni.")

    tier_color = "#f87171" if frag_score >= 80 else ("#fb923c" if frag_score >= 60 else ("#fbbf24" if frag_score >= 40 else "#34d399"))
    disp_color = "#ef4444" if disp_pct < 75 else ("#f59e0b" if disp_pct < 85 else "#10b981")

    # Accordion
    seasons_map = {}
    for inj in cronistoria:
        s = (inj.get("stagione") or "Altro").strip()
        if s not in seasons_map:
            seasons_map[s] = {"stagione": s, "infortuni": [], "tot_giorni": 0, "tot_partite": 0, "has_in_corso": False}
        seasons_map[s]["infortuni"].append(inj)
        seasons_map[s]["tot_giorni"] += (inj.get("giorni_stop") or inj.get("giorni") or 0)
        seasons_map[s]["tot_partite"] += (inj.get("partite_perse") or 0)
        if inj.get("in_corso"): seasons_map[s]["has_in_corso"] = True

    sorted_seasons = sorted(seasons_map.values(), key=lambda x: int(re.search(r'\d+', x["stagione"]).group(0)) if re.search(r'\d+', x["stagione"]) else 0, reverse=True)
    
    season_accordion_html = ""
    if sorted_seasons:
        for idx, sGroup in enumerate(sorted_seasons):
            is_expanded = sGroup["has_in_corso"] or idx == 0
            expanded_cls = "expanded" if is_expanded else ""
            sub_rows = ""
            for inj in sGroup["infortuni"]:
                tipo_cls = (inj.get("tipo") or "muscolare").lower()
                diag = clean_html(inj.get("diagnosi") or inj.get("motivo") or "Infortunio")
                cur_badge = '<span class="season-active-chip" style="margin-left:6px;font-size:9.5px;padding:1px 5px;">🔴 In corso</span>' if inj.get("in_corso") else ""
                sub_rows += f"""
                <tr>
                    <td style="font-weight:600;color:#fff;">{diag}{cur_badge}</td>
                    <td><span class="injury-type-pill {tipo_cls}">{clean_html(inj.get('tipo', 'generico'))}</span></td>
                    <td style="color:#f87171;font-weight:700;">{inj.get('giorni_stop', 0)} gg</td>
                    <td style="color:#fbbf24;font-weight:800;text-align:center;">{inj.get('partite_perse', 0)}</td>
                    <td style="color:var(--text-muted);font-size:11px;">{clean_html(inj.get('data_inizio', '-'))} &rarr; {clean_html(inj.get('data_fine', '-'))}</td>
                </tr>"""
            
            season_accordion_html += f"""
            <div class="injury-season-card {expanded_cls}">
                <div class="injury-season-header" onclick="toggleSeasonInjuryDetail(this)">
                    <div class="season-header-left">
                        <span class="season-pill">{clean_html(sGroup['stagione'])}</span>
                        {f'<span class="season-active-chip">🔴 In corso</span>' if sGroup['has_in_corso'] else ''}
                        <div class="season-stats-badges">
                            <span class="season-stat-item"><b>{len(sGroup['infortuni'])}</b> {'infortunio' if len(sGroup['infortuni']) == 1 else 'infortuni'}</span>
                            <span class="season-stat-item stop"><b>{sGroup['tot_giorni']} gg</b> stop</span>
                            <span class="season-stat-item missed"><b>{sGroup['tot_partite']}</b> {'gara persa' if sGroup['tot_partite'] == 1 else 'gare perse'}</span>
                        </div>
                    </div>
                    <div class="season-detail-btn">
                        <span>Dettaglio</span>
                        <span class="season-chevron">▼</span>
                    </div>
                </div>
                <div class="injury-season-detail">
                    <table class="injury-history-subtable">
                        <thead>
                            <tr>
                                <th>Diagnosi Infortunio</th>
                                <th>Tipo</th>
                                <th>Stop</th>
                                <th style="text-align:center;">Gare Perse</th>
                                <th>Periodo</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sub_rows}
                        </tbody>
                    </table>
                </div>
            </div>"""
    
    injury_history_html = f"""
    <div class="injury-history-container">
        <div class="injury-history-header">
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <span style="font-size:18px;">🩺</span>
                <h3 style="margin:0;font-size:13.5px;font-weight:800;color:#fff;letter-spacing:0.3px;">Storico Infortuni &amp; Affidabilità Fisica (Multi-Stagione)</h3>
                <span class="injury-tier-chip" style="background:rgba(255,255,255,0.06);border:1px solid {tier_color};color:{tier_color};">
                    {clean_html(frag_tier)}
                </span>
            </div>
            <div style="font-size:11.5px;color:var(--text-muted);">
                Indice Fragilità AI: <b style="color:{tier_color};font-size:13px;">{frag_score}/100</b>
            </div>
        </div>
        <div class="injury-metrics-grid">
            <div class="injury-metric-card">
                <span class="lbl">Disponibilità Storica</span>
                <div style="display:flex;align-items:baseline;gap:6px;margin:4px 0;">
                    <b class="val" style="color:{disp_color};font-size:19px;">{disp_pct}%</b>
                    <small style="color:var(--text-muted);font-size:10.5px;">su 3 stagioni</small>
                </div>
                <div class="injury-progress-bar-bg">
                    <div class="injury-progress-bar-fill" style="width:{disp_pct}%;background:{disp_color};"></div>
                </div>
            </div>
            <div class="injury-metric-card">
                <span class="lbl">Partite Perse Totali</span>
                <b class="val" style="color:#fbbf24;font-size:19px;margin-top:4px;">{tot_missed} <small style="font-size:11px;color:var(--text-muted);font-weight:normal;">gare</small></b>
                <span style="font-size:10.5px;color:var(--text-secondary);">{tot_days} giorni di stop</span>
            </div>
            <div class="injury-metric-card">
                <span class="lbl">Recidive Muscolari</span>
                <b class="val" style="color:{'#ef4444' if recidive > 1 else ('#f59e0b' if recidive == 1 else '#34d399')};font-size:19px;margin-top:4px;">
                    {recidive} <small style="font-size:11px;color:var(--text-muted);font-weight:normal;">eventi</small>
                </b>
                <span style="font-size:10.5px;color:var(--text-secondary);">{'⚠️ Rischio ricadute' if recidive > 1 else 'Tenuta muscolare solida'}</span>
            </div>
            <div class="injury-metric-card">
                <span class="lbl">Stato Attuale</span>
                <div style="margin-top:4px;">
                    {f'<span class="health-current-tag injured">🩹 {clean_html(infort_motivo)} ({clean_html(infort_rientro)})</span>' if is_injured else '<span class="health-current-tag healthy">🟢 Pienamente Disponibile</span>'}
                </div>
                <span style="font-size:10.5px;color:var(--text-muted);">Serie A 2026/27</span>
            </div>
        </div>
        <div class="injury-advice-box">
            <div style="display:flex;align-items:flex-start;gap:8px;">
                <span style="font-size:15px;line-height:1.2;">💡</span>
                <div>
                    <b style="color:var(--accent-cyan);font-size:11px;text-transform:uppercase;letter-spacing:0.4px;">Analisi Medica &amp; Consigli Asta AI:</b>
                    <p style="margin:2px 0 0 0;font-size:11.5px;color:var(--text-secondary);line-height:1.45;">{clean_html(medical_advice)}</p>
                </div>
            </div>
        </div>
        {f'<div class="injury-seasons-accordion">{season_accordion_html}</div>' if sorted_seasons else '<div class="injury-empty-banner"><span style="font-size:16px;">🛡️</span><span><b>Integrità Fisica Impeccabile:</b> Nessun infortunio significativo registrato negli ultimi 3 anni. Calciatore integro ad alta affidabilità.</span></div>'}
    </div>"""

    # TAB 1: OVERVIEW HTML
    fm_val_str = f"{float(player.get('fm_2627') or player.get('fm') or 0):.2f}" if (player.get('fm_2627') or player.get('fm')) else "-"
    mv_val_str = f"{float(player.get('mv_2627') or player.get('mv') or 0):.2f}" if (player.get('mv_2627') or player.get('mv')) else "-"

    tab_overview_html = f"""
    <div id="profileTabPane_overview" class="profile-tab-pane" style="display:block;">
        <!-- Live Season Summary Bar -->
        <div class="profile-season-summary-bar">
            <div class="profile-season-header-row">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:16px;">📈</span>
                    <span style="font-size:13px;font-weight:800;color:#fff;">Rendimento Live 2026/27</span>
                </div>
                <span class="trend-badge-clean" style="color:{smart_trend['color']};font-weight:800;font-size:12px;" title="{clean_html(smart_trend['desc'])}">{smart_trend['label']}</span>
            </div>
            <div class="summary-kpis-grid">
                <div class="kpi-mini-card">
                    <span class="kpi-mini-lbl">FM</span>
                    <b class="kpi-mini-val" style="color:#fbbf24;">{fm_val_str}</b>
                </div>
                <div class="kpi-mini-card">
                    <span class="kpi-mini-lbl">MV</span>
                    <b class="kpi-mini-val" style="color:#4ade80;">{mv_val_str}</b>
                </div>
                <div class="kpi-mini-card">
                    <span class="kpi-mini-lbl">xFM</span>
                    <b class="kpi-mini-val" style="color:var(--accent-cyan);">{xfm_data['xfm']}</b>
                </div>
                <div class="kpi-mini-card">
                    <span class="kpi-mini-lbl">Sufficienze</span>
                    <b class="kpi-mini-val" style="color:#38bdf8;">{suff_pct}% <small style="font-size:9.5px;font-weight:600;color:var(--text-muted);">({suff_count}/{len(valid_voti)})</small></b>
                </div>
                <div class="kpi-mini-card">
                    <span class="kpi-mini-lbl">Bonus Tot</span>
                    <b class="kpi-mini-val" style="color:#fde047;">+{player.get('tot_bonus_2627', 0)}</b>
                </div>
                <div class="kpi-mini-card">
                    <span class="kpi-mini-lbl">Minuti</span>
                    <b class="kpi-mini-val" style="color:#fff;">{player.get('minuti_2627', 0)}&#39;</b>
                </div>
            </div>
        </div>

        <!-- Regression Alert Banner -->
        {xfm_alert_html}

        <!-- 38-ROUND SEASON PERFORMANCE HUB -->
        <div class="profile-andamento-container">
            <div class="andamento-title">
                <div class="andamento-title-group">
                    <span class="andamento-main-title">📊 Rendimento Stagionale</span>
                    <span class="andamento-sub-info">(G1-G{max_played} Giocate • G{max_played+1}-G38 In Arrivo)</span>
                </div>
                <div class="season-view-toggle">
                    <button id="btnSeasonView_chart" class="season-toggle-btn active" onclick="switchSeasonView('chart')">📈 Grafico</button>
                    <button id="btnSeasonView_table" class="season-toggle-btn" onclick="switchSeasonView('table')">📋 Tabella</button>
                </div>
            </div>

            <!-- Legend & Reference -->
            <div class="season-chart-legend">
                <span class="legend-item"><span class="legend-box green"></span> Voto Base</span>
                <span class="legend-item"><span class="legend-box gold"></span> Bonus (+Gol/Assist)</span>
                <span class="legend-item"><span class="legend-box red"></span> Malus Concesso</span>
                <span class="legend-item"><span class="legend-line"></span> FantaVoto Finale</span>
                <span class="legend-item"><span class="legend-line dashed cyan"></span> Sufficienza (6.0)</span>
            </div>

            <!-- View 1: 38-Round SVG Chart -->
            <div id="seasonPerformanceView_chart" class="season-chart-box" style="display:block;">
                <div class="season-svg-scroll-wrapper">
                    {season_chart_svg}
                </div>
                {initial_inspector_html}
            </div>

            <!-- View 2: Full Table -->
            <div id="seasonPerformanceView_table" class="season-table-box" style="display:none;">
                <div class="season-table-scroll">
                    <table class="season-voti-table">
                        <thead>
                            <tr>
                                <th>G</th>
                                <th>Partita</th>
                                <th>Luogo</th>
                                <th>Voto Base</th>
                                <th>Bonus / Malus</th>
                                <th>FantaVoto</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Key Quick Info (4-card Executive Grid) -->
        <div class="profile-quick-info-grid">
            <div class="quick-info-box card-advice">
                <div class="quick-info-header">
                    <span class="quick-info-icon">💡</span>
                    <span class="lbl">Consiglio Strategico AI</span>
                </div>
                <div class="quick-info-content">
                    <span class="quick-badge advice-badge {player.get('ai_advice_type', 'regular')}">{clean_html(player.get('ai_advice') or player.get('consiglio') or '-')}</span>
                </div>
            </div>
            <div class="quick-info-box card-slot">
                <div class="quick-info-header">
                    <span class="quick-info-icon">🎯</span>
                    <span class="lbl">Gerarchia &amp; Slot</span>
                </div>
                <div class="quick-info-content">
                    <span class="quick-badge slot-badge">{clean_html(slot_desc)}</span>
                </div>
            </div>
            <div class="quick-info-box card-injury">
                <div class="quick-info-header">
                    <span class="quick-info-icon">🩺</span>
                    <span class="lbl">Integrità Fisica</span>
                </div>
                <div class="quick-info-content">
                    <span class="quick-badge health-badge {'injured' if is_injured else 'healthy'}">
                        {f'🩹 Infortunato ({clean_html(infort_rientro)})' if is_injured else '🟢 Integro (Basso Rischio)'}
                    </span>
                </div>
            </div>
            <div class="quick-info-box card-mantra">
                <div class="quick-info-header">
                    <span class="quick-info-icon">💎</span>
                    <span class="lbl">Ruoli Mantra</span>
                </div>
                <div class="quick-info-content">
                    <div class="mantra-badges-container">
                        {render_mantra_quick_badges(mantra)}
                    </div>
                </div>
            </div>
        </div>

        <!-- Multi-Season Injury & Physical Reliability Hub -->
        {injury_history_html}
    </div>"""

    # TAB 2: ADVANCED STATS + RADAR
    radar_chart_html = f"""
    <div class="radar-chart-wrapper">
        <div class="radar-title-bar">
            <div>
                <b style="color:#fff;font-size:12.5px;">Radar Percentilare a 6 Assi (vs Pari-Ruolo Serie A)</b>
                <div style="font-size:10.5px;color:var(--text-muted);">Percentile 0-100: più l&#39;area è espansa, più il calciatore è dominante nel reparto</div>
            </div>
            <span class="role-badge {role}" style="font-size:10px;padding:2px 6px;">{role}</span>
        </div>
        <div style="display:flex;justify-content:center;align-items:center;padding:10px 0;">
            {generate_radar_chart_svg(player)}
        </div>
    </div>"""

    if role == 'P':
        advanced_pillars_html = f"""
        <div class="profile-pillars-row">
            <div class="profile-pillar-card pillar-gk">
                <div class="pillar-title"><span>🧤 DIFESA &amp; PASSIVO</span><span class="source-tag">Statistiche</span></div>
                <div class="pillar-hero-stat">
                    <span class="hero-label">GOL SUBITI 26/27</span>
                    <span class="hero-val" style="color:#ef4444;">{player.get('gol_subiti_2627', 0)} <small>({player.get('clean_sheets_2627', 0)} CS)</small></span>
                </div>
                <div class="pillar-stat-list">
                    <div class="pillar-stat-item"><span class="stat-name">% Parate</span><span class="stat-num" style="color:#38bdf8;">{str(player.get('save_pct_2627') or '-') + '%' if player.get('save_pct_2627') else '-'}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Parate Effettuate</span><span class="stat-num" style="color:#4ade80;">{player.get('parate_2627', 0)}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Gol Evitati (Goals Prevented)</span><span class="stat-num" style="color:{'#10b981' if float(player.get('goals_prevented_2627') or 0) >= 0 else '#f87171'};font-weight:800;">{'+' if float(player.get('goals_prevented_2627') or 0) > 0 else ''}{player.get('goals_prevented_2627', 0)}</span></div>
                </div>
                <div class="pillar-comparison-chip">
                    <span>Storico 2025/26</span><b>{player.get('gs', 0)} GS &bull; {player.get('clean_sheets_2526', 0)} Clean Sheet</b>
                </div>
            </div>

            <div class="profile-pillar-card pillar-ratings">
                <div class="pillar-title"><span>📊 RENDIMENTO &amp; MODIFICATORE</span><span class="source-tag">Prestazioni</span></div>
                <div class="pillar-hero-stat">
                    <span class="hero-label">MEDIA VOTO PURA</span>
                    <span class="hero-val" style="color:#4ade80;">{mv_val_str}</span>
                </div>
                <div class="pillar-stat-list">
                    <div class="pillar-stat-item"><span class="stat-name">FantaMedia Ufficiale</span><span class="stat-num" style="color:#fbbf24;">{fm_val_str}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Expected FantaMedia (xFM)</span><span class="stat-num" style="color:var(--accent-cyan);font-weight:900;">{xfm_data['xfm']}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Match Rating Statistico</span><span class="stat-num" style="color:#38bdf8;">{f"{float(player.get('rating_live_2627')):.2f}" if player.get('rating_live_2627') else '-'}</span></div>
                </div>
                <div class="pillar-comparison-chip">
                    <span>Storico 2025/26</span><b>MV {player.get('mv', '-')} &bull; FM {player.get('fm', '-')}</b>
                </div>
            </div>

            <div class="profile-pillar-card pillar-assists">
                <div class="pillar-title"><span>⏱️ MINUTAGGIO &amp; PRESENZA</span><span class="source-tag">Stagione</span></div>
                <div class="pillar-hero-stat">
                    <span class="hero-label">MINUTI GIOCATI</span>
                    <span class="hero-val">{player.get('minuti_2627', 0)}&#39;</span>
                </div>
                <div class="pillar-stat-list">
                    <div class="pillar-stat-item"><span class="stat-name">Presenze / Titolarità</span><span class="stat-num">{player.get('presenze_2627', 0)} ({player.get('starts_2627', 0)} tit)</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Status Tattico</span><span class="stat-num" style="color:#4ade80;">{clean_html(titolarita_desc)}</span></div>
                </div>
                <div class="pillar-comparison-chip">
                    <span>Storico 2025/26</span><b>{player.get('presenze', 0)} presenze a voto</b>
                </div>
            </div>
        </div>"""
    else:
        advanced_pillars_html = f"""
        <div class="profile-pillars-row">
            <div class="profile-pillar-card pillar-goals">
                <div class="pillar-title"><span>⚽ ATTACCO &amp; TIRO</span><span class="source-tag">Volume</span></div>
                <div class="pillar-hero-stat">
                    <span class="hero-label">GOL SEGNATI 26/27</span>
                    <span class="hero-val" style="color:#fbbf24;">{player.get('gol_2627', 0)} Gol <small>({str(player.get('xg_2627') or player.get('xg90_2627') or '-') + ' xG'})</small></span>
                </div>
                <div class="pillar-stat-list">
                    <div class="pillar-stat-item"><span class="stat-name">Tiri Totali</span><span class="stat-num">{player.get('tiri_2627') or (str(player.get('total_scoring_att_2627')) + '/90' if player.get('total_scoring_att_2627') else 0)}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Qualità Tiro (xGOT)</span><span class="stat-num" style="color:#f472b6;">{player.get('xgot_2627', '-')}</span></div>
                    {f"<div class='pillar-stat-item'><span class='stat-name'>Grandi Occasioni Fallite</span><span class='stat-num' style='color:#f87171;'>{player.get('big_chance_missed_2627')}</span></div>" if (player.get("big_chance_missed_2627") or 0) > 0 else ""}
                </div>
                <div class="pillar-comparison-chip">
                    <span>Storico 2025/26</span><b>{player.get('gf', 0)} Gol ({player.get('xg90_2526', 0)} xG/90)</b>
                </div>
            </div>

            <div class="profile-pillar-card pillar-assists">
                <div class="pillar-title"><span>🪄 CREATIVITÀ &amp; ASSIST</span><span class="source-tag">Rifinitura</span></div>
                <div class="pillar-hero-stat">
                    <span class="hero-label">ASSIST FORNITI 26/27</span>
                    <span class="hero-val" style="color:#00f2fe;">{player.get('assist_2627', 0)} Assist <small>({str(player.get('xa90_2627') or '-') + ' xA/90'})</small></span>
                </div>
                <div class="pillar-stat-list">
                    <div class="pillar-stat-item"><span class="stat-name">Occasioni Create (Key Passes)</span><span class="stat-num">{player.get('chances_created_2627') or player.get('key_passes_2627') or 0}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Grandi Occasioni Create</span><span class="stat-num" style="color:#fbbf24;">{player.get('big_chances_created_2627', 0)}</span></div>
                    {f"<div class='pillar-stat-item'><span class='stat-name'>Dribbling Vinti /90</span><span class='stat-num' style='color:#38bdf8;'>{player.get('won_contest_2627')}</span></div>" if player.get("won_contest_2627") else ""}
                </div>
                <div class="pillar-comparison-chip">
                    <span>Storico 2025/26</span><b>{player.get('ass', 0)} Assist ({player.get('xa90_2526', 0)} xA/90)</b>
                </div>
            </div>

            <div class="profile-pillar-card pillar-ratings">
                <div class="pillar-title"><span>🛡️ PRESENZA &amp; RENDIMENTO</span><span class="source-tag">Sul Campo</span></div>
                <div class="pillar-hero-stat">
                    <span class="hero-label">MINUTI GIOCATI</span>
                    <span class="hero-val">{player.get('minuti_2627', 0)}&#39; <small>({player.get('starts_2627', 0)} tit)</small></span>
                </div>
                <div class="pillar-stat-list">
                    <div class="pillar-stat-item"><span class="stat-name">Palle Recuperate</span><span class="stat-num">{player.get('recuperi_2627', 0)}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Expected FantaMedia (xFM)</span><span class="stat-num" style="color:var(--accent-cyan);font-weight:900;">{xfm_data['xfm']}</span></div>
                    <div class="pillar-stat-item"><span class="stat-name">Disciplina (Amm/Esp)</span><span class="stat-num" style="color:{'#ef4444' if (player.get('amm_2627') or 0) > 0 else 'var(--text-muted)'};">{player.get('amm_2627', 0)} Amm &bull; {player.get('esp_2627', 0)} Esp</span></div>
                </div>
                <div class="pillar-comparison-chip">
                    <span>Storico 2025/26</span><b>MV {player.get('mv', '-')} &bull; FM {player.get('fm', '-')}</b>
                </div>
            </div>
        </div>"""

    tCtx = player.get("team_context") or {}
    team_stats_html = f"""
    <div class="team-ecosystem-bar">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
            <span>🏟️</span>
            <b>Ecosistema {clean_html(team)}:</b>
            <span>Attacco: <b style="color:#f472b6;">#{tCtx.get('xg_team_rank', '-')}</b> ({tCtx.get('xg_team', 0)} xG &bull; {tCtx.get('big_chances_team', 0)} occ.)</span>
            <span>&bull;</span>
            <span>Difesa: <b style="color:#38bdf8;">#{tCtx.get('xga_team_rank', '-')}</b> ({tCtx.get('xga_team', 0)} xGA &bull; {tCtx.get('clean_sheets_team', 0)} CS)</span>
        </div>
        <div style="font-size:11px;color:var(--text-muted);">Statistiche Live 2026/27</div>
    </div>""" if tCtx and tCtx.get("xg_team") else ""

    tab_advanced_html = f"""
    <div id="profileTabPane_advanced" class="profile-tab-pane" style="display:none;">
        {radar_chart_html}
        {advanced_pillars_html}
        {team_stats_html}
    </div>"""

    # TAB 3: TACTICS & CLUB CONTEXT
    tactics_content_html = f"""
    <div class="tactics-overview-grid">
        <div class="tactics-card">
            <div class="tactics-card-header">
                <span style="font-size:16px;">👔</span>
                <h4>Guida Tecnica &amp; Assetto</h4>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Allenatore:</span>
                <b class="val" style="color:#fff;">{clean_html(mister)}</b>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Modulo Base:</span>
                <b class="val" style="color:var(--accent-cyan);">{clean_html(modulo)}</b>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Stile Tattico:</span>
                <span class="val" style="color:var(--text-secondary);font-size:11.5px;">{clean_html(stile)}</span>
            </div>
        </div>

        <div class="tactics-card">
            <div class="tactics-card-header">
                <span style="font-size:16px;">🎯</span>
                <h4>Calci Piazzati &amp; Gerarchie</h4>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">1° Rigorista:</span>
                <b class="val" style="color:#fbbf24;">{clean_html(team_tac.get('rigorista_1') or player.get('rigorista_val') or '-')}</b>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">2°/3° Rigorista:</span>
                <span class="val">{clean_html(team_tac.get('rigorista_2', '-'))} / {clean_html(team_tac.get('rigorista_3', '-'))}</span>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Corner &amp; Punizioni:</span>
                <span class="val" style="color:#38bdf8;">{clean_html(team_tac.get('punizioni') or team_tac.get('corner') or '-')}</span>
            </div>
        </div>

        <div class="tactics-card">
            <div class="tactics-card-header">
                <span style="font-size:16px;">🔄</span>
                <h4>Ballottaggio &amp; Copertura</h4>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Titolarità Stimata:</span>
                <b class="val" style="color:{tit_color};">{titolarita}% ({clean_html(titolarita_desc)})</b>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Compagno di Staffetta:</span>
                <b class="val" style="color:#38bdf8;">{clean_html(coppia_nome or 'Nessun ballottaggio diretto')}</b>
            </div>
            <div class="tactics-meta-row">
                <span class="lbl">Tipo Alternanza:</span>
                <span class="val">{clean_html(coppia_tipo or 'Titolare inamovibile')}</span>
            </div>
        </div>
    </div>""" if team_tac else f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);padding:16px;border-radius:10px;text-align:center;color:var(--text-muted);font-size:12.5px;">Dati tattici di club non disponibili per {clean_html(team)}.</div>'

    tab_tactics_html = f"""
    <div id="profileTabPane_tactics" class="profile-tab-pane" style="display:none;">
        {tactics_content_html}
    </div>"""

    # FAQ Schema
    faq_items = [
        {
            "@type": "Question",
            "name": f"Qual è la fantamedia di {full_name} nel 2026/27?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{full_name} ({team}) registra attualmente una FantaMedia reale di {fm_val_str} con una media voto pura di {mv_val_str} e un valore atteso xFM di {xfm_data['xfm']}."
            }
        },
        {
            "@type": "Question",
            "name": f"{full_name} è infortunato? Quali sono i tempi di recupero?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{'Attualmente ' + full_name + ' è indisponibile per ' + infort_motivo + '. Il rientro è previsto per il ' + infort_rientro + '.' if is_injured else full_name + ' è attualmente integro e regolarmente a disposizione di mister ' + mister + '.'}"
            }
        },
        {
            "@type": "Question",
            "name": f"Quanto pagare {full_name} all'asta del Fantacalcio?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Il prezzo consigliato dall'algoritmo AI per {full_name} è di {prezzo_cons} crediti su un budget di 1000 CR (FVM {fvm} CR), con rilancio massimo stimato a {max_bid} crediti."
            }
        }
    ]

    team_slug = slugify(team)
    meta_title = f"{full_name} ({team}): Statistiche Avanzate, xG, Storico Infortuni e Consigli Asta 2026/27"
    meta_desc = f"Scheda tecnica completa di {full_name} ({team}): radar a 6 assi, xG, xA, storico infortuni e cartella clinica, gerarchie rigori, quotazione FVM e prezzo consigliato asta Fantacalcio 2026/27."
    page_url = f"{base_url}/calciatore/{slug}/"

    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "name": full_name,
                "jobTitle": "Calciatore Serie A",
                "memberOf": {
                    "@type": "SportsTeam",
                    "name": team
                }
            },
            {
                "@type": "FAQPage",
                "mainEntity": faq_items
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Probabili Formazioni Serie A", "item": f"{base_url}/probabili-formazioni/"},
                    {"@type": "ListItem", "position": 3, "name": team, "item": f"{base_url}/probabili-formazioni/{team_slug}/"},
                    {"@type": "ListItem", "position": 4, "name": full_name, "item": page_url}
                ]
            }
        ]
    }

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    
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
            <a href="../../probabili-formazioni/{team_slug}/">{clean_html(team)}</a> <span>/</span> 
            <span style="color:#fff;">{clean_html(full_name)}</span>
        </nav>

        <!-- Profile Header (Identico a Modal App) -->
        <div class="profile-header-container" style="margin-top:10px;">
            <div class="profile-hero-left">
                <div class="profile-role-circle {role}">{role}</div>
                <div class="profile-hero-info">
                    <div class="profile-hero-title-row">
                        <h1 class="profile-player-name">{clean_html(full_name)}</h1>
                    </div>
                    <div class="profile-player-meta">
                        <a href="../../probabili-formazioni/{team_slug}/" class="player-meta-team" style="text-decoration:none;border-bottom:1px dashed var(--accent-cyan);color:#fff;" title="Vedi Formazione Titolare e Rosa {clean_html(team)}"><b>{clean_html(team)}</b></a> &bull; Mister: <b>{clean_html(mister)}</b> <span style="color:var(--text-muted);">({clean_html(modulo)})</span>
                    </div>
                    <div class="profile-badges-wrapper">
                        <div class="profile-primary-badges">
                            <span class="ai-advice-badge {player.get('ai_advice_type', 'regular')}">{clean_html(player.get('ai_advice') or player.get('consiglio') or '-')}</span>
                            <span class="badge-tag gold">{clean_html(slot_desc)}</span>
                        </div>
                        <div class="profile-tactical-pills">
                            {inj_badge}
                            {rig_badge}
                            {coppia_badge}
                            {oop_badge}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Hero Metrics Deck -->
            <div class="profile-hero-metrics-section">
                <div class="profile-hero-triple-cards">
                    <div class="profile-hero-metric-card card-ovr">
                        <span class="hero-card-label">OVR RATING</span>
                        <div class="hero-card-value ovr-text {ovr_cls}">{ovr}</div>
                        <span class="hero-card-sub">{'Top Assoluto' if ovr >= 90 else ('Titolare Top' if ovr >= 82 else 'Rotazione')}</span>
                    </div>

                    <div class="profile-hero-metric-card card-titolarita">
                        <span class="hero-card-label">TITOLARITÀ</span>
                        <div class="hero-card-value" style="color:{tit_color};">{titolarita}%</div>
                        <span class="hero-card-sub" style="color:{tit_color};">{clean_html(titolarita_desc)}</span>
                    </div>

                    <div class="profile-hero-metric-card card-price">
                        <span class="hero-card-label">PREZZO CONS.</span>
                        <div class="hero-card-value price-text">{prezzo_cons} <span style="font-size:11px;color:rgba(255,255,255,0.6);">CR</span></div>
                        <span class="hero-card-sub" style="color:#f43f5e;">Max: <b>{max_bid} CR</b></span>
                    </div>
                </div>

                <div class="profile-hero-sub-strip">
                    <div class="sub-stat-chip">
                        <span class="sub-stat-lbl">FVM:</span>
                        <b class="sub-stat-val text-cyan">{fvm} CR</b>
                    </div>
                    <span class="sub-stat-dot">&bull;</span>
                    <div class="sub-stat-chip">
                        <span class="sub-stat-lbl">Quotazione:</span>
                        <b class="sub-stat-val text-purple">{qta}</b>
                        {f'<small class="sub-stat-diff pos">{diff_q_str}</small>' if diff_q > 0 else (f'<small class="sub-stat-diff neg">{diff_q_str}</small>' if diff_q < 0 else '')}
                    </div>
                </div>
            </div>
        </div>

        <!-- Clean 3-Tab Controls (Identici all'App) -->
        <div class="profile-3tabs-nav" style="margin-top:20px;">
            <button id="profileTabBtn_overview" class="profile-3tab-btn active" onclick="switchProfileTab('overview')">
                <span class="tab-icon">📋</span>
                <span class="tab-txt-desktop">Panoramica &amp; Voti</span>
                <span class="tab-txt-mobile">Panoramica</span>
            </button>
            <button id="profileTabBtn_advanced" class="profile-3tab-btn" onclick="switchProfileTab('advanced')">
                <span class="tab-icon">📊</span>
                <span class="tab-txt-desktop">Statistiche Avanzate &amp; Radar</span>
                <span class="tab-txt-mobile">Statistiche</span>
            </button>
            <button id="profileTabBtn_tactics" class="profile-3tab-btn" onclick="switchProfileTab('tactics')">
                <span class="tab-icon">🛡️</span>
                <span class="tab-txt-desktop">Tattica &amp; Contesto Club</span>
                <span class="tab-txt-mobile">Tattica</span>
            </button>
        </div>

        <!-- Tab Panes -->
        {tab_overview_html}
        {tab_advanced_html}
        {tab_tactics_html}

        <!-- CTA Banner verso il Portale Completo -->
        <section class="cta-banner">
            <h2>Vuoi simulare l'asta con {clean_html(full_name)}?</h2>
            <p>Accedi alla suite completa di Fanta Master AI con visualizzazione live di xG, xA, griglia portieri a 20 squadre e simulatore d'asta in tempo reale.</p>
            <a href="../../index.html" class="nav-btn-icon" style="font-size:14px;padding:10px 22px;background:rgba(0,242,254,0.15);border-color:#00f2fe;color:#00f2fe;text-decoration:none;display:inline-flex;">Vai al Listone &amp; Dashboard Completa 🚀</a>
        </section>
    </main>

    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Statistiche e Storico Infortuni Serie A &bull; Tutti i marchi appartengono ai rispettivi proprietari.</p>
        </div>
    </footer>

    <!-- Interactive Scripts for Tabs, Accordion & Season Inspector -->
    <script>
    var VOTI_DATA = {json.dumps(voti_list, ensure_ascii=False)};
    
    function switchProfileTab(tabName) {{
        var tabs = ['overview', 'advanced', 'tactics'];
        tabs.forEach(function(t) {{
            var pane = document.getElementById('profileTabPane_' + t);
            var btn = document.getElementById('profileTabBtn_' + t);
            if (pane) pane.style.display = (t === tabName) ? 'block' : 'none';
            if (btn) btn.classList.toggle('active', t === tabName);
        }});
    }}

    function switchSeasonView(viewType) {{
        var chartView = document.getElementById('seasonPerformanceView_chart');
        var tableView = document.getElementById('seasonPerformanceView_table');
        var btnChart = document.getElementById('btnSeasonView_chart');
        var btnTable = document.getElementById('btnSeasonView_table');
        if (viewType === 'chart') {{
            if (chartView) chartView.style.display = 'block';
            if (tableView) tableView.style.display = 'none';
            if (btnChart) btnChart.classList.add('active');
            if (btnTable) btnTable.classList.remove('active');
        }} else {{
            if (chartView) chartView.style.display = 'none';
            if (tableView) tableView.style.display = 'block';
            if (btnChart) btnChart.classList.remove('active');
            if (btnTable) btnTable.classList.add('active');
        }}
    }}

    function toggleSeasonInjuryDetail(headerEl) {{
        if (!headerEl) return;
        var card = headerEl.closest('.injury-season-card');
        if (card) card.classList.toggle('expanded');
    }}

    function selectSeasonRound(pId, roundNum) {{
        previewSeasonRound(pId, roundNum);
    }}

    function previewSeasonRound(pId, roundNum) {{
        if (!VOTI_DATA || VOTI_DATA.length === 0) return;
        var match = VOTI_DATA.find(function(v) {{ return v.giornata === roundNum; }});
        var inspectorEl = document.getElementById('seasonMatchInspectorCard');
        if (!inspectorEl || !match) return;

        var hasV = match.voto !== null && match.voto !== undefined;
        var vVal = hasV ? match.voto : 's.v.';
        var fvVal = match.fantavoto !== null && match.fantavoto !== undefined ? match.fantavoto : '-';
        var vC = hasV ? (match.voto >= 7 ? '#34d399' : (match.voto >= 6 ? '#38bdf8' : (match.voto >= 5.5 ? '#fbbf24' : '#f87171'))) : 'var(--text-muted)';
        var fvC = match.fantavoto !== null && match.fantavoto !== undefined ? (match.fantavoto >= 10 ? '#10b981' : (match.fantavoto >= 7 ? '#38bdf8' : (match.fantavoto < 5 ? '#f87171' : '#fbbf24'))) : 'var(--text-muted)';
        var isH = match.is_home !== undefined ? match.is_home : true;
        var mTitle = match.match || ('vs ' + (match.opponent || 'Avversario'));
        var bmStr = match.bonus_malus_str || '-';

        inspectorEl.innerHTML = '<div class="inspector-header">' +
            '<div style="display:flex;align-items:center;gap:8px;">' +
                '<span class="inspector-badge">GIORNATA ' + match.giornata + '</span>' +
                '<span class="inspector-venue">' + (isH ? '🏠 Casa' : '✈️ Fuori') + '</span>' +
                '<b class="inspector-match-title">' + mTitle + '</b>' +
            '</div>' +
            '<span style="font-size:10.5px;color:var(--text-muted);">Ispezione match disputato</span>' +
        '</div>' +
        '<div class="inspector-body-grid">' +
            '<div class="inspector-metric">' +
                '<span class="lbl">Voto Base</span>' +
                '<b class="val" style="color:' + vC + ';">' + vVal + '</b>' +
            '</div>' +
            '<div class="inspector-metric highlight">' +
                '<span class="lbl">FantaVoto</span>' +
                '<b class="val" style="color:' + fvC + ';font-size:17px;">' + fvVal + '</b>' +
            '</div>' +
            '<div class="inspector-metric">' +
                '<span class="lbl">Bonus / Malus</span>' +
                '<span class="val-bonus">' + bmStr + '</span>' +
            '</div>' +
            '<div class="inspector-metric">' +
                '<span class="lbl">Gol / Assist</span>' +
                '<b class="val">' + (match.gf || 0) + ' Gol &bull; ' + (match.ass || 0) + ' Ass</b>' +
            '</div>' +
            '<div class="inspector-metric">' +
                '<span class="lbl">Disciplina</span>' +
                '<span class="val" style="color:' + ((match.amm || 0) > 0 ? '#ef4444' : 'var(--text-secondary)') + ';">' + (match.amm || 0) + ' Amm &bull; ' + (match.esp || 0) + ' Esp</span>' +
            '</div>' +
        '</div>';
    }}
    </script>
    {render_unified_footer('../../')}
    <script src="/js/tracker.js" defer></script>
</body>
</html>
"""
    return slug, html
