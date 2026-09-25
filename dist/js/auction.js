// ==============================================================================
// MODULO TABELLONE ASTA LIVE & GESTIONE BUDGET (CON STATISTICHE 2025/2026 REALI)
// ==============================================================================

function isAuctionMantraMode() {
    if (typeof State !== 'undefined') {
        if (State.auctionTableMode) return State.auctionTableMode === 'mantra';
        return State.systemMode === 'mantra';
    }
    return false;
}

function setAuctionTableMode(mode) {
    if (typeof State === 'undefined') return;
    State.auctionTableMode = (mode === 'mantra') ? 'mantra' : 'classic';

    const btnClassic = document.getElementById('btnAuctionModeClassic');
    const btnMantra = document.getElementById('btnAuctionModeMantra');
    if (btnClassic) btnClassic.classList.toggle('active', State.auctionTableMode === 'classic');
    if (btnMantra) btnMantra.classList.toggle('active', State.auctionTableMode === 'mantra');

    // Toggle Classic Role Chips vs Mantra Subroles Bar
    const classicChips = document.getElementById('classicRoleChipsGroup') || document.querySelector('.role-chip-group');
    const mantraBar = document.getElementById('mantraQuickSubrolesBar');
    if (classicChips) {
        classicChips.style.display = (State.auctionTableMode === 'classic') ? 'flex' : 'none';
    }
    if (mantraBar) {
        mantraBar.style.display = (State.auctionTableMode === 'mantra') ? 'flex' : 'none';
    }

    // Reset role filter when switching mode
    State.filterRole = 'ALL';
    const selRole = document.getElementById('filterRole');
    if (selRole) selRole.value = 'ALL';

    document.querySelectorAll('.role-chip').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-role') === 'ALL');
    });

    updateRoleFilterOptionsUI();
    renderTable();
}

function isPlayerBought(playerId) {
    for (let r in State.slots) {
        if (State.slots[r].players.some(p => p.id === playerId)) return true;
    }
    return false;
}

function updateBudgetUI() {
    const remaining = State.budgetTotal - State.budgetSpent;
    const elRem = document.getElementById('lblRemainingBudget');
    const elSpn = document.getElementById('lblSpentBudget');
    if (elRem) elRem.textContent = `${remaining} CR`;
    if (elSpn) elSpn.textContent = `${State.budgetSpent} CR`;

    const elP = document.getElementById('lblSlotP');
    const elD = document.getElementById('lblSlotD');
    const elC = document.getElementById('lblSlotC');
    const elA = document.getElementById('lblSlotA');
    if (elP) elP.textContent = `${State.slots.P.players.length}/3`;
    if (elD) elD.textContent = `${State.slots.D.players.length}/8`;
    if (elC) elC.textContent = `${State.slots.C.players.length}/8`;
    if (elA) elA.textContent = `${State.slots.A.players.length}/6`;

    // Aggiorna tracker Mantra (3 Por + 28 Movimento = 31 Totale)
    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const allBought = [...State.slots.P.players, ...State.slots.D.players, ...State.slots.C.players, ...State.slots.A.players];
    const porBought = State.slots.P.players.length;
    const movBought = State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length;

    const elMantraPor = document.getElementById('lblMantraSlotPor');
    const elMantraMov = document.getElementById('lblMantraSlotMov');
    const elMantraTot = document.getElementById('lblMantraSlotTot');
    if (elMantraPor) elMantraPor.textContent = `${porBought}`;
    if (elMantraMov) elMantraMov.textContent = `${movBought}`;
    if (elMantraTot) elMantraTot.textContent = `${allBought.length}/31`;

    // Fallback retrocompatibilità per vecchi id tracker se presenti
    const elMantraDef = document.getElementById('lblMantraSlotDef');
    const elMantraMed = document.getElementById('lblMantraSlotMed');
    const elMantraAtt = document.getElementById('lblMantraSlotAtt');
    if (elMantraDef) elMantraDef.textContent = `${State.slots.D.players.length}`;
    if (elMantraMed) elMantraMed.textContent = `${State.slots.C.players.length}`;
    if (elMantraAtt) elMantraAtt.textContent = `${State.slots.A.players.length}`;

    const maxSlots = isMantraMode ? 31 : 25;
    const totalSlotsRemaining = Math.max(0, maxSlots - allBought.length);
    const maxSingleBid = totalSlotsRemaining > 0 ? Math.max(1, remaining - (totalSlotsRemaining - 1)) : 0;
    const elBid = document.getElementById('lblMaxBidAllowed');
    if (elBid) elBid.textContent = `${maxSingleBid} CR`;

    const elHdrBud = document.getElementById('hdrRemainingBudget');
    const elHdrCnt = document.getElementById('hdrPlayersCount');
    const elMobBadge = document.getElementById('mobRosterBadge');
    if (elHdrBud) elHdrBud.textContent = `${remaining} CR`;
    if (elHdrCnt) elHdrCnt.textContent = `${allBought.length}/${maxSlots}`;
    if (elMobBadge) elMobBadge.textContent = `${allBought.length}/${maxSlots}`;

    if (typeof renderHeaderLeaguesDropdown === 'function') {
        renderHeaderLeaguesDropdown();
    }

    if (typeof syncBudgetButtonsUI === 'function') {
        syncBudgetButtonsUI();
    }

    renderSidebarRoster();
}

function updateRoleFilterOptionsUI() {
    const sel = document.getElementById('filterRole');
    const isMantra = isAuctionMantraMode();
    
    if (sel) {
        const prevVal = sel.value;
        if (isMantra) {
            sel.innerHTML = `
                <option value="ALL">✨ Tutti i Ruoli Mantra</option>
                <optgroup label="🧤 Portieri">
                    <option value="Por">🧤 Por — Portiere</option>
                </optgroup>
                <optgroup label="🛡️ Linea Difensiva">
                    <option value="DEF_ALL">🛡️ Tutti i Difensori (Dc, B, Dd, Ds)</option>
                    <option value="Dc">🛡️ Dc — Difensore Centrale</option>
                    <option value="B">🛡️ B — Braccetto / Terzo di Difesa</option>
                    <option value="Dd">🛡️ Dd — Terzino Destro</option>
                    <option value="Ds">🛡️ Ds — Terzino Sinistro</option>
                </optgroup>
                <optgroup label="⚙️ Linea Mediana & Esterni">
                    <option value="MID_ALL">⚙️ Tutta la Mediana & Esterni (E, M, C)</option>
                    <option value="E">⚙️ E — Esterno a Tutta Fascia</option>
                    <option value="M">⚙️ M — Mediano Difensivo / Interdittore</option>
                    <option value="C">⚙️ C — Centrocampista Centrale / Mezzala</option>
                </optgroup>
                <optgroup label="⚡ Linea Fantasia & Attacco">
                    <option value="ATT_ALL">⚡ Tutto l'Attacco & Trequarti (T, W, A, Pc)</option>
                    <option value="T">⚡ T — Trequartista / Fantasista</option>
                    <option value="W">⚡ W — Ala Offensiva Pura</option>
                    <option value="A">⚡ A — Seconda Punta / Raccordo</option>
                    <option value="Pc">⚡ Pc — Punta Centrale / Centravanti</option>
                </optgroup>
                <optgroup label="💎 Polivalenti">
                    <option value="MULTI">💎 Multi-Ruolo (2+ Ruoli Mantra)</option>
                </optgroup>
            `;
        } else {
            sel.innerHTML = `
                <option value="ALL">Tutti i Ruoli</option>
                <option value="P">🧤 Portieri (P)</option>
                <option value="D">🛡️ Difensori (D)</option>
                <option value="C">🪄 Centrocampisti (C)</option>
                <option value="A">⚡ Attaccanti (A)</option>
            `;
        }
        
        const isValidOption = Array.from(sel.options).some(o => o.value === prevVal);
        sel.value = isValidOption ? prevVal : 'ALL';
        State.filterRole = sel.value;
    }

    renderMantraQuickBar();
}

function renderMantraQuickBar() {
    const bar = document.getElementById('mantraQuickSubrolesBar');
    if (!bar) return;

    const isMantra = isAuctionMantraMode();
    if (!isMantra) {
        bar.style.display = 'none';
        return;
    }

    bar.style.display = 'flex';

    // Calcolo conteggi reali dal database calciatori
    const counts = {
        ALL: (typeof PLAYERS !== 'undefined') ? PLAYERS.length : 0,
        Por: 0,
        DEF_ALL: 0,
        Dc: 0,
        B: 0,
        Dd: 0,
        Ds: 0,
        MID_ALL: 0,
        E: 0,
        M: 0,
        C: 0,
        ATT_ALL: 0,
        T: 0,
        W: 0,
        A: 0,
        Pc: 0,
        MULTI: 0
    };

    if (typeof PLAYERS !== 'undefined' && typeof isPlayerEligibleForMantraRole === 'function') {
        for (let i = 0; i < PLAYERS.length; i++) {
            const p = PLAYERS[i];
            const m = String(p.mantra || '').split(';').map(s => s.trim().toUpperCase()).filter(Boolean);
            if (m.includes('POR')) counts.Por++;
            if (m.some(r => ['DC', 'B', 'DD', 'DS'].includes(r))) counts.DEF_ALL++;
            if (m.includes('DC')) counts.Dc++;
            if (m.includes('B')) counts.B++;
            if (m.includes('DD')) counts.Dd++;
            if (m.includes('DS')) counts.Ds++;
            if (m.some(r => ['E', 'M', 'C'].includes(r))) counts.MID_ALL++;
            if (m.includes('E')) counts.E++;
            if (m.includes('M')) counts.M++;
            if (m.includes('C')) counts.C++;
            if (m.some(r => ['T', 'W', 'A', 'PC'].includes(r))) counts.ATT_ALL++;
            if (m.includes('T')) counts.T++;
            if (m.includes('W')) counts.W++;
            if (m.includes('A')) counts.A++;
            if (m.includes('PC')) counts.Pc++;
            if (m.length >= 2) counts.MULTI++;
        }
    }

    const cur = State.filterRole || 'ALL';

    bar.innerHTML = `
        <div class="mantra-bar-label">
            <span>🛡️</span> <b>Sottoposizioni:</b>
        </div>
        <button type="button" class="mantra-subrole-pill ${cur === 'ALL' ? 'active' : ''}" data-role="ALL" onclick="setAuctionMantraRoleFilter('ALL')">
            <span>✨ Tutti</span>
            <span class="pill-count">${counts.ALL}</span>
        </button>

        <div class="mantra-subroles-divider"></div>

        <!-- Portieri -->
        <button type="button" class="mantra-subrole-pill ${cur === 'Por' ? 'active' : ''}" data-role="Por" onclick="setAuctionMantraRoleFilter('Por')">
            <span class="mantra-badge por" style="padding:1px 6px;font-size:11px;">Por</span>
            <span>Portieri</span>
            <span class="pill-count">${counts.Por}</span>
        </button>

        <div class="mantra-subroles-divider"></div>

        <!-- Difesa -->
        <button type="button" class="mantra-subrole-pill ${cur === 'DEF_ALL' ? 'active' : ''}" data-role="DEF_ALL" onclick="setAuctionMantraRoleFilter('DEF_ALL')">
            <span>🛡️ Tutti Dif</span>
            <span class="pill-count">${counts.DEF_ALL}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'Dc' ? 'active' : ''}" data-role="Dc" onclick="setAuctionMantraRoleFilter('Dc')">
            <span class="mantra-badge dc" style="padding:1px 6px;font-size:11px;">Dc</span>
            <span>Centrale</span>
            <span class="pill-count">${counts.Dc}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'B' ? 'active' : ''}" data-role="B" onclick="setAuctionMantraRoleFilter('B')">
            <span class="mantra-badge b" style="padding:1px 6px;font-size:11px;">B</span>
            <span>Braccetto</span>
            <span class="pill-count">${counts.B}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'Dd' ? 'active' : ''}" data-role="Dd" onclick="setAuctionMantraRoleFilter('Dd')">
            <span class="mantra-badge dd" style="padding:1px 6px;font-size:11px;">Dd</span>
            <span>Terzino Dx</span>
            <span class="pill-count">${counts.Dd}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'Ds' ? 'active' : ''}" data-role="Ds" onclick="setAuctionMantraRoleFilter('Ds')">
            <span class="mantra-badge ds" style="padding:1px 6px;font-size:11px;">Ds</span>
            <span>Terzino Sx</span>
            <span class="pill-count">${counts.Ds}</span>
        </button>

        <div class="mantra-subroles-divider"></div>

        <!-- Mediana & Fasce -->
        <button type="button" class="mantra-subrole-pill ${cur === 'MID_ALL' ? 'active' : ''}" data-role="MID_ALL" onclick="setAuctionMantraRoleFilter('MID_ALL')">
            <span>⚙️ Tutta Med</span>
            <span class="pill-count">${counts.MID_ALL}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'E' ? 'active' : ''}" data-role="E" onclick="setAuctionMantraRoleFilter('E')">
            <span class="mantra-badge e" style="padding:1px 6px;font-size:11px;">E</span>
            <span>Esterno</span>
            <span class="pill-count">${counts.E}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'M' ? 'active' : ''}" data-role="M" onclick="setAuctionMantraRoleFilter('M')">
            <span class="mantra-badge m" style="padding:1px 6px;font-size:11px;">M</span>
            <span>Mediano</span>
            <span class="pill-count">${counts.M}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'C' ? 'active' : ''}" data-role="C" onclick="setAuctionMantraRoleFilter('C')">
            <span class="mantra-badge c" style="padding:1px 6px;font-size:11px;">C</span>
            <span>Centrocampista</span>
            <span class="pill-count">${counts.C}</span>
        </button>

        <div class="mantra-subroles-divider"></div>

        <!-- Trequarti & Attacco -->
        <button type="button" class="mantra-subrole-pill ${cur === 'ATT_ALL' ? 'active' : ''}" data-role="ATT_ALL" onclick="setAuctionMantraRoleFilter('ATT_ALL')">
            <span>⚡ Tutto Att</span>
            <span class="pill-count">${counts.ATT_ALL}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'T' ? 'active' : ''}" data-role="T" onclick="setAuctionMantraRoleFilter('T')">
            <span class="mantra-badge t" style="padding:1px 6px;font-size:11px;">T</span>
            <span>Trequartista</span>
            <span class="pill-count">${counts.T}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'W' ? 'active' : ''}" data-role="W" onclick="setAuctionMantraRoleFilter('W')">
            <span class="mantra-badge w" style="padding:1px 6px;font-size:11px;">W</span>
            <span>Ala Offensiva</span>
            <span class="pill-count">${counts.W}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'A' ? 'active' : ''}" data-role="A" onclick="setAuctionMantraRoleFilter('A')">
            <span class="mantra-badge a" style="padding:1px 6px;font-size:11px;">A</span>
            <span>Seconda Punta</span>
            <span class="pill-count">${counts.A}</span>
        </button>
        <button type="button" class="mantra-subrole-pill ${cur === 'Pc' ? 'active' : ''}" data-role="Pc" onclick="setAuctionMantraRoleFilter('Pc')">
            <span class="mantra-badge pc" style="padding:1px 6px;font-size:11px;">Pc</span>
            <span>Punta Centrale</span>
            <span class="pill-count">${counts.Pc}</span>
        </button>

        <div class="mantra-subroles-divider"></div>

        <!-- Multi-Ruolo -->
        <button type="button" class="mantra-subrole-pill ${cur === 'MULTI' ? 'active' : ''}" data-role="MULTI" onclick="setAuctionMantraRoleFilter('MULTI')">
            <span style="color:var(--accent-purple);font-size:13px;">💎</span>
            <span>Multi-Ruolo (2+)</span>
            <span class="pill-count">${counts.MULTI}</span>
        </button>
    `;
}

function setAuctionMantraRoleFilter(role) {
    if (State.filterRole === role && role !== 'ALL') {
        State.filterRole = 'ALL';
    } else {
        State.filterRole = role;
    }
    const sel = document.getElementById('filterRole');
    if (sel) sel.value = State.filterRole;
    updateMantraQuickBarActiveState();
    renderTable();
}

function updateMantraQuickBarActiveState() {
    const cur = State.filterRole || 'ALL';
    document.querySelectorAll('.mantra-subrole-pill').forEach(btn => {
        const r = btn.getAttribute('data-role');
        if (r === cur) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// ==============================================================================
// MODELLO DINAMICO BUDGET PER SLOT (TARATO SU 1000 CREDITI)
// ==============================================================================
const BASELINE_SLOT_BUDGETS = {
    P: [45, 14, 1],                      // 60 CR total (6%): 1° Big, 2° Alternanza, 3° Terzo
    D: [45, 28, 20, 15, 10, 6, 4, 2],    // 130 CR total (13%): 1° Top/Mod, 2° Semibig, 3°-5° Titolari, 6°-8° Scommesse/Coperture
    C: [110, 75, 45, 30, 20, 15, 10, 5], // 310 CR total (31%): 1° Top/Rigorista, 2° Semitop/Ala, 3°-5° Titolari, 6°-8° Scommesse/Coperture
    A: [275, 130, 55, 25, 12, 3]         // 500 CR total (50%): 1° Top, 2° Semitop, 3° Titolare, 4° Rotazione, 5° Scommessa, 6° Copertura
};

function getSlotBudgetAnalysis() {
    const scale = (State.budgetTotal || 1000) / 1000;
    const remaining = State.budgetTotal - State.budgetSpent;
    
    const roleConfigs = [
        { role: 'P', max: 3 },
        { role: 'D', max: 8 },
        { role: 'C', max: 8 },
        { role: 'A', max: 6 }
    ];

    let totalBought = 0;
    const deptSlots = {};

    roleConfigs.forEach(cfg => {
        const role = cfg.role;
        const baselines = BASELINE_SLOT_BUDGETS[role];
        const boughtPlayers = (State.slots[role].players || []).map((p, origIdx) => ({
            ...p,
            origIdx,
            intendedSlot: Math.min(cfg.max, Math.max(1, p.slot_num || 1))
        }));

        totalBought += boughtPlayers.length;

        // Inizializza gli slot da 1 a max
        const slots = [];
        for (let i = 1; i <= cfg.max; i++) {
            slots.push({
                slotNum: i,
                baseTarget: Math.round((baselines[i - 1] || 1) * scale),
                player: null,
                origIdx: null
            });
        }

        // Ordina i giocatori acquistati: per spesa decrescente o per slot_num
        const sorted = [...boughtPlayers].sort((a, b) => {
            if ((b.paidPrice || 0) !== (a.paidPrice || 0)) {
                return (b.paidPrice || 0) - (a.paidPrice || 0);
            }
            return (a.intendedSlot || 1) - (b.intendedSlot || 1);
        });

        // Assegna ciascun giocatore allo slot ideale o al più vicino libero
        sorted.forEach(p => {
            let pref = p.intendedSlot - 1;
            if (!slots[pref].player) {
                slots[pref].player = p;
                slots[pref].origIdx = p.origIdx;
            } else {
                let bestIdx = -1;
                let bestDist = 999;
                for (let j = 0; j < cfg.max; j++) {
                    if (!slots[j].player) {
                        const dist = Math.abs(j - pref);
                        if (dist < bestDist) {
                            bestDist = dist;
                            bestIdx = j;
                        }
                    }
                }
                if (bestIdx !== -1) {
                    slots[bestIdx].player = p;
                    slots[bestIdx].origIdx = p.origIdx;
                }
            }
        });

        deptSlots[role] = slots;
    });

    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const maxRosterSlots = isMantraMode ? 31 : 25;
    const totalSlotsRemaining = Math.max(0, maxRosterSlots - totalBought);
    const maxSingleBid = totalSlotsRemaining > 0 ? Math.max(1, remaining - (totalSlotsRemaining - 1)) : 0;
    const freePool = Math.max(0, remaining - totalSlotsRemaining);

    // Calcola il fabbisogno teorico sopra il credito minimo per gli slot liberi
    let sumUnfilledWeights = 0;
    roleConfigs.forEach(cfg => {
        deptSlots[cfg.role].forEach(s => {
            if (!s.player) {
                const wAbove1 = Math.max(0, s.baseTarget - 1);
                sumUnfilledWeights += wAbove1;
                s.wAbove1 = wAbove1;
            }
        });
    });

    const pacingRatio = sumUnfilledWeights > 0 ? (freePool / sumUnfilledWeights) : (totalSlotsRemaining === 0 ? 1 : 0);

    // Ricalcola il target dinamico per ciascuno slot vuoto
    roleConfigs.forEach(cfg => {
        deptSlots[cfg.role].forEach(s => {
            if (!s.player) {
                let dynTarget;
                if (freePool <= 0) {
                    dynTarget = 1;
                } else if (sumUnfilledWeights > 0) {
                    dynTarget = 1 + Math.round(s.wAbove1 * pacingRatio);
                } else {
                    dynTarget = Math.max(1, Math.floor(remaining / Math.max(1, totalSlotsRemaining)));
                }
                dynTarget = Math.min(dynTarget, maxSingleBid);
                dynTarget = Math.max(1, dynTarget);
                s.dynTarget = dynTarget;
                s.pacingRatio = pacingRatio;
            } else {
                s.delta = (s.player.paidPrice || 0) - s.baseTarget;
            }
        });
    });

    return {
        remaining,
        totalBought,
        totalSlotsRemaining,
        maxSingleBid,
        freePool,
        pacingRatio,
        deptSlots
    };
}

function filterBySlotShortcut(role, slotNum) {
    if (typeof switchTab === 'function') switchTab('auction');
    const roleSelect = document.getElementById('filterRole');
    const slotSelect = document.getElementById('filterSlot');
    const availCheck = document.getElementById('chkFilterAvailable');

    if (roleSelect) {
        roleSelect.value = role;
        State.filterRole = role;
    }
    if (slotSelect) {
        const slotVal = `${slotNum}° Slot`;
        let found = false;
        for (let opt of slotSelect.options) {
            if (opt.value === slotVal) {
                slotSelect.value = slotVal;
                State.filterSlot = slotVal;
                found = true;
                break;
            }
        }
        if (!found) {
            slotSelect.value = 'ALL';
            State.filterSlot = 'ALL';
        }
    }
    if (availCheck) {
        availCheck.checked = true;
        State.filterOnlyAvailable = true;
    }
    renderTable();
}

function renderSidebarRoster() {
    const container = document.getElementById('sidebarRosterContainer');
    if (!container) return;
    const healthContainer = document.getElementById('sidebarBudgetHealthContainer');
    const analysis = getSlotBudgetAnalysis();
    
    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const maxSlots = isMantraMode ? 31 : 25;

    // Update summary card in sidebar
    const elRem = document.getElementById('sidebarBudgetRem');
    const elSpn = document.getElementById('sidebarBudgetSpent');
    const elSlots = document.getElementById('sidebarSlotsFilled');
    const elMaxBid = document.getElementById('sidebarMaxBid');
    const elProg = document.getElementById('sidebarProgressBar');

    if (elRem) elRem.textContent = `${analysis.remaining} CR`;
    if (elSpn) elSpn.textContent = `${State.budgetSpent} CR`;
    if (elSlots) elSlots.textContent = `${analysis.totalBought} / ${maxSlots}`;
    if (elMaxBid) elMaxBid.textContent = `${analysis.maxSingleBid} CR`;
    if (elProg) elProg.style.width = `${(analysis.totalBought / maxSlots) * 100}%`;

    // Render Pill di Salute Finanziaria Dinamica
    if (healthContainer) {
        let healthClass = 'balanced';
        let healthIcon = '⚖️';
        let healthTitle = 'Budget In Equilibrio';
        let healthSubtitle = 'Target slot ottimali';

        if (analysis.totalBought === 0) {
            healthClass = 'balanced';
            healthIcon = '⚖️';
            healthTitle = `Budget Base ${State.budgetTotal || 1000} CR`;
            healthSubtitle = `Tutti i ${maxSlots} slot ai valori target`;
        } else if (analysis.pacingRatio >= 1.25) {
            const extraPct = Math.round((analysis.pacingRatio - 1) * 100);
            healthClass = 'surplus';
            healthIcon = '✨';
            healthTitle = `Extra Budget (+${extraPct}%)`;
            healthSubtitle = 'Slot rimanenti potenziati';
        } else if (analysis.pacingRatio >= 1.05) {
            healthClass = 'surplus';
            healthIcon = '🟢';
            healthTitle = 'Ottima Gestione (Attivo)';
            healthSubtitle = 'Leggero margine di spesa';
        } else if (analysis.pacingRatio >= 0.85) {
            healthClass = 'balanced';
            healthIcon = '⚖️';
            healthTitle = 'In Equilibrio Finanziario';
            healthSubtitle = 'Spesa perfettamente sostenibile';
        } else if (analysis.pacingRatio >= 0.50) {
            const cutPct = Math.round((1 - analysis.pacingRatio) * 100);
            healthClass = 'deficit';
            healthIcon = '⚠️';
            healthTitle = `Budget Ristretto (-${cutPct}%)`;
            healthSubtitle = 'Slot rimanenti ridotti';
        } else {
            healthClass = 'critical';
            healthIcon = '🚨';
            healthTitle = 'Allarme Riserva';
            healthSubtitle = 'Completa a 1 CR';
        }

        healthContainer.innerHTML = `
            <div class="sidebar-budget-health ${healthClass}" title="Rapporto di liquidità dinamico: ${Math.round(analysis.pacingRatio * 100)}% rispetto al piano iniziale">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:13px;">${healthIcon}</span>
                    <div>
                        <div style="font-size:10.5px;font-weight:800;">${healthTitle}</div>
                        <div style="font-size:9px;opacity:0.8;">${healthSubtitle}</div>
                    </div>
                </div>
                <div style="font-size:10.5px;font-weight:800;font-family:'Outfit',sans-serif;">${Math.round(analysis.pacingRatio * 100)}%</div>
            </div>
        `;
    }

    if (!container) return;

    // RENDER MANTRA: Nessuna divisione rigida P, D, C, A - 3 Portieri + 28 Movimento in ordine gerarchico Mantra
    if (isMantraMode) {
        const porList = State.slots.P.players || [];
        const movList = [...(State.slots.D.players || []), ...(State.slots.C.players || []), ...(State.slots.A.players || [])];

        const sortedMov = [...movList].sort((a, b) => {
            const scoreA = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(a.mantra) : 50;
            const scoreB = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(b.mantra) : 50;
            if (scoreA !== scoreB) return scoreA - scoreB;
            if ((b.paidPrice || 0) !== (a.paidPrice || 0)) return (b.paidPrice || 0) - (a.paidPrice || 0);
            return (b.ovr || 0) - (a.ovr || 0);
        });

        let html = '';

        // 1. Box Portieri (Liberi in Mantra: 3 o più)
        const porTargetSlots = Math.max(3, porList.length);
        html += `
            <div class="roster-dept">
                <div class="roster-dept-header">
                    <span style="color:var(--mantra-por);">🧤 Portieri (Por)</span>
                    <span style="font-size:11px;color:var(--text-secondary);font-weight:800;">${porList.length} in rosa</span>
                </div>
        `;
        for (let i = 0; i < porTargetSlots; i++) {
            const p = porList[i];
            if (p) {
                html += `
                    <div class="roster-slot-item">
                        <div style="display:flex;align-items:center;gap:6px;min-width:0;">
                            <span class="role-badge-mini P" style="background:var(--mantra-por);color:#fff;font-size:9px;padding:1px 4px;">Por</span>
                            <span style="font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})" title="${p.name} (${p.team}) - OVR ${p.ovr}">${p.name}</span>
                            <span style="font-size:10px;color:var(--text-muted);">${p.team.substring(0,3).toUpperCase()}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
                            <span style="color:var(--accent-gold);font-weight:800;font-size:11px;">${p.paidPrice} CR</span>
                            <button class="roster-del-btn" title="Rimuovi portiere" onclick="removePlayerById(${p.id})">✕</button>
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="roster-slot-empty" style="cursor:default;" title="Slot Portiere Libero">
                        <span class="slot-empty-title">+ Portiere ${i + 1} Libero</span>
                        <span class="slot-target-tag normal">min 1 CR</span>
                    </div>
                `;
            }
        }
        html += `</div>`;

        // 2. Box Giocatori di Movimento ordinati per ruolo Mantra
        html += `
            <div class="roster-dept">
                <div class="roster-dept-header" style="background:rgba(2,132,199,0.12);">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="color:var(--accent-cyan);">🏃‍♂️ Giocatori Movimento</span>
                        <span style="font-size:9.5px;color:var(--text-muted);">(in ordine)</span>
                    </div>
                    <span style="font-size:11px;color:var(--text-secondary);font-weight:800;">${sortedMov.length} in rosa</span>
                </div>
        `;
        sortedMov.forEach(p => {
            const roleBadgeHtml = (typeof renderMantraRoleBadges === 'function') 
                ? renderMantraRoleBadges(p.mantra) 
                : `<span class="role-badge ${p.role}">${p.role}</span>`;
            html += `
                <div class="roster-slot-item">
                    <div style="display:flex;align-items:center;gap:6px;min-width:0;">
                        ${roleBadgeHtml}
                        <span style="font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})" title="${p.name} (${p.team}) - ${p.mantra}">${p.name}</span>
                        <span style="font-size:10px;color:var(--text-muted);">${p.team.substring(0,3).toUpperCase()}</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
                        <span style="color:var(--accent-gold);font-weight:800;font-size:11px;">${p.paidPrice} CR</span>
                        <button class="roster-del-btn" title="Rimuovi calciatore" onclick="removePlayerById(${p.id})">✕</button>
                    </div>
                </div>
            `;
        });
        const totalRosterCount = porList.length + sortedMov.length;
        const emptyTotalSlots = Math.max(0, 31 - totalRosterCount);
        if (emptyTotalSlots > 0) {
            html += `
                <div class="roster-slot-empty" style="cursor:default;margin-top:4px;">
                    <span class="slot-empty-title">+ ${emptyTotalSlots} slot liberi in rosa</span>
                    <span class="slot-target-tag normal">Max 31 Totali</span>
                </div>
            `;
        }
        html += `</div>`;

        container.innerHTML = html;
        return;
    }

    // RENDER CLASSIC: 4 reparti P (3), D (8), C (8), A (6)
    const roleConfig = [
        { role: 'P', name: '🧤 Portieri', max: 3, color: 'var(--role-p)' },
        { role: 'D', name: '🛡️ Difensori', max: 8, color: 'var(--role-d)' },
        { role: 'C', name: '🪄 Centrocampisti', max: 8, color: 'var(--role-c)' },
        { role: 'A', name: '⚡ Attaccanti', max: 6, color: 'var(--role-a)' }
    ];

    let html = '';
    roleConfig.forEach(cfg => {
        const slots = analysis.deptSlots[cfg.role] || [];
        const boughtCount = slots.filter(s => s.player).length;

        html += `
            <div class="roster-dept">
                <div class="roster-dept-header">
                    <span style="color:${cfg.color};">${cfg.name}</span>
                    <span style="font-size:11px;color:var(--text-secondary);">${boughtCount}/${cfg.max}</span>
                </div>
        `;

        slots.forEach(s => {
            if (s.player) {
                const p = s.player;
                let deltaHtml = '';
                if (s.delta > 0) {
                    deltaHtml = `<span class="slot-delta-badge over" title="Spesi +${s.delta} CR sopra il target base di ${s.baseTarget} CR">+${s.delta}</span>`;
                } else if (s.delta < 0) {
                    deltaHtml = `<span class="slot-delta-badge saved" title="Risparmiati ${Math.abs(s.delta)} CR rispetto al target base di ${s.baseTarget} CR">${s.delta}</span>`;
                } else {
                    deltaHtml = `<span class="slot-delta-badge equal" title="In target perfetto (${s.baseTarget} CR)">=</span>`;
                }

                const roleBadgeHtml = `<span class="role-badge ${cfg.role}" style="font-size:8.5px;padding:1px 4px;" title="Slot ${s.slotNum}">${s.slotNum}°</span>`;

                html += `
                    <div class="roster-slot-item">
                        <div style="display:flex;align-items:center;gap:6px;min-width:0;">
                            ${roleBadgeHtml}
                            <span style="font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})" title="${p.name} (${p.team}) - OVR ${p.ovr}">${p.name}</span>
                            <span style="font-size:10px;color:var(--text-muted);">${p.team.substring(0,3).toUpperCase()}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
                            ${deltaHtml}
                            <span style="color:var(--accent-gold);font-weight:800;font-size:11px;">${p.paidPrice} CR</span>
                            <button class="roster-del-btn" title="Rimuovi calciatore" onclick="removePlayerFromRoster('${cfg.role}', ${s.origIdx})">✕</button>
                        </div>
                    </div>
                `;
            } else {
                let tagClass = 'normal';
                let tagBadge = '';
                if (s.pacingRatio >= 1.18 && s.dynTarget > s.baseTarget) {
                    tagClass = 'extra';
                    tagBadge = '✨ ';
                } else if (s.pacingRatio < 0.82 && s.dynTarget < s.baseTarget) {
                    tagClass = 'tight';
                    tagBadge = '⚠️ ';
                } else if (s.dynTarget <= 1) {
                    tagClass = 'critical';
                }

                html += `
                    <div class="roster-slot-empty" onclick="filterBySlotShortcut('${cfg.role}', ${s.slotNum})" title="Slot ${s.slotNum} Libero: Budget dinamico consigliato ~${s.dynTarget} CR (Base: ${s.baseTarget} CR). Clicca per cercare giocatori di ${s.slotNum}° fascia.">
                        <span class="slot-empty-title">+ Slot ${s.slotNum} Libero</span>
                        <span class="slot-target-tag ${tagClass}">${tagBadge}max ~${s.dynTarget} CR</span>
                    </div>
                `;
            }
        });

        html += `</div>`;
    });

    container.innerHTML = html;
}

function renderTable() {
    const tbody = document.getElementById('auctionTableBody');
    if (!tbody) return;

    const isMantraTable = isAuctionMantraMode();

    let filtered = PLAYERS.filter(p => {
        if (State.filterRole && State.filterRole !== 'ALL') {
            if (isMantraTable) {
                if (typeof isPlayerEligibleForMantraRole === 'function' && !isPlayerEligibleForMantraRole(p, State.filterRole)) return false;
            } else {
                if (p.role !== State.filterRole) return false;
            }
        }
        if (State.filterTeam && State.filterTeam !== 'ALL' && p.team !== State.filterTeam) return false;
        if (State.filterSlot && State.filterSlot !== 'ALL' && (!p.slot_fascia || !p.slot_fascia.includes(State.filterSlot))) return false;
        if (State.filterAdvice && State.filterAdvice !== 'ALL' && p.ai_advice_type !== State.filterAdvice) return false;
        if (State.filterFragilita && State.filterFragilita !== 'ALL' && (p.fragilita_badge || 'bassa') !== State.filterFragilita) return false;

        // Rigoristi & Calci Piazzati
        if (State.filterRigoristi && State.filterRigoristi !== 'ALL') {
            const isRig1 = !!(p.is_rigorista_1 || p.rigorista_val === '1° Rigorista');
            const isRig2 = !!(p.is_rigorista_2 || p.rigorista_val === '2° Rigorista');
            const isRig3 = !!(p.is_rigorista_3 || p.rigorista_val === '3° Rigorista');
            const isAnyRig = isRig1 || isRig2 || isRig3 || (p.rigorista_val && p.rigorista_val !== '-');
            const isPiazzati = !!(p.is_punizioni || p.is_corner || (p.piazzati_val && p.piazzati_val !== '-'));
            
            if (State.filterRigoristi === 'any_rig' && !isAnyRig) return false;
            if (State.filterRigoristi === 'rig_1' && !isRig1) return false;
            if (State.filterRigoristi === 'rig_2_3' && !isRig2 && !isRig3) return false;
            if (State.filterRigoristi === 'piazzati' && !isPiazzati) return false;
        }

        // Titolarità Stimata
        if (State.filterTitolarita && State.filterTitolarita !== 'ALL') {
            const tit = (p.titolarita !== undefined && p.titolarita !== null) ? p.titolarita : 50;
            if (State.filterTitolarita === 'tit_85' && tit < 85) return false;
            if (State.filterTitolarita === 'tit_70' && (tit < 70 || tit >= 85)) return false;
            if (State.filterTitolarita === 'tit_ballottaggio' && (tit < 50 || tit >= 70)) return false;
            if (State.filterTitolarita === 'tit_riserva' && tit >= 50) return false;
        }

        // Fascia Prezzo FVM
        if (State.filterPriceRange && State.filterPriceRange !== 'ALL') {
            const price = Number(p.fvm || p.qta || 1);
            if (State.filterPriceRange === 'top' && price < 100) return false;
            if (State.filterPriceRange === 'high' && (price < 40 || price >= 100)) return false;
            if (State.filterPriceRange === 'mid' && (price < 15 || price >= 40)) return false;
            if (State.filterPriceRange === 'low' && (price < 5 || price >= 15)) return false;
            if (State.filterPriceRange === 'budget' && price >= 5) return false;
        }

        if (State.filterOop && (!p.oop_val || p.oop_val === '-')) return false;
        if (State.filterInjured && !p.is_injured) return false;
        if (State.filterHealthy && p.is_injured) return false;

        // Solo Svincolati (non acquistati né da me né da altre squadre)
        if (State.filterOnlyAvailable && !isPlayerAvailable(p.id)) return false;
        if (State.filterOnlyFavorites && !isFavorite(p.id)) return false;

        if (State.searchQuery) {
            const q = State.searchQuery.toLowerCase();
            const matchName = p.name.toLowerCase().includes(q);
            const matchTeam = p.team.toLowerCase().includes(q);
            const matchMantra = (p.mantra || '').toLowerCase().includes(q);
            if (!matchName && !matchTeam && !matchMantra) return false;
        }
        return true;
    });

    // Ordinamento
    filtered.sort((a, b) => {
        if (State.sortBy === 'role') {
            if (isMantraTable) {
                const ordA = typeof getMantraHierarchyScore === 'function' ? getMantraHierarchyScore(a.mantra) : 99;
                const ordB = typeof getMantraHierarchyScore === 'function' ? getMantraHierarchyScore(b.mantra) : 99;
                if (ordA !== ordB) return State.sortAsc ? ordA - ordB : ordB - ordA;
                return (b.ovr || 0) - (a.ovr || 0);
            } else {
                const roleOrder = { 'P': 1, 'D': 2, 'C': 3, 'A': 4 };
                const ordA = roleOrder[a.role] || 5;
                const ordB = roleOrder[b.role] || 5;
                if (ordA !== ordB) return State.sortAsc ? ordA - ordB : ordB - ordA;
                return (b.ovr || 0) - (a.ovr || 0);
            }
        }

        if (State.sortBy === 'xg_2627') {
            vA = (a.xg_2627 !== null && a.xg_2627 !== undefined) ? a.xg_2627 : (a.xg90_2627 ? parseFloat(a.xg90_2627) : 0);
            vB = (b.xg_2627 !== null && b.xg_2627 !== undefined) ? b.xg_2627 : (b.xg90_2627 ? parseFloat(b.xg90_2627) : 0);
        } else if (State.sortBy === 'xa_2627') {
            vA = (a.xa_2627 !== null && a.xa_2627 !== undefined) ? a.xa_2627 : (a.xa90_2627 ? parseFloat(a.xa90_2627) : 0);
            vB = (b.xa_2627 !== null && b.xa_2627 !== undefined) ? b.xa_2627 : (b.xa90_2627 ? parseFloat(b.xa90_2627) : 0);
        } else if (State.sortBy === 'minuti_2627') {
            vA = a.minuti_2627 || a.minuti_stat_2627 || 0;
            vB = b.minuti_2627 || b.minuti_stat_2627 || 0;
        } else if (State.sortBy === 'amm_2627') {
            vA = (a.amm_2627 || 0) + (a.esp_2627 || 0) * 2;
            vB = (b.amm_2627 || 0) + (b.esp_2627 || 0) * 2;
        }

        let vA = a[State.sortBy];
        let vB = b[State.sortBy];
        if (State.sortBy === 'xfm' || State.sortBy === 'delta_xfm') {
            if ((vA === undefined || vA === null) && typeof computeExpectedFantaMedia === 'function') {
                const resA = computeExpectedFantaMedia(a);
                vA = State.sortBy === 'xfm' ? resA.xfm : resA.delta;
            }
            if ((vB === undefined || vB === null) && typeof computeExpectedFantaMedia === 'function') {
                const resB = computeExpectedFantaMedia(b);
                vB = State.sortBy === 'xfm' ? resB.xfm : resB.delta;
            }
        }
        if (vA === undefined || vA === null) vA = State.sortAsc ? 999999 : -999999;
        if (vB === undefined || vB === null) vB = State.sortAsc ? 999999 : -999999;
        if (typeof vA === 'string') vA = vA.toLowerCase();
        if (typeof vB === 'string') vB = vB.toLowerCase();
        if (vA < vB) return State.sortAsc ? -1 : 1;
        if (vA > vB) return State.sortAsc ? 1 : -1;
        return 0;
    });

    const countEl = document.getElementById('lblPlayerCount');
    if (countEl) {
        countEl.textContent = `Mostrati: ${filtered.length} / ${PLAYERS.length} Calciatori`;
    }

    tbody.innerHTML = '';

    filtered.forEach(p => {
        try {
            const tr = document.createElement('tr');
            const isBought = isPlayerBought(p.id);
            const isTaken = isPlayerTakenByOther(p.id);
            const isFav = isFavorite(p.id);
            if (isBought) tr.classList.add('bought-row');
            if (isTaken) tr.classList.add('taken-row');

            const ovrTierClass = getOvrClass(p.ovr);
            
            // Azioni (Modalità Consultazione: creazione squadra bloccata con Coming Soon)
            let actionCellHtml = '';
            if (isBought) {
                actionCellHtml = `<span class="action-status bought" title="Nella tua rosa">✓</span>`;
            } else if (isTaken) {
                actionCellHtml = `
                    <div class="action-cell-group">
                        <span class="action-status taken" title="Preso da altra squadra">⛔</span>
                        <button class="btn-clean-undo" title="Annulla assegnazione (In Arrivo)" onclick="showComingSoonModal('Gestione Rose & Asta Live')">🔒</button>
                    </div>
                `;
            } else {
                actionCellHtml = `
                    <div class="action-cell-group">
                        <button class="btn-clean-add" onclick="showComingSoonModal('Creazione Squadra & Asta Live')" title="Crea Squadra / Acquista (In Arrivo per l'asta di riparazione)" style="opacity:0.85;font-size:11px;cursor:pointer;">🔒</button>
                        <button class="btn-clean-rival" title="Assegna a rivale (In Arrivo)" onclick="showComingSoonModal('Assegnazione Squadre & Asta Live')" style="opacity:0.75;font-size:10px;cursor:pointer;">⛔</button>
                    </div>
                `;
            }

            // Ruolo Cell
            const roleCellHtml = isMantraTable 
                ? (typeof renderMantraRoleBadges === 'function' ? renderMantraRoleBadges(p.mantra) : `<span class="role-badge ${p.role}">${p.role}</span>`)
                : `<span class="role-badge ${p.role}">${p.role}</span>`;

            // Calciatore & Sub-info
            const mantraSubLabel = (isMantraTable || !p.mantra) ? '' : `<span class="mantra-sub-txt">${p.mantra}</span>`;
            const injIcon = p.is_injured ? `<span class="inj-indicator" title="${p.infortunio_motivo || 'Infortunato'} (Rientro: ${p.infortunio_rientro || 'TBD'})">🩹</span>` : '';
            const customBadge = p.is_custom_edited ? `<span class="mod-pill" title="Personalizzato">Mod</span>` : '';

            // Smart Badge: visualizzazione standard (tag singolo compatto) vs avanzata (tutti i tag posseduti)
            const singleSmartTag = getSmartBadgeHtml(p);
            const multiSmartTags = getAllSmartBadgesHtml(p);
            const smartTagHtml = `
                <div class="col-tag-standard">${singleSmartTag}</div>
                <div class="col-tag-advanced">${multiSmartTags}</div>
            `;

            // Titolarità
            let titClass = 'tit-mid';
            if (p.titolarita >= 85) titClass = 'tit-high';
            else if (p.titolarita < 60) titClass = 'tit-low';
            const titHtml = `<span class="tit-pill ${titClass}" title="Titolarità stimata: ${p.titolarita || 0}%">${p.titolarita || 0}%</span>`;

            // Sostituto / Coppia Dinamica basata su titolarità effettiva
            let coppiaHtml = `<span class="dim-dash">-</span>`;
            if (p.coppia_nome && p.coppia_nome !== '-') {
                const clickHandler = p.coppia_id ? `onclick="openPlayerProfileModal(${p.coppia_id})"` : '';
                const clickStyle = p.coppia_id ? 'cursor:pointer;' : 'cursor:default;';

                let icon = '🔄';
                let rolePrefix = '';
                const tit = (p.titolarita !== undefined && p.titolarita !== null) ? p.titolarita : 50;

                if (p.role === 'P') {
                    if (tit >= 82) {
                        icon = '🛡️';
                        rolePrefix = 'Vice: ';
                    } else if (tit <= 38) {
                        icon = '⬆️';
                        rolePrefix = '1°: ';
                    } else {
                        icon = '⚖️';
                        rolePrefix = 'Staffetta: ';
                    }
                } else {
                    if (tit >= 75) {
                        icon = '⬇️';
                        rolePrefix = 'Ris: ';
                    } else if (tit <= 35) {
                        icon = '⬆️';
                        rolePrefix = 'Tit: ';
                    } else {
                        icon = '🔄';
                        rolePrefix = 'Ball.: ';
                    }
                }

                coppiaHtml = `<span class="coppia-pill" style="${clickStyle}" ${clickHandler} title="${p.coppia_dettaglio || `${rolePrefix}${p.coppia_nome}`}">${icon} ${rolePrefix}${p.coppia_nome}</span>`;
            }

            // Statistiche 2026/2027 Live
            const mv2627Str = p.mv_2627 ? `<span class="stat-live mv">${p.mv_2627.toFixed(2)}</span>` : `<span class="dim-dash">-</span>`;
            const fm2627Str = p.fm_2627 ? `<span class="stat-live fm">${p.fm_2627.toFixed(2)}</span>` : `<span class="dim-dash">-</span>`;

            // Expected FantaMedia (xFM) & Delta Performance (FM - xFM)
            let xfmVal = p.xfm;
            let deltaVal = p.delta_xfm;
            if (xfmVal === undefined || xfmVal === null) {
                if (typeof computeExpectedFantaMedia === 'function') {
                    const xfmData = computeExpectedFantaMedia(p);
                    xfmVal = xfmData.xfm;
                    deltaVal = xfmData.delta;
                }
            }

            const xfmStr = (xfmVal !== undefined && xfmVal !== null && !isNaN(xfmVal))
                ? `<span class="stat-live xfm" style="font-weight:800;color:var(--accent-cyan);" title="Expected FantaMedia: ${Number(xfmVal).toFixed(2)}">${Number(xfmVal).toFixed(2)}</span>`
                : `<span class="dim-dash">-</span>`;

            let deltaHtml = `<span class="dim-dash">-</span>`;
            if (deltaVal !== undefined && deltaVal !== null && !isNaN(deltaVal)) {
                const dNum = Number(deltaVal);
                if (dNum > 0.25) {
                    deltaHtml = `<span class="delta-pill delta-over" title="Overperformance (+${dNum.toFixed(2)}): Ha raccolto più bonus rispetto al volume di gioco/xG/xA prodotto">+${dNum.toFixed(2)}</span>`;
                } else if (dNum < -0.25) {
                    deltaHtml = `<span class="delta-pill delta-under" title="Underperformance (${dNum.toFixed(2)}): OCCASIONE! Ha prodotto alto volume di gioco/xG/xA ma ha raccolto meno bonus per sfortuna">${dNum.toFixed(2)} 💎</span>`;
                } else {
                    const sign = dNum >= 0 ? '+' : '';
                    deltaHtml = `<span class="delta-pill delta-neutral" title="In linea con i dati attesi (${sign}${dNum.toFixed(2)})">${sign}${dNum.toFixed(2)}</span>`;
                }
            }

            let ga2627Html = `<span class="dim-dash">0/0</span>`;
            if (p.role === 'P') {
                if (p.has_data_2627 && p.presenze_2627 > 0) {
                    ga2627Html = `<span class="stat-gk-ga">${p.gol_subiti_2627 || 0}</span> <small class="stat-gk-cs">(${p.clean_sheets_2627 || 0})</small>`;
                } else {
                    ga2627Html = `<span class="dim-dash">-</span>`;
                }
            } else {
                if (p.has_data_2627 && p.presenze_2627 > 0) {
                    const gText = p.gol_2627 > 0 ? `<b class="stat-gol">${p.gol_2627}</b>` : `<span>0</span>`;
                    const aText = p.assist_2627 > 0 ? `<b class="stat-ass">${p.assist_2627}</b>` : `<span>0</span>`;
                    ga2627Html = `${gText}/${aText}`;
                } else {
                    ga2627Html = `<span class="dim-dash">0/0</span>`;
                }
            }

            // Statistiche Avanzate (Visuale Statistiche Avanzate)
            const xgVal = (p.xg_2627 !== null && p.xg_2627 !== undefined) ? p.xg_2627 : (p.xg90_2627 ? parseFloat(p.xg90_2627) : null);
            const xgHtml = (xgVal !== null && !isNaN(xgVal))
                ? `<span class="stat-live xg" style="color:#f472b6;font-weight:700;">${Number(xgVal).toFixed(2)}</span>`
                : `<span class="dim-dash">-</span>`;

            const xaVal = (p.xa_2627 !== null && p.xa_2627 !== undefined) ? p.xa_2627 : (p.xa90_2627 ? parseFloat(p.xa90_2627) : null);
            const xaHtml = (xaVal !== null && !isNaN(xaVal))
                ? `<span class="stat-live xa" style="color:#38bdf8;font-weight:700;">${Number(xaVal).toFixed(2)}</span>`
                : `<span class="dim-dash">-</span>`;

            const minsVal = p.minuti_2627 || p.minuti_stat_2627 || (p.presenze_2627 ? (p.presenze_2627 * 75) : null);
            const minHtml = minsVal
                ? `<span class="stat-live mins" style="color:#a78bfa;font-size:11.5px;font-weight:600;">${minsVal}'</span>`
                : `<span class="dim-dash">-</span>`;

            const ammVal = p.amm_2627 || 0;
            const espVal = p.esp_2627 || 0;
            const cardsHtml = (ammVal > 0 || espVal > 0)
                ? `<span class="stat-live cards" style="font-size:11px;font-weight:700;">${ammVal ? ammVal+'🟨' : ''}${espVal ? ' '+espVal+'🟥' : ''}</span>`
                : `<span class="dim-dash">-</span>`;

            // FVM Scalato su budget dinamico (1000, 500, Custom)
            const bRatio = (typeof getGlobalBudgetRatio === 'function') ? getGlobalBudgetRatio() : ((typeof State !== 'undefined' && State.budgetTotal ? State.budgetTotal : 1000) / 1000);
            const currentB = (typeof State !== 'undefined' && State.budgetTotal) ? State.budgetTotal : 1000;
            const scaledFvm = (p.fvm !== undefined && p.fvm !== null) ? Math.max(1, Math.round(p.fvm * bRatio)) : '-';
            const fvmPct = (p.fvm !== undefined && p.fvm !== null) ? (((p.fvm || 0) / 1000) * 100).toFixed(1) : null;
            const fvmTip = fvmPct !== null ? `FVM: ${scaledFvm} CR (${fvmPct}% del budget su ${currentB} CR)` : 'FVM non disponibile';

            tr.innerHTML = `
                <td style="text-align:center;"><span class="ovr-pill ${ovrTierClass}">${p.ovr}</span></td>
                <td style="text-align:center;">${roleCellHtml}</td>
                <td onclick="if(!event.target.closest('button')) openPlayerProfileModal(${p.id})" style="cursor:pointer;" title="Clicca per aprire la Scheda Calciatore">
                    <div class="player-name-cell">
                        <button class="sb-star-toggle ${isFav ? 'active' : ''}" onclick="toggleFavorite(${p.id})" title="Preferito">${isFav ? '⭐' : '☆'}</button>
                        <span class="player-name-link" title="Apri Scheda Calciatore">${p.name}</span>
                        ${injIcon}
                        ${mantraSubLabel}
                        ${customBadge}
                    </div>
                </td>
                <td><span class="team-cell">${p.team}</span></td>
                <td style="text-align:center;"><span class="price-pill" title="${fvmTip}">${scaledFvm}</span></td>
                <td style="text-align:center;"><span class="qta-val">${p.qta !== undefined && p.qta !== null ? p.qta : '-'}</span></td>
                <td>${smartTagHtml}</td>
                <td style="text-align:center;">${titHtml}</td>
                <td>${coppiaHtml}</td>
                <td style="text-align:center;">${mv2627Str}</td>
                <td style="text-align:center;">${fm2627Str}</td>
                <td style="text-align:center;">${xfmStr}</td>
                <td style="text-align:center;">${deltaHtml}</td>
                <td style="text-align:center;">${ga2627Html}</td>
                <td class="col-adv-stat" style="text-align:center;">${xgHtml}</td>
                <td class="col-adv-stat" style="text-align:center;">${xaHtml}</td>
                <td class="col-adv-stat" style="text-align:center;">${minHtml}</td>
                <td class="col-adv-stat" style="text-align:center;">${cardsHtml}</td>
                <td style="text-align:center;">${actionCellHtml}</td>
            `;
            tbody.appendChild(tr);
        } catch (rowErr) {
            console.error("Errore rendering riga calciatore:", p, rowErr);
        }
    });
}

function setAuctionTableView(mode) {
    const table = document.getElementById('auctionTable');
    const btnStd = document.getElementById('btnViewStandard');
    const btnAdv = document.getElementById('btnViewAdvanced');
    
    if (mode === 'advanced') {
        if (table) table.classList.add('table-view-advanced');
        if (btnStd) btnStd.classList.remove('active');
        if (btnAdv) btnAdv.classList.add('active');
        try { localStorage.setItem('fanta_auction_table_view', 'advanced'); } catch(e){}
    } else {
        if (table) table.classList.remove('table-view-advanced');
        if (btnStd) btnStd.classList.add('active');
        if (btnAdv) btnAdv.classList.remove('active');
        try { localStorage.setItem('fanta_auction_table_view', 'standard'); } catch(e){}
    }
}

function initAuctionTableView() {
    try {
        const saved = localStorage.getItem('fanta_auction_table_view');
        if (saved === 'advanced') {
            setAuctionTableView('advanced');
        } else {
            setAuctionTableView('standard');
        }
    } catch(e){}
}

window.setAuctionTableView = setAuctionTableView;
window.initAuctionTableView = initAuctionTableView;

function getAllSmartBadgesHtml(p) {
    const badges = [];

    // 1. Infortunio (se presente)
    if (p.is_injured) {
        badges.push(`<span class="smart-tag injured" title="Infortunato: ${p.infortunio_motivo || ''}">🩹 ${p.infortunio_rientro || 'Infortunato'}</span>`);
    }

    // 2. Rigorista
    if (p.is_rigorista_1 || p.rigorista_val === '1° Rigorista') {
        badges.push(`<span class="smart-tag penalty" title="1° Rigorista ufficiale">👑 1° Rigorista</span>`);
    } else if (p.is_rigorista_2 || p.rigorista_val === '2° Rigorista') {
        badges.push(`<span class="smart-tag penalty-sub" title="2° Rigorista">🎯 2° Rigorista</span>`);
    }

    // 3. Calci Piazzati (Punizioni o Corner)
    if (p.is_punizioni && p.is_corner) {
        badges.push(`<span class="smart-tag setpiece" title="Specialista Calci Piazzati (Corner & Punizioni)">📐 Corner & Puniz.</span>`);
    } else if (p.is_punizioni) {
        badges.push(`<span class="smart-tag setpiece" title="Specialista Punizioni">📐 Punizioni</span>`);
    } else if (p.is_corner) {
        badges.push(`<span class="smart-tag setpiece" title="Specialista Corner">📐 Corner</span>`);
    }

    // 4. OOP Mantra
    const oopValStr = typeof p.oop_val === 'string' ? p.oop_val : (p.oop_val ? String(p.oop_val) : '');
    if (oopValStr && oopValStr !== '-') {
        const isGold = p.oop_tier === 'ORO' || oopValStr.includes('ORO');
        const isSilver = p.oop_tier === 'ARGENTO' || oopValStr.includes('ARGENTO');
        const tagType = isGold ? 'oop-gold' : (isSilver ? 'oop-silver' : 'oop-bronze');
        const tierName = isGold ? 'Oro' : (isSilver ? 'Arg' : 'Bro');
        badges.push(`<span class="smart-tag ${tagType}" title="${p.oop_desc || oopValStr}">💎 OOP ${tierName}</span>`);
    }

    // 5. Profilo Strategico AI & Advice Tag
    const adviceType = p.ai_advice_type || 'regular';
    const adviceText = p.ai_advice || p.consiglio || '';
    
    if (p.ovr >= 92 || p.slot_num === 1 || adviceType === 'top' || adviceText.toLowerCase().includes('top player') || adviceText.toLowerCase().includes('top di reparto')) {
        badges.push(`<span class="smart-tag top" title="${adviceText || 'Top Player Assoluto'}">👑 Top Player</span>`);
    } else if (adviceType === 'leader' || adviceText.toLowerCase().includes('leader')) {
        badges.push(`<span class="smart-tag leader" title="${adviceText}">⭐ Leader</span>`);
    } else if (adviceType === 'sleeper' || adviceText.toLowerCase().includes('sleeper')) {
        badges.push(`<span class="smart-tag sleeper" title="${adviceText}">🔥 Sleeper</span>`);
    } else if (adviceType === 'buy' || adviceText.toLowerCase().includes('best value')) {
        badges.push(`<span class="smart-tag value" title="${adviceText}">🚀 Best Value</span>`);
    } else if (adviceType === 'supersub' || adviceText.includes('SUPER-SUB')) {
        badges.push(`<span class="smart-tag sleeper" style="background:rgba(245,158,11,0.2);border-color:#f59e0b;color:#fbbf24;" title="${adviceText}">⚡ Super-Sub</span>`);
    } else if (adviceType === 'titolarissimo' || adviceText.toLowerCase().includes('titolarissimo')) {
        badges.push(`<span class="smart-tag starter" title="${adviceText}">🔒 Titolarissimo</span>`);
    } else if (adviceType === 'lowcost' || adviceText.toLowerCase().includes('low cost')) {
        badges.push(`<span class="smart-tag lowcost" title="${adviceText}">🪙 Low Cost</span>`);
    } else if (adviceType === 'rotation' || adviceText.toLowerCase().includes('ballottaggio')) {
        badges.push(`<span class="smart-tag rotation" title="${adviceText}">🔄 Ballottaggio</span>`);
    } else if (adviceType === 'flop' || (adviceType === 'danger' && adviceText.toLowerCase().includes('flop'))) {
        badges.push(`<span class="smart-tag danger" title="${adviceText}">⚠️ Possibile Flop</span>`);
    } else if (adviceText.includes('TOP DI VETRO') || adviceText.includes('COPERTURA')) {
        badges.push(`<span class="smart-tag value" style="background:rgba(245,158,11,0.18);border-color:#f59e0b;color:#fbbf24;" title="${adviceText}">🛡️ Con Copertura</span>`);
    } else if (adviceText) {
        badges.push(`<span class="smart-tag regular">${adviceText}</span>`);
    }

    if (badges.length === 0) {
        badges.push(`<span class="smart-tag regular">${p.slot_fascia || (p.slot_num ? p.slot_num + '° Slot' : '-')}</span>`);
    }

    return `<div class="smart-tags-multi-container" style="display:flex;flex-wrap:wrap;gap:4px;align-items:center;">${badges.join('')}</div>`;
}

function getSmartBadgeHtml(p) {
    if (p.is_injured) {
        return `<span class="smart-tag injured" title="Infortunato: ${p.infortunio_motivo || ''}">🩹 ${p.infortunio_rientro || 'Infortunato'}</span>`;
    }
    if (p.is_rigorista_1 || p.rigorista_val === '1° Rigorista') {
        return `<span class="smart-tag penalty" title="1° Rigorista ufficiale">👑 1° Rigorista</span>`;
    }
    const oopValStr = typeof p.oop_val === 'string' ? p.oop_val : (p.oop_val ? String(p.oop_val) : '');
    if (oopValStr && oopValStr !== '-') {
        const isGold = p.oop_tier === 'ORO' || oopValStr.includes('ORO');
        const isSilver = p.oop_tier === 'ARGENTO' || oopValStr.includes('ARGENTO');
        const tagType = isGold ? 'oop-gold' : (isSilver ? 'oop-silver' : 'oop-bronze');
        const tierName = isGold ? 'Oro' : (isSilver ? 'Arg' : 'Bro');
        return `<span class="smart-tag ${tagType}" title="${p.oop_desc || oopValStr}">💎 OOP ${tierName}</span>`;
    }
    const adviceType = p.ai_advice_type || 'regular';
    const adviceText = p.ai_advice || p.consiglio || '';
    
    if (p.ovr >= 92 || p.slot_num === 1 || adviceType === 'top' || adviceText.toLowerCase().includes('top player') || adviceText.toLowerCase().includes('top di reparto')) {
        return `<span class="smart-tag top" title="${adviceText || 'Top Player Assoluto'}">👑 Top Player</span>`;
    }
    if (adviceType === 'leader' || adviceText.toLowerCase().includes('leader')) {
        return `<span class="smart-tag leader" title="${adviceText}">⭐ Leader</span>`;
    }
    if (adviceType === 'sleeper' || adviceText.toLowerCase().includes('sleeper')) {
        return `<span class="smart-tag sleeper" title="${adviceText}">🔥 Sleeper</span>`;
    }
    if (adviceType === 'buy' || adviceText.toLowerCase().includes('best value')) {
        return `<span class="smart-tag value" title="${adviceText}">🚀 Best Value</span>`;
    }
    if (adviceType === 'supersub' || adviceText.includes('SUPER-SUB')) {
        return `<span class="smart-tag sleeper" style="background:rgba(245,158,11,0.2);border-color:#f59e0b;color:#fbbf24;" title="${adviceText}">⚡ Super-Sub</span>`;
    }
    if (adviceType === 'titolarissimo' || adviceText.toLowerCase().includes('titolarissimo')) {
        return `<span class="smart-tag starter" title="${adviceText}">🔒 Titolarissimo</span>`;
    }
    if (adviceType === 'lowcost' || adviceText.toLowerCase().includes('low cost')) {
        return `<span class="smart-tag lowcost" title="${adviceText}">🪙 Low Cost</span>`;
    }
    if (adviceType === 'rotation' || adviceText.toLowerCase().includes('ballottaggio')) {
        return `<span class="smart-tag rotation" title="${adviceText}">🔄 Ballottaggio</span>`;
    }
    if (adviceType === 'flop' || (adviceType === 'danger' && adviceText.toLowerCase().includes('flop'))) {
        return `<span class="smart-tag danger" title="${adviceText}">⚠️ Possibile Flop</span>`;
    }
    if (adviceText.includes('TOP DI VETRO') || adviceText.includes('COPERTURA')) {
        return `<span class="smart-tag value" style="background:rgba(245,158,11,0.18);border-color:#f59e0b;color:#fbbf24;" title="${adviceText}">🛡️ Con Copertura</span>`;
    }
    if (p.is_rigorista_2 || p.rigorista_val === '2° Rigorista') {
        return `<span class="smart-tag penalty-sub" title="2° Rigorista">🎯 2° Rigorista</span>`;
    }
    if (p.is_punizioni || p.is_corner) {
        return `<span class="smart-tag setpiece" title="Specialista Calci Piazzati">📐 Piazzati</span>`;
    }
    if (adviceText) {
        return `<span class="smart-tag regular">${adviceText}</span>`;
    }
    return `<span class="smart-tag regular">${p.slot_fascia || (p.slot_num ? p.slot_num + '° Slot' : '-')}</span>`;
}

function setRoleFilterQuick(role) {
    State.filterRole = role;
    document.querySelectorAll('.role-chip').forEach(btn => {
        if (btn.getAttribute('data-role') === role) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    const fr = document.getElementById('filterRole');
    if (fr) fr.value = role;
    if (typeof updateMantraQuickBarActiveState === 'function') {
        updateMantraQuickBarActiveState();
    }
    renderTable();
}

function toggleFavFilterQuick() {
    State.filterOnlyFavorites = !State.filterOnlyFavorites;
    const btn = document.getElementById('btnToggleFav');
    if (btn) btn.classList.toggle('active', State.filterOnlyFavorites);
    const chk = document.getElementById('chkOnlyFavorites');
    if (chk) chk.checked = State.filterOnlyFavorites;
    renderTable();
}

function toggleAvailFilterQuick() {
    State.filterOnlyAvailable = !State.filterOnlyAvailable;
    const btn = document.getElementById('btnToggleAvail');
    if (btn) btn.classList.toggle('active', State.filterOnlyAvailable);
    const chk = document.getElementById('chkOnlyAvailable');
    if (chk) chk.checked = State.filterOnlyAvailable;
    renderTable();
}

function toggleOopFilterQuick() {
    State.filterOop = !State.filterOop;
    const btn = document.getElementById('btnToggleOop');
    if (btn) btn.classList.toggle('active', State.filterOop);
    const chk = document.getElementById('chkOop');
    if (chk) chk.checked = State.filterOop;
    renderTable();
}

function toggleAdvancedFiltersDrawer() {
    const drawer = document.getElementById('advancedFiltersDrawer');
    const btn = document.getElementById('btnAdvancedFilters');
    if (!drawer) return;
    const isHidden = drawer.style.display === 'none' || !drawer.style.display;
    drawer.style.display = isHidden ? 'block' : 'none';
    if (btn) btn.classList.toggle('active', isHidden);
}

function toggleSidebarRoster() {
    const sidebar = document.getElementById('rosterSidebar');
    const btn = document.getElementById('btnToggleSidebar');
    if (!sidebar) return;
    sidebar.classList.toggle('collapsed');
    if (btn) btn.classList.toggle('active', sidebar.classList.contains('collapsed'));
}

function setFragilitaFilter(val) {
    State.filterFragilita = val;
    renderTable();
}

let currentBuyingPlayerId = null;

function buyPlayer(playerId, directPrice = undefined) {
    if (typeof showComingSoonModal === 'function') {
        showComingSoonModal('Creazione Squadra & Asta Live');
        return;
    }
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;

    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const isGK = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR')));

    if (isMantraMode) {
        const allBoughtCount = State.slots.P.players.length + State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length;
        const maxSlots = 31;
        if (allBoughtCount >= maxSlots) {
            alert(`Hai già raggiunto il limite massimo di ${maxSlots} calciatori in rosa per il Mantra!`);
            return;
        }
    } else {
        const slot = State.slots[p.role];
        if (slot && slot.players.length >= slot.max) {
            alert(`Hai già raggiunto il limite di ${slot.max} calciatori per il ruolo ${p.role}!`);
            return;
        }
    }

    if (directPrice !== undefined && directPrice !== null) {
        executePurchase(p, directPrice);
        return;
    }

    openBuyPlayerModal(p);
}

function openBuyPlayerModal(p) {
    currentBuyingPlayerId = p.id;
    const modal = document.getElementById('buyPlayerModal');
    const body = document.getElementById('buyPlayerModalBody');
    if (!modal || !body) {
        const paidStr = prompt(`Inserisci il prezzo di acquisto per ${p.name} (Consigliato: ${p.prezzo_cons} CR):`, p.prezzo_cons);
        if (paidStr === null) return;
        const paidPrice = parseInt(paidStr, 10);
        if (!isNaN(paidPrice) && paidPrice >= 1) {
            executePurchase(p, paidPrice);
        }
        return;
    }

    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const remaining = State.budgetTotal - State.budgetSpent;
    let totalSlotsRemaining;
    if (isMantraMode) {
        const allBoughtCount = State.slots.P.players.length + State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length;
        const maxSlots = 31;
        totalSlotsRemaining = Math.max(0, maxSlots - allBoughtCount - 1);
    } else {
        totalSlotsRemaining = Math.max(0, (3 - State.slots.P.players.length) + 
                               (8 - State.slots.D.players.length) + 
                               (8 - State.slots.C.players.length) + 
                               (6 - State.slots.A.players.length) - 1);
    }
    const maxAllowed = totalSlotsRemaining > 0 ? Math.max(1, remaining - totalSlotsRemaining) : remaining;
    const defaultPrice = Math.min(p.prezzo_cons || 1, maxAllowed);

    body.innerHTML = `
        <div style="background:rgba(255,255,255,0.04);border:1px solid var(--border-glass);padding:12px;border-radius:10px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="role-badge ${p.role}" style="font-size:11px;padding:2px 6px;">${p.role}</span>
                    <b style="color:#fff;font-size:16px;">${p.name}</b>
                    <span style="font-size:12px;color:var(--text-muted);">${p.team}</span>
                    ${p.mantra ? `<span style="font-size:11px;color:var(--accent-cyan);font-weight:700;">[${p.mantra}]</span>` : ''}
                </div>
                <span class="ovr-pill ${p.ovr >= 90 ? 'top-tier' : ''}" style="font-size:12px;">OVR ${p.ovr}</span>
            </div>
            <div style="display:flex;gap:12px;margin-top:8px;font-size:11.5px;color:var(--text-secondary);">
                <span>Slot: <b style="color:#fff;">${p.slot_fascia || 'Slot'}</b></span>
                <span>Consiglio: <b style="color:var(--accent-cyan);">${p.ai_advice || '-'}</b></span>
            </div>
        </div>

        <div style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;font-size:12px;">
                <span style="color:var(--text-secondary);">Prezzo d'Asta Pagato (CR):</span>
                <span style="color:var(--accent-gold);font-weight:700;">Max consentito: ${maxAllowed} CR</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <input type="number" id="buyModalPriceInput" min="1" max="${maxAllowed}" value="${defaultPrice}" 
                    style="flex:1;background:rgba(0,0,0,0.5);border:2px solid var(--accent-cyan);color:#fbbf24;font-size:22px;font-weight:900;padding:8px 14px;border-radius:8px;text-align:center;"
                    onkeydown="if(event.key==='Enter') submitBuyFromModal(${p.id})">
            </div>
            <div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;justify-content:center;">
                <button type="button" class="btn-action" style="padding:4px 8px;font-size:11px;" onclick="adjustBuyPrice(-5, ${maxAllowed})">-5</button>
                <button type="button" class="btn-action" style="padding:4px 8px;font-size:11px;" onclick="adjustBuyPrice(-1, ${maxAllowed})">-1</button>
                <button type="button" class="btn-action" style="padding:4px 8px;font-size:11px;background:rgba(251,191,36,0.15);border-color:#fbbf24;color:#fbbf24;" onclick="setBuyPrice(${p.prezzo_cons || 1}, ${maxAllowed})">Consigliato (${p.prezzo_cons || 1})</button>
                <button type="button" class="btn-action" style="padding:4px 8px;font-size:11px;" onclick="adjustBuyPrice(1, ${maxAllowed})">+1</button>
                <button type="button" class="btn-action" style="padding:4px 8px;font-size:11px;" onclick="adjustBuyPrice(5, ${maxAllowed})">+5</button>
                <button type="button" class="btn-action" style="padding:4px 8px;font-size:11px;" onclick="adjustBuyPrice(10, ${maxAllowed})">+10</button>
            </div>
        </div>

        <div style="display:flex;gap:10px;justify-content:flex-end;">
            <button class="btn-action" style="padding:8px 16px;font-size:12px;" onclick="closeBuyPlayerModal()">Annulla</button>
            <button class="btn-action" style="background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#000;font-weight:900;padding:8px 20px;font-size:13px;border:none;" onclick="submitBuyFromModal(${p.id})">✓ Conferma Acquisto</button>
        </div>
    `;

    modal.style.display = 'flex';
    modal.classList.add('active');
    setTimeout(() => {
        const inp = document.getElementById('buyModalPriceInput');
        if (inp) { inp.focus(); inp.select(); }
    }, 50);
}

function adjustBuyPrice(delta, maxAllowed) {
    const inp = document.getElementById('buyModalPriceInput');
    if (!inp) return;
    let val = (parseInt(inp.value, 10) || 1) + delta;
    val = Math.max(1, Math.min(val, maxAllowed));
    inp.value = val;
}

function setBuyPrice(val, maxAllowed) {
    const inp = document.getElementById('buyModalPriceInput');
    if (!inp) return;
    inp.value = Math.max(1, Math.min(val, maxAllowed));
}

function closeBuyPlayerModal() {
    const modal = document.getElementById('buyPlayerModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
    currentBuyingPlayerId = null;
}

function submitBuyFromModal(playerId) {
    const inp = document.getElementById('buyModalPriceInput');
    if (!inp) return;
    const paidPrice = parseInt(inp.value, 10);
    if (isNaN(paidPrice) || paidPrice < 1) {
        alert('Prezzo inserito non valido!');
        return;
    }
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;
    closeBuyPlayerModal();
    executePurchase(p, paidPrice);
}

function executePurchase(p, paidPrice) {
    const isMantraMode = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const isGK = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR')));

    let totalSlotsRemaining;
    if (isMantraMode) {
        const allBoughtCount = State.slots.P.players.length + State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length;
        const maxSlots = 31;
        if (allBoughtCount >= maxSlots) {
            alert(`Hai già raggiunto il limite massimo di ${maxSlots} calciatori in rosa per il Mantra!`);
            return;
        }
        totalSlotsRemaining = Math.max(0, maxSlots - allBoughtCount - 1);
    } else {
        const slot = State.slots[p.role];
        if (slot && slot.players.length >= slot.max) {
            alert(`Hai già raggiunto il limite di ${slot.max} calciatori per il ruolo ${p.role}!`);
            return;
        }
        totalSlotsRemaining = Math.max(0, (3 - State.slots.P.players.length) + 
                               (8 - State.slots.D.players.length) + 
                               (8 - State.slots.C.players.length) + 
                               (6 - State.slots.A.players.length) - 1);
    }

    if (totalSlotsRemaining > 0 && (State.budgetTotal - (State.budgetSpent + paidPrice) < totalSlotsRemaining)) {
        alert(`Attenzione: Non puoi spendere ${paidPrice} CR perché non ti rimarrebbero abbastanza crediti (min 1 CR/slot) per completare gli altri ${totalSlotsRemaining} slot!`);
        return;
    }

    State.budgetSpent += paidPrice;
    const targetSlotKey = isGK ? 'P' : (State.slots[p.role] ? p.role : 'C');
    State.slots[targetSlotKey].players.push({ ...p, paidPrice });

    saveStateToStorage();
    updateBudgetUI();
    renderTable();
    renderSidebarRoster();
    if (typeof renderSquadBuilder === 'function') {
        renderSquadBuilder();
    }
}

function removePlayerFromRoster(role, idx) {
    const removed = State.slots[role].players.splice(idx, 1)[0];
    if (removed) {
        State.budgetSpent -= removed.paidPrice;
        saveStateToStorage();
        updateBudgetUI();
        renderTable();
        renderSidebarRoster();
        if (typeof renderSquadBuilder === 'function') {
            renderSquadBuilder();
        }
        const modal = document.getElementById('rosterModal');
        if (modal && modal.classList.contains('active')) {
            openRosterModal();
        }
    }
}

function resetLiveAuction() {
    renderResetAuctionModal();
    const modal = document.getElementById('resetAuctionModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
    } else {
        const choice = prompt("Opzioni Reset Asta:\n1 = Ripristina Calciatori Scelti da Altri\n2 = Azzera Solo la Mia Rosa\n3 = Azzera Tutto Completo\n\nDigita 1, 2 o 3:", "1");
        if (choice === "1") confirmResetRivalsTaken();
        else if (choice === "2") confirmResetMyRoster();
        else if (choice === "3") confirmResetAllAuction();
    }
}

function closeResetAuctionModal() {
    const modal = document.getElementById('resetAuctionModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function renderResetAuctionModal() {
    const container = document.getElementById('resetAuctionModalContent');
    if (!container) return;

    const myP = State.slots?.P?.players?.length || 0;
    const myD = State.slots?.D?.players?.length || 0;
    const myC = State.slots?.C?.players?.length || 0;
    const myA = State.slots?.A?.players?.length || 0;
    const myCount = myP + myD + myC + myA;
    const mySpent = State.budgetSpent || 0;
    const myRem = (State.budgetTotal || 1000) - mySpent;

    const rivalCount = Array.isArray(State.takenByOthers) ? State.takenByOthers.length : 0;
    let rivalSpent = 0;
    let activeRivalsCount = 0;
    if (State.rivals) {
        Object.values(State.rivals).forEach(r => {
            const count = r.players ? r.players.length : 0;
            if (count > 0) activeRivalsCount++;
            rivalSpent += (r.spent || 0);
        });
    }

    container.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,rgba(56,189,248,0.2),rgba(239,68,68,0.2));display:flex;align-items:center;justify-content:center;font-size:20px;border:1px solid rgba(56,189,248,0.3);">
                    🔄
                </div>
                <div>
                    <h3 style="margin:0;font-size:17.5px;font-weight:900;color:#fff;letter-spacing:-0.3px;">Gestione Reset Asta</h3>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">Scegli se ripristinare i calciatori scelti da altri, la tua rosa o azzerare tutto</div>
                </div>
            </div>
            <button onclick="closeResetAuctionModal()" style="background:none;border:none;color:var(--text-secondary);font-size:20px;cursor:pointer;padding:4px 8px;border-radius:6px;transition:0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-secondary)'">✕</button>
        </div>

        <!-- Live Status Badges -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(0,242,254,0.25);padding:10px 12px;border-radius:10px;">
                <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:var(--neon-cyan);font-weight:800;text-transform:uppercase;">
                    <span>👤</span> LA TUA ROSA
                </div>
                <div style="font-size:14px;font-weight:800;color:#fff;margin-top:4px;">
                    ${myCount} <span style="font-size:11px;font-weight:500;color:var(--text-secondary);">calciatori acquistati</span>
                </div>
                <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">
                    Spesi: <b style="color:#ef4444;">${mySpent} CR</b> | Rimasti: <b style="color:#10b981;">${myRem} CR</b>
                </div>
            </div>

            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(56,189,248,0.25);padding:10px 12px;border-radius:10px;">
                <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#38bdf8;font-weight:800;text-transform:uppercase;">
                    <span>👥</span> SCELTI DA ALTRI (7 RIVALI)
                </div>
                <div style="font-size:14px;font-weight:800;color:#fff;margin-top:4px;">
                    ${rivalCount} <span style="font-size:11px;font-weight:500;color:var(--text-secondary);">calciatori assegnati</span>
                </div>
                <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">
                    Squadre coinvolte: <b>${activeRivalsCount} / 7</b> | Spesa: <b>${rivalSpent} CR</b>
                </div>
            </div>
        </div>

        <!-- Reset Options Cards -->
        <div style="display:flex;flex-direction:column;gap:11px;">

            <!-- Opzione 1: Ripristina Calciatori Altri -->
            <div class="reset-option-card" style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:12px;background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.3);transition:all 0.2s ease;">
                <div style="flex:1;padding-right:12px;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:16px;">👥</span>
                        <b style="color:#38bdf8;font-size:13px;">Ripristina Calciatori Scelti da Altri</b>
                        <span style="font-size:10px;background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.35);padding:1px 6px;border-radius:10px;font-weight:700;">7 Rivali</span>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:3px;line-height:1.35;">
                        Svincola tutti i <b>${rivalCount}</b> calciatori assegnati alle altre squadre e ripristina i loro crediti. <span style="color:#10b981;font-weight:700;">La tua rosa (${myCount} giocatori) resta intatta!</span>
                    </div>
                </div>
                <button type="button" class="btn-action" style="background:rgba(56,189,248,0.18);border-color:#38bdf8;color:#38bdf8;font-weight:800;font-size:12px;padding:9px 15px;white-space:nowrap;cursor:pointer;border-radius:8px;box-shadow:0 0 10px rgba(56,189,248,0.2);" onclick="confirmResetRivalsTaken()" ${rivalCount === 0 ? 'disabled style="opacity:0.4;cursor:not-allowed;"' : ''}>
                    ↩️ Ripristina Altri
                </button>
            </div>

            <!-- Opzione 2: Azzera solo la Mia Rosa -->
            <div class="reset-option-card" style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:12px;background:rgba(234,179,8,0.05);border:1px solid rgba(234,179,8,0.3);transition:all 0.2s ease;">
                <div style="flex:1;padding-right:12px;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:16px;">👤</span>
                        <b style="color:#fbbf24;font-size:13px;">Azzera Solo la Mia Rosa</b>
                        <span style="font-size:10px;background:rgba(251,191,36,0.15);color:#fbbf24;border:1px solid rgba(251,191,36,0.35);padding:1px 6px;border-radius:10px;font-weight:700;">Mia Rosa</span>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:3px;line-height:1.35;">
                        Cancella i tuoi <b>${myCount}</b> calciatori acquistati e riporta il tuo budget a 1000 CR. <span style="color:#38bdf8;font-weight:700;">I calciatori delle altre squadre rimangono intatti!</span>
                    </div>
                </div>
                <button type="button" class="btn-action" style="background:rgba(245,158,11,0.18);border-color:#f59e0b;color:#fbbf24;font-weight:800;font-size:12px;padding:9px 15px;white-space:nowrap;cursor:pointer;border-radius:8px;" onclick="confirmResetMyRoster()" ${myCount === 0 ? 'disabled style="opacity:0.4;cursor:not-allowed;"' : ''}>
                    🗑️ Azzera Mia Rosa
                </button>
            </div>

            <!-- Opzione 3: Azzera Tutto Completo -->
            <div class="reset-option-card" style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:12px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.35);transition:all 0.2s ease;">
                <div style="flex:1;padding-right:12px;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:16px;">⚠️</span>
                        <b style="color:#f87171;font-size:13px;">Azzera Tutto (Reset Totale Asta)</b>
                        <span style="font-size:10px;background:rgba(239,68,68,0.2);color:#f87171;border:1px solid rgba(239,68,68,0.4);padding:1px 6px;border-radius:10px;font-weight:700;">Totale</span>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:3px;line-height:1.35;">
                        Cancella sia i tuoi acquisti che tutti i calciatori assegnati alle altre 7 squadre. Ricomincia l'asta completamente da capo.
                    </div>
                </div>
                <button type="button" class="btn-action" style="background:rgba(239,68,68,0.22);border-color:#ef4444;color:#f87171;font-weight:800;font-size:12px;padding:9px 15px;white-space:nowrap;cursor:pointer;border-radius:8px;" onclick="confirmResetAllAuction()">
                    💥 Azzera Tutto
                </button>
            </div>

        </div>

        <div style="margin-top:16px;text-align:center;border-top:1px solid rgba(255,255,255,0.06);padding-top:12px;">
            <button type="button" class="btn-action" style="padding:7px 24px;font-size:12px;color:var(--text-secondary);background:rgba(255,255,255,0.05);border-color:rgba(255,255,255,0.1);border-radius:8px;" onclick="closeResetAuctionModal()">
                ✕ Annulla / Chiudi
            </button>
        </div>
    `;
}

function confirmResetRivalsTaken() {
    const rivalCount = Array.isArray(State.takenByOthers) ? State.takenByOthers.length : 0;
    if (rivalCount === 0) {
        if (typeof showSyncToast === 'function') {
            showSyncToast('ℹ️ Nessun calciatore è attualmente assegnato ad altre squadre.');
        } else {
            alert('Nessun calciatore è attualmente assegnato ad altre squadre.');
        }
        closeResetAuctionModal();
        return;
    }
    const myP = State.slots?.P?.players?.length || 0;
    const myD = State.slots?.D?.players?.length || 0;
    const myC = State.slots?.C?.players?.length || 0;
    const myA = State.slots?.A?.players?.length || 0;
    const myCount = myP + myD + myC + myA;

    if (!confirm(`Sei sicuro di voler svincolare e ripristinare tutti i ${rivalCount} calciatori scelti dalle altre squadre?\n\nLa tua rosa (${myCount} giocatori) e i tuoi crediti rimarranno intatti.`)) {
        return;
    }

    State.takenByOthers = [];
    State.rivalAssignments = {};
    State.rivals = JSON.parse(JSON.stringify(RIVALS_TEMPLATE));
    saveStateToStorage();
    updateAllViews();
    if (typeof renderSquadBuilder === 'function') {
        renderSquadBuilder();
    }
    closeResetAuctionModal();
    if (typeof showSyncToast === 'function') {
        showSyncToast(`👥 Ripristinati con successo tutti i calciatori delle altre squadre!`);
    }
}

function confirmResetMyRoster() {
    const myP = State.slots?.P?.players?.length || 0;
    const myD = State.slots?.D?.players?.length || 0;
    const myC = State.slots?.C?.players?.length || 0;
    const myA = State.slots?.A?.players?.length || 0;
    const myCount = myP + myD + myC + myA;

    if (myCount === 0 && (State.budgetSpent || 0) === 0) {
        if (typeof showSyncToast === 'function') {
            showSyncToast('ℹ️ La tua rosa è già vuota.');
        } else {
            alert('La tua rosa è già vuota.');
        }
        closeResetAuctionModal();
        return;
    }

    const rivalCount = Array.isArray(State.takenByOthers) ? State.takenByOthers.length : 0;
    if (!confirm(`Sei sicuro di voler cancellare la tua rosa (${myCount} giocatori acquistati) e ripristinare il tuo budget a 1000 CR?\n\nI calciatori assegnati alle altre squadre (${rivalCount} assegnati) rimarranno intatti.`)) {
        return;
    }

    State.budgetSpent = 0;
    State.slots.P.players = [];
    State.slots.D.players = [];
    State.slots.C.players = [];
    State.slots.A.players = [];
    saveStateToStorage();
    updateAllViews();
    if (typeof renderSquadBuilder === 'function') {
        renderSquadBuilder();
    }
    closeResetAuctionModal();
    if (typeof showSyncToast === 'function') {
        showSyncToast('👤 Rosa personale azzerata (1000 CR ripristinati). Giocatori dei rivali intatti.');
    }
}

function confirmResetAllAuction() {
    const myP = State.slots?.P?.players?.length || 0;
    const myD = State.slots?.D?.players?.length || 0;
    const myC = State.slots?.C?.players?.length || 0;
    const myA = State.slots?.A?.players?.length || 0;
    const myCount = myP + myD + myC + myA;
    const rivalCount = Array.isArray(State.takenByOthers) ? State.takenByOthers.length : 0;

    if (!confirm(`⚠️ ATTENZIONE: RESET TOTALE ASTA!\n\nStai per cancellare:\n- La tua rosa (${myCount} giocatori)\n- Tutti i calciatori scelti da altre squadre (${rivalCount} assegnati)\n- Ripristinare tutti i budget a 1000 CR\n\nVuoi davvero procedere con l'azzeramento completo?`)) {
        return;
    }

    State.budgetSpent = 0;
    State.slots.P.players = [];
    State.slots.D.players = [];
    State.slots.C.players = [];
    State.slots.A.players = [];
    State.takenByOthers = [];
    State.rivalAssignments = {};
    State.rivals = JSON.parse(JSON.stringify(RIVALS_TEMPLATE));
    saveStateToStorage();
    updateAllViews();
    if (typeof renderSquadBuilder === 'function') {
        renderSquadBuilder();
    }
    closeResetAuctionModal();
    if (typeof showSyncToast === 'function') {
        showSyncToast('🔄 Asta completamente azzerata (Tua Rosa e Calciatori Altri ripristinati a 1000 CR).');
    }
}

function confirmResetLiveAuction() {
    confirmResetMyRoster();
}

function openRosterModal(targetTeam = 'my_team') {
    if ((typeof isCreatorModeActive !== 'function' || !isCreatorModeActive()) && typeof showComingSoonModal === 'function') {
        showComingSoonModal('Gestione Rose & Campionati');
        return;
    }
    const modal = document.getElementById('rosterModal');
    const body = document.getElementById('rosterModalBody');
    if (!modal || !body) return;
    modal.classList.add('active');
    modal.style.display = 'flex';

    if (targetTeam === 'ALL_RIVALS') {
        targetTeam = 'ALL';
    } else if (targetTeam === 'RIVALS') {
        targetTeam = Object.keys(State.rivals || RIVALS_TEMPLATE)[0] || 'ALL';
    }

    const unikaSpent = State.budgetSpent || 0;
    const unikaRem = (State.budgetTotal || 1000) - unikaSpent;
    const rivalsList = Object.keys(State.rivals || RIVALS_TEMPLATE);
    const isMyTeamTab = (targetTeam === 'my_team' || targetTeam === 'Unika' || targetTeam === (State.teamName || 'La Mia Rosa'));

    // 1. Switcher bar per le 8 squadre della lega + vista comparativa ALL
    let tabsHtml = `
        <div class="roster-team-switcher">
            <button type="button" class="roster-team-tab ${isMyTeamTab ? 'active' : ''}" onclick="openRosterModal('my_team')">
                🌟 ${escapeHtml(State.teamName || 'La Mia Rosa')} <span class="tab-budget-badge">${unikaRem} CR</span>
            </button>
    `;

    rivalsList.forEach(rName => {
        const rData = State.rivals[rName] || { spent: 0, budget: 1000, players: [] };
        const rSpent = rData.spent || 0;
        const rRem = (rData.budget || 1000) - rSpent;
        const pCount = rData.players ? rData.players.length : 0;
        const shortName = rName.split(' ')[0];
        tabsHtml += `
            <button type="button" class="roster-team-tab ${targetTeam === rName ? 'active' : ''}" onclick="openRosterModal('${rName}')">
                🛡️ ${shortName} <span class="tab-budget-badge">${rRem} CR</span> <span style="font-size:10px;color:var(--text-muted);">(${pCount})</span>
            </button>
        `;
    });

    tabsHtml += `
            <button type="button" class="roster-team-tab ${targetTeam === 'ALL' ? 'active' : ''}" onclick="openRosterModal('ALL')">
                📊 Tutte le 8 Rose (Griglia)
            </button>
        </div>
    `;

    // 2. Contenuto in base al target selezionato
    let contentHtml = '';

    if (targetTeam === 'ALL') {
        // VISTA COMPARATIVA DELLE 8 SQUADRE
        const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
        const maxSlotsAll = isMantra ? 31 : 25;
        let teamCardsHtml = '';

        // Unika Card
        const unikaTotalPlayers = (State.slots.P.players.length + State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length);
        const unikaMovPlayers = (State.slots.D.players.length + State.slots.C.players.length + State.slots.A.players.length);
        teamCardsHtml += `
            <div class="all-teams-card" style="border-color:rgba(0,242,254,0.4);background:rgba(0,242,254,0.04);" onclick="openRosterModal('my_team')">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div>
                        <div style="font-size:11px;color:var(--accent-cyan);font-weight:800;letter-spacing:0.5px;">LA TUA SQUADRA</div>
                        <h4 style="margin:2px 0 0 0;font-size:15px;color:#fff;font-weight:900;">🌟 ${escapeHtml(State.teamName || 'La Mia Rosa')}</h4>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:16px;font-weight:900;color:var(--accent-gold);">${unikaRem} CR</span>
                        <div style="font-size:10.5px;color:var(--text-muted);">${unikaTotalPlayers}/${maxSlotsAll} slot</div>
                    </div>
                </div>
                <div style="display:flex;gap:6px;font-size:11px;margin-bottom:8px;padding:4px 8px;background:rgba(0,0,0,0.3);border-radius:6px;">
                    ${isMantra ? `
                        <span style="color:var(--mantra-por);">🧤 Por ${State.slots.P.players.length}</span>
                        <span style="color:var(--accent-cyan);">🏃‍♂️ Mov ${unikaMovPlayers}</span>
                    ` : `
                        <span style="color:var(--role-p);">🧤 ${State.slots.P.players.length}/3</span>
                        <span style="color:var(--role-d);">🛡️ ${State.slots.D.players.length}/8</span>
                        <span style="color:var(--role-c);">🪄 ${State.slots.C.players.length}/8</span>
                        <span style="color:var(--role-a);">⚡ ${State.slots.A.players.length}/6</span>
                    `}
                </div>
                <div style="font-size:11px;color:var(--text-secondary);max-height:110px;overflow-y:auto;padding-right:2px;">
                    ${unikaTotalPlayers === 0 ? 'Nessun acquisto ancora effettuato.' : 
                        ['P','D','C','A'].flatMap(r => State.slots[r].players).map(p => `<div>• <b>${p.name}</b> (${p.team}) <span style="color:#fbbf24;">${p.paidPrice} CR</span></div>`).join('')
                    }
                </div>
                <div style="margin-top:auto;padding-top:8px;font-size:11px;color:var(--accent-cyan);text-align:right;font-weight:700;">Dettagli Rosa ➜</div>
            </div>
        `;

        // 7 Rivali Cards
        rivalsList.forEach(rName => {
            const rData = State.rivals[rName] || { spent: 0, budget: 1000, players: [], manager: '', tendency: '' };
            const rSpent = rData.spent || 0;
            const rRem = (rData.budget || 1000) - rSpent;
            const pCount = { P: 0, D: 0, C: 0, A: 0 };
            rData.players.forEach(pl => {
                const full = PLAYERS.find(p => p.id === pl.id);
                if (full && pCount[full.role] !== undefined) pCount[full.role]++;
            });
            const rTotal = rData.players.length;
            const rMovTotal = pCount.D + pCount.C + pCount.A;

            teamCardsHtml += `
                <div class="all-teams-card" onclick="openRosterModal('${rName}')">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                        <div>
                            <div style="font-size:10.5px;color:var(--text-muted);font-weight:700;">MANAGER: ${rData.manager}</div>
                            <h4 style="margin:2px 0 0 0;font-size:14.5px;color:#fff;font-weight:900;">🛡️ ${rName}</h4>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:16px;font-weight:900;color:var(--accent-gold);">${rRem} CR</span>
                            <div style="font-size:10.5px;color:var(--text-muted);">${rTotal}/${maxSlotsAll} slot</div>
                        </div>
                    </div>
                    <div style="display:flex;gap:6px;font-size:11px;margin-bottom:8px;padding:4px 8px;background:rgba(0,0,0,0.3);border-radius:6px;">
                        ${isMantra ? `
                            <span style="color:var(--mantra-por);">🧤 Por ${pCount.P}/3</span>
                            <span style="color:var(--accent-cyan);">🏃‍♂️ Mov ${rMovTotal}/28</span>
                        ` : `
                            <span style="color:var(--role-p);">🧤 ${pCount.P}/3</span>
                            <span style="color:var(--role-d);">🛡️ ${pCount.D}/8</span>
                            <span style="color:var(--role-c);">🪄 ${pCount.C}/8</span>
                            <span style="color:var(--role-a);">⚡ ${pCount.A}/6</span>
                        `}
                    </div>
                    <div style="font-size:11px;color:var(--text-secondary);max-height:110px;overflow-y:auto;padding-right:2px;">
                        ${rTotal === 0 ? 'Nessun calciatore assegnato finora.' : 
                            rData.players.map(pl => {
                                const full = PLAYERS.find(p => p.id === pl.id);
                                return `<div>• <b>${full ? full.name : 'Giocatore'}</b> (${full ? full.team : '-'}) <span style="color:#fbbf24;">${pl.price} CR</span></div>`;
                            }).join('')
                        }
                    </div>
                    <div style="margin-top:auto;padding-top:8px;font-size:11px;color:var(--accent-cyan);text-align:right;font-weight:700;">Apri Rosa Completa ➜</div>
                </div>
            `;
        });

        contentHtml = `
            <div style="margin-bottom:14px;">
                <h4 style="margin:0 0 4px 0;font-size:16px;color:#fff;font-weight:900;">📊 Tabellone Generale delle 8 Squadre della Lega</h4>
                <p style="margin:0;font-size:12px;color:var(--text-secondary);">Clicca su una squadra qualsiasi per vederne la rosa reparto per reparto o svincolare calciatori.</p>
            </div>
            <div class="all-teams-grid">
                ${teamCardsHtml}
            </div>
        `;
    } else if (targetTeam === 'my_team' || targetTeam === 'Unika') {
        // VISTA ROSA PERSONALE CON MODELLO DINAMICO SLOT
        const analysis = getSlotBudgetAnalysis();
        const totalPurchased = analysis.totalBought;
        const maxBid = analysis.maxSingleBid;

        const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
        const maxRosterSlots = isMantra ? 31 : 25;
        let rolesHtml = '';

        if (isMantra) {
            const porList = State.slots.P.players || [];
            const movList = [...(State.slots.D.players || []), ...(State.slots.C.players || []), ...(State.slots.A.players || [])];

            const sortedMov = [...movList].sort((a, b) => {
                const scoreA = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(a.mantra) : 50;
                const scoreB = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(b.mantra) : 50;
                if (scoreA !== scoreB) return scoreA - scoreB;
                if ((b.paidPrice || 0) !== (a.paidPrice || 0)) return (b.paidPrice || 0) - (a.paidPrice || 0);
                return (b.ovr || 0) - (a.ovr || 0);
            });

            // 1. Box Portieri Mantra (3 max)
            let porRowsHtml = '';
            for (let i = 0; i < 3; i++) {
                const p = porList[i];
                if (p) {
                    porRowsHtml += `
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span class="role-badge P" style="font-size:10px;padding:2px 5px;background:var(--mantra-por);color:#fff;">${i + 1}° Por</span>
                                <b style="color:#fff;font-size:13px;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                <span style="font-size:11px;color:var(--text-muted);">${p.team}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span style="color:var(--accent-gold);font-weight:900;font-size:13px;">${p.paidPrice} CR</span>
                                <button class="btn-action" style="padding:2px 7px;font-size:10.5px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" onclick="removePlayerById(${p.id}); openRosterModal('my_team');">✕ Svincola</button>
                            </div>
                        </div>
                    `;
                } else {
                    porRowsHtml += `
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 10px;border-radius:6px;margin:4px 0;background:rgba(255,255,255,0.015);border:1px dashed rgba(255,255,255,0.08);">
                            <div style="font-size:11.5px;color:rgba(255,255,255,0.42);display:flex;align-items:center;gap:6px;">
                                <span style="opacity:0.4;">+</span> <span>Slot Portiere ${i + 1} Libero</span>
                            </div>
                            <div class="slot-target-tag normal" style="font-size:11px;">min 1 CR</div>
                        </div>
                    `;
                }
            }

            rolesHtml += `
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);padding:12px 16px;border-radius:10px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:6px;">
                        <h4 style="color:var(--mantra-por);font-size:13.5px;margin:0;font-weight:800;">🧤 Portieri (Por) - Max 3</h4>
                        <span style="font-size:11.5px;font-weight:800;color:${porList.length >= 3 ? '#4ade80' : 'var(--text-muted)'};">${porList.length}/3 acquistati</span>
                    </div>
                    ${porRowsHtml}
                </div>
            `;

            // 2. Box Movimento Mantra (28 max) ordinati per ruolo Mantra
            let movRowsHtml = '';
            sortedMov.forEach((p, idx) => {
                const badges = (typeof renderMantraRoleBadges === 'function') ? renderMantraRoleBadges(p.mantra) : `<span class="role-badge ${p.role}">${p.role}</span>`;
                movRowsHtml += `
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                        <div style="display:flex;align-items:center;gap:8px;">
                            ${badges}
                            <b style="color:#fff;font-size:13px;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                            <span style="font-size:11px;color:var(--text-muted);">${p.team}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="color:var(--accent-gold);font-weight:900;font-size:13px;">${p.paidPrice} CR</span>
                            <button class="btn-action" style="padding:2px 7px;font-size:10.5px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" onclick="removePlayerById(${p.id}); openRosterModal('my_team');">✕ Svincola</button>
                        </div>
                    </div>
                `;
            });
            const emptyMov = 28 - sortedMov.length;
            for (let i = 0; i < emptyMov; i++) {
                movRowsHtml += `
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 10px;border-radius:6px;margin:4px 0;background:rgba(255,255,255,0.015);border:1px dashed rgba(255,255,255,0.08);">
                        <div style="font-size:11.5px;color:rgba(255,255,255,0.42);display:flex;align-items:center;gap:6px;">
                            <span style="opacity:0.4;">+</span> <span>Slot Movimento ${sortedMov.length + i + 1} Libero</span>
                        </div>
                        <div class="slot-target-tag normal" style="font-size:11px;">Max 28</div>
                    </div>
                `;
            }

            rolesHtml += `
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);padding:12px 16px;border-radius:10px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:6px;">
                        <div style="display:flex;align-items:center;gap:6px;">
                            <h4 style="color:var(--accent-cyan);font-size:13.5px;margin:0;font-weight:800;">🏃‍♂️ Giocatori di Movimento (Ordinati per Ruolo)</h4>
                        </div>
                        <span style="font-size:11.5px;font-weight:800;color:${sortedMov.length >= 28 ? '#4ade80' : 'var(--text-muted)'};">${sortedMov.length}/28 acquistati</span>
                    </div>
                    ${movRowsHtml}
                </div>
            `;
        } else {
            // CLASSIC MODE
            ['P', 'D', 'C', 'A'].forEach(role => {
                const slots = analysis.deptSlots[role] || [];
                const boughtCount = slots.filter(s => s.player).length;
                const maxCount = role === 'P' ? 3 : (role === 'A' ? 6 : 8);
                const roleLabels = { P: '🧤 Portieri (Max 3)', D: '🛡️ Difensori (Max 8)', C: '🪄 Centrocampisti (Max 8)', A: '⚡ Attaccanti (Max 6)' };
                
                let slotRowsHtml = '';
                slots.forEach(s => {
                    if (s.player) {
                        const p = s.player;
                        let deltaHtml = '';
                        if (s.delta > 0) {
                            deltaHtml = `<span class="slot-delta-badge over" title="Spesi +${s.delta} CR sopra il target base di ${s.baseTarget} CR">+${s.delta} CR</span>`;
                        } else if (s.delta < 0) {
                            deltaHtml = `<span class="slot-delta-badge saved" title="Risparmiati ${Math.abs(s.delta)} CR rispetto al target base di ${s.baseTarget} CR">${s.delta} CR</span>`;
                        } else {
                            deltaHtml = `<span class="slot-delta-badge equal" title="In target perfetto (${s.baseTarget} CR)">Target OK</span>`;
                        }

                        slotRowsHtml += `
                            <div style="display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <span class="role-badge ${p.role}" style="font-size:10px;padding:2px 5px;" title="Slot ${s.slotNum}">${s.slotNum}° ${p.role}</span>
                                    <b style="color:#fff;font-size:13px;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                    <span style="font-size:11px;color:var(--text-muted);">${p.team}</span>
                                    ${p.mantra ? `<span style="font-size:9.5px;color:var(--text-muted);background:rgba(255,255,255,0.06);padding:1px 4px;border-radius:3px;">${p.mantra}</span>` : ''}
                                </div>
                                <div style="display:flex;align-items:center;gap:10px;">
                                    ${deltaHtml}
                                    <span style="color:var(--accent-gold);font-weight:900;font-size:13px;">${p.paidPrice} CR</span>
                                    <button class="btn-action" style="padding:2px 7px;font-size:10.5px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" onclick="removePlayerFromRoster('${role}', ${s.origIdx}); openRosterModal('my_team');">✕ Svincola</button>
                                </div>
                            </div>
                        `;
                    } else {
                        let tagClass = 'normal';
                        let tagBadge = '';
                        if (s.pacingRatio >= 1.18 && s.dynTarget > s.baseTarget) {
                            tagClass = 'extra';
                            tagBadge = '✨ ';
                        } else if (s.pacingRatio < 0.82 && s.dynTarget < s.baseTarget) {
                            tagClass = 'tight';
                            tagBadge = '⚠️ ';
                        } else if (s.dynTarget <= 1) {
                            tagClass = 'critical';
                        }

                        slotRowsHtml += `
                            <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 10px;border-radius:6px;margin:4px 0;background:rgba(255,255,255,0.015);border:1px dashed rgba(255,255,255,0.08);cursor:pointer;transition:all 0.15s ease;" onclick="closeRosterModal(); filterBySlotShortcut('${role}', ${s.slotNum});" title="Slot ${s.slotNum} Libero: Budget dinamico ~${s.dynTarget} CR (Base: ${s.baseTarget} CR). Clicca per visualizzare i calciatori consigliati per questo slot.">
                                <div style="font-size:11.5px;color:rgba(255,255,255,0.42);display:flex;align-items:center;gap:6px;">
                                    <span style="opacity:0.4;">+</span> <span>Slot ${s.slotNum} Libero</span>
                                </div>
                                <div class="slot-target-tag ${tagClass}" style="font-size:11px;">
                                    ${tagBadge}max ~${s.dynTarget} CR <span style="opacity:0.4;font-size:9.5px;margin-left:4px;">(base: ${s.baseTarget})</span>
                                </div>
                            </div>
                        `;
                    }
                });

                rolesHtml += `
                    <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);padding:12px 16px;border-radius:10px;margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:6px;">
                            <h4 style="color:var(--accent-cyan);font-size:13.5px;margin:0;font-weight:800;">${roleLabels[role]}</h4>
                            <span style="font-size:11.5px;font-weight:800;color:${boughtCount >= maxCount ? '#4ade80' : 'var(--text-muted)'};">${boughtCount}/${maxCount} acquistati</span>
                        </div>
                        ${slotRowsHtml}
                    </div>
                `;
            });
        }

        contentHtml = `
            <!-- Header La Mia Rosa con Salute Finanziaria -->
            <div style="background:linear-gradient(135deg, rgba(0,242,254,0.1) 0%, rgba(139,92,246,0.1) 100%);border:1px solid rgba(0,242,254,0.3);padding:14px 18px;border-radius:12px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:22px;">🌟</span>
                        <h3 style="margin:0;font-size:18px;font-weight:900;color:#fff;">Rosa Ufficiale: ${escapeHtml(State.teamName || 'La Mia Rosa')}</h3>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:3px;">
                        Slot completati: <b style="color:#fff;">${totalPurchased} / ${maxRosterSlots}</b> &nbsp;•&nbsp; Max Rilancio Consentito: <b style="color:var(--accent-cyan);">${maxBid} CR</b>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:16px;">
                    <div style="text-align:right;">
                        <div style="font-size:10.5px;color:var(--text-muted);font-weight:700;">BUDGET RIMASTO</div>
                        <div style="font-size:22px;font-weight:900;color:var(--accent-gold);font-family:'Outfit',sans-serif;">${unikaRem} <small style="font-size:12px;">CR</small></div>
                    </div>
                    <div style="text-align:right;border-left:1px solid rgba(255,255,255,0.1);padding-left:14px;">
                        <div style="font-size:10.5px;color:var(--text-muted);font-weight:700;">SPESI</div>
                        <div style="font-size:16px;font-weight:800;color:#fff;">${unikaSpent} CR</div>
                    </div>
                </div>
            </div>

            <!-- Reparti con Slot Dinamici -->
            ${rolesHtml}
        `;
    } else {
        // VISTA SQUADRA RIVALE SELEZIONATA
        const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
        const maxRivalSlots = isMantra ? 31 : 25;
        const rData = State.rivals[targetTeam] || { spent: 0, budget: 1000, players: [], manager: '', tendency: '' };
        const rSpent = rData.spent || 0;
        const rRem = (rData.budget || 1000) - rSpent;
        const rTotal = rData.players.length;
        const maxBid = Math.max(1, rRem - (maxRivalSlots - rTotal) + 1);

        // Separa i giocatori del rivale per ruolo
        const byRole = { P: [], D: [], C: [], A: [] };
        rData.players.forEach(pl => {
            const full = PLAYERS.find(p => p.id === pl.id);
            if (full && byRole[full.role]) {
                byRole[full.role].push({ ...full, paidPrice: pl.price });
            }
        });

        let rolesHtml = '';

        if (isMantra) {
            const porList = byRole.P || [];
            const movList = [...(byRole.D || []), ...(byRole.C || []), ...(byRole.A || [])];

            const sortedMov = [...movList].sort((a, b) => {
                const scoreA = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(a.mantra) : 50;
                const scoreB = (typeof getMantraHierarchyScore === 'function') ? getMantraHierarchyScore(b.mantra) : 50;
                if (scoreA !== scoreB) return scoreA - scoreB;
                if ((b.paidPrice || 0) !== (a.paidPrice || 0)) return (b.paidPrice || 0) - (a.paidPrice || 0);
                return (b.ovr || 0) - (a.ovr || 0);
            });

            // 1. Portieri Rivali
            rolesHtml += `
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);padding:12px 16px;border-radius:10px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:6px;">
                        <h4 style="color:var(--mantra-por);font-size:13.5px;margin:0;font-weight:800;">🧤 Portieri (Por) - Max 3</h4>
                        <span style="font-size:11.5px;font-weight:800;color:${porList.length >= 3 ? '#4ade80' : 'var(--text-muted)'};">${porList.length}/3 acquistati</span>
                    </div>
            `;
            if (porList.length === 0) {
                rolesHtml += `<div style="font-size:12px;color:var(--text-muted);padding:4px 0;">Nessun portiere acquistato.</div>`;
            } else {
                porList.forEach(p => {
                    rolesHtml += `
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span class="role-badge P" style="font-size:10px;padding:2px 5px;background:var(--mantra-por);color:#fff;">Por</span>
                                <b style="color:#fff;font-size:13px;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                <span style="font-size:11px;color:var(--text-muted);">${p.team}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:12px;">
                                <span style="color:var(--accent-gold);font-weight:900;font-size:13px;">${p.paidPrice} CR</span>
                                <span style="font-size:10px;color:var(--text-muted);">(cons. ${p.prezzo_cons || 1} CR)</span>
                                <button class="btn-action" style="padding:2px 7px;font-size:10.5px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" title="Annulla assegnazione" onclick="unmarkPlayerTaken(${p.id}); openRosterModal('${targetTeam}');">✕ Svincola</button>
                            </div>
                        </div>
                    `;
                });
            }
            rolesHtml += `</div>`;

            // 2. Movimento Rivali (in ordine Mantra)
            rolesHtml += `
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);padding:12px 16px;border-radius:10px;margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:6px;">
                        <h4 style="color:var(--accent-cyan);font-size:13.5px;margin:0;font-weight:800;">🏃‍♂️ Giocatori di Movimento (Ordinati per Ruolo) - Max 28</h4>
                        <span style="font-size:11.5px;font-weight:800;color:${sortedMov.length >= 28 ? '#4ade80' : 'var(--text-muted)'};">${sortedMov.length}/28 acquistati</span>
                    </div>
            `;
            if (sortedMov.length === 0) {
                rolesHtml += `<div style="font-size:12px;color:var(--text-muted);padding:4px 0;">Nessun giocatore di movimento acquistato.</div>`;
            } else {
                sortedMov.forEach(p => {
                    const badges = (typeof renderMantraRoleBadges === 'function') ? renderMantraRoleBadges(p.mantra) : `<span class="role-badge ${p.role}">${p.role}</span>`;
                    rolesHtml += `
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                            <div style="display:flex;align-items:center;gap:8px;">
                                ${badges}
                                <b style="color:#fff;font-size:13px;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                <span style="font-size:11px;color:var(--text-muted);">${p.team}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:12px;">
                                <span style="color:var(--accent-gold);font-weight:900;font-size:13px;">${p.paidPrice} CR</span>
                                <span style="font-size:10px;color:var(--text-muted);">(cons. ${p.prezzo_cons || 1} CR)</span>
                                <button class="btn-action" style="padding:2px 7px;font-size:10.5px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" title="Annulla assegnazione" onclick="unmarkPlayerTaken(${p.id}); openRosterModal('${targetTeam}');">✕ Svincola</button>
                            </div>
                        </div>
                    `;
                });
            }
            rolesHtml += `</div>`;
        } else {
            // CLASSIC RIVALS
            ['P', 'D', 'C', 'A'].forEach(role => {
                const list = byRole[role];
                const roleLabels = { P: '🧤 Portieri (Max 3)', D: '🛡️ Difensori (Max 8)', C: '⚙️ Centrocampisti (Max 8)', A: '🎯 Attaccanti (Max 6)' };
                
                rolesHtml += `
                    <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);padding:12px 16px;border-radius:10px;margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:6px;">
                            <h4 style="color:var(--accent-cyan);font-size:13.5px;margin:0;font-weight:800;">${roleLabels[role]}</h4>
                            <span style="font-size:11.5px;font-weight:800;color:${list.length >= (role === 'P'?3:role==='A'?6:8) ? '#4ade80' : 'var(--text-muted)'};">${list.length} acquistati</span>
                        </div>
                `;

                if (list.length === 0) {
                    rolesHtml += `<div style="font-size:12px;color:var(--text-muted);padding:4px 0;">Nessun calciatore acquistato in questo reparto dal rivale.</div>`;
                } else {
                    list.forEach((p) => {
                        rolesHtml += `
                            <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <span class="role-badge ${p.role}" style="font-size:10.5px;width:20px;height:20px;">${p.role}</span>
                                    <b style="color:#fff;font-size:13px;cursor:pointer;" onclick="openPlayerProfileModal(${p.id})">${p.name}</b>
                                    <span style="font-size:11px;color:var(--text-muted);">${p.team}</span>
                                    ${p.mantra ? `<span style="font-size:9.5px;color:var(--text-muted);background:rgba(255,255,255,0.06);padding:1px 4px;border-radius:3px;">${p.mantra}</span>` : ''}
                                </div>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <span style="color:var(--accent-gold);font-weight:900;font-size:13px;">${p.paidPrice} CR</span>
                                    <span style="font-size:10px;color:var(--text-muted);">(cons. ${p.prezzo_cons || 1} CR)</span>
                                    <button class="btn-action" style="padding:2px 7px;font-size:10.5px;background:rgba(239,68,68,0.2);border-color:#ef4444;color:#ef4444;" title="Annulla assegnazione e rimborsa i crediti a questa squadra" onclick="unmarkPlayerTaken(${p.id}); openRosterModal('${targetTeam}');">✕ Svincola</button>
                                </div>
                            </div>
                        `;
                    });
                }
                rolesHtml += `</div>`;
            });
        }

        contentHtml = `
            <!-- Header Squadra Rivale -->
            <div style="background:linear-gradient(135deg, rgba(239,68,68,0.1) 0%, rgba(245,158,11,0.08) 100%);border:1px solid rgba(239,68,68,0.35);padding:14px 18px;border-radius:12px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:22px;">🛡️</span>
                        <h3 style="margin:0;font-size:18px;font-weight:900;color:#fff;">Rosa Rivale: ${targetTeam}</h3>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:3px;">
                        Manager: <b style="color:var(--accent-cyan);">${rData.manager}</b> &nbsp;•&nbsp; Tendenza: <b style="color:#fff;">${rData.tendency}</b>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">
                        Slot completati: <b style="color:#fff;">${rTotal} / ${maxRivalSlots}</b> &nbsp;•&nbsp; Max Rilancio: <b style="color:var(--accent-cyan);">${maxBid} CR</b>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:16px;">
                    <div style="text-align:right;">
                        <div style="font-size:10.5px;color:var(--text-muted);font-weight:700;">BUDGET RIMASTO</div>
                        <div style="font-size:22px;font-weight:900;color:var(--accent-gold);font-family:'Outfit',sans-serif;">${rRem} <small style="font-size:12px;">CR</small></div>
                    </div>
                    <div style="text-align:right;border-left:1px solid rgba(255,255,255,0.1);padding-left:14px;">
                        <div style="font-size:10.5px;color:var(--text-muted);font-weight:700;">SPESI</div>
                        <div style="font-size:16px;font-weight:800;color:#fff;">${rSpent} CR</div>
                    </div>
                </div>
            </div>

            <!-- Reparti del Rivale -->
            ${rolesHtml}
        `;
    }

    body.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:24px;">📋</span>
                <div>
                    <h3 class="font-title" style="color:var(--accent-cyan);font-size:19px;margin:0;">Rose Ufficiali Lega a 8 (Asta Live 2026/27)</h3>
                    <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">Visualizza le rose di tutti gli 8 partecipanti, crediti rimasti e colpi di mercato</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <button class="btn-action" style="padding:4px 10px;font-size:12px;background:rgba(14,165,233,0.18);border-color:#0284c7;color:#38bdf8;font-weight:600;" onclick="openCsvRosterImportModal('${targetTeam === 'ALL' ? 'Unika' : targetTeam}')">📂 Carica CSV</button>
                <button class="btn-action" style="padding:4px 10px;font-size:12px;" onclick="closeRosterModal()">Chiudi ✕</button>
            </div>
        </div>

        ${tabsHtml}
        ${contentHtml}
    `;
}

function closeRosterModal() {
    const modal = document.getElementById('rosterModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
}
