#!/usr/bin/env python3
"""
tools/seo_footer.py
===================
Componente unificato per Footer & Mobile Bottom Navigation Bar per tutte le pagine del portale.
Garantisce coerenza di navigazione mobile e desktop tra SPA e pagine SEO statiche.
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
                    <div class="footer-social-row" style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
                        <a href="https://t.me/fantamasterai" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:6px;background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.25);color:#38bdf8;padding:4px 10px;border-radius:20px;font-size:11.5px;font-weight:700;text-decoration:none;">
                            <span>✈️</span> Telegram Ufficiale
                        </a>
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
                        <li><a href="{rel_path}chi-schiero/" class="footer-link">⚔️ Head-to-Head 1vs1</a></li>
                    </ul>
                </div>

                <div class="footer-links-col">
                    <div class="footer-heading">Community &amp; Note Legali</div>
                    <ul class="footer-nav-list">
                        <li><a href="https://t.me/fantamasterai" target="_blank" rel="noopener" class="footer-link" style="color:#38bdf8;font-weight:800;">📲 Canale Telegram Ufficiale</a></li>
                        <li><a href="https://www.instagram.com/fantamasterai" target="_blank" rel="noopener" class="footer-link" style="color:#f43f5e;font-weight:800;">📸 Profilo Instagram Ufficiale</a></li>
                        <li><a href="{rel_path}privacy-policy/" class="footer-link" id="footer-privacy-link">🔒 Privacy Policy (GDPR)</a></li>
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
                    <a href="{rel_path}privacy-policy/" class="footer-bottom-link">Privacy Policy</a>
                    <span class="footer-sep">•</span>
                    <a href="mailto:info@fantamasterai.it" class="footer-bottom-link">info@fantamasterai.it</a>
                </div>
            </div>
        </div>
    </footer>

    <!-- MOBILE BOTTOM NAVIGATION (Persistent Across All Pages: Probabili | Chi Schiero | Consigli AI | La Tua Rosa | Menu) -->
    <nav class="mobile-bottom-nav" id="mobileBottomNav">
        <a href="{rel_path}probabili-formazioni/" class="mobile-nav-item" id="mobNavProbabili">
            <span class="mob-icon">⚽</span>
            <span class="mob-label">Probabili</span>
        </a>
        <a href="{rel_path}chi-schiero/" class="mobile-nav-item" id="mobNavChiSchiero">
            <span class="mob-icon">⚔️</span>
            <span class="mob-label">Chi Schiero</span>
        </a>
        <a href="{rel_path}consigli-fantacalcio/" class="mobile-nav-item" id="mobNavAdvice">
            <span class="mob-icon">🎯</span>
            <span class="mob-label">Consigli AI</span>
        </a>
        <a href="{rel_path}?openSquad=1" class="mobile-nav-item" id="mobNavSquad">
            <span class="mob-icon">📋</span>
            <span class="mob-label">La Tua Rosa</span>
        </a>
        <button type="button" class="mobile-nav-item" id="mobNavMenu" onclick="openMobileMenuModal()" aria-label="Apri menu completo">
            <span class="mob-icon">☰</span>
            <span class="mob-label">Menu</span>
        </button>
    </nav>

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
                <!-- HOME PAGE -->
                <div class="mobile-menu-section" style="padding:0;">
                    <div class="mobile-menu-links">
                        <a href="{rel_path}" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.16);color:#fff;font-weight:900;">🏠 Torna alla Home Page</a>
                    </div>
                </div>

                <!-- FASE 1: GIORNATA & FORMAZIONE -->
                <div class="mobile-menu-section" style="border:1px solid rgba(16,185,129,0.28);background:rgba(16,185,129,0.05);border-radius:12px;padding:12px;">
                    <div class="mobile-menu-section-title" style="color:#34d399;font-weight:900;"><span>⚽</span> FASE 1: GIORNATA &amp; FORMAZIONE (11 Titolari)</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}?openSquad=1" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(16,185,129,0.18);border-color:rgba(16,185,129,0.45);color:#34d399;font-weight:800;">📋 La Mia Rosa &amp; Miglior 11 AI</a>
                        <a href="{rel_path}probabili-formazioni/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(56,189,248,0.15);border-color:rgba(56,189,248,0.4);color:#38bdf8;font-weight:800;">⚽ Probabili Formazioni di Giornata (4 Fonti)</a>
                        <a href="{rel_path}chi-schiero/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(168,85,247,0.15);border-color:rgba(168,85,247,0.4);color:#e9d5ff;font-weight:800;">⚔️ Tool &ldquo;Chi Schiero?&rdquo; (Dubbio 1vs1)</a>
                        <a href="{rel_path}consigli-fantacalcio/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🎯 Consigliati di Giornata &amp; Top 11</a>
                        <a href="{rel_path}infortunati-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;color:#fca5a5;">🩺 Infortunati, Squalificati &amp; Rientri</a>
                        <a href="{rel_path}statistiche-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">📊 Statistiche Serie A (xG, xA, xFM)</a>
                        <a href="{rel_path}top-flop/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">⚡ Top &amp; Flop di Giornata</a>
                        <a href="{rel_path}match-report/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">📑 Match Reports &amp; Voti Ufficiali</a>
                    </div>
                </div>

                <!-- FASE 2: MERCATO & ASTA -->
                <div class="mobile-menu-section" style="border:1px solid rgba(245,158,11,0.28);background:rgba(245,158,11,0.05);border-radius:12px;padding:12px;">
                    <div class="mobile-menu-section-title" style="color:#fbbf24;font-weight:900;"><span>💰</span> FASE 2: MERCATO &amp; ASTA (Creazione Squadra)</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}listone/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(245,158,11,0.16);border-color:rgba(245,158,11,0.4);color:#fde68a;font-weight:800;">📋 Listone Calciatori &amp; Quotazioni FVM</a>
                        <a href="{rel_path}probabili-formazioni/inter/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;color:#fcd34d;font-weight:700;">🏟️ Top 11 &amp; Gerarchie Stagionali (20 Squadre)</a>
                        <a href="{rel_path}griglia-portieri/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🧤 Griglia Portieri &amp; Incroci 38/38</a>
                        <a href="{rel_path}rigoristi-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🎯 Rigoristi, Punizioni &amp; Calci Piazzati</a>
                        <a href="{rel_path}scommesse-talenti/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🔮 Gemme Nascoste &amp; Scommesse Low-Cost</a>
                        <a href="{rel_path}confronto-calciatori/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">⚖️ Confronto Calciatori (Scambi &amp; Asta)</a>
                        <a href="{rel_path}top-11-ai/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🤖 5 Squadre Perfette AI (Budget)</a>
                    </div>
                </div>

                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🏠</span> Home Page</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🏠 Torna alla Home Page</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
    function openMobileMenuModal() {{
        var m = document.getElementById('mobileMenuModal');
        if (m) m.style.display = 'flex';
    }}
    function closeMobileMenuModal() {{
        var m = document.getElementById('mobileMenuModal');
        if (m) m.style.display = 'none';
    }}
    (function() {{
        var p = window.location.pathname || '';
        var activeId = null;
        if (p.indexOf('/chi-schiero') !== -1) activeId = 'mobNavChiSchiero';
        else if (p.indexOf('/consigli-fantacalcio') !== -1) activeId = 'mobNavAdvice';
        else if (p.indexOf('/probabili-formazioni') !== -1) activeId = 'mobNavProbabili';
        if (activeId) {{
            var el = document.getElementById(activeId);
            if (el) el.classList.add('active');
        }}
    }})();
    </script>
    """
