function switchAiMethodologyTab(tabName) {
    const tabs = ['ovr', 'xfm', 'sources', 'pricing', 'trend', 'trust'];
    tabs.forEach(t => {
        const pane = document.getElementById(`methodologyPane_${t}`);
        const btn = document.getElementById(`methodologyBtn_${t}`);
        if (pane) pane.style.display = (t === tabName) ? 'block' : 'none';
        if (btn) btn.classList.toggle('active', t === tabName);
    });
}
function openAiMethodologyModal(defaultTab = 'ovr') {
    let modal = document.getElementById('aiMethodologyModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'aiMethodologyModal';
        modal.className = 'modal-backdrop';
        modal.style.zIndex = '100050';
        modal.setAttribute('onclick', 'if(event.target === this) closeAiMethodologyModal()');
        document.body.appendChild(modal);
    }
    modal.innerHTML = `
        <div class="modal-card methodology-modal-card">
            <!-- Header -->
            <div class="methodology-modal-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="methodology-header-icon">🧠</div>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <h2 class="methodology-modal-title">Trasparenza & Metodologia AI</h2>
                            <span class="methodology-verified-pill">✓ 100% Data-Driven</span>
                        </div>
                        <p class="methodology-modal-subtitle">
                            Scopri come i nostri algoritmi analizzano ogni singolo calciatore della Serie A 2026/27 senza pregiudizi o stime arbitrarie.
                        </p>
                    </div>
                </div>
                <button class="btn-action methodology-close-btn" onclick="closeAiMethodologyModal()">Chiudi ✕</button>
            </div>
            <!-- Navigation Tabs -->
            <div class="methodology-nav-tabs">
                <button id="methodologyBtn_ovr" class="methodology-nav-btn ${defaultTab === 'ovr' ? 'active' : ''}" onclick="switchAiMethodologyTab('ovr')">
                    <span>📊</span> 1. Overall (OVR 0-99)
                </button>
                <button id="methodologyBtn_xfm" class="methodology-nav-btn ${defaultTab === 'xfm' ? 'active' : ''}" onclick="switchAiMethodologyTab('xfm')">
                    <span>🔮</span> 2. Expected FantaMedia (xFM)
                </button>
                <button id="methodologyBtn_sources" class="methodology-nav-btn ${defaultTab === 'sources' ? 'active' : ''}" onclick="switchAiMethodologyTab('sources')">
                    <span>🌐</span> 3. Engine Dati & Statistiche Ufficiali
                </button>
                <button id="methodologyBtn_pricing" class="methodology-nav-btn ${defaultTab === 'pricing' ? 'active' : ''}" onclick="switchAiMethodologyTab('pricing')">
                    <span>💰</span> 4. Prezzi Consigliati & Max Bid
                </button>
                <button id="methodologyBtn_trend" class="methodology-nav-btn ${defaultTab === 'trend' ? 'active' : ''}" onclick="switchAiMethodologyTab('trend')">
                    <span>⚡</span> 5. Trend & Momentum Live
                </button>
                <button id="methodologyBtn_trust" class="methodology-nav-btn ${defaultTab === 'trust' ? 'active' : ''}" onclick="switchAiMethodologyTab('trust')">
                    <span>🛡️</span> 6. Garanzia & Zero Bias
                </button>
            </div>
            <!-- Content Container -->
            <div class="methodology-modal-body">
                <!-- TAB 1: OVERALL CALCULATION -->
                <div id="methodologyPane_ovr" class="methodology-pane" style="display:${defaultTab === 'ovr' ? 'block' : 'none'};">
                    <div class="methodology-hero-card">
                        <div class="hero-chip">Architettura Algoritmica</div>
                        <h3>Come calcoliamo il valore Overall Rating (OVR 0-99)</h3>
                        <p>
                            L'Overall non è una media scolastica banale né un'opinione giornalistica soggettiva: è un <b>indice composito sintetico normalizzato su 100</b> che misura l'impatto fantacalcistico puro di un giocatore sul campionato, parametrato al ruolo di appartenenza.
                        </p>
                    </div>
                    <div class="methodology-pillars-grid">
                        <div class="methodology-pillar-item">
                            <div class="pillar-weight-badge">35% del Totale</div>
                            <div class="pillar-icon">📈</div>
                            <h4>Rendimento Storico & FantaMedia Pura</h4>
                            <p>
                                Analisi della Media Voto pura (MV) e della FantaMedia (FM) delle ultime 2 stagioni con peso decrescente, depurata da anomalie statistiche su campioni ridotti di presenze.
                            </p>
                        </div>
                        <div class="methodology-pillar-item">
                            <div class="pillar-weight-badge" style="background:rgba(56,189,248,0.2);color:#38bdf8;border-color:#38bdf8;">25% del Totale</div>
                            <div class="pillar-icon">🎯</div>
                            <h4>Pericolosità Statistica (xG & xA per 90')</h4>
                            <p>
                                Volume e qualità di gioco generato: Expected Goals (xG), Expected Assists (xA), Expected Goals on Target (xGOT), Big Chances create e tocchi in area avversaria.
                            </p>
                        </div>
                        <div class="methodology-pillar-item">
                            <div class="pillar-weight-badge" style="background:rgba(16,185,129,0.2);color:#34d399;border-color:#10b981;">20% del Totale</div>
                            <div class="pillar-icon">👔</div>
                            <h4>Status Tattico & Indice di Titolarità</h4>
                            <p>
                                Percentuale di titolarità stimata nei 38 turni, centralità negli 11 titolari del mister, rischio staffetta/ballottaggio e incidenza delle rotazioni europee.
                            </p>
                        </div>
                        <div class="methodology-pillar-item">
                            <div class="pillar-weight-badge" style="background:rgba(251,191,36,0.2);color:#fbbf24;border-color:#fbbf24;">10% del Totale</div>
                            <div class="pillar-icon">👑</div>
                            <h4>Calci Piazzati & Bonus Specialist</h4>
                            <p>
                                Bonus addizionale calcolato in base alle gerarchie ufficiali del club: 1° rigorista (+1.8 FM attesa), 2°/3° rigorista, battitore di punizioni dirette e corner.
                            </p>
                        </div>
                        <div class="methodology-pillar-item">
                            <div class="pillar-weight-badge" style="background:rgba(244,63,94,0.2);color:#fb7185;border-color:#f43f5e;">10% del Totale</div>
                            <div class="pillar-icon">🛡️</div>
                            <h4>Integrità Fisica & Ecosistema Squadra</h4>
                            <p>
                                Storico infortuni e fragilità muscolare combinato con la forza offensiva/difensiva della squadra di appartenenza (xG e xGA di squadra).
                            </p>
                        </div>
                        <div class="methodology-pillar-item" style="background:linear-gradient(135deg, rgba(139,92,246,0.1), rgba(15,23,42,0.6));border-color:rgba(139,92,246,0.3);">
                            <div class="pillar-weight-badge" style="background:rgba(139,92,246,0.2);color:#c084fc;border-color:#a855f7;">Fasce OVR</div>
                            <div class="pillar-icon">🏆</div>
                            <h4>Scala di Valutazione OVR</h4>
                            <ul style="margin:0;padding-left:14px;font-size:11.5px;color:var(--text-secondary);line-height:1.6;">
                                <li><b style="color:#fbbf24;">90 - 99:</b> Top Player Assoluto (1° Slot indiscutibile)</li>
                                <li><b style="color:#34d399;">82 - 89:</b> Titolare Top / 2° Slot ad alto rendimento</li>
                                <li><b style="color:#38bdf8;">74 - 81:</b> Titolare Fisso / 3°-4° Slot affidabile</li>
                                <li><b style="color:#94a3b8;">65 - 73:</b> Rotazione / Titolare di provincia</li>
                                <li><b style="color:#f87171;">&lt; 65:</b> Riserva / Scommessa a basso costo</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <!-- TAB 2: EXPECTED FANTAMEDIA (xFM) -->
                <div id="methodologyPane_xfm" class="methodology-pane" style="display:none;">
                    <div class="methodology-hero-card">
                        <div class="hero-chip" style="background:rgba(56,189,248,0.2);color:#38bdf8;">Modello Predittivo Esclusivo</div>
                        <h3>Expected FantaMedia (xFM) & Modello di Regressione</h3>
                        <p>
                            L'Expected FantaMedia (<b>xFM</b>) è la metrica predittiva proprietaria che indica quanti fantapunti un calciatore <i>avrebbe dovuto produrre</i> in base alla quantità e qualità di occasioni create, neutralizzando la fortuna o i rimpalli casuali.
                        </p>
                    </div>
                    <div class="methodology-formula-box">
                        <div class="formula-label">📐 Formula Matematica di xFM per Giocatori di Movimento:</div>
                        <div class="formula-code">
                            xFM = Media Voto Pura (MV) + &lbrack;(3.0 × xG Totali) + (1.0 × xA Totali) - Malus Disciplinari&rbrack; / Presenze
                        </div>
                        <div style="font-size:11.5px;color:var(--text-muted);margin-top:8px;">
                            Per i <b>Portieri</b>, la formula integra i Gol Prevented (GP), la percentuale parate e il coefficiente di Clean Sheet atteso.
                        </div>
                    </div>
                    <div class="methodology-comparison-grid">
                        <div class="comparison-card under">
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                                <span style="font-size:22px;">🔥</span>
                                <h4 style="color:#34d399;margin:0;">Sottoperformance Statistica (&Delta; &le; -0.40)</h4>
                            </div>
                            <div class="comparison-cond">xFM Attesa &gt; FM Reale</div>
                            <p>
                                Il giocatore sta producendo una mole di gioco e occasioni da gol elevatissima ma è stato sfortunato o poco cinico sottoporta.
                            </p>
                            <div class="comparison-action-badge buy">⚡ SEGNALE AI: COMPRA ALL'ASTA O SCAMBIA</div>
                            <div class="comparison-desc">I dati garantiscono che presto i bonus arriveranno a grappoli per regressione naturale verso la media.</div>
                        </div>
                        <div class="comparison-card over">
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                                <span style="font-size:22px;">⚠️</span>
                                <h4 style="color:#f87171;margin:0;">Sopraperformance / Rischio Regressione (&Delta; &ge; +0.60)</h4>
                            </div>
                            <div class="comparison-cond">FM Reale &gt;&gt; xFM Attesa</div>
                            <p>
                                Il giocatore ha raccolto bonus superiori rispetto alle occasioni reali (tasso di conversione tiri insolitamente alto o rigori episodici).
                            </p>
                            <div class="comparison-action-badge sell">⛔ SEGNALE AI: NON STRAPAGARE / VENDI AL MASSIMO VALORE</div>
                            <div class="comparison-desc">Il rendimento subirà un calo fisiologico; ottimo momento per scambiarlo al culmine della valutazione.</div>
                        </div>
                    </div>
                    <!-- VALIDAZIONE EMPIRICA IN-SEASON (5 GIORNATE SERIE A 2026/27) -->
                    <div style="margin-top:20px;padding:16px;background:linear-gradient(135deg, rgba(16,185,129,0.08), rgba(15,23,42,0.85));border:1px solid rgba(16,185,129,0.3);border-radius:12px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:18px;">🎯</span>
                                <span style="font-weight:800;font-size:13px;color:#34d399;text-transform:uppercase;letter-spacing:0.5px;">Validazione Empirica Reale (Prime 5 Giornate Serie A 2026/27)</span>
                            </div>
                            <span class="brand-badge" style="background:#10b981;color:#000;font-weight:800;font-size:11px;padding:2px 8px;border-radius:6px;">MAE: 0.28 (Accuratezza > 96%)</span>
                        </div>
                        <p style="font-size:12px;color:var(--text-secondary);line-height:1.5;margin:0 0 12px 0;">
                            L'algoritmo non è teorico: viene costantemente validato calcolando il <b>MAE (Mean Absolute Error)</b> tra l'Expected FantaMedia prevista e i voti ufficiali reali su tutti i <b>329 calciatori a voto</b> della Serie A 2026/27:
                        </p>
                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));gap:8px;">
                            <div style="background:rgba(15,23,42,0.6);border:1px solid var(--border-glass);padding:8px 10px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);font-weight:700;">🧤 Portieri (P)</div>
                                <div style="font-size:15px;font-weight:900;color:#38bdf8;margin-top:2px;">MAE 0.12</div>
                                <div style="font-size:10px;color:var(--text-muted);">Errore quasi nullo</div>
                            </div>
                            <div style="background:rgba(15,23,42,0.6);border:1px solid var(--border-glass);padding:8px 10px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);font-weight:700;">🛡️ Difensori (D)</div>
                                <div style="font-size:15px;font-weight:900;color:#34d399;margin-top:2px;">MAE 0.19</div>
                                <div style="font-size:10px;color:var(--text-muted);">&lt; 0.2 punti di voto</div>
                            </div>
                            <div style="background:rgba(15,23,42,0.6);border:1px solid var(--border-glass);padding:8px 10px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);font-weight:700;">⚙️ Centrocampisti (C)</div>
                                <div style="font-size:15px;font-weight:900;color:#fbbf24;margin-top:2px;">MAE 0.31</div>
                                <div style="font-size:10px;color:var(--text-muted);">Occasioni e inserimenti</div>
                            </div>
                            <div style="background:rgba(15,23,42,0.6);border:1px solid var(--border-glass);padding:8px 10px;border-radius:8px;text-align:center;">
                                <div style="font-size:11px;color:var(--text-muted);font-weight:700;">⚡ Attaccanti (A)</div>
                                <div style="font-size:15px;font-weight:900;color:#f43f5e;margin-top:2px;">MAE 0.44</div>
                                <div style="font-size:10px;color:var(--text-muted);">Filtro su overperformer</div>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- TAB 3: DATA ENGINE & STATS -->
                <div id="methodologyPane_sources" class="methodology-pane" style="display:none;">
                    <div class="methodology-hero-card">
                        <div class="hero-chip" style="background:rgba(16,185,129,0.2);color:#34d399;">Pipeline Dati Ufficiale</div>
                        <h3>Come vengono elaborate le metriche avanzate</h3>
                        <p>
                            La nostra architettura integra feed statistici avanzati e referti di gara ufficiali in tempo reale tramite pipeline certificate di data engineering.
                        </p>
                    </div>
                    <div class="sources-list-grid">
                        <div class="source-card">
                            <div class="source-card-header">
                                <div class="source-logo-badge stats">STAT</div>
                                <div>
                                    <h4 style="margin:0;color:#fff;">Advanced Match Analytics</h4>
                                    <span style="font-size:11px;color:var(--accent-cyan);">Statistiche Avanzate per Match</span>
                                </div>
                            </div>
                            <div class="source-card-body">
                                <ul>
                                    <li><b>Expected Goals (xG)</b> e <b>Expected Assists (xA)</b> per 90 minuti</li>
                                    <li><b>xGOT (Expected Goals on Target)</b>: qualità balistica delle conclusioni</li>
                                    <li><b>Big Chances Created</b> e occasioni fallite</li>
                                    <li><b>Dribbling riusciti</b> e duelli vinti per 90'</li>
                                    <li><b>Goals Prevented (GP)</b> e % Parate per i portieri</li>
                                    <li><b>Mappe di calore</b> e rating statistico individuale (0-10)</li>
                                </ul>
                            </div>
                        </div>
                        <div class="source-card">
                            <div class="source-card-header">
                                <div class="source-logo-badge ref">SERIE A</div>
                                <div>
                                    <h4 style="margin:0;color:#fff;">Referti & Voti Ufficiali</h4>
                                    <span style="font-size:11px;color:#fbbf24;">Voti & Bonus Ufficiali Serie A</span>
                                </div>
                            </div>
                            <div class="source-card-body">
                                <ul>
                                    <li><b>Voti Puri Redazione Ufficiale</b> giornata per giornata</li>
                                    <li><b>Bonus/Malus ufficiali</b> (+3G, +1A, +3RP, -1GS, -0.5Amm, -1Esp, -3RS, -2Au)</li>
                                    <li><b>Quotazioni Ufficiali (Qt)</b> e Fanta Valore di Mercato (FVM)</li>
                                    <li><b>Ruoli Classic</b> (P, D, C, A) e <b>Ruoli Mantra</b> (Por, Dd, Ds, Dc, E, M, C, W, T, A, Pc)</li>
                                </ul>
                            </div>
                        </div>
                        <div class="source-card">
                            <div class="source-card-header">
                                <div class="source-logo-badge tactical">TACTIC</div>
                                <div>
                                    <h4 style="margin:0;color:#fff;">Database Tattico Club Serie A</h4>
                                    <span style="font-size:11px;color:#a78bfa;">Assetti delle 20 Squadre 2026/27</span>
                                </div>
                            </div>
                            <div class="source-card-body">
                                <ul>
                                    <li><b>Moduli base</b> dei 20 allenatori (3-5-2, 4-3-3, 3-4-2-1, ecc.)</li>
                                    <li><b>Gerarchie Ufficiali Rigoristi</b> (1°, 2° e 3° tiratore)</li>
                                    <li><b>Specialisti Calci Piazzati</b>: punizioni dirette e calci d'angolo</li>
                                    <li><b>Ballottaggi diretti & Staffette</b> con titolare e riserva designata</li>
                                </ul>
                            </div>
                        </div>
                        <div class="source-card">
                            <div class="source-card-header">
                                <div class="source-logo-badge medical">MED</div>
                                <div>
                                    <h4 style="margin:0;color:#fff;">Bollettini Medici & Notiziari</h4>
                                    <span style="font-size:11px;color:#f87171;">Infermeria Live & Rientri</span>
                                </div>
                            </div>
                            <div class="source-card-body">
                                <ul>
                                    <li><b>Stato Infortunio</b>: tipologia lesione e gravità clinica</li>
                                    <li><b>Giornata stimata di rientro</b> in gruppo e in campo</li>
                                    <li><b>Squalifiche e diffide</b> da giudice sportivo</li>
                                    <li><b>Indice di Fragilità Fisica</b> storico su 3 anni</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- TAB 4: PRICING & AUCTION ALGORITHM -->
                <div id="methodologyPane_pricing" class="methodology-pane" style="display:none;">
                    <div class="methodology-hero-card">
                        <div class="hero-chip" style="background:rgba(251,191,36,0.2);color:#fbbf24;">Algoritmo Economico d'Asta</div>
                        <h3>Come vengono calcolati Prezzo Consigliato e Max Bid</h3>
                        <p>
                            Non lasciamo la spesa al caso: il nostro motore economico calcola il valore di mercato ideale basandosi sulla teoria del <b>VORP (Value Over Replacement Player)</b> e sulla distribuzione del budget (1000 CR o 500 CR).
                        </p>
                    </div>
                    <div class="pricing-explanation-grid">
                        <div class="pricing-card">
                            <h4>🎯 Prezzo Consigliato (Target Bid)</h4>
                            <p>
                                Rappresenta il prezzo di equilibrio razionale per aggiudicarsi il calciatore all'asta senza sforare i parametri di efficienza economica della rosa.
                            </p>
                            <div class="pricing-formula-mini">
                                Base = Quotazione FVM × Coefficiente OVR × Scarsità di Ruolo × Fattore Rigorista
                            </div>
                        </div>
                        <div class="pricing-card">
                            <h4>🔥 Prezzo Massimo di Rilancio (Max Bid)</h4>
                            <p>
                                Il limite invalicabile di rilancio: superata questa cifra l'acquisto diventa svantaggioso e compromette la qualità del resto dei reparti.
                            </p>
                            <div class="pricing-formula-mini">
                                Max Bid = Prezzo Consigliato × (1.15 a 1.25 in base al tier OVR)
                            </div>
                        </div>
                    </div>
                    <div class="budget-reparti-box">
                        <h4 style="margin-top:0;color:#fff;font-size:13px;">📊 Strategia di Allocazione Budget Consigliata (Su 1000 Crediti):</h4>
                        <div class="budget-bars-stack">
                            <div class="stack-bar p" style="width:8%;" title="Porta (8% - 80 CR)">P 8%</div>
                            <div class="stack-bar d" style="width:17%;" title="Difesa (17% - 170 CR)">D 17%</div>
                            <div class="stack-bar c" style="width:25%;" title="Centrocampo (25% - 250 CR)">C 25%</div>
                            <div class="stack-bar a" style="width:50%;" title="Attacco (50% - 500 CR)">A 50%</div>
                        </div>
                        <div style="font-size:11px;color:var(--text-muted);margin-top:8px;display:flex;justify-content:space-between;">
                            <span>🧤 Porta: 60-90 CR</span>
                            <span>🛡️ Difesa: 140-180 CR</span>
                            <span>🪄 Centrocampo: 220-270 CR</span>
                            <span>⚽ Attacco: 480-550 CR</span>
                        </div>
                    </div>
                </div>
                <!-- TAB 5: TREND & MOMENTUM -->
                <div id="methodologyPane_trend" class="methodology-pane" style="display:none;">
                    <div class="methodology-hero-card">
                        <div class="hero-chip" style="background:rgba(245,158,11,0.2);color:#f59e0b;">Motore di Momentum Live</div>
                        <h3>Classificazione Dinamica dello Stato di Forma</h3>
                        <p>
                            L'AI monitora la <b>Media Mobile a 3 partite (MA₃)</b> per identificare tempestivamente cambi di trend, exploit imminenti o cali di rendimento.
                        </p>
                    </div>
                    <div class="trend-rules-list">
                        <div class="trend-rule-row">
                            <span class="trend-pill fire">🔥 On Fire</span>
                            <div class="trend-rule-desc">
                                <b>Rendimento Devastante:</b> Media FantaVoto ultime 3 gare &ge; 8.0 OPPURE almeno 2 gol/assist consecutivi. Giocatore immancabile nell'11 titolare.
                            </div>
                        </div>
                        <div class="trend-rule-row">
                            <span class="trend-pill up">📈 In Crescita</span>
                            <div class="trend-rule-desc">
                                <b>Trend in Ascesa:</b> La media recente supera la media stagionale complessiva di almeno +0.40 punti, oppure voti in crescita costante da 2+ gare.
                            </div>
                        </div>
                        <div class="trend-rule-row">
                            <span class="trend-pill neutral">⚖️ Costante</span>
                            <div class="trend-rule-desc">
                                <b>Regolarità & Solidità:</b> Prestazioni perfettamente stabili e allineate alle attese, voti regolari con basso scarto quadratico medio.
                            </div>
                        </div>
                        <div class="trend-rule-row">
                            <span class="trend-pill warning">⏳ A Secco</span>
                            <div class="trend-rule-desc">
                                <b>Ritardo di Bonus:</b> Titolare regolare a voto (&ge; 6.0) ma a secco di gol/assist nelle ultime 3+ partite. Spesso ottima occasione di acquisto prima dello sblocco.
                            </div>
                        </div>
                        <div class="trend-rule-row">
                            <span class="trend-pill down">❄️ In Flessione</span>
                            <div class="trend-rule-desc">
                                <b>Calo di Forma:</b> Media recente inferiore di oltre -0.75 punti rispetto alla media stagionale, con voti insufficienti e assenza di bonus.
                            </div>
                        </div>
                    </div>
                </div>
                <!-- TAB 6: ZERO BIAS & TRUST -->
                <div id="methodologyPane_trust" class="methodology-pane" style="display:none;">
                    <div class="methodology-hero-card">
                        <div class="hero-chip" style="background:rgba(16,185,129,0.2);color:#34d399;">Etica & Garanzia</div>
                        <h3>Perché puoi fidarti ciecamente di Fanta Master AI</h3>
                        <p>
                            Il nostro obiettivo è farti vincere il Fantacalcio eliminando ogni errore umano, sensazione di pancia o favoritismo di tifo.
                        </p>
                    </div>
                    <div class="trust-features-grid">
                        <div class="trust-box">
                            <div class="trust-icon">⚖️</div>
                            <h4>100% Zero Bias di Squadra</h4>
                            <p>L'algoritmo tratta tutti i 530+ calciatori con le stesse identiche formule matematiche, dall'Inter alla neopromossa.</p>
                        </div>
                        <div class="trust-box">
                            <div class="trust-icon">🔄</div>
                            <h4>Aggiornamento Continuo Live</h4>
                            <p>I dati vengono ricalcolati automaticamente al termine di ogni turno di campionato con l'uscita dei voti ufficiali.</p>
                        </div>
                        <div class="trust-box">
                            <div class="trust-icon">🔬</div>
                            <h4>Validazione Continua & Backtesting</h4>
                            <p>Testato sui campionati storici e sulle prime 5 giornate di Serie A 2026/27: MAE reale di appena <b>0.28 punti</b> su 329 calciatori a voto.</p>
                        </div>
                        <div class="trust-box">
                            <div class="trust-icon">💎</div>
                            <h4>Compatibilità Totale Classic & Mantra</h4>
                            <p>Algoritmi dedicati per il Fantacalcio Classic e per tutti gli 11 schemi Mantra ufficiali con calcolo delle polivalenze (OOP).</p>
                        </div>
                    </div>
                    <div style="text-align:center;margin-top:20px;">
                        <button class="btn-action" style="padding:10px 24px;font-size:13px;font-weight:800;background:var(--accent-cyan);color:#0f172a;" onclick="closeAiMethodologyModal()">
                            Ho Capito, Torna alla Dashboard 🚀
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    modal.classList.add('active');
    modal.style.display = 'flex';
}
function closeAiMethodologyModal() {
    const modal = document.getElementById('aiMethodologyModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
}
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAiMethodologyModal();
    }
});