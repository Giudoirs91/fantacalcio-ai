// ==============================================================================
// MODULO SQUAD BUILDER & RACCOMANDAZIONI DINAMICHE AI
// (LAYOUT A LISTA & GRIGLIA, SLIDER RUOLI, FILTRO CONSIGLI, PREFERITI ⭐ & RICERCA)
// ==============================================================================

function setSbViewMode(mode) {
    State.sbViewMode = mode;
    renderSquadBuilderList();
    updateSbViewModeUI();
}

function updateSbViewModeUI() {
    document.querySelectorAll('.sb-view-btn').forEach(btn => {
        const mode = btn.getAttribute('data-mode');
        if (mode === State.sbViewMode) btn.classList.add('active');
        else btn.classList.remove('active');
    });
}

function onSbRoleSelect(role) {
    if (State.sbRole === role && role !== 'ALL') {
        State.sbRole = 'ALL';
    } else {
        State.sbRole = role;
    }
    renderSquadBuilderList();
    updateSbRolePillsUI();
}

function onSbAdviceSelect(advice) {
    State.sbAdvice = advice;
    renderSquadBuilderList();
}

function toggleSbFavoriteFilter() {
    State.sbOnlyFav = !State.sbOnlyFav;
    renderSquadBuilderList();
    updateSbFavButtonUI();
}

function toggleSbAvailableFilter() {
    State.sbOnlyAvail = !State.sbOnlyAvail;
    renderSquadBuilderList();
    updateSbAvailButtonUI();
}

function onSbSearchQuery(val) {
    State.sbQuery = val;
    renderSquadBuilderList();
}

function updateSbRolePillsUI() {
    const cur = State.sbRole || 'ALL';
    document.querySelectorAll('.sb-role-pill-btn, .sb-subrole-btn').forEach(btn => {
        const role = btn.getAttribute('data-role');
        if (role === cur) btn.classList.add('active');
        else btn.classList.remove('active');
    });
}

function updateSbFavButtonUI() {
    const btn = document.getElementById('btnSbOnlyFav');
    if (btn) {
        if (State.sbOnlyFav) {
            btn.classList.add('active');
            btn.style.background = 'rgba(251, 191, 36, 0.25)';
            btn.style.borderColor = '#fbbf24';
            btn.style.color = '#fbbf24';
        } else {
            btn.classList.remove('active');
            btn.style.background = 'rgba(255, 255, 255, 0.05)';
            btn.style.borderColor = 'var(--border-glass)';
            btn.style.color = 'var(--text-secondary)';
        }
    }
}

function updateSbAvailButtonUI() {
    const btn = document.getElementById('btnSbOnlyAvail');
    if (btn) {
        if (State.sbOnlyAvail) {
            btn.classList.add('active');
            btn.style.background = 'rgba(34, 197, 94, 0.2)';
            btn.style.borderColor = '#22c55e';
            btn.style.color = '#4ade80';
        } else {
            btn.classList.remove('active');
            btn.style.background = 'rgba(255, 255, 255, 0.05)';
            btn.style.borderColor = 'var(--border-glass)';
            btn.style.color = 'var(--text-secondary)';
        }
    }
}

function renderSquadBuilder() {
    const container = document.getElementById('squadBuilderContainer');
    if (!container) return;

    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    if (!State.sbViewMode) State.sbViewMode = 'list';

    const remaining = State.budgetTotal - State.budgetSpent;
    const totalBought = State.slots.P.players.length + State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length;
    const maxRosterSlots = isMantraMode ? 31 : 25;
    const totalSlotsRemaining = Math.max(0, maxRosterSlots - totalBought);
    const maxSingleBid = totalSlotsRemaining > 0 ? Math.max(1, remaining - (totalSlotsRemaining - 1)) : 0;
    const takenCount = State.takenByOthers ? State.takenByOthers.length : 0;
    const favCount = State.favorites ? State.favorites.length : 0;

    // Percentuali di spesa effettive
    const pSpent = State.slots.P.players.reduce((sum, p) => sum + (p.paidPrice || 0), 0);
    const dSpent = State.slots.D.players.reduce((sum, p) => sum + (p.paidPrice || 0), 0);
    const cSpent = State.slots.C.players.reduce((sum, p) => sum + (p.paidPrice || 0), 0);
    const aSpent = State.slots.A.players.reduce((sum, p) => sum + (p.paidPrice || 0), 0);

    // Metriche aggregate della rosa
    const allBought = [...State.slots.P.players, ...State.slots.D.players, ...State.slots.C.players, ...State.slots.A.players];
    const avgOvr = allBought.length > 0 ? (allBought.reduce((acc, p) => acc + p.ovr, 0) / allBought.length).toFixed(1) : '-';
    const totalG2526 = allBought.reduce((acc, p) => acc + (p.gf || 0), 0);
    const totalA2526 = allBought.reduce((acc, p) => acc + (p.ass || 0), 0);

    let html = `
        <!-- HEADER STATS BAR SQUAD BUILDER -->
        <div class="sb-stats-bar">
            <div class="sb-stat-card primary">
                <span class="sb-lbl">💰 Crediti Residui</span>
                <span class="sb-val gold">${remaining} <small>CR</small></span>
                <span class="sb-sub">Spesi: ${State.budgetSpent} CR / ${State.budgetTotal} CR</span>
            </div>
            <div class="sb-stat-card">
                <span class="sb-lbl">📊 Rosa Completata</span>
                <span class="sb-val">${totalBought} <small>/ ${maxRosterSlots}</small></span>
                <span class="sb-sub">${isMantraMode ? `Rimanenti: ${totalSlotsRemaining} (3 Por + 28 Mov)` : `Rimanenti: ${totalSlotsRemaining} slot`}</span>
            </div>
            <div class="sb-stat-card">
                <span class="sb-lbl">🎯 Max Bid Possibile</span>
                <span class="sb-val cyan">${maxSingleBid} <small>CR</small></span>
                <span class="sb-sub">Min 1 CR/slot garantito</span>
            </div>
            <div class="sb-stat-card">
                <span class="sb-lbl">⭐ Qualità Rosa (OVR)</span>
                <span class="sb-val purple">${avgOvr}</span>
                <span class="sb-sub">Gol 25/26: ${totalG2526} | Assist: ${totalA2526}</span>
            </div>
            <div class="sb-stat-card">
                <span class="sb-lbl">🚫 Presi da Altri</span>
                <span class="sb-val" style="color:#ef4444;">${takenCount} <small>calciatori</small></span>
                <div style="display:flex;align-items:center;gap:6px;margin-top:2px;">
                    <button onclick="openRivalsRadarModal();" style="font-size:9.5px;background:rgba(0,242,254,0.15);border:1px solid var(--accent-cyan);color:var(--accent-cyan);padding:1px 5px;border-radius:3px;cursor:pointer;">🕵️ Radar Rivals</button>
                    ${takenCount > 0 ? `<button onclick="clearAllTaken();" style="font-size:9.5px;background:rgba(239,68,68,0.2);border:1px solid #ef4444;color:#ef4444;padding:1px 4px;border-radius:3px;cursor:pointer;">Reset</button>` : ''}
                </div>
            </div>
        </div>

        <!-- TOOLBAR: TOP 11, RADAR RIVALS, EXPORT WHATSAPP -->
        <div class="sb-actions-toolbar">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <button class="sb-tool-btn primary" onclick="openBest11Modal();">
                    <span>⚡ Schiera Miglior 11 AI</span>
                </button>
                <button class="sb-tool-btn" onclick="openRivalsRadarModal();">
                    <span>🕵️ Spionaggio & Budget 7 Avversari</span>
                </button>
                <button class="sb-tool-btn success" onclick="exportRosterToWhatsApp();">
                    <span>📤 Copia Rosa per WhatsApp</span>
                </button>
                <button class="sb-tool-btn" onclick="downloadRosterCSV();">
                    <span>📥 Scarica Excel / CSV</span>
                </button>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:11.5px;color:var(--text-muted);">Visualizzazione:</span>
                <div class="sb-viewmode-toggle">
                    <button class="sb-view-btn ${State.sbViewMode === 'list' ? 'active' : ''}" data-mode="list" onclick="setSbViewMode('list')">📋 Lista</button>
                    <button class="sb-view-btn ${State.sbViewMode === 'grid' ? 'active' : ''}" data-mode="grid" onclick="setSbViewMode('grid')">🔲 Griglia</button>
                </div>
            </div>
        </div>

        <!-- MAIN LAYOUT: UNIFIED FULL-WIDTH RECOMMENDATIONS -->
        <div class="sb-main-grid" style="display:block;width:100%;">
            <!-- RIGHT SECTION: UNIFIED RECOMMENDATION ENGINE CON SLIDER RUOLI E FILTRI -->
            <div class="sb-ai-unified-wrapper">
                <!-- 1. SLIDER RUOLI A SCHEDE / PILLS -->
                <div class="sb-role-slider-bar">
                    ${isMantraMode ? `
                        <button class="sb-role-pill-btn ${State.sbRole === 'ALL' ? 'active' : ''}" data-role="ALL" onclick="onSbRoleSelect('ALL')">
                            <span>✨ Tutti i Ruoli Mantra</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'Por' ? 'active' : ''}" data-role="Por" onclick="onSbRoleSelect('Por')">
                            <span style="color:var(--mantra-por);">🧤 Portieri (Por)</span>
                            <span class="sb-pill-badge">${State.slots.P.players.length}</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'DEF_ALL' ? 'active' : ''}" data-role="DEF_ALL" onclick="onSbRoleSelect('DEF_ALL')">
                            <span style="color:var(--mantra-dc);">🛡️ Difensori</span>
                            <span class="sb-pill-badge">${State.slots.D.players.length}</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'MID_ALL' ? 'active' : ''}" data-role="MID_ALL" onclick="onSbRoleSelect('MID_ALL')">
                            <span style="color:var(--mantra-c);">⚙️ Mediana / Esterni</span>
                            <span class="sb-pill-badge">${State.slots.C.players.length}</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'ATT_ALL' ? 'active' : ''}" data-role="ATT_ALL" onclick="onSbRoleSelect('ATT_ALL')">
                            <span style="color:var(--mantra-pc);">⚡ Attacco / TreQ</span>
                            <span class="sb-pill-badge">${State.slots.A.players.length}</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'MULTI' ? 'active' : ''}" data-role="MULTI" onclick="onSbRoleSelect('MULTI')">
                            <span style="color:var(--accent-purple);">💎 Polivalenti (2+)</span>
                        </button>
                    ` : `
                        <button class="sb-role-pill-btn ${State.sbRole === 'ALL' ? 'active' : ''}" data-role="ALL" onclick="onSbRoleSelect('ALL')">
                            <span>✨ Tutti i Ruoli</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'P' ? 'active' : ''}" data-role="P" onclick="onSbRoleSelect('P')">
                            <span style="color:var(--role-p);">🧤 Portieri (P)</span>
                            <span class="sb-pill-badge">${State.slots.P.players.length}/3</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'D' ? 'active' : ''}" data-role="D" onclick="onSbRoleSelect('D')">
                            <span style="color:var(--role-d);">🛡️ Difensori (D)</span>
                            <span class="sb-pill-badge">${State.slots.D.players.length}/8</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'C' ? 'active' : ''}" data-role="C" onclick="onSbRoleSelect('C')">
                            <span style="color:var(--role-c);">🪄 Centrocampisti (C)</span>
                            <span class="sb-pill-badge">${State.slots.C.players.length}/8</span>
                        </button>
                        <button class="sb-role-pill-btn ${State.sbRole === 'A' ? 'active' : ''}" data-role="A" onclick="onSbRoleSelect('A')">
                            <span style="color:var(--role-a);">⚡ Attaccanti (A)</span>
                            <span class="sb-pill-badge">${State.slots.A.players.length}/6</span>
                        </button>
                    `}
                </div>

                ${isMantraMode ? `
                    <!-- 1b. BARRA SOTTOPOSIZIONI SINGOLE MANTRA -->
                    <div class="sb-subroles-slider-bar">
                        <span class="sb-subroles-title">🎯 Sottoposizioni:</span>
                        <button class="sb-subrole-btn ${State.sbRole === 'Dc' ? 'active' : ''}" data-role="Dc" onclick="onSbRoleSelect('Dc')">
                            <span class="mantra-badge dc" style="padding:1px 5px;font-size:10.5px;">Dc</span> Centrale
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'B' ? 'active' : ''}" data-role="B" onclick="onSbRoleSelect('B')">
                            <span class="mantra-badge b" style="padding:1px 5px;font-size:10.5px;">B</span> Braccetto
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'Dd' ? 'active' : ''}" data-role="Dd" onclick="onSbRoleSelect('Dd')">
                            <span class="mantra-badge dd" style="padding:1px 5px;font-size:10.5px;">Dd</span> Terzino Dx
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'Ds' ? 'active' : ''}" data-role="Ds" onclick="onSbRoleSelect('Ds')">
                            <span class="mantra-badge ds" style="padding:1px 5px;font-size:10.5px;">Ds</span> Terzino Sx
                        </button>
                        <span class="sb-subroles-sep">|</span>
                        <button class="sb-subrole-btn ${State.sbRole === 'E' ? 'active' : ''}" data-role="E" onclick="onSbRoleSelect('E')">
                            <span class="mantra-badge e" style="padding:1px 5px;font-size:10.5px;">E</span> Esterno
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'M' ? 'active' : ''}" data-role="M" onclick="onSbRoleSelect('M')">
                            <span class="mantra-badge m" style="padding:1px 5px;font-size:10.5px;">M</span> Mediano
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'C' ? 'active' : ''}" data-role="C" onclick="onSbRoleSelect('C')">
                            <span class="mantra-badge c" style="padding:1px 5px;font-size:10.5px;">C</span> Centrocampista
                        </button>
                        <span class="sb-subroles-sep">|</span>
                        <button class="sb-subrole-btn ${State.sbRole === 'T' ? 'active' : ''}" data-role="T" onclick="onSbRoleSelect('T')">
                            <span class="mantra-badge t" style="padding:1px 5px;font-size:10.5px;">T</span> Trequartista
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'W' ? 'active' : ''}" data-role="W" onclick="onSbRoleSelect('W')">
                            <span class="mantra-badge w" style="padding:1px 5px;font-size:10.5px;">W</span> Ala Offensiva
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'A' ? 'active' : ''}" data-role="A" onclick="onSbRoleSelect('A')">
                            <span class="mantra-badge a" style="padding:1px 5px;font-size:10.5px;">A</span> Seconda Punta
                        </button>
                        <button class="sb-subrole-btn ${State.sbRole === 'Pc' ? 'active' : ''}" data-role="Pc" onclick="onSbRoleSelect('Pc')">
                            <span class="mantra-badge pc" style="padding:1px 5px;font-size:10.5px;">Pc</span> Centravanti
                        </button>
                    </div>
                ` : ''}

                <!-- 2. BARRA FILTRI (CONSIGLI AI, PREFERITI ⭐, DISPONIBILI, RICERCA) -->
                <div class="sb-filter-control-panel">
                    <div class="sb-filter-left-group">
                        <div class="sb-input-search-box">
                            <input type="text" id="sbUnifiedSearchInput" class="sb-unified-search" placeholder="🔍 Cerca calciatore, squadra o ruolo..." value="${State.sbQuery || ''}" oninput="onSbSearchQuery(this.value)">
                        </div>

                        <select id="sbAdviceFilterSelect" class="select-filter" style="max-width:200px;" onchange="onSbAdviceSelect(this.value)">
                            <option value="ALL" ${State.sbAdvice === 'ALL' ? 'selected' : ''}>🎯 Tutti i Consigli AI</option>
                            <option value="top" ${State.sbAdvice === 'top' ? 'selected' : ''}>⭐ Top Player Assoluto</option>
                            <option value="leader" ${State.sbAdvice === 'leader' ? 'selected' : ''}>👑 Leader di Squadra / Rigorista</option>
                            <option value="buy" ${State.sbAdvice === 'buy' ? 'selected' : ''}>🔥 Da Acquistare (Best Value)</option>
                            <option value="sleeper" ${State.sbAdvice === 'sleeper' ? 'selected' : ''}>💎 Scommessa / Sleeper</option>
                            <option value="lowcost" ${State.sbAdvice === 'lowcost' ? 'selected' : ''}>🪙 Low Cost Modificatore</option>
                            <option value="titolarissimo" ${State.sbAdvice === 'titolarissimo' ? 'selected' : ''}>🔒 Titolarissimo da Voto</option>
                            <option value="flop" ${State.sbAdvice === 'flop' ? 'selected' : ''}>⚠️ Possibile Flop / Fragile</option>
                        </select>
                    </div>

                    <div class="sb-filter-right-group">
                        <button id="btnSbOnlyFav" class="sb-toggle-btn ${State.sbOnlyFav ? 'active' : ''}" onclick="toggleSbFavoriteFilter()">
                            <span>⭐ Solo Preferiti (${favCount})</span>
                        </button>
                        <button id="btnSbOnlyAvail" class="sb-toggle-btn ${State.sbOnlyAvail ? 'active' : ''}" onclick="toggleSbAvailableFilter()">
                            <span>🟢 Solo Disponibili</span>
                        </button>
                    </div>
                </div>

                <!-- 3. LISTA DINAMICA UNIFICATA CALCIATORI CONSIGLIATI (LISTA O GRIGLIA) -->
                <div class="sb-unified-list-container" id="sbUnifiedListContainer">
                    <!-- Popolato dinamicamente da renderSquadBuilderList() -->
                </div>
            </div>
        </div>

        <!-- MODAL OVERLAY -->
        <div id="sbGenericModal" class="sb-modal-backdrop" style="display:none;" onclick="if(event.target===this) closeSbModal();">
            <div class="sb-modal-card" id="sbModalContent"></div>
        </div>
    `;

    container.innerHTML = html;
    renderSquadBuilderList();
}

// -----------------------------------------------------------------------------
// RENDER DELLA LISTA / GRIGLIA UNIFICATA DEI CALCIATORI
// -----------------------------------------------------------------------------
function renderSquadBuilderList() {
    const listContainer = document.getElementById('sbUnifiedListContainer');
    if (!listContainer) return;

    let list = PLAYERS.filter(p => {
        if (State.systemMode === 'mantra') {
            if (State.sbRole && State.sbRole !== 'ALL' && !isPlayerEligibleForMantraRole(p, State.sbRole)) return false;
        } else {
            if (State.sbRole && State.sbRole !== 'ALL' && p.role !== State.sbRole) return false;
        }
        if (State.sbOnlyAvail && !isPlayerAvailable(p.id)) return false;
        if (State.sbOnlyFav && !isFavorite(p.id)) return false;
        if (State.sbAdvice && State.sbAdvice !== 'ALL' && p.ai_advice_type !== State.sbAdvice) return false;

        if (State.sbQuery) {
            const q = State.sbQuery.toLowerCase();
            const mName = p.name.toLowerCase().includes(q);
            const mTeam = p.team.toLowerCase().includes(q);
            const mMantra = (p.mantra || '').toLowerCase().includes(q);
            if (!mName && !mTeam && !mMantra) return false;
        }
        return true;
    });

    list.sort((a, b) => {
        if (a.role === 'P' && b.role === 'P' && State.slots.P.players.length === 1) {
            const teamP = State.slots.P.players[0].team;
            const row = (typeof GK_DATA !== 'undefined' && GK_DATA.matrix) ? GK_DATA.matrix[teamP] : null;
            if (row) {
                const aSame = a.team === teamP ? -1 : 1;
                const bSame = b.team === teamP ? -1 : 1;
                if (aSame !== bSame) return aSame - bSame;

                const disA = row[a.team] !== undefined ? row[a.team] : 99;
                const disB = row[b.team] !== undefined ? row[b.team] : 99;
                if (disA !== disB) return disA - disB;
            }
        }

        const aRig = (a.rigorista_val && a.rigorista_val.includes('1°')) ? 30 : 0;
        const bRig = (b.rigorista_val && b.rigorista_val.includes('1°')) ? 30 : 0;
        const aScore = a.ovr + aRig + (a.xg90_2526 || 0) * 30 + (a.xa90_2526 || 0) * 30;
        const bScore = b.ovr + bRig + (b.xg90_2526 || 0) * 30 + (b.xa90_2526 || 0) * 30;
        return bScore - aScore;
    });

    if (list.length === 0) {
        listContainer.innerHTML = `
            <div class="sb-no-results-big">
                <span style="font-size:32px;">🔍</span>
                <p style="margin:6px 0 0 0;font-size:14px;color:var(--text-secondary);">Nessun calciatore trovato con i filtri correnti.</p>
                <button class="sb-tool-btn" style="margin-top:10px;" onclick="resetSbFilters()">Reimposta Filtri</button>
            </div>
        `;
        return;
    }

    const viewMode = State.sbViewMode || 'list';

    if (viewMode === 'list') {
        let itemsHtml = list.slice(0, 100).map(p => renderUnifiedPlayerRow(p)).join('');
        listContainer.innerHTML = `<div class="sb-list-rows-wrapper">${itemsHtml}</div>`;
    } else {
        let itemsHtml = list.slice(0, 100).map(p => renderUnifiedPlayerCard(p)).join('');
        listContainer.innerHTML = `<div class="sb-cards-grid-unified">${itemsHtml}</div>`;
    }
}

// -----------------------------------------------------------------------------
// 1. VISTA A RIGA (LISTA ORIZZONTALE COMPATTA E PULITA)
// -----------------------------------------------------------------------------
function renderUnifiedPlayerRow(p) {
    const isFav = isFavorite(p.id);
    const isBought = isPlayerBought(p.id);
    const isTaken = isPlayerTakenByOther(p.id);
    const starIcon = isFav ? '⭐' : '☆';
    const starClass = isFav ? 'active' : '';

    const fragIcon = p.fragilita_badge === 'alta' ? '🔴' : (p.fragilita_badge === 'media' ? '🟡' : '🟢');
    const topOvrClass = getOvrClass(p.ovr);

    let prioBadge = '';
    if (p.role === 'P' && State.slots.P.players.length === 1) {
        const team1 = State.slots.P.players[0].team;
        if (p.team === team1) prioBadge = `<span class="sb-prio-badge safe">🛡️ Copertura ${team1}</span>`;
        else if (typeof GK_DATA !== 'undefined' && GK_DATA.matrix && GK_DATA.matrix[team1]) {
            const dis = GK_DATA.matrix[team1][p.team];
            if (dis !== undefined) prioBadge = `<span class="sb-prio-badge incrocio">🗓️ Incrocio (Disall.: ${dis})</span>`;
        }
    } else if (p.rigorista_val && p.rigorista_val.includes('1°')) {
        prioBadge = `<span class="sb-prio-badge gold">🎯 1° Rigorista</span>`;
    } else if (p.ovr >= 92) {
        prioBadge = `<span class="sb-prio-badge purple">👑 1° Slot Bomber</span>`;
    } else if (p.ovr >= 85 && p.role === 'D') {
        prioBadge = `<span class="sb-prio-badge green">👑 Top Modificatore</span>`;
    } else if (p.xa90_2526 >= 0.12 || p.oop_val !== '-') {
        prioBadge = `<span class="sb-prio-badge cyan">🪄 Terzino da Bonus</span>`;
    } else if (p.prezzo_cons <= 5) {
        prioBadge = `<span class="sb-prio-badge dim">💎 Low Cost / Sleeper</span>`;
    }

    let statsShort = '';
    let liveBadge2627 = '';
    if (p.has_data_2627 && p.presenze_2627 > 0) {
        if (p.role === 'P') {
            liveBadge2627 = `<span class="sb-prio-badge safe" title="Dati Reali Serie A 2026/27 (G1+G2)">🧤 26/27: ${p.clean_sheets_2627} CS | ${p.parate_2627} Par | ${p.gol_subiti_2627} GS</span>`;
        } else {
            const gText = p.gol_2627 > 0 ? `<b>${p.gol_2627} G</b>` : `0G`;
            const aText = p.assist_2627 > 0 ? `<b>${p.assist_2627} A</b>` : `0A`;
            const colorClass = (p.gol_2627 > 0 || p.assist_2627 > 0) ? 'gold' : 'dim';
            liveBadge2627 = `<span class="sb-prio-badge ${colorClass}" title="Dati Reali Serie A 2026/27 (G1+G2)">🔥 26/27: ${gText}/${aText} (${p.presenze_2627}P, ${p.minuti_2627}')</span>`;
        }
    }

    if (p.has_data_2526) {
        if (p.role === 'P') {
            statsShort = `CS 25/26: <b>${p.clean_sheets_2526 || 0}</b> | % Par: <b>${p.save_pct_2526 || 0}%</b> | FM: <b>${p.fm || '-'}</b>`;
        } else {
            statsShort = `G/A 25/26: <b>${p.gf}/${p.ass}</b> | xG: <b>${p.xg90_2526 || 0}</b> | xA: <b>${p.xa90_2526 || 0}</b> | FM: <b>${p.fm || '-'}</b>`;
        }
    } else {
        statsShort = `<span style="color:#a78bfa;">✨ Nuovo 26/27</span> | FM: <b>${p.fm || '-'}</b>`;
    }

    let actionsHtml = '';
    if (isBought) {
        actionsHtml = `<span style="color:#4ade80;font-weight:800;font-size:11px;">✓ NELLA TUA ROSA</span>`;
    } else if (isTaken) {
        actionsHtml = `
            <div style="display:flex;align-items:center;gap:4px;">
                <span style="color:#ef4444;font-weight:800;font-size:10.5px;">⛔ ALTRI</span>
                <button class="roster-del-btn" title="Annulla" onclick="unmarkPlayerTaken(${p.id})">↩️</button>
            </div>
        `;
    } else {
        actionsHtml = `
            <div style="display:flex;gap:4px;align-items:center;">
                <button class="sb-row-btn-buy" onclick="quickBuyPlayer('${p.name}')">+ Compra</button>
                <button class="sb-row-btn-taken" onclick="openRivalAssignModal(${p.id})" title="Assegna a un rivale">⛔ Altri</button>
            </div>
        `;
    }

    const roleBadgeHtml = State.systemMode === 'mantra'
        ? renderMantraRoleBadges(p.mantra)
        : `<span class="role-badge ${p.role}">${p.role}</span>`;

    return `
        <div class="sb-unified-row ${isBought ? 'bought' : ''} ${isTaken ? 'taken' : ''}">
            <div class="sb-row-left">
                ${roleBadgeHtml}
                <button class="sb-star-toggle ${starClass}" onclick="toggleFavorite(${p.id})" title="Preferito">${starIcon}</button>
                <div style="min-width:0;">
                    <b class="sb-unified-name" onclick="openPlayerProfileModal(${p.id})" title="Apri Scheda Calciatore">${p.name}</b>
                    <span class="sb-unified-team">(${p.team})</span>
                    ${State.systemMode === 'classic' ? `<span style="font-size:10.5px;color:var(--text-muted);">${p.mantra || ''}</span>` : ''}
                </div>
            </div>

            <div class="sb-row-mid">
                ${liveBadge2627}
                ${prioBadge}
                <span class="sb-advice-tag ${p.ai_advice_type || 'regular'}">${p.ai_advice || p.consiglio}</span>
                <span title="Fragilità: ${p.fragilita_val || ''}" style="cursor:help;font-size:13px;">${fragIcon}</span>
                ${p.is_injured ? `<span style="color:#f87171;font-size:10px;font-weight:700;">🏥 ${p.infortunio_rientro}</span>` : ''}
                <span class="sb-row-stats">${statsShort}</span>
            </div>

            <div class="sb-row-right">
                <span class="ovr-pill ${topOvrClass}">${p.ovr}</span>
                <span class="price-pill">${p.prezzo_cons} CR</span>
                ${actionsHtml}
            </div>
        </div>
    `;
}

// -----------------------------------------------------------------------------
// 2. VISTA A GRIGLIA (SCHEDE CARD)
// -----------------------------------------------------------------------------
function renderUnifiedPlayerCard(p) {
    const isFav = isFavorite(p.id);
    const isBought = isPlayerBought(p.id);
    const isTaken = isPlayerTakenByOther(p.id);
    const starIcon = isFav ? '⭐' : '☆';
    const starClass = isFav ? 'active' : '';

    const fragIcon = p.fragilita_badge === 'alta' ? '🔴' : (p.fragilita_badge === 'media' ? '🟡' : '🟢');
    const topOvrClass = getOvrClass(p.ovr);

    let prioBadge = '';
    if (p.role === 'P' && State.slots.P.players.length === 1) {
        const team1 = State.slots.P.players[0].team;
        if (p.team === team1) prioBadge = `<span class="sb-prio-badge safe">🛡️ Copertura ${team1}</span>`;
        else if (typeof GK_DATA !== 'undefined' && GK_DATA.matrix && GK_DATA.matrix[team1]) {
            const dis = GK_DATA.matrix[team1][p.team];
            if (dis !== undefined) prioBadge = `<span class="sb-prio-badge incrocio">🗓️ Incrocio (Disall.: ${dis})</span>`;
        }
    } else if (p.rigorista_val && p.rigorista_val.includes('1°')) {
        prioBadge = `<span class="sb-prio-badge gold">🎯 1° Rigorista</span>`;
    } else if (p.ovr >= 92) {
        prioBadge = `<span class="sb-prio-badge purple">👑 1° Slot Bomber</span>`;
    } else if (p.ovr >= 85 && p.role === 'D') {
        prioBadge = `<span class="sb-prio-badge green">👑 Top Modificatore</span>`;
    } else if (p.xa90_2526 >= 0.12 || p.oop_val !== '-') {
        prioBadge = `<span class="sb-prio-badge cyan">🪄 Terzino da Bonus</span>`;
    } else if (p.prezzo_cons <= 5) {
        prioBadge = `<span class="sb-prio-badge dim">💎 Low Cost / Sleeper</span>`;
    }

    let statsRow = '';
    if (p.has_data_2526) {
        if (p.role === 'P') {
            statsRow = `<span>CS: <b>${p.clean_sheets_2526 || 0}</b></span> • <span>% Parate: <b>${p.save_pct_2526 || 0}%</b></span> • <span>FM: <b>${p.fm || '-'}</b></span>`;
        } else {
            statsRow = `<span>G/A: <b>${p.gf}/${p.ass}</b></span> • <span>xG90: <b>${p.xg90_2526 || 0}</b></span> • <span>xA90: <b>${p.xa90_2526 || 0}</b></span> • <span>FM: <b>${p.fm || '-'}</b></span>`;
        }
    } else {
        statsRow = `<span style="color:#a78bfa;">✨ Nuovo 2026/27</span> • <span>FM: <b>${p.fm || '-'}</b></span>`;
    }

    let actionsHtml = '';
    if (isBought) {
        actionsHtml = `<span style="color:#4ade80;font-weight:800;font-size:11px;">✓ NELLA TUA ROSA</span>`;
    } else if (isTaken) {
        actionsHtml = `
            <div style="display:flex;align-items:center;gap:4px;">
                <span style="color:#ef4444;font-weight:800;font-size:10.5px;">⛔ PRESO DA ALTRI</span>
                <button class="roster-del-btn" title="Annulla" onclick="unmarkPlayerTaken(${p.id})">↩️</button>
            </div>
        `;
    } else {
        actionsHtml = `
            <div style="display:flex;gap:4px;width:100%;">
                <button class="sb-card-btn-buy" onclick="quickBuyPlayer('${p.name}')">+ Compra (Mio)</button>
                <button class="sb-card-btn-taken" onclick="openRivalAssignModal(${p.id})">🚫 Altri</button>
            </div>
        `;
    }

    const roleBadgeHtml = State.systemMode === 'mantra'
        ? renderMantraRoleBadges(p.mantra)
        : `<span class="role-badge ${p.role}">${p.role}</span>`;

    return `
        <div class="sb-unified-card ${isBought ? 'bought' : ''} ${isTaken ? 'taken' : ''}">
            <div class="sb-unified-card-header">
                <div style="display:flex;align-items:center;gap:6px;">
                    ${roleBadgeHtml}
                    <button class="sb-star-toggle ${starClass}" onclick="toggleFavorite(${p.id})" title="Aggiungi / Rimuovi dai Preferiti">${starIcon}</button>
                    <div>
                        <b class="sb-unified-name" onclick="openPlayerProfileModal(${p.id})" title="Apri Scheda Calciatore">${p.name}</b>
                        <span class="sb-unified-team">(${p.team})</span>
                        ${State.systemMode === 'classic' ? `<span style="font-size:10.5px;color:var(--text-muted);">${p.mantra || ''}</span>` : ''}
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span class="ovr-pill ${topOvrClass}">${p.ovr}</span>
                    <span class="price-pill">${p.prezzo_cons} CR</span>
                </div>
            </div>

            <div class="sb-unified-card-body">
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                    ${prioBadge}
                    <span class="sb-advice-tag ${p.ai_advice_type || 'regular'}">${p.ai_advice || p.consiglio}</span>
                    <span title="Fragilità: ${p.fragilita_val || ''}" style="cursor:help;font-size:13px;">${fragIcon}</span>
                    ${p.is_injured ? `<span style="color:#f87171;font-size:10.5px;font-weight:700;">🏥 ${p.infortunio_rientro}</span>` : ''}
                </div>

                <div class="sb-unified-stats-row">
                    ${statsRow}
                </div>
            </div>

            <div class="sb-unified-card-footer">
                ${actionsHtml}
            </div>
        </div>
    `;
}

function resetSbFilters() {
    State.sbRole = 'ALL';
    State.sbAdvice = 'ALL';
    State.sbOnlyFav = false;
    State.sbOnlyAvail = false;
    State.sbQuery = '';
    const inp = document.getElementById('sbUnifiedSearchInput');
    if (inp) inp.value = '';
    const sel = document.getElementById('sbAdviceFilterSelect');
    if (sel) sel.value = 'ALL';
    updateSbRolePillsUI();
    updateSbFavButtonUI();
    updateSbAvailButtonUI();
    renderSquadBuilderList();
}

// -----------------------------------------------------------------------------
// RENDER COMPACT SLOTS PER LA COLONNA SINISTRA
// -----------------------------------------------------------------------------
function renderCompactDepartmentSlots(role, label, maxSlots, color, slotLabels) {
    const list = State.slots[role].players || [];
    const spentDept = list.reduce((acc, p) => acc + (p.paidPrice || 0), 0);

    let html = `
        <div class="sb-dept-box-compact">
            <div class="sb-dept-header-compact">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:12px;color:${color};font-weight:800;">${label}</span>
                    <span class="sb-dept-count-compact">${list.length}/${maxSlots}</span>
                </div>
                <span style="font-size:11px;font-weight:700;color:var(--accent-gold);">${spentDept} CR</span>
            </div>
            <div class="sb-slots-list-compact">
    `;

    // Costruiamo la mappatura per piazzare ogni giocatore nel suo slot AI corrispondente
    const mappedSlots = new Array(maxSlots).fill(null);
    const unplaced = [];
    
    // 1. Assegna al posto ideale se libero
    for (let p of list) {
        const idealIdx = Math.min(Math.max(p.slot_num || 1, 1), maxSlots) - 1;
        if (!mappedSlots[idealIdx]) {
            mappedSlots[idealIdx] = p;
        } else {
            unplaced.push(p);
        }
    }
    
    // 2. Colma i buchi con chi ha trovato lo slot occupato (es. due top acquisti)
    for (let p of unplaced) {
        for (let i = 0; i < maxSlots; i++) {
            if (!mappedSlots[i]) {
                mappedSlots[i] = p;
                break;
            }
        }
    }

    for (let i = 0; i < maxSlots; i++) {
        const p = mappedSlots[i];
        if (p) {
            const fragIcon = p.fragilita_badge === 'alta' ? '🔴' : (p.fragilita_badge === 'media' ? '🟡' : '🟢');
            const originalIdx = list.indexOf(p);
            html += `
                <div class="sb-slot-card-compact filled">
                    <div class="sb-slot-left-compact">
                        <span class="role-badge-mini ${role}">${role}</span>
                        <div style="min-width:0;line-height:1.2;">
                            <div style="display:flex;align-items:center;gap:4px;">
                                <b style="color:#fff;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.name}</b>
                                <span style="font-size:10px;color:var(--text-secondary);">(${p.team})</span>
                                <span style="font-size:11px;">${fragIcon}</span>
                            </div>
                            <div style="font-size:10px;color:var(--text-muted);">
                                OVR <b>${p.ovr}</b> | FM: <b>${p.fm > 0 ? p.fm : '-'}</b>
                            </div>
                        </div>
                    </div>
                    <div class="sb-slot-right-compact">
                        <span class="sb-price-tag-compact">${p.paidPrice} CR</span>
                        <button class="roster-del-btn-compact" title="Rimuovi" onclick="removePlayerFromRoster('${role}', ${originalIdx}); renderSquadBuilder();">✕</button>
                    </div>
                </div>
            `;
        } else {
            const placeholder = slotLabels[i] || `Slot ${i + 1} Libero`;
            html += `
                <div class="sb-slot-card-compact empty">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span class="sb-empty-dot-mini">+</span>
                        <span style="font-size:10.5px;color:var(--text-muted);">${placeholder}</span>
                    </div>
                    <span style="font-size:9.5px;color:rgba(255,255,255,0.2);">Libero</span>
                </div>
            `;
        }
    }

    html += `
            </div>
        </div>
    `;
    return html;
}

function renderCompactMantraGoalkeeperSlots() {
    const list = State.slots.P.players || [];
    const spentGk = list.reduce((acc, p) => acc + (p.paidPrice || 0), 0);
    const maxSlots = 3;
    const slotLabels = ['1° Portiere', '2° Portiere', '3° Portiere'];

    let html = `
        <div class="sb-dept-box-compact">
            <div class="sb-dept-header-compact">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:12px;color:var(--mantra-por);font-weight:800;">🧤 Portieri (Por)</span>
                    <span class="sb-dept-count-compact">${list.length}/${maxSlots}</span>
                </div>
                <span style="font-size:11px;font-weight:700;color:var(--accent-gold);">${spentGk} CR</span>
            </div>
            <div class="sb-slots-list-compact">
    `;

    for (let i = 0; i < maxSlots; i++) {
        const p = list[i];
        if (p) {
            const fragIcon = p.fragilita_badge === 'alta' ? '🔴' : (p.fragilita_badge === 'media' ? '🟡' : '🟢');
            html += `
                <div class="sb-slot-card-compact filled">
                    <div class="sb-slot-left-compact">
                        <span class="role-badge-mini P" style="background:var(--mantra-por);color:#fff;">Por</span>
                        <div style="min-width:0;line-height:1.2;">
                            <div style="display:flex;align-items:center;gap:4px;">
                                <b style="color:#fff;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                <span style="font-size:10px;color:var(--text-secondary);">(${p.team})</span>
                                <span style="font-size:11px;">${fragIcon}</span>
                            </div>
                            <div style="font-size:10px;color:var(--text-muted);">
                                OVR <b>${p.ovr}</b> | FM: <b>${p.fm > 0 ? p.fm : '-'}</b>
                            </div>
                        </div>
                    </div>
                    <div class="sb-slot-right-compact">
                        <span class="sb-price-tag-compact">${p.paidPrice} CR</span>
                        <button class="roster-del-btn-compact" title="Rimuovi portiere" onclick="removePlayerById(${p.id}); renderSquadBuilder();">✕</button>
                    </div>
                </div>
            `;
        } else {
            const placeholder = slotLabels[i] || `Slot ${i + 1} Libero`;
            html += `
                <div class="sb-slot-card-compact empty">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span class="sb-empty-dot-mini">+</span>
                        <span style="font-size:10.5px;color:var(--text-muted);">${placeholder}</span>
                    </div>
                    <span style="font-size:9.5px;color:rgba(255,255,255,0.2);">Libero</span>
                </div>
            `;
        }
    }

    html += `
            </div>
        </div>
    `;
    return html;
}

function renderCompactMantraMovementSlots() {
    const list = [...(State.slots.D.players || []), ...(State.slots.C.players || []), ...(State.slots.A.players || [])];
    const spentMov = list.reduce((acc, p) => acc + (p.paidPrice || 0), 0);
    const maxSlots = 28;

    // Ordina i calciatori di movimento secondo gerarchia tattica Mantra
    const sortedList = [...list].sort((a, b) => {
        const scoreA = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(a.mantra) : 50;
        const scoreB = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(b.mantra) : 50;
        if (scoreA !== scoreB) return scoreA - scoreB;
        if ((b.paidPrice || 0) !== (a.paidPrice || 0)) return (b.paidPrice || 0) - (a.paidPrice || 0);
        return (b.ovr || 0) - (a.ovr || 0);
    });

    let html = `
        <div class="sb-dept-box-compact">
            <div class="sb-dept-header-compact" style="background:linear-gradient(90deg, rgba(2,132,199,0.18), rgba(139,92,246,0.12));">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:12px;color:var(--accent-cyan);font-weight:800;">🏃‍♂️ Giocatori Movimento</span>
                    <span class="sb-dept-count-compact">${sortedList.length}/${maxSlots}</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:9.5px;color:var(--text-muted);">In Ordine Mantra</span>
                    <span style="font-size:11px;font-weight:700;color:var(--accent-gold);">${spentMov} CR</span>
                </div>
            </div>
            <div class="sb-slots-list-compact" style="max-height: 520px; overflow-y: auto;">
    `;

    for (let i = 0; i < maxSlots; i++) {
        const p = sortedList[i];
        if (p) {
            const fragIcon = p.fragilita_badge === 'alta' ? '🔴' : (p.fragilita_badge === 'media' ? '🟡' : '🟢');
            const mantraBadges = (typeof renderMantraRoleBadges === 'function') ? renderMantraRoleBadges(p.mantra) : `<span class="role-badge ${p.role}">${p.role}</span>`;
            html += `
                <div class="sb-slot-card-compact filled" style="padding:5px 8px;">
                    <div class="sb-slot-left-compact">
                        <div style="display:flex;align-items:center;gap:4px;flex-shrink:0;">
                            ${mantraBadges}
                        </div>
                        <div style="min-width:0;line-height:1.2;">
                            <div style="display:flex;align-items:center;gap:4px;">
                                <b style="color:#fff;font-size:11.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                <span style="font-size:10px;color:var(--text-secondary);">(${p.team})</span>
                                <span style="font-size:11px;">${fragIcon}</span>
                            </div>
                            <div style="font-size:10px;color:var(--text-muted);">
                                OVR <b>${p.ovr}</b> | FM: <b>${p.fm > 0 ? p.fm : '-'}</b>
                            </div>
                        </div>
                    </div>
                    <div class="sb-slot-right-compact">
                        <span class="sb-price-tag-compact">${p.paidPrice} CR</span>
                        <button class="roster-del-btn-compact" title="Rimuovi calciatore" onclick="removePlayerById(${p.id}); renderSquadBuilder();">✕</button>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="sb-slot-card-compact empty">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span class="sb-empty-dot-mini">+</span>
                        <span style="font-size:10px;color:var(--text-muted);">Slot Movimento ${i + 1} Libero</span>
                    </div>
                    <span style="font-size:9px;color:rgba(255,255,255,0.2);">Libero</span>
                </div>
            `;
        }
    }

    html += `
            </div>
        </div>
    `;
    return html;
}

function quickBuyPlayer(playerName) {
    const player = PLAYERS.find(p => p.name.toLowerCase() === playerName.toLowerCase());
    if (!player) return;
    buyPlayer(player.id);
    renderSquadBuilder();
}

function clearAllTaken() {
    if (typeof confirmResetRivalsTaken === 'function') {
        confirmResetRivalsTaken();
        return;
    }
    if (!confirm('Vuoi ripristinare tutti i calciatori segnati come presi da altre squadre?')) return;
    State.takenByOthers = [];
    State.rivalAssignments = {};
    State.rivals = JSON.parse(JSON.stringify(RIVALS_TEMPLATE));
    saveStateToStorage();
    updateAllViews();
}

// ==============================================================================
// MODALE 1: ASSEGNAZIONE GIOCATORE AI 7 RIVALI
// ==============================================================================
function openRivalAssignModal(playerId) {
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;

    let modal = document.getElementById('rivalAssignModal');
    let content = document.getElementById('rivalAssignModalContent');
    if (!modal || !content) {
        modal = document.getElementById('sbGenericModal');
        content = document.getElementById('sbModalContent');
    }
    if (!modal || !content) return;

    const rivalsList = Object.keys(State.rivals || RIVALS_TEMPLATE);

    let rivalsBtnsHtml = rivalsList.map(rName => {
        const rData = State.rivals[rName];
        const rSpent = rData.spent || 0;
        const rRem = (rData.budget || 1000) - rSpent;
        const count = rData.players ? rData.players.length : 0;
        return `
            <button type="button" class="sb-rival-select-btn" onclick="submitRivalAssign(${p.id}, '${rName}')">
                <div style="text-align:left;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:15px;">🛡️</span>
                        <b style="color:#fff;font-size:13px;">${rName}</b>
                    </div>
                    <div style="font-size:10.5px;color:var(--text-secondary);margin-top:3px;line-height:1.3;">
                        Manager: <b style="color:var(--accent-cyan);">${rData.manager}</b> &nbsp;•&nbsp; ${rData.tendency}
                    </div>
                </div>
                <div style="text-align:right;min-width:85px;">
                    <div style="color:var(--accent-gold);font-weight:900;font-size:13.5px;font-family:'Outfit',sans-serif;">${rRem} CR</div>
                    <div style="font-size:10px;color:var(--text-muted);margin-top:2px;">${count} / 25 presi</div>
                </div>
            </button>
        `;
    }).join('');

    content.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px;margin-bottom:14px;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:22px;">🕵️</span>
                    <h3 style="margin:0;font-size:17px;font-weight:900;color:var(--accent-cyan);">Assegna a Squadra Rivale</h3>
                </div>
                <div style="margin-top:4px;font-size:12.5px;color:var(--text-secondary);">
                    Calciatore: <b style="color:#fff;">${p.name}</b> (${p.team}) &nbsp;•&nbsp; <span class="role-badge ${p.role}" style="font-size:11px;padding:1px 6px;">${p.role}</span> &nbsp;•&nbsp; Consigliato: <b style="color:#fbbf24;">${p.prezzo_cons || 1} CR</b>
                </div>
            </div>
            <button class="btn-action" style="padding:4px 10px;font-size:12px;" onclick="closeRivalAssignModal()">Chiudi ✕</button>
        </div>

        <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px 14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <label style="font-size:12px;color:var(--text-secondary);font-weight:800;">PREZZO PAGATO:</label>
                <div style="display:flex;align-items:center;">
                    <button type="button" onclick="adjustRivalPrice(-1)" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#fff;font-weight:900;padding:4px 9px;border-radius:6px 0 0 6px;cursor:pointer;">-</button>
                    <input type="number" id="rivalPaidPriceInput" value="${p.prezzo_cons || 1}" min="1" max="1000" style="width:70px;background:rgba(0,0,0,0.6);border-top:1px solid rgba(255,255,255,0.15);border-bottom:1px solid rgba(255,255,255,0.15);border-left:none;border-right:none;color:#fbbf24;font-size:14px;font-weight:900;text-align:center;padding:4px 0;outline:none;">
                    <button type="button" onclick="adjustRivalPrice(1)" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#fff;font-weight:900;padding:4px 9px;border-radius:0 6px 6px 0;cursor:pointer;">+</button>
                </div>
                <span style="font-size:12px;color:var(--accent-gold);font-weight:800;">CR</span>
            </div>

            <button type="button" class="btn-action" style="margin-left:auto;background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.15);font-size:11.5px;padding:6px 12px;" onclick="submitRivalAssign(${p.id}, null)" title="Segna come acquistato da altri ma senza specificare la squadra">
                👤 Altro Generico (Senza Rivale)
            </button>
        </div>

        <div style="font-size:11px;font-weight:800;color:var(--text-muted);letter-spacing:0.5px;text-transform:uppercase;margin-bottom:6px;">
            SCEGLI LA SQUADRA RIVALE CHE LO HA PRESO:
        </div>

        <div class="sb-rivals-grid-select">
            ${rivalsBtnsHtml}
        </div>
    `;

    modal.style.display = 'flex';
}

function adjustRivalPrice(delta) {
    const input = document.getElementById('rivalPaidPriceInput');
    if (!input) return;
    let val = parseInt(input.value, 10) || 1;
    val = Math.max(1, val + delta);
    input.value = val;
}

function submitRivalAssign(playerId, rivalName) {
    const priceInput = document.getElementById('rivalPaidPriceInput');
    const price = priceInput ? parseInt(priceInput.value, 10) || 1 : null;
    markPlayerTaken(playerId, rivalName, price);
    closeRivalAssignModal();
    if (typeof renderGemsTab === 'function') renderGemsTab();
    if (typeof renderTeamRosterTable === 'function' && State.currentTeamPitch) renderTeamRosterTable(State.currentTeamPitch);
}

function closeRivalAssignModal() {
    const modal = document.getElementById('rivalAssignModal');
    if (modal) modal.style.display = 'none';
    closeSbModal();
}

function closeSbModal() {
    const modal = document.getElementById('sbGenericModal');
    if (modal) modal.style.display = 'none';
    const content = document.getElementById('sbModalContent');
    if (content) content.classList.remove('sb-modal-large');
    const rModal = document.getElementById('rivalAssignModal');
    if (rModal) rModal.style.display = 'none';
}

// ==============================================================================
// MODALE 2: RADAR SPIONAGGIO AVVERSARI
// ==============================================================================
function openRivalsRadarModal() {
    const modal = document.getElementById('sbGenericModal');
    const content = document.getElementById('sbModalContent');
    if (!modal || !content) return;

    const rivalsList = Object.keys(State.rivals || RIVALS_TEMPLATE);
    
    const sortedRivals = rivalsList.map(rName => {
        const rData = State.rivals[rName];
        const spent = rData.spent || 0;
        const rem = 1000 - spent;
        return { name: rName, ...rData, remaining: rem };
    }).sort((a, b) => b.remaining - a.remaining);

    let rowsHtml = sortedRivals.map((r, idx) => {
        const pCount = { P: 0, D: 0, C: 0, A: 0 };
        r.players.forEach(pl => {
            const full = PLAYERS.find(p => p.id === pl.id);
            if (full && pCount[full.role] !== undefined) pCount[full.role]++;
        });

        let alertBadge = '';
        if (pCount.A === 0 && r.remaining >= 350) {
            alertBadge = `<span class="sb-threat-badge high">🔥 PERICOLO ATTACCO (Ha ${r.remaining} CR e 0 Punte)</span>`;
        } else if (pCount.P === 3) {
            alertBadge = `<span class="sb-threat-badge safe">🧤 Portieri Completi (3/3)</span>`;
        } else if (r.remaining >= 600) {
            alertBadge = `<span class="sb-threat-badge mid">💰 Cassaforte Asta (${r.remaining} CR liberi)</span>`;
        } else {
            alertBadge = `<span class="sb-threat-badge low">📊 In Gestione (${r.players.length}/25 slot)</span>`;
        }

        return `
            <div class="sb-rival-radar-card">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:14px;font-weight:900;color:var(--accent-cyan);">#${idx + 1}</span>
                        <div>
                            <b style="color:#fff;font-size:13px;">${r.name}</b>
                            <div style="font-size:10.5px;color:var(--text-secondary);">${r.tendency}</div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:14px;font-weight:900;color:var(--accent-gold);">${r.remaining} <small>CR</small></span>
                        <div style="font-size:10px;color:var(--text-muted);">Spesi: ${r.spent} CR</div>
                    </div>
                </div>

                <div style="display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.06);">
                    <div style="display:flex;gap:6px;font-size:11px;">
                        <span style="color:var(--role-p);">🧤 ${pCount.P}/3</span>
                        <span style="color:var(--role-d);">🛡️ ${pCount.D}/8</span>
                        <span style="color:var(--role-c);">🪄 ${pCount.C}/8</span>
                        <span style="color:var(--role-a);">⚡ ${pCount.A}/6</span>
                    </div>
                    ${alertBadge}
                </div>
            </div>
        `;
    }).join('');

    content.innerHTML = `
        <div class="sb-modal-header">
            <div>
                <h3 style="margin:0;font-size:16px;color:var(--accent-cyan);">🕵️ Radar & Spionaggio 7 Manager Rivali</h3>
                <p style="margin:0;font-size:11.5px;color:var(--text-secondary);">Budget residui, slot occupati e predizione delle prossime offerte</p>
            </div>
            <button class="sb-modal-close" onclick="closeSbModal()">✕</button>
        </div>

        <div style="display:flex;flex-direction:column;gap:8px;margin-top:12px;max-height:550px;overflow-y:auto;">
            ${rowsHtml}
        </div>
    `;

    modal.style.display = 'flex';
}

// ==============================================================================
// REGOLA MANTRA 5.3: VERIFICA COMPATIBILITÀ E ADATTABILITÀ RUOLI FUORI POSIZIONE
// ==============================================================================
function checkMantraSlotCompatibility(player, slot) {
    if (!player || !slot) return { allowed: false };
    const pRoles = (player.mantra || '').split(';').map(r => r.trim()).filter(Boolean);
    
    // 1. Ruolo naturale (nessun malus)
    if (slot.roles.some(r => pRoles.includes(r))) {
        return { allowed: true, isAdapted: false, malus: 0 };
    }

    // 2. Portiere: nessuna adattabilità permessa
    if (slot.roles.includes('Por') || pRoles.includes('Por')) {
        return { allowed: false };
    }

    // 3. REGOLA 5.3: INIBIZIONI ASSOLUTE IN FASE DI INSERIMENTO FORMAZIONE
    // - Inibito schierare B, Dd o Ds in posizione Dc
    const isPureDcSlot = slot.roles.length === 1 && slot.roles[0] === 'Dc';
    if (isPureDcSlot && !pRoles.includes('Dc')) {
        if (pRoles.some(r => ['B', 'Dd', 'Ds'].includes(r))) {
            return { allowed: false };
        }
    }

    // - Inibito schierare Dd in posizione Ds e viceversa
    if (slot.roles.includes('Ds') && !pRoles.includes('Ds') && pRoles.includes('Dd')) {
        return { allowed: false };
    }
    if (slot.roles.includes('Dd') && !pRoles.includes('Dd') && pRoles.includes('Ds')) {
        return { allowed: false };
    }

    // - Inibito schierare E in posizione M pura (rimane possibile in posizione M/C)
    const isPureMSlot = slot.roles.length === 1 && slot.roles[0] === 'M';
    if (isPureMSlot && pRoles.includes('E') && !pRoles.includes('M')) {
        return { allowed: false };
    }

    // - Inibito schierare M in posizione E pura (rimane possibile in posizione E/W)
    const isPureESlot = slot.roles.length === 1 && slot.roles[0] === 'E';
    if (isPureESlot && pRoles.includes('M') && !pRoles.includes('E')) {
        return { allowed: false };
    }

    // - Inibito schierare W in posizione T pura (rimane possibile in posizione T/A)
    const isPureTSlot = slot.roles.length === 1 && slot.roles[0] === 'T';
    if (isPureTSlot && pRoles.includes('W') && !pRoles.includes('T')) {
        return { allowed: false };
    }

    // 4. ADATTABILITÀ CONSENTITE DALLA TABELLA MANTRA (CON AGGRAVIO MALUS 1 PUNTO)
    const ADAPT_MAP = {
        'Dd': ['E'],
        'Ds': ['E'],
        'E': ['M', 'C', 'W'], // E in M/C consentito (inibito in M pura)
        'M': ['C', 'E'],      // M in E/W consentito (inibito in E pura)
        'C': ['M', 'T'],
        'T': ['C', 'W', 'A'],
        'W': ['A', 'E', 'T'], // W in T/A consentito (inibito in T pura)
        'A': ['Pc', 'T', 'W'],
        'Pc': ['A']
    };

    for (const r of pRoles) {
        const targets = ADAPT_MAP[r] || [];
        if (slot.roles.some(target => targets.includes(target))) {
            return { allowed: true, isAdapted: true, malus: 1 };
        }
    }

    return { allowed: false };
}

// Helper: Risolutore Algoritmico Ottimale per Formazioni Mantra
function solveOptimalMantraFormation(schema, allBought) {
    const slots = schema.slots;
    const nSlots = slots.length;
    let bestScore = -1;
    let bestCount = -1;
    let bestAssignment = new Array(nSlots).fill(null);

    // Costruisci candidati per ciascuno slot (priorità assoluta ai ruoli naturali, poi adattati con malus)
    const candidatesPerSlot = slots.map((slot) => {
        const list = [];
        for (const p of allBought) {
            const compat = checkMantraSlotCompatibility(p, slot);
            if (compat.allowed) {
                // Penalità di 15 punti OVR per i fuori posizione: garantisce che i naturali vincano sempre
                const effectiveOvr = (p.ovr || 60) - (compat.isAdapted ? 15 : 0);
                list.push({
                    ...p,
                    isAdapted: compat.isAdapted,
                    malus: compat.malus,
                    effectiveOvr
                });
            }
        }
        return list.sort((a, b) => b.effectiveOvr - a.effectiveOvr);
    });

    const currentAssignment = new Array(nSlots).fill(null);
    const used = new Set();

    function backtrack(sIdx, currentScore, currentCount) {
        if (sIdx === nSlots) {
            if (currentCount > bestCount || (currentCount === bestCount && currentScore > bestScore)) {
                bestCount = currentCount;
                bestScore = currentScore;
                bestAssignment = [...currentAssignment];
            }
            return;
        }

        let maxPossibleScore = currentScore;
        let maxPossibleCount = currentCount;
        for (let j = sIdx; j < nSlots; j++) {
            let maxOvr = 0;
            let canPlace = false;
            for (const cand of candidatesPerSlot[j]) {
                if (!used.has(cand.id)) {
                    canPlace = true;
                    if ((cand.effectiveOvr || 0) > maxOvr) maxOvr = cand.effectiveOvr || 0;
                }
            }
            if (canPlace) {
                maxPossibleCount++;
                maxPossibleScore += maxOvr;
            }
        }

        if (maxPossibleCount < bestCount) return;
        if (maxPossibleCount === bestCount && maxPossibleScore <= bestScore) return;

        // Prova i migliori candidati per questo slot (fino a 6 per contenere la combinatoria)
        const cands = candidatesPerSlot[sIdx].slice(0, 6);
        for (const cand of cands) {
            if (!used.has(cand.id)) {
                used.add(cand.id);
                currentAssignment[sIdx] = { 
                    player: cand, 
                    slot: slots[sIdx], 
                    isAdapted: cand.isAdapted, 
                    malus: cand.malus 
                };
                backtrack(sIdx + 1, currentScore + (cand.effectiveOvr || 0), currentCount + 1);
                used.delete(cand.id);
                currentAssignment[sIdx] = null;
            }
        }

        // Ramo con slot vuoto/libero
        currentAssignment[sIdx] = { player: null, slot: slots[sIdx], isAdapted: false, malus: 0 };
        backtrack(sIdx + 1, currentScore, currentCount);
    }

    backtrack(0, 0, 0);

    const naturalCount = bestAssignment.filter(a => a && a.player && !a.isAdapted).length;
    const adaptedCount = bestAssignment.filter(a => a && a.player && a.isAdapted).length;

    return { 
        assignment: bestAssignment, 
        score: bestScore, 
        count: bestCount, 
        naturalCount, 
        adaptedCount 
    };
}

// ==============================================================================
// MODALE 3: MIGLIOR 11 TITOLARE AI (CON SCELTA MANUALE & REGOLA DEL RUOLO)
// ==============================================================================

const BEST11_CUSTOM_STORAGE_KEY = 'FANTA_MASTER_BEST11_CUSTOM_V1';

function getBest11CustomSelections() {
    try {
        const raw = localStorage.getItem(BEST11_CUSTOM_STORAGE_KEY);
        const all = raw ? JSON.parse(raw) : {};
        const leagueKey = (typeof State !== 'undefined' && State.activeLeagueId) ? State.activeLeagueId : 'default';
        return all[leagueKey] || {};
    } catch (e) {
        return {};
    }
}

function saveBest11CustomSelections(sel) {
    try {
        const raw = localStorage.getItem(BEST11_CUSTOM_STORAGE_KEY);
        const all = raw ? JSON.parse(raw) : {};
        const leagueKey = (typeof State !== 'undefined' && State.activeLeagueId) ? State.activeLeagueId : 'default';
        all[leagueKey] = sel;
        localStorage.setItem(BEST11_CUSTOM_STORAGE_KEY, JSON.stringify(all));
    } catch (e) {}
}

function setBest11CustomSlot(modName, slotIdx, playerId) {
    const allCustom = getBest11CustomSelections();
    if (!allCustom[modName]) allCustom[modName] = {};
    allCustom[modName][slotIdx] = playerId;
    saveBest11CustomSelections(allCustom);
    closeBest11PickerModal();
    openBest11Modal(modName);
}

function revertBest11Slot(modName, slotIdx) {
    const allCustom = getBest11CustomSelections();
    if (allCustom[modName] && allCustom[modName][slotIdx] !== undefined) {
        delete allCustom[modName][slotIdx];
        saveBest11CustomSelections(allCustom);
        openBest11Modal(modName);
    }
}

function resetBest11ModToAuto(modName) {
    const allCustom = getBest11CustomSelections();
    if (allCustom[modName]) {
        delete allCustom[modName];
        saveBest11CustomSelections(allCustom);
        openBest11Modal(modName);
    }
}

function openBest11Modal(preferredFormation = null) {
    const modal = document.getElementById('sbGenericModal');
    const content = document.getElementById('sbModalContent');
    if (!modal || !content) return;

    const allBought = [...State.slots.P.players, ...State.slots.D.players, ...State.slots.C.players, ...State.slots.A.players];
    if (allBought.length === 0) {
        alert("Acquista prima qualche calciatore nella tua rosa per calcolare la Top 11!");
        return;
    }

    // Allarga e ottimizza visibilità modale a 2 colonne
    content.classList.add('sb-modal-large');

    const customSelectionsAll = getBest11CustomSelections();

    if (State.systemMode === 'mantra') {
        const mantraMods = Object.keys(MANTRA_FORMATIONS);
        let bestMod = preferredFormation;

        // Se non è specificato un modulo preferito, calcola il punteggio su tutti gli 11 moduli e scegli il migliore
        if (!bestMod || !MANTRA_FORMATIONS[bestMod]) {
            let maxCount = -1;
            let maxScore = -1;
            bestMod = '4-3-3';
            for (const mod of mantraMods) {
                const sch = MANTRA_FORMATIONS[mod];
                const res = solveOptimalMantraFormation(sch, allBought);
                if (res.count > maxCount || (res.count === maxCount && res.score > maxScore)) {
                    maxCount = res.count;
                    maxScore = res.score;
                    bestMod = mod;
                }
            }
        }

        const schema = MANTRA_FORMATIONS[bestMod];
        const res = solveOptimalMantraFormation(schema, allBought);
        const assigned = [...res.assignment];

        const customMod = customSelectionsAll[bestMod] || {};
        let hasCustom = false;

        // Applica le selezioni manuali dell'utente rispettando il ruolo dello slot
        Object.keys(customMod).forEach(idxStr => {
            const sIdx = parseInt(idxStr, 10);
            const customPId = customMod[sIdx];
            const customP = PLAYERS.find(pl => pl.id === customPId);
            if (customP && assigned[sIdx] && assigned[sIdx].slot) {
                const slot = assigned[sIdx].slot;
                const compat = checkMantraSlotCompatibility(customP, slot);
                if (compat.allowed) {
                    assigned[sIdx] = {
                        slot: slot,
                        player: customP,
                        isAdapted: compat.isAdapted,
                        malus: compat.malus || 0,
                        isCustom: true
                    };
                    hasCustom = true;
                }
            }
        });

        const fieldedPlayerIds = assigned.filter(a => a && a.player).map(a => a.player.id);
        const benchPlayers = allBought.filter(p => !fieldedPlayerIds.includes(p.id)).sort((a, b) => (b.ovr || 0) - (a.ovr || 0));

        const fieldedCount = assigned.filter(a => a && a.player).length;
        const adaptedCount = assigned.filter(a => a && a.player && a.isAdapted).length;
        const naturalCount = fieldedCount - adaptedCount;

        const startersList = assigned.filter(a => a && a.player).map(a => a.player);
        const avgStarterOvr = startersList.length ? (startersList.reduce((s, p) => s + (p.ovr || 70), 0) / startersList.length).toFixed(1) : '-';
        const avgBenchOvr = benchPlayers.length ? (benchPlayers.reduce((s, p) => s + (p.ovr || 70), 0) / benchPlayers.length).toFixed(1) : '-';

        const startersSummary = adaptedCount > 0 
            ? `${fieldedCount}/11 Schierati (${naturalCount} Nat., ${adaptedCount} Adatt.)`
            : `${fieldedCount}/11 Titolari (Tutti Naturali)`;

        const renderMantraPill = (item, sIdx) => {
            const isCustom = item && item.isCustom;
            if (!item || !item.player) {
                const posLbl = item && item.slot ? item.slot.pos : 'Slot';
                const rolesNeeded = item && item.slot ? item.slot.roles.join('/') : '';
                return `
                    <div class="sb-best11-pill empty" onclick="openBest11SlotPickerModal('${bestMod}', ${sIdx})" style="cursor:pointer;" title="Clicca per scegliere un calciatore per questo ruolo">
                        <span class="sb-best11-pos-badge" style="opacity:0.6;background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.2);color:var(--text-muted);">${posLbl}</span>
                        <span style="font-size:10px;color:var(--text-muted);font-weight:700;">(Libero)</span>
                        ${rolesNeeded ? `<span style="font-size:8.5px;color:rgba(255,255,255,0.4);letter-spacing:0.2px;">${rolesNeeded}</span>` : ''}
                        <button class="sb-best11-swap-btn" style="margin-top:2px;" onclick="event.stopPropagation(); openBest11SlotPickerModal('${bestMod}', ${sIdx})">
                            ➕ Scegli
                        </button>
                    </div>
                `;
            }
            const p = item.player;
            const posLbl = item.slot.pos;
            const isAdapted = item.isAdapted;

            const adaptedBadge = isAdapted ? `
                <span style="font-size:8px;font-weight:900;color:#f59e0b;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.35);padding:1px 3px;border-radius:3px;">
                    ⚠️ -1 pt
                </span>
            ` : '';

            const customTag = isCustom ? `
                <span class="sb-best11-custom-tag" title="Calciatore scelto manualmente">✏️ Manuale</span>
            ` : '';

            const ratingDisplay = isAdapted ? `
                <span class="sb-best11-ovr-tag" style="background:rgba(239,68,68,0.18);color:#fca5a5;border-color:rgba(239,68,68,0.35);" title="Punteggio decurtato per Malus Fuori Posizione (-1 punto)">
                    ⭐ ${p.ovr - 1} <small style="font-size:7.5px;opacity:0.8;">(-1)</small>
                </span>
            ` : `
                <span class="sb-best11-ovr-tag">⭐ ${p.ovr}</span>
            `;

            return `
                <div class="sb-best11-pill mantra-pill-card ${isAdapted ? 'adapted' : ''}" onclick="openBest11SlotPickerModal('${bestMod}', ${sIdx})" style="cursor:pointer;" title="Clicca per cambiare questo calciatore">
                    <div style="display:flex;align-items:center;gap:3px;flex-wrap:wrap;justify-content:center;">
                        <span class="sb-best11-pos-badge">${posLbl}</span>
                        ${adaptedBadge}
                        ${customTag}
                    </div>
                    <span class="sb-best11-player-name" title="${p.name} (${p.team || ''})">${p.name}</span>
                    <div class="sb-best11-badges-row">
                        ${renderMantraRoleBadges(p.mantra)}
                    </div>
                    <div style="display:flex;align-items:center;gap:5px;margin-top:1px;">
                        ${ratingDisplay}
                        <span style="font-size:9px;color:var(--text-muted);font-weight:600;">FM ${p.fm ? Number(p.fm).toFixed(2) : '-'}</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:3px;margin-top:3px;width:100%;justify-content:center;" onclick="event.stopPropagation()">
                        <button class="sb-best11-swap-btn" onclick="openBest11SlotPickerModal('${bestMod}', ${sIdx})" title="Cambia calciatore per il ruolo ${posLbl}">
                            🔄 Cambia
                        </button>
                        ${isCustom ? `
                            <button class="sb-best11-undo-btn" onclick="revertBest11Slot('${bestMod}', ${sIdx})" title="Ripristina consigliato AI">
                                ↺
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        };

        // Ripartizione moduli Mantra in Difesa a 3 e Difesa a 4
        const def3Mods = mantraMods.filter(m => MANTRA_FORMATIONS[m].defCount === 3);
        const def4Mods = mantraMods.filter(m => MANTRA_FORMATIONS[m].defCount === 4);

        // Rendering delle linee tattiche del campo esattamente secondo lo schema selezionato
        let slotCounter = 0;
        const pitchRowsHtml = schema.lines.map(lineSlots => {
            const rowPills = lineSlots.map(() => {
                const sIdx = slotCounter++;
                const item = assigned[sIdx];
                return renderMantraPill(item, sIdx);
            }).join('');
            return `<div class="sb-best11-row">${rowPills}</div>`;
        }).join('');

        const benchHtml = benchPlayers.length > 0 ? benchPlayers.map(bp => `
            <div class="sb-best11-bench-item" title="${bp.name} (${bp.team || ''}) - A disposizione">
                <div style="display:flex;align-items:center;gap:6px;min-width:0;flex:1;">
                    ${renderMantraRoleBadges(bp.mantra, 'mini')}
                    <div style="display:flex;flex-direction:column;min-width:0;">
                        <span style="color:#fff;font-size:11px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${bp.name}</span>
                        <span style="font-size:9px;color:var(--text-muted);">${bp.team || ''}</span>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:5px;">
                    <span class="sb-best11-ovr-tag">⭐ ${bp.ovr}</span>
                    <span style="font-size:9px;color:var(--text-muted);font-weight:600;">FM ${bp.fm ? Number(bp.fm).toFixed(2) : '-'}</span>
                </div>
            </div>
        `).join('') : `
            <div style="text-align:center;padding:16px 8px;color:var(--text-muted);font-size:11px;">
                Tutti i calciatori in rosa sono schierati nell'11 titolare.
            </div>
        `;

        content.innerHTML = `
            <!-- MODAL HEADER -->
            <div class="sb-modal-header" style="margin-bottom:0;padding-bottom:10px;">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <h3 style="margin:0;font-size:17px;color:var(--accent-cyan);display:flex;align-items:center;gap:8px;">
                        <span>⚡ Miglior 11 Mantra AI</span>
                        <span style="font-size:11px;font-weight:900;background:rgba(0,242,254,0.18);border:1px solid var(--accent-cyan);color:#fff;padding:2px 8px;border-radius:10px;">
                            Schema: ${bestMod}
                        </span>
                    </h3>
                    <span style="font-size:11px;font-weight:800;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.35);color:#34d399;padding:2px 8px;border-radius:10px;">
                        ✓ ${startersSummary}
                    </span>
                    <span style="font-size:11px;font-weight:800;background:rgba(251,191,36,0.15);border:1px solid rgba(251,191,36,0.35);color:#fbbf24;padding:2px 8px;border-radius:10px;">
                        OVR Titolari: ⭐ ${avgStarterOvr}
                    </span>
                    ${hasCustom ? `
                        <button class="sb-best11-reset-btn" onclick="resetBest11ModToAuto('${bestMod}')" title="Ripristina formazione consigliata AI">
                            ↺ Ripristina AI
                        </button>
                    ` : ''}
                </div>
                <button class="sb-modal-close" onclick="closeSbModal()">✕</button>
            </div>

            <!-- 2-COLUMN EXECUTIVE WORKSPACE -->
            <div class="sb-best11-layout">
                <!-- LEFT SIDEBAR: SCHEMI TATTICI + PANCHINA -->
                <div class="sb-best11-sidebar">
                    <!-- 1. SELETTORE SCHEMI MANTRA -->
                    <div class="sb-best11-card">
                        <div style="font-size:11px;font-weight:800;color:var(--accent-cyan);text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
                            <span>📐 Schemi Ufficiali Mantra</span>
                            <span style="font-size:9.5px;color:var(--text-muted);font-weight:600;">(11 Moduli)</span>
                        </div>

                        <!-- DIFESA A 3 -->
                        <div style="margin-bottom:8px;">
                            <div style="font-size:10px;font-weight:800;color:var(--text-muted);margin-bottom:4px;">🛡️ DIFESA A 3 (5 SCHEMI):</div>
                            <div style="display:flex;gap:4px;flex-wrap:wrap;">
                                ${def3Mods.map(m => `
                                    <button class="sb-mod-select-btn ${m === bestMod ? 'active' : ''}" onclick="openBest11Modal('${m}')">
                                        ${m}
                                    </button>
                                `).join('')}
                            </div>
                        </div>

                        <!-- DIFESA A 4 -->
                        <div>
                            <div style="font-size:10px;font-weight:800;color:var(--text-muted);margin-bottom:4px;">🛡️ DIFESA A 4 (6 SCHEMI):</div>
                            <div style="display:flex;gap:4px;flex-wrap:wrap;">
                                ${def4Mods.map(m => `
                                    <button class="sb-mod-select-btn ${m === bestMod ? 'active' : ''}" onclick="openBest11Modal('${m}')">
                                        ${m}
                                    </button>
                                `).join('')}
                            </div>
                        </div>

                        <div style="font-size:10.5px;color:var(--text-secondary);margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.06);line-height:1.3;">
                            ${schema.description}
                        </div>
                    </div>

                    <!-- 2. INFO REGOLA RUOLO -->
                    <div style="background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.25);padding:7px 10px;border-radius:8px;font-size:10.5px;color:#38bdf8;line-height:1.35;">
                        💡 <b>Regola del Ruolo:</b> Clicca su <b>'🔄 Cambia'</b> per sostituire qualsiasi titolare. Schieramento fuori ruolo consentito con <b>Malus di -1 pt</b>.
                    </div>

                    <!-- 3. PANCHINA DEI SOSTITUTI -->
                    <div class="sb-best11-card sb-best11-bench-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.08);">
                            <span style="font-size:11.5px;font-weight:800;color:#fff;">🪑 Panchina & Riserve (${benchPlayers.length})</span>
                            <span style="font-size:10px;color:var(--accent-gold);font-weight:800;">OVR Medio: ⭐ ${avgBenchOvr}</span>
                        </div>
                        <div class="sb-best11-bench-list">
                            ${benchHtml}
                        </div>
                    </div>
                </div>

                <!-- RIGHT COLUMN: CAMPO DA CALCIO FULL-HEIGHT -->
                <div class="sb-best11-pitch-area">
                    <div class="sb-best11-pitch">
                        ${pitchRowsHtml}
                    </div>
                </div>
            </div>
        `;

        modal.style.display = 'flex';
        return;
    }

    // Modalità Classic
    const gks = [...State.slots.P.players].sort((a, b) => b.ovr - a.ovr);
    const defs = [...State.slots.D.players].sort((a, b) => b.ovr - a.ovr);
    const mids = [...State.slots.C.players].sort((a, b) => b.ovr - a.ovr);
    const fwds = [...State.slots.A.players].sort((a, b) => b.ovr - a.ovr);

    const formations = {
        '3-4-3': { d: 3, c: 4, a: 3 },
        '4-3-3': { d: 4, c: 3, a: 3 },
        '3-5-2': { d: 3, c: 5, a: 2 },
        '4-4-2': { d: 4, c: 4, a: 2 },
        '4-2-3-1': { d: 4, c: 5, a: 1 }
    };

    let bestMod = preferredFormation || '3-4-3';
    if (!preferredFormation) {
        let maxScore = -1;
        for (const [mod, sch] of Object.entries(formations)) {
            if (defs.length >= sch.d && mids.length >= sch.c && fwds.length >= sch.a && gks.length >= 1) {
                const score = gks[0].ovr + 
                    defs.slice(0, sch.d).reduce((s, p) => s + p.ovr, 0) +
                    mids.slice(0, sch.c).reduce((s, p) => s + p.ovr, 0) +
                    fwds.slice(0, sch.a).reduce((s, p) => s + p.ovr, 0);
                if (score > maxScore) {
                    maxScore = score;
                    bestMod = mod;
                }
            }
        }
    }

    const schema = formations[bestMod];
    const customMod = customSelectionsAll[bestMod] || {};
    let hasCustom = false;

    const starterGkObj = { p: gks[0] || null, role: 'P', sIdx: 10 };
    const starterFwdsObjs = Array.from({ length: schema.a }).map((_, i) => ({ p: fwds[i] || null, role: 'A', sIdx: i }));
    const starterMidsObjs = Array.from({ length: schema.c }).map((_, i) => ({ p: mids[i] || null, role: 'C', sIdx: schema.a + i }));
    const starterDefsObjs = Array.from({ length: schema.d }).map((_, i) => ({ p: defs[i] || null, role: 'D', sIdx: schema.a + schema.c + i }));

    const allClassicSlots = [...starterFwdsObjs, ...starterMidsObjs, ...starterDefsObjs, starterGkObj];

    // Applica custom
    allClassicSlots.forEach(slotItem => {
        if (customMod[slotItem.sIdx] !== undefined) {
            const customP = PLAYERS.find(pl => pl.id === customMod[slotItem.sIdx]);
            if (customP && customP.role === slotItem.role) {
                slotItem.p = customP;
                slotItem.isCustom = true;
                hasCustom = true;
            }
        }
    });

    const starterGk = starterGkObj.p;
    const starterDefs = starterDefsObjs.map(s => s.p).filter(Boolean);

    let modifHtml = '';
    if (schema.d >= 4 && starterDefs.length >= 4) {
        const top3Defs = [...starterDefs].sort((a, b) => (b.fm || b.ovr) - (a.fm || a.ovr)).slice(0, 3);
        const avgDefFM = ((starterGk ? (starterGk.fm || 6.0) : 6.0) + top3Defs.reduce((s, p) => s + (p.fm || 6.0), 0)) / 4.0;
        let modBonus = '+0';
        if (avgDefFM >= 6.5) modBonus = '+6 PUNTI';
        else if (avgDefFM >= 6.25) modBonus = '+3 PUNTI';
        else if (avgDefFM >= 6.0) modBonus = '+1 PUNTO';

        modifHtml = `
            <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);padding:6px 10px;border-radius:8px;font-size:10.5px;color:#4ade80;line-height:1.35;">
                🛡️ <b>Modificatore Difesa a 4:</b> Media Voto stimata <b>${avgDefFM.toFixed(2)}</b> ➜ Bonus: <b>${modBonus}</b>
            </div>
        `;
    }

    const starterPlayerIds = allClassicSlots.filter(s => s.p).map(s => s.p.id);
    const benchPlayers = allBought.filter(p => !starterPlayerIds.includes(p.id)).sort((a, b) => (b.ovr || 0) - (a.ovr || 0));

    const startersList = allClassicSlots.filter(s => s.p).map(s => s.p);
    const avgStarterOvr = startersList.length ? (startersList.reduce((s, p) => s + (p.ovr || 70), 0) / startersList.length).toFixed(1) : '-';
    const avgBenchOvr = benchPlayers.length ? (benchPlayers.reduce((s, p) => s + (p.ovr || 70), 0) / benchPlayers.length).toFixed(1) : '-';

    const renderPlayerPill = (item) => {
        const p = item.p;
        const sIdx = item.sIdx;
        const role = item.role;
        const isCustom = item.isCustom;

        if (!p) {
            return `
                <div class="sb-best11-pill empty" onclick="openBest11SlotPickerModal('${bestMod}', ${sIdx})" style="cursor:pointer;" title="Scegli calciatore">
                    <span class="role-badge-mini ${role}">${role}</span>
                    <span style="font-size:10px;color:var(--text-muted);">(Libero)</span>
                    <button class="sb-best11-swap-btn" style="margin-top:2px;" onclick="event.stopPropagation(); openBest11SlotPickerModal('${bestMod}', ${sIdx})">
                        ➕ Scegli
                    </button>
                </div>
            `;
        }

        return `
            <div class="sb-best11-pill ${p.role}" onclick="openBest11SlotPickerModal('${bestMod}', ${sIdx})" style="cursor:pointer;" title="Clicca per cambiare questo calciatore">
                <div style="display:flex;align-items:center;gap:4px;">
                    <span class="role-badge-mini ${p.role}">${p.role}</span>
                    <span class="sb-best11-player-name" title="${p.name} (${p.team || ''})">${p.name}</span>
                </div>
                <div style="display:flex;align-items:center;gap:4px;">
                    <span class="sb-best11-ovr-tag">⭐ ${p.ovr}</span>
                    ${isCustom ? `<span class="sb-best11-custom-tag">✏️ Manuale</span>` : ''}
                    <span style="font-size:9px;color:var(--text-muted);font-weight:600;">FM ${p.fm ? Number(p.fm).toFixed(2) : '-'}</span>
                </div>
                <div style="display:flex;align-items:center;gap:3px;margin-top:3px;width:100%;justify-content:center;" onclick="event.stopPropagation()">
                    <button class="sb-best11-swap-btn" onclick="openBest11SlotPickerModal('${bestMod}', ${sIdx})" title="Cambia calciatore per questo ruolo">
                        🔄 Cambia
                    </button>
                    ${isCustom ? `
                        <button class="sb-best11-undo-btn" onclick="revertBest11Slot('${bestMod}', ${sIdx})" title="Ripristina consigliato AI">
                            ↺
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    };

    const modButtonsHtml = Object.keys(formations).map(m => `
        <button class="sb-mod-select-btn ${m === bestMod ? 'active' : ''}" onclick="openBest11Modal('${m}')">
            ${m}
        </button>
    `).join('');

    const benchHtml = benchPlayers.length > 0 ? benchPlayers.map(bp => `
        <div class="sb-best11-bench-item" title="${bp.name} (${bp.team || ''}) - A disposizione">
            <div style="display:flex;align-items:center;gap:6px;min-width:0;flex:1;">
                <span class="role-badge-mini ${bp.role}">${bp.role}</span>
                <div style="display:flex;flex-direction:column;min-width:0;">
                    <span style="color:#fff;font-size:11px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${bp.name}</span>
                    <span style="font-size:9px;color:var(--text-muted);">${bp.team || ''}</span>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:5px;">
                <span class="sb-best11-ovr-tag">⭐ ${bp.ovr}</span>
                <span style="font-size:9px;color:var(--text-muted);font-weight:600;">FM ${bp.fm ? Number(bp.fm).toFixed(2) : '-'}</span>
            </div>
        </div>
    `).join('') : `
        <div style="text-align:center;padding:16px 8px;color:var(--text-muted);font-size:11px;">
            Tutti i calciatori in rosa sono schierati nell'11 titolare.
        </div>
    `;

    content.innerHTML = `
        <!-- MODAL HEADER -->
        <div class="sb-modal-header" style="margin-bottom:0;padding-bottom:10px;">
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <h3 style="margin:0;font-size:17px;color:var(--accent-cyan);display:flex;align-items:center;gap:8px;">
                    <span>⚡ Miglior 11 Classic AI</span>
                    <span style="font-size:11px;font-weight:900;background:rgba(0,242,254,0.18);border:1px solid var(--accent-cyan);color:#fff;padding:2px 8px;border-radius:10px;">
                        Modulo: ${bestMod}
                    </span>
                </h3>
                <span style="font-size:11px;font-weight:800;background:rgba(251,191,36,0.15);border:1px solid rgba(251,191,36,0.35);color:#fbbf24;padding:2px 8px;border-radius:10px;">
                    OVR Titolari: ⭐ ${avgStarterOvr}
                </span>
                ${hasCustom ? `
                    <button class="sb-best11-reset-btn" onclick="resetBest11ModToAuto('${bestMod}')" title="Ripristina formazione consigliata AI">
                        ↺ Ripristina AI
                    </button>
                ` : ''}
            </div>
            <button class="sb-modal-close" onclick="closeSbModal()">✕</button>
        </div>

        <!-- 2-COLUMN EXECUTIVE WORKSPACE -->
        <div class="sb-best11-layout">
            <!-- LEFT SIDEBAR: MODULI + MODIFICATORE + PANCHINA -->
            <div class="sb-best11-sidebar">
                <!-- 1. SELETTORE MODULI -->
                <div class="sb-best11-card">
                    <div style="font-size:11px;font-weight:800;color:var(--accent-cyan);text-transform:uppercase;margin-bottom:8px;">
                        📐 Modulo Tattico
                    </div>
                    <div style="display:flex;gap:5px;flex-wrap:wrap;">
                        ${modButtonsHtml}
                    </div>
                </div>

                <!-- 2. MODIFICATORE DIFESA -->
                ${modifHtml}

                <!-- 3. PANCHINA DEI SOSTITUTI -->
                <div class="sb-best11-card sb-best11-bench-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.08);">
                        <span style="font-size:11.5px;font-weight:800;color:#fff;">🪑 Panchina & Riserve (${benchPlayers.length})</span>
                        <span style="font-size:10px;color:var(--accent-gold);font-weight:800;">OVR Medio: ⭐ ${avgBenchOvr}</span>
                    </div>
                    <div class="sb-best11-bench-list">
                        ${benchHtml}
                    </div>
                </div>
            </div>

            <!-- RIGHT COLUMN: CAMPO DA CALCIO FULL-HEIGHT -->
            <div class="sb-best11-pitch-area">
                <div class="sb-best11-pitch">
                    <div class="sb-best11-row">
                        ${starterFwdsObjs.map(renderPlayerPill).join('')}
                    </div>
                    <div class="sb-best11-row">
                        ${starterMidsObjs.map(renderPlayerPill).join('')}
                    </div>
                    <div class="sb-best11-row">
                        ${starterDefsObjs.map(renderPlayerPill).join('')}
                    </div>
                    <div class="sb-best11-row">
                        ${renderPlayerPill(starterGkObj)}
                    </div>
                </div>
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

// ==============================================================================
// MODALE SELEZIONE CALCIATORE PER MIGLIOR 11 AI (RISPETTO REGOLA DEL RUOLO)
// ==============================================================================

let best11PickerState = {
    modName: null,
    slotIdx: null,
    sourceTab: 'team', // 'team' o 'all'
    searchQuery: ''
};

function openBest11SlotPickerModal(modName, slotIdx) {
    best11PickerState.modName = modName;
    best11PickerState.slotIdx = slotIdx;
    best11PickerState.sourceTab = 'team';
    best11PickerState.searchQuery = '';

    let modal = document.getElementById('best11PickerModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'best11PickerModal';
        modal.className = 'modal-backdrop';
        modal.style.zIndex = '100000';
        modal.setAttribute('onclick', 'if(event.target === this) closeBest11PickerModal()');
        modal.innerHTML = `
            <div class="modal-card ai-replace-modal-card" style="max-width:680px;">
                <div id="best11PickerModalContent"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    renderBest11PickerModal();
    modal.style.display = 'flex';
    modal.classList.add('active');

    setTimeout(() => {
        const inp = document.getElementById('best11PickerSearchInput');
        if (inp) inp.focus();
    }, 50);
}

function closeBest11PickerModal() {
    const modal = document.getElementById('best11PickerModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function setBest11PickerSourceTab(tab) {
    best11PickerState.sourceTab = tab;
    renderBest11PickerCandidates();
}

function onBest11PickerSearch(val) {
    best11PickerState.searchQuery = val;
    renderBest11PickerCandidates();
}

function renderBest11PickerModal() {
    const content = document.getElementById('best11PickerModalContent');
    if (!content) return;

    const { modName, slotIdx } = best11PickerState;
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');

    let posTitle = 'Slot';
    let roleReqText = '';

    if (isMantra) {
        const schema = MANTRA_FORMATIONS[modName];
        if (schema && schema.slots && schema.slots[slotIdx]) {
            const sl = schema.slots[slotIdx];
            posTitle = `Posizione ${sl.pos}`;
            roleReqText = `Ruoli ammessi: <b>${sl.roles.join(', ')}</b> (o adattati consentiti da Regola 5.3)`;
        }
    } else {
        const formations = { '3-4-3': { d:3,c:4,a:3 }, '4-3-3': { d:4,c:3,a:3 }, '3-5-2': { d:3,c:5,a:2 }, '4-4-2': { d:4,c:4,a:2 }, '4-2-3-1': { d:4,c:5,a:1 } };
        const sch = formations[modName] || formations['3-4-3'];
        let role = 'P';
        if (slotIdx < sch.a) role = 'A';
        else if (slotIdx < sch.a + sch.c) role = 'C';
        else if (slotIdx < sch.a + sch.c + sch.d) role = 'D';
        posTitle = `Ruolo ${role}`;
        roleReqText = `Regola del Ruolo attiva: elenco limitato rigorosamente a calciatori di ruolo <b>${role}</b>.`;
    }

    content.innerHTML = `
        <div class="ai-replace-modal-inner">
            <div class="ai-replace-modal-header">
                <div>
                    <h3 class="ai-replace-title">🔄 Scegli Calciatore Titolare (${posTitle})</h3>
                    <div class="ai-replace-sub">Miglior 11 AI • Modulo <b>${modName}</b></div>
                </div>
                <button class="btn-action" style="padding:4px 10px;font-size:12px;" onclick="closeBest11PickerModal()">✕ Chiudi</button>
            </div>

            <div class="ai-replace-rule-alert" style="border-left-color:var(--accent-cyan);">
                <div style="font-size:12px;color:var(--accent-cyan);font-weight:800;">🛡️ Regola del Ruolo Rigorosa</div>
                <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">
                    ${roleReqText}
                </div>
            </div>

            <div class="ai-replace-toolbar">
                <div class="ai-replace-search-box">
                    <span style="font-size:14px;opacity:0.6;">🔍</span>
                    <input type="text" id="best11PickerSearchInput" class="ai-replace-input" placeholder="Cerca calciatore o squadra..." value="${best11PickerState.searchQuery}" oninput="onBest11PickerSearch(this.value)">
                </div>

                <div class="ai-replace-filters-row">
                    <div class="ai-replace-status-group">
                        <button id="best11TabTeam" class="ai-replace-status-btn ${best11PickerState.sourceTab === 'team' ? 'active' : ''}" onclick="setBest11PickerSourceTab('team'); document.getElementById('best11TabTeam').classList.add('active'); document.getElementById('best11TabAll').classList.remove('active');">
                            🔵 Calciatori in Rosa
                        </button>
                        <button id="best11TabAll" class="ai-replace-status-btn ${best11PickerState.sourceTab === 'all' ? 'active' : ''}" onclick="setBest11PickerSourceTab('all'); document.getElementById('best11TabAll').classList.add('active'); document.getElementById('best11TabTeam').classList.remove('active');">
                            🌐 Tutto il Database Serie A
                        </button>
                    </div>
                </div>
            </div>

            <div id="best11PickerCandidatesList" class="ai-replace-candidates-container">
                <!-- Popolato da renderBest11PickerCandidates -->
            </div>
        </div>
    `;

    renderBest11PickerCandidates();
}

function renderBest11PickerCandidates() {
    const container = document.getElementById('best11PickerCandidatesList');
    if (!container) return;

    const { modName, slotIdx, sourceTab, searchQuery } = best11PickerState;
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const allBought = [...State.slots.P.players, ...State.slots.D.players, ...State.slots.C.players, ...State.slots.A.players];

    let pool = (sourceTab === 'team') ? allBought : PLAYERS;
    let candidates = [];

    if (isMantra) {
        const schema = MANTRA_FORMATIONS[modName];
        const slot = schema.slots[slotIdx];
        candidates = pool.map(p => {
            const compat = checkMantraSlotCompatibility(p, slot);
            return {
                player: p,
                allowed: compat.allowed,
                isAdapted: compat.isAdapted,
                malus: compat.malus || 0
            };
        }).filter(item => item.allowed);
    } else {
        const formations = { '3-4-3': { d:3,c:4,a:3 }, '4-3-3': { d:4,c:3,a:3 }, '3-5-2': { d:3,c:5,a:2 }, '4-4-2': { d:4,c:4,a:2 }, '4-2-3-1': { d:4,c:5,a:1 } };
        const sch = formations[modName] || formations['3-4-3'];
        let role = 'P';
        if (slotIdx < sch.a) role = 'A';
        else if (slotIdx < sch.a + sch.c) role = 'C';
        else if (slotIdx < sch.a + sch.c + sch.d) role = 'D';

        candidates = pool.filter(p => p.role === role).map(p => ({
            player: p,
            allowed: true,
            isAdapted: false,
            malus: 0
        }));
    }

    const q = (searchQuery || '').toLowerCase().trim();
    if (q) {
        candidates = candidates.filter(item => {
            const p = item.player;
            return p.name.toLowerCase().includes(q) || (p.team && p.team.toLowerCase().includes(q)) || (p.mantra && p.mantra.toLowerCase().includes(q));
        });
    }

    candidates.sort((a, b) => (b.player.ovr || 0) - (a.player.ovr || 0));

    if (candidates.length === 0) {
        container.innerHTML = `
            <div style="padding:40px 20px;text-align:center;color:var(--text-muted);">
                <div style="font-size:26px;margin-bottom:6px;">⚠️</div>
                <div style="font-weight:700;color:#fff;font-size:13.5px;">Nessun calciatore compatibile</div>
                <div style="font-size:11.5px;margin-top:3px;">
                    ${sourceTab === 'team' ? 'Nessun giocatore acquistato nella tua rosa può ricoprire questo ruolo. Prova a passare alla scheda "Tutto il Database Serie A".' : 'Nessun calciatore trovato per i filtri selezionati.'}
                </div>
            </div>
        `;
        return;
    }

    const displayList = candidates.slice(0, 60);

    const itemsHtml = displayList.map(item => {
        const p = item.player;
        const roleBadgeHtml = isMantra
            ? renderMantraRoleBadges(p.mantra)
            : `<span class="role-badge ${p.role}">${p.role}</span>`;

        const adaptedTag = item.isAdapted 
            ? `<span style="font-size:9px;color:#f59e0b;background:rgba(245,158,11,0.15);padding:1px 4px;border-radius:3px;">⚠️ Fuori Pos. (-1 pt)</span>`
            : `<span style="font-size:9px;color:#4ade80;background:rgba(34,197,94,0.12);padding:1px 4px;border-radius:3px;">✓ Naturale</span>`;

        const isBought = allBought.some(b => b.id === p.id);

        return `
            <div class="ai-replace-item">
                <div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0;">
                    <div style="width:36px;text-align:center;flex-shrink:0;">
                        ${roleBadgeHtml}
                    </div>
                    <div style="display:flex;flex-direction:column;gap:2px;min-width:0;flex:1;">
                        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                            <span class="ai-cand-name" onclick="openPlayerProfileModal(${p.id})">${p.name}</span>
                            <span class="ai-cand-team">${p.team}</span>
                            ${adaptedTag}
                            ${isBought ? `<span style="font-size:9px;color:#4ade80;background:rgba(34,197,94,0.15);padding:1px 4px;border-radius:3px;">In Rosa</span>` : ''}
                        </div>
                        <div style="display:flex;align-items:center;gap:8px;font-size:11px;color:var(--text-muted);">
                            <span class="ovr-pill ${p.ovr >= 85 ? 'top-tier' : ''}" style="font-size:10px;padding:1px 5px;">${p.ovr} OVR</span>
                            <span>FM: <b style="color:#fff;">${p.fm ? Number(p.fm).toFixed(2) : '-'}</b></span>
                            <span>Tit: <b style="color:#fff;">${p.titolarita || 50}%</b></span>
                        </div>
                    </div>
                </div>

                <div style="flex-shrink:0;">
                    <button class="ai-cand-btn select" onclick="setBest11CustomSlot('${modName}', ${slotIdx}, ${p.id})">
                        ✅ Schiera
                    </button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div style="padding:6px 12px;font-size:11px;color:var(--text-muted);border-bottom:1px solid rgba(255,255,255,0.06);">
            ${candidates.length} calciatori compatibili (Regola del Ruolo rispettata)
        </div>
        <div class="ai-replace-items-list">${itemsHtml}</div>
    `;
}

window.openBest11SlotPickerModal = openBest11SlotPickerModal;
window.closeBest11PickerModal = closeBest11PickerModal;
window.setBest11CustomSlot = setBest11CustomSlot;
window.revertBest11Slot = revertBest11Slot;
window.resetBest11ModToAuto = resetBest11ModToAuto;
window.setBest11PickerSourceTab = setBest11PickerSourceTab;
window.onBest11PickerSearch = onBest11PickerSearch;


// ==============================================================================
// 4. ESPORTAZIONE ROSA WHATSAPP & CSV
// ==============================================================================
function exportRosterToWhatsApp() {
    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const remaining = State.budgetTotal - State.budgetSpent;
    const gks = State.slots.P.players || [];
    const defs = State.slots.D.players || [];
    const mids = State.slots.C.players || [];
    const fwds = State.slots.A.players || [];
    const allBought = [...gks, ...defs, ...mids, ...fwds];

    if (allBought.length === 0) {
        alert("La tua rosa è vuota! Acquista prima qualche calciatore.");
        return;
    }

    let text = `🏆 *LA MIA ROSA FANTA 2026/2027 (${isMantraMode ? 'MANTRA' : 'CLASSIC'})*\n`;
    text += `💰 Spesi: ${State.budgetSpent} CR | Residui: ${remaining} CR (su ${State.budgetTotal})\n\n`;

    if (isMantraMode) {
        text += `🧤 *PORTIERI (${gks.length}/3)*\n`;
        gks.forEach(p => { text += `• ${p.name} (${p.team}) - ${p.paidPrice} CR\n`; });
        if (gks.length === 0) text += `• Nessun portiere acquistato\n`;

        const movList = [...defs, ...mids, ...fwds];
        movList.sort((a, b) => {
            const scoreA = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(a.mantra) : 50;
            const scoreB = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(b.mantra) : 50;
            if (scoreA !== scoreB) return scoreA - scoreB;
            if ((b.paidPrice || 0) !== (a.paidPrice || 0)) return (b.paidPrice || 0) - (a.paidPrice || 0);
            return (b.ovr || 0) - (a.ovr || 0);
        });

        text += `\n🏃‍♂️ *GIOCATORI DI MOVIMENTO (${movList.length}/28)*\n`;
        movList.forEach(p => { text += `• [${p.mantra || p.role}] ${p.name} (${p.team}) - ${p.paidPrice} CR\n`; });
        if (movList.length === 0) text += `• Nessun giocatore di movimento acquistato\n`;
    } else {
        text += `🧤 *PORTIERI (${gks.length}/3)*\n`;
        gks.forEach(p => { text += `• ${p.name} (${p.team}) - ${p.paidPrice} CR\n`; });
        if (gks.length === 0) text += `• Nessun portiere acquistato\n`;

        text += `\n🛡️ *DIFENSORI (${defs.length}/8)*\n`;
        defs.forEach(p => { text += `• ${p.name} (${p.team}) - ${p.paidPrice} CR\n`; });
        if (defs.length === 0) text += `• Nessun difensore acquistato\n`;

        text += `\n🪄 *CENTROCAMPISTI (${mids.length}/8)*\n`;
        mids.forEach(p => { text += `• ${p.name} (${p.team}) - ${p.paidPrice} CR\n`; });
        if (mids.length === 0) text += `• Nessun centrocampista acquistato\n`;

        text += `\n⚡ *ATTACCANTI (${fwds.length}/6)*\n`;
        fwds.forEach(p => { text += `• ${p.name} (${p.team}) - ${p.paidPrice} CR\n`; });
        if (fwds.length === 0) text += `• Nessun attaccante acquistato\n`;
    }

    text += `\n_Generato con Fanta Master AI 2026/27_`;

    navigator.clipboard.writeText(text).then(() => {
        alert("✓ Rosa copiata negli appunti con successo!\n\nPuoi incollarla direttamente nella chat WhatsApp della tua Lega.");
    }).catch(() => {
        prompt("Copia manualmente il testo della tua rosa:", text);
    });
}

function downloadRosterCSV() {
    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const all = [...State.slots.P.players, ...State.slots.D.players, ...State.slots.C.players, ...State.slots.A.players];
    if (all.length === 0) {
        alert("La rosa è vuota!");
        return;
    }

    let csv = "Ruolo,Ruolo_Mantra,Nome,Squadra,OVR,Prezzo Pagato (CR),Fragilita,Slot\n";
    all.forEach(p => {
        csv += `${p.role},"${p.mantra || ''}","${p.name}","${p.team}",${p.ovr},${p.paidPrice},"${p.fragilita_val || ''}","${p.slot_fascia || ''}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `Rosa_Fanta_2026_27_${isMantraMode ? 'Mantra' : 'Classic'}.csv`;
    link.click();
}

// ==============================================================================
// 5. IMPORTAZIONE ROSA CSV & TESTO (LA MIA ROSA & RIVALI)
// ==============================================================================
let csvImportState = {
    targetTeam: 'my_team',
    mode: 'replace', // 'replace' | 'append'
    parsedRows: [],
    showPasteArea: false,
    fileName: ''
};

function cleanCsvStr(s) {
    if (!s) return '';
    return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, ' ').replace(/\s+/g, ' ').trim();
}

function matchPlayerAgainstMaster(rawName, rawTeam, rawRole, playerPool) {
    if (!playerPool || !playerPool.length) return null;
    const cQ = cleanCsvStr(rawName);
    const cTeam = cleanCsvStr(rawTeam);
    const qParts = cQ.split(' ').filter(Boolean);
    if (!qParts.length) return null;

    let pool = playerPool;
    let normRole = '';
    if (rawRole) {
        const rUpper = String(rawRole).trim().toUpperCase();
        if (['P', 'POR'].includes(rUpper)) normRole = 'P';
        else if (['D', 'DD', 'DS', 'DC', 'E'].includes(rUpper)) normRole = 'D';
        else if (['C', 'M', 'T', 'W'].includes(rUpper)) normRole = 'C';
        else if (['A', 'PC'].includes(rUpper)) normRole = 'A';
    }

    if (normRole) {
        const byRole = pool.filter(p => p.role === normRole);
        if (byRole.length > 0) pool = byRole;
    }

    // 1. Match esatto nome + squadra
    let match = pool.find(p => cleanCsvStr(p.name) === cQ && (!cTeam || cleanCsvStr(p.team) === cTeam));
    if (match) return match;

    // 2. Match esatto nome (anche squadra diversa se trasferito o mancante)
    match = pool.find(p => cleanCsvStr(p.name) === cQ);
    if (match) return match;

    // 3. Match fallback su tutto il database se il ruolo indicato non coincideva
    if (normRole) {
        match = playerPool.find(p => cleanCsvStr(p.name) === cQ && (!cTeam || cleanCsvStr(p.team) === cTeam));
        if (match) return match;
        match = playerPool.find(p => cleanCsvStr(p.name) === cQ);
        if (match) return match;
    }

    // 4. Match intelligente per cognome / parti del nome
    const candidates = [];
    for (const p of pool) {
        const cp = cleanCsvStr(p.name);
        const cpParts = cp.split(' ').filter(Boolean);
        const pSurname = cpParts[0];
        if (qParts.includes(pSurname) || cpParts.includes(qParts[0])) {
            candidates.push(p);
        }
    }

    if (candidates.length === 1) return candidates[0];
    if (candidates.length > 1) {
        if (cTeam) {
            const byTeam = candidates.find(p => cleanCsvStr(p.team) === cTeam);
            if (byTeam) return byTeam;
        }
        if (qParts.length > 1) {
            const init = qParts[1][0];
            const byInit = candidates.find(p => cleanCsvStr(p.name).includes(init));
            if (byInit) return byInit;
        }
        return candidates[0];
    }

    return null;
}

function parseCsvRawLines(text) {
    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
    if (!lines.length) return [];

    const firstLine = lines[0];
    let delim = ',';
    const semicolons = (firstLine.match(/;/g) || []).length;
    const commas = (firstLine.match(/,/g) || []).length;
    const tabs = (firstLine.match(/\t/g) || []).length;
    if (semicolons > commas && semicolons > tabs) delim = ';';
    else if (tabs > commas && tabs > semicolons) delim = '\t';

    function splitRow(row) {
        const parts = [];
        let cur = '';
        let inQuotes = false;
        for (let i = 0; i < row.length; i++) {
            const char = row[i];
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === delim && !inQuotes) {
                parts.push(cur.trim().replace(/^"|"$/g, '').trim());
                cur = '';
            } else {
                cur += char;
            }
        }
        parts.push(cur.trim().replace(/^"|"$/g, '').trim());
        return parts;
    }

    const rawRows = lines.map(splitRow).filter(r => r.length >= 2);
    if (!rawRows.length) return [];

    const h = rawRows[0].map(c => cleanCsvStr(c));
    let nameIdx = -1, roleIdx = -1, teamIdx = -1, priceIdx = -1;

    for (let i = 0; i < h.length; i++) {
        const col = h[i];
        if (['nome', 'calciatore', 'player', 'giocatore', 'atleta'].includes(col)) nameIdx = i;
        else if (['ruolo', 'r', 'role', 'pos', 'ruolo classic', 'ruolo mantra'].includes(col) && roleIdx === -1) roleIdx = i;
        else if (['squadra', 'team', 'club'].includes(col)) teamIdx = i;
        else if (['prezzo', 'prezzo pagato', 'prezzo pagato cr', 'costo', 'spesa', 'pagato', 'cr', 'prezzo acquisto', 'qta', 'quotazione', 'fvm'].includes(col)) priceIdx = i;
    }

    let dataRows = rawRows;
    const hasHeader = (nameIdx !== -1 || roleIdx !== -1 || priceIdx !== -1);
    if (hasHeader) {
        dataRows = rawRows.slice(1);
    } else {
        nameIdx = 1;
        roleIdx = 0;
        teamIdx = 2;
        priceIdx = 3;
    }

    return dataRows.map((row, idx) => {
        const rawRole = roleIdx >= 0 && roleIdx < row.length ? row[roleIdx] : '';
        const rawName = nameIdx >= 0 && nameIdx < row.length ? row[nameIdx] : (row[1] || row[0]);
        const rawTeam = teamIdx >= 0 && teamIdx < row.length ? row[teamIdx] : '';
        let price = 1;
        if (priceIdx >= 0 && priceIdx < row.length) {
            const parsed = parseInt(String(row[priceIdx]).replace(/[^0-9]/g, ''), 10);
            if (!isNaN(parsed) && parsed >= 0) price = parsed;
        }

        const matched = (typeof PLAYERS !== 'undefined') ? matchPlayerAgainstMaster(rawName, rawTeam, rawRole, PLAYERS) : null;
        return {
            rowId: idx,
            rawRole,
            rawName,
            rawTeam,
            price,
            matchedPlayer: matched,
            isExcluded: false
        };
    });
}

function openCsvRosterImportModal(targetTeam = 'my_team') {
    if (typeof showComingSoonModal === 'function') {
        showComingSoonModal('Importazione Rose da CSV');
        return;
    }
    csvImportState.targetTeam = targetTeam;
    const modal = document.getElementById('csvRosterImportModal');
    if (!modal) return;
    modal.style.display = 'flex';
    modal.classList.add('active');
    renderCsvImportModalContent();
}

function closeCsvRosterImportModal() {
    const modal = document.getElementById('csvRosterImportModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
}

function onCsvImportTargetChange(val) {
    csvImportState.targetTeam = val;
    renderCsvImportModalContent();
}

function onCsvImportModeChange(val) {
    csvImportState.mode = val;
    renderCsvImportModalContent();
}

function toggleCsvPasteArea() {
    csvImportState.showPasteArea = !csvImportState.showPasteArea;
    renderCsvImportModalContent();
}

function handleCsvFileSelected(event) {
    const file = event.target?.files?.[0];
    if (file) {
        readCsvFile(file);
    }
}

function handleCsvDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    const zone = document.getElementById('csvDropZone');
    if (zone) zone.classList.add('dragover');
}

function handleCsvDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    const zone = document.getElementById('csvDropZone');
    if (zone) zone.classList.remove('dragover');
    if (event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files.length > 0) {
        const file = event.dataTransfer.files[0];
        readCsvFile(file);
    }
}

function readCsvFile(file) {
    csvImportState.fileName = file.name;
    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        if (text) {
            parseAndProcessCsv(text);
        }
    };
    reader.readAsText(file);
}

function parsePastedCsvText() {
    const textarea = document.getElementById('csvTextarea');
    if (!textarea || !textarea.value.trim()) {
        alert("Incolla prima il testo del file CSV!");
        return;
    }
    csvImportState.fileName = 'Testo incollato';
    parseAndProcessCsv(textarea.value.trim());
}

function parseAndProcessCsv(text) {
    try {
        const rows = parseCsvRawLines(text);
        if (!rows.length) {
            alert("Nessun dato valido trovato nel CSV fornito. Assicurati che contenga almeno i nomi dei calciatori.");
            return;
        }
        csvImportState.parsedRows = rows;
        renderCsvImportModalContent();
    } catch (e) {
        console.error("Errore durante il parsing CSV:", e);
        alert("Si è verificato un errore durante l'analisi del CSV: " + e.message);
    }
}

function updateCsvRowPrice(rowId, newPrice) {
    const r = csvImportState.parsedRows.find(x => x.rowId === rowId);
    if (r) {
        const val = parseInt(newPrice, 10);
        r.price = (!isNaN(val) && val >= 1) ? val : 1;
        renderCsvImportModalContent();
    }
}

function removeCsvRow(rowId) {
    const idx = csvImportState.parsedRows.findIndex(x => x.rowId === rowId);
    if (idx !== -1) {
        csvImportState.parsedRows.splice(idx, 1);
        renderCsvImportModalContent();
    }
}

function renderCsvImportModalContent() {
    const container = document.getElementById('csvRosterImportModalContent');
    if (!container) return;

    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const rivalsList = (typeof State !== 'undefined' && State.rivals) ? Object.keys(State.rivals) : ['FC Sparta', 'Real Fanta', 'AC Picchia', 'Dinamo', 'Atletico', 'Virtus', 'Sporting'];
    const target = csvImportState.targetTeam || 'my_team';
    const isMyTeam = (target === 'my_team' || target === 'Unika' || target === (typeof State !== 'undefined' ? State.teamName : 'La Mia Rosa'));
    const mode = csvImportState.mode || 'replace';
    const rows = csvImportState.parsedRows || [];

    // Calcolo statistiche anteprima
    const validRows = rows.filter(r => r.matchedPlayer && !r.isExcluded);
    const unmatchedRows = rows.filter(r => !r.matchedPlayer);
    
    let porCount = 0, defCount = 0, midCount = 0, attCount = 0, totalSpent = 0;
    validRows.forEach(r => {
        const p = r.matchedPlayer;
        totalSpent += r.price;
        if (p.role === 'P') porCount++;
        else if (p.role === 'D') defCount++;
        else if (p.role === 'C') midCount++;
        else if (p.role === 'A') attCount++;
    });

    const targetBudget = isMyTeam ? (State.budgetTotal || 1000) : (State.rivals?.[target]?.budget || 1000);
    const remBudget = targetBudget - totalSpent;

    let rivalsOptionsHtml = rivalsList.map(rName => {
        return `<option value="${rName}" ${target === rName ? 'selected' : ''}>👥 ${rName} (Rivale)</option>`;
    }).join('');

    let previewHtml = '';
    if (rows.length > 0) {
        const rowsTrHtml = rows.map(r => {
            const isFound = !!r.matchedPlayer;
            const p = r.matchedPlayer;
            const role = isFound ? p.role : (r.rawRole || '?');
            const name = isFound ? p.name : r.rawName;
            const team = isFound ? p.team : (r.rawTeam || '-');
            const mantra = isFound && p.mantra ? ` <span style="font-size:10px;color:var(--accent-cyan);font-weight:700;">[${p.mantra}]</span>` : '';
            const statusBadge = isFound 
                ? `<span class="csv-stat-badge success" style="padding:2px 7px;font-size:10.5px;">✓ Riconosciuto</span>`
                : `<span class="csv-stat-badge warning" style="padding:2px 7px;font-size:10.5px;" title="Non presente nel listone ufficiale 2026/27">⚠️ Non trovato</span>`;

            return `
                <tr style="${!isFound ? 'opacity:0.6;background:rgba(239,68,68,0.04);' : ''}">
                    <td style="text-align:center;width:40px;">
                        <span class="role-badge ${role}" style="font-size:10.5px;padding:2px 6px;">${role}</span>
                    </td>
                    <td>
                        <div style="font-weight:700;color:${isFound ? '#fff' : '#fca5a5'};">${name}${mantra}</div>
                        <div style="font-size:11px;color:var(--text-muted);">${team} ${!isFound && r.rawName !== name ? `(dal CSV: "${r.rawName}")` : ''}</div>
                    </td>
                    <td style="text-align:center;width:95px;">
                        <input type="number" min="1" max="1000" class="csv-price-input" value="${r.price}" onchange="updateCsvRowPrice(${r.rowId}, this.value)">
                        <span style="font-size:10px;color:var(--text-muted);">CR</span>
                    </td>
                    <td style="text-align:center;width:120px;">
                        ${statusBadge}
                    </td>
                    <td style="text-align:center;width:40px;">
                        <button class="btn-action" style="padding:2px 6px;font-size:11px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" onclick="removeCsvRow(${r.rowId})" title="Rimuovi questo calciatore">✕</button>
                    </td>
                </tr>
            `;
        }).join('');

        previewHtml = `
            <div style="margin-top:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                        <span class="csv-stat-badge ${unmatchedRows.length === 0 ? 'success' : 'warning'}">
                            ${validRows.length} / ${rows.length} Calciatori Riconosciuti
                        </span>
                        ${isMantraMode ? `
                            <span class="csv-stat-badge">🧤 Por: ${porCount}</span>
                            <span class="csv-stat-badge">🏃 Mov: ${defCount + midCount + attCount}</span>
                        ` : `
                            <span class="csv-stat-badge">🧤 P: ${porCount}/3</span>
                            <span class="csv-stat-badge">🛡️ D: ${defCount}/8</span>
                            <span class="csv-stat-badge">🪄 C: ${midCount}/8</span>
                            <span class="csv-stat-badge">⚡ A: ${attCount}/6</span>
                        `}
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span class="csv-stat-badge" style="background:rgba(0,242,254,0.1);border-color:rgba(0,242,254,0.3);color:var(--accent-cyan);">
                            💰 Spesa: ${totalSpent} CR | Residui: ${remBudget} CR
                        </span>
                    </div>
                </div>

                ${unmatchedRows.length > 0 ? `
                    <div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:8px;padding:8px 12px;margin-bottom:10px;font-size:11.5px;color:#fbbf24;">
                        ⚠️ <b>Attenzione:</b> ${unmatchedRows.length} calciatori non sono stati trovati nel database Serie A 2026/27 (potrebbero essere trasferiti all'estero o avere un nome diverso). Solo i calciatori con spunta verde verranno inseriti nella rosa.
                    </div>
                ` : ''}

                <div class="csv-preview-table-wrap">
                    <table class="csv-preview-table">
                        <thead>
                            <tr>
                                <th style="text-align:center;width:40px;">R</th>
                                <th>Calciatore & Squadra</th>
                                <th style="text-align:center;width:95px;">Prezzo</th>
                                <th style="text-align:center;width:120px;">Stato</th>
                                <th style="text-align:center;width:40px;">✕</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsTrHtml}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        <!-- HEADER -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:26px;">📂</span>
                <div>
                    <h3 class="font-title" style="color:var(--accent-cyan);font-size:19px;margin:0;">Carica Rosa da File CSV o Testo</h3>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">Importa automaticamente la tua rosa o quella dei tuoi avversari da Leghe Fantacalcio o Excel</div>
                </div>
            </div>
            <button class="btn-action" style="padding:4px 10px;font-size:12px;" onclick="closeCsvRosterImportModal()">Chiudi ✕</button>
        </div>

        <!-- SETTINGS: TARGET TEAM & MODE -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);padding:12px;border-radius:10px;margin-bottom:14px;">
            <div>
                <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px;">Squadra di Destinazione</label>
                <select id="csvImportTargetSelect" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:6px 10px;font-size:12.5px;" onchange="onCsvImportTargetChange(this.value)">
                    <option value="my_team" ${isMyTeam ? 'selected' : ''}>🌟 ${escapeQuotes(typeof State !== 'undefined' && State.teamName ? State.teamName : 'La Mia Rosa')}</option>
                    ${rivalsOptionsHtml}
                </select>
            </div>
            <div>
                <label style="display:block;font-size:11.5px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.5px;">Modalità di Caricamento</label>
                <div style="display:flex;gap:12px;align-items:center;height:34px;">
                    <label style="display:inline-flex;align-items:center;gap:5px;font-size:12px;cursor:pointer;">
                        <input type="radio" name="csvImportMode" value="replace" ${mode === 'replace' ? 'checked' : ''} onchange="onCsvImportModeChange(this.value)">
                        <span>🔄 Sostituisci intera rosa</span>
                    </label>
                    <label style="display:inline-flex;align-items:center;gap:5px;font-size:12px;cursor:pointer;">
                        <input type="radio" name="csvImportMode" value="append" ${mode === 'append' ? 'checked' : ''} onchange="onCsvImportModeChange(this.value)">
                        <span>➕ Aggiungi</span>
                    </label>
                </div>
            </div>
        </div>

        <!-- UPLOAD DROP ZONE -->
        <div class="csv-drop-zone" id="csvDropZone" ondragover="handleCsvDragOver(event)" ondrop="handleCsvDrop(event)" onclick="document.getElementById('csvFileInput').click()">
            <div style="font-size:26px;margin-bottom:4px;">📄</div>
            <div style="font-size:13.5px;font-weight:700;color:var(--accent-cyan);">
                ${csvImportState.fileName ? `File caricato: ${csvImportState.fileName}` : 'Trascina qui il file .CSV o .TXT oppure clicca per selezionarlo'}
            </div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">
                Supporta separatori virgola (,), punto e virgola (;), esportazioni Leghe Fantacalcio o formati personalizzati
            </div>
            <input type="file" id="csvFileInput" accept=".csv, .txt, text/csv, text/plain" style="display:none;" onchange="handleCsvFileSelected(event)">
        </div>

        <!-- TOGGLE TEXTAREA FOR PASTE -->
        <div style="display:flex;justify-content:flex-end;margin-top:8px;">
            <button class="btn-action" style="font-size:11.5px;padding:3px 10px;background:rgba(255,255,255,0.04);" onclick="toggleCsvPasteArea()">
                ${csvImportState.showPasteArea ? 'Nascondi area incolla ▴' : '📝 Oppure incolla il testo CSV ▾'}
            </button>
        </div>

        ${csvImportState.showPasteArea ? `
            <div style="margin-top:8px;">
                <textarea id="csvTextarea" class="csv-textarea" rows="5" placeholder="Esempio:&#10;Ruolo,Calciatore,Squadra,Prezzo&#10;P,Svilar,Roma,25&#10;D,Dimarco,Inter,28&#10;C,Calhanoglu,Inter,50&#10;A,Martinez L.,Inter,230"></textarea>
                <div style="display:flex;justify-content:flex-end;margin-top:6px;">
                    <button class="btn-action" style="background:var(--accent-cyan);color:#000;font-weight:800;font-size:12px;padding:6px 14px;border:none;" onclick="parsePastedCsvText()">
                        🔍 Analizza Testo Incollato
                    </button>
                </div>
            </div>
        ` : ''}

        <!-- PREVIEW TABLE -->
        ${previewHtml}

        <!-- FOOTER ACTIONS -->
        <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:18px;border-top:1px solid rgba(255,255,255,0.08);padding-top:12px;">
            <button class="btn-action" style="padding:8px 16px;font-size:12px;" onclick="closeCsvRosterImportModal()">Annulla</button>
            <button class="btn-action" style="background:linear-gradient(135deg, #10b981, #059669);color:#fff;font-weight:900;padding:8px 22px;font-size:13px;border:none;box-shadow:0 4px 15px rgba(16,185,129,0.3);${validRows.length === 0 ? 'opacity:0.4;cursor:not-allowed;' : ''}" ${validRows.length === 0 ? 'disabled' : ''} onclick="confirmApplyCsvRoster()">
                ✓ Conferma e Carica Rosa (${validRows.length} Calciatori)
            </button>
        </div>
    `;
}

function confirmApplyCsvRoster() {
    const target = csvImportState.targetTeam || 'my_team';
    const isMyTeam = (target === 'my_team' || target === 'Unika' || target === (typeof State !== 'undefined' ? State.teamName : 'La Mia Rosa'));
    const mode = csvImportState.mode || 'replace';
    const rows = csvImportState.parsedRows || [];
    const validRows = rows.filter(r => r.matchedPlayer && !r.isExcluded);

    if (validRows.length === 0) {
        alert("Nessun calciatore valido da importare!");
        return;
    }

    if (mode === 'replace') {
        const teamDesc = isMyTeam ? (State.teamName || 'la tua Rosa') : `la rosa di ${target}`;
        if (!confirm(`Stai per sovrascrivere completamente ${teamDesc} con i ${validRows.length} calciatori caricati dal CSV.\n\nVuoi procedere?`)) {
            return;
        }
    }

    if (isMyTeam) {
        if (mode === 'replace') {
            State.slots.P.players = [];
            State.slots.D.players = [];
            State.slots.C.players = [];
            State.slots.A.players = [];
            State.budgetSpent = 0;
        }

        validRows.forEach(r => {
            const p = r.matchedPlayer;
            const price = Math.max(1, parseInt(r.price, 10) || 1);

            // Rimuovi da rivali se precedentemente assegnato
            if (State.takenByOthers && State.takenByOthers.includes(p.id)) {
                if (typeof unmarkPlayerTaken === 'function') {
                    unmarkPlayerTaken(p.id);
                }
            }

            const isGK = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR')));
            const slotKey = isGK ? 'P' : (State.slots[p.role] ? p.role : 'C');

            // Evita duplicati se in modalità append
            if (!State.slots[slotKey].players.some(x => x.id === p.id)) {
                State.slots[slotKey].players.push({ ...p, paidPrice: price });
                State.budgetSpent += price;
            }
        });
    } else {
        // Assegnazione a squadra rivale
        if (State.rivals && State.rivals[target]) {
            if (mode === 'replace') {
                const oldPlayers = [...(State.rivals[target].players || [])];
                oldPlayers.forEach(op => {
                    if (typeof unmarkPlayerTaken === 'function') {
                        unmarkPlayerTaken(op.id);
                    }
                });
                State.rivals[target].players = [];
                State.rivals[target].spent = 0;
            }

            validRows.forEach(r => {
                const p = r.matchedPlayer;
                const price = Math.max(1, parseInt(r.price, 10) || 1);
                if (typeof markPlayerTaken === 'function') {
                    markPlayerTaken(p.id, target, price);
                }
            });
        }
    }

    if (typeof saveStateToStorage === 'function') saveStateToStorage();
    if (typeof updateAllViews === 'function') updateAllViews();

    // Aggiorna rosterModal se è aperto in background
    const rModal = document.getElementById('rosterModal');
    if (rModal && rModal.classList.contains('active') && typeof openRosterModal === 'function') {
        openRosterModal(target);
    }

    closeCsvRosterImportModal();

    const successMsg = `✓ Rosa caricata con successo (${validRows.length} calciatori in ${teamDesc})!`;
    if (typeof showSyncToast === 'function') {
        showSyncToast(successMsg);
    } else {
        alert(successMsg);
    }
}

window.openCsvRosterImportModal = openCsvRosterImportModal;
window.closeCsvRosterImportModal = closeCsvRosterImportModal;
window.onCsvImportTargetChange = onCsvImportTargetChange;
window.onCsvImportModeChange = onCsvImportModeChange;
window.handleCsvFileSelected = handleCsvFileSelected;
window.handleCsvDrop = handleCsvDrop;
window.handleCsvDragOver = handleCsvDragOver;
window.toggleCsvPasteArea = toggleCsvPasteArea;
window.parsePastedCsvText = parsePastedCsvText;
window.updateCsvRowPrice = updateCsvRowPrice;
window.removeCsvRow = removeCsvRow;
window.confirmApplyCsvRoster = confirmApplyCsvRoster;

