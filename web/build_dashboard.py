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

    # 2. Carica CSS e JS modulari minificati
    css_path = os.path.join(root_dir, "web", "css", "dashboard.css")
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = minify_css(f.read())

    js_modules = [
        "state.js",
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
    top_flop_json = json.dumps(top_flop_data, ensure_ascii=False)
    cal_json = json.dumps(cal_data, ensure_ascii=False)
    accuracy_json = json.dumps(accuracy_data, ensure_ascii=False)

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
</head>
<body>
    <header class="app-header-unified">
        <div class="header-main-row">
            <!-- LEFT: MODERN BRAND LOGO -->
            <div class="header-left">
                <a href="/" class="brand-logo-modern" onclick="onNavClick(event, 'home')" title="Fanta Master AI — Serie A 2026/27">
                    <div class="brand-icon-box" style="padding:2px;overflow:hidden;display:flex;align-items:center;justify-content:center;">
                        <img src="/static/icon-192.png" alt="Fanta Master AI Logo" style="width:100%;height:100%;object-fit:cover;border-radius:6px;">
                    </div>
                    <div class="brand-text-wrap">
                        <span class="brand-main-name">Fanta Master <span class="brand-gradient-tag">AI</span></span>
                    </div>
                    <span class="brand-season-capsule">2026/27</span>
                </a>

                <button class="nav-btn-icon creator-only-control" id="tabLeaguesBtn" onclick="switchTab('leagues')" title="Hub Campionati & Leghe (Accesso Creatore)">
                    👑 Leghe
                </button>

                <!-- Hidden container preserving ID for JS state compatibility -->
                <span id="headerPageTitle" style="display:none;">Home — Statistiche Serie A</span>
            </div>

            <!-- CENTER: SLEEK SEGMENTED PILL NAVIGATION BAR -->
            <nav class="header-nav-groups">
                <!-- 0. HOME -->
                <a href="/" class="nav-direct-btn active" id="tabHomeNavBtn" onclick="onNavClick(event, 'home')" title="Home — Statistiche Principali & Leader">
                    <span>🏠</span> Home
                </a>

                <!-- 1. LISTONE CALCIATORI -->
                <a href="/listone/" class="nav-direct-btn" id="tabAuctionBtn" onclick="onNavClick(event, 'auction')" title="Tabellone & Listone Calciatori">
                    <span>📋</span> Listone Calciatori
                </a>

                <!-- 2. STATISTICHE SERIE A -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupTactics" onclick="onNavClick(event, 'stats')">
                        <span>📈</span> Statistiche Serie A <span class="nav-caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/statistiche-serie-a/" class="dropdown-item" id="tabStatsBtn" onclick="onNavClick(event, 'stats')">📊 Statistiche & xG Serie A</a>
                        <a href="/top-flop/" class="dropdown-item" id="tabTopFlopBtn" onclick="onNavClick(event, 'top_flop')">⚡ Top & Flop di Giornata</a>
                        <a href="/football-analytics/" class="dropdown-item" id="tabMatrixBtn" onclick="onNavClick(event, 'matrix')">📈 Matrice & Scatter Analytics</a>
                        <a href="/probabili-formazioni/" class="dropdown-item" id="tabPitchBtn" onclick="onNavClick(event, 'pitch')">⚽ Campo 2D & Schemi Club</a>
                        <a href="/confronto-calciatori/" class="dropdown-item" id="tabMatchupBtn" onclick="onNavClick(event, 'matchup')">⚔️ Matchup 1vs1 Calciatori</a>
                        <a href="/griglia-portieri/" class="dropdown-item" id="tabGkBtn" onclick="onNavClick(event, 'gk')">🧤 Griglia Portieri 38/38</a>
                    </div>
                </div>

                <!-- 3. AI & CONSIGLI -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupAi" onclick="onNavClick(event, 'matchday_advice')">
                        <span>🧠</span> AI & Consigli <span class="nav-caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/consigli-fantacalcio/" class="dropdown-item" id="tabMatchdayAdviceBtn" onclick="onNavClick(event, 'matchday_advice')">🎯 Chi Schierare Prossima Giornata</a>
                        <a href="/chi-schiero/" class="dropdown-item" id="tabChiSchieroBtn" onclick="onNavClick(event, 'chi_schiero')">⚔️ Tool "Chi Schiero?" (Ballottaggi 1vs1)</a>
                        <a href="/top-11-ai/" class="dropdown-item" id="tabAiSquadsBtn" onclick="onNavClick(event, 'ai_squads')">🔒 5 Squadre Perfette AI <span style="font-size:10px;background:rgba(239,68,68,0.2);color:#f87171;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:6px;">In Aggiornamento</span></a>
                        <a href="/scommesse-talenti/" class="dropdown-item" id="tabGemsBtn" onclick="onNavClick(event, 'gems')">🔮 Gemme & Scommesse AI</a>
                        <div class="dropdown-divider"></div>
                        <a href="/infortunati-serie-a/" class="dropdown-item">🩺 Infortunati & Tempi di Recupero</a>
                        <a href="/rigoristi-serie-a/" class="dropdown-item">🎯 Rigoristi & Calci Piazzati</a>
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

        <!-- Tab 0-Bis: Home Page Principale (AI Command Center & Predictive Hub) -->
        <section id="viewHome" class="tab-content active" style="display:flex;flex-direction:column;gap:20px;width:100%;">
            <div class="ai-hub-container">

                <!-- 1. HERO NEURAL COMMAND CENTER -->
                <div class="ai-hub-hero">
                    <!-- Badges Bar -->
                    <div class="ai-hub-badge-bar">
                        <span class="ai-badge-chip live">
                            <span class="pulse-dot-green"></span>
                            Serie A 2026/27 • Live Engine
                        </span>
                        <span class="ai-badge-chip tech">🧠 Motore Predittivo xFM v2.4</span>
                        <span class="ai-badge-chip purple">📊 534 Calciatori Modellati</span>
                        <span class="ai-badge-chip tech">🏟️ 20 Club su Campo 2D</span>
                    </div>

                    <!-- Main Catchy Title -->
                    <h1 class="ai-hub-title">
                        L'Algoritmo Predittivo N°1 per il <span class="gradient-text">Fantacalcio Serie A</span>
                    </h1>

                    <!-- Authoritative Subtitle -->
                    <p class="ai-hub-subtitle">
                        Smetti di affidarti alle impressioni soggettive dei giornali. Fanta Master AI elabora oltre 50 metriche avanzate (Expected Goals, Expected Assists, Indici di Schierabilità e Fragilità Fisica) per anticipare bonus, flop e occasioni di mercato con precisione matematica.
                    </p>

                    <!-- Interactive Real-time Search Box -->
                    <div class="ai-hub-search-wrap">
                        <div class="ai-hub-search-inner">
                            <span class="ai-hub-search-icon">🔍</span>
                            <input type="text" id="hubQuickSearch" class="ai-hub-search-input" placeholder="Cerca qualsiasi calciatore (es. Malen, Lautaro, Nico Paz, Svilar)..." oninput="filterHubPlayers(this.value)" autocomplete="off">
                        </div>
                        <div id="hubSearchResults" class="ai-hub-search-results"></div>
                    </div>

                    <!-- Quick Chips -->
                    <div class="ai-hub-quick-chips">
                        <span class="quick-chip-lbl">Ricerche Rapide:</span>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Malen')">🔥 Malen</button>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Lautaro')">⚡ Lautaro</button>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Dybala')">🎯 Dybala</button>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Paz N.')">💎 Nico Paz</button>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Dimarco')">🛡️ Dimarco</button>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Svilar')">🧤 Svilar</button>
                        <button class="hub-chip-btn" onclick="openPlayerByName('Woltemade')">🔮 Woltemade</button>
                    </div>

                    <!-- Primary CTAs -->
                    <div class="ai-hub-cta-bar">
                        <button class="hub-cta-btn primary" onclick="switchTab('chi_schiero')">
                            <span>⚔️ Risolvi un Ballottaggio (Chi Schiero 1vs1)</span>
                        </button>
                        <button class="hub-cta-btn secondary" onclick="switchTab('pitch')">
                            <span>🏟️ Probabili Formazioni 2D &amp; Schemi</span>
                        </button>
                        <button class="hub-cta-btn secondary" onclick="switchTab('auction')">
                            <span>📋 Listone &amp; Valutazioni FVM</span>
                        </button>
                    </div>
                </div>

                <!-- 2. AI INTELLIGENCE PULSE (3-BENTO: TOP PICK, FLOP ALERT, SCOMMESSA) -->
                <div>
                    <div class="ai-section-title-wrap">
                        <span class="ai-section-tag">⚡ Live Intelligence Pulse</span>
                        <h2 class="ai-section-title">
                            <span>🧠</span> I 3 Verdetti Chiave dell'Algoritmo
                        </h2>
                        <p class="ai-section-subtitle">Analisi computazionale match-by-match per schierare la formazione ideale e minimizzare i rimpianti.</p>
                    </div>

                    <div class="ai-pulse-grid">
                        <!-- Card 1: Top AI Pick & Capitano Ideale -->
                        <div class="ai-pulse-card pick">
                            <div class="pulse-card-header">
                                <span class="pulse-badge green">🚀 Top Pick &amp; Capitano AI</span>
                                <span class="pulse-card-score" style="color:#4ade80;">98% Schierabile</span>
                            </div>
                            <div class="pulse-player-box">
                                <span class="role-badge A" style="width:34px;height:34px;font-size:15px;">A</span>
                                <div>
                                    <div class="pulse-player-name">Donyell Malen</div>
                                    <div class="pulse-player-sub">Roma • Attaccante • OVR 88</div>
                                </div>
                            </div>
                            <div class="pulse-metrics-strip">
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">xFM Previsto</span>
                                    <span class="p-val" style="color:#00e676;">8.45</span>
                                </div>
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">xG / 90m</span>
                                    <span class="p-val" style="color:#38bdf8;">0.92</span>
                                </div>
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">Status Tattico</span>
                                    <span class="p-val" style="color:#fbbf24;">1° Rigorista</span>
                                </div>
                            </div>
                            <div class="pulse-quote-box">
                                <b>Verdetto AI:</b> <i>"Capocannoniere del torneo con 6 reti e miglior volume di tiri nello specchio. Matchup ideale contro difesa a linea alta. Must-have assoluto di giornata."</i>
                            </div>
                            <button class="pulse-action-link" onclick="openPlayerByName('Malen')">
                                <span>Apri Scheda Calciatore &amp; Radar SVG</span>
                                <span>&rarr;</span>
                            </button>
                        </div>

                        <!-- Card 2: Flop & Trap Alert -->
                        <div class="ai-pulse-card danger">
                            <div class="pulse-card-header">
                                <span class="pulse-badge red">⚠️ Flop &amp; Trappola Alert</span>
                                <span class="pulse-card-score" style="color:#f87171;">Difficoltà 4.7/5</span>
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
                                    <span class="p-lbl">Matchup</span>
                                    <span class="p-val" style="color:#f87171;">vs Milan</span>
                                </div>
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">Indice Difesa</span>
                                    <span class="p-val" style="color:#ef4444;">🧱 Muro</span>
                                </div>
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">xFM Proiettato</span>
                                    <span class="p-val" style="color:#fbbf24;">7.02 (Down)</span>
                                </div>
                            </div>
                            <div class="pulse-quote-box" style="border-left-color:#ef4444;">
                                <b>Verdetto AI:</b> <i>"Big match proibitivo a San Siro contro la difesa meno battuta. Alto rischio isolamento e cartellini; l'algoritmo suggerisce cautela e rotazione se disponi di alternative d'attacco."</i>
                            </div>
                            <button class="pulse-action-link" onclick="openPlayerByName('Laurient')">
                                <span>Analizza Matchup &amp; Profilo Giocatore</span>
                                <span>&rarr;</span>
                            </button>
                        </div>

                        <!-- Card 3: Scommessa & Differenziale AI -->
                        <div class="ai-pulse-card gem">
                            <div class="pulse-card-header">
                                <span class="pulse-badge purple">🔮 Vera Gemma Low-Cost</span>
                                <span class="pulse-card-score" style="color:#c084fc;">Upside +38%</span>
                            </div>
                            <div class="pulse-player-box">
                                <span class="role-badge C" style="width:34px;height:34px;font-size:15px;">C</span>
                                <div>
                                    <div class="pulse-player-name">Vasilije Adzic</div>
                                    <div class="pulse-player-sub">Sassuolo • Trequartista / C • 11 CR</div>
                                </div>
                            </div>
                            <div class="pulse-metrics-strip">
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">xG / 90m</span>
                                    <span class="p-val" style="color:#c084fc;">0.78</span>
                                </div>
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">Gol &amp; Assist</span>
                                    <span class="p-val" style="color:#34d399;">3G + 1A</span>
                                </div>
                                <div class="pulse-metric-item">
                                    <span class="p-lbl">Prezzo Cons.</span>
                                    <span class="p-val" style="color:#fbbf24;">11 CR (Gemma)</span>
                                </div>
                            </div>
                            <div class="pulse-quote-box" style="border-left-color:#c084fc;">
                                <b>Verdetto AI:</b> <i>"Furto d'asta legalizzato a soli 11 crediti: numeri offensivi sbalorditivi con 0.78 xG90 da attaccante aggiunto e già 3 reti. Il miglior rapporto costo/resa di giornata per la trequarti."</i>
                            </div>
                            <button class="pulse-action-link" onclick="openPlayerByName('Adzic')">
                                <span>Esplora Radar &amp; Proiezioni Future</span>
                                <span>&rarr;</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 3. LA SUITE DEI 6 SUPERPOTERI AI (BENTO CAPABILITIES) -->
                <div>
                    <div class="ai-section-title-wrap">
                        <span class="ai-section-tag">🛠️ Strumenti Pro di Nuova Generazione</span>
                        <h2 class="ai-section-title">
                            <span>✨</span> La Suite Completa di Fanta Master AI
                        </h2>
                        <p class="ai-section-subtitle">Tutti i tool analitici sviluppati per farti vincere leghe a 8, 10 o 12 partecipanti.</p>
                    </div>

                    <div class="ai-capabilities-grid">
                        <!-- Tool 1: Chi Schiero -->
                        <div class="ai-cap-card" onclick="switchTab('chi_schiero')">
                            <div>
                                <div class="cap-card-top">
                                    <div class="cap-icon-box" style="background:rgba(168,85,247,0.15);border:1px solid rgba(168,85,247,0.3);color:#c084fc;">⚔️</div>
                                    <span class="cap-badge-tag">Simulatore 1vs1</span>
                                </div>
                                <h3 class="cap-title">Tool "Chi Schiero?"</h3>
                                <p class="cap-desc">Hai un dubbio di formazione? Confronta due giocatori testa a testa. L'algoritmo simula bonus attesi, difficoltà dell'avversario e ti fornisce il verdetto motivato.</p>
                            </div>
                            <div class="cap-card-footer" style="color:#c084fc;">
                                <span>Risolvi Ballottaggio &rarr;</span>
                                <span style="font-size:11px;color:var(--text-muted);">Algoritmo Predittivo</span>
                            </div>
                        </div>

                        <!-- Tool 2: Probabili Formazioni 2D -->
                        <div class="ai-cap-card" onclick="switchTab('pitch')">
                            <div>
                                <div class="cap-card-top">
                                    <div class="cap-icon-box" style="background:rgba(56,189,248,0.15);border:1px solid rgba(56,189,248,0.3);color:#38bdf8;">🏟️</div>
                                    <span class="cap-badge-tag">20 Club 2D</span>
                                </div>
                                <h3 class="cap-title">Probabili Formazioni 2D</h3>
                                <p class="cap-desc">Lavagna tattica interattiva per tutti i 20 club di Serie A. Percentuali di titolarità stimate, ballottaggi aperti, gerarchie rigoristi e tiratori piazzati.</p>
                            </div>
                            <div class="cap-card-footer" style="color:#38bdf8;">
                                <span>Vedi Schemi Club &rarr;</span>
                                <span style="font-size:11px;color:var(--text-muted);">Live 2026/27</span>
                            </div>
                        </div>

                        <!-- Tool 3: Football Analytics & Radar -->
                        <div class="ai-cap-card" onclick="switchTab('matrix')">
                            <div>
                                <div class="cap-card-top">
                                    <div class="cap-icon-box" style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.3);color:#4ade80;">📈</div>
                                    <span class="cap-badge-tag">Expected Metrics</span>
                                </div>
                                <h3 class="cap-title">Football Analytics &amp; Radar</h3>
                                <p class="cap-desc">Matrice avanzata con xG, xA, Floor vs Ceiling, sub-impact delle riserve e regressione per scovare chi sta sovraperformando o per esplodere.</p>
                            </div>
                            <div class="cap-card-footer" style="color:#4ade80;">
                                <span>Analizza Metriche Avanzate &rarr;</span>
                                <span style="font-size:11px;color:var(--text-muted);">Data Science</span>
                            </div>
                        </div>

                        <!-- Tool 4: Listone & FVM Dinamico -->
                        <div class="ai-cap-card" onclick="switchTab('auction')">
                            <div>
                                <div class="cap-card-top">
                                    <div class="cap-icon-box" style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fbbf24;">💰</div>
                                    <span class="cap-badge-tag">Scala 1-1000 CR</span>
                                </div>
                                <h3 class="cap-title">Listone Intelligente &amp; FVM</h3>
                                <p class="cap-desc">534 calciatori con prezzi stimati d'asta (Fantalive Value Market), slot reparto 1-8, indici di spesa percentuale e ruoli sia Classic che Mantra.</p>
                            </div>
                            <div class="cap-card-footer" style="color:#fbbf24;">
                                <span>Apri Tabellone Asta &rarr;</span>
                                <span style="font-size:11px;color:var(--text-muted);">534 Calciatori</span>
                            </div>
                        </div>

                        <!-- Tool 5: Griglia Portieri Dinamica -->
                        <div class="ai-cap-card" onclick="switchTab('gk')">
                            <div>
                                <div class="cap-card-top">
                                    <div class="cap-icon-box" style="background:rgba(0,242,254,0.15);border:1px solid rgba(0,242,254,0.3);color:#00f2fe;">🧤</div>
                                    <span class="cap-badge-tag">38 Turni</span>
                                </div>
                                <h3 class="cap-title">Griglia Portieri Algoritmica</h3>
                                <p class="cap-desc">Matrice combinatoria degli incroci casa/trasferta a 38 giornate. Trova la coppia perfetta di portieri a basso costo per non subire mai imbarcate.</p>
                            </div>
                            <div class="cap-card-footer" style="color:#00f2fe;">
                                <span>Consulta Matrice Incroci &rarr;</span>
                                <span style="font-size:11px;color:var(--text-muted);">Zero Malus</span>
                            </div>
                        </div>

                        <!-- Tool 6: Top 11 AI & Scommesse -->
                        <div class="ai-cap-card" onclick="switchTab('matchday_advice')">
                            <div>
                                <div class="cap-card-top">
                                    <div class="cap-icon-box" style="background:rgba(236,72,153,0.15);border:1px solid rgba(236,72,153,0.3);color:#f472b6;">🎯</div>
                                    <span class="cap-badge-tag">Top 11 AI</span>
                                </div>
                                <h3 class="cap-title">Consigliati &amp; Top 11 del Turno</h3>
                                <p class="cap-desc">La formazione ideale calcolata su vincoli tattici e di budget per la giornata imminente, con indici di schierabilità percentuali per ogni ruolo.</p>
                            </div>
                            <div class="cap-card-footer" style="color:#f472b6;">
                                <span>Scopri la Top 11 &rarr;</span>
                                <span style="font-size:11px;color:var(--text-muted);">Machine Learning</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 4. PERCHÉ FANTA MASTER AI BATTE I METODI TRADIZIONALI -->
                <div class="ai-comparison-box">
                    <div class="ai-section-title-wrap" style="margin-bottom:0;">
                        <span class="ai-section-tag" style="color:#00e676;">⚔️ The Next Generation</span>
                        <h2 class="ai-section-title">
                            <span>⚡</span> Perché l'Approccio Scientifico Batte i Siti Tradizionali
                        </h2>
                        <p class="ai-section-subtitle">Il divario tra chi si affida alle "sensazioni" e chi vince usando modelli quantitativi.</p>
                    </div>

                    <div class="ai-comp-grid">
                        <!-- Legacy Methods -->
                        <div class="comp-column legacy">
                            <div class="comp-column-head">
                                <span style="font-size:22px;">📉</span>
                                <h3 style="color:#f87171;">I Metodi Tradizionali &amp; Portali Storici</h3>
                            </div>
                            <ul class="comp-feature-list">
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#ef4444;">✕</span>
                                    <span style="color:#94a3b8;"><b>Voti post-partita soggettivi:</b> Valutazioni basate sull'emotività o sulla simpatia del giornalista di turno.</span>
                                </li>
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#ef4444;">✕</span>
                                    <span style="color:#94a3b8;"><b>Consigli generici sul "nome":</b> Consigliano i calciatori più famosi senza considerare la difficoltà del matchup difensivo.</span>
                                </li>
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#ef4444;">✕</span>
                                    <span style="color:#94a3b8;"><b>Nessuna nozione di regressione:</b> Incapacità di distinguere tra un gol fortunoso e una produzione solida di Expected Goals (xG).</span>
                                </li>
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#ef4444;">✕</span>
                                    <span style="color:#94a3b8;"><b>Infortuni valutati a spanne:</b> Nessun calcolo scientifico sulla fragilità fisica, sui giorni di stop e sulle ricadute muscolari.</span>
                                </li>
                            </ul>
                        </div>

                        <!-- Fanta Master AI -->
                        <div class="comp-column ai-powered">
                            <div class="comp-column-head">
                                <span style="font-size:22px;">🚀</span>
                                <h3 style="color:#38bdf8;">Fanta Master AI (Nuova Generazione)</h3>
                            </div>
                            <ul class="comp-feature-list">
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#22c55e;">✓</span>
                                    <span style="color:#e2e8f0;"><b>Algoritmo Predittivo xFM (Expected FantaMedia):</b> Modello matematico che calcola il rendimento atteso futuro prima che i bonus si verifichino.</span>
                                </li>
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#22c55e;">✓</span>
                                    <span style="color:#e2e8f0;"><b>Simulatore 1vs1 per ogni ballottaggio:</b> Verdetto quantitativo imparziale su chi schierare tra due calciatori nel weekend.</span>
                                </li>
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#22c55e;">✓</span>
                                    <span style="color:#e2e8f0;"><b>Radar Chart SVG a 6-8 Dimensioni:</b> Visualizzazione istantanea dei percentili reali per ruolo su tiro, rifinitura, recuperi e titolarità.</span>
                                </li>
                                <li class="comp-item">
                                    <span class="comp-icon" style="color:#22c55e;">✓</span>
                                    <span style="color:#e2e8f0;"><b>Indice di Fragilità &amp; Cronistoria Medica:</b> Algoritmo di affidabilità fisica per non rischiare crediti su calciatori cronici.</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- 5. LEADER & STATISTICHE SERIE A (RE-IMAGINED & CLICKABLE) -->
                <div>
                    <div class="ai-section-title-wrap">
                        <span class="ai-section-tag">📊 Serie A 2026/27 Live</span>
                        <h2 class="ai-section-title">
                            <span>🏆</span> I Leader Statistici del Campionato
                        </h2>
                        <p class="ai-section-subtitle">Le 6 metriche più determinanti: clicca su qualsiasi calciatore per aprire la sua scheda analitica con Radar.</p>
                    </div>

                    <div class="leader-grid">
                        <!-- 1. Capocannoniere -->
                        <div class="leader-card" onclick="openPlayerByName('Malen')" style="cursor:pointer;">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">⚽ Più Gol Segnati</span>
                                <span class="leader-val">6</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge A">A</span>
                                <div>
                                    <div class="leader-player-name">Donyell Malen <span class="ovr-pill ovr-tier-elite" style="font-size:10px;margin-left:4px;">OVR 88</span></div>
                                    <div class="leader-player-team">Roma • Attaccante</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> 2° L. Martinez (Inter, 4 gol) • 3° Varela G. (Monza, 4 gol)
                            </div>
                        </div>

                        <!-- 2. Miglior Assistman -->
                        <div class="leader-card" onclick="openPlayerByName('Dybala')" style="cursor:pointer;">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">🎯 Più Assist Forniti</span>
                                <span class="leader-val">4</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge A">A</span>
                                <div>
                                    <div class="leader-player-name">Paulo Dybala <span class="ovr-pill ovr-tier-elite" style="font-size:10px;margin-left:4px;">OVR 87</span></div>
                                    <div class="leader-player-team">Roma • Seconda Punta</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> 2° Diouf (Inter, 3 assist) • 3° Schmid (Frosinone, 3 assist)
                            </div>
                        </div>

                        <!-- 3. Più xGoals (xG) -->
                        <div class="leader-card" onclick="openPlayerByName('Lautaro')" style="cursor:pointer;">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">⚡ Più xGoals (xG)</span>
                                <span class="leader-val">4.7</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge A">A</span>
                                <div>
                                    <div class="leader-player-name">Lautaro Martinez <span class="ovr-pill ovr-tier-elite" style="font-size:10px;margin-left:4px;">OVR 94</span></div>
                                    <div class="leader-player-team">Inter • Punta Centrale</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> 2° Malen (Roma, 4.6 xG) • 3° Raimondo (Frosinone, 2.5 xG)
                            </div>
                        </div>

                        <!-- 4. Più xAssists (xA) -->
                        <div class="leader-card" onclick="openPlayerByName('Dybala')" style="cursor:pointer;">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">🎨 Più xAssists (xA)</span>
                                <span class="leader-val">3.4</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge A">A</span>
                                <div>
                                    <div class="leader-player-name">Paulo Dybala <span class="ovr-pill ovr-tier-elite" style="font-size:10px;margin-left:4px;">OVR 87</span></div>
                                    <div class="leader-player-team">Roma • Trequartista / Punta</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> 2° Dimarco (Inter, 1.6 xA) • 3° Diouf (Inter, 1.5 xA)
                            </div>
                        </div>

                        <!-- 5. Miglior FantaMedia -->
                        <div class="leader-card" onclick="openPlayerByName('Malen')" style="cursor:pointer;">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">⭐ Miglior FantaMedia (FM)</span>
                                <span class="leader-val">10.6</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge A">A</span>
                                <div>
                                    <div class="leader-player-name">Donyell Malen <span class="ovr-pill ovr-tier-elite" style="font-size:10px;margin-left:4px;">OVR 88</span></div>
                                    <div class="leader-player-team">Roma • FM 10.60 (6 presenze)</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> 2° L. Martinez (Inter, 8.85 FM) • 3° Dybala (Roma, 7.90 FM)
                            </div>
                        </div>

                        <!-- 6. Più Bonus Totali -->
                        <div class="leader-card" onclick="openPlayerByName('Malen')" style="cursor:pointer;">
                            <div class="leader-card-header">
                                <span class="leader-stat-badge">💎 Più Bonus Totali (+Gol &amp; +Assist)</span>
                                <span class="leader-val">+18.0</span>
                            </div>
                            <div class="leader-player-info">
                                <span class="role-badge A">A</span>
                                <div>
                                    <div class="leader-player-name">Donyell Malen <span class="ovr-pill ovr-tier-elite" style="font-size:10px;margin-left:4px;">OVR 88</span></div>
                                    <div class="leader-player-team">Roma • 6 gol (+18 pt bonus)</div>
                                </div>
                            </div>
                            <div class="leader-podium">
                                <strong>Inseguitori:</strong> 2° L. Martinez (+12.0 bonus) • 3° Raimondo (+12.0 bonus)
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 6. SOCIAL PROOF & PLATFORM METRICS -->
                <div class="ai-counter-strip">
                    <div class="ai-counter-item">
                        <div class="c-val">534</div>
                        <div class="c-lbl">Calciatori Modellati</div>
                    </div>
                    <div class="ai-counter-item">
                        <div class="c-val">20</div>
                        <div class="c-lbl">Club Serie A in 2D</div>
                    </div>
                    <div class="ai-counter-item">
                        <div class="c-val">38</div>
                        <div class="c-lbl">Turni Monitorati</div>
                    </div>
                    <div class="ai-counter-item">
                        <div class="c-val" style="background:linear-gradient(135deg,#22c55e,#00f2fe);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">100%</div>
                        <div class="c-lbl">Statistiche Oggettive</div>
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
                            <h1>⚽ Fanta Master <span class="gradient-text">AI</span></h1>
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
                    <button class="btn-action creator-only-control" id="btnEditPitchLineup" onclick="openTacticalEditorModal()" style="background:linear-gradient(135deg, rgba(0,242,254,0.18) 0%, rgba(56,189,248,0.25) 100%);border:1px solid var(--accent-cyan);color:#fff;font-weight:800;padding:6px 14px;border-radius:8px;align-items:center;gap:7px;box-shadow:0 0 14px rgba(0,242,254,0.2);cursor:pointer;transition:all 0.2s ease;">
                        ⚙️ Modifica Formazione & Sostituti
                    </button>
                    <button class="btn-action creator-only-control" onclick="autoFillAndSaveCurrentTeam()" style="background:linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(109,40,217,0.3) 100%);border:1px solid rgba(139,92,246,0.5);color:#c084fc;font-weight:800;padding:6px 14px;border-radius:8px;align-items:center;gap:7px;box-shadow:0 0 14px rgba(139,92,246,0.2);cursor:pointer;transition:all 0.2s ease;" title="Popola e salva automaticamente titolari e sostituti da dati reali 2026/27">
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
                    <button class="btn-action" id="btnSharePitch" onclick="exportPitchScreenshot()" style="font-size:12px;background:linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(5,150,105,0.3) 100%);border:1px solid #10b981;color:#34d399;font-weight:800;padding:6px 14px;border-radius:8px;display:flex;align-items:center;gap:6px;cursor:pointer;box-shadow:0 0 14px rgba(16,185,129,0.25);" title="Scarica o condividi l'immagine grafica del campo da calcetto su WhatsApp">
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

        <!-- Tab 9b: Matrice & Scatter Analytics -->
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
        <div class="modal-card" style="max-width:520px;width:92%;background:rgba(18,22,29,0.98);backdrop-filter:blur(24px);border:1px solid rgba(245,158,11,0.35);padding:28px 24px;border-radius:20px;box-shadow:0 25px 60px rgba(0,0,0,0.9), 0 0 35px rgba(245,158,11,0.12);text-align:center;">
            <div style="width:64px;height:64px;margin:0 auto 16px;background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 0 20px rgba(245,158,11,0.2);">
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

    <!-- MOBILE BOTTOM NAVIGATION (Native App Bar - Tabellone Home) -->
    <nav class="mobile-bottom-nav" id="mobileBottomNav">
        <button class="mobile-nav-item active" id="mobNavHome" onclick="switchTabMobile('home')">
            <span class="mob-icon">🏠</span>
            <span class="mob-label">Home</span>
        </button>
        <button class="mobile-nav-item" id="mobNavAuction" onclick="switchTabMobile('auction')">
            <span class="mob-icon">📋</span>
            <span class="mob-label">Listone</span>
        </button>
        <button class="mobile-nav-item" id="mobNavPitch" onclick="switchTabMobile('pitch')">
            <span class="mob-icon">⚽</span>
            <span class="mob-label">Campo 2D</span>
        </button>
        <button class="mobile-nav-item" id="mobNavAdvice" onclick="switchTabMobile('matchday_advice')">
            <span class="mob-icon">🎯</span>
            <span class="mob-label">Consigli AI</span>
        </button>
        <button class="mobile-nav-item" id="mobNavMenu" onclick="openMobileMenuModal()">
            <span class="mob-icon">☰</span>
            <span class="mob-label">Menu</span>
        </button>
    </nav>

    <!-- Mobile Drawer Backdrop -->
    <div id="mobileDrawerBackdrop" class="mobile-drawer-backdrop" onclick="toggleMobileRosterDrawer(false)"></div>

    <!-- Mobile Menu Modal -->
    <div id="mobileMenuModal" class="modal-backdrop" style="display:none;z-index:100002;" onclick="if(event.target === this) closeMobileMenuModal()">
        <div class="modal-card" style="max-width:540px;background:rgba(18,22,29,0.98);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,0.1);padding:20px;border-radius:18px;box-shadow:0 25px 60px rgba(0,0,0,0.9);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">🏆</span>
                    <h3 style="margin:0;font-size:17px;font-weight:900;color:#fff;">Menu Principale & Sezioni</h3>
                </div>
                <button class="btn-action" onclick="closeMobileMenuModal()">✕</button>
            </div>
            
            <div class="mobile-menu-grid">
                <!-- Section 0: Home Page -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🏠</span> Home Page</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('home')">🏠 Home &amp; Leader Serie A</button>
                    </div>
                </div>

                <!-- Section 1: Calciatori & Listone -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>📋</span> Listone Principale</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('auction')">📋 Listone Calciatori & OVR</button>
                    </div>
                </div>

                <!-- Section 2: Statistiche & Calciatori -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>📖</span> Statistiche & Analisi</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('auction')">📋 Listone Calciatori & OVR</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('stats')">📊 Statistiche Serie A & xG</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('top_flop')">⚡ Top & Flop Giornata</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('matrix')">📈 Matrice Analytics</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('pitch')">⚽ Campo 2D & Schemi</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('matchup')">⚔️ Matchup 1vs1 Calciatori</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('gk')">🧤 Griglia Portieri 38/38</button>
                    </div>
                </div>

                <!-- Section 3: AI & Strategia -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🧠</span> AI & Consigli</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('matchday_advice')">🎯 Chi Schierare (Consigli)</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('ai_squads')">🔒 5 Squadre Perfette AI <span style="font-size:10px;background:rgba(239,68,68,0.2);color:#f87171;padding:2px 6px;border-radius:4px;font-weight:700;margin-left:6px;">In Aggiornamento</span></button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('gems')">🔮 Gemme & Scommesse</button>
                        <button class="mobile-menu-link-btn" onclick="closeMobileMenuModal(); openAiMethodologyModal('ovr');">ℹ️ Come Funziona l'AI</button>
                    </div>
                </div>

                <!-- Section 4: Strumenti & Gestione -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>⚙️</span> Strumenti</div>
                    <div class="mobile-menu-links">
                        <button class="mobile-menu-link-btn" onclick="closeMobileMenuModal(); resetAllFilters();">🔄 Reimposta Filtri Listone</button>
                        <button class="mobile-menu-link-btn" onclick="closeMobileMenuModal(); openCreatorAuthModal();" style="color:#fbbf24;">👑 Accesso Creatore</button>
                    </div>
                </div>

                <!-- Section 5: Community & Social Ufficiali -->
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🌐</span> Community & Social Ufficiali</div>
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
        const TOP_FLOP_DATA = {top_flop_json};
        const OFFICIAL_CALENDAR_2026_27 = {cal_json};
        const MATCHDAY_ACCURACY_DATA = {accuracy_json};

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
            '/listone': 'auction',
            '/listone/': 'auction',
            '/listone/index.html': 'auction',
            '/leghe': 'leagues',
            '/leghe/': 'leagues',
            '/top-flop': 'top_flop',
            '/top-flop/': 'top_flop',
            '/top-flop/index.html': 'top_flop',
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
            '/probabili-formazioni': 'pitch',
            '/probabili-formazioni/': 'pitch',
            '/probabili-formazioni/index.html': 'pitch',
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
            'top_flop': 'top_flop',
            'matchday_advice': 'matchday_advice',
            'chi_schiero': 'chi_schiero',
            'matrix': 'matrix',
            'stats': 'stats',
            'pitch': 'pitch',
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

        // Router & UI Handlers
        function switchTabMobile(tabId) {{
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

            State.activeTab = tabId;

            // Aggiorna titolo pulito della pagina nell'header (senza trofei, senza cornici)
            const TAB_TITLES = {{
                'home': 'Home — Statistiche Serie A',
                'auction': 'Listone Calciatori',
                'stats': 'Statistiche & xG',
                'top_flop': 'Top & Flop',
                'matrix': 'Matrice Analytics',
                'pitch': 'Campo 2D & Schemi',
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

            ['tabHomeNavBtn', 'tabLeaguesBtn', 'tabHomeBtn', 'tabAuctionBtn', 'tabAiSquadsBtn', 'tabMatchdayAdviceBtn', 'tabChiSchieroBtn', 'tabSquadBuilderBtn', 'tabTopFlopBtn', 'tabMatrixBtn', 'tabStatsBtn', 'tabPitchBtn', 'tabMatchupBtn', 'tabGkBtn', 'tabGemsBtn', 'tabTradeBtn', 'tabRepairBtn', 'tabReportBtn'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            // Reset mobile bottom nav active tabs
            ['mobNavHome', 'mobNavStats', 'mobNavAuction', 'mobNavAdvice', 'mobNavPitch'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            // Reset dropdown group buttons
            ['navGroupAuction', 'navGroupTactics', 'navGroupAi'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            ['viewHome', 'viewHomeHub', 'viewAuction', 'viewMatchdayAdvice', 'viewChiSchiero', 'viewAiSquads', 'viewSquadBuilder', 'viewTopFlop', 'viewMatrix', 'viewStats', 'viewPitch', 'viewMatchup', 'viewGk', 'viewGems', 'viewTradeMachine', 'viewRepairAuction', 'viewLeagueReport'].forEach(id => {{
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
                const grp = document.getElementById('navGroupAi');
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
                const btn = document.getElementById('tabChiSchieroBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
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
                const btn = document.getElementById('tabPitchBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavPitch');
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
                const grp = document.getElementById('navGroupTactics');
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
                const grp = document.getElementById('navGroupTactics');
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
                        <li><a href="/" class="footer-link">🏟️ Formazione &amp; Asta AI</a></li>
                        <li><a href="/consigli-fantacalcio/" class="footer-link">🎯 Consigli di Giornata</a></li>
                        <li><a href="/probabili-formazioni/" class="footer-link">⚽ Probabili Formazioni 2D</a></li>
                        <li><a href="/top-flop/" class="footer-link">⭐ Top &amp; Flop Settimanali</a></li>
                        <li><a href="/football-analytics/" class="footer-link">📊 Scatter Matrix xG &amp; xA</a></li>
                    </ul>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Strumenti Tattici</div>
                    <ul class="footer-nav-list">
                        <li><a href="/rigoristi-serie-a/" class="footer-link">🎯 Tabella Rigoristi &amp; Tiratori</a></li>
                        <li><a href="/griglia-portieri/" class="footer-link">🧤 Griglia Portieri 38 Turni</a></li>
                        <li><a href="/infortunati-serie-a/" class="footer-link">🏥 Report Infortunati &amp; Rientri</a></li>
                        <li><a href="/scommesse-talenti/" class="footer-link">💎 Talenti Low-Cost</a></li>
                        <li><a href="/confronto-calciatori/" class="footer-link">⚔️ Head-to-Head 1vs1</a></li>
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
