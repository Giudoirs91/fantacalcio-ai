import os
import json

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

    # 2. Carica CSS e JS modulari
    css_path = os.path.join(root_dir, "web", "css", "dashboard.css")
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    xlsx_script_tag = '<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>\n'

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
        "trade_machine.js",
        "repair_auction.js",
        "league_report.js",
        "top_flop.js",
        "stats_seriea.js",
        "analytics_matrix.js",
        "sync.js"
    ]
    js_content = ""
    for jm in js_modules:
        j_path = os.path.join(root_dir, "web", "js", jm)
        with open(j_path, 'r', encoding='utf-8') as f:
            js_content += f"\n// --- {jm} ---\n" + f.read() + "\n"

    players_json = json.dumps(players_data, ensure_ascii=False)
    gk_json = json.dumps(gk_data, ensure_ascii=False)
    tactical_json = json.dumps(tactical_data, ensure_ascii=False)
    team_stats_json = json.dumps(team_stats_data, ensure_ascii=False)
    top_flop_json = json.dumps(top_flop_data, ensure_ascii=False)
    cal_json = json.dumps(cal_data, ensure_ascii=False)

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
    <meta name="twitter:card" content="summary_large_image">
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
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- VENDOR_XLSX_INJECTION -->
    <!-- Vercel Analytics -->
    <script defer src="/_vercel/insights/script.js"></script>
    <style>
{css_content}
    </style>
</head>
<body>
    <header class="app-header-unified">
        <div class="header-main-row">
            <!-- LEFT: BRANDING + LEAGUES HUB + LEAGUE SELECTOR + MODE -->
            <div class="header-left">
                <div class="brand-badge" onclick="handleBrandSecretClick(); switchTab('auction');" title="Fanta Master AI — Portale Statistico Serie A 2026/27">
                    <span class="brand-icon">⚡</span>
                    <div>
                        <div class="brand-title">FANTA MASTER AI</div>
                        <div class="brand-sub">Portale Statistico</div>
                    </div>
                </div>

                <button class="nav-btn-icon creator-only-control" id="tabHomeBtn" onclick="switchTab('home')" title="Hub Campionati & Leghe (Accesso Creatore)">
                    🏠 Leghe
                </button>

                <!-- LEAGUE SELECTOR DROPDOWN (Popolato dinamicamente da LeaguesManager) -->
                <div id="headerLeagueSelectorContainer"></div>
            </div>

            <!-- CENTER: INTELLIGENT DIRECT NAVIGATION (NO REDUNDANCY!) -->
            <nav class="header-nav-groups">
                <!-- 1. LISTONE CALCIATORI (ACCESSO DIRETTO PRIMARIO) -->
                <a href="/" class="nav-direct-btn" id="tabAuctionBtn" onclick="onNavClick(event, 'auction')" title="Tabellone & Listone Calciatori">
                    <span>📋</span> Listone Calciatori
                </a>

                <!-- 2. STATISTICHE SERIE A (FOCUS ANALISI & DATI) -->
                <div class="nav-dropdown">
                    <button class="nav-group-btn" id="navGroupTactics">
                        <span>📈</span> Statistiche Serie A <span class="caret">▾</span>
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
                    <button class="nav-group-btn" id="navGroupAi">
                        <span>🧠</span> AI & Consigli <span class="caret">▾</span>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/consigli-fantacalcio/" class="dropdown-item" id="tabMatchdayAdviceBtn" onclick="onNavClick(event, 'matchday_advice')">🎯 Chi Schierare Prossima Giornata</a>
                        <a href="/top-11-ai/" class="dropdown-item" id="tabAiSquadsBtn" onclick="onNavClick(event, 'ai_squads')">🧠 5 Squadre Perfette AI</a>
                        <a href="/scommesse-talenti/" class="dropdown-item" id="tabGemsBtn" onclick="onNavClick(event, 'gems')">🔮 Gemme & Sleeper AI</a>
                        <div class="dropdown-divider"></div>
                        <a href="/infortunati-serie-a/" class="dropdown-item">🩺 Infortunati & Tempi di Recupero</a>
                        <a href="/rigoristi-serie-a/" class="dropdown-item">🎯 Rigoristi & Calci Piazzati</a>
                    </div>
                </div>
            </nav>

            <div class="header-right">
                <!-- CREATOR STATUS BADGE (Visibile solo se abilitato) -->
                <div id="creatorStatusBadge" class="creator-status-badge creator-only-control" onclick="openCreatorAuthModal()" title="👑 Modalità Creatore Attiva. Clicca per disattivare o gestire.">
                    <span>👑 Creatore Attivo</span>
                </div>

                <div class="header-squad-pill" style="display:none;" onclick="showComingSoonModal('Gestione Rose & Crediti')" title="Gestione Rosa (In Arrivo)">
                    <span style="font-size:13px;">📋</span>
                    <span class="pill-credits" id="hdrRemainingBudget">1000 CR</span>
                    <span class="pill-divider">•</span>
                    <span class="pill-count" id="hdrPlayersCount">0/25</span>
                </div>

                <!-- METODOLOGIA & INFO AI BUTTON (UNICO E CHIARO) -->
                <button class="nav-btn-icon btn-ai-info-pill" onclick="openAiMethodologyModal('ovr')" title="Trasparenza & Metodologia AI — Come funziona l'algoritmo">
                    <span class="info-icon-badge">ℹ️</span>
                    <span class="info-text-label">Come Funziona l'AI</span>
                </button>

                <!-- GESTIONE DROPDOWN (PULITO, ZERO RIDONDANZE) -->
                <div class="nav-dropdown align-right">
                    <button class="nav-btn-icon" title="Opzioni e Strumenti">
                        ⚙️ Gestione <span class="caret">▾</span>
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

                <!-- MOBILE HAMBURGER MENU BUTTON -->
                <button class="mobile-menu-trigger" id="btnMobileMenu" onclick="openMobileMenuModal()" title="Menu Navigazione & Opzioni">☰</button>
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

        <!-- Tab 1: Tabellone Asta -->
        <section id="viewAuction" class="tab-content auction-main-layout">
            <!-- Left: Filters & Table -->
            <div class="auction-table-column" id="auctionTableColumn" style="flex:1;min-width:0;display:flex;flex-direction:column;gap:12px;">
                <!-- Clean Modern Filter Bar -->
                <div class="clean-filter-bar">
                    <!-- Local Super Partes Mode Switcher (Classic vs Mantra) -->
                    <div class="auction-mode-switch-group" id="auctionModeSwitchContainer" title="Modalità di visualizzazione per questo Tabellone Super Partes">
                        <button type="button" class="auction-mode-toggle-btn active" id="btnAuctionModeClassic" onclick="setAuctionTableMode('classic')">⚡ Classic</button>
                        <button type="button" class="auction-mode-toggle-btn" id="btnAuctionModeMantra" onclick="setAuctionTableMode('mantra')">💎 Mantra</button>
                    </div>

                    <div class="search-group" style="flex:1;min-width:200px;">
                        <input type="text" id="searchBox" class="clean-input-search" placeholder="🔍 Cerca calciatore, club o 'rigoristi'..." oninput="onSearchChange(this.value)">
                    </div>

                    <!-- Role Quick Chips (Classic) -->
                    <div class="role-chip-group" id="classicRoleChipsGroup">
                        <button class="role-chip active" data-role="ALL" onclick="setRoleFilterQuick('ALL')">TUTTI</button>
                        <button class="role-chip P" data-role="P" onclick="setRoleFilterQuick('P')">🧤 P</button>
                        <button class="role-chip D" data-role="D" onclick="setRoleFilterQuick('D')">🛡️ D</button>
                        <button class="role-chip C" data-role="C" onclick="setRoleFilterQuick('C')">🪄 C</button>
                        <button class="role-chip A" data-role="A" onclick="setRoleFilterQuick('A')">⚡ A</button>
                    </div>

                    <!-- Compact Team Select -->
                    <select id="filterTeam" class="clean-select" onchange="onFilterTeamChange(this.value)">
                        <option value="ALL">Tutti i 20 Club</option>
                    </select>

                    <!-- Quick Toggles -->
                    <div class="quick-toggles">
                        <button id="btnToggleFav" class="chip-toggle" onclick="toggleFavFilterQuick()">⭐ Preferiti</button>
                        <button id="btnToggleAvail" class="chip-toggle" onclick="toggleAvailFilterQuick()">🟢 Svincolati</button>
                        <button id="btnToggleOop" class="chip-toggle" onclick="toggleOopFilterQuick()">💎 OOP</button>
                    </div>

                    <!-- Advanced Filter Drawer Button -->
                    <div class="filter-actions-right">
                        <button id="btnAdvancedFilters" class="btn-clean-action" onclick="toggleAdvancedFiltersDrawer()" title="Filtri Avanzati">
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

                <!-- Advanced Filters Collapsible Drawer -->
                <div id="advancedFiltersDrawer" class="advanced-filters-drawer" style="display:none;">
                    <div class="advanced-filters-grid">
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
                                <option value="titolarissimo">🔒 Titolarissimo</option>
                                <option value="rotation">🔄 Ballottaggio</option>
                                <option value="sleeper">🔥 Sleeper</option>
                                <option value="lowcost">🪙 Low Cost</option>
                                <option value="flop">⚠️ A Rischio</option>
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
                                <option value="delta_xfm">💎 Occasioni (Sotto-rendimento Δ)</option>
                                <option value="mv_2627">📊 Media Voto Pura (MV)</option>
                                <option value="titolarita">🔒 Titolarità %</option>
                                <option value="name">🔤 Nome Alfabetico</option>
                            </select>
                        </div>

                        <div class="adv-filter-item" style="display:flex;align-items:flex-end;">
                            <button class="btn-clean-reset" onclick="resetAllFilters()" title="Reimposta filtri">↺ Reset Filtri</button>
                        </div>
                    </div>
                </div>

                <div class="table-subbar-container" style="display:flex;align-items:center;justify-content:space-between;padding:4px 4px 8px 4px;flex-wrap:wrap;gap:8px;">
                    <span id="lblPlayerCount" style="color:var(--text-secondary);font-weight:700;font-size:12px;">Mostrati: 523 / 523 Calciatori</span>

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
                                <th onclick="setSort('qta')" style="text-align:center;cursor:pointer;" title="Quotazione Ufficiale">Qt.</th>
                                <th onclick="setSort('ai_advice')" style="cursor:pointer;" title="Tag Smart AI (Consiglio, Rigori, OOP)">Tag AI & Strategia</th>
                                <th onclick="setSort('titolarita')" style="text-align:center;cursor:pointer;" title="Percentuale Titolarità">Tit.</th>
                                <th onclick="setSort('coppia_nome')" style="cursor:pointer;" title="Sostituto / Staffetta di Reparto">Sostituto / Coppia</th>
                                <th onclick="setSort('mv_2627')" style="text-align:center;cursor:pointer;" title="Media Voto 2026/27">MV</th>
                                <th onclick="setSort('fm_2627')" style="text-align:center;cursor:pointer;" title="FantaMedia Reale 2026/27">FM</th>
                                <th onclick="setSort('xfm')" style="text-align:center;cursor:pointer;" title="Expected FantaMedia (xFM) - FantaMedia Attesa dal Modello AI">xFM</th>
                                <th onclick="setSort('delta_xfm')" style="text-align:center;cursor:pointer;" title="Delta Performance (FM - xFM): Verde=Overperforming, Oro/Rosso=Underperforming/Occasione">Δ xFM</th>
                                <th onclick="setSort('gol_2627')" style="text-align:center;cursor:pointer;" title="Gol / Assist 2026/27">Gol/Ass</th>
                                <th onclick="setSort('xg_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Expected Goals (xG 2026/27)">xG</th>
                                <th onclick="setSort('xa_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Expected Assists (xA 2026/27)">xA</th>
                                <th onclick="setSort('minuti_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Minuti Giocati 2026/27">Min'</th>
                                <th onclick="setSort('amm_2627')" class="col-adv-stat" style="text-align:center;cursor:pointer;" title="Cartellini Gialli e Rossi (Amm/Esp)">Cart.</th>
                                <th style="width:48px;text-align:center;" title="Azioni Asta">Az.</th>
                            </tr>
                        </thead>
                        <tbody id="auctionTableBody"></tbody>
                    </table>
                </div>
            </div>

            <!-- Hidden Container for JS compatibility -->
            <div id="sidebarRosterContainer" style="display:none !important;"></div>
        </section>

        <!-- Tab: Consigliati Prossima Giornata (AI & Report) -->
        <section id="viewMatchdayAdvice" class="tab-content" style="display:none;width:100%;">
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

        <!-- Tab 5: Gemme Nascoste & Sleeper AI -->
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
        <button class="mobile-nav-item active" id="mobNavAuction" onclick="switchTabMobile('auction')">
            <span class="mob-icon">📋</span>
            <span class="mob-label">Tabellone</span>
        </button>
        <button class="mobile-nav-item" id="mobNavStats" onclick="switchTabMobile('stats')">
            <span class="mob-icon">📊</span>
            <span class="mob-label">Statistiche</span>
        </button>
        <button class="mobile-nav-item" id="mobNavAdvice" onclick="switchTabMobile('matchday_advice')">
            <span class="mob-icon">🎯</span>
            <span class="mob-label">Consigli AI</span>
        </button>
        <button class="mobile-nav-item" id="mobNavPitch" onclick="switchTabMobile('pitch')">
            <span class="mob-icon">⚽</span>
            <span class="mob-label">Campo 2D</span>
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
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('ai_squads')">🧠 5 Squadre Perfette AI</button>
                        <button class="mobile-menu-link-btn" onclick="switchTabMobile('gems')">🔮 Gemme & Sleeper</button>
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
            'auction': '/',
            'top_flop': '/top-flop/',
            'matchday_advice': '/consigli-fantacalcio/',
            'matrix': '/football-analytics/',
            'stats': '/statistiche-serie-a/',
            'pitch': '/probabili-formazioni/',
            'matchup': '/confronto-calciatori/',
            'gk': '/griglia-portieri/',
            'ai_squads': '/top-11-ai/',
            'gems': '/scommesse-talenti/',
            'home': '/leghe/'
        }};

        const PATH_TO_TAB = {{
            '/': 'auction',
            '/index.html': 'auction',
            '/app.html': 'auction',
            '/top-flop': 'top_flop',
            '/top-flop/': 'top_flop',
            '/top-flop/index.html': 'top_flop',
            '/consigli-fantacalcio': 'matchday_advice',
            '/consigli-fantacalcio/': 'matchday_advice',
            '/consigli-fantacalcio/index.html': 'matchday_advice',
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
            'matrix': 'matrix',
            'stats': 'stats',
            'pitch': 'pitch',
            'matchup': 'matchup',
            'gk': 'gk',
            'ai_squads': 'ai_squads',
            'gems': 'gems',
            'auction': 'auction',
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
            const LOCKED_TABS = ['home', 'squad_builder', 'repair', 'trade', 'report'];
            if (LOCKED_TABS.includes(tabId)) {{
                if (typeof isCreatorModeActive === 'function' && isCreatorModeActive()) {{
                    // Accesso consentito per il Creatore!
                }} else {{
                    const tabNames = {{
                        'home': 'Hub Gestione Leghe Private',
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
            try {{
                localStorage.setItem('FANTA_LAST_ACTIVE_TAB', tabId);
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

            ['tabHomeBtn', 'tabAuctionBtn', 'tabAiSquadsBtn', 'tabMatchdayAdviceBtn', 'tabSquadBuilderBtn', 'tabTopFlopBtn', 'tabMatrixBtn', 'tabStatsBtn', 'tabPitchBtn', 'tabMatchupBtn', 'tabGkBtn', 'tabGemsBtn', 'tabTradeBtn', 'tabRepairBtn', 'tabReportBtn'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            // Reset mobile bottom nav active tabs
            ['mobNavStats', 'mobNavAuction', 'mobNavAdvice', 'mobNavPitch'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            // Reset dropdown group buttons
            ['navGroupAuction', 'navGroupTactics', 'navGroupAi'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            }});

            ['viewHomeHub', 'viewAuction', 'viewMatchdayAdvice', 'viewAiSquads', 'viewSquadBuilder', 'viewTopFlop', 'viewMatrix', 'viewStats', 'viewPitch', 'viewMatchup', 'viewGk', 'viewGems', 'viewTradeMachine', 'viewRepairAuction', 'viewLeagueReport'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.style.display = 'none';
            }});

            // Budget bar is only for live auctions (hidden in statistical consultation mode)
            const budgetBar = document.querySelector('.budget-bar-wrapper');
            if (budgetBar) budgetBar.style.display = 'none';

            if (tabId === 'home') {{
                const btn = document.getElementById('tabHomeBtn');
                if (btn) btn.classList.add('active');
                const view = document.getElementById('viewHomeHub');
                if (view) view.style.display = 'block';
                if (typeof renderHomeHubView === 'function') renderHomeHubView();
            }} else if (tabId === 'auction') {{
                const btn = document.getElementById('tabAuctionBtn');
                if (btn) btn.classList.add('active');
                const mob = document.getElementById('mobNavAuction');
                if (mob) mob.classList.add('active');
                const view = document.getElementById('viewAuction');
                if (view) view.style.display = 'flex';
                if (typeof renderTable === 'function') renderTable();
            }} else if (tabId === 'stats') {{
                const btn = document.getElementById('tabStatsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavStats');
                if (mob) mob.classList.add('active');
                document.getElementById('viewStats').style.display = 'block';
                if (typeof renderStatsSerieAView === 'function') renderStatsSerieAView();
            }} else if (tabId === 'matchday_advice') {{
                const btn = document.getElementById('tabMatchdayAdviceBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavAdvice');
                if (mob) mob.classList.add('active');
                document.getElementById('viewMatchdayAdvice').style.display = 'block';
                if (typeof renderMatchdayAdviceView === 'function') renderMatchdayAdviceView();
            }} else if (tabId === 'top_flop') {{
                const btn = document.getElementById('tabTopFlopBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                document.getElementById('viewTopFlop').style.display = 'block';
                if (typeof renderTopFlopView === 'function') renderTopFlopView();
            }} else if (tabId === 'matrix') {{
                const btn = document.getElementById('tabMatrixBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                document.getElementById('viewMatrix').style.display = 'block';
                if (typeof renderAnalyticsMatrixView === 'function') renderAnalyticsMatrixView();
            }} else if (tabId === 'pitch') {{
                const btn = document.getElementById('tabPitchBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavPitch');
                if (mob) mob.classList.add('active');
                document.getElementById('viewPitch').style.display = 'block';
                const currentClub = State.currentTeamPitch || 'Inter';
                const sel = document.getElementById('selectPitchTeam');
                if (sel) sel.value = currentClub;
                renderPitchTeam(currentClub);
            }} else if (tabId === 'matchup') {{
                const btn = document.getElementById('tabMatchupBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                document.getElementById('viewMatchup').style.display = 'flex';
                updateMatchup();
            }} else if (tabId === 'gk') {{
                const btn = document.getElementById('tabGkBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupTactics');
                if (grp) grp.classList.add('active');
                const mob = document.getElementById('mobNavGk');
                if (mob) mob.classList.add('active');
                document.getElementById('viewGk').style.display = 'flex';
                renderGkGrid();
            }} else if (tabId === 'ai_squads') {{
                const btn = document.getElementById('tabAiSquadsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                document.getElementById('viewAiSquads').style.display = 'flex';
                renderAiSquadsTab();
            }} else if (tabId === 'gems') {{
                const btn = document.getElementById('tabGemsBtn');
                if (btn) btn.classList.add('active');
                const grp = document.getElementById('navGroupAi');
                if (grp) grp.classList.add('active');
                document.getElementById('viewGems').style.display = 'block';
                renderGemsTab();
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
            if (State.sortBy === field) {{
                State.sortAsc = !State.sortAsc;
            }} else {{
                State.sortBy = field;
                State.sortAsc = (field === 'role' || field === 'name' || field === 'team' || field === 'slot_num');
            }}
            renderTable();
        }}

        // Inizializzazione Applicazione
        window.addEventListener('DOMContentLoaded', () => {{
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
                return 'auction';
            }}

            const initialTab = resolveCurrentTab();
            switchTab(initialTab, false);
            renderPitchTeam('Inter');
        }});

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
</body>
</html>
"""

    # Inietta libreria SheetJS vendor
    html_template = html_template.replace("<!-- VENDOR_XLSX_INJECTION -->", xlsx_script_tag)

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
