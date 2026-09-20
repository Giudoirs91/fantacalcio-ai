// --- leagues_hub.js ---
// Gestione Home Hub, visualizzazione campionati multi-lega e commutazione rapida

function renderHomeHubView() {
    const container = document.getElementById('viewHomeHub');
    if (!container) return;

    const leagues = LeaguesManager.getAll();
    const activeId = LeaguesManager.getActiveId();

    const cardsHtml = leagues.map(l => {
        const isActive = (l.id === activeId);
        
        // Calcola statistiche rosa
        const pCount = (l.slots?.P?.players?.length || 0) +
                       (l.slots?.D?.players?.length || 0) +
                       (l.slots?.C?.players?.length || 0) +
                       (l.slots?.A?.players?.length || 0);
        
        const maxSlots = l.rules?.maxRosterSize || ((l.systemMode === 'mantra') ? 30 : 25);
        const spent = l.budgetSpent || 0;
        const total = l.budgetTotal || 1000;
        const remaining = total - spent;
        const rivalsCount = Object.keys(l.rivals || {}).length;

        // Calcolo OVR medio della rosa
        const allBought = [
            ...(l.slots?.P?.players || []),
            ...(l.slots?.D?.players || []),
            ...(l.slots?.C?.players || []),
            ...(l.slots?.A?.players || [])
        ];
        const avgOvr = allBought.length > 0 ? (allBought.reduce((s, p) => s + (p.ovr || 70), 0) / allBought.length).toFixed(1) : '-';

        return `
            <div class="league-card ${isActive ? 'active-league' : ''}">
                <div class="league-card-header">
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <h3 class="league-title">${l.name}</h3>
                            ${isActive ? `<span class="active-badge">✓ ATTIVA</span>` : ''}
                        </div>
                        <div class="league-meta-tags">
                            <span class="meta-tag ${l.systemMode}">${l.systemMode === 'mantra' ? '🔮 Mantra' : '⚡ Classic'}</span>
                            <span class="meta-tag">💰 ${total} CR</span>
                            <span class="meta-tag">🏟️ ${rivalsCount + 1} Squadre</span>
                            ${l.rules?.modificatoreDifesa ? `<span class="meta-tag" style="border-color:rgba(59,130,246,0.4);color:#60a5fa;">🛡️ Mod. Difesa</span>` : ''}
                            <span class="meta-tag" style="border-color:rgba(168,85,247,0.4);color:#c084fc;">👥 ${maxSlots} Slot</span>
                        </div>
                    </div>

                    <div style="display:flex;gap:6px;">
                        <button class="icon-btn" title="Modifica impostazioni lega" onclick="event.stopPropagation(); openEditLeagueModal('${l.id}')">⚙️</button>
                        ${leagues.length > 1 ? `<button class="icon-btn danger" title="Elimina lega" onclick="event.stopPropagation(); promptDeleteLeague('${l.id}')">🗑️</button>` : ''}
                    </div>
                </div>

                <!-- INFO ROSA UTENTE -->
                <div class="league-team-box">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-weight:700;font-size:13px;color:#fff;">🌟 ${l.myTeamName || 'La Mia Rosa'}</span>
                        <span style="font-size:11.5px;color:var(--text-muted);">OVR Rosa: <b style="color:var(--accent-cyan);">${avgOvr}</b></span>
                    </div>

                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
                        <span style="color:var(--text-muted);">Calciatori:</span>
                        <b style="color:#fff;">${pCount} / ${maxSlots}</b>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:${Math.min(100, (pCount / maxSlots) * 100)}%;"></div>
                    </div>

                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-top:8px;">
                        <span style="color:var(--text-muted);">Budget Residuo:</span>
                        <b style="color:#34d399;">${remaining} CR <span style="font-size:10.5px;color:var(--text-muted);">(spesi ${spent})</span></b>
                    </div>
                </div>

                <!-- FOOTER ACTIONS -->
                <div class="league-card-footer">
                    <button class="btn-action enter-btn ${isActive ? 'active' : ''}" onclick="selectAndEnterLeague('${l.id}')">
                        ${isActive ? '⚽ Sei Già in Questa Lega' : '⚽ Entra nel Campionato'}
                    </button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div class="home-hub-container">
            <!-- HERO WELCOME BANNER -->
            <div class="home-hero">
                <div class="hero-left">
                    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                        <span style="font-size:38px;">🏆</span>
                        <div>
                            <h1 class="hero-title">I Tuoi Campionati & Leghe</h1>
                            <div class="hero-sub">
                                Ogni lega è un mondo a sé: rose, budget, rivali e strategie completamente indipendenti
                            </div>
                        </div>
                    </div>
                </div>

                <div class="hero-actions">
                    <button class="btn-action hero-btn primary" onclick="openCreateLeagueModal()">
                        <span>➕ Crea Nuova Lega</span>
                    </button>
                    <button class="btn-action hero-btn secondary" onclick="openXlsxImportModal()">
                        <span>📥 Importa da Excel (.xlsx)</span>
                    </button>
                </div>
            </div>

            <!-- LEAGUES GRID -->
            <div class="leagues-grid">
                ${cardsHtml}

                <!-- ADD LEAGUE CARD -->
                <div class="league-card add-card" onclick="openCreateLeagueModal()">
                    <div style="font-size:42px;margin-bottom:8px;">➕</div>
                    <h3 style="margin:0;font-size:16px;color:#fff;">Crea un Altro Campionato</h3>
                    <div style="font-size:11.5px;color:var(--text-muted);margin-top:4px;text-align:center;">
                        Aggiungi una nuova lega per un altro gruppo di amici (Classic o Mantra)
                    </div>
                </div>
            </div>
        </div>
    `;
}

function selectAndEnterLeague(leagueId) {
    LeaguesManager.switchLeague(leagueId);
    switchTab('auction');
    if (typeof showSyncToast === 'function') {
        const active = LeaguesManager.getActive();
        showSyncToast(`⚽ Benvenuto in "${active ? active.name : 'Lega'}"!`);
    }
}

// Rendering del selettore a tendina nell'Header superiore
function renderHeaderLeagueDropdown() {
    const container = document.getElementById('headerLeagueSelectorContainer') || document.getElementById('leagueSelectorDropdown');
    if (!container) return;

    const leagues = LeaguesManager.getAll();
    const active = LeaguesManager.getActive();
    if (!active) return;

    const itemsHtml = leagues.map(l => {
        const isCurrent = (l.id === active.id);
        return `
            <a href="javascript:void(0)" class="dropdown-item ${isCurrent ? 'active' : ''}" onclick="LeaguesManager.switchLeague('${l.id}')">
                <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
                    <span>${isCurrent ? '✓ ' : ''}${l.name}</span>
                    <span style="font-size:10px;color:var(--text-muted);margin-left:8px;">[${l.systemMode.toUpperCase()}]</span>
                </div>
            </a>
        `;
    }).join('');

    container.innerHTML = `
        <div class="nav-dropdown">
            <button class="header-league-btn" title="Cambia campionato">
                <span style="font-size:14px;">🏆</span>
                <span class="league-btn-name">${active.name}</span>
                <span style="font-size:9.5px;padding:2px 6px;border-radius:4px;font-weight:800;background:${active.systemMode === 'mantra' ? 'rgba(0,242,254,0.18)' : 'rgba(251,191,36,0.18)'};color:${active.systemMode === 'mantra' ? 'var(--accent-cyan)' : '#fbbf24'};border:1px solid ${active.systemMode === 'mantra' ? 'rgba(0,242,254,0.4)' : 'rgba(251,191,36,0.4)'};">${active.systemMode === 'mantra' ? '🔮 MANTRA' : '⚡ CLASSIC'}</span>
                <span class="caret">▾</span>
            </button>
            <div class="nav-dropdown-menu">
                <div class="dropdown-header">I Tuoi Campionati</div>
                ${itemsHtml}
                <div class="dropdown-divider"></div>
                <a href="javascript:void(0)" class="dropdown-item" onclick="openCreateLeagueModal()">➕ Crea Nuova Lega</a>
                <a href="javascript:void(0)" class="dropdown-item" onclick="openXlsxImportModal()">📥 Importa Excel (.xlsx)</a>
                <a href="javascript:void(0)" class="dropdown-item" onclick="switchTab('home')">🏠 Tutte le Leghe (Home Hub)</a>
            </div>
        </div>
    `;

    // Aggiorna anche il badge compatto della rosa nell'header
    const hdrBudget = document.getElementById('hdrRemainingBudget');
    const hdrCount = document.getElementById('hdrPlayersCount');
    if (hdrBudget) {
        const rem = (State.budgetTotal || 1000) - (State.budgetSpent || 0);
        hdrBudget.textContent = `${rem} CR`;
    }
    if (hdrCount) {
        const pCount = (State.slots?.P?.players?.length || 0) +
                       (State.slots?.D?.players?.length || 0) +
                       (State.slots?.C?.players?.length || 0) +
                       (State.slots?.A?.players?.length || 0);
        const max = (State.systemMode === 'mantra') ? 31 : 25;
        hdrCount.textContent = `${pCount}/${max}`;
    }
}

// Modal Creazione Nuova Lega
// Modal Creazione Nuova Lega
function openCreateLeagueModal() {
    const modal = document.getElementById('createLeagueModal');
    if (!modal) return;
    modal.style.display = 'flex';
    modal.classList.add('active');

    const body = document.getElementById('createLeagueModalBody');
    if (body) {
        body.innerHTML = `
            <form id="createLeagueForm" onsubmit="event.preventDefault(); submitCreateLeague();">
                <div style="display:flex;flex-direction:column;gap:13px;">
                    <!-- 1. NOME LEGA -->
                    <div>
                        <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:3px;text-transform:uppercase;">1. Nome del Campionato / Lega</label>
                        <input type="text" id="newLeagueName" required placeholder="Es. Lega Fantacalcio Serie A" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px 12px;font-size:13px;">
                    </div>

                    <!-- 2. NOME SQUADRA -->
                    <div>
                        <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:3px;text-transform:uppercase;">2. Nome della Tua Squadra</label>
                        <input type="text" id="newLeagueTeamName" required value="La Mia Rosa" placeholder="Es. FC Campioni" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px 12px;font-size:13px;">
                    </div>

                    <!-- 3. BUDGET & 4. NUMERO PARTECIPANTI -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                        <div>
                            <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:3px;text-transform:uppercase;">3. Budget Iniziale</label>
                            <select id="newLeagueBudget" onchange="onNewLeagueBudgetChange(this.value)" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px;font-size:12.5px;">
                                <option value="1000">1000 Crediti (Consigliato)</option>
                                <option value="500">500 Crediti (Standard)</option>
                                <option value="600">600 Crediti</option>
                                <option value="800">800 Crediti</option>
                                <option value="custom">✏️ Altro (Personalizzato)...</option>
                            </select>
                            <input type="number" id="newLeagueBudgetCustom" placeholder="Es. 750" min="100" max="10000" style="display:none;width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:7px 10px;font-size:12px;margin-top:4px;">
                        </div>
                        <div>
                            <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:3px;text-transform:uppercase;">4. Partecipanti</label>
                            <select id="newLeagueNumTeams" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px;font-size:12.5px;">
                                <option value="8">8 Squadre (Tu + 7 Rivali)</option>
                                <option value="10">10 Squadre (Tu + 9 Rivali)</option>
                                <option value="6">6 Squadre (Tu + 5 Rivali)</option>
                                <option value="12">12 Squadre (Tu + 11 Rivali)</option>
                            </select>
                        </div>
                    </div>

                    <!-- 5. MODALITÀ DI GIOCO -->
                    <div>
                        <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:3px;text-transform:uppercase;">5. Modalità Regolamento</label>
                        <select id="newLeagueMode" onchange="onNewLeagueModeChange(this.value)" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px;font-size:12.5px;">
                            <option value="classic">⚡ Classic (Ruoli Tradizionali P, D, C, A)</option>
                            <option value="mantra">🔮 Mantra (Schemi & Ruoli Fanta.it)</option>
                        </select>
                    </div>

                    <!-- REGOLE DINAMICHE: 6. DIMENSIONI ROSA & PORTIERI, 7. MODIFICATORE DIFESA -->
                    <div id="leagueRulesContainer"></div>

                    <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:8px;border-top:1px solid rgba(255,255,255,0.08);padding-top:12px;">
                        <button type="button" class="btn-action" onclick="closeCreateLeagueModal()">Annulla</button>
                        <button type="submit" class="btn-action" style="background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#000;font-weight:900;border:none;padding:8px 18px;">
                            ✓ Crea Campionato
                        </button>
                    </div>
                </div>
            </form>
        `;
        renderLeagueRulesSection('classic');
    }
}

function onNewLeagueModeChange(mode) {
    renderLeagueRulesSection(mode);
}

function onNewLeagueBudgetChange(val) {
    const customInp = document.getElementById('newLeagueBudgetCustom');
    if (customInp) {
        customInp.style.display = (val === 'custom') ? 'block' : 'none';
        if (val === 'custom') customInp.focus();
    }
}

function updateClassicRosterTotal() {
    const p = parseInt(document.getElementById('classicSlotP')?.value, 10) || 0;
    const d = parseInt(document.getElementById('classicSlotD')?.value, 10) || 0;
    const c = parseInt(document.getElementById('classicSlotC')?.value, 10) || 0;
    const a = parseInt(document.getElementById('classicSlotA')?.value, 10) || 0;
    const tot = p + d + c + a;
    const badge = document.getElementById('classicTotalSlotsBadge');
    if (badge) {
        badge.textContent = `${tot} Slot (${p}P - ${d}D - ${c}C - ${a}A)`;
    }
}

function renderLeagueRulesSection(mode) {
    const container = document.getElementById('leagueRulesContainer');
    if (!container) return;

    if (mode === 'mantra') {
        container.innerHTML = `
            <div style="background:rgba(0,242,254,0.04);border:1px solid rgba(0,242,254,0.25);border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:12px;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:14px;">🔮</span>
                    <span style="font-size:12px;font-weight:800;color:var(--accent-cyan);text-transform:uppercase;">Regole del Campionato Mantra</span>
                </div>

                <!-- 6. DIMENSIONI ROSA & PORTIERI MANTRA -->
                <div>
                    <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:6px;text-transform:uppercase;">6. Dimensioni Rosa (Min / Max) & Portieri</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px;">
                        <div style="background:rgba(0,0,0,0.3);padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                            <div style="font-size:11px;color:#f59e0b;font-weight:700;margin-bottom:4px;">🧤 Portieri (Por)</div>
                            <div style="display:flex;gap:6px;align-items:center;">
                                <div style="flex:1;">
                                    <span style="font-size:10px;color:var(--text-muted);">Min:</span>
                                    <input type="number" id="mantraMinKeepers" min="1" max="4" value="3" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;">
                                </div>
                                <div style="flex:1;">
                                    <span style="font-size:10px;color:var(--text-muted);">Max:</span>
                                    <input type="number" id="mantraMaxKeepers" min="1" max="4" value="3" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;">
                                </div>
                            </div>
                        </div>

                        <div style="background:rgba(0,0,0,0.3);padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                            <div style="font-size:11px;color:var(--accent-cyan);font-weight:700;margin-bottom:4px;">👥 Rosa Totale</div>
                            <div style="display:flex;gap:6px;align-items:center;">
                                <div style="flex:1;">
                                    <span style="font-size:10px;color:var(--text-muted);">Min:</span>
                                    <input type="number" id="mantraMinRoster" min="20" max="40" value="25" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;">
                                </div>
                                <div style="flex:1;">
                                    <span style="font-size:10px;color:var(--text-muted);">Max:</span>
                                    <input type="number" id="mantraMaxRoster" min="23" max="45" value="30" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;">
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="font-size:11px;color:var(--text-muted);background:rgba(255,255,255,0.02);padding:6px 8px;border-radius:6px;">
                        ℹ️ Nel Mantra i calciatori di movimento sono a composizione libera per coprire gli 11 schemi tattici ufficiali.
                    </div>
                </div>

                <!-- 7. MODIFICATORE DIFESA MANTRA -->
                <div>
                    <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">7. Modificatore Difesa</label>
                    <select id="newLeagueModDifesaMantra" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px;font-size:12.5px;">
                        <option value="no">❌ No — Ufficiale Mantra (Nessun modificatore di reparto)</option>
                        <option value="yes">🛡️ Sì — Regola Personalizzata / Ibrida</option>
                    </select>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div style="background:rgba(251,191,36,0.04);border:1px solid rgba(251,191,36,0.25);border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:12px;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:14px;">⚡</span>
                    <span style="font-size:12px;font-weight:800;color:#fbbf24;text-transform:uppercase;">Regole del Campionato Classic</span>
                </div>

                <!-- 6. DIMENSIONI ROSA & PORTIERI CLASSIC -->
                <div>
                    <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:6px;text-transform:uppercase;">6. Dimensioni Rosa & Portieri (Suddivisione Slot)</label>
                    <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:8px;margin-bottom:8px;">
                        <div style="background:rgba(0,0,0,0.3);padding:6px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);text-align:center;">
                            <div style="font-size:10.5px;color:#f59e0b;font-weight:700;">🧤 Portieri (P)</div>
                            <input type="number" id="classicSlotP" min="1" max="5" value="3" oninput="updateClassicRosterTotal()" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;margin-top:3px;">
                        </div>
                        <div style="background:rgba(0,0,0,0.3);padding:6px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);text-align:center;">
                            <div style="font-size:10.5px;color:#3b82f6;font-weight:700;">🛡️ Difensori (D)</div>
                            <input type="number" id="classicSlotD" min="4" max="15" value="8" oninput="updateClassicRosterTotal()" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;margin-top:3px;">
                        </div>
                        <div style="background:rgba(0,0,0,0.3);padding:6px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);text-align:center;">
                            <div style="font-size:10.5px;color:#10b981;font-weight:700;">🪄 Centroc. (C)</div>
                            <input type="number" id="classicSlotC" min="4" max="15" value="8" oninput="updateClassicRosterTotal()" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;margin-top:3px;">
                        </div>
                        <div style="background:rgba(0,0,0,0.3);padding:6px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);text-align:center;">
                            <div style="font-size:10.5px;color:#ef4444;font-weight:700;">⚡ Attaccanti (A)</div>
                            <input type="number" id="classicSlotA" min="3" max="12" value="6" oninput="updateClassicRosterTotal()" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px;font-size:12px;text-align:center;margin-top:3px;">
                        </div>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(251,191,36,0.1);border-radius:6px;font-size:11.5px;">
                        <span style="color:var(--text-muted);">Totale Calciatori in Rosa:</span>
                        <b id="classicTotalSlotsBadge" style="color:#fbbf24;font-size:12.5px;">25 Slot (3P - 8D - 8C - 6A)</b>
                    </div>
                </div>

                <!-- 7. MODIFICATORE DIFESA CLASSIC -->
                <div>
                    <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">7. Modificatore Difesa</label>
                    <select id="newLeagueModDifesa" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:8px;font-size:12.5px;">
                        <option value="yes">🛡️ Sì — Modificatore Difesa Attivo (+1, +3, +6 a fasce)</option>
                        <option value="no">❌ No — Modificatore Difesa Disattivato</option>
                    </select>
                </div>
            </div>
        `;
    }
}

function closeCreateLeagueModal() {
    const modal = document.getElementById('createLeagueModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function submitCreateLeague() {
    const name = document.getElementById('newLeagueName')?.value.trim();
    const teamName = document.getElementById('newLeagueTeamName')?.value.trim();
    const mode = document.getElementById('newLeagueMode')?.value || 'classic';
    
    let budget = parseInt(document.getElementById('newLeagueBudget')?.value, 10);
    if (isNaN(budget) || document.getElementById('newLeagueBudget')?.value === 'custom') {
        budget = parseInt(document.getElementById('newLeagueBudgetCustom')?.value, 10) || 1000;
    }
    const numTeams = parseInt(document.getElementById('newLeagueNumTeams')?.value, 10) || 8;

    if (!name) {
        alert("Inserisci un nome per la lega!");
        return;
    }

    let slotsP = 3, slotsD = 8, slotsC = 8, slotsA = 6;
    let minKeepers = 3, maxKeepers = 3;
    let minRosterSize = 25, maxRosterSize = 25;
    let modificatoreDifesa = false;

    if (mode === 'classic') {
        slotsP = parseInt(document.getElementById('classicSlotP')?.value, 10) || 3;
        slotsD = parseInt(document.getElementById('classicSlotD')?.value, 10) || 8;
        slotsC = parseInt(document.getElementById('classicSlotC')?.value, 10) || 8;
        slotsA = parseInt(document.getElementById('classicSlotA')?.value, 10) || 6;
        minKeepers = slotsP;
        maxKeepers = slotsP;
        minRosterSize = slotsP + slotsD + slotsC + slotsA;
        maxRosterSize = minRosterSize;
        modificatoreDifesa = (document.getElementById('newLeagueModDifesa')?.value === 'yes');
    } else {
        minKeepers = parseInt(document.getElementById('mantraMinKeepers')?.value, 10) || 3;
        maxKeepers = parseInt(document.getElementById('mantraMaxKeepers')?.value, 10) || 3;
        minRosterSize = parseInt(document.getElementById('mantraMinRoster')?.value, 10) || 25;
        maxRosterSize = parseInt(document.getElementById('mantraMaxRoster')?.value, 10) || 30;
        slotsP = maxKeepers;
        modificatoreDifesa = (document.getElementById('newLeagueModDifesaMantra')?.value === 'yes');
    }

    const created = LeaguesManager.createLeague({
        name,
        myTeamName: teamName || 'La Mia Rosa',
        systemMode: mode,
        budgetTotal: budget,
        numTeams,
        slotsP,
        slotsD,
        slotsC,
        slotsA,
        minKeepers,
        maxKeepers,
        minRosterSize,
        maxRosterSize,
        modificatoreDifesa
    });

    closeCreateLeagueModal();
    selectAndEnterLeague(created.id);
}

// Modal Modifica Lega Esistente
function openEditLeagueModal(leagueId) {
    const leagues = LeaguesManager.getAll();
    const l = leagues.find(x => x.id === leagueId);
    if (!l) return;

    const modal = document.getElementById('editLeagueModal');
    if (!modal) return;
    modal.style.display = 'flex';
    modal.classList.add('active');

    const isClassic = (l.systemMode === 'classic');
    const curModDifesa = l.rules?.modificatoreDifesa ? 'yes' : 'no';
    const curMaxRoster = l.rules?.maxRosterSize || (isClassic ? 25 : 30);

    const body = document.getElementById('editLeagueModalBody');
    if (body) {
        body.innerHTML = `
            <form id="editLeagueForm" onsubmit="event.preventDefault(); submitEditLeague('${l.id}');">
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div>
                        <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Nome del Campionato</label>
                        <input type="text" id="editLeagueName" required value="${l.name}" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px 12px;font-size:13px;">
                    </div>

                    <div>
                        <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Nome della Tua Squadra</label>
                        <input type="text" id="editLeagueTeamName" required value="${l.myTeamName || 'La Mia Rosa'}" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px 12px;font-size:13px;">
                    </div>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                        <div>
                            <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Budget Totale</label>
                            <input type="number" id="editLeagueBudget" required min="100" max="5000" value="${l.budgetTotal || 1000}" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px 12px;font-size:13px;">
                        </div>
                        <div>
                            <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Max Calciatori in Rosa</label>
                            <input type="number" id="editLeagueMaxRoster" required min="20" max="45" value="${curMaxRoster}" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px 12px;font-size:13px;">
                        </div>
                    </div>

                    <div>
                        <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Modificatore Difesa</label>
                        <select id="editLeagueModDifesa" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px;font-size:13px;">
                            <option value="yes" ${curModDifesa === 'yes' ? 'selected' : ''}>🛡️ Sì — Modificatore Difesa Attivo</option>
                            <option value="no" ${curModDifesa === 'no' ? 'selected' : ''}>❌ No — Modificatore Difesa Disattivato</option>
                        </select>
                    </div>

                    <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:10px;border-top:1px solid rgba(255,255,255,0.08);padding-top:12px;">
                        <button type="button" class="btn-action" onclick="closeEditLeagueModal()">Annulla</button>
                        <button type="submit" class="btn-action" style="background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#000;font-weight:900;border:none;padding:9px 20px;">
                            ✓ Salva Modifiche
                        </button>
                    </div>
                </div>
            </form>
        `;
    }
}

function submitEditLeague(leagueId) {
    const leagues = LeaguesManager.getAll();
    const idx = leagues.findIndex(x => x.id === leagueId);
    if (idx === -1) return;

    const name = document.getElementById('editLeagueName')?.value.trim();
    const teamName = document.getElementById('editLeagueTeamName')?.value.trim();
    const budget = parseInt(document.getElementById('editLeagueBudget')?.value, 10);
    const maxRoster = parseInt(document.getElementById('editLeagueMaxRoster')?.value, 10);
    const modDifesa = (document.getElementById('editLeagueModDifesa')?.value === 'yes');

    if (name) leagues[idx].name = name;
    if (teamName) leagues[idx].myTeamName = teamName;
    if (!isNaN(budget) && budget >= 100) leagues[idx].budgetTotal = budget;
    if (!leagues[idx].rules) leagues[idx].rules = {};
    if (!isNaN(maxRoster) && maxRoster >= 20) leagues[idx].rules.maxRosterSize = maxRoster;
    leagues[idx].rules.modificatoreDifesa = modDifesa;

    LeaguesManager.saveAll(leagues);

    if (LeaguesManager.getActiveId() === leagueId) {
        LeaguesManager.loadLeagueIntoState(leagues[idx]);
    }

    closeEditLeagueModal();
    updateAllViews();
    renderHeaderLeagueDropdown();
    if (State.activeTab === 'home') renderHomeHubView();

    if (typeof showSyncToast === 'function') {
        showSyncToast(`✓ Impostazioni lega "${leagues[idx].name}" aggiornate!`);
    }
}

function closeEditLeagueModal() {
    const modal = document.getElementById('editLeagueModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

// GESTIONE DOPPIA CONFERMA ELIMINAZIONE LEGA
let leaguePendingDeleteId = null;

function promptDeleteLeague(leagueId) {
    const leagues = LeaguesManager.getAll();
    if (leagues.length <= 1) {
        alert("⚠️ Non puoi eliminare l'unica lega presente. Crea prima un altro campionato per poter eliminare questo.");
        return;
    }

    const l = leagues.find(x => x.id === leagueId);
    if (!l) return;

    leaguePendingDeleteId = leagueId;
    const modal = document.getElementById('deleteLeagueModal');
    if (!modal) {
        if (confirm(`Sei sicuro di voler eliminare la lega "${l.name}"?`)) {
            if (confirm(`CONFERMA DEFINITIVA: Procedere con l'eliminazione irreversibile di "${l.name}"?`)) {
                executeDeleteLeague(leagueId);
            }
        }
        return;
    }

    modal.style.display = 'flex';
    modal.classList.add('active');

    renderDeleteStep1(l);
}

function closeDeleteLeagueModal() {
    leaguePendingDeleteId = null;
    const modal = document.getElementById('deleteLeagueModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function renderDeleteStep1(l) {
    const body = document.getElementById('deleteLeagueModalBody');
    if (!body) return;

    const pCount = (l.slots?.P?.players?.length || 0) +
                   (l.slots?.D?.players?.length || 0) +
                   (l.slots?.C?.players?.length || 0) +
                   (l.slots?.A?.players?.length || 0);

    body.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:16px;">
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:12px 14px;color:#fca5a5;font-size:13px;line-height:1.5;">
                ⚠️ <b>Conferma Eliminazione (Passo 1 di 2):</b><br>
                Stai per eliminare il campionato <b>"${l.name}"</b>.
            </div>

            <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;font-size:12.5px;display:flex;flex-direction:column;gap:6px;">
                <div style="display:flex;justify-content:space-between;"><span style="color:var(--text-muted);">Regolamento:</span> <b>${l.systemMode === 'mantra' ? '🔮 Mantra' : '⚡ Classic'}</b></div>
                <div style="display:flex;justify-content:space-between;"><span style="color:var(--text-muted);">Tua Squadra:</span> <b>${l.myTeamName || 'La Mia Rosa'}</b></div>
                <div style="display:flex;justify-content:space-between;"><span style="color:var(--text-muted);">Calciatori in Rosa:</span> <b>${pCount}</b></div>
                <div style="display:flex;justify-content:space-between;"><span style="color:var(--text-muted);">Budget:</span> <b>${l.budgetSpent || 0} / ${l.budgetTotal || 1000} CR</b></div>
            </div>

            <div style="font-size:12px;color:var(--text-muted);line-height:1.4;">
                Tutti i dati, le rose, i crediti spesi e lo storico d'asta di questa lega verranno cancellati.
            </div>

            <div style="display:flex;justify-content:flex-end;gap:10px;border-top:1px solid rgba(255,255,255,0.08);padding-top:14px;">
                <button type="button" class="btn-action" onclick="closeDeleteLeagueModal()">Annulla</button>
                <button type="button" class="btn-action" onclick="renderDeleteStep2('${l.id}')" style="background:rgba(239,68,68,0.25);border:1px solid #ef4444;color:#ef4444;font-weight:800;padding:8px 16px;">
                    Procedi all'Eliminazione ➔
                </button>
            </div>
        </div>
    `;
}

function renderDeleteStep2(leagueId) {
    const leagues = LeaguesManager.getAll();
    const l = leagues.find(x => x.id === leagueId);
    if (!l) return closeDeleteLeagueModal();

    const body = document.getElementById('deleteLeagueModalBody');
    if (!body) return;

    body.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:16px;">
            <div style="background:rgba(220,38,38,0.2);border:1px solid #ef4444;border-radius:10px;padding:14px;color:#f87171;font-size:13px;line-height:1.5;">
                🚨 <b>DOPPIA CONFERMA DI SICUREZZA (Passo 2 di 2):</b><br>
                Questa azione è <b>irreversibile</b> al 100%. Confermi di voler distruggere definitivamente la lega <b>"${l.name}"</b>?
            </div>

            <div style="font-size:12.5px;color:#cbd5e1;line-height:1.5;">
                Tutti i dati della lega verranno rimossi permanentemente dal dispositivo.
            </div>

            <div style="display:flex;justify-content:flex-end;gap:10px;border-top:1px solid rgba(255,255,255,0.08);padding-top:14px;">
                <button type="button" class="btn-action" onclick="closeDeleteLeagueModal()">✕ Annulla</button>
                <button type="button" class="btn-action" onclick="executeDeleteLeague('${l.id}')" style="background:linear-gradient(135deg, #ef4444, #b91c1c);color:#fff;border:none;font-weight:900;padding:10px 20px;box-shadow:0 0 16px rgba(239,68,68,0.4);">
                    🗑️ SÌ, ELIMINA DEFINITIVAMENTE
                </button>
            </div>
        </div>
    `;
}

function executeDeleteLeague(leagueId) {
    const leagues = LeaguesManager.getAll();
    const target = leagues.find(x => x.id === leagueId);
    const targetName = target ? target.name : 'Lega';

    const success = LeaguesManager.deleteLeague(leagueId);
    closeDeleteLeagueModal();

    if (success && typeof showSyncToast === 'function') {
        showSyncToast(`✓ Campionato "${targetName}" eliminato con successo!`);
    }
}

function exportCurrentLeagueJson() {
    const active = LeaguesManager.getActive();
    if (!active) return;
    LeaguesManager.saveCurrentStateToActiveLeague();
    const updated = LeaguesManager.getActive();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(updated, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    const safeName = (updated.name || 'lega').replace(/[^a-z0-9_-]/gi, '_').toLowerCase();
    dlAnchor.setAttribute("download", `fanta_ai_${safeName}_${Date.now()}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
}

window.renderHomeHubView = renderHomeHubView;
window.renderHeaderLeagueDropdown = renderHeaderLeagueDropdown;
window.selectAndEnterLeague = selectAndEnterLeague;
window.openCreateLeagueModal = openCreateLeagueModal;
window.closeCreateLeagueModal = closeCreateLeagueModal;
window.submitCreateLeague = submitCreateLeague;
window.openEditLeagueModal = openEditLeagueModal;
window.closeEditLeagueModal = closeEditLeagueModal;
window.submitEditLeague = submitEditLeague;
window.exportCurrentLeagueJson = exportCurrentLeagueJson;
window.promptDeleteLeague = promptDeleteLeague;
window.closeDeleteLeagueModal = closeDeleteLeagueModal;
window.renderDeleteStep1 = renderDeleteStep1;
window.renderDeleteStep2 = renderDeleteStep2;
window.executeDeleteLeague = executeDeleteLeague;
window.onNewLeagueModeChange = onNewLeagueModeChange;
window.onNewLeagueBudgetChange = onNewLeagueBudgetChange;
window.updateClassicRosterTotal = updateClassicRosterTotal;
window.renderLeagueRulesSection = renderLeagueRulesSection;

