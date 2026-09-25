let tradeMachineState = {
    selectedRival: null,
    givingPlayerIds: [],
    receivingPlayerIds: [],
    activeView: 'auto' // 'auto' | 'custom'
};
function getRivalPlayersFull(rivalName) {
    if (!State.rivals || !State.rivals[rivalName] || !State.rivals[rivalName].players) return [];
    return State.rivals[rivalName].players.map(item => {
        const p = PLAYERS.find(pl => pl.id === item.id);
        return p ? { ...p, paidPrice: item.price } : null;
    }).filter(Boolean);
}
function getMyTeamPlayersFull() {
    if (!State.slots) return [];
    return [
        ...(State.slots.P?.players || []),
        ...(State.slots.D?.players || []),
        ...(State.slots.C?.players || []),
        ...(State.slots.A?.players || [])
    ];
}
const getUnikaPlayersFull = getMyTeamPlayersFull;
function renderTradePlayerBadge(p) {
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    if (isMantra && p.mantra) {
        return `<span class="mantra-pill" style="font-size:10px;padding:2px 6px;background:rgba(0,242,254,0.15);border:1px solid var(--accent-cyan);color:var(--accent-cyan);border-radius:4px;font-weight:800;letter-spacing:0.3px;">${p.mantra}</span>`;
    }
    return `<span class="role-badge ${p.role}" style="font-size:10px;padding:2px 5px;">${p.role}</span>`;
}
function getMantraRolesList(p) {
    if (!p.mantra) return [(p.role === 'P' ? 'Por' : p.role)];
    return String(p.mantra).split(/[,;/]+/).map(s => s.trim()).filter(Boolean);
}
function analyzeRosterStrengths(playersList) {
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    if (isMantra) {
        const categories = {
            POR: { label: 'Portieri', roles: ['Por'], target: 3, players: [] },
            DC: { label: 'Difensori Centrali (Dc/B)', roles: ['Dc', 'B'], target: 5, players: [] },
            TER: { label: 'Terzini (Dd/Ds)', roles: ['Dd', 'Ds'], target: 4, players: [] },
            EST: { label: 'Esterni (E/W)', roles: ['E', 'W'], target: 4, players: [] },
            MED: { label: 'Mediani (M)', roles: ['M'], target: 3, players: [] },
            CC: { label: 'Centrocampisti (C)', roles: ['C'], target: 4, players: [] },
            TREQ: { label: 'Trequartisti (T/A)', roles: ['T', 'A'], target: 3, players: [] },
            PUNTA: { label: 'Punte Centrali (Pc)', roles: ['Pc'], target: 3, players: [] }
        };
        playersList.forEach(p => {
            const pRoles = getMantraRolesList(p);
            Object.keys(categories).forEach(catKey => {
                const cat = categories[catKey];
                if (pRoles.some(r => cat.roles.includes(r))) {
                    cat.players.push(p);
                }
            });
        });
        const stats = {};
        Object.keys(categories).forEach(catKey => {
            const cat = categories[catKey];
            const count = cat.players.length;
            const totalOvr = cat.players.reduce((s, p) => s + (p.ovr || 70), 0);
            const avgOvr = count > 0 ? (totalOvr / count) : 0;
            const topTierCount = cat.players.filter(p => (p.ovr || 0) >= 82).length;
            let status = 'balanced';
            if (count >= cat.target + 2 || (count >= cat.target + 1 && topTierCount >= 2)) status = 'surplus';
            else if (count <= cat.target - 2 || count === 0) status = 'deficit';
            stats[catKey] = {
                label: cat.label,
                count,
                totalOvr,
                avgOvr,
                topTierCount,
                status,
                players: cat.players
            };
        });
        return stats;
    }
    const roles = { P: [], D: [], C: [], A: [] };
    playersList.forEach(p => {
        const r = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (p.role || 'C');
        if (roles[r]) roles[r].push(p);
    });
    const stats = {};
    ['P', 'D', 'C', 'A'].forEach(r => {
        const count = roles[r].length;
        const totalOvr = roles[r].reduce((s, p) => s + (p.ovr || 70), 0);
        const avgOvr = count > 0 ? (totalOvr / count) : 0;
        const topTierCount = roles[r].filter(p => (p.ovr || 0) >= 83).length;
        const idealCounts = { P: 3, D: 8, C: 8, A: 6 };
        const idealAvg = { P: 78, D: 78, C: 79, A: 81 };
        const countDiff = count - idealCounts[r];
        const qualityDiff = avgOvr - idealAvg[r];
        let status = 'balanced';
        if (topTierCount >= 3 || (countDiff >= 1 && qualityDiff >= 2)) status = 'surplus';
        else if (countDiff <= -2 || qualityDiff <= -3 || (r === 'A' && topTierCount === 0)) status = 'deficit';
        stats[r] = { count, totalOvr, avgOvr, topTierCount, status, players: roles[r] };
    });
    return stats;
}
function generateAutoTradeProposals() {
    const unikaPlayers = getUnikaPlayersFull();
    if (unikaPlayers.length === 0) return [];
    const rivalsList = Object.keys(State.rivals || {});
    if (rivalsList.length === 0) return [];
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const unikaStats = analyzeRosterStrengths(unikaPlayers);
    const proposals = [];
    rivalsList.forEach(rName => {
        const rPlayers = getRivalPlayersFull(rName);
        if (rPlayers.length === 0) return;
        const rStats = analyzeRosterStrengths(rPlayers);
        if (!isMantra) {
            const classicRoles = ['P', 'D', 'C', 'A'];
            classicRoles.forEach(roleKey => {
                const giveStat = unikaStats[roleKey];
                const recStat = rStats[roleKey];
                if (!giveStat || !recStat) return;
                const unikaCandidates = giveStat.players.filter(p => (p.ovr || 70) >= 74);
                const rivalCandidates = recStat.players.filter(p => (p.ovr || 70) >= 74);
                unikaCandidates.forEach(pGive => {
                    rivalCandidates.forEach(pRec => {
                        if (pGive.id === pRec.id) return;
                        const ovrDiff = (pRec.ovr || 70) - (pGive.ovr || 70);
                        const fvmDiff = (pRec.fvm || 0) - (pGive.fvm || 0);
                        if (Math.abs(ovrDiff) <= 4) {
                            const equityScore = Math.max(55, Math.min(99, 100 - Math.abs(ovrDiff) * 8 - Math.abs(fvmDiff) * 0.35));
                            let rationale = '';
                            if (pGive.is_chronic_fragile && !pRec.is_chronic_fragile) {
                                rationale = `Upgrade Integrità Fisica: cedi ${pGive.name} a rischio infortuni per un ${pRec.name} con tenuta fisica al 100% nel medesimo ruolo (${roleKey}).`;
                            } else if ((pRec.fm_2627 || pRec.fm || 6) > (pGive.fm_2627 || pGive.fm || 6)) {
                                rationale = `Scambio Classic pari-ruolo (${roleKey}): ottieni ${pRec.name} con FantaMedia più alta a fronte di un OVR comparabile (${pGive.ovr} vs ${pRec.ovr}).`;
                            } else {
                                rationale = `Scambio Classic bilanciato nel reparto ${roleKey} (${pGive.name} [${pGive.ovr} OVR] per ${pRec.name} [${pRec.ovr} OVR]).`;
                            }
                            proposals.push({
                                rivalName: rName,
                                giving: [pGive],
                                receiving: [pRec],
                                equityScore: Math.round(equityScore),
                                unikaOvrDelta: ovrDiff,
                                rationale
                            });
                        }
                    });
                });
            });
        } else {
            const mantraCategories = ['DC', 'TER', 'EST', 'MED', 'CC', 'TREQ', 'PUNTA'];
            mantraCategories.forEach(giveCat => {
                mantraCategories.forEach(recCat => {
                    const giveStat = unikaStats[giveCat];
                    const recStat = rStats[recCat];
                    if (!giveStat || !recStat) return;
                    const isSameCat = (giveCat === recCat);
                    const isAsymmetry = (giveStat.status === 'surplus' && unikaStats[recCat]?.status === 'deficit') ||
                                        (rStats[giveCat]?.status === 'deficit' && recStat.status === 'surplus');
                    if (!isSameCat && !isAsymmetry) return;
                    const unikaCanGive = giveStat.players.filter(p => (p.ovr || 70) >= 74);
                    const rivalCanGive = recStat.players.filter(p => (p.ovr || 70) >= 74);
                    unikaCanGive.forEach(pGive => {
                        rivalCanGive.forEach(pRec => {
                            if (pGive.id === pRec.id) return;
                            const ovrDiff = (pRec.ovr || 70) - (pGive.ovr || 70);
                            const fvmDiff = (pRec.fvm || 0) - (pGive.fvm || 0);
                            if (Math.abs(ovrDiff) <= 4) {
                                const equityScore = Math.max(50, Math.min(99, 100 - Math.abs(ovrDiff) * 8 - Math.abs(fvmDiff) * 0.4));
                                let rationale = '';
                                const giveLabel = giveStat.label || giveCat;
                                const recLabel = recStat.label || recCat;
                                if (!isSameCat) {
                                    if (giveStat.status === 'surplus' && unikaStats[recCat]?.status === 'deficit') {
                                        rationale = `Ottimizzazione Tattica Mantra: colmi il deficit in ${recLabel} sacrificando un elemento in ${giveLabel} dove hai surplus di titolari.`;
                                    } else {
                                        rationale = `Sinergia Mantra Win-Win: ${rName} è a corto di ${giveLabel} e ti cede un profilo affine in ${recLabel}.`;
                                    }
                                } else {
                                    rationale = `Scambio Mantra bilanciato nella categoria ${giveLabel} (${pGive.name} [${pGive.mantra}] per ${pRec.name} [${pRec.mantra}]).`;
                                }
                                proposals.push({
                                    rivalName: rName,
                                    giving: [pGive],
                                    receiving: [pRec],
                                    equityScore: Math.round(equityScore),
                                    unikaOvrDelta: ovrDiff,
                                    rationale
                                });
                            }
                        });
                    });
                });
            });
        }
    });
    const seenCombos = new Set();
    const uniqueProposals = [];
    proposals.forEach(p => {
        const key = `${p.rivalName}_${p.giving[0].id}_${p.receiving[0].id}`;
        if (!seenCombos.has(key)) {
            seenCombos.add(key);
            uniqueProposals.push(p);
        }
    });
    uniqueProposals.sort((a, b) => b.equityScore - a.equityScore);
    return uniqueProposals.slice(0, 15);
}
function evaluateCustomTrade(givingIds, receivingIds, rivalName) {
    const unikaPlayers = getUnikaPlayersFull();
    const rivalPlayers = getRivalPlayersFull(rivalName);
    const giving = unikaPlayers.filter(p => givingIds.includes(p.id));
    const receiving = rivalPlayers.filter(p => receivingIds.includes(p.id));
    if (giving.length === 0 || receiving.length === 0) {
        return {
            verdict: 'neutral',
            title: 'Seleziona i giocatori per simulare lo scambio',
            badge: 'In attesa',
            score: 0,
            analysis: 'Seleziona almeno un calciatore da cedere e uno da richiedere per calcolare la fattibilità.',
            negotiationText: ''
        };
    }
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const giveOvrSum = giving.reduce((s, p) => s + (p.ovr || 70), 0);
    const recOvrSum = receiving.reduce((s, p) => s + (p.ovr || 70), 0);
    const ovrDelta = recOvrSum - giveOvrSum;
    const giveFvmSum = giving.reduce((s, p) => s + (p.fvm || p.prezzo_cons || 10), 0);
    const recFvmSum = receiving.reduce((s, p) => s + (p.fvm || p.prezzo_cons || 10), 0);
    const fvmDelta = recFvmSum - giveFvmSum;
    let classicSlotWarning = '';
    if (!isMantra) {
        const giveRolesCount = { P: 0, D: 0, C: 0, A: 0 };
        const recRolesCount = { P: 0, D: 0, C: 0, A: 0 };
        giving.forEach(p => { giveRolesCount[p.role] = (giveRolesCount[p.role] || 0) + 1; });
        receiving.forEach(p => { recRolesCount[p.role] = (recRolesCount[p.role] || 0) + 1; });
        const isRolesMismatched = ['P', 'D', 'C', 'A'].some(r => giveRolesCount[r] !== recRolesCount[r]);
        if (isRolesMismatched) {
            const gSummary = Object.keys(giveRolesCount).filter(r => giveRolesCount[r] > 0).map(r => `${giveRolesCount[r]}${r}`).join('+');
            const rSummary = Object.keys(recRolesCount).filter(r => recRolesCount[r] > 0).map(r => `${recRolesCount[r]}${r}`).join('+');
            classicSlotWarning = `⚠️ <b>Vincolo Regolamento Classic:</b> Questo scambio coinvolge ruoli non corrispondenti (${gSummary} per ${rSummary}). Nelle leghe Classic gli slot di rosa sono bloccati (3P-8D-8C-6A) e richiedono scambi pari-ruolo.`;
        }
    }
    let verdict = 'fair';
    let title = '🤝 Scambio Equo Win-Win';
    let badge = 'Equilibrato';
    let analysis = '';
    if (ovrDelta >= 6 || fvmDelta >= 35) {
        verdict = 'unrealistic';
        title = '⛔ Proposta Troppo Sbilanciata (Rifiuto Probabile)';
        badge = 'Improbabile';
        analysis = `Stai chiedendo troppo valore rispetto a quello che offri (+${ovrDelta} OVR, +${fvmDelta} FVM). Il manager di ${rivalName} rifiuterà a meno che tu non aggiunga una contropartita migliore.`;
    } else if (ovrDelta >= 2 || fvmDelta >= 12) {
        verdict = 'win';
        title = '🌟 Ottimo Affare per la Tua Rosa';
        badge = 'Favorevole';
        analysis = `Scambio vantaggioso per te (+${ovrDelta} OVR). Se ${rivalName} ha necessità nei ruoli che stai cedendo, ha ottime possibilità di andare a buon fine.`;
    } else if (ovrDelta <= -5 || fvmDelta <= -30) {
        verdict = 'lose';
        title = '⚠️ Scambio Svantaggioso per la Tua Rosa';
        badge = 'Sconsigliato';
        analysis = `Stai cedendo troppo talento (${giveOvrSum} OVR contro ${recOvrSum} OVR). Salvo gravi emergenze di ruolo, stai regalando valore al tuo avversario.`;
    } else {
        verdict = 'fair';
        title = '🤝 Scambio Equo & Trattabile';
        badge = 'Win-Win';
        analysis = `I valori in campo sono molto allineati (scarto di appena ${Math.abs(ovrDelta)} punti OVR). Entrambe le squadre possono trarne reciproco beneficio.`;
    }
    if (classicSlotWarning) {
        analysis = `${classicSlotWarning}<br><br>${analysis}`;
    }
    const givingNames = giving.map(p => `${p.name} (${p.team}, ${isMantra ? (p.mantra || p.role) : p.role})`).join(' + ');
    const receivingNames = receiving.map(p => `${p.name} (${p.team}, ${isMantra ? (p.mantra || p.role) : p.role})`).join(' + ');
    const giveRoles = [...new Set(giving.map(p => isMantra ? (p.mantra || p.role) : p.role))].join(' / ');
    const recRoles = [...new Set(receiving.map(p => isMantra ? (p.mantra || p.role) : p.role))].join(' / ');
    const msg = `Ciao! Stavo dando un'occhiata alle nostre rose per il Fanta${isMantra ? ' (Modalità Mantra)' : ''}. 
Ho visto che potresti avere bisogno di rinforzare i ruoli: *${giveRoles}*. 
Cosa ne diresti di uno scambio:
➡️ Ti do: *${givingNames}*
⬅️ Mi daresti: *${receivingNames}*
Secondo me è un'ottima operazione Win-Win per entrambi perché sistemi i ruoli di cui hai bisogno e io posso coprire *${recRoles}*. Fammi sapere cosa ne pensi! ⚽`;
    return {
        verdict,
        title,
        badge,
        giveOvrSum,
        recOvrSum,
        ovrDelta,
        giveFvmSum,
        recFvmSum,
        fvmDelta,
        analysis,
        negotiationText: msg
    };
}
function executeTrade(givingIds, receivingIds, rivalName) {
    if (!givingIds.length || !receivingIds.length || !rivalName) {
        alert("Seleziona almeno un calciatore da cedere e uno da ricevere!");
        return;
    }
    if (!confirm(`Sei sicuro di voler ufficializzare questo scambio con ${rivalName}?\n\nLe rose di entrambe le squadre verranno aggiornate istantaneamente.`)) {
        return;
    }
    const unikaPlayers = getUnikaPlayersFull();
    const rivalPlayers = getRivalPlayersFull(rivalName);
    const giving = unikaPlayers.filter(p => givingIds.includes(p.id));
    const receiving = rivalPlayers.filter(p => receivingIds.includes(p.id));
    giving.forEach(p => {
        const slotKey = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (State.slots[p.role] ? p.role : 'C');
        const idx = State.slots[slotKey].players.findIndex(x => x.id === p.id);
        if (idx !== -1) {
            State.slots[slotKey].players.splice(idx, 1);
        }
        markPlayerTaken(p.id, rivalName, p.paidPrice || p.prezzo_cons || 1);
    });
    receiving.forEach(p => {
        unmarkPlayerTaken(p.id);
        const slotKey = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (State.slots[p.role] ? p.role : 'C');
        State.slots[slotKey].players.push({ ...p, paidPrice: p.paidPrice || p.prezzo_cons || 1 });
    });
    saveStateToStorage();
    updateAllViews();
    tradeMachineState.givingPlayerIds = [];
    tradeMachineState.receivingPlayerIds = [];
    renderTradeMachineView();
    const toastMsg = `✓ Scambio con ${rivalName} completato con successo!`;
    if (typeof showSyncToast === 'function') {
        showSyncToast(toastMsg);
    } else {
        alert(toastMsg);
    }
}
function setTradeViewMode(mode) {
    tradeMachineState.activeView = mode;
    renderTradeMachineView();
}
function selectTradeRival(rivalName) {
    tradeMachineState.selectedRival = rivalName;
    tradeMachineState.receivingPlayerIds = [];
    renderTradeMachineView();
}
function toggleTradeGiving(playerId) {
    const idx = tradeMachineState.givingPlayerIds.indexOf(playerId);
    if (idx !== -1) tradeMachineState.givingPlayerIds.splice(idx, 1);
    else tradeMachineState.givingPlayerIds.push(playerId);
    renderTradeMachineView();
}
function toggleTradeReceiving(playerId) {
    const idx = tradeMachineState.receivingPlayerIds.indexOf(playerId);
    if (idx !== -1) tradeMachineState.receivingPlayerIds.splice(idx, 1);
    else tradeMachineState.receivingPlayerIds.push(playerId);
    renderTradeMachineView();
}
function loadProposalIntoSimulator(rName, giveIds, recIds) {
    tradeMachineState.selectedRival = rName;
    tradeMachineState.givingPlayerIds = [...giveIds];
    tradeMachineState.receivingPlayerIds = [...recIds];
    tradeMachineState.activeView = 'custom';
    renderTradeMachineView();
}
function copyTradeNegotiationText() {
    const txt = document.getElementById('tradeNegotiationTextarea')?.value;
    if (!txt) return;
    navigator.clipboard.writeText(txt).then(() => {
        alert("✓ Messaggio di negoziazione copiato negli appunti! Incollalo su WhatsApp per avviare la trattativa.");
    }).catch(() => {
        prompt("Copia manualmente il messaggio:", txt);
    });
}
function renderTradeMachineView() {
    const container = document.getElementById('viewTradeMachine');
    if (!container) return;
    const rivalsList = Object.keys(State.rivals || {});
    if (!tradeMachineState.selectedRival && rivalsList.length > 0) {
        tradeMachineState.selectedRival = rivalsList[0];
    }
    const unikaPlayers = getUnikaPlayersFull();
    const rivalName = tradeMachineState.selectedRival;
    const rivalPlayers = rivalName ? getRivalPlayersFull(rivalName) : [];
    let html = `
        <div class="trade-machine-container">
            <div class="trade-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:32px;">🔄</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:22px;color:var(--accent-cyan);">AI Trade Machine (Mercato Scambi)</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            Algoritmo avanzato di negoziazione, asimmetrie di rosa, calcolo win-win e copywriter WhatsApp
                        </div>
                    </div>
                </div>
                <div class="trade-tab-toggle">
                    <button class="trade-toggle-btn ${tradeMachineState.activeView === 'auto' ? 'active' : ''}" onclick="setTradeViewMode('auto')">
                        ⚡ Scambi Consigliati AI
                    </button>
                    <button class="trade-toggle-btn ${tradeMachineState.activeView === 'custom' ? 'active' : ''}" onclick="setTradeViewMode('custom')">
                        ⚖️ Simulatore Trattativa Custom
                    </button>
                </div>
            </div>
    `;
    if (unikaPlayers.length === 0) {
        html += `
            <div class="trade-empty-state">
                <span style="font-size:40px;">📋</span>
                <h3 style="margin:10px 0 6px 0;color:#fff;">La tua rosa è attualmente vuota</h3>
                <p style="color:var(--text-muted);font-size:13px;max-width:500px;margin:0 auto 16px auto;">
                    Acquista qualche calciatore all'asta o carica una rosa da file CSV per iniziare a scovare opportunità di scambio con i rivali.
                </p>
                <button class="btn-action" style="background:var(--accent-cyan);color:#000;font-weight:700;" onclick="openCsvRosterImportModal('my_team')">
                    📂 Carica Rosa da CSV
                </button>
            </div>
        </div>`;
        container.innerHTML = html;
        return;
    }
    if (tradeMachineState.activeView === 'auto') {
        const autoProposals = generateAutoTradeProposals();
        let proposalsHtml = '';
        if (autoProposals.length === 0) {
            proposalsHtml = `
                <div style="grid-column: 1 / -1; padding:30px; text-align:center; background:rgba(255,255,255,0.02); border-radius:12px; border:1px dashed rgba(255,255,255,0.1);">
                    <div style="font-size:24px;margin-bottom:6px;">🔎</div>
                    <div style="font-weight:700;color:#fff;">Nessuno scambio automatico ad alta compatibilità trovato al momento</div>
                    <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Assegna più calciatori alle rose rivali o prova il simulatore custom per impostare una trattativa manuale.</div>
                </div>
            `;
        } else {
            proposalsHtml = autoProposals.map((prop, idx) => {
                const give = prop.giving[0];
                const rec = prop.receiving[0];
                return `
                    <div class="trade-card">
                        <div class="trade-card-header">
                            <span class="trade-rival-tag">👥 ${prop.rivalName}</span>
                            <span class="trade-equity-badge ${prop.equityScore >= 85 ? 'top' : ''}">
                                ${prop.equityScore}% Win-Win
                            </span>
                        </div>
                        <div class="trade-exchange-row">
                            <!-- CEDI -->
                            <div class="trade-player-box give">
                                <span class="trade-box-label">Tu Cedi</span>
                                <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                                    ${renderTradePlayerBadge(give)}
                                    <b style="font-size:13px;color:#fff;">${give.name}</b>
                                </div>
                                <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${give.team} • OVR ${give.ovr}</div>
                            </div>
                            <div class="trade-exchange-arrow">⇄</div>
                            <!-- RICEVI -->
                            <div class="trade-player-box receive">
                                <span class="trade-box-label">Tu Ricevi</span>
                                <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                                    ${renderTradePlayerBadge(rec)}
                                    <b style="font-size:13px;color:#38bdf8;">${rec.name}</b>
                                </div>
                                <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${rec.team} • OVR ${rec.ovr}</div>
                            </div>
                        </div>
                        <div class="trade-rationale">
                            💡 ${prop.rationale}
                        </div>
                        <div class="trade-card-footer">
                            <button class="trade-action-btn secondary" onclick="loadProposalIntoSimulator('${prop.rivalName}', [${give.id}], [${rec.id}])">
                                ⚖️ Negozia
                            </button>
                            <button class="trade-action-btn primary" onclick="executeTrade([${give.id}], [${rec.id}], '${prop.rivalName}')">
                                ✓ Applica Scambio
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }
        html += `
            <div class="trade-auto-grid">
                ${proposalsHtml}
            </div>
        </div>`;
    } else {
        const evaluation = evaluateCustomTrade(tradeMachineState.givingPlayerIds, tradeMachineState.receivingPlayerIds, rivalName);
        const rivalOptionsHtml = rivalsList.map(rName => {
            return `<option value="${rName}" ${rName === rivalName ? 'selected' : ''}>👥 ${rName}</option>`;
        }).join('');
        const unikaListHtml = unikaPlayers.map(p => {
            const isSelected = tradeMachineState.givingPlayerIds.includes(p.id);
            return `
                <div class="trade-pick-item ${isSelected ? 'selected' : ''}" onclick="toggleTradeGiving(${p.id})">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} style="pointer-events:none;">
                    ${renderTradePlayerBadge(p)}
                    <div style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        <b style="font-size:12px;color:#fff;">${p.name}</b>
                        <span style="font-size:10.5px;color:var(--text-muted);">(${p.team})</span>
                    </div>
                    <span class="ovr-pill" style="font-size:11px;">OVR ${p.ovr}</span>
                </div>
            `;
        }).join('');
        const rivalListHtml = rivalPlayers.length === 0 ? `
            <div style="padding:20px;text-align:center;color:var(--text-muted);font-size:12px;">
                Nessun calciatore assegnato a questa squadra.
            </div>
        ` : rivalPlayers.map(p => {
            const isSelected = tradeMachineState.receivingPlayerIds.includes(p.id);
            return `
                <div class="trade-pick-item ${isSelected ? 'selected' : ''}" onclick="toggleTradeReceiving(${p.id})">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} style="pointer-events:none;">
                    ${renderTradePlayerBadge(p)}
                    <div style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        <b style="font-size:12px;color:#fff;">${p.name}</b>
                        <span style="font-size:10.5px;color:var(--text-muted);">(${p.team})</span>
                    </div>
                    <span class="ovr-pill" style="font-size:11px;">OVR ${p.ovr}</span>
                </div>
            `;
        }).join('');
        html += `
            <div class="trade-simulator-layout">
                <!-- COLONNA LA TUA ROSA -->
                <div class="trade-sim-col">
                    <div class="trade-col-header">
                        <span style="font-size:13px;font-weight:700;color:var(--accent-cyan);">🌟 La Tua Rosa (Cedi)</span>
                        <span style="font-size:11px;color:var(--text-muted);">${tradeMachineState.givingPlayerIds.length} selezionati</span>
                    </div>
                    <div class="trade-sim-list">
                        ${unikaListHtml}
                    </div>
                </div>
                <!-- PANNELLO ANALISI CENTRALE -->
                <div class="trade-eval-panel">
                    <div style="margin-bottom:12px;">
                        <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;margin-bottom:4px;">Seleziona Squadra Rivale</label>
                        <select style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:6px 10px;font-size:12.5px;" onchange="selectTradeRival(this.value)">
                            ${rivalOptionsHtml}
                        </select>
                    </div>
                    <!-- CARD VERDETTO -->
                    <div class="trade-verdict-card ${evaluation.verdict}">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                            <span style="font-weight:800;font-size:14px;color:#fff;">${evaluation.title}</span>
                            <span class="trade-verdict-badge">${evaluation.badge}</span>
                        </div>
                        <div style="font-size:12px;color:#e2e8f0;line-height:1.4;">${evaluation.analysis}</div>
                        ${evaluation.giveOvrSum ? `
                            <div style="display:flex;justify-content:space-around;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.08);font-size:11.5px;">
                                <div>OVR Ceduto: <b>${evaluation.giveOvrSum}</b></div>
                                <div style="color:${evaluation.ovrDelta >= 0 ? '#34d399' : '#f87171'};font-weight:800;">
                                    Delta: ${evaluation.ovrDelta >= 0 ? '+' : ''}${evaluation.ovrDelta} OVR
                                </div>
                                <div>OVR Ricevuto: <b>${evaluation.recOvrSum}</b></div>
                            </div>
                        ` : ''}
                    </div>
                    <!-- COPYWRITER WHATSAPP -->
                    ${evaluation.negotiationText ? `
                        <div style="margin-top:14px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                <label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">💬 Copywriter Trattativa WhatsApp</label>
                                <button class="btn-action" style="font-size:10.5px;padding:2px 8px;" onclick="copyTradeNegotiationText()">📋 Copia</button>
                            </div>
                            <textarea id="tradeNegotiationTextarea" class="trade-textarea" rows="5" readonly>${evaluation.negotiationText}</textarea>
                        </div>
                    ` : ''}
                    <div style="margin-top:16px;">
                        <button class="btn-action" style="width:100%;padding:10px;font-size:13px;font-weight:800;background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#000;border:none;box-shadow:0 4px 15px rgba(0,242,254,0.3);${(!tradeMachineState.givingPlayerIds.length || !tradeMachineState.receivingPlayerIds.length) ? 'opacity:0.4;cursor:not-allowed;' : ''}" ${(!tradeMachineState.givingPlayerIds.length || !tradeMachineState.receivingPlayerIds.length) ? 'disabled' : ''} onclick="executeTrade(tradeMachineState.givingPlayerIds, tradeMachineState.receivingPlayerIds, '${rivalName}')">
                            ✓ Ufficializza Scambio in Rosa
                        </button>
                    </div>
                </div>
                <!-- COLONNA RIVALE -->
                <div class="trade-sim-col">
                    <div class="trade-col-header">
                        <span style="font-size:13px;font-weight:700;color:#38bdf8;">👥 Rosa di ${rivalName} (Chiedi)</span>
                        <span style="font-size:11px;color:var(--text-muted);">${tradeMachineState.receivingPlayerIds.length} selezionati</span>
                    </div>
                    <div class="trade-sim-list">
                        ${rivalListHtml}
                    </div>
                </div>
            </div>
        </div>`;
    }
    container.innerHTML = html;
}
window.renderTradeMachineView = renderTradeMachineView;
window.setTradeViewMode = setTradeViewMode;
window.selectTradeRival = selectTradeRival;
window.toggleTradeGiving = toggleTradeGiving;
window.toggleTradeReceiving = toggleTradeReceiving;
window.loadProposalIntoSimulator = loadProposalIntoSimulator;
window.copyTradeNegotiationText = copyTradeNegotiationText;
window.executeTrade = executeTrade;