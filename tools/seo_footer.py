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

    <!-- MOBILE BOTTOM NAVIGATION (Persistent Across All Pages) -->
    <nav class="mobile-bottom-nav" id="mobileBottomNav">
        <a href="{rel_path}" class="mobile-nav-item" id="mobNavHome">
            <span class="mob-icon">🏠</span>
            <span class="mob-label">Home</span>
        </a>
        <a href="{rel_path}listone/" class="mobile-nav-item" id="mobNavAuction">
            <span class="mob-icon">📋</span>
            <span class="mob-label">Listone</span>
        </a>
        <a href="{rel_path}probabili-formazioni/" class="mobile-nav-item" id="mobNavProbabili">
            <span class="mob-icon">⚽</span>
            <span class="mob-label">Probabili</span>
        </a>
        <a href="{rel_path}consigli-fantacalcio/" class="mobile-nav-item" id="mobNavAdvice">
            <span class="mob-icon">🎯</span>
            <span class="mob-label">Consigli AI</span>
        </a>
        <button type="button" class="mobile-nav-item" id="mobNavMenu" onclick="openMobileMenuModal()">
            <span class="mob-icon">☰</span>
            <span class="mob-label">Menu</span>
        </button>
    </nav>

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
                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🏠</span> Home Page</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🏠 Home &amp; Leader Serie A</a>
                    </div>
                </div>

                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>📋</span> Listone & Probabili</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}probabili-formazioni/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(56,189,248,0.15);border-color:rgba(56,189,248,0.4);color:#38bdf8;font-weight:800;">⚽ Probabili Formazioni (4 Fonti)</a>
                        <a href="{rel_path}listone/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">📋 Listone Calciatori & OVR</a>
                    </div>
                </div>

                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>📖</span> Statistiche & Analisi</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}statistiche-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">📊 Statistiche Serie A & xG</a>
                        <a href="{rel_path}top-flop/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">⚡ Top & Flop Giornata</a>
                        <a href="{rel_path}match-report/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">📑 Match Reports &amp; Tabellini</a>
                        <a href="{rel_path}football-analytics/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">📈 Matrice Analytics</a>
                        <a href="{rel_path}chi-schiero/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">⚔️ Matchup 1vs1 (Chi Schiero)</a>
                        <a href="{rel_path}griglia-portieri/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🧤 Griglia Portieri 38/38</a>
                        <a href="{rel_path}rigoristi-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🎯 Rigoristi & Tiratori</a>
                        <a href="{rel_path}infortunati-serie-a/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🏥 Infortunati & Rientri</a>
                    </div>
                </div>

                <div class="mobile-menu-section">
                    <div class="mobile-menu-section-title"><span>🤖</span> Strumenti AI</div>
                    <div class="mobile-menu-links">
                        <a href="{rel_path}consigli-fantacalcio/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;background:rgba(0,230,118,0.15);border-color:rgba(0,230,118,0.4);color:#00e676;font-weight:800;">🎯 Consigli Formazione & AI Advice</a>
                        <a href="{rel_path}scommesse-talenti/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">💎 Scommesse & Talenti Low-Cost</a>
                        <a href="{rel_path}ottimizzatore-formazione/" class="mobile-menu-link-btn" style="text-decoration:none;display:flex;align-items:center;gap:8px;">🧠 Ottimizzatore Formazione 2D</a>
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
    </script>
    """
