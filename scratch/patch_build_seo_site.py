import re

script_path = "tools/build_seo_site.py"
with open(script_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add render_unified_header function before generate_player_page
header_func = '''def render_unified_header(rel_path=""):
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

'''

if "def render_unified_header" not in content:
    content = content.replace("def generate_player_page(", header_func + "\ndef generate_player_page(")

# 2. In generate_player_page, replace header
old_player_nav = """    <!-- Top Nav -->
    <header class="site-nav">
        <div class="site-container site-nav-inner">
            <a href="../../index.html" class="brand-logo">
                ⚽ FANTA MASTER <span>AI</span>
            </a>
            <nav class="nav-links">
                <a href="../../infortunati-serie-a/index.html">Infortunati</a>
                <a href="../../rigoristi-serie-a/index.html">Rigoristi</a>
                <a href="../../griglia-portieri/index.html">Griglia Portieri</a>
                <a href="../../app.html" class="btn-launch-app">Lancia Dashboard Live 🚀</a>
            </nav>
        </div>
    </header>"""

new_player_nav = "{render_unified_header('../../')}"
content = content.replace(old_player_nav, new_player_nav)

# 3. In generate_injuries_pillar, replace header
old_inj_nav = """    <header class="site-nav">
        <div class="site-container site-nav-inner">
            <a href="../index.html" class="brand-logo">⚽ FANTA MASTER <span>AI</span></a>
            <nav class="nav-links">
                <a href="../infortunati-serie-a/index.html" style="color:#fff;">Infortunati</a>
                <a href="../rigoristi-serie-a/index.html">Rigoristi</a>
                <a href="../griglia-portieri/index.html">Griglia Portieri</a>
                <a href="../app.html" class="btn-launch-app">Lancia Dashboard Live 🚀</a>
            </nav>
        </div>
    </header>"""

new_pillar_nav = "{render_unified_header('../')}"
content = content.replace(old_inj_nav, new_pillar_nav)

# 4. In generate_rigoristi_pillar, replace header
old_rig_nav = """    <header class="site-nav">
        <div class="site-container site-nav-inner">
            <a href="../index.html" class="brand-logo">⚽ FANTA MASTER <span>AI</span></a>
            <nav class="nav-links">
                <a href="../infortunati-serie-a/index.html">Infortunati</a>
                <a href="../rigoristi-serie-a/index.html" style="color:#fff;">Rigoristi</a>
                <a href="../griglia-portieri/index.html">Griglia Portieri</a>
                <a href="../app.html" class="btn-launch-app">Lancia Dashboard Live 🚀</a>
            </nav>
        </div>
    </header>"""
content = content.replace(old_rig_nav, new_pillar_nav)

# 5. In generate_gk_pillar, replace header
old_gk_nav = """    <header class="site-nav">
        <div class="site-container site-nav-inner">
            <a href="../index.html" class="brand-logo">⚽ FANTA MASTER <span>AI</span></a>
            <nav class="nav-links">
                <a href="../infortunati-serie-a/index.html">Infortunati</a>
                <a href="../rigoristi-serie-a/index.html">Rigoristi</a>
                <a href="../griglia-portieri/index.html" style="color:#fff;">Griglia Portieri</a>
                <a href="../app.html" class="btn-launch-app">Lancia Dashboard Live 🚀</a>
            </nav>
        </div>
    </header>"""
content = content.replace(old_gk_nav, new_pillar_nav)

# Also update CTA banners in pillars to point to index.html with cohesive message
content = content.replace(
    """        <!-- CTA Box -->
        <section class="cta-banner">
            <h2>Vuoi simulare l'asta con {clean_html(full_name)}?</h2>
            <p>Accedi alla suite completa di Fanta Master AI con visualizzazione live di xG, xA, griglia portieri a 20 squadre e simulatore d'asta in tempo reale.</p>
            <a href="../../app.html" class="btn-launch-app" style="font-size:14px;padding:10px 22px;">Lancia Fanta Master AI Dashboard 🚀</a>
        </section>""",
    """        <!-- CTA Box -->
        <section class="cta-banner">
            <h2>Vuoi esplorare tutti i 532 calciatori e simulare l'asta?</h2>
            <p>Accedi al tabellone interattivo di Fanta Master AI con expected metrics (xG, xA, xFM), filtri avanzati e gestione della rosa in tempo reale.</p>
            <a href="../../index.html" class="nav-btn-icon" style="font-size:14px;padding:10px 22px;background:rgba(0,242,254,0.15);border-color:#00f2fe;color:#00f2fe;">Vai al Listone &amp; Dashboard Completa 🚀</a>
        </section>"""
)

with open(script_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: tools/build_seo_site.py patched with unified header across all pages!")
