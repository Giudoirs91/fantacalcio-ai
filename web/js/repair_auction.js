// --- repair_auction.js ---
// Mercato di Riparazione Fanta Master AI 2026/27
// Gestione svincoli con regole di rimborso personalizzate, radar svincolati e lista della spesa AI

let repairAuctionState = {
    selectedCutIds: [],
    refundRule: 'half_qta', // 'half_qta' | 'paid' | 'half_paid' | 'one'
    roleFilter: 'ALL',
    searchQuery: '',
    sortBy: 'ovr', // 'ovr' | 'fvm' | 'qta' | 'prezzo_cons'
    onlyNewArrivals: false
};

function calculatePlayerRefund(p, rule) {
    if (!p) return 0;
    const paid = p.paidPrice || p.prezzo_cons || 1;
    const qta = p.qta || p.fvm || 10;

    switch (rule) {
        case 'half_qta':
            return Math.max(1, Math.ceil(qta / 2));
        case 'paid':
            return paid;
        case 'half_paid':
            return Math.max(1, Math.ceil(paid / 2));
        case 'one':
            return 1;
        default:
            return Math.max(1, Math.ceil(qta / 2));
    }
}

function toggleCutPlayer(playerId) {
    const idx = repairAuctionState.selectedCutIds.indexOf(playerId);
    if (idx !== -1) {
        repairAuctionState.selectedCutIds.splice(idx, 1);
    } else {
        repairAuctionState.selectedCutIds.push(playerId);
    }
    renderRepairAuctionView();
}

function setRepairRefundRule(rule) {
    repairAuctionState.refundRule = rule;
    renderRepairAuctionView();
}

function setRepairRoleFilter(role) {
    repairAuctionState.roleFilter = role;
    renderRepairAuctionView();
}

function setRepairSortBy(sortKey) {
    repairAuctionState.sortBy = sortKey;
    renderRepairAuctionView();
}

function toggleRepairNewArrivals() {
    repairAuctionState.onlyNewArrivals = !repairAuctionState.onlyNewArrivals;
    renderRepairAuctionView();
}

function onRepairSearchInput(val) {
    repairAuctionState.searchQuery = val.trim().toLowerCase();
    renderRepairAuctionView();
}

function confirmExecuteCuts() {
    if (repairAuctionState.selectedCutIds.length === 0) {
        alert("Seleziona almeno un calciatore da svincolare!");
        return;
    }

    const unikaPlayers = getUnikaPlayersFull();
    const toCut = unikaPlayers.filter(p => repairAuctionState.selectedCutIds.includes(p.id));
    const refundTotal = toCut.reduce((sum, p) => sum + calculatePlayerRefund(p, repairAuctionState.refundRule), 0);

    if (!confirm(`Sei sicuro di voler svincolare ${toCut.length} calciatori?\n\nRecupererai complessivamente +${refundTotal} CR per l'asta di riparazione.`)) {
        return;
    }

    // Rimuovi da State.slots
    toCut.forEach(p => {
        const slotKey = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (State.slots[p.role] ? p.role : 'C');
        const idx = State.slots[slotKey].players.findIndex(x => x.id === p.id);
        if (idx !== -1) {
            State.slots[slotKey].players.splice(idx, 1);
        }
    });

    // Riduci la spesa complessiva restituendo i crediti recuperati
    State.budgetSpent = Math.max(0, State.budgetSpent - refundTotal);

    saveStateToStorage();
    updateAllViews();

    repairAuctionState.selectedCutIds = [];
    renderRepairAuctionView();

    const toastMsg = `✓ Svincolati ${toCut.length} calciatori! +${refundTotal} CR aggiunti al budget disponibile.`;
    if (typeof showSyncToast === 'function') {
        showSyncToast(toastMsg);
    } else {
        alert(toastMsg);
    }
}

// Calcolo Lista della Spesa Ottimizzata AI
function generateRepairShoppingList(freeSlots, availableBudget, freeAgents) {
    if (availableBudget <= 0) return [];
    
    // Ordina i liberi per efficienza OVR / prezzo_cons
    const candidates = freeAgents.filter(p => (p.ovr || 70) >= 74);
    candidates.sort((a, b) => {
        const effA = (a.ovr || 70) / Math.max(1, a.prezzo_cons || 1);
        const effB = (b.ovr || 70) / Math.max(1, b.prezzo_cons || 1);
        return effB - effA;
    });

    return candidates.slice(0, 5);
}

function buyFreeAgentDirect(playerId) {
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;
    buyPlayer(p.id);
}

function renderRepairPlayerBadge(p) {
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    if (isMantra && p.mantra) {
        return `<span class="mantra-pill" style="font-size:10px;padding:2px 6px;background:rgba(0,242,254,0.15);border:1px solid var(--accent-cyan);color:var(--accent-cyan);border-radius:4px;font-weight:800;">${p.mantra}</span>`;
    }
    return `<span class="role-badge ${p.role}" style="font-size:10px;padding:2px 5px;">${p.role}</span>`;
}

function renderRepairAuctionView() {
    const container = document.getElementById('viewRepairAuction');
    if (!container) return;

    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const unikaPlayers = getUnikaPlayersFull();
    const takenIds = Array.isArray(State.takenByOthers) ? State.takenByOthers : [];
    const unikaIds = unikaPlayers.map(p => p.id);

    // Calcolo crediti attuali e recuperabili
    const currentRemaining = (State.budgetTotal || 1000) - (State.budgetSpent || 0);
    const toCut = unikaPlayers.filter(p => repairAuctionState.selectedCutIds.includes(p.id));
    const refundSum = toCut.reduce((s, p) => s + calculatePlayerRefund(p, repairAuctionState.refundRule), 0);
    const projectedRemaining = currentRemaining + refundSum;

    // Calcolo slot liberati
    const freedSlots = { P: 0, D: 0, C: 0, A: 0 };
    toCut.forEach(p => {
        const r = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (p.role || 'C');
        if (freedSlots[r] !== undefined) freedSlots[r]++;
    });

    // Calcolo Calciatori Svincolati Liberi
    let freeAgents = PLAYERS.filter(p => !unikaIds.includes(p.id) && !takenIds.includes(p.id));

    // Filtri radar (Mantra o Classic)
    if (repairAuctionState.roleFilter !== 'ALL') {
        const rf = repairAuctionState.roleFilter.toUpperCase();
        if (isMantra) {
            freeAgents = freeAgents.filter(p => {
                if (!p.mantra) return false;
                const mRoles = String(p.mantra).toUpperCase().split(/[,;/]+/).map(s => s.trim());
                if (rf === 'DIF') return mRoles.some(r => ['DC', 'B', 'DD', 'DS'].includes(r));
                if (rf === 'MED') return mRoles.some(r => ['E', 'M', 'C'].includes(r));
                if (rf === 'ATT') return mRoles.some(r => ['T', 'W', 'A', 'PC'].includes(r));
                return mRoles.includes(rf);
            });
        } else {
            freeAgents = freeAgents.filter(p => p.role === repairAuctionState.roleFilter);
        }
    }
    if (repairAuctionState.onlyNewArrivals) {
        freeAgents = freeAgents.filter(p => p.is_new_arrival || p.diff_q > 0 || (p.presenze_2627 && p.presenze_2627 > 0));
    }
    if (repairAuctionState.searchQuery) {
        const q = repairAuctionState.searchQuery;
        freeAgents = freeAgents.filter(p => p.name.toLowerCase().includes(q) || p.team.toLowerCase().includes(q) || (p.mantra && p.mantra.toLowerCase().includes(q)));
    }

    // Ordinamento
    freeAgents.sort((a, b) => {
        if (repairAuctionState.sortBy === 'ovr') return (b.ovr || 0) - (a.ovr || 0);
        if (repairAuctionState.sortBy === 'fvm') return (b.fvm || 0) - (a.fvm || 0);
        if (repairAuctionState.sortBy === 'qta') return (b.qta || 0) - (a.qta || 0);
        if (repairAuctionState.sortBy === 'prezzo_cons') return (b.prezzo_cons || 0) - (a.prezzo_cons || 0);
        return 0;
    });

    const aiSuggestions = generateRepairShoppingList(freedSlots, projectedRemaining, freeAgents);

    // Render Lista Giocatori Unika da Svincolare
    let unikaCutListHtml = '';
    if (unikaPlayers.length === 0) {
        unikaCutListHtml = `
            <div style="padding:30px;text-align:center;color:var(--text-muted);font-size:12.5px;">
                La tua rosa è vuota. Nessun calciatore da svincolare.
            </div>
        `;
    } else {
        const rolesOrder = isMantra ? [
            { key: 'P', label: '🧤 Portieri (Por)' },
            { key: 'D', label: '🛡️ Difensori (Dc, B, Dd, Ds)' },
            { key: 'C', label: '🪄 Centrocampo & Esterni (E, M, C)' },
            { key: 'A', label: '⚡ Trequarti & Attacco (T, W, A, Pc)' }
        ] : [
            { key: 'P', label: '🧤 Portieri' },
            { key: 'D', label: '🛡️ Difensori' },
            { key: 'C', label: '🪄 Centrocampisti' },
            { key: 'A', label: '⚡ Attaccanti' }
        ];

        rolesOrder.forEach(grp => {
            const rolePlayers = unikaPlayers.filter(p => {
                const isP = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR')));
                return isP ? (grp.key === 'P') : (p.role === grp.key);
            });

            if (rolePlayers.length > 0) {
                unikaCutListHtml += `
                    <div style="font-size:11px;font-weight:700;color:var(--text-muted);margin:8px 0 4px 0;text-transform:uppercase;">
                        ${grp.label}
                    </div>
                `;

                rolePlayers.forEach(p => {
                    const isCut = repairAuctionState.selectedCutIds.includes(p.id);
                    const refund = calculatePlayerRefund(p, repairAuctionState.refundRule);

                    unikaCutListHtml += `
                        <div class="repair-cut-item ${isCut ? 'selected' : ''}" onclick="toggleCutPlayer(${p.id})">
                            <input type="checkbox" ${isCut ? 'checked' : ''} style="pointer-events:none;">
                            ${renderRepairPlayerBadge(p)}
                            <div style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                                <b style="color:#fff;font-size:12.5px;">${p.name}</b>
                                <span style="font-size:11px;color:var(--text-muted);">(${p.team})</span>
                            </div>
                            <div style="text-align:right;white-space:nowrap;">
                                <span style="font-size:10.5px;color:var(--text-muted);">Pagato: ${p.paidPrice || p.prezzo_cons || 1} CR</span>
                                <div style="font-size:11.5px;font-weight:800;color:#34d399;">+${refund} CR</div>
                            </div>
                        </div>
                    `;
                });
            }
        });
    }

    // Render Lista Svincolati Liberi (Top 40)
    const freeAgentsRowsHtml = freeAgents.slice(0, 40).map(p => {
        return `
            <tr>
                <td style="text-align:center;width:${isMantra ? '70px' : '40px'};">
                    ${renderRepairPlayerBadge(p)}
                </td>
                <td>
                    <div style="font-weight:700;color:#fff;font-size:12.5px;">
                        ${p.name} 
                        ${(!isMantra && p.mantra) ? `<span style="font-size:10.5px;color:var(--text-muted);">[${p.mantra}]</span>` : ''}
                        ${p.is_new_arrival ? `<span class="tag-new" style="font-size:9.5px;padding:1px 4px;margin-left:4px;">NUOVO</span>` : ''}
                    </div>
                    <div style="font-size:11px;color:var(--text-muted);">${p.team}</div>
                </td>
                <td style="text-align:center;"><span class="ovr-pill ${p.ovr >= 85 ? 'top-tier' : ''}" style="font-size:11px;">${p.ovr}</span></td>
                <td style="text-align:center;font-weight:700;color:#fbbf24;">${p.qta || p.fvm || '-'}</td>
                <td style="text-align:center;font-weight:700;color:var(--accent-cyan);">${p.prezzo_cons || 1} CR</td>
                <td style="text-align:center;width:80px;">
                    <button class="btn-action" style="padding:3px 8px;font-size:11px;background:rgba(0,242,254,0.18);border-color:#0284c7;color:#38bdf8;font-weight:700;" onclick="buyFreeAgentDirect(${p.id})">
                        + Acquista
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    container.innerHTML = `
        <div class="repair-container">
            <!-- HEADER -->
            <div class="repair-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:32px;">🛒</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:22px;color:var(--accent-cyan);">Mercato di Riparazione & Svincoli</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            Simulatore tagli con recupero crediti, radar svincolati liberi e suggerimenti per l'asta di riparazione
                        </div>
                    </div>
                </div>

                <div class="repair-budget-summary">
                    <div class="repair-badge-box">
                        <span class="label">Budget Attuale</span>
                        <span class="val">${currentRemaining} CR</span>
                    </div>
                    <div class="repair-badge-box refund">
                        <span class="label">Crediti Recuperati</span>
                        <span class="val">+${refundSum} CR</span>
                    </div>
                    <div class="repair-badge-box total">
                        <span class="label">Budget Riparazione</span>
                        <span class="val">${projectedRemaining} CR</span>
                    </div>
                </div>
            </div>

            <!-- LAYOUT A DUE COLONNE: SVINCOLI (SX) + RADAR LIBERI (DX) -->
            <div class="repair-layout">
                <!-- COLONNA SINISTRA: SIMULATORE SVINCOLI -->
                <div class="repair-panel cuts">
                    <div class="repair-panel-header">
                        <div>
                            <h3 style="margin:0;font-size:15px;color:#fff;">✂️ Tagli & Recupero Crediti</h3>
                            <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">
                                Seleziona i calciatori da cedere per incassare crediti
                            </div>
                        </div>
                    </div>

                    <!-- REGOLA RIMBORSO -->
                    <div style="margin:12px 0;background:rgba(255,255,255,0.02);padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);">
                        <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;margin-bottom:6px;">Regola Recupero Crediti</label>
                        <select style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:6px 10px;font-size:12px;" onchange="setRepairRefundRule(this.value)">
                            <option value="half_qta" ${repairAuctionState.refundRule === 'half_qta' ? 'selected' : ''}>Metà Quotazione Attuale (Standard Fanta)</option>
                            <option value="paid" ${repairAuctionState.refundRule === 'paid' ? 'selected' : ''}>100% del Prezzo Pagato all'asta</option>
                            <option value="half_paid" ${repairAuctionState.refundRule === 'half_paid' ? 'selected' : ''}>50% del Prezzo Pagato all'asta</option>
                            <option value="one" ${repairAuctionState.refundRule === 'one' ? 'selected' : ''}>1 Credito Fisso per svincolo</option>
                        </select>
                    </div>

                    <!-- LISTA GIOCATORI UNIKA -->
                    <div class="repair-cut-list">
                        ${unikaCutListHtml}
                    </div>

                    <!-- RIEPILOGO E CONFERMA TAGLI -->
                    <div style="margin-top:14px;border-top:1px solid rgba(255,255,255,0.08);padding-top:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-size:12px;">
                            <span style="color:var(--text-muted);">Calciatori selezionati: <b>${toCut.length}</b></span>
                            <span style="color:#34d399;font-weight:800;">Totale: +${refundSum} CR</span>
                        </div>
                        <button class="btn-action" style="width:100%;padding:10px;font-size:13px;font-weight:800;background:linear-gradient(135deg, #ef4444, #dc2626);color:#fff;border:none;box-shadow:0 4px 15px rgba(239,68,68,0.3);${toCut.length === 0 ? 'opacity:0.4;cursor:not-allowed;' : ''}" ${toCut.length === 0 ? 'disabled' : ''} onclick="confirmExecuteCuts()">
                            ✂️ Conferma Svincoli (+${refundSum} CR)
                        </button>
                    </div>
                </div>

                <!-- COLONNA DESTRA: RADAR CALCIATORI LIBERI & LISTA DELLA SPESA -->
                <div class="repair-panel free-agents">
                    <div class="repair-panel-header">
                        <div>
                            <h3 style="margin:0;font-size:15px;color:var(--accent-cyan);">🔍 Radar Svincolati Liberi</h3>
                            <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">
                                ${freeAgents.length} calciatori liberi acquistabili all'asta di riparazione
                            </div>
                        </div>

                        <div style="display:flex;align-items:center;gap:8px;">
                            <input type="text" class="repair-search-input" placeholder="Cerca svincolato o squadra..." value="${repairAuctionState.searchQuery}" oninput="onRepairSearchInput(this.value)">
                        </div>
                    </div>

                    <!-- FILTRI TOOLBAR -->
                    <div class="repair-filter-toolbar">
                        <div class="repair-role-tabs">
                            ${(isMantra ? [
                                { id: 'ALL', label: 'Tutti' },
                                { id: 'Por', label: 'Por' },
                                { id: 'Dc', label: 'Dc' },
                                { id: 'Dd', label: 'Dd' },
                                { id: 'Ds', label: 'Ds' },
                                { id: 'E', label: 'E' },
                                { id: 'M', label: 'M' },
                                { id: 'C', label: 'C' },
                                { id: 'T', label: 'T' },
                                { id: 'W', label: 'W' },
                                { id: 'A', label: 'A' },
                                { id: 'Pc', label: 'Pc' }
                            ] : [
                                { id: 'ALL', label: 'Tutti' },
                                { id: 'P', label: 'P' },
                                { id: 'D', label: 'D' },
                                { id: 'C', label: 'C' },
                                { id: 'A', label: 'A' }
                            ]).map(r => `
                                <button class="repair-role-btn ${repairAuctionState.roleFilter === r.id ? 'active' : ''}" onclick="setRepairRoleFilter('${r.id}')">
                                    ${r.label}
                                </button>
                            `).join('')}
                        </div>

                        <div style="display:flex;align-items:center;gap:8px;">
                            <button class="btn-action ${repairAuctionState.onlyNewArrivals ? 'active' : ''}" style="font-size:11px;padding:4px 8px;background:${repairAuctionState.onlyNewArrivals ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.05)'};color:${repairAuctionState.onlyNewArrivals ? '#000' : '#fff'};font-weight:700;" onclick="toggleRepairNewArrivals()">
                                🆕 Nuovi Arrivi / Trend
                            </button>
                            <select style="background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.12);color:#fff;border-radius:6px;padding:4px 8px;font-size:11px;" onchange="setRepairSortBy(this.value)">
                                <option value="ovr" ${repairAuctionState.sortBy === 'ovr' ? 'selected' : ''}>Ordina: OVR</option>
                                <option value="qta" ${repairAuctionState.sortBy === 'qta' ? 'selected' : ''}>Ordina: Quotazione</option>
                                <option value="fvm" ${repairAuctionState.sortBy === 'fvm' ? 'selected' : ''}>Ordina: FVM</option>
                                <option value="prezzo_cons" ${repairAuctionState.sortBy === 'prezzo_cons' ? 'selected' : ''}>Ordina: Prezzo Consigliato</option>
                            </select>
                        </div>
                    </div>

                    <!-- CONSIGLI LISTA SPESA AI -->
                    ${aiSuggestions.length > 0 ? `
                        <div class="repair-ai-suggestions">
                            <div style="font-size:11px;font-weight:700;color:var(--accent-cyan);margin-bottom:6px;display:flex;align-items:center;gap:5px;">
                                <span>💡</span> <b>Consigliati dall'AI per la Riparazione:</b>
                            </div>
                            <div style="display:flex;gap:8px;flex-wrap:wrap;">
                                ${aiSuggestions.map(s => `
                                    <div class="repair-ai-chip" onclick="buyFreeAgentDirect(${s.id})">
                                        ${renderRepairPlayerBadge(s)}
                                        <b>${s.name}</b> (${s.team})
                                        <span style="color:#fbbf24;">${s.prezzo_cons} CR</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <!-- TABELLA CALCIATORI LIBERI -->
                    <div class="repair-table-wrap">
                        <table class="repair-table">
                            <thead>
                                <tr>
                                    <th style="text-align:center;width:${isMantra ? '70px' : '40px'};">${isMantra ? 'R. Mantra' : 'R'}</th>
                                    <th>Calciatore & Squadra</th>
                                    <th style="text-align:center;width:60px;">OVR</th>
                                    <th style="text-align:center;width:65px;">Quot.</th>
                                    <th style="text-align:center;width:75px;">Cons.</th>
                                    <th style="text-align:center;width:80px;">Azione</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${freeAgents.length === 0 ? `
                                    <tr><td colspan="6" style="text-align:center;padding:30px;color:var(--text-muted);">Nessun calciatore trovato con i filtri correnti.</td></tr>
                                ` : freeAgentsRowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

window.renderRepairAuctionView = renderRepairAuctionView;
window.toggleCutPlayer = toggleCutPlayer;
window.setRepairRefundRule = setRepairRefundRule;
window.setRepairRoleFilter = setRepairRoleFilter;
window.setRepairSortBy = setRepairSortBy;
window.toggleRepairNewArrivals = toggleRepairNewArrivals;
window.onRepairSearchInput = onRepairSearchInput;
window.confirmExecuteCuts = confirmExecuteCuts;
window.buyFreeAgentDirect = buyFreeAgentDirect;
