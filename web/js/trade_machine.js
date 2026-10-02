// --- trade_machine.js ---
// AI Trade Machine per Fanta Master AI 2026/27
// Analisi asimmetrie, generatore scambi Win-Win, simulatore trattativa e copywriter WhatsApp

let tradeMachineState = {
    selectedRival: null,
    givingPlayerIds: [],
    receivingPlayerIds: [],
    activeView: 'auto', // 'auto' | 'custom' | 'sandbox'
    sandboxSearchGive: '',
    sandboxSearchRec: '',
    sandboxRoleGive: 'ALL',
    sandboxRoleRec: 'ALL'
};

function getPlayerByIdUnified(id) {
    if (typeof PLAYERS !== 'undefined' && Array.isArray(PLAYERS)) {
        const found = PLAYERS.find(p => p.id === id);
        if (found) return found;
    }
    const my = getMyTeamPlayersFull().find(p => p.id === id);
    if (my) return my;
    for (const rName in (State.rivals || {})) {
        const riv = getRivalPlayersFull(rName).find(p => p.id === id);
        if (riv) return riv;
    }
    return null;
}


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

// Analisi punti di forza e carenze di una rosa (Classic o Mantra)
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

    // Modalità Classic
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
        
        // Classic target: P:3, D:8, C:8, A:6
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

// Generatore automatico di proposte Win-Win
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
            // ==========================================
            // MODALITÀ CLASSIC: SCAMBI RIGOROSAMENTE PARI-RUOLO (P-P, D-D, C-C, A-A)
            // ==========================================
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

                        // Scambio pari-ruolo equilibrato (-4 <= ovrDiff <= 4)
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
            // ==========================================
            // MODALITÀ MANTRA: SCAMBI STRUTTURALI & TATTICI
            // ==========================================
            const mantraCategories = ['DC', 'TER', 'EST', 'MED', 'CC', 'TREQ', 'PUNTA'];
            
            mantraCategories.forEach(giveCat => {
                mantraCategories.forEach(recCat => {
                    const giveStat = unikaStats[giveCat];
                    const recStat = rStats[recCat];
                    if (!giveStat || !recStat) return;

                    // Nel Mantra lo scambio può essere pari-categoria O cross-categoria solo in caso di asimmetria
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

    // Filtra duplicati mantenendo il migliore
    const seenCombos = new Set();
    const uniqueProposals = [];
    proposals.forEach(p => {
        const key = `${p.rivalName}_${p.giving[0].id}_${p.receiving[0].id}`;
        if (!seenCombos.has(key)) {
            seenCombos.add(key);
            uniqueProposals.push(p);
        }
    });

    // Ordina per miglior punteggio di equità ed equilibrio
    uniqueProposals.sort((a, b) => b.equityScore - a.equityScore);
    return uniqueProposals.slice(0, 15);
}

// Valutatore simulazione trattativa custom & sandbox potenziato con AI Predittiva
function evaluateCustomTrade(givingIds, receivingIds, rivalName) {
    const giving = givingIds.map(id => getPlayerByIdUnified(id)).filter(Boolean);
    const receiving = receivingIds.map(id => getPlayerByIdUnified(id)).filter(Boolean);

    if (giving.length === 0 || receiving.length === 0) {
        return {
            verdict: 'neutral',
            title: 'Seleziona i giocatori per simulare lo scambio',
            badge: 'In attesa',
            score: 0,
            deltaPts: 0,
            deltaFvm: 0,
            deltaOvr: 0,
            deltaFloor: 0,
            deltaCeiling: 0,
            analysis: 'Seleziona almeno un calciatore da cedere e uno da richiedere per calcolare la fattibilità, l\'impatto sui punti residui e la stabilità.',
            negotiationText: ''
        };
    }

    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const remainingRounds = 33; // Turni rimanenti G6 - G38

    function calcBundle(playersList) {
        let totPts = 0;
        let totFvm = 0;
        let totOvr = 0;
        let fragPen = 0;
        let sumFloor = 0;
        let sumCeiling = 0;
        playersList.forEach(p => {
            const xfm = parseFloat(p.xfm || p.fm_2627 || p.fm || 6.0);
            const tit = parseFloat(p.titolarita || 60) / 100.0;
            const tier = p.fragility_tier || 'ROCCIA';
            let injRate = 0.02;
            if (tier === 'CRISTALLO') injRate = 0.28;
            else if (tier === 'FRAGILE') injRate = 0.16;
            else if (tier === 'ATTENZIONE') injRate = 0.08;

            totPts += xfm * tit * remainingRounds * (1.0 - injRate);
            totFvm += parseFloat(p.fvm || p.prezzo_cons || 10);
            totOvr += (p.ovr || 70);
            fragPen += injRate;
            sumFloor += parseFloat(p.floor || (p.role === 'P' ? 4.0 : 5.0));
            sumCeiling += parseFloat(p.ceiling || 8.0);
        });
        return { totPts, totFvm, totOvr, fragPen, sumFloor, sumCeiling };
    }

    const giveBundle = calcBundle(giving);
    const recBundle = calcBundle(receiving);

    const deltaPts = Math.round((recBundle.totPts - giveBundle.totPts) * 10) / 10;
    const deltaFvm = Math.round((recBundle.totFvm - giveBundle.totFvm) * 10) / 10;
    const deltaOvr = recBundle.totOvr - giveBundle.totOvr;
    const deltaFloor = Math.round((recBundle.sumFloor - giveBundle.sumFloor) * 10) / 10;
    const deltaCeiling = Math.round((recBundle.sumCeiling - giveBundle.sumCeiling) * 10) / 10;

    // Controllo Regolamentare Ruoli per Classic
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
            classicSlotWarning = `⚠️ <b>Vincolo Classic:</b> Scambio asimmetrico per ruoli (${gSummary} per ${rSummary}). Nelle leghe Classic gli slot sono fissi (3P-8D-8C-6A) e richiedono pari-ruolo.`;
        }
    }

    let verdict = 'fair';
    let title = '🤝 Scambio Equo Win-Win';
    let badge = 'Equilibrato';
    let analysis = '';

    if (deltaPts >= 12.0 || deltaFvm >= 30) {
        verdict = 'win';
        title = '🚀 Affare d\'Oro: Accetta Subito!';
        badge = 'Consigliatissimo';
        analysis = `Guadagni un impressionante surplus di <b>+${deltaPts} punti stimati</b> da qui a fine stagione e +${deltaFvm} crediti FVM. L'algoritmo predittivo approva con entusiasmo.`;
    } else if (deltaPts >= 4.0 || deltaOvr >= 3) {
        verdict = 'win';
        title = '🌟 Scambio Favorevole per la Tua Rosa';
        badge = 'Favorevole';
        analysis = `Operazione vantaggiosa (+${deltaPts} xPoints residui). La combinazione in entrata garantisce maggiore continuità o un Floor più affidabile.`;
    } else if (deltaPts <= -10.0 || deltaOvr <= -6) {
        verdict = 'lose';
        title = '⛔ Rifiuta: Scambio Molto Sfavorevole';
        badge = 'Sconsigliato';
        analysis = `Stai svendendo potenziale: perdi stimati <b>${Math.abs(deltaPts)} punti</b> fino alla 38ª giornata e ${Math.abs(deltaOvr)} punti OVR. Non farti ingolosire senza adeguate contropartite.`;
    } else if (deltaPts <= -3.5) {
        verdict = 'lose';
        title = '⚠️ Leggermente Sfavorevole';
        badge = 'Rischioso';
        analysis = `Perdi circa ${Math.abs(deltaPts)} punti attesi. Accetta solo se risolve un'emergenza tassativa di titolarità in un reparto scoperto.`;
    } else {
        verdict = 'fair';
        title = '🤝 Scambio Equilibrato & Win-Win';
        badge = 'Bilanciato';
        analysis = `Valori matematici quasi identici (scarto minimo di appena ${Math.abs(deltaPts)} punti). L'affare ha senso per entrambe le parti in base alle coperture di ruolo.`;
    }

    if (recBundle.fragPen > giveBundle.fragPen + 0.12) {
        analysis += `<br><span style="color:#f87171;font-weight:700;">🩺 Alert Medico:</span> Stai assorbendo un pacchetto con fragilità clinica più elevata. Prevedi un ricambio in panchina.`;
    }

    if (classicSlotWarning) {
        analysis = `${classicSlotWarning}<br><br>${analysis}`;
    }

    // Generatore Messaggio di Negoziazione per WhatsApp
    const givingNames = giving.map(p => `${p.name} (${p.team}, ${isMantra ? (p.mantra || p.role) : p.role})`).join(' + ');
    const receivingNames = receiving.map(p => `${p.name} (${p.team}, ${isMantra ? (p.mantra || p.role) : p.role})`).join(' + ');
    const giveRoles = [...new Set(giving.map(p => isMantra ? (p.mantra || p.role) : p.role))].join(' / ');
    const recRoles = [...new Set(receiving.map(p => isMantra ? (p.mantra || p.role) : p.role))].join(' / ');

    const msg = `Ciao! Stavo valutando i valori di mercato e le statistiche per il Fanta${isMantra ? ' (Mantra)' : ''}. 
Ho notato che potresti beneficiare di rinforzi nei ruoli: *${giveRoles}*. 

Cosa ne diresti di imbastire questo scambio:
➡️ Ti do: *${givingNames}*
⬅️ Mi daresti: *${receivingNames}*

I dati statistici e gli xFM mostrano che l'operazione è molto equilibrata e risponde esattamente ai bisogni tattici di entrambe le squadre (*${recRoles}* per me, *${giveRoles}* per te). Che ne pensi? ⚽`;

    return {
        verdict,
        title,
        badge,
        giveOvrSum: giveBundle.totOvr,
        recOvrSum: recBundle.totOvr,
        ovrDelta: deltaOvr,
        giveFvmSum: giveBundle.totFvm,
        recFvmSum: recBundle.totFvm,
        fvmDelta: deltaFvm,
        deltaPts,
        ptsGiven: Math.round(giveBundle.totPts * 10) / 10,
        ptsRec: Math.round(recBundle.totPts * 10) / 10,
        deltaFloor,
        deltaCeiling,
        analysis,
        negotiationText: msg
    };
}

// Applica lo scambio ufficiale tra la Mia Rosa e Rivale
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

    // 1. Rimuovi i calciatori ceduti dalla tua rosa
    giving.forEach(p => {
        const slotKey = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (State.slots[p.role] ? p.role : 'C');
        const idx = State.slots[slotKey].players.findIndex(x => x.id === p.id);
        if (idx !== -1) {
            State.slots[slotKey].players.splice(idx, 1);
        }
        // Assegnali al rivale
        markPlayerTaken(p.id, rivalName, p.paidPrice || p.prezzo_cons || 1);
    });

    // 2. Rimuovi i calciatori ricevuti dal rivale
    receiving.forEach(p => {
        unmarkPlayerTaken(p.id);
        const slotKey = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (State.slots[p.role] ? p.role : 'C');
        State.slots[slotKey].players.push({ ...p, paidPrice: p.paidPrice || p.prezzo_cons || 1 });
    });

    saveStateToStorage();
    updateAllViews();

    // Reset selezioni
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

// Controller e Rendering Interfaccia
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

function setTradeSandboxFilter(side, query) {
    if (side === 'give') tradeMachineState.sandboxSearchGive = query.toLowerCase();
    else tradeMachineState.sandboxSearchRec = query.toLowerCase();
    renderTradeMachineView();
}

function setTradeSandboxRole(side, role) {
    if (side === 'give') tradeMachineState.sandboxRoleGive = role;
    else tradeMachineState.sandboxRoleRec = role;
    renderTradeMachineView();
}

function resetTradeSelections() {
    tradeMachineState.givingPlayerIds = [];
    tradeMachineState.receivingPlayerIds = [];
    renderTradeMachineView();
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

    // Se la rosa è vuota e l'utente era su 'auto', default intelligente a 'sandbox'
    if (unikaPlayers.length === 0 && tradeMachineState.activeView === 'auto') {
        tradeMachineState.activeView = 'sandbox';
    }

    // Header & Toggle Tabs
    let html = `
        <div class="trade-machine-container">
            <div class="trade-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:32px;">🔄</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:22px;color:var(--accent-cyan);">AI Trade Machine (Mercato Scambi)</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            Valutatore Matematico di Scambi: Delta xPoints G6-G38, Shift Floor/Ceiling, Rischio Fragilità e WhatsApp Copywriter
                        </div>
                    </div>
                </div>

                <div class="trade-tab-toggle" style="display:flex;flex-wrap:wrap;gap:6px;">
                    <button class="trade-toggle-btn ${tradeMachineState.activeView === 'sandbox' ? 'active' : ''}" onclick="setTradeViewMode('sandbox')">
                        🌐 Sandbox Libera Serie A
                    </button>
                    <button class="trade-toggle-btn ${tradeMachineState.activeView === 'custom' ? 'active' : ''}" onclick="setTradeViewMode('custom')">
                        ⚖️ Rosa vs Rivale
                    </button>
                    <button class="trade-toggle-btn ${tradeMachineState.activeView === 'auto' ? 'active' : ''}" onclick="setTradeViewMode('auto')">
                        ⚡ Consigli Automatici AI
                    </button>
                </div>
            </div>
    `;

    if (tradeMachineState.activeView === 'auto') {
        if (unikaPlayers.length === 0) {
            html += `
                <div class="trade-empty-state">
                    <span style="font-size:40px;">📋</span>
                    <h3 style="margin:10px 0 6px 0;color:#fff;">La tua rosa è attualmente vuota</h3>
                    <p style="color:var(--text-muted);font-size:13px;max-width:500px;margin:0 auto 16px auto;">
                        Acquista qualche calciatore all'asta o carica una rosa da file CSV per iniziare a scovare opportunità automatiche di scambio con i rivali.
                    </p>
                    <div style="display:flex;gap:10px;justify-content:center;">
                        <button class="btn-action" style="background:var(--accent-cyan);color:#000;font-weight:700;" onclick="openCsvRosterImportModal('my_team')">
                            📂 Carica Rosa da CSV
                        </button>
                        <button class="btn-action" style="background:rgba(255,255,255,0.1);color:#fff;" onclick="setTradeViewMode('sandbox')">
                            🌐 Usa la Sandbox Libera Serie A
                        </button>
                    </div>
                </div>
            </div>`;
            container.innerHTML = html;
            return;
        }

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
    } else if (tradeMachineState.activeView === 'custom') {
        // VISTA SIMULATORE ROSA VS RIVALE
        if (unikaPlayers.length === 0) {
            html += `
                <div class="trade-empty-state">
                    <span style="font-size:40px;">📋</span>
                    <h3 style="margin:10px 0 6px 0;color:#fff;">La tua rosa è attualmente vuota</h3>
                    <p style="color:var(--text-muted);font-size:13px;max-width:500px;margin:0 auto 16px auto;">
                        Per confrontare direttamente la tua squadra contro un rivale devi prima caricare la tua rosa, oppure puoi usare il <b>Sandbox Libero Serie A</b> per testare qualsiasi scambio all'istante!
                    </p>
                    <div style="display:flex;gap:10px;justify-content:center;">
                        <button class="btn-action" style="background:var(--accent-cyan);color:#000;font-weight:700;" onclick="openCsvRosterImportModal('my_team')">
                            📂 Carica Rosa da CSV
                        </button>
                        <button class="btn-action" style="background:rgba(255,255,255,0.1);color:#fff;" onclick="setTradeViewMode('sandbox')">
                            🌐 Vai al Sandbox Serie A
                        </button>
                    </div>
                </div>
            </div>`;
            container.innerHTML = html;
            return;
        }

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

                    <!-- CARD VERDETTO CON PREDICTIVE METRICS -->
                    <div class="trade-verdict-card ${evaluation.verdict}">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                            <span style="font-weight:800;font-size:14px;color:#fff;">${evaluation.title}</span>
                            <span class="trade-verdict-badge">${evaluation.badge}</span>
                        </div>
                        <div style="font-size:12px;color:#e2e8f0;line-height:1.45;">${evaluation.analysis}</div>

                        ${evaluation.giveOvrSum ? `
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.08);font-size:11px;">
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Delta Punti (G6-G38):</div>
                                    <b style="font-size:13px;color:${evaluation.deltaPts >= 0 ? '#34d399' : '#f87171'};">${evaluation.deltaPts >= 0 ? '+' : ''}${evaluation.deltaPts} pt</b>
                                </div>
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Delta FVM (Crediti):</div>
                                    <b style="font-size:13px;color:${evaluation.fvmDelta >= 0 ? '#38bdf8' : '#fbbf24'};">${evaluation.fvmDelta >= 0 ? '+' : ''}${evaluation.fvmDelta} CR</b>
                                </div>
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Floor (Min Senza Bonus):</div>
                                    <b style="font-size:12px;color:#fff;">${evaluation.deltaFloor >= 0 ? '+' : ''}${evaluation.deltaFloor}</b>
                                </div>
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Ceiling (Potenziale Max):</div>
                                    <b style="font-size:12px;color:#fff;">${evaluation.deltaCeiling >= 0 ? '+' : ''}${evaluation.deltaCeiling}</b>
                                </div>
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

                    <div style="margin-top:16px;display:flex;gap:8px;">
                        <button class="btn-action" style="flex:1;padding:10px;font-size:13px;font-weight:800;background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#000;border:none;box-shadow:0 4px 15px rgba(0,242,254,0.3);${(!tradeMachineState.givingPlayerIds.length || !tradeMachineState.receivingPlayerIds.length) ? 'opacity:0.4;cursor:not-allowed;' : ''}" ${(!tradeMachineState.givingPlayerIds.length || !tradeMachineState.receivingPlayerIds.length) ? 'disabled' : ''} onclick="executeTrade(tradeMachineState.givingPlayerIds, tradeMachineState.receivingPlayerIds, '${rivalName}')">
                            ✓ Ufficializza Scambio
                        </button>
                        <button class="btn-action" style="background:rgba(255,255,255,0.08);color:#cbd5e1;padding:10px;" onclick="resetTradeSelections()" title="Azzera selezioni">
                            ✕
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
    } else {
        // VISTA SANDBOX LIBERA SERIE A (QUALSIASI CALCIATORE)
        const evaluation = evaluateCustomTrade(tradeMachineState.givingPlayerIds, tradeMachineState.receivingPlayerIds, "Rivale Sandbox");
        const allPlayers = (typeof PLAYERS !== 'undefined' && Array.isArray(PLAYERS)) ? PLAYERS : [];

        // Filtro Cedi (Give)
        const giveRole = tradeMachineState.sandboxRoleGive || 'ALL';
        const giveQuery = tradeMachineState.sandboxSearchGive || '';
        const filteredGive = allPlayers.filter(p => {
            if (giveRole !== 'ALL' && p.role !== giveRole) return false;
            if (giveQuery && !p.name.toLowerCase().includes(giveQuery) && !p.team.toLowerCase().includes(giveQuery)) return false;
            return true;
        }).slice(0, 40);

        // Filtro Ricevi (Rec)
        const recRole = tradeMachineState.sandboxRoleRec || 'ALL';
        const recQuery = tradeMachineState.sandboxSearchRec || '';
        const filteredRec = allPlayers.filter(p => {
            if (recRole !== 'ALL' && p.role !== recRole) return false;
            if (recQuery && !p.name.toLowerCase().includes(recQuery) && !p.team.toLowerCase().includes(recQuery)) return false;
            return true;
        }).slice(0, 40);

        const renderSandboxRow = (p, isGive) => {
            const isSelected = isGive ? tradeMachineState.givingPlayerIds.includes(p.id) : tradeMachineState.receivingPlayerIds.includes(p.id);
            const toggleFn = isGive ? `toggleTradeGiving(${p.id})` : `toggleTradeReceiving(${p.id})`;
            return `
                <div class="trade-pick-item ${isSelected ? 'selected' : ''}" onclick="${toggleFn}">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} style="pointer-events:none;">
                    ${renderTradePlayerBadge(p)}
                    <div style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        <b style="font-size:12px;color:#fff;">${p.name}</b>
                        <span style="font-size:10.5px;color:var(--text-muted);">(${p.team})</span>
                    </div>
                    <div style="text-align:right;">
                        <span class="ovr-pill" style="font-size:10px;">OVR ${p.ovr}</span>
                        <div style="font-size:9.5px;color:var(--accent-cyan);margin-top:1px;">FVM ${p.fvm || p.prezzo_cons || 1}</div>
                    </div>
                </div>
            `;
        };

        const renderRolePills = (currentRole, side) => {
            return ['ALL', 'P', 'D', 'C', 'A'].map(r => `
                <button style="border:none;background:${currentRole === r ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.06)'};color:${currentRole === r ? '#000' : '#cbd5e1'};font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;cursor:pointer;" onclick="setTradeSandboxRole('${side}', '${r}')">
                    ${r === 'ALL' ? 'Tutti' : r}
                </button>
            `).join('');
        };

        html += `
            <div class="trade-simulator-layout">
                <!-- COLONNA CEDI (SANDBOX) -->
                <div class="trade-sim-col">
                    <div class="trade-col-header" style="flex-direction:column;align-items:flex-start;gap:8px;">
                        <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
                            <span style="font-size:13px;font-weight:700;color:var(--accent-cyan);">📤 Calciatori da Cedere (Squadra A)</span>
                            <span style="font-size:11px;color:var(--text-muted);">${tradeMachineState.givingPlayerIds.length} scelti</span>
                        </div>
                        <input type="text" placeholder="🔍 Cerca calciatore o club..." value="${giveQuery}" oninput="setTradeSandboxFilter('give', this.value)" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px 8px;font-size:11.5px;box-sizing:border-box;">
                        <div style="display:flex;gap:4px;">
                            ${renderRolePills(giveRole, 'give')}
                        </div>
                    </div>
                    <div class="trade-sim-list">
                        ${filteredGive.map(p => renderSandboxRow(p, true)).join('')}
                    </div>
                </div>

                <!-- PANNELLO ANALISI CENTRALE -->
                <div class="trade-eval-panel">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <span style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">🎯 Simulazione Aperta Serie A</span>
                        <button class="btn-action" style="font-size:10.5px;padding:2px 8px;background:rgba(255,255,255,0.06);color:#cbd5e1;" onclick="resetTradeSelections()">Azzera</button>
                    </div>

                    <!-- CARD VERDETTO -->
                    <div class="trade-verdict-card ${evaluation.verdict}">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                            <span style="font-weight:800;font-size:14px;color:#fff;">${evaluation.title}</span>
                            <span class="trade-verdict-badge">${evaluation.badge}</span>
                        </div>
                        <div style="font-size:12px;color:#e2e8f0;line-height:1.45;">${evaluation.analysis}</div>

                        ${evaluation.giveOvrSum ? `
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.08);font-size:11px;">
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Delta Punti (G6-G38):</div>
                                    <b style="font-size:13px;color:${evaluation.deltaPts >= 0 ? '#34d399' : '#f87171'};">${evaluation.deltaPts >= 0 ? '+' : ''}${evaluation.deltaPts} pt</b>
                                </div>
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Delta FVM (Crediti):</div>
                                    <b style="font-size:13px;color:${evaluation.fvmDelta >= 0 ? '#38bdf8' : '#fbbf24'};">${evaluation.fvmDelta >= 0 ? '+' : ''}${evaluation.fvmDelta} CR</b>
                                </div>
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Floor (Min Senza Bonus):</div>
                                    <b style="font-size:12px;color:#fff;">${evaluation.deltaFloor >= 0 ? '+' : ''}${evaluation.deltaFloor}</b>
                                </div>
                                <div style="background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                    <div style="color:var(--text-muted);">Ceiling (Potenziale Max):</div>
                                    <b style="font-size:12px;color:#fff;">${evaluation.deltaCeiling >= 0 ? '+' : ''}${evaluation.deltaCeiling}</b>
                                </div>
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
                </div>

                <!-- COLONNA RICEVI (SANDBOX) -->
                <div class="trade-sim-col">
                    <div class="trade-col-header" style="flex-direction:column;align-items:flex-start;gap:8px;">
                        <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
                            <span style="font-size:13px;font-weight:700;color:#38bdf8;">📥 Calciatori da Ricevere (Squadra B)</span>
                            <span style="font-size:11px;color:var(--text-muted);">${tradeMachineState.receivingPlayerIds.length} scelti</span>
                        </div>
                        <input type="text" placeholder="🔍 Cerca calciatore o club..." value="${recQuery}" oninput="setTradeSandboxFilter('rec', this.value)" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:6px;padding:5px 8px;font-size:11.5px;box-sizing:border-box;">
                        <div style="display:flex;gap:4px;">
                            ${renderRolePills(recRole, 'rec')}
                        </div>
                    </div>
                    <div class="trade-sim-list">
                        ${filteredRec.map(p => renderSandboxRow(p, false)).join('')}
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
window.setTradeSandboxFilter = setTradeSandboxFilter;
window.setTradeSandboxRole = setTradeSandboxRole;
window.resetTradeSelections = resetTradeSelections;
