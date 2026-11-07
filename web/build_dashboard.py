import os
import json
import re

def minify_css(css: str) -> str:
    """Minifica il CSS rimuovendo commenti e spazi ridondanti."""
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([\{\}\:\;\,\>])\s*', r'\1', css)
    css = re.sub(r';\}', '}', css)
    return css.strip()

def minify_js(js: str) -> str:
    """Rimuove commenti e linee vuote dal JavaScript per alleggerire il payload."""
    lines = []
    for line in js.splitlines():
        s = line.strip()
        if not s or s.startswith('//'):
            continue
        lines.append(line)
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'/\*[\s\S]*?\*/', '', cleaned)
    return cleaned

def generate_home_leaders_html(players_data: list) -> str:
    """Genera dinamicamente le 6 card dei leader statistici della Serie A 2026/27."""
    def get_ovr_tier(ovr):
        try:
            val = int(ovr)
        except Exception:
            val = 0
        if val >= 90: return 'ovr-tier-elite'
        if val >= 85: return 'ovr-tier-top'
        if val >= 80: return 'ovr-tier-high'
        if val >= 75: return 'ovr-tier-good'
        if val >= 70: return 'ovr-tier-mid'
        if val >= 65: return 'ovr-tier-low'
        return 'ovr-tier-bench'

    role_map = {'P': 'Portiere', 'D': 'Difensore', 'C': 'Centrocampista', 'A': 'Attaccante'}

    categories = [
        {
            'title': '⚽ Più Gol Segnati',
            'key': lambda p: float(p.get('gol_2627') if p.get('gol_2627') is not None else p.get('gol', 0)),
            'min_p': 0,
            'val_str': lambda v: f"{int(v)}",
            'sub': lambda p: f"{p.get('team', '')} • {p.get('role_desc') or role_map.get(p.get('role', 'A'), 'Attaccante')}",
            'runner': lambda p, v: f"{p.get('name', '')} ({p.get('team', '')}, {int(v)} gol)"
        },
        {
            'title': '🎯 Più Assist Forniti',
            'key': lambda p: float(p.get('assist_2627') if p.get('assist_2627') is not None else p.get('assist', 0)),
            'min_p': 0,
            'val_str': lambda v: f"{int(v)}",
            'sub': lambda p: f"{p.get('team', '')} • {p.get('role_desc') or role_map.get(p.get('role', 'C'), 'Centrocampista')}",
            'runner': lambda p, v: f"{p.get('name', '')} ({p.get('team', '')}, {int(v)} assist)"
        },
        {
            'title': '⚡ Più xGoals (xG)',
            'key': lambda p: float(p.get('xg_2627') if p.get('xg_2627') is not None else p.get('xg', 0)),
            'min_p': 0,
            'val_str': lambda v: f"{v:.1f}",
            'sub': lambda p: f"{p.get('team', '')} • {p.get('role_desc') or role_map.get(p.get('role', 'A'), 'Attaccante')}",
            'runner': lambda p, v: f"{p.get('name', '')} ({p.get('team', '')}, {v:.1f} xG)"
        },
        {
            'title': '🎨 Più xAssists (xA)',
            'key': lambda p: float(p.get('xa_2627') if p.get('xa_2627') is not None else p.get('xa', 0)),
            'min_p': 0,
            'val_str': lambda v: f"{v:.1f}",
            'sub': lambda p: f"{p.get('team', '')} • {p.get('role_desc') or role_map.get(p.get('role', 'C'), 'Centrocampista')}",
            'runner': lambda p, v: f"{p.get('name', '')} ({p.get('team', '')}, {v:.1f} xA)"
        },
        {
            'title': '⭐ Miglior FantaMedia (FM)',
            'key': lambda p: float(p.get('fm_2627') if p.get('fm_2627') is not None else p.get('fm', 0)),
            'min_p': 4,
            'val_str': lambda v: f"{v:.2f}",
            'sub': lambda p: f"{p.get('team', '')} • FM {float(p.get('fm_2627') or p.get('fm', 0)):.2f} ({int(p.get('presenze_2627') or p.get('presenze', 0))} presenze)",
            'runner': lambda p, v: f"{p.get('name', '')} ({p.get('team', '')}, {v:.2f} FM)"
        },
        {
            'title': '💎 Più Bonus Totali (+Gol & +Assist)',
            'key': lambda p: float(p.get('tot_bonus_2627') if p.get('tot_bonus_2627') is not None else (float(p.get('gol_2627', 0))*3.0 + float(p.get('assist_2627', 0)))),
            'min_p': 0,
            'val_str': lambda v: f"+{v:.1f}",
            'sub': lambda p: f"{p.get('team', '')} • {int(p.get('gol_2627', 0))} gol, {int(p.get('assist_2627', 0))} assist (+{float(p.get('tot_bonus_2627', 0)):.1f} pt)",
            'runner': lambda p, v: f"{p.get('name', '')} (+{v:.1f} bonus)"
        }
    ]

    cards_html = []
    for c in categories:
        pool = [p for p in players_data if int(p.get('presenze_2627') or p.get('presenze', 0)) >= c['min_p']]
        sorted_p = sorted(pool, key=lambda x: c['key'](x), reverse=True)
        if not sorted_p:
            continue
        top1 = sorted_p[0]
        val1 = c['key'](top1)
        p2 = sorted_p[1] if len(sorted_p) > 1 else None
        p3 = sorted_p[2] if len(sorted_p) > 2 else None

        runners_parts = []
        if p2:
            val2 = c['key'](p2)
            runners_parts.append(f"<span onclick=\"event.stopPropagation(); if (typeof openPlayerProfileModal==='function') openPlayerProfileModal({p2.get('id', 0)});\" style=\"cursor:pointer;\" title=\"Vedi scheda {p2.get('name', '')}\">2° {c['runner'](p2, val2)}</span>")
        if p3:
            val3 = c['key'](p3)
            runners_parts.append(f"<span onclick=\"event.stopPropagation(); if (typeof openPlayerProfileModal==='function') openPlayerProfileModal({p3.get('id', 0)});\" style=\"cursor:pointer;\" title=\"Vedi scheda {p3.get('name', '')}\">3° {c['runner'](p3, val3)}</span>")
        runners_str = " • ".join(runners_parts)

        card = f'''                        <div class="leader-card" onclick="openPlayerProfileModal({top1.get('id', 0)})" style="cursor:pointer;" title="Clicca per aprire la scheda di {top1.get('name', '')}">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">{c['title']}</span>
                                <span class="leader-val">{c['val_str'](val1)}</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge {top1.get('role', 'A')}">{top1.get('role', 'A')}</span>
                                <div>
                                    <div class="leader-player-name">{top1.get('name', '')} <span class="ovr-pill {get_ovr_tier(top1.get('ovr', 75))}" style="font-size:10px;margin-left:4px;">OVR {top1.get('ovr', '-')}</span></div>
                                    <div class="leader-player-team">{c['sub'](top1)}</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> {runners_str}
                            </div>
                        </div>'''
        cards_html.append(card)

    return "\n".join(cards_html)

def generate_hero_trust_showcase_html(accuracy_data: dict) -> str:
    """Genera la barra visuale ultra-compatta di accuratezza certificata AI (zero muri di testo)."""
    meta = accuracy_data.get('meta', {}) if isinstance(accuracy_data, dict) else {}
    last_completed = meta.get('last_completed_round', 8)
    last_summary = accuracy_data.get(str(last_completed), {}).get('summary', {}) if isinstance(accuracy_data, dict) else {}
    
    acc_hit_rate = float(last_summary.get('hit_rate_pct', 75.0))
    acc_hits = int(last_summary.get('hits', 9))
    acc_total = int(last_summary.get('total_consigliati', 12))
    acc_suff = float(last_summary.get('sufficiency_rate_pct', 75.0))
    acc_avg_fv = float(last_summary.get('avg_fantavoto', 6.27))

    return f'''                    <!-- BARRA COMPATTA ACCURATEZZA AI CERTIFICATA (VISUAL FIRST) -->
                    <div class="hpro-trust-strip" id="heroTrustShowcase">
                        <div class="hpro-trust-left">
                            <span class="hpro-trust-seal"><span class="pulse-dot-green"></span> G{last_completed} CERTIFICATA</span>
                        </div>
                        <div class="hpro-trust-kpis">
                            <div class="hpro-trust-pill hit">
                                <span class="ht-val">{acc_hit_rate:.0f}%</span>
                                <span class="ht-lbl">Hit Bonus ({acc_hits}/{acc_total})</span>
                            </div>
                            <div class="hpro-trust-pill suff">
                                <span class="ht-val">{acc_suff:.0f}%</span>
                                <span class="ht-lbl">Voto &ge; 6.0</span>
                            </div>
                            <div class="hpro-trust-pill fv">
                                <span class="ht-val">{acc_avg_fv:.2f}</span>
                                <span class="ht-lbl">FantaVoto Medio</span>
                            </div>
                            <div class="hpro-trust-pill db">
                                <span class="ht-val">534</span>
                                <span class="ht-lbl">Calciatori xFM</span>
                            </div>
                        </div>
                        <a href="/consigli-fantacalcio/" class="hpro-trust-cta" onclick="if(window.switchTab) {{ event.preventDefault(); switchTab('matchday_advice'); }}">
                            Storico AI &rarr;
                        </a>
                    </div>'''

def generate_home_matches_strip_html(consensus_data: dict) -> str:
    """Genera la griglia visuale delle 10 partite di giornata con link diretti alle probabili formazioni."""
    matches = consensus_data.get("matches", []) if isinstance(consensus_data, dict) else []
    if not matches:
        return ""
    cards = []
    for m in matches:
        slug = m.get("slug", "")
        h_team = m.get("home_team", "")
        a_team = m.get("away_team", "")
        time_str = m.get("time", "20:45")
        date_str = (m.get("date", "") or "")[:5]
        is_big = m.get("big_match", False)
        h_mod = m.get("home", {}).get("formation", "4-3-3")
        a_mod = m.get("away", {}).get("formation", "4-3-3")
        n_dubbi = len(m.get("ballottaggi", []))
        big_badge = '<span class="hpro-match-big">🔥 BIG</span>' if is_big else f'<span class="hpro-match-dubbi">⚖️ {n_dubbi} dubbi</span>'
        cards.append(f'''                            <a href="/probabili-formazioni/{slug}/" class="hpro-match-card{' is-big' if is_big else ''}" title="Probabili formazioni {h_team} - {a_team}">
                                <div class="hpro-mc-top">
                                    <span class="hpro-mc-time">{date_str} • {time_str}</span>
                                    {big_badge}
                                </div>
                                <div class="hpro-mc-teams">
                                    <span class="hpro-mc-t">{h_team}</span>
                                    <span class="hpro-mc-vs">vs</span>
                                    <span class="hpro-mc-t">{a_team}</span>
                                </div>
                                <div class="hpro-mc-mods">
                                    <span>{h_mod} • {a_mod}</span>
                                    <span class="hpro-mc-arr">&rarr;</span>
                                </div>
                            </a>''')
    return "\n".join(cards)

def build_standalone_dashboard(sync_android=False):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Carica i dati processati
    players_path = os.path.join(root_dir, "data", "processed", "processed_players_master.json")
    if not os.path.exists(players_path):
        players_path = os.path.join(root_dir, "processed_players_master.json")
    
    gk_path = os.path.join(root_dir, "data", "processed", "gk_matrix_2026_27.json")
    if not os.path.exists(gk_path):
        gk_path = os.path.join(root_dir, "gk_matrix_2026_27.json")

    tactical_path = os.path.join(root_dir, "config", "tactical_db.json")
    team_stats_path = os.path.join(root_dir, "data", "raw", "team_stats_2026_27.json")
    if not os.path.exists(team_stats_path):
        team_stats_path = os.path.join(root_dir, "data", "raw", "fotmob_team_stats_2026_27.json")

    with open(players_path, 'r', encoding='utf-8') as f:
        players_data = json.load(f)

    with open(gk_path, 'r', encoding='utf-8') as f:
        gk_data = json.load(f)

    with open(tactical_path, 'r', encoding='utf-8') as f:
        tactical_data = json.load(f)

    team_stats_data = {}
    if os.path.exists(team_stats_path):
        with open(team_stats_path, 'r', encoding='utf-8') as f:
            team_stats_data = json.load(f)

    team_ratings_path = os.path.join(root_dir, "config", "team_ratings.json")
    team_ratings_data = {}
    if os.path.exists(team_ratings_path):
        with open(team_ratings_path, 'r', encoding='utf-8') as f:
            team_ratings_data = json.load(f)

    top_flop_path = os.path.join(root_dir, "data", "processed", "top_flop_rounds.json")
    top_flop_data = {}
    if os.path.exists(top_flop_path):
        with open(top_flop_path, 'r', encoding='utf-8') as f:
            top_flop_data = json.load(f)

    cal_path = os.path.join(root_dir, "data", "processed", "calendario_serie_a_2026_27.json")
    if not os.path.exists(cal_path):
        cal_path = os.path.join(root_dir, "config", "calendario_serie_a_2026_27.json")
    cal_data = []
    if os.path.exists(cal_path):
        with open(cal_path, 'r', encoding='utf-8') as f:
            cal_data = json.load(f)

    accuracy_path = os.path.join(root_dir, "data", "processed", "matchday_advice_accuracy.json")
    accuracy_data = {}
    if os.path.exists(accuracy_path):
        with open(accuracy_path, 'r', encoding='utf-8') as f:
            accuracy_data = json.load(f)

    match_reports_path = os.path.join(root_dir, "data", "processed", "match_reports_hub.json")
    match_reports_data = {}
    if os.path.exists(match_reports_path):
        with open(match_reports_path, 'r', encoding='utf-8') as f:
            match_reports_data = json.load(f)

    consensus_path = os.path.join(root_dir, "config", "matchday_consensus.json")
    consensus_data = {}
    if os.path.exists(consensus_path):
        with open(consensus_path, 'r', encoding='utf-8') as f:
            consensus_data = json.load(f)

    # 2. Carica CSS e JS modulari minificati
    css_path = os.path.join(root_dir, "web", "css", "dashboard.css")
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = minify_css(f.read())

    js_modules = [
        "state.js",
        "my_squad_engine.js",
        "leagues_hub.js",
        "sample_fantarefri_data.js",
        "xlsx_importer.js",
        "player_profile.js",
        "ai_methodology.js",
        "pitch.js",
        "matchup.js",
        "gk_grid.js",
        "auction.js",
        "squad_builder.js",
        "ai_squads.js",
        "gems.js",
        "matchday_advice.js",
        "chi_schiero.js",
        "trade_machine.js",
        "repair_auction.js",
        "league_report.js",
        "top_flop.js",
        "match_reports.js",
        "stats_seriea.js",
        "analytics_matrix.js",
        "home_hub.js",
        "sync.js"
    ]
    js_content = ""
    for jm in js_modules:
        j_path = os.path.join(root_dir, "web", "js", jm)
        with open(j_path, 'r', encoding='utf-8') as f:
            js_content += f"\n// --- {jm} ---\n" + f.read() + "\n"
    js_content = minify_js(js_content)

    players_json = json.dumps(players_data, ensure_ascii=False)
    gk_json = json.dumps(gk_data, ensure_ascii=False)
    tactical_json = json.dumps(tactical_data, ensure_ascii=False)
    team_stats_json = json.dumps(team_stats_data, ensure_ascii=False)
    team_ratings_json = json.dumps(team_ratings_data, ensure_ascii=False)
    top_flop_json = json.dumps(top_flop_data, ensure_ascii=False)
    match_reports_json = json.dumps(match_reports_data, ensure_ascii=False)
    cal_json = json.dumps(cal_data, ensure_ascii=False)
    accuracy_json = json.dumps(accuracy_data, ensure_ascii=False)
    home_leaders_html = generate_home_leaders_html(players_data)
    hero_trust_showcase_html = generate_hero_trust_showcase_html(accuracy_data)
    home_matches_strip_html = generate_home_matches_strip_html(consensus_data)

    # 3. Costruisci il documento HTML completo
    html_template = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
    <title>Statistiche Fantacalcio Serie A 2026/27 — xG, xA, xFM & Consigli Formazione | Fanta Master AI</title>
    <meta name="description" content="Il portale statistico n°1 in Italia per il Fantacalcio: expected metrics (xG, xA, xFM), algoritmi predittivi, griglia portieri 38/38, rigoristi, probabili formazioni e consigli su chi schierare.">
    <meta name="keywords" content="statistiche fantacalcio, consigli fantacalcio chi schierare, xg fantacalcio, xfm expected fantamedia, probabili formazioni serie a 2026 2027, griglia portieri fantacalcio, rigoristi serie a">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://www.fantamasterai.it/">
    <meta property="og:title" content="Statistiche Fantacalcio Serie A 2026/27 — xG, xA, xFM & Consigli Formazione | Fanta Master AI">
    <meta property="og:description" content="Expected metrics ufficiali, algoritmi di previsione bonus, griglia portieri e consigli di formazione per vincere al Fantacalcio.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://www.fantamasterai.it/">
    <meta property="og:site_name" content="Fanta Master AI">
    <meta property="og:image" content="https://www.fantamasterai.it/static/og-image.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Statistiche Fantacalcio Serie A 2026/27 — Fanta Master AI">
    <meta name="twitter:description" content="Expected metrics ufficiali, algoritmi di previsione bonus, griglia portieri e consigli di formazione per vincere al Fantacalcio.">
    <meta name="twitter:image" content="https://www.fantamasterai.it/static/og-image.jpg">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "SportsApplication",
      "name": "Fanta Master AI",
      "description": "Portale di consultazione statistica avanzata (xG, xA, xFM, griglia portieri e consigli) per il Fantacalcio Serie A 2026/27.",
      "applicationCategory": "Sports",
      "operatingSystem": "All",
      "offers": {{
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "EUR"
      }}
    }}
    </script>
    <!-- PWA Manifest & App Icons -->
    <link rel="manifest" href="/static/manifest.json">
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    <meta name="theme-color" content="#00e676">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Fanta Master AI">

    <!-- Google Fonts Optimized (Preconnect, Preload & Non-blocking Swap) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@600;700;800;900&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@600;700;800;900&display=swap" media="print" onload="this.media='all'">
    <noscript>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@600;700;800;900&display=swap">
    </noscript>
    <!-- Vercel Analytics -->
    <script defer src="/_vercel/insights/script.js"></script>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-4QNYJ5YZXY"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-4QNYJ5YZXY', {{ 'anonymize_ip': true }});
    </script>
    <style>
{css_content}
    </style>
    <script>
      window.openMobileMenuModal = function() {{
        var m = document.getElementById('mobileMenuModal');
        if (m) m.style.display = 'flex';
      }};
      window.closeMobileMenuModal = function() {{
        var m = document.getElementById('mobileMenuModal');
        if (m) m.style.display = 'none';
      }};
      window.switchTabMobile = function(tabId, event) {{
        if (window.switchTab) {{
          if (event && event.preventDefault) event.preventDefault();
          window.switchTab(tabId);
          window.closeMobileMenuModal();
        }}
      }};
    </script>
</head>
<body>
    <header class="app-header-unified" style="position:sticky;top:0;z-index:9999;background:rgba(10,14,22,0.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.08);width:100%;">
        <div class="header-main-row" style="display:flex;align-items:center;justify-content:space-between;padding:0 14px;height:52px;min-height:52px;max-width:1560px;margin:0 auto;width:100%;box-sizing:border-box;">
            <!-- LEFT: MODERN BRAND LOGO -->
            <div class="header-left" style="display:flex;align-items:center;gap:10px;flex-shrink:0;">
                <a href="/" class="brand-logo-modern" onclick="onNavClick(event, 'home')" style="display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:#ffffff;line-height:1;flex-shrink:0;" title="Fanta Master AI — Serie A 2026/27">
                    <div class="brand-icon-box" style="width:30px;height:30px;min-width:30px;min-height:30px;max-width:30px;max-height:30px;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,rgba(0,230,118,0.2),rgba(0,242,254,0.2));border:1px solid rgba(0,242,254,0.35);padding:2px;box-sizing:border-box;flex-shrink:0;">
                        <img src="/static/icon-192.png" alt="Logo" width="30" height="30" style="width:30px;height:30px;max-width:30px;max-height:30px;min-width:30px;min-height:30px;object-fit:cover;border-radius:5px;display:block;">
                    </div>
                    <div class="brand-text-wrap" style="display:inline-flex;align-items:baseline;gap:6px;line-height:1;">
                        <span class="brand-main-name" style="font-family:'Outfit',system-ui,-apple-system,sans-serif;font-weight:800;font-size:15px;color:#ffffff;letter-spacing:-0.2px;white-space:nowrap;text-decoration:none;">Fanta Master <span class="brand-gradient-tag" style="background:linear-gradient(135deg,#00e676,#00f2fe);-webkit-background-clip:text;-webkit-text-fill-color:transparent;color:#00f2fe;font-weight:900;">AI</span></span>
                    </div>
                    <span class="brand-season-capsule" style="font-family:'Inter',system-ui,-apple-system,sans-serif;font-size:10px;font-weight:700;color:#94a3b8;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);padding:2px 7px;border-radius:9999px;letter-spacing:0.3px;white-space:nowrap;text-decoration:none;">2026/27</span>
                </a>

                <button class="nav-btn-icon creator-only-control" id="tabLeaguesBtn" onclick="switchTab('leagues')" title="Hub Campionati & Leghe (Accesso Creatore)">
                    👑 Leghe
                </button>

                <!-- Hidden container preserving ID for JS state compatibility -->
                <span id="headerPageTitle" style="display:none;">Home — Statistiche Serie A</span>
            </div>

            <!-- CENTER: 2-PHASE MACRO NAVIGATION (GIORNATA & FORMAZIONE vs MERCATO & ASTA) -->
            <nav class="header-nav-groups">
                <!-- 0. HOME -->
                <a href="/" class="nav-direct-btn active" id="tabHomeNavBtn" onclick="onNavClick(event, 'home')" title="Home — Giornata &amp; Mercato Fantacalcio">
                    <span>🏠</span> Home
                </a>

                <!-- 0-BIS. LA MIA ROSA -->
                <button class="nav-direct-btn" id="tabMySquadNavBtn" onclick="openMySquadModal()" style="background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4); color: #4ade80;" title="Gestisci la tua Rosa e Calcola la Formazione Perfetta">
                    <span>📋</span> La Mia Rosa
                </button>

                <!-- 1. PROBABILI FORMAZIONI (DIRETTO ALLA PAGINA DEDICATA) -->
                <a href="/probabili-formazioni/" class="nav-direct-btn" id="tabProbabiliNavBtn" title="Probabili Formazioni Serie A &amp; Ballottaggi Consensus 4 Fonti">
                    <span>⚽</span> Probabili Formazioni
                </a>

                <!-- 2. CHI SCHIERO 1VS1 (DIRETTO) -->
                <a href="/chi-schiero/" class="nav-direct-btn" id="tabChiSchieroDirectBtn" onclick="onNavClick(event, 'chi_schiero')" title="Hai un dubbio tra 2 giocatori? Confrontali testa a testa con l'AI">
                    <span>⚔️</span> Chi Schiero 1vs1
                </a>

                <!-- FASE 1: GIORNATA & STATISTICHE -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupTactics" type="button" aria-haspopup="true">
                        <span>📊</span> Giornata &amp; Statistiche <span class="nav-caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/probabili-formazioni/" class="dropdown-item" id="tabPitchBtn">⚽ Probabili Formazioni &amp; Ballottaggi</a>
                        <a href="/chi-schiero/" class="dropdown-item" id="tabChiSchieroBtn" onclick="onNavClick(event, 'chi_schiero')">⚔️ Tool "Chi Schiero?" (Dubbi 1vs1)</a>
                        <a href="/consigli-fantacalcio/" class="dropdown-item" id="tabMatchdayAdviceBtn" onclick="onNavClick(event, 'matchday_advice')">🎯 Chi Schierare &amp; Consigli di Giornata</a>
                        <a href="/infortunati-serie-a/" class="dropdown-item">🩺 Infortunati, Squalificati &amp; Rientri</a>
                        <div class="dropdown-divider"></div>
                        <a href="/statistiche-serie-a/" class="dropdown-item" id="tabStatsBtn" onclick="onNavClick(event, 'stats')">📊 Statistiche &amp; xG Serie A</a>
                        <a href="/top-flop/" class="dropdown-item" id="tabTopFlopBtn" onclick="onNavClick(event, 'top_flop')">⚡ Top &amp; Flop di Giornata</a>
                        <a href="/match-report/" class="dropdown-item" id="tabMatchReportsBtn" onclick="onNavClick(event, 'match_reports')">📑 Match Reports &amp; Tabellini</a>
                        <a href="/football-analytics/" class="dropdown-item" id="tabMatrixBtn" onclick="onNavClick(event, 'matrix')">📈 Matrice &amp; Scatter Analytics</a>
                        <a href="/confronto-calciatori/" class="dropdown-item" id="tabMatchupBtn" onclick="onNavClick(event, 'matchup')">⚖️ Confronto Statistico Calciatori</a>
                    </div>
                </div>

                <!-- FASE 2: MERCATO & ASTA (ESTATE & RIPARAZIONE) -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAi" type="button" aria-haspopup="true">
                        <span>💰</span> Mercato &amp; Asta <span class="nav-caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/listone/" class="dropdown-item" id="tabAuctionBtn" onclick="onNavClick(event, 'auction')">📋 Listone Calciatori &amp; Valutazioni FVM</a>
                        <a href="/probabili-formazioni/como/" class="dropdown-item" onclick="onNavClick(event, 'pitch')">🏟️ Top 11 &amp; Gerarchie Stagionali (20 Squadre)</a>
                        <a href="/griglia-portieri/" class="dropdown-item" id="tabGkBtn" onclick="onNavClick(event, 'gk')">🧤 Griglia Portieri 38/38</a>
                        <a href="/rigoristi-serie-a/" class="dropdown-item">🎯 Rigoristi &amp; Calci Piazzati</a>
                        <a href="/scommesse-talenti/" class="dropdown-item" id="tabGemsBtn" onclick="onNavClick(event, 'gems')">🔮 Gemme &amp; Scommesse Low-Cost</a>
                        <a href="/top-11-ai/" class="dropdown-item" id="tabAiSquadsBtn" onclick="onNavClick(event, 'ai_squads')">🔒 5 Squadre Perfette AI <span style="font-size:10px;background:rgba(239,68,68,0.2);color:#f87171;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:6px;">In Aggiornamento</span></a>
                    </div>
                </div>
            </nav>

            <!-- RIGHT: MODERN ACTIONS -->
            <div class="header-right">
                <!-- CANALI SOCIAL: TELEGRAM & INSTAGRAM -->
                <a href="https://t.me/fantamasterai" target="_blank" rel="noopener noreferrer" class="social-header-btn social-btn-telegram" title="Canale Telegram Ufficiale @fantamasterai" aria-label="Canale Telegram Ufficiale">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.75-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .37z"/></svg>
                </a>
                <a href="https://www.instagram.com/fantamasterai" target="_blank" rel="noopener noreferrer" class="social-header-btn social-btn-instagram" title="Profilo Instagram Ufficiale @fantamasterai" aria-label="Profilo Instagram Ufficiale">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
                </a>

                <!-- CREATOR STATUS BADGE (Visibile solo se abilitato) -->
                <div id="creatorStatusBadge" class="creator-status-badge creator-only-control" onclick="openCreatorAuthModal()" title="👑 Modalità Creatore Attiva. Clicca per disattivare o gestire.">
                    <span>👑 Creatore Attivo</span>
                </div>

                <!-- METODOLOGIA & INFO AI BUTTON -->
                <button class="modern-header-pill-btn header-ai-info-pill" onclick="openAiMethodologyModal('ovr')" title="Trasparenza & Metodologia AI — Come funziona l'algoritmo">
                    <span class="pill-dot-cyan"></span>
                    <span class="header-pill-full-text">Come Funziona l'AI</span>
                    <span class="header-pill-short-text">AI</span>
                </button>

                <!-- PWA INSTALL BUTTON (Dinamico) -->
                <button id="btnPwaInstall" class="modern-header-pill-btn header-pwa-pill" style="display:none;color:#00e676;border-color:rgba(0,230,118,0.3);background:rgba(0,230,118,0.08);" onclick="triggerPwaInstall()" title="Installa l'App Fanta Master AI su Smartphone o PC">
                    <span>📲</span> <span class="header-pwa-full-text">Installa</span>
                </button>

                <!-- GESTIONE DROPDOWN -->
                <div class="nav-dropdown align-right">
                    <button class="modern-header-icon-btn" title="Opzioni e Strumenti">
                        <span>⚙️</span> <span class="nav-caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <!-- VISTA VISITATORE -->
                        <div class="visitor-only-item">
                            <div class="dropdown-header">Strumenti Listone</div>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="resetAllFilters()">🔄 Reimposta Filtri Listone</a>
                            <div class="dropdown-divider"></div>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="openCreatorAuthModal()" style="color:#fbbf24;font-weight:700;">👑 Accesso Riservato Creatore</a>
                        </div>

                        <!-- VISTA CREATORE (Strumenti Completi Sbloccati) -->
                        <div class="creator-only-block">
                            <div class="dropdown-header" style="color:var(--accent-gold);font-weight:900;">👑 Strumenti Creatore</div>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="openXlsxImportModal()">📗 Carica Rose da Excel (.xlsx)</a>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="openCsvRosterImportModal(State.currentTeam || 'Unika')">📂 Carica Rosa da CSV</a>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="openRosterModal('ALL_RIVALS')">🕵️ Rose Rivale (7 Squadre)</a>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="switchTab('home')">🏠 Hub Leghe & Crea Lega</a>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="exportTacticalDbJson()">📥 Esporta Database Tattico</a>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="exportCurrentLeagueJson()">💾 Scarica Backup JSON Lega</a>
                            <a href="javascript:void(0)" class="dropdown-item danger" onclick="resetLiveAuction()" style="color:#f87171;">🔄 Azzera Asta Lega Attiva</a>
                            <div class="dropdown-divider"></div>
                            <a href="javascript:void(0)" class="dropdown-item" onclick="openCreatorAuthModal()" style="color:#fbbf24;font-weight:700;font-size:11.5px;">👁️ Esci da Modalità Creatore</a>
                        </div>
                    </div>
                </div>

                <!-- MOBILE HAMBURGER MENU BUTTON (HIDDEN PER USER REQUEST: ONLY BOTTOM FLOATING NAV MENU IS KEPT) -->
                <button class="mobile-menu-trigger" id="btnMobileMenu" onclick="openMobileMenuModal()" title="Menu Navigazione & Opzioni" style="display:none !important;">☰</button>
            </div>
        </div>
    </header>

    <!-- Hidden Budget & Slots Container for Script Compatibility -->
    <div class="budget-bar-wrapper" style="display:none !important;">
        <span id="lblRemainingBudget"></span>
        <span id="lblSpentBudget"></span>
        <span id="lblSlotP"></span>
        <span id="lblSlotD"></span>
        <span id="lblSlotC"></span>
        <span id="lblSlotA"></span>
        <span id="lblMantraSlotPor"></span>
        <span id="lblMantraSlotMov"></span>
        <span id="lblMantraSlotTot"></span>
        <span id="lblMaxBidAllowed"></span>
    </div>

    <!-- Main Workspace -->
    <main>
        <!-- Tab 0: Home Hub (Tutte le Leghe & Campionati) -->
        <section id="viewHomeHub" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 0-Bis: Home Page Principale (Visual Command Center — Zero Fluff, 100% SEO) -->
        <section id="viewHome" class="tab-content active" style="display:flex;flex-direction:column;gap:16px;width:100%;">
            <div class="ai-hub-container hpro-wrapper">

                <!-- 1. COMPACT COMMAND HERO (RICERCA ISTANTANEA + SWITCH 2 FASI) -->
                <div class="ai-hub-hero hpro-command-hero">
                    <!-- Top Status Strip -->
                    <div class="hpro-status-strip">
                        <span class="ai-badge-chip live">
                            <span class="pulse-dot-green"></span>
                            LIVE • 11ª Giornata Serie A
                        </span>
                        <a href="/probabili-formazioni/" class="ai-badge-chip live" style="text-decoration:none;">
                            ⚽ Probabili 4 Fonti
                        </a>
                        <span class="ai-badge-chip tech">🎯 75% Hit Rate AI</span>
                    </div>

                    <!-- H1 SEO (1 riga compatta, zero paragrafi prolissi) -->
                    <h1 class="ai-hub-title hpro-main-h1">
                        Statistiche Fantacalcio, Probabili Formazioni &amp; <span class="gradient-text">Consigli AI Serie A</span>
                    </h1>

                    <!-- Omni-Search Bar Istantanea -->
                    <div class="ai-hub-search-wrap hpro-search-wrap">
                        <div class="ai-hub-search-inner">
                            <span class="ai-hub-search-icon">🔍</span>
                            <input type="text" id="hubQuickSearch" class="ai-hub-search-input" placeholder="Cerca calciatore o club (es. Malen, Nico Paz, Barella, Svilar)..." oninput="filterHubPlayers(this.value)" autocomplete="off">
                        </div>
                        <div id="hubSearchResults" class="ai-hub-search-results"></div>
                    </div>

                    <!-- Chip Trending Calciatori (Link SEO + Apertura Rapida) -->
                    <div class="ai-hub-quick-chips hpro-trending-chips">
                        <span class="quick-chip-lbl">🔥 Trending:</span>
                        <a href="/calciatore/malen/" class="hub-chip-btn" onclick="if(typeof openPlayerByName==='function'){{event.preventDefault();openPlayerByName('Malen');}}">🔥 Malen <small>97</small></a>
                        <a href="/calciatore/paz-n/" class="hub-chip-btn" onclick="if(typeof openPlayerByName==='function'){{event.preventDefault();openPlayerByName('Nico Paz');}}">💎 Paz N. <small>98</small></a>
                        <a href="/calciatore/barella/" class="hub-chip-btn" onclick="if(typeof openPlayerByName==='function'){{event.preventDefault();openPlayerByName('Barella');}}">⚡ Barella <small>96</small></a>
                        <a href="/calciatore/pulisic/" class="hub-chip-btn" onclick="if(typeof openPlayerByName==='function'){{event.preventDefault();openPlayerByName('Pulisic');}}">🎯 Pulisic <small>96</small></a>
                        <a href="/calciatore/dimarco/" class="hub-chip-btn" onclick="if(typeof openPlayerByName==='function'){{event.preventDefault();openPlayerByName('Dimarco');}}">🛡️ Dimarco <small>95</small></a>
                        <a href="/calciatore/svilar/" class="hub-chip-btn" onclick="if(typeof openPlayerByName==='function'){{event.preventDefault();openPlayerByName('Svilar');}}">🧤 Svilar <small>89</small></a>
                    </div>

                    <!-- TACTILE 2-PHASE APP SWITCHER (Zero Testo Inutile) -->
                    <div class="hpro-phase-switcher">
                        <button type="button" id="btnPhaseMatchday" class="hpro-phase-btn active" onclick="switchHomePhase('matchday')">
                            <span class="hpro-p-ico">⚽</span>
                            <div class="hpro-p-txt">
                                <span class="hpro-p-title">1. GIORNATA 11 <span class="hpro-p-badge green">LIVE</span></span>
                                <span class="hpro-p-sub">Probabili • Chi Schiero • La Tua Rosa • Infortuni</span>
                            </div>
                        </button>
                        <button type="button" id="btnPhaseMarket" class="hpro-phase-btn" onclick="switchHomePhase('market')">
                            <span class="hpro-p-ico">💰</span>
                            <div class="hpro-p-txt">
                                <span class="hpro-p-title">2. MERCATO &amp; ASTA <span class="hpro-p-badge amber">ROSA</span></span>
                                <span class="hpro-p-sub">Listone FVM • Top 11 Club • Portieri • Rigoristi</span>
                            </div>
                        </button>
                    </div>
                </div>

                <!-- =========================================================================
                     FASE 1 (DEFAULT): GIORNATA 11 — SCHIERA I TUOI 11 IN 1 CLICK
                     ========================================================================= -->
                <div id="homePhaseMatchday" class="hpro-phase-pane" style="display:flex;">

                    <!-- RIGA 1: DOCK OPERATIVO IMMEDIATO (LA TUA ROSA AI + CHI SCHIERO 1VS1) -->
                    <div class="hpro-action-dock">
                        <!-- Card 1: La Tua Rosa AI -->
                        <div class="hpro-dock-card squad" onclick="openMySquadModal()">
                            <div class="hpro-dc-top">
                                <div class="hpro-dc-ico green">📋</div>
                                <div class="hpro-dc-headings">
                                    <span class="hpro-dc-tag green">⚡ OTTIMIZZATORE 1-CLICK</span>
                                    <h2 class="hpro-dc-title">La Tua Rosa &amp; Miglior 11 AI</h2>
                                </div>
                            </div>
                            <div class="hpro-dc-pills">
                                <span class="hpro-mini-pill">🧠 Modulo Ideale</span>
                                <span class="hpro-mini-pill">👑 Capitano &amp; Panchina</span>
                                <span class="hpro-mini-pill">🛡️ Zero S.V.</span>
                            </div>
                            <button type="button" class="hpro-dc-btn green" onclick="event.stopPropagation(); openMySquadModal();">
                                <span>⚡ Inserisci Rosa &amp; Calcola 11</span>
                                <span>&rarr;</span>
                            </button>
                        </div>

                        <!-- Card 2: Chi Schiero 1vs1 -->
                        <div class="hpro-dock-card duel" onclick="switchTab('chi_schiero')">
                            <div class="hpro-dc-top">
                                <div class="hpro-dc-ico purple">⚔️</div>
                                <div class="hpro-dc-headings">
                                    <span class="hpro-dc-tag purple">⚖️ BALLOTTAGGIO SECCO</span>
                                    <h2 class="hpro-dc-title">Chi Schiero? Confronto 1vs1</h2>
                                </div>
                            </div>
                            <div class="hpro-dc-pills" onclick="event.stopPropagation();">
                                <a href="/chi-schiero/malen-vs-martinez-l/" class="hpro-duel-chip">⚔️ Malen vs Lautaro</a>
                                <a href="/chi-schiero/paz-n-vs-calhanoglu/" class="hpro-duel-chip">⚔️ Paz vs Calhanoglu</a>
                                <a href="/chi-schiero/pulisic-vs-zaccagni/" class="hpro-duel-chip">⚔️ Pulisic vs Zaccagni</a>
                            </div>
                            <a href="/chi-schiero/" class="hpro-dc-btn purple" onclick="event.stopPropagation(); onNavClick(event, 'chi_schiero');">
                                <span>⚔️ Confronta 2 Giocatori (1vs1)</span>
                                <span>&rarr;</span>
                            </a>
                        </div>
                    </div>

                    <!-- RIGA 2: STRISCIA VISUALE 10 PARTITE 11ª GIORNATA (PROBABILI FORMAZIONI 4 FONTI) -->
                    <div class="hpro-matches-box">
                        <div class="hpro-box-header">
                            <div class="hpro-bh-left">
                                <span class="hpro-bh-ico">⚽</span>
                                <div>
                                    <h2 class="hpro-bh-title">Probabili Formazioni 11ª Giornata</h2>
                                    <span class="hpro-bh-sub">Media Consensus 4 Fonti • Fantacalcio • Gazzetta • Sky • SOS Fanta</span>
                                </div>
                            </div>
                            <a href="/probabili-formazioni/" class="hpro-bh-cta">
                                Tutte le 10 Partite &rarr;
                            </a>
                        </div>
                        <div class="hpro-matches-grid">
{home_matches_strip_html}
                        </div>
                    </div>

                    <!-- RIGA 3: 4 TILES RAPIDE DI GIORNATA (ZERO PARAGRAFI, SOLO ICONA + KPI) -->
                    <div class="hpro-quick-tools-4">
                        <a href="/consigli-fantacalcio/" class="hpro-qtile pink" onclick="onNavClick(event, 'matchday_advice')">
                            <span class="hq-ico">🎯</span>
                            <div class="hq-body">
                                <span class="hq-title">Consigliati G11</span>
                                <span class="hq-meta">Top 11 &amp; Indice AI</span>
                            </div>
                            <span class="hq-arr">&rarr;</span>
                        </a>
                        <a href="/infortunati-serie-a/" class="hpro-qtile red">
                            <span class="hq-ico">🩺</span>
                            <div class="hq-body">
                                <span class="hq-title">Infortuni &amp; Squalifiche</span>
                                <span class="hq-meta">Bollettino 20 Club</span>
                            </div>
                            <span class="hq-arr">&rarr;</span>
                        </a>
                        <a href="/statistiche-serie-a/" class="hpro-qtile green" onclick="onNavClick(event, 'stats')">
                            <span class="hq-ico">📊</span>
                            <div class="hq-body">
                                <span class="hq-title">Statistiche &amp; xG</span>
                                <span class="hq-meta">534 Calciatori Live</span>
                            </div>
                            <span class="hq-arr">&rarr;</span>
                        </a>
                        <a href="/top-flop/" class="hpro-qtile amber" onclick="onNavClick(event, 'top_flop')">
                            <span class="hq-ico">⚡</span>
                            <div class="hq-body">
                                <span class="hq-title">Top, Flop &amp; Voti</span>
                                <span class="hq-meta">Pagelle &amp; Tabellini</span>
                            </div>
                            <span class="hq-arr">&rarr;</span>
                        </a>
                    </div>

                    <!-- RIGA 4: 3 FLASH PICKS G11 (CAPITANO, TRAPPOLA, GEMMA — ZERO MURI DI TESTO) -->
                    <div class="hpro-section-block">
                        <div class="hpro-sec-bar">
                            <h2 class="hpro-sec-h2"><span>⚡</span> Flash AI 11ª Giornata</h2>
                            <span class="hpro-sec-pill">Calcolo xFM Live</span>
                        </div>
                        <div class="ai-pulse-grid hpro-flash-grid">
                            <!-- Card 1: Top AI Pick & Capitano Ideale -->
                            <div class="ai-pulse-card pick" onclick="openPlayerByName('Malen')" style="cursor:pointer;">
                                <div class="pulse-card-header">
                                    <span class="pulse-badge green">🚀 CAPITANO AI</span>
                                    <span class="pulse-card-score" style="color:#4ade80;">98% Schierabile</span>
                                </div>
                                <div class="pulse-player-box">
                                    <span class="role-badge A" style="width:34px;height:34px;font-size:15px;">A</span>
                                    <div>
                                        <div class="pulse-player-name">Donyell Malen</div>
                                        <div class="pulse-player-sub">Roma • Attaccante • OVR 97</div>
                                    </div>
                                </div>
                                <div class="pulse-metrics-strip">
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">xFM G11</span>
                                        <span class="p-val" style="color:#00e676;">8.45</span>
                                    </div>
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">Partita</span>
                                        <span class="p-val" style="color:#38bdf8;">vs Sassuolo</span>
                                    </div>
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">Status</span>
                                        <span class="p-val" style="color:#fbbf24;">1° Rigorista</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Card 2: Flop & Trap Alert -->
                            <div class="ai-pulse-card danger" onclick="openPlayerByName('Laurient')" style="cursor:pointer;">
                                <div class="pulse-card-header">
                                    <span class="pulse-badge red">⚠️ RISCHIO FLOP</span>
                                    <span class="pulse-card-score" style="color:#f87171;">Diff. 4.7/5</span>
                                </div>
                                <div class="pulse-player-box">
                                    <span class="role-badge A" style="width:34px;height:34px;font-size:15px;">A</span>
                                    <div>
                                        <div class="pulse-player-name">Armand Laurienté</div>
                                        <div class="pulse-player-sub">Sassuolo • Attaccante • 77 CR</div>
                                    </div>
                                </div>
                                <div class="pulse-metrics-strip">
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">Partita</span>
                                        <span class="p-val" style="color:#f87171;">@ Roma</span>
                                    </div>
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">Ostacolo</span>
                                        <span class="p-val" style="color:#ef4444;">Muro Difesa</span>
                                    </div>
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">xFM G11</span>
                                        <span class="p-val" style="color:#fbbf24;">5.65 ↓</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Card 3: Scommessa & Differenziale AI -->
                            <div class="ai-pulse-card gem" onclick="openPlayerByName('Adzic')" style="cursor:pointer;">
                                <div class="pulse-card-header">
                                    <span class="pulse-badge purple">💎 GEMMA G11</span>
                                    <span class="pulse-card-score" style="color:#c084fc;">Upside +38%</span>
                                </div>
                                <div class="pulse-player-box">
                                    <span class="role-badge C" style="width:34px;height:34px;font-size:15px;">C</span>
                                    <div>
                                        <div class="pulse-player-name">Vasilije Adzic</div>
                                        <div class="pulse-player-sub">Sassuolo • Centrocampista • 11 CR</div>
                                    </div>
                                </div>
                                <div class="pulse-metrics-strip">
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">xG / 90m</span>
                                        <span class="p-val" style="color:#c084fc;">0.78</span>
                                    </div>
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">Bonus</span>
                                        <span class="p-val" style="color:#34d399;">3G + 1A</span>
                                    </div>
                                    <div class="pulse-metric-item">
                                        <span class="p-lbl">Costo</span>
                                        <span class="p-val" style="color:#fbbf24;">11 CR</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- RIGA 5: LEADER STATISTICI SERIE A 2026/27 (UNICA ISTANZA PULITA) -->
                    <div class="hpro-section-block">
                        <div class="hpro-sec-bar">
                            <h2 class="hpro-sec-h2"><span>🏆</span> Leader Serie A 2026/27</h2>
                            <a href="/statistiche-serie-a/" class="hpro-sec-link" onclick="onNavClick(event, 'stats')">Classifiche Complete &rarr;</a>
                        </div>
                        <div class="leader-grid" id="homeLeadersGrid">
{home_leaders_html}
                        </div>
                    </div>

                    <!-- RIGA 6: BARRA COMPATTA ACCURATEZZA AI CERTIFICATA -->
{hero_trust_showcase_html}

                </div>

                <!-- =========================================================================
                     FASE 2: MERCATO, ASTA & SCAMBI (CREAZIONE / RIPARAZIONE SQUADRA)
                     ========================================================================= -->
                <div id="homePhaseMarket" class="hpro-phase-pane" style="display:none;">

                    <!-- GRIGLIA VISUALE 6 STRUMENTI MERCATO (ZERO PARAGRAFI LUNGHI) -->
                    <div class="hpro-market-grid">
                        <a href="/listone/" class="hpro-mcard amber" onclick="onNavClick(event, 'auction')">
                            <div class="hmc-top">
                                <span class="hmc-ico">📋</span>
                                <span class="hmc-tag">1-1000 CR</span>
                            </div>
                            <h3 class="hmc-title">Listone &amp; Valori FVM</h3>
                            <div class="hmc-pills">
                                <span>534 Calciatori</span>
                                <span>Classic &amp; Mantra</span>
                                <span>Slot 1-8</span>
                            </div>
                            <span class="hmc-cta">Apri Listone &rarr;</span>
                        </a>

                        <a href="/probabili-formazioni/inter/" class="hpro-mcard pink">
                            <div class="hmc-top">
                                <span class="hmc-ico">🏟️</span>
                                <span class="hmc-tag">20 Club 2D</span>
                            </div>
                            <h3 class="hmc-title">Top 11 Stagionali Squadre</h3>
                            <div class="hmc-pills">
                                <span>Titolari Tipo</span>
                                <span>Staffette</span>
                                <span>Indice FRP</span>
                            </div>
                            <span class="hmc-cta">Esplora 20 Club &rarr;</span>
                        </a>

                        <a href="/griglia-portieri/" class="hpro-mcard cyan">
                            <div class="hmc-top">
                                <span class="hmc-ico">🧤</span>
                                <span class="hmc-tag">38 Giornate</span>
                            </div>
                            <h3 class="hmc-title">Griglia Portieri 38/38</h3>
                            <div class="hmc-pills">
                                <span>190 Coppie</span>
                                <span>Incroci Casa/Fuori</span>
                            </div>
                            <span class="hmc-cta">Apri Matrice &rarr;</span>
                        </a>

                        <a href="/rigoristi-serie-a/" class="hpro-mcard green">
                            <div class="hmc-top">
                                <span class="hmc-ico">🎯</span>
                                <span class="hmc-tag">Bonus +3</span>
                            </div>
                            <h3 class="hmc-title">Rigoristi &amp; Piazzati</h3>
                            <div class="hmc-pills">
                                <span>1° / 2° / 3° Tiratore</span>
                                <span>Punizioni &amp; Corner</span>
                            </div>
                            <span class="hmc-cta">Vedi Gerarchie &rarr;</span>
                        </a>

                        <a href="/scommesse-talenti/" class="hpro-mcard purple" onclick="onNavClick(event, 'gems')">
                            <div class="hmc-top">
                                <span class="hmc-ico">🔮</span>
                                <span class="hmc-tag">Colpacci 1 CR</span>
                            </div>
                            <h3 class="hmc-title">Gemme &amp; Scommesse</h3>
                            <div class="hmc-pills">
                                <span>Low-Cost</span>
                                <span>Alto xG/90</span>
                            </div>
                            <span class="hmc-cta">Scopri Talenti &rarr;</span>
                        </a>

                        <a href="/confronto-calciatori/" class="hpro-mcard blue" onclick="onNavClick(event, 'matchup')">
                            <div class="hmc-top">
                                <span class="hmc-ico">⚖️</span>
                                <span class="hmc-tag">Scambi &amp; Asta</span>
                            </div>
                            <h3 class="hmc-title">Confronto Radar 1vs1</h3>
                            <div class="hmc-pills">
                                <span>Radar 6 Assi</span>
                                <span>OVR &amp; FVM</span>
                            </div>
                            <span class="hmc-cta">Confronta Profili &rarr;</span>
                        </a>
                    </div>

                    <!-- ACCESSO DIRETTO TOP 11 STAGIONALI DEI 20 CLUB (OTTIMO PER UX MERCATO + SEO) -->
                    <div class="hpro-clubs-box">
                        <div class="hpro-sec-bar" style="margin-bottom:10px;">
                            <h2 class="hpro-sec-h2"><span>🏟️</span> Top 11 &amp; Gerarchie Stagionali (20 Club Serie A)</h2>
                            <span class="hpro-sec-pill">Titolari Base per Asta &amp; Mercato</span>
                        </div>
                        <div class="hpro-clubs-grid">
                            <a href="/probabili-formazioni/atalanta/" class="hpro-club-pill">Atalanta</a>
                            <a href="/probabili-formazioni/bologna/" class="hpro-club-pill">Bologna</a>
                            <a href="/probabili-formazioni/cagliari/" class="hpro-club-pill">Cagliari</a>
                            <a href="/probabili-formazioni/como/" class="hpro-club-pill">Como</a>
                            <a href="/probabili-formazioni/fiorentina/" class="hpro-club-pill">Fiorentina</a>
                            <a href="/probabili-formazioni/frosinone/" class="hpro-club-pill">Frosinone</a>
                            <a href="/probabili-formazioni/genoa/" class="hpro-club-pill">Genoa</a>
                            <a href="/probabili-formazioni/inter/" class="hpro-club-pill">Inter</a>
                            <a href="/probabili-formazioni/juventus/" class="hpro-club-pill">Juventus</a>
                            <a href="/probabili-formazioni/lazio/" class="hpro-club-pill">Lazio</a>
                            <a href="/probabili-formazioni/lecce/" class="hpro-club-pill">Lecce</a>
                            <a href="/probabili-formazioni/milan/" class="hpro-club-pill">Milan</a>
                            <a href="/probabili-formazioni/napoli/" class="hpro-club-pill">Napoli</a>
                            <a href="/probabili-formazioni/parma/" class="hpro-club-pill">Parma</a>
                            <a href="/probabili-formazioni/pisa/" class="hpro-club-pill">Pisa</a>
                            <a href="/probabili-formazioni/roma/" class="hpro-club-pill">Roma</a>
                            <a href="/probabili-formazioni/sassuolo/" class="hpro-club-pill">Sassuolo</a>
                            <a href="/probabili-formazioni/torino/" class="hpro-club-pill">Torino</a>
                            <a href="/probabili-formazioni/udinese/" class="hpro-club-pill">Udinese</a>
                            <a href="/probabili-formazioni/venezia/" class="hpro-club-pill">Venezia</a>
                        </div>
                    </div>

                </div>

            </div>
        </section>

        <!-- Tab 1: Tabellone Asta -->
        <section id="viewAuction" class="tab-content auction-main-layout" style="display:none;">
            <!-- Left: Filters & Table -->
            <div class="auction-table-column" id="auctionTableColumn" style="flex:1;min-width:0;display:flex;flex-direction:column;gap:12px;">
                
                <!-- HERO WELCOME & ACTION HUB (PRIMO IMPATTO VISIVO MODERNO) -->
                <div class="portal-hero-section">
                    <div class="portal-hero-header">
                        <div class="portal-hero-title-group">
                            <h2 style="font-size:22px;font-weight:900;margin:0 0 6px 0;">⚽ Fanta Master <span class="gradient-text">AI</span></h2>
                            <p>Il motore quantitativo che trasforma statistiche avanzate (xG, xA, xFM) in decisioni vincenti per il tuo Fantacalcio.</p>
                        </div>
                        <div class="portal-hero-pills">
                            <span class="brand-badge" style="background:rgba(0,230,118,0.15);color:#00e676;border:1px solid rgba(0,230,118,0.3);padding:6px 12px;border-radius:20px;font-weight:800;font-size:12px;">✓ Serie A 2026/27</span>
                            <span class="brand-badge" style="background:rgba(0,242,254,0.15);color:#00f2fe;border:1px solid rgba(0,242,254,0.3);padding:6px 12px;border-radius:20px;font-weight:800;font-size:12px;">🔮 Algoritmo Predittivo</span>
                        </div>
                    </div>

                    <!-- 3 Action Cards ad Alto Valore -->
                    <div class="hero-feature-grid">
                        <div class="hero-card" onclick="switchTab('chi_schiero')">
                            <div class="hero-card-icon" style="background:linear-gradient(135deg,rgba(0,242,254,0.15),rgba(56,189,248,0.25));color:var(--accent-cyan);">⚔️</div>
                            <div class="hero-card-content">
                                <div class="hero-card-title">Chi Schiero? 1vs1</div>
                                <div class="hero-card-desc">Risolvi i tuoi dubbi di formazione con il confronto testa a testa AI</div>
                            </div>
                            <span class="hero-card-action">➔</span>
                        </div>

                        <div class="hero-card" onclick="switchTab('matchday_advice')">
                            <div class="hero-card-icon" style="background:linear-gradient(135deg,rgba(0,230,118,0.15),rgba(34,197,94,0.25));color:var(--accent-neon);">🎯</div>
                            <div class="hero-card-content">
                                <div class="hero-card-title">I Consigliati del Turno</div>
                                <div class="hero-card-desc">Top 11, indici di schierabilità e bonus attesi per la giornata</div>
                            </div>
                            <span class="hero-card-action">➔</span>
                        </div>

                        <div class="hero-card" onclick="switchTab('gems')">
                            <div class="hero-card-icon" style="background:linear-gradient(135deg,rgba(168,85,247,0.15),rgba(147,51,234,0.25));color:var(--accent-purple);">🔮</div>
                            <div class="hero-card-content">
                                <div class="hero-card-title">Gemme & Scommesse</div>
                                <div class="hero-card-desc">Calciatori low-cost con alto volume di xG/xA a prezzo stracciato</div>
                            </div>
                            <span class="hero-card-action">➔</span>
                        </div>

                        <div class="hero-card" onclick="switchTab('match_reports')" style="border-color:rgba(56,189,248,0.45);">
                            <div class="hero-card-icon" style="background:linear-gradient(135deg,rgba(56,189,248,0.2),rgba(14,165,233,0.3));color:#38bdf8;">📑</div>
                            <div class="hero-card-content">
                                <div class="hero-card-title">Match Reports G8 <span style="font-size:10px;background:rgba(239,68,68,0.25);color:#f87171;padding:1px 5px;border-radius:4px;font-weight:800;margin-left:4px;">Nuovo</span></div>
                                <div class="hero-card-desc">Tabellini ufficiali, km corsi, formazioni e analisi AI dei 6 match</div>
                            </div>
                            <span class="hero-card-action">➔</span>
                        </div>
                    </div>
                </div>

                <!-- Clean Modern Filter Bar (DESKTOP: 1 RIGA UNICA / MOBILE: 2 RIGHE STREAMLINED) -->
                <div class="clean-filter-bar">
                    <!-- 1. Switch Classic / Mantra -->
                    <div class="auction-mode-switch-group" id="auctionModeSwitchContainer" title="Modalità di visualizzazione per questo Tabellone Super Partes">
                        <button type="button" class="auction-mode-toggle-btn active" id="btnAuctionModeClassic" onclick="setAuctionTableMode('classic')">⚡ Classic</button>
                        <button type="button" class="auction-mode-toggle-btn" id="btnAuctionModeMantra" onclick="setAuctionTableMode('mantra')">💎 Mantra</button>
                    </div>

                    <!-- 2. Ruoli e Quick Toggles (Inline su Desktop, Scroll su Mobile) -->
                    <div class="filter-pills-row" id="filterPillsRow">
                        <!-- Role Quick Chips (Classic) -->
                        <div class="role-chip-group" id="classicRoleChipsGroup">
                            <button class="role-chip active" data-role="ALL" onclick="setRoleFilterQuick('ALL')">TUTTI</button>
                            <button class="role-chip P" data-role="P" onclick="setRoleFilterQuick('P')">🧤 P</button>
                            <button class="role-chip D" data-role="D" onclick="setRoleFilterQuick('D')">🛡️ D</button>
                            <button class="role-chip C" data-role="C" onclick="setRoleFilterQuick('C')">🪄 C</button>
                            <button class="role-chip A" data-role="A" onclick="setRoleFilterQuick('A')">⚡ A</button>
                        </div>

                        <!-- Quick Toggles -->
                        <div class="quick-toggles" id="auctionQuickToggles">
                            <button id="btnToggleFav" class="chip-toggle" onclick="toggleFavFilterQuick()">⭐ Preferiti</button>
                            <button id="btnToggleAvail" class="chip-toggle" onclick="toggleAvailFilterQuick()">🟢 Svincolati</button>
                            <button id="btnToggleHot" class="chip-toggle" onclick="toggleHotFilterQuick()" title="Calciatori in forma">🔥 In Forma</button>
                            <button id="btnToggleRig" class="chip-toggle" onclick="toggleRigFilterQuick()" title="Tutti i rigoristi">🎯 Rigoristi</button>
                            <button id="btnToggleOop" class="chip-toggle" onclick="toggleOopFilterQuick()" title="Fuori Ruolo Positivo">💎 FRP</button>
                        </div>
                    </div>

                    <!-- 3. Search Bar Principale -->
                    <div class="search-group" id="filterSearchGroup">
                        <input type="text" id="searchBox" class="clean-input-search" placeholder="🔍 Cerca calciatore, club..." oninput="onSearchChange(this.value)">
                    </div>

                    <!-- 4. Advanced Filter Drawer Button -->
                    <div class="filter-actions-right">
                        <button id="btnAdvancedFilters" class="btn-clean-action" onclick="toggleAdvancedFiltersDrawer()" title="Apri filtri avanzati per budget, slot, club e prezzi">
                            <span>⚙️ Filtri</span>
                        </button>
                    </div>
                </div>

                <!-- Hidden inputs for compatibility with existing state handlers -->
                <input type="checkbox" id="chkOnlyFavorites" style="display:none;" onchange="onToggleOnlyFavorites(this.checked)">
                <input type="checkbox" id="chkOnlyAvailable" style="display:none;" onchange="onToggleOnlyAvailable(this.checked)">
                <input type="checkbox" id="chkOop" style="display:none;" onchange="onToggleOop(this.checked)">
                <input type="checkbox" id="chkInj" style="display:none;" onchange="onToggleInjured(this.checked)">
                <input type="checkbox" id="chkHealthy" style="display:none;" onchange="onToggleHealthy(this.checked)">
                <select id="filterRole" style="display:none;"><option value="ALL">ALL</option></select>

                <!-- Advanced Filters Collapsible Drawer (COMPLETO DI BUDGET E CLUB NEL DRAWER) -->
                <div id="advancedFiltersDrawer" class="advanced-filters-drawer" style="display:none;">
                    <div class="advanced-filters-grid">
                        <!-- BUDGET CALCOLATO (ESTESO SU 2 COLONNE IN ALTO) -->
                        <div class="adv-filter-item adv-filter-span-all">
                            <label>Budget Calcolato</label>
                            <div class="auction-budget-switch-group" id="auctionBudgetSwitchContainer" style="display:flex;width:100%;gap:4px;" title="Budget di Riferimento per Valutazioni & Prezzi Asta">
                                <button type="button" class="auction-budget-btn active" style="flex:1;" id="btnBudget1000" onclick="setGlobalBudget(1000)">1000 CR</button>
                                <button type="button" class="auction-budget-btn" style="flex:1;" id="btnBudget500" onclick="setGlobalBudget(500)">500 CR</button>
                                <button type="button" class="auction-budget-btn" style="flex:1;" id="btnBudgetCustom" onclick="promptCustomBudget()" title="Imposta budget personalizzato">⚙️ Custom</button>
                            </div>
                        </div>

                        <div class="adv-filter-item">
                            <label>Filtra per Club</label>
                            <select id="filterTeam" class="clean-select-sub" onchange="onFilterTeamChange(this.value)">
                                <option value="ALL">Tutti i 20 Club</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>Fascia / Slot</label>
                            <select id="filterSlot" class="clean-select-sub" onchange="onFilterSlotChange(this.value)">
                                <option value="ALL">Tutti gli Slot</option>
                                <option value="1° Slot">1° Slot (Top)</option>
                                <option value="2° Slot">2° Slot (Semitiolari)</option>
                                <option value="3° Slot">3° Slot (Titolari)</option>
                                <option value="4° Slot">4° Slot</option>
                                <option value="5° Slot">5° Slot</option>
                                <option value="6° Slot">6° Slot</option>
                                <option value="7° Slot">7° Slot</option>
                                <option value="8° Slot">8° Slot</option>
                                <option value="Riserva">Riserve / Scommesse</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>Consiglio AI</label>
                            <select id="filterAdvice" class="clean-select-sub" onchange="onFilterAdviceChange(this.value)">
                                <option value="ALL">Tutti i Consigli</option>
                                <option value="top">👑 Top Player</option>
                                <option value="leader">⭐ Leader</option>
                                <option value="buy">🚀 Best Value</option>
                                <option value="titolarissimo">🔒 Titolarissimo (100%)</option>
                                <option value="titolare">🛡️ Titolare (75-94%)</option>
                                <option value="hot">🔥 In Forma (ultime giornate)</option>
                                <option value="rotation">🔄 Ballottaggio</option>
                                <option value="supersub">⚡ Super-Sub / Jolly</option>
                                <option value="sleeper">🔥 Scommessa</option>
                                <option value="lowcost">🪙 Low Cost</option>
                                <option value="benched">🪑 In Panchina</option>
                                <option value="flop">⚠️ A Rischio / Flop</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>🎯 Rigori & Piazzati</label>
                            <select id="filterRigoristi" class="clean-select-sub" onchange="onFilterRigoristiChange(this.value)">
                                <option value="ALL">Tutti</option>
                                <option value="any_rig">🎯 Tutti i Rigoristi</option>
                                <option value="rig_1">🥇 1° Rigoristi</option>
                                <option value="rig_2_3">🥈 2° / 3° Rigoristi</option>
                                <option value="piazzati">📐 Punizioni & Corner</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>Titolarità</label>
                            <select id="filterTitolarita" class="clean-select-sub" onchange="onFilterTitolaritaChange(this.value)">
                                <option value="ALL">Tutte le %</option>
                                <option value="tit_85">🔒 Titolarissimi (≥85%)</option>
                                <option value="tit_70">🛡️ Titolari (70-84%)</option>
                                <option value="tit_ballottaggio">🔄 Ballottaggio (50-69%)</option>
                                <option value="tit_riserva">🪑 Riserve (&lt;50%)</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>Fascia Prezzo (FVM)</label>
                            <select id="filterPriceRange" class="clean-select-sub" onchange="onFilterPriceRangeChange(this.value)">
                                <option value="ALL">Tutti i Prezzi</option>
                                <option value="top">👑 Top Player (&gt;100 CR)</option>
                                <option value="high">💎 Fascia Alta (40-100 CR)</option>
                                <option value="mid">⚖️ Fascia Media (15-39 CR)</option>
                                <option value="low">🪙 Low Cost (5-14 CR)</option>
                                <option value="budget">🎟️ Budget 1-4 CR</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>Infortuni & Integrità</label>
                            <select id="filterFragilita" class="clean-select-sub" onchange="setFragilitaFilter(this.value)">
                                <option value="ALL">Tutti i Giocatori</option>
                                <option value="bassa">🟢 Solo Integri</option>
                                <option value="media">🟡 Discontinui</option>
                                <option value="alta">🔴 Solo Infortunati / Fragili</option>
                            </select>
                        </div>

                        <div class="adv-filter-item">
                            <label>🔮 Ordinamento & Expected</label>
                            <select id="filterSortSelect" class="clean-select-sub" onchange="setSort(this.value)">
                                <option value="ovr">⭐ Overall Decrescente (Top)</option>
                                <option value="fvm">💰 FVM (Fanta Valore Mercato)</option>
                                <option value="fm_2627">📈 FantaMedia Reale (FM)</option>
                                <option value="xfm">🔮 Expected FantaMedia (xFM)</option>
                                <option value="delta_xfm">💎 Sotto-performanti (Occasioni AI: xFM > FM)</option>
                                <option value="delta_xfm_desc">⚠️ Sovra-performanti (Rischio Regressione: FM > xFM)</option>
                                <option value="mv_2627">📊 Media Voto Pura (MV)</option>
                                <option value="titolarita">🔒 Titolarità %</option>
                                <option value="name">🔤 Nome Alfabetico</option>
                            </select>
                        </div>

                        <!-- RESET FILTRI (ESTESO SU 2 COLONNE IN BASSO, SOTTILE E PULITO) -->
                        <div class="adv-filter-item adv-filter-span-all" style="margin-top:4px;">
                            <button class="btn-clean-reset-full" onclick="resetAllFilters()" title="Reimposta tutti i filtri">↺ Reset Filtri</button>
                        </div>
                    </div>
                </div>

                <div class="table-subbar-container" style="display:flex;align-items:center;justify-content:space-between;padding:6px 6px 10px 6px;flex-wrap:wrap;gap:12px;">
                    <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
                        <span id="lblPlayerCount" style="color:var(--text-secondary);font-weight:700;font-size:12.5px;">Mostrati: 535 / 535 Calciatori</span>

                        <!-- Selettore Quantità Calciatori: 50 / 100 / 200 / Tutti -->
                        <div class="page-size-selector-group" id="auctionPageSizeGroup" style="display:inline-flex;align-items:center;gap:6px;">
                            <span style="color:var(--text-muted);font-size:11.5px;font-weight:800;text-transform:uppercase;letter-spacing:0.4px;">Mostra:</span>
                            <div class="page-size-buttons" style="display:inline-flex;background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:2px;gap:2px;">
                                <button type="button" class="btn-page-size" data-size="50" onclick="setAuctionPageSize(50)" title="Mostra 50 calciatori per pagina">50</button>
                                <button type="button" class="btn-page-size" data-size="100" onclick="setAuctionPageSize(100)" title="Mostra 100 calciatori per pagina">100</button>
                                <button type="button" class="btn-page-size" data-size="200" onclick="setAuctionPageSize(200)" title="Mostra 200 calciatori per pagina">200</button>
                                <button type="button" class="btn-page-size active" data-size="all" onclick="setAuctionPageSize('all')" title="Mostra tutti i calciatori">Tutti</button>
                            </div>
                        </div>

                        <!-- Paginazione Superiore (attiva solo se selezionato 50/100/200) -->
                        <div id="auctionPaginationControls" class="pagination-controls" style="display:none;align-items:center;gap:6px;">
                            <button type="button" id="btnPrevPage" class="btn-pagination" onclick="changeAuctionPage(-1)" title="Pagina precedente">◀ Prec</button>
                            <span id="lblPaginationInfo" style="color:#38bdf8;font-size:12px;font-weight:800;">Pagina 1 di 6</span>
                            <button type="button" id="btnNextPage" class="btn-pagination" onclick="changeAuctionPage(1)" title="Pagina successiva">Succ ▶</button>
                        </div>
                    </div>

                    <div class="table-view-toggle" id="auctionTableViewToggle" role="group" aria-label="Visuale Tabella">
                        <span class="table-view-label">Visuale:</span>
                        <button type="button" class="btn-view-toggle active" id="btnViewStandard" onclick="setAuctionTableView('standard')" title="Visuale standard e pulita">
                            <span>📋 Standard</span>
                        </button>
                        <button type="button" class="btn-view-toggle" id="btnViewAdvanced" onclick="setAuctionTableView('advanced')" title="Visuale avanzata con più statistiche (xG, xA, Minuti, Cartellini)">
                            <span>📊 Statistiche Avanzate</span>
                        </button>
                    </div>
                </div>

                <!-- MANTRA SUB-POSITIONS QUICK FILTER BAR -->
                <div id="mantraQuickSubrolesBar" class="mantra-subroles-bar" style="display:none;"></div>

                <div class="table-wrapper">
                    <table class="fanta-table main-auction-table clean-table" id="auctionTable">
                        <thead>
                            <tr>
                                <th onclick="setSort('ovr')" style="width:48px;text-align:center;cursor:pointer;" title="Overall Scientifico (Rating AI 45-98)">OVR</th>
                                <th onclick="setSort('role')" id="thRoleHeader" style="width:36px;text-align:center;cursor:pointer;" title="Ruolo">R</th>
                                <th onclick="setSort('name')" style="cursor:pointer;">Calciatore & Mantra</th>
                                <th onclick="setSort('team')" style="cursor:pointer;">Club</th>
                                <th onclick="setSort('fvm')" style="text-align:center;cursor:pointer;" title="Fanta Valore di Mercato">FVM</th>
                                <th onclick="setSort('qta')" class="col-hide-on-standard" style="text-align:center;cursor:pointer;" title="Quotazione Ufficiale">Qt.</th>
                                <th onclick="setSort('ai_advice')" style="cursor:pointer;" title="Tag Smart AI (Consigli d'Asta, Rigoristi, Fuori Ruolo Positivo - FRP)">Tag AI & Strategia</th>
                                <th onclick="setSort('titolarita')" style="text-align:center;cursor:pointer;" title="Percentuale Titolarità">Tit.</th>
                                <th onclick="setSort('coppia_nome')" class="col-hide-on-standard" style="cursor:pointer;" title="Sostituto / Staffetta di Reparto">Sostituto / Coppia</th>
                                <th onclick="setSort('mv_2627')" class="col-hide-on-standard" style="text-align:center;cursor:pointer;" title="Media Voto 2026/27">MV</th>
                                <th onclick="setSort('fm_2627')" style="text-align:center;cursor:pointer;" title="FantaMedia Reale 2026/27">FM</th>
                                <th onclick="setSort('xfm')" class="col-hide-on-standard" style="text-align:center;cursor:pointer;" title="Expected FantaMedia (xFM) - FantaMedia Attesa dal Modello AI">xFM</th>
                                <th onclick="setSort('delta_xfm')" class="col-hide-on-standard" style="text-align:center;cursor:pointer;" title="Delta Performance (FM - xFM): Verde=Overperforming, Oro/Rosso=Underperforming/Occasione">Δ xFM</th>
                                <th onclick="setSort('gol_2627')" class="col-hide-on-standard" style="text-align:center;cursor:pointer;" title="Gol / Assist 2026/27">Gol/Ass</th>
                                <th onclick="setSort('xg_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Expected Goals (xG 2026/27)">xG</th>
                                <th onclick="setSort('xa_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Expected Assists (xA 2026/27)">xA</th>
                                <th onclick="setSort('minuti_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Minuti Giocati 2026/27">Min'</th>
                                <th onclick="setSort('amm_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Cartellini Gialli e Rossi (Amm/Esp)">Cart.</th>
                                <th style="width:48px;text-align:center;" title="Scheda Calciatore">Info</th>
                            </tr>
                        </thead>
                        <tbody id="auctionTableBody"></tbody>
                    </table>

                    <!-- Paginazione Inferiore (visibile solo se non è 'Tutti' e ci sono più pagine) -->
                    <div id="auctionBottomPaginationControls" class="pagination-controls" style="display:none;align-items:center;justify-content:center;gap:10px;padding:14px 10px;border-top:1px solid rgba(255,255,255,0.06);background:rgba(11,15,23,0.6);">
                        <button type="button" id="btnPrevPageBottom" class="btn-pagination" onclick="changeAuctionPage(-1)" title="Pagina precedente">◀ Pagina Precedente</button>
                        <span id="lblPaginationInfoBottom" style="color:#38bdf8;font-size:12.5px;font-weight:800;">Pagina 1 di 6</span>
                        <button type="button" id="btnNextPageBottom" class="btn-pagination" onclick="changeAuctionPage(1)" title="Pagina successiva">Pagina Successiva ▶</button>
                    </div>
                </div>
            </div>

            <!-- Hidden Container for JS compatibility -->
            <div id="sidebarRosterContainer" style="display:none !important;"></div>
        </section>

        <!-- Tab: Consigliati Prossima Giornata (AI & Report) -->
        <section id="viewMatchdayAdvice" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab: Tool "Chi Schiero?" (Ballottaggi 1vs1) -->
        <section id="viewChiSchiero" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab: 5 Squadre Perfette Consigliate dall'AI -->
        <section id="viewAiSquads" class="tab-content" style="display:none;">
        </section>

        <!-- Tab: Creazione Squadra & AI Squad Builder -->
        <section id="viewSquadBuilder" class="tab-content" style="display:none;">
            <div id="squadBuilderContainer"></div>
        </section>

        <!-- Tab 2: Campo 2D & Tattica -->
        <section id="viewPitch" class="tab-content" style="display:none;">
            <div class="filter-panel" style="justify-content:space-between;margin-bottom:8px;">
                <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                    <label style="font-size:12px;font-weight:800;color:var(--text-secondary);">SELEZIONA CLUB:</label>
                    <select id="selectPitchTeam" class="select-filter" onchange="renderPitchTeam(this.value)">
                    </select>
                    <button class="btn-action creator-only-control" id="btnEditPitchLineup" onclick="openTacticalEditorModal()" style="background:linear-gradient(135deg, rgba(0,242,254,0.18) 0%, rgba(56,189,248,0.25) 100%);border:1px solid var(--accent-cyan);color:#fff;font-weight:800;padding:6px 14px;border-radius:8px;align-items:center;gap:7px;cursor:pointer;transition:all 0.2s ease;">
                        ⚙️ Modifica Formazione & Sostituti
                    </button>
                    <button class="btn-action creator-only-control" onclick="autoFillAndSaveCurrentTeam()" style="background:linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(109,40,217,0.3) 100%);border:1px solid rgba(139,92,246,0.5);color:#c084fc;font-weight:800;padding:6px 14px;border-radius:8px;align-items:center;gap:7px;cursor:pointer;transition:all 0.2s ease;" title="Popola e salva automaticamente titolari e sostituti da dati reali 2026/27">
                        🤖 Auto-Fill da Titolarità
                    </button>
                </div>
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <button class="btn-action creator-only-control" onclick="autoFillAllTeams()" style="font-size:11.5px;background:linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(109,40,217,0.15) 100%);border-color:rgba(139,92,246,0.35);color:#c084fc;font-weight:700;" title="Auto-Fill e salva per tutte le 20 squadre di Serie A">
                        🤖 Auto-Fill Tutte le Squadre
                    </button>
                    <button class="btn-action creator-only-control" onclick="exportTacticalDbJson()" style="font-size:11.5px;background:rgba(255,255,255,0.05);border-color:rgba(255,255,255,0.15);" title="Scarica il file tactical_db.json ufficiale aggiornato">
                        📥 Esporta Database Tattico
                    </button>
                    <button class="btn-action" id="btnSharePitch" onclick="exportPitchScreenshot()" style="font-size:12px;background:linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(5,150,105,0.3) 100%);border:1px solid #10b981;color:#34d399;font-weight:800;padding:6px 14px;border-radius:8px;display:flex;align-items:center;gap:6px;cursor:pointer;" title="Scarica o condividi l'immagine grafica del campo da calcetto su WhatsApp">
                        <span>📸</span> <span>Condividi Formazione</span>
                    </button>
                    <div style="font-size:12px;color:var(--text-secondary);">
                        💡 Clicca su qualsiasi calciatore in campo o nella tabella per aprire la Scheda Profilo.
                    </div>
                </div>
            </div>

            <!-- Barra di Selezione Rapida dei 20 Club di Serie A -->
            <div class="pitch-club-quick-bar" id="pitchClubQuickBar"></div>

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

                        <div class="pitch-band" id="pitchAtt"></div>
                        <div class="pitch-band" id="pitchTrq"></div>
                        <div class="pitch-band" id="pitchMed"></div>
                        <div class="pitch-band" id="pitchDef"></div>
                        <div class="pitch-band" id="pitchPor"></div>
                    </div>
                </div>

                <div id="teamTacticsDashboard" class="pitch-side-grid"></div>
            </div>

            <!-- Tabella Rosa Completa del Club Selezionato -->
            <div id="teamRosterTableContainer"></div>
        </section>

        <!-- Tab 3: Matchup 1vs1 -->
        <section id="viewMatchup" class="tab-content" style="display:none;">
            <div class="filter-panel" style="justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:16px;">
                    <div class="filter-box">
                        <label style="color:var(--accent-cyan);">Calciatore A (Blu)</label>
                        <select id="selectMatchupA" class="select-filter" onchange="updateMatchup()"></select>
                    </div>
                    <div style="font-size:20px;font-weight:900;color:var(--text-muted);margin-top:16px;">VS</div>
                    <div class="filter-box">
                        <label style="color:#f472b6;">Calciatore B (Rosa)</label>
                        <select id="selectMatchupB" class="select-filter" onchange="updateMatchup()"></select>
                    </div>
                </div>
            </div>

            <div id="matchupComparisonContainer"></div>
        </section>

        <!-- Tab 4: Griglia Portieri -->
        <section id="viewGk" class="tab-content" style="display:none;">
            <div class="filter-panel" style="justify-content:space-between;">
                <div class="nav-tabs" style="border:none;">
                    <button class="tab-btn active" id="btnGkPairs" onclick="switchGkSubTab('pairs')">Top Coppie & Alternanza</button>
                    <button class="tab-btn" id="btnGkMatrix" onclick="switchGkSubTab('matrix')">Matrice Incroci Heatmap</button>
                </div>
            </div>

            <div id="gkFilterPanel" class="filter-panel">
                <div class="filter-box">
                    <label>Filtra per Club</label>
                    <select id="filterGkTeam" class="select-filter" onchange="renderGkGrid()">
                        <option value="ALL">Tutti i Club</option>
                    </select>
                </div>

                <div class="filter-box">
                    <label>Filtra per Portiere</label>
                    <select id="filterGkPlayer" class="select-filter" onchange="renderGkGrid()">
                        <option value="ALL">Tutti i Portieri</option>
                    </select>
                </div>

                <div class="filter-box">
                    <label>Fascia Incrocio</label>
                    <select id="filterGkTier" class="select-filter" onchange="renderGkGrid()">
                        <option value="ALL">Tutte le Fasce</option>
                        <option value="perfect">Incrocio Perfetto (38/38 Casa)</option>
                        <option value="elite">Elite (34+/38 Casa)</option>
                        <option value="optimal">Ottimale (32/38 Casa)</option>
                    </select>
                </div>
            </div>

            <div id="gkPairsView">
                <div id="gkGridTable"></div>
            </div>

            <div id="gkMatrixView" style="display:none;">
                <div id="gkMatrixContainer"></div>
            </div>
        </section>

        <!-- Tab 5: Gemme Nascoste & Scommesse AI -->
        <section id="viewGems" class="tab-content" style="display:none;">
        </section>

        <!-- Tab 6: AI Trade Machine (Mercato Scambi) -->
        <section id="viewTradeMachine" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 7: Mercato di Riparazione & Svincoli -->
        <section id="viewRepairAuction" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 8: Pagelle della Lega & AI Roast -->
        <section id="viewLeagueReport" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 9: Top & Flop di Giornata -->
        <section id="viewTopFlop" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 9b: Match Reports & Analisi Partite Ufficiali -->
        <section id="viewMatchReports" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 9c: Matrice & Scatter Analytics -->
        <section id="viewMatrix" class="tab-content" style="display:none;width:100%;">
        </section>

        <!-- Tab 10: Statistiche Serie A -->
        <section id="viewStats" class="tab-content" style="display:none;width:100%;">
        </section>
    </main>

    <!-- Modale Gestione Rose (Personale Unika & 7 Squadre Rivale) -->
    <div id="rosterModal" class="modal-backdrop" onclick="if(event.target === this) closeRosterModal()">
        <div class="modal-card" style="max-width:960px;width:95%;max-height:92vh;display:flex;flex-direction:column;background:rgba(18,24,38,0.97);backdrop-filter:blur(20px);border:1px solid rgba(0,242,254,0.3);padding:22px;border-radius:14px;box-shadow:0 14px 45px rgba(0,0,0,0.75);">
            <div id="rosterModalBody" style="overflow-y:auto;padding-right:4px;"></div>
        </div>
    </div>

    <!-- Modale Editor Tattico & Sostituti Ufficiali -->
    <div id="tacticalEditorModal" class="modal-backdrop" style="display:none;" onclick="if(event.target === this) closeTacticalEditorModal()">
        <div class="modal-card tactical-editor-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid var(--border-glass);padding-bottom:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:24px;">⚙️</span>
                    <div>
                        <h3 class="font-title" id="tacticalEditorTitle" style="color:var(--accent-cyan);font-size:18px;margin:0;">Editor Formazione & Sostituti Ufficiali</h3>
                        <div style="font-size:11.5px;color:var(--text-muted);margin-top:2px;">Configura modulo, 11 titolari, sostituti diretti e ricalcola le quotazioni del Listone</div>
                    </div>
                </div>
                <button class="btn-action" onclick="closeTacticalEditorModal()">Chiudi ✕</button>
            </div>
            <div id="tacticalEditorModalBody"></div>
        </div>
    </div>

    <!-- Modale Personalizzazione Calciatore (Slot, OOP, Consiglio AI) -->
    <div id="editPlayerModal" class="modal-backdrop">
        <div class="modal-card" style="max-width:540px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid var(--border-glass);padding-bottom:10px;">
                <h3 class="font-title" style="color:var(--accent-cyan);font-size:18px;margin:0;">⚙️ Personalizza Calciatore</h3>
                <button class="btn-action" onclick="closeEditPlayerModal()">Chiudi ✕</button>
            </div>
            <div id="editPlayerModalBody"></div>
        </div>
    </div>

    <!-- Modale Scheda Calciatore Dettagliata (Player Profile) -->
    <div id="playerDetailModal" class="modal-backdrop" onclick="if(event.target === this) closePlayerProfileModal()">
        <div class="modal-card player-profile-card">
            <button class="player-profile-close-btn" onclick="closePlayerProfileModal()" title="Chiudi Scheda" aria-label="Chiudi">✕</button>
            <div id="playerDetailModalBody"></div>
        </div>
    </div>

    <!-- Modal Acquisto Calciatore Live (Glassmorphism, No prompt nativo) -->
    <div id="buyPlayerModal" class="modal-backdrop" style="display:none;" onclick="if(event.target === this) closeBuyPlayerModal()">
        <div class="modal-card" style="max-width:440px;background:rgba(18,24,38,0.95);backdrop-filter:blur(16px);border:1px solid rgba(0,242,254,0.3);padding:24px;border-radius:14px;box-shadow:0 10px 40px rgba(0,0,0,0.6);">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:22px;">💰</span>
                    <h3 style="margin:0;font-size:17px;font-weight:900;color:#fff;">Acquista per la tua Rosa</h3>
                </div>
                <button class="btn-action" style="padding:3px 8px;font-size:12px;" onclick="closeBuyPlayerModal()">✕</button>
            </div>
            <div id="buyPlayerModalBody"></div>
        </div>
    </div>

    <!-- Modal Globale Assegna Calciatore a Squadra Rivale -->
    <div id="rivalAssignModal" class="modal-backdrop" style="display:none;" onclick="if(event.target === this) closeRivalAssignModal()">
        <div class="modal-card" style="max-width:580px;background:rgba(18,24,38,0.97);backdrop-filter:blur(20px);border:1px solid rgba(239,68,68,0.35);padding:22px;border-radius:14px;box-shadow:0 14px 45px rgba(0,0,0,0.7);">
            <div id="rivalAssignModalContent"></div>
        </div>
    </div>

    <!-- Modal Dettaglio Rosa Completa & Crediti (League Report Squad Modal) -->
    <div id="teamRosterModal" class="modal-backdrop" style="display:none;" onclick="if(event.target === this) closeTeamRosterModal()">
        <div class="modal-card team-roster-minimal-card" id="teamRosterModalCard">
            <div id="teamRosterModalContent"></div>
        </div>
    </div>

    <!-- Modal Opzioni Reset Asta Live -->
    <div id="resetAuctionModal" class="modal-backdrop" style="display:none;" onclick="if(event.target === this) closeResetAuctionModal()">
        <div class="modal-card" id="resetAuctionModalCard" style="max-width:540px;width:92%;background:rgba(18,22,34,0.98);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.12);padding:22px;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,0.85);">
            <div id="resetAuctionModalContent"></div>
        </div>
    </div>

    <!-- Modal Sostituzione Giocatore Formazioni Consigliate AI (Regola del Ruolo) -->
    <div id="aiSquadReplaceModal" class="modal-backdrop" style="display:none;" onclick="if(event.target === this) closeAiSquadReplaceModal()">
        <div class="modal-card ai-replace-modal-card">
            <div id="aiSquadReplaceModalContent"></div>
        </div>
    </div>

    <!-- Modal Sostituzione Giocatore Miglior 11 AI (Regola del Ruolo) -->
    <div id="best11PickerModal" class="modal-backdrop" style="display:none;z-index:100000;" onclick="if(event.target === this) closeBest11PickerModal()">
        <div class="modal-card ai-replace-modal-card" style="max-width:680px;">
            <div id="best11PickerModalContent"></div>
        </div>
    </div>

    <!-- Modal Caricamento Rosa CSV -->
    <div id="csvRosterImportModal" class="modal-backdrop" style="display:none;z-index:100000;" onclick="if(event.target === this) closeCsvRosterImportModal()">
        <div class="modal-card csv-import-card">
            <div id="csvRosterImportModalContent"></div>
        </div>
    </div>

    <!-- Modal Caricamento Lega Excel (.xlsx) -->
    <div id="xlsxImportModal" class="modal-backdrop" style="display:none;z-index:100000;" onclick="if(event.target === this) closeXlsxImportModal()">
        <div class="modal-card" style="max-width:860px;width:95%;max-height:92vh;display:flex;flex-direction:column;background:rgba(18,24,38,0.98);backdrop-filter:blur(24px);border:1px solid rgba(0,242,254,0.3);padding:22px;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,0.85);">
            <div id="xlsxImportModalContent" style="overflow-y:auto;padding-right:4px;"></div>
        </div>
    </div>

    <!-- Modal Creazione Nuova Lega -->
    <div id="createLeagueModal" class="modal-backdrop" style="display:none;z-index:100000;" onclick="if(event.target === this) closeCreateLeagueModal()">
        <div class="modal-card" style="max-width:560px;width:95%;background:rgba(18,24,38,0.98);backdrop-filter:blur(24px);border:1px solid rgba(0,242,254,0.3);padding:24px;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,0.85);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:24px;">🏆</span>
                    <h3 style="margin:0;font-size:18px;font-weight:900;color:#fff;">Crea Nuovo Campionato</h3>
                </div>
                <button class="btn-action" onclick="closeCreateLeagueModal()">✕</button>
            </div>
            <div id="createLeagueModalBody"></div>
        </div>
    </div>

    <!-- Modal Impostazioni Lega -->
    <div id="editLeagueModal" class="modal-backdrop" style="display:none;z-index:100000;" onclick="if(event.target === this) closeEditLeagueModal()">
        <div class="modal-card" style="max-width:560px;width:95%;background:rgba(18,24,38,0.98);backdrop-filter:blur(24px);border:1px solid rgba(0,242,254,0.3);padding:24px;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,0.85);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:24px;">⚙️</span>
                    <h3 style="margin:0;font-size:18px;font-weight:900;color:#fff;">Impostazioni Campionato</h3>
                </div>
                <button class="btn-action" onclick="closeEditLeagueModal()">✕</button>
            </div>
            <div id="editLeagueModalBody"></div>
        </div>
    </div>

    <!-- Modal Coming Soon / Funzionalità in Arrivo -->
    <div id="comingSoonModal" class="modal-backdrop" style="display:none;z-index:100050;" onclick="if(event.target === this) closeComingSoonModal()">
        <div class="modal-card" style="max-width:520px;width:92%;background:rgba(18,22,29,0.98);backdrop-filter:blur(24px);border:1px solid rgba(245,158,11,0.35);padding:28px 24px;border-radius:20px;box-shadow:0 25px 60px rgba(0,0,0,0.9);text-align:center;">
            <div style="width:64px;height:64px;margin:0 auto 16px;background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;">
                🔒
            </div>
            <div style="display:inline-block;padding:3px 10px;border-radius:20px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.35);color:#fbbf24;font-size:11px;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:12px;">
                Funzionalità In Arrivo
            </div>
            <h3 id="comingSoonTitle" style="margin:0 0 10px;font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.3px;">
                Asta & Gestione Leghe
            </h3>
            <p id="comingSoonDesc" style="margin:0 0 20px;font-size:13.5px;line-height:1.55;color:var(--text-secondary);">
                Le aste estive 2026/27 sono concluse! Il modulo di Asta Live e Gestione Leghe è temporaneamente bloccato e tornerà attivo per l'asta di riparazione di gennaio.<br><br>
                Nel frattempo, consulta le <strong>statistiche avanzate Serie A, gli indici xG/xA e i consigli AI</strong> per vincere ogni giornata!
            </p>
            <div style="display:flex;flex-direction:column;gap:10px;">
                <button class="btn-action" onclick="closeComingSoonModal(); switchTab('stats');" style="width:100%;padding:12px;background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);color:#0c0e12;font-weight:900;font-size:14px;border:none;border-radius:10px;cursor:pointer;box-shadow:0 4px 14px rgba(245,158,11,0.35);transition:all 0.2s ease;">
                    📊 Vai alle Statistiche Serie A
                </button>
                <button class="btn-action" onclick="closeComingSoonModal(); switchTab('matchday_advice');" style="width:100%;padding:11px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#e2e8f0;font-weight:700;font-size:13px;border-radius:10px;cursor:pointer;">
                    🎯 Consulta Consigli di Giornata AI
                </button>
                <button class="btn-action" onclick="closeComingSoonModal()" style="width:100%;padding:9px;background:transparent;border:none;color:var(--text-muted);font-weight:600;font-size:12.5px;cursor:pointer;">
                    Chiudi
                </button>
            </div>
        </div>
    </div>

    <!-- MOBILE BOTTOM NAVIGATION (Native App Bar: Probabili | Chi Schiero | Consigli AI | La Tua Rosa | Menu) -->
    <nav class="mobile-bottom-nav" id="mobileBottomNav">
        <a href="/probabili-formazioni/" class="mobile-nav-item" id="mobNavProbabili">
            <span class="mob-icon">⚽</span>
            <span class="mob-label">Probabili</span>
        </a>
        <a href="/chi-schiero/" class="mobile-nav-item" id="mobNavChiSchiero" onclick="switchTabMobile('chi_schiero', event)">
            <span class="mob-icon">⚔️</span>
            <span class="mob-label">Chi Schiero</span>
        </a>
        <a href="/consigli-fantacalcio/" class="mobile-nav-item" id="mobNavAdvice" onclick="switchTabMobile('matchday_advice', event)">
            <span class="mob-icon">🎯</span>
            <span class="mob-label">Consigli AI</span>
        </a>
        <button type="button" class="mobile-nav-item" id="mobNavSquad" onclick="openMySquadModal()">
            <span class="mob-icon">📋</span>
            <span class="mob-label">La Tua Rosa</span>
        </button>
        <button type="button" class="mobile-nav-item" id="mobNavMenu" onclick="openMobileMenuModal()" aria-label="Apri menu completo">
            <span class="mob-icon">☰</span>
            <span class="mob-label">Menu</span>
        </button>
    </nav>

    <!-- Mobile Drawer Backdrop -->
    <div id="mobileDrawerBackdrop" class="mobile-drawer-backdrop" onclick="toggleMobileRosterDrawer(false)"></div>

    <!-- Mobile Menu Modal (Diviso nelle 2 Fasi del Fantacalcio) -->
    <div id="mobileMenuModal" class="modal-backdrop" style="display:none;z-index:100002;" onclick="if(event.target === this) closeMobileMenuModal()">
        <div class="modal-card" style="max-width:540px;background:rgba(18,22,29,0.98);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.1);padding:20px;border-radius:18px;box-shadow:0 25px 60px rgba(0,0,0,0.9);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">🏆</span>
                    <h3 style="margin:0;font-size:17px;font-weight:900;color:#fff;">Navigazione: Le 2 Fasi del Fantacalcio</h3>
                </div>
                <button class="btn-action" onclick="closeMobileMenuModal()">✕</button>
            </div>
            
            <div class="mobile-menu-grid">
                <!-- Section 0: HOME PAGE -->
                <div class="mobile-menu-section" style="padding:0;">
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('home')" style="background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.16);color:#fff;font-weight:900;">🏠 Torna alla Home Page</button>
                    </div>
                </div>

                <!-- Section 1: FASE 1 - GIORNATA & FORMAZIONE -->
                <div class="mobile-menu-section" style="border:1px solid rgba(16,185,129,0.28);background:rgba(16,185,129,0.05);border-radius:12px;padding:12px;">
                    <div class="mobile-menu-section-title" style="color:#34d399;font-weight:900;"><span>⚽</span> FASE 1: GIORNATA &amp; FORMAZIONE (11 Titolari)</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="closeMobileMenuModal(); openMySquadModal();" style="background:rgba(16,185,129,0.18);border-color:rgba(16,185,129,0.45);color:#34d399;font-weight:800;">📋 La Mia Rosa &amp; Miglior 11 AI</button>
                        <a href="/probabili-formazioni/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(56,189,248,0.15);border-color:rgba(56,189,248,0.4);color:#38bdf8;font-weight:800;">⚽ Probabili Formazioni &amp; Ballottaggi (4 Fonti)</a>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('chi_schiero')" style="background:rgba(168,85,247,0.15);border-color:rgba(168,85,247,0.4);color:#e9d5ff;font-weight:800;">⚔️ Tool &ldquo;Chi Schiero?&rdquo; (Dubbio 1vs1)</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('matchday_advice')">🎯 Consigliati di Giornata &amp; Top 11</button>
                        <a href="/infortunati-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;color:#fca5a5;">🩺 Infortunati, Squalificati &amp; Rientri</a>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('stats')">📊 Statistiche Serie A (xG, xA, xFM)</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('top_flop')">⚡ Top &amp; Flop di Giornata</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('match_reports')">📑 Match Reports &amp; Voti Ufficiali</button>
                    </div>
                </div>

                <!-- Section 2: FASE 2 - MERCATO & ASTA -->
                <div class="mobile-menu-section" style="border:1px solid rgba(245,158,11,0.28);background:rgba(245,158,11,0.05);border-radius:12px;padding:12px;">
                    <div class="mobile-menu-section-title" style="color:#fbbf24;font-weight:900;"><span>💰</span> FASE 2: MERCATO &amp; ASTA (Estate &amp; Riparazione)</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('auction')" style="background:rgba(245,158,11,0.16);border-color:rgba(245,158,11,0.4);color:#fde68a;font-weight:800;">📋 Listone Calciatori &amp; Quotazioni FVM</button>
                        <a href="/probabili-formazioni/como/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;color:#fcd34d;font-weight:700;">🏟️ Top 11 &amp; Gerarchie Stagionali (20 Squadre)</a>
                        <a href="/griglia-portieri/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🧤 Griglia Portieri &amp; Accoppiamenti 38/38</a>
                        <a href="/rigoristi-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🎯 Rigoristi, Punizioni &amp; Calci Piazzati</a>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('gems')">🔮 Gemme Nascoste &amp; Scommesse Low-Cost</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('matchup')">⚖️ Confronto Calciatori (Scambi &amp; Asta)</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('ai_squads')">🤖 5 Squadre Perfette AI (Budget)</button>
                    </div>
                </div>

                <!-- Section 3: Home & Strumenti -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>⚙️</span> Home &amp; Metodologia</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('home')">🏠 Torna alla Home Page</button>
                        <button class="mobile-menu-link-btn" onclick="closeMobileMenuModal(); openAiMethodologyModal('ovr');">ℹ️ Come Funziona l'Algoritmo AI</button>
                        <button class="mobile-menu-link-btn" onclick="closeMobileMenuModal(); openCreatorAuthModal();" style="color:#fbbf24;">👑 Accesso Creatore</button>
                    </div>
                </div>

                <!-- Section 4: Community & Social Ufficiali -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🌐</span> Community &amp; Social Ufficiali</div>
                    <div class="mobile-menu-links">
                        <a href="https://t.me/fantamasterai" target="_blank" rel="noopener noreferrer" class="mobile-menu-link-btn" style="color:#38bdf8;font-weight:700;text-decoration:none;display:flex;align-items:center;gap:10px;">
                            <span>✈️</span> Canale Telegram Ufficiale (@fantamasterai)
                        </a>
                        <a href="https://www.instagram.com/fantamasterai" target="_blank" rel="noopener noreferrer" class="mobile-menu-link-btn" style="color:#f43f5e;font-weight:700;text-decoration:none;display:flex;align-items:center;gap:10px;">
                            <span>📸</span> Instagram Ufficiale (@fantamasterai)
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- CREATOR AUTH MODAL (Sicuro, Input Password Mascherato, SHA-256) -->
    <div id="creatorAuthModal" class="modal-backdrop" style="display:none;z-index:100005;" onclick="if(event.target === this) closeCreatorAuthModal()">
        <div class="modal-card" style="max-width:380px;background:rgba(18,22,29,0.98);backdrop-filter:blur(24px);border:1px solid rgba(245,158,11,0.35);padding:26px 22px;border-radius:18px;box-shadow:0 25px 60px rgba(0,0,0,0.9);text-align:center;">
            <div style="font-size:34px;margin-bottom:12px;">👑</div>
            <h3 style="margin:0 0 6px 0;font-size:18px;font-weight:900;color:#fff;">Accesso Riservato Creatore</h3>
            <p style="font-size:12px;color:var(--text-secondary);margin:0 0 20px 0;line-height:1.4;">Autenticati per sbloccare la modifica formazioni, auto-fill e gestione campionati.</p>
            <input type="password" id="creatorPasswordInput" class="clean-input-search" placeholder="••••••••" autocomplete="off" style="width:100%;text-align:center;font-size:16px;letter-spacing:3px;padding:11px 14px;border-radius:10px;background:rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.18);color:#fff;margin-bottom:12px;" onkeydown="if(event.key==='Enter') submitCreatorAuth()">
            <div id="creatorAuthError" style="display:none;color:#f87171;font-size:12px;margin-bottom:14px;font-weight:700;">❌ Password non corretta</div>
            <div style="display:flex;gap:10px;justify-content:center;">
                <button class="btn-clean-action" onclick="closeCreatorAuthModal()" style="flex:1;padding:9px 14px;border-radius:8px;">Annulla</button>
                <button class="btn-action" onclick="submitCreatorAuth()" style="flex:1;padding:9px 14px;background:linear-gradient(135deg,rgba(245,158,11,0.35),rgba(217,119,6,0.55));border:1px solid #fbbf24;color:#fbbf24;font-weight:800;border-radius:8px;">Sblocca</button>
            </div>
        </div>
    </div>

    <!-- Data Injection & Engine Scripts -->
    <script>
        const PLAYERS = {players_json};
        const GK_DATA = {gk_json};
        const TACTICAL_DB = {tactical_json};
        const TEAM_STATS_DB = {team_stats_json};
        const TEAM_RATINGS_DB = {team_ratings_json};
        const TOP_FLOP_DATA = {top_flop_json};
        const OFFICIAL_CALENDAR_2026_27 = {cal_json};
        const MATCHDAY_ACCURACY_DATA = {accuracy_json};
        const MATCH_REPORTS_DATA = {match_reports_json};
        // === END_DATASET_INJECTION ===

{js_content}

        // Coming Soon Modal Handlers
        function showComingSoonModal(featureName) {{
            const modal = document.getElementById('comingSoonModal');
            const titleEl = document.getElementById('comingSoonTitle');
            if (titleEl && featureName) {{
                titleEl.textContent = featureName + ' — In Arrivo';
            }}
            if (modal) modal.style.display = 'flex';
        }}

        function closeComingSoonModal() {{
            const modal = document.getElementById('comingSoonModal');
            if (modal) modal.style.display = 'none';
        }}

        // --- CLEAN URL ROUTING & NAVIGATION ---
        const ROUTE_MAP = {{
            'home': '/',
            'auction': '/listone/',
            'top_flop': '/top-flop/',
            'match_reports': '/match-report/',
            'matchday_advice': '/consigli-fantacalcio/',
            'chi_schiero': '/chi-schiero/',
            'matrix': '/football-analytics/',
            'stats': '/statistiche-serie-a/',
            'pitch': '/probabili-formazioni/',
            'matchup': '/confronto-calciatori/',
            'gk': '/griglia-portieri/',
            'ai_squads': '/top-11-ai/',
            'gems': '/scommesse-talenti/',
            'leagues': '/leghe/'
        }};

        const PATH_TO_TAB = {{
            '/': 'home',
            '/index.html': 'home',
            '/app.html': 'home',
            '/home': 'home',
            '/home/': 'home',
            '/probabili-formazioni': 'pitch',
            '/probabili-formazioni/': 'pitch',
            '/probabili-formazioni/index.html': 'pitch',
            '/listone': 'auction',
            '/listone/': 'auction',
            '/listone/index.html': 'auction',
            '/leghe': 'leagues',
            '/leghe/': 'leagues',
            '/top-flop': 'top_flop',
            '/top-flop/': 'top_flop',
            '/top-flop/index.html': 'top_flop',
            '/match-report': 'match_reports',
            '/match-report/': 'match_reports',
            '/match-report/index.html': 'match_reports',
            '/match-reports': 'match_reports',
            '/match-reports/': 'match_reports',
            '/match-reports/index.html': 'match_reports',
            '/consigli-fantacalcio': 'matchday_advice',
            '/consigli-fantacalcio/': 'matchday_advice',
            '/consigli-fantacalcio/index.html': 'matchday_advice',
            '/chi-schiero': 'chi_schiero',
            '/chi-schiero/': 'chi_schiero',
            '/chi-schiero/index.html': 'chi_schiero',
            '/football-analytics': 'matrix',
            '/football-analytics/': 'matrix',
            '/football-analytics/index.html': 'matrix',
            '/statistiche-serie-a': 'stats',
            '/statistiche-serie-a/': 'stats',
            '/statistiche-serie-a/index.html': 'stats',
            '/confronto-calciatori': 'matchup',
            '/confronto-calciatori/': 'matchup',
            '/confronto-calciatori/index.html': 'matchup',
            '/griglia-portieri': 'gk',
            '/griglia-portieri/': 'gk',
            '/griglia-portieri/index.html': 'gk',
            '/top-11-ai': 'ai_squads',
            '/top-11-ai/': 'ai_squads',
            '/top-11-ai/index.html': 'ai_squads',
            '/scommesse-talenti': 'gems',
            '/scommesse-talenti/': 'gems',
            '/scommesse-talenti/index.html': 'gems',
            // Direct identifiers & legacy hashes
            'pitch': 'pitch',
            'top_flop': 'top_flop',
            'match_reports': 'match_reports',
            'matchday_advice': 'matchday_advice',
            'chi_schiero': 'chi_schiero',
            'matrix': 'matrix',
            'stats': 'stats',
            'matchup': 'matchup',
            'gk': 'gk',
            'ai_squads': 'ai_squads',
            'gems': 'gems',
            'auction': 'auction',
            'leagues': 'leagues',
            'home': 'home'
        }};

        function onNavClick(e, tabId) {{
            if (e && e.preventDefault) e.preventDefault();
            switchTab(tabId, true);
        }}

        // Intercetta tutti i click su link assoluti quando il file è aperto localmente (file://)
        document.addEventListener('click', function(e) {{
            if (window.location.protocol !== 'file:') return;
            const a = e.target.closest('a');
            if (!a) return;
            const href = a.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('http://') || href.startsWith('https://')) return;
            
            if (href.startsWith('/')) {{
                // 1. Pagine dedicate e strutturate del portale (Probabili Formazioni, Infortunati, Rigoristi, Griglia Portieri, Privacy)
                if (href.startsWith('/probabili-formazioni') || href.startsWith('/infortunati-serie-a') || href.startsWith('/rigoristi-serie-a') || href.startsWith('/griglia-portieri') || href.startsWith('/privacy-policy')) {{
                    e.preventDefault();
                    const cleanPath = href.replace(/\/index\.html$/, '');
                    const rel = './dist' + (cleanPath.endsWith('/') ? cleanPath : cleanPath + '/') + 'index.html';
                    window.location.href = rel;
                    return;
                }}
                // 2. Moduli interni della Dashboard gestiti come Tab SPA
                const clean = href.replace(/[/]+$/, '') || '/';
                const tab = PATH_TO_TAB[clean] || PATH_TO_TAB[clean + '/'] || PATH_TO_TAB[href];
                if (tab && tab !== 'pitch') {{
                    e.preventDefault();
                    switchTab(tab, true);
                    return;
                }}
            }}
        }});

        // Router & UI Handlers
        function switchTabMobile(tabId, event) {{
            if (event && event.preventDefault) event.preventDefault();
            closeMobileMenuModal();
            toggleMobileRosterDrawer(false);
            switchTab(tabId, true);
        }}

        function toggleMobileRosterDrawer(forceState) {{
            const sidebar = document.getElementById('rosterSidebar');
            const backdrop = document.getElementById('mobileDrawerBackdrop');
            if (!sidebar) return;

            const shouldOpen = (typeof forceState === 'boolean') ? forceState : !sidebar.classList.contains('mobile-drawer-open');
            sidebar.classList.toggle('mobile-drawer-open', shouldOpen);
            if (backdrop) backdrop.style.display = shouldOpen ? 'block' : 'none';

            const btn = document.getElementById('mobNavRoster');
            if (btn) btn.classList.toggle('active', shouldOpen);
        }}

        function openMobileMenuModal() {{
            const modal = document.getElementById('mobileMenuModal');
            if (modal) modal.style.display = 'flex';
        }}

        function closeMobileMenuModal() {{
            const modal = document.getElementById('mobileMenuModal');
            if (modal) modal.style.display = 'none';
        }}

        function switchTab(tabId, pushHistory = true) {{
            // Intercept locked tabs for auction/league management (Creazione Squadra & Gestione Leghe)
            const LOCKED_TABS = ['leagues', 'squad_builder', 'repair', 'trade', 'report'];
            if (LOCKED_TABS.includes(tabId)) {{
                if (typeof isCreatorModeActive === 'function' && isCreatorModeActive()) {{
                    // Accesso consentito per il Creatore!
                }} else {{
                    const tabNames = {{
                        'leagues': 'Hub Gestione Leghe Private',
                        'squad_builder': 'Creazione Squadra & 11',
                        'repair': 'Asta di Riparazione & Svincoli',
                        'trade': 'Scambi & Trade Machine',
                        'report': 'Pagelle Lega & AI Roast'
                    }};
                    showComingSoonModal(tabNames[tabId] || 'Modulo Asta');
                    return;
                }}
            }}

            // Fallback for standalone pages where SPA views are not in DOM
            if (!document.getElementById('viewHome')) {{
                const targetUrl = ROUTE_MAP[tabId] || '/';
                window.location.href = targetUrl;
                return;
            }}

            State.activeTab = tabId;

            // Aggiorna titolo pulito della pagina nell'header (senza trofei, senza cornici)
            const TAB_TITLES = {{
                'home': 'Home — Statistiche Serie A',
                'auction': 'Listone Calciatori',
                'stats': 'Statistiche & xG',
                'top_flop': 'Top & Flop',
                'match_reports': 'Match Reports — Analisi Partite',
                'matrix': 'Matrice Analytics',
                'pitch': 'Top 11 & Gerarchie 20 Squadre',
                'matchup': 'Matchup 1vs1',
                'gk': 'Griglia Portieri',
                'matchday_advice': 'Consigli Formazione',
                'chi_schiero': 'Chi Schiero? 1vs1',
                'ai_squads': '5 Squadre Perfette AI',
                'gems': 'Gemme & Scommesse',
                'leagues': 'Hub Leghe'
            }};
            const hdrTitle = document.getElementById('headerPageTitle');
            if (hdrTitle) {{
                hdrTitle.textContent = TAB_TITLES[tabId] || 'Statistiche Serie A';
            }}
            try {{
                const isFile = window.location.protocol === 'file:';
                const targetPath = ROUTE_MAP[tabId] || '/';
                if (!isFile) {{
                    const cur = (window.location.pathname.replace(/[/]+$/, '') || '/');
                    const tgt = (targetPath.replace(/[/]+$/, '') || '/');
                    if (cur !== tgt || window.location.hash) {{
                        if (pushHistory) {{
                            history.pushState({{ tab: tabId }}, '', targetPath);
                        }} else {{
                            history.replaceState({{ tab: tabId }}, '', targetPath);
                        }}
                    }}
                }} else {{
                    if (window.location.hash !== '#' + tabId) {{
                        history.replaceState(null, null, '#' + tabId);
                    }}
                }}
            }} catch (e) {{}}

            // Tracciamento virtual pageview per Google Analytics 4
            try {{
                if (typeof gtag === 'function') {{
                    gtag('event', 'page_view', {{
                        page_path: ROUTE_MAP[tabId] || window.location.pathname,
                        page_title: TAB_TITLES[tabId] || document.title
                    }});
                }}
            }} catch (e) {{}}

            ['tabHomeNavBtn', 'tabProbabiliNavBtn', 'tabChiSchieroDirectBtn', 'tabLeaguesBtn', 'tabHomeBtn', 'tabAuctionBtn', 'tabAiSquadsBtn', 'tabMatchdayAdviceBtn', 'tabChiSchieroBtn', 'tabSquadBuilderBtn', 'tabTopFlopBtn', 'tabMatchReportsBtn', 'tabMatrixBtn', 'tabStatsBtn', 'tabPitchBtn', 'tabMatchupBtn', 'tabGkBtn', 'tabGemsBtn', 'tabTradeBtn', 'tabRepairBtn', 'tabReportBtn'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            // Reset mobile bottom nav active tabs
            ['mobNavHome', 'mobNavStats', 'mobNavAuction', 'mobNavAdvice', 'mobNavChiSchiero', 'mobNavPitch', 'mobNavProbabili'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            // Reset dropdown group buttons
            ['navGroupAuction', 'navGroupTactics', 'navGroupAi'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            ['viewHome', 'viewHomeHub', 'viewAuction', 'viewMatchdayAdvice', 'viewChiSchiero', 'viewAiSquads', 'viewSquadBuilder', 'viewTopFlop', 'viewMatchReports', 'viewMatrix', 'viewStats', 'viewPitch', 'viewMatchup', 'viewGk', 'viewGems', 'viewTradeMachine', 'viewRepairAuction', 'viewLeagueReport'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) {{
                    el.style.display = 'none';
                    el.classList.remove('active');
                }}
            }});

            // Budget bar is only for live auctions (hidden in statistical consultation mode)
            const budgetBar = document.querySelector('.budget-bar-wrapper');
            if (budgetBar) budgetBar.style.display = 'none';

            if (tabId === 'home') {{
                const btn = document.getElementById('tabHomeNavBtn');
                if (btn) btn.classList.add('active');
                const mob = document.getElementById('mobNavHome');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewHome');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'flex';
                }}
                if (typeof renderHomeLeaders === 'function') renderHomeLeaders();
                if (typeof renderLiveIntelligencePulseCards === 'function') renderLiveIntelligencePulseCards();
            }} else if (tabId === 'leagues') {{
                const btn = document.getElementById('tabLeaguesBtn') || document.getElementById('tabHomeBtn');
                if (btn) btn.classList.add('active');
                const view = document.getElementById('viewHomeHub');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderHomeHubView === 'function') renderHomeHubView();
            }} else if (tabId === 'auction') {{
                const btn = document.getElementById('tabAuctionBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavAuction');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewAuction');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'flex';
                }}
                if (typeof renderTable === 'function') renderTable();
            }} else if (tabId === 'stats') {{
                const btn = document.getElementById('tabStatsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavStats');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewStats');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderStatsSerieAView === 'function') renderStatsSerieAView();
            }} else if (tabId === 'matchday_advice') {{
                const btn = document.getElementById('tabMatchdayAdviceBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavAdvice');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewMatchdayAdvice');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderMatchdayAdviceView === 'function') renderMatchdayAdviceView();
            }} else if (tabId === 'chi_schiero') {{
                const btnDirect = document.getElementById('tabChiSchieroDirectBtn');
                if (btnDirect) btnDirect.classList.add('active');
                const btn = document.getElementById('tabChiSchieroBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavChiSchiero');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewChiSchiero');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderChiSchieroView === 'function') renderChiSchieroView();
            }} else if (tabId === 'top_flop') {{
                const btn = document.getElementById('tabTopFlopBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const view = document.getElementById('viewTopFlop');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderTopFlopView === 'function') renderTopFlopView();
            }} else if (tabId === 'match_reports') {{
                const btn = document.getElementById('tabMatchReportsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const view = document.getElementById('viewMatchReports');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderMatchReportsView === 'function') renderMatchReportsView();
            }} else if (tabId === 'matrix') {{
                const btn = document.getElementById('tabMatrixBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const view = document.getElementById('viewMatrix');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                if (typeof renderAnalyticsMatrixView === 'function') renderAnalyticsMatrixView();
            }} else if (tabId === 'pitch') {{
                const btnNav = document.getElementById('tabProbabiliNavBtn');
                if (btnNav) btnNav.classList.add('active');
                const btn = document.getElementById('tabPitchBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavPitch') || document.getElementById('mobNavProbabili');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewPitch');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                const currentClub = State.currentTeamPitch || 'Inter';
                const sel = document.getElementById('selectPitchTeam');
                if (sel) sel.value = currentClub;
                renderPitchTeam(currentClub);
            }} else if (tabId === 'matchup') {{
                const btn = document.getElementById('tabMatchupBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                const view = document.getElementById('viewMatchup');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'flex';
                }}
                updateMatchup();
            }} else if (tabId === 'gk') {{
                const btn = document.getElementById('tabGkBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavGk');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewGk');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'flex';
                }}
                renderGkGrid();
            }} else if (tabId === 'ai_squads') {{
                const btn = document.getElementById('tabAiSquadsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                const view = document.getElementById('viewAiSquads');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'flex';
                }}
                renderAiSquadsTab();
            }} else if (tabId === 'gems') {{
                const btn = document.getElementById('tabGemsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                const view = document.getElementById('viewGems');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'block';
                }}
                renderGemsTab();
            }} else {{
                // Fallback sicuro se il tab non corrisponde a nessun id
                const btn = document.getElementById('tabHomeNavBtn');
                if (btn) btn.classList.add('active');
                const mob = document.getElementById('mobNavHome');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewHome');
                if (view) {{
                    view.classList.add('active');
                    view.style.display = 'flex';
                }}
            }}
        }}

        function onSearchChange(val) {{
            State.searchQuery = val;
            renderTable();
        }}
        function onSearchInput(val) {{
            State.searchQuery = val;
            renderTable();
        }}
        function onFilterRoleChange(val) {{
            State.filterRole = val;
            if (typeof updateMantraQuickBarActiveState === 'function') {{
                updateMantraQuickBarActiveState();
            }}
            renderTable();
        }}
        function onFilterTeamChange(val) {{
            State.filterTeam = val;
            renderTable();
        }}
        function onFilterSlotChange(val) {{
            State.filterSlot = val;
            renderTable();
        }}
        function onFilterAdviceChange(val) {{
            State.filterAdvice = val;
            renderTable();
        }}
        function onFilterRigoristiChange(val) {{
            State.filterRigoristi = val;
            renderTable();
        }}
        function onFilterTitolaritaChange(val) {{
            State.filterTitolarita = val;
            renderTable();
        }}
        function onFilterPriceRangeChange(val) {{
            State.filterPriceRange = val;
            renderTable();
        }}
        function onToggleOop(checked) {{
            State.filterOop = checked;
            renderTable();
        }}
        function onToggleInjured(checked) {{
            State.filterInjured = checked;
            renderTable();
        }}
        function onToggleHealthy(checked) {{
            State.filterHealthy = checked;
            renderTable();
        }}
        function onToggleOnlyAvailable(checked) {{
            State.filterOnlyAvailable = checked;
            renderTable();
        }}
        function onToggleOnlyFavorites(checked) {{
            State.filterOnlyFavorites = checked;
            renderTable();
        }}
        function resetAllFilters() {{
            State.searchQuery = '';
            State.filterRole = 'ALL';
            State.filterTeam = 'ALL';
            State.filterSlot = 'ALL';
            State.filterAdvice = 'ALL';
            State.filterFragilita = 'ALL';
            State.filterRigoristi = 'ALL';
            State.filterTitolarita = 'ALL';
            State.filterPriceRange = 'ALL';
            State.filterOop = false;
            State.filterHot = false;
            State.filterRigid = false;
            State.filterInjured = false;
            State.filterHealthy = false;
            State.filterOnlyAvailable = false;
            State.filterOnlyFavorites = false;

            const sb = document.getElementById('searchBox'); if (sb) sb.value = '';
            const fr = document.getElementById('filterRole'); if (fr) fr.value = 'ALL';
            const ft = document.getElementById('filterTeam'); if (ft) ft.value = 'ALL';
            const fs = document.getElementById('filterSlot'); if (fs) fs.value = 'ALL';
            const fa = document.getElementById('filterAdvice'); if (fa) fa.value = 'ALL';
            const ff = document.getElementById('filterFragilita'); if (ff) ff.value = 'ALL';
            const frig = document.getElementById('filterRigoristi'); if (frig) frig.value = 'ALL';
            const ftit = document.getElementById('filterTitolarita'); if (ftit) ftit.value = 'ALL';
            const fpr = document.getElementById('filterPriceRange'); if (fpr) fpr.value = 'ALL';

            const bFav = document.getElementById('btnToggleFav'); if (bFav) bFav.classList.remove('active');
            const bAvail = document.getElementById('btnToggleAvail'); if (bAvail) bAvail.classList.remove('active');
            const bOop = document.getElementById('btnToggleOop'); if (bOop) bOop.classList.remove('active');
            const bHot = document.getElementById('btnToggleHot'); if (bHot) bHot.classList.remove('active');
            const bRig = document.getElementById('btnToggleRig'); if (bRig) bRig.classList.remove('active');

            const cFav = document.getElementById('chkOnlyFavorites'); if (cFav) cFav.checked = false;
            const cAvail = document.getElementById('chkOnlyAvailable'); if (cAvail) cAvail.checked = false;
            const cOop = document.getElementById('chkOop'); if (cOop) cOop.checked = false;
            const cInj = document.getElementById('chkInj'); if (cInj) cInj.checked = false;
            const cHlt = document.getElementById('chkHealthy'); if (cHlt) cHlt.checked = false;

            if (typeof updateMantraQuickBarActiveState === 'function') {{
                updateMantraQuickBarActiveState();
            }}
            renderTable();
        }}

        function setSort(field) {{
            if (field === 'delta_xfm_desc') {{
                State.sortBy = 'delta_xfm';
                State.sortAsc = false;
            }} else if (field === 'delta_xfm') {{
                State.sortBy = 'delta_xfm';
                State.sortAsc = true;
            }} else if (State.sortBy === field) {{
                State.sortAsc = !State.sortAsc;
            }} else {{
                State.sortBy = field;
                State.sortAsc = (field === 'role' || field === 'name' || field === 'team' || field === 'slot_num');
            }}
            renderTable();
        }}

        // Inizializzazione Applicazione
        function initApp() {{
            loadStateFromStorage();
            if (typeof renderHeaderLeagueDropdown === 'function') {{
                renderHeaderLeagueDropdown();
            }}
            if (typeof setSystemMode === 'function') {{
                setSystemMode(State.systemMode || 'classic', false);
            }}
            if (typeof initAuctionTableView === 'function') {{
                initAuctionTableView();
            }}

            // Popola selettore squadre
            const selTeam = document.getElementById('filterTeam');
            const selPitchTeam = document.getElementById('selectPitchTeam');
            const teams = Object.keys(TACTICAL_DB).sort();
            
            teams.forEach(tm => {{
                if (selTeam) {{
                    const opt = document.createElement('option');
                    opt.value = tm;
                    opt.textContent = tm;
                    selTeam.appendChild(opt);
                }}
                if (selPitchTeam) {{
                    const opt2 = document.createElement('option');
                    opt2.value = tm;
                    opt2.textContent = tm;
                    selPitchTeam.appendChild(opt2);
                }}
            }});

            State.matchupA = PLAYERS[0] || null;
            State.matchupB = PLAYERS[1] || null;
            initMatchupSelects();

            updateBudgetUI();

            function resolveCurrentTab() {{
                if (window.INITIAL_TAB && PATH_TO_TAB[window.INITIAL_TAB]) {{
                    return PATH_TO_TAB[window.INITIAL_TAB];
                }}
                const cur = (window.location.pathname.replace(/[/]+$/, '') || '/');
                if (PATH_TO_TAB[cur]) {{
                    return PATH_TO_TAB[cur];
                }}
                const h = window.location.hash ? window.location.hash.replace('#', '') : null;
                if (h && PATH_TO_TAB[h]) {{
                    return PATH_TO_TAB[h];
                }}
                const saved = localStorage.getItem('FANTA_LAST_ACTIVE_TAB');
                if (saved && PATH_TO_TAB[saved]) {{
                    return PATH_TO_TAB[saved];
                }}
                return 'home';
            }}

            const initialTab = resolveCurrentTab();
            switchTab(initialTab || 'home', false);
            const initialPitchTeam = (typeof getInitialPitchClub === 'function') 
                ? getInitialPitchClub() 
                : (window.INITIAL_PITCH_TEAM || 'Inter');
            renderPitchTeam(initialPitchTeam, false);

            // Apertura automatica de "La Tua Rosa" se richiesto da query string (?openSquad=1) o hash (#my_squad)
            try {{
                if ((window.location.search && window.location.search.indexOf('openSquad=1') !== -1) || window.location.hash === '#my_squad') {{
                    setTimeout(function() {{
                        if (typeof openMySquadModal === 'function') openMySquadModal();
                    }}, 120);
                }}
            }} catch (e) {{}}

            // Registrazione Service Worker per Progressive Web App (PWA)
            if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {{
                navigator.serviceWorker.register('/static/sw.js')
                    .then(() => console.log('✓ Service Worker Fanta Master AI registrato'))
                    .catch(e => console.warn('SW registration fallback:', e));
            }}
        }}

        if (document.readyState === 'loading') {{
            window.addEventListener('DOMContentLoaded', initApp);
        }} else {{
            initApp();
        }}

        // Gestione Installazione PWA (Prompt Dinamico)
        let _deferredPwaPrompt = null;
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            _deferredPwaPrompt = e;
            const pwaBtn = document.getElementById('btnPwaInstall');
            if (pwaBtn) pwaBtn.style.display = 'inline-flex';
        }});

        window.addEventListener('appinstalled', () => {{
            console.log('✓ Fanta Master AI installata con successo come Web App');
            const pwaBtn = document.getElementById('btnPwaInstall');
            if (pwaBtn) pwaBtn.style.display = 'none';
        }});

        function triggerPwaInstall() {{
            if (_deferredPwaPrompt) {{
                _deferredPwaPrompt.prompt();
                _deferredPwaPrompt.userChoice.then((choice) => {{
                    if (choice.outcome === 'accepted') {{
                        console.log('Utente ha accettato l\\'installazione PWA');
                    }}
                    _deferredPwaPrompt = null;
                    const pwaBtn = document.getElementById('btnPwaInstall');
                    if (pwaBtn) pwaBtn.style.display = 'none';
                }});
            }} else {{
                alert("Per installare l'app:\\n- Su iPhone/iPad: tocca 'Condividi' e poi 'Aggiungi alla schermata Home'\\n- Su Android/Chrome: tocca i 3 puntini in alto a destra e seleziona 'Aggiungi a schermata Home'");
            }}
        }}

        window.addEventListener('popstate', (e) => {{
            const cur = (window.location.pathname.replace(/[/]+$/, '') || '/');
            const tab = (e.state && e.state.tab) || (PATH_TO_TAB[cur] || 'auction');
            if (tab && tab !== State.activeTab) {{
                switchTab(tab, false);
            }}
        }});

        window.addEventListener('hashchange', () => {{
            const hTab = window.location.hash ? window.location.hash.replace('#', '') : null;
            if (hTab && PATH_TO_TAB[hTab] && PATH_TO_TAB[hTab] !== State.activeTab) {{
                switchTab(PATH_TO_TAB[hTab], true);
            }}
        }});

        // Export navigation functions to window for global availability
        window.switchTabMobile = switchTabMobile;
        window.openMobileMenuModal = openMobileMenuModal;
        window.closeMobileMenuModal = closeMobileMenuModal;
        window.switchTab = switchTab;
    </script>

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
                    <div class="footer-social-row" style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
                        <a href="https://t.me/fantamasterai" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:6px;background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.25);color:#38bdf8;padding:4px 10px;border-radius:20px;font-size:11.5px;font-weight:700;text-decoration:none;">
                            <span>✈️</span> Telegram
                        </a>
                        <a href="https://www.instagram.com/fantamasterai" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:6px;background:rgba(244,63,94,0.1);border:1px solid rgba(244,63,94,0.25);color:#fb7185;padding:4px 10px;border-radius:20px;font-size:11.5px;font-weight:700;text-decoration:none;">
                            <span>📸</span> Instagram
                        </a>
                    </div>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Navigazione Portale</div>
                    <ul class="footer-nav-list">
                        <li><a href="/" class="footer-link" onclick="onNavClick(event, 'home')">🏟️ Formazione &amp; Asta AI</a></li>
                        <li><a href="/consigli-fantacalcio/" class="footer-link" onclick="onNavClick(event, 'matchday_advice')">🎯 Consigli di Giornata</a></li>
                        <li><a href="/probabili-formazioni/" class="footer-link" onclick="onNavClick(event, 'pitch')">⚽ Probabili Formazioni 2D</a></li>
                        <li><a href="/top-flop/" class="footer-link" onclick="onNavClick(event, 'top_flop')">⭐ Top &amp; Flop Settimanali</a></li>
                        <li><a href="/football-analytics/" class="footer-link" onclick="onNavClick(event, 'matrix')">📊 Scatter Matrix xG &amp; xA</a></li>
                    </ul>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Strumenti Tattici</div>
                    <ul class="footer-nav-list">
                        <li><a href="/rigoristi-serie-a/" class="footer-link">🎯 Tabella Rigoristi &amp; Tiratori</a></li>
                        <li><a href="/griglia-portieri/" class="footer-link" onclick="onNavClick(event, 'gk')">🧤 Griglia Portieri 38 Turni</a></li>
                        <li><a href="/infortunati-serie-a/" class="footer-link">🏥 Report Infortunati &amp; Rientri</a></li>
                        <li><a href="/scommesse-talenti/" class="footer-link" onclick="onNavClick(event, 'gems')">💎 Talenti Low-Cost</a></li>
                        <li><a href="/confronto-calciatori/" class="footer-link" onclick="onNavClick(event, 'matchup')">⚔️ Head-to-Head 1vs1</a></li>
                    </ul>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Note Legali &amp; Privacy</div>
                    <ul class="footer-nav-list">
                        <li><a href="/privacy-policy/" class="footer-link" id="footer-privacy-link">🔒 Privacy Policy (GDPR)</a></li>
                        <li><span class="footer-status-pill">🛡️ Privacy by Design</span></li>
                        <li><span class="footer-status-pill">🚫 No Cookie Pubblicitari</span></li>
                        <li><span class="footer-status-pill">📊 GA4 IP Anonimizzato</span></li>
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
                    <strong>Informativa Privacy &amp; Cookie (Linee Guida Garante Privacy 10/06/2021):</strong> Questo sito rispetta rigorosamente la privacy degli utenti. Non viene effettuata alcuna profilazione commerciale né tracciamento pubblicitario; gli indirizzi IP sono mascherati. Il portale adotta metriche statistiche aggregate (Google Analytics 4 con IP anonimizzato e senza combinazione dati) formalmente equiparate a cookie tecnici ai sensi delle Linee Guida del Garante per la Protezione dei Dati Personali del 10 giugno 2021, esentando la piattaforma dall'obbligo di banner cookie preventivo.
                </p>
            </div>

            <div class="footer-bottom-bar">
                <div class="footer-copy">
                    &copy; 2026/2027 <strong>Fanta Master AI</strong> — <code>fantamasterai.it</code>. Tutti i diritti riservati.
                </div>
                <div class="footer-bottom-links">
                    <a href="/privacy-policy/" class="footer-bottom-link">Privacy Policy</a>
                    <span class="footer-sep">•</span>
                    <a href="mailto:info@fantamasterai.it" class="footer-bottom-link">info@fantamasterai.it</a>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>
"""

    out_path = os.path.join(root_dir, "Dashboard_Fanta_1000.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"-> [BuildDashboard] File standalone compilato con successo: {out_path}")

    # Sincronizzazione con l'App Android (solo se esplicitamente richiesta)
    if sync_android:
        android_assets_dir = os.path.join(root_dir, "android", "app", "src", "main", "assets")
        if os.path.exists(android_assets_dir):
            android_out = os.path.join(android_assets_dir, "Dashboard_Fanta_1000.html")
            with open(android_out, 'w', encoding='utf-8') as f:
                f.write(html_template)
            print(f"-> [BuildDashboard] Asset sincronizzato nell'App Android: {android_out}")

    return out_path

if __name__ == "__main__":
    build_standalone_dashboard()
