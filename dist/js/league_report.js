function evaluateTeamRoster(teamName, playersList, budgetSpent, budgetTotal = 1000) {
    const roles = { P: [], D: [], C: [], A: [] };
    playersList.forEach(p => {
        const r = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (p.role || 'C');
        if (roles[r]) roles[r].push(p);
    });
    function calcGrade(list, idealCount, minTargetOvr) {
        if (!list || list.length === 0) return 4.0;
        const avg = list.reduce((s, p) => s + (p.ovr || 70), 0) / list.length;
        const countRatio = Math.min(1.0, list.length / idealCount);
        const topCount = list.filter(p => (p.ovr || 0) >= 82).length;
        let grade = 5.0 + ((avg - 72) / 3.2) * 1.5 + (topCount * 0.4);
        if (countRatio < 0.7) grade -= 1.2;
        return Math.max(4.5, Math.min(9.8, Math.round(grade * 10) / 10));
    }
    const gradeP = calcGrade(roles.P, 3, 78);
    const gradeD = calcGrade(roles.D, 8, 77);
    const gradeC = calcGrade(roles.C, 8, 79);
    const gradeA = calcGrade(roles.A, 6, 81);
    const overallGrade = Math.round(((gradeP * 0.15) + (gradeD * 0.20) + (gradeC * 0.30) + (gradeA * 0.35)) * 10) / 10;
    let topPick = null;
    let bestDealScore = -999;
    playersList.forEach(p => {
        const paid = Math.max(1, p.paidPrice || p.price || p.prezzo_cons || 1);
        const cons = Math.max(1, p.prezzo_cons || p.fvm || 1);
        const ovr = p.ovr || 70;
        let dealScore = 0;
        if (paid === 1) {
            if ((p.titolarita || 50) >= 70 && ovr >= 74) {
                dealScore = 15 + (ovr - 70) * 1.5; // Ottimo titolare preso a 1
            } else {
                dealScore = 2; // Tappabuchi a 1, non è il "miglior colpo d'asta"
            }
        } else {
            const savings = cons - paid;
            dealScore = savings * 1.4 + (ovr >= 80 ? (ovr - 78) * 3 : (ovr - 70));
        }
        if (dealScore > bestDealScore) {
            bestDealScore = dealScore;
            topPick = p;
        }
    });
    if (!topPick && playersList.length > 0) {
        topPick = [...playersList].sort((a, b) => (b.ovr || 0) - (a.ovr || 0))[0];
    }
    let flopRisk = null;
    let maxFlopScore = -999;
    playersList.forEach(p => {
        if (topPick && p.id === topPick.id) return; // Un calciatore non può essere sia miglior colpo che flop!
        const paid = Math.max(1, p.paidPrice || p.price || p.prezzo_cons || 1);
        const role = p.role || 'C';
        const isGk = (role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR')));
        const fragVal = p.fragilita_val || '';
        const fragPoints = (fragVal === 'A' || fragVal === 'ALTA') ? 3 : (fragVal === 'M' || fragVal === 'MEDIA') ? 1.5 : 0;
        const titol = p.titolarita || 70;
        let flopScore = 0;
        if (paid < 5) return;
        const cons = Math.max(1, p.prezzo_cons || p.fvm || 1);
        const overpaid = paid - cons;
        flopScore = (paid * 0.8) + (overpaid > 0 ? overpaid * 1.2 : 0) + (fragPoints * 12) + (titol < 65 ? (65 - titol) * 0.8 : 0);
        if (isGk) {
            flopScore *= 0.35;
        }
        if (flopScore > maxFlopScore) {
            maxFlopScore = flopScore;
            flopRisk = p;
        }
    });
    if (!flopRisk && playersList.length > 1) {
        const remaining = playersList.filter(p => !topPick || p.id !== topPick.id);
        const outfielders = remaining.filter(p => p.role !== 'P' && (!p.mantra || !String(p.mantra).toUpperCase().includes('POR')));
        const pool = outfielders.length > 0 ? outfielders : remaining;
        flopRisk = pool.find(p => p.fragilita_val === 'A' || p.fragilita_val === 'ALTA') || pool[0];
    }
    let totalFragScore = 0;
    playersList.forEach(p => {
        const f = p.fragilita_val || '';
        if (f === 'A' || f === 'ALTA') totalFragScore += 3;
        else if (f === 'M' || f === 'MEDIA') totalFragScore += 2;
        else totalFragScore += 1;
    });
    const avgFragility = playersList.length > 0 ? (totalFragScore / playersList.length) : 1;
    const fragilityTag = avgFragility >= 2.2 ? '🔴 Alta (Rischio Infermeria)' : avgFragility >= 1.6 ? '🟡 Media' : '🟢 Bassa (Rocce)';
    return {
        teamName,
        totalPlayers: playersList.length,
        budgetSpent,
        remainingBudget: budgetTotal - budgetSpent,
        gradeP,
        gradeD,
        gradeC,
        gradeA,
        overallGrade,
        topPick,
        flopRisk,
        fragilityTag,
        roles,
        playersList
    };
}
function generateUniqueAiRoast(teamData, allTeams, assignedTemplateIds = new Set()) {
    const { teamName, roles, overallGrade, topPick, flopRisk, gradeP, gradeD, gradeC, gradeA, playersList } = teamData;
    const myName = (typeof State !== 'undefined' && State.teamName) ? State.teamName : 'La Mia Rosa';
    const isMyTeam = (teamName === myName || teamName === 'La Mia Rosa' || teamName === 'Unika');
    if (!playersList || playersList.length === 0) {
        return "Rosa ancora fantasma: sono ancora al buffet dell'asta o stanno leggendo la Guida Gazzetta del 2018.";
    }
    const highFragilityCount = playersList.filter(p => p.fragilita_val === 'A' || p.fragilita_val === 'ALTA').length;
    const penaltyCount = playersList.filter(p => p.is_rigorista_1 || p.is_rigorista_2).length;
    const totalBudget = (typeof State !== 'undefined' && State.budgetTotal) ? State.budgetTotal : 1000;
    const totalSpent = teamData.budgetSpent || playersList.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
    const remaining = totalBudget - totalSpent;
    const listP = (roles && roles.P) ? roles.P : [];
    const listD = (roles && roles.D) ? roles.D : [];
    const listC = (roles && roles.C) ? roles.C : [];
    const listA = (roles && roles.A) ? roles.A : [];
    const spentP = listP.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
    const spentD = listD.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
    const spentC = listC.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
    const spentA = listA.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
    const pctA = totalSpent > 0 ? (spentA / totalSpent) * 100 : 0;
    const pctC = totalSpent > 0 ? (spentC / totalSpent) * 100 : 0;
    const pctD = totalSpent > 0 ? (spentD / totalSpent) * 100 : 0;
    const pctP = totalSpent > 0 ? (spentP / totalSpent) * 100 : 0;
    const bestP = listP.length > 0 ? [...listP].sort((a, b) => (b.paidPrice || b.price || b.ovr || 0) - (a.paidPrice || a.price || a.ovr || 0))[0] : null;
    const bestD = listD.length > 0 ? [...listD].sort((a, b) => (b.paidPrice || b.price || b.ovr || 0) - (a.paidPrice || a.price || a.ovr || 0))[0] : null;
    const bestC = listC.length > 0 ? [...listC].sort((a, b) => (b.paidPrice || b.price || b.ovr || 0) - (a.paidPrice || a.price || a.ovr || 0))[0] : null;
    const bestA = listA.length > 0 ? [...listA].sort((a, b) => (b.paidPrice || b.price || b.ovr || 0) - (a.paidPrice || a.price || a.ovr || 0))[0] : null;
    const topAttackerName = bestA ? bestA.name : 'i centravanti';
    const topMidfielderName = bestC ? bestC.name : 'la mediana';
    const topDefenderName = bestD ? bestD.name : 'la difesa';
    const topKeeperName = bestP ? bestP.name : 'la porta';
    const flopName = flopRisk ? flopRisk.name : 'le scommesse';
    const candidates = [];
    if (pctA >= 45 && bestA) {
        candidates.push({
            id: 'heavy_attack_1',
            text: `All-in totale sull'attacco con ${spentA} CR (il ${Math.round(pctA)}% del budget) per ${topAttackerName}: se i bomber girano lottano per il titolo, ma con ${spentD} CR in difesa rischiano troppi malus.`
        });
        candidates.push({
            id: 'heavy_attack_2',
            text: `Tattica Zemaniana pura: ${spentA} crediti riversati in attacco su ${topAttackerName}. Ogni partita finirà 4-3 o 3-4 col cardiopalma fino al 90'.`
        });
    }
    if (pctC >= 32 && bestC) {
        candidates.push({
            id: 'heavy_mid_1',
            text: `Mediana di lusso con ben ${spentC} CR spesi e guidata da ${topMidfielderName}: una fabbrica di gol e assist da dietro che compenserà i turni a secco dell'attacco.`
        });
        candidates.push({
            id: 'heavy_mid_2',
            text: `Centrocampo da sogno (${spentC} CR, voto ${gradeC}) con ${topMidfielderName}: puntano forte sugli inserimenti e sui calci piazzati per fare la differenza.`
        });
    }
    if (spentP >= 80 && bestP) {
        candidates.push({
            id: 'golden_gk_1',
            text: `Porta blindata a peso d'oro (${spentP} CR con ${topKeeperName}): filosofia da 1-0 fisso e caccia al bonus modificatore difesa di ${topDefenderName}.`
        });
    }
    if (spentP <= 20 && listP.length >= 2) {
        candidates.push({
            id: 'budget_gk_1',
            text: `Portieri al discount pagati solo ${spentP} CR totali: hanno risparmiato tra i pali per scatenarsi avanti, ma ogni gol subito la domenica farà malissimo.`
        });
    }
    if (remaining >= 35) {
        candidates.push({
            id: 'cash_hoarder_1',
            text: `Hanno chiuso l'asta con un tesoretto di ${remaining} CR residui: o hanno dormito durante i rilanci dei top player o preparano un mercato di riparazione da padroni.`
        });
    }
    if (highFragilityCount >= 3) {
        candidates.push({
            id: 'hospital_1',
            text: `Rosa dal talento indiscutibile ma con abbonamento fisso all'infermeria (${highFragilityCount} giocatori fragili tra cui ${flopName}): il giovedì si passerà leggendo i bollettini medici.`
        });
    }
    if (penaltyCount === 0 && playersList.length >= 14) {
        candidates.push({
            id: 'no_penalty_takers',
            text: `Zero rigoristi in rosa: ogni penalty concesso in Serie A sarà motivo di ansia perché non porterà mai il +3 sperato.`
        });
    }
    if (bestA && (bestA.paidPrice || bestA.price || 0) >= 280) {
        const pPrice = bestA.paidPrice || bestA.price;
        candidates.push({
            id: 'one_man_army',
            text: `Squadra one-man-band: hanno puntato ${pPrice} CR su ${bestA.name} e completato il resto della rosa al discount. Si vive o si muore sui suoi gol.`
        });
    }
    if (overallGrade >= 8.0) {
        if (isMyTeam) {
            candidates.push({
                id: 'scudetto_myteam',
                text: `Rosa costruita alla perfezione con l'AI: ${topAttackerName} davanti e ${topMidfielderName} in mezzo. Favoriti indiscussi per il titolo di lega.`
            });
        } else {
            candidates.push({
                id: 'scudetto_rival',
                text: `Corazzata da scudetto guidata da ${topAttackerName} e ${topMidfielderName}: struttura solida in tutti i 4 reparti, la squadra da battere.`
            });
        }
    }
    if (overallGrade <= 6.8) {
        candidates.push({
            id: 'wood_spoon_1',
            text: `Asta al risparmio estremo con troppi titolari di provincia: a novembre staranno già calcolando i punti salvezza per non pagare la cena di fine anno.`
        });
        candidates.push({
            id: 'wood_spoon_2',
            text: `Rosa infarcita di scommesse a 1 credito: il brivido di giocare in 10 alle 14:59 con i cambi contati sarà la vera routine settimanale.`
        });
    }
    candidates.push({
        id: 'solid_mid_1',
        text: `Squadra da classico pareggio 1-1 col 66.5 a 66.0: ${topAttackerName} e ${topMidfielderName} portano voti onesti senza strafare, salvezza tranquilla a metà classifica.`
    });
    candidates.push({
        id: 'solid_mid_2',
        text: `Formazione quadrata ed equilibrata: spesa ben distribuita tra difesa (${spentD} CR), centrocampo (${spentC} CR) e attacco (${spentA} CR). Mina vagante del campionato.`
    });
    candidates.push({
        id: 'solid_mid_3',
        text: `Titolari affidabili da 35 presenze: rosa operaia pronta a colpire quando i top player avversari riposeranno per il turnover europeo.`
    });
    for (const c of candidates) {
        if (!assignedTemplateIds.has(c.id)) {
            assignedTemplateIds.add(c.id);
            return c.text;
        }
    }
    const fallback = candidates[Math.floor(Math.random() * candidates.length)];
    assignedTemplateIds.add(fallback.id);
    return fallback.text;
}
function getAllTeamsEvaluations() {
    const evals = [];
    const myName = (typeof State !== 'undefined' && State.teamName) ? State.teamName : 'La Mia Squadra';
    const unikaPlayers = getUnikaPlayersFull();
    evals.push(evaluateTeamRoster(myName, unikaPlayers, State.budgetSpent || 0, State.budgetTotal || 1000));
    const rivalsList = Object.keys(State.rivals || {});
    rivalsList.forEach(rName => {
        const rData = State.rivals[rName] || { spent: 0, budget: (State.budgetTotal || 1000), players: [] };
        const rPlayers = getRivalPlayersFull(rName);
        evals.push(evaluateTeamRoster(rName, rPlayers, rData.spent || 0, rData.budget || (State.budgetTotal || 1000)));
    });
    evals.sort((a, b) => b.overallGrade - a.overallGrade);
    const assignedRoasts = new Set();
    evals.forEach(e => {
        e.roast = generateUniqueAiRoast(e, evals, assignedRoasts);
    });
    evals.forEach((e, idx) => {
        e.rank = idx + 1;
        if (e.rank === 1) e.rankBadge = '🥇 1° Posto (Scudetto)';
        else if (e.rank === 2) e.rankBadge = '🥈 2° Posto (Zona Champions)';
        else if (e.rank === 3) e.rankBadge = '🥉 3° Posto (Zona Champions)';
        else if (e.rank <= 5) e.rankBadge = '🎖️ Zona Europa League';
        else if (e.rank <= 7) e.rankBadge = '⚠️ Metà Classifica';
        else e.rankBadge = `💀 ${e.rank}° Posto (Cucchiaio di Legno)`;
    });
    return evals;
}
function copyLeagueReportToWhatsApp() {
    const evals = getAllTeamsEvaluations();
    if (!evals.length) return;
    let text = `🏆 *PAGELLE UFFICIALI LEGA FANTA 2026/27 (AI ENGINE)* 🏆\n`;
    text += `_Valutazioni oggettive basate su OVR, profondità di rosa e proiezione punti_\n\n`;
    const myName = (typeof State !== 'undefined' && State.teamName) ? State.teamName : 'La Mia Rosa';
    evals.forEach(e => {
        const isMyTeam = (e.teamName === myName || e.teamName === 'La Mia Rosa' || e.teamName === 'Unika');
        const teamTitle = isMyTeam ? `🌟 ${e.teamName.toUpperCase()} (La Tua Rosa)` : `👥 ${e.teamName.toUpperCase()}`;
        text += `------------------------------------\n`;
        text += `${e.rankBadge} • *${teamTitle}*\n`;
        text += `📊 *VOTO COMPLESSIVO: ${e.overallGrade} / 10*\n`;
        text += `🧤 Porta: ${e.gradeP} | 🛡️ Dif: ${e.gradeD} | 🪄 Cent: ${e.gradeC} | ⚡ Att: ${e.gradeA}\n`;
        if (e.topPick) text += `⭐ Miglior Colpo: ${e.topPick.name} (${e.topPick.team}) [OVR ${e.topPick.ovr}]\n`;
        if (e.flopRisk) text += `🎲 Scommessa/Rischio: ${e.flopRisk.name} [Fragilità: ${e.flopRisk.fragilita_val || 'M'}]\n`;
        text += `🔥 *AI Roast:* _"${e.roast}"_\n\n`;
    });
    text += `_Generato con Fanta Master AI 2026/27_`;
    navigator.clipboard.writeText(text).then(() => {
        alert("✓ Pagellone della Lega copiato negli appunti con successo!\n\nIncollalo nella chat WhatsApp della tua Lega per far partire le discussioni.");
    }).catch(() => {
        prompt("Copia manualmente il report delle pagelle:", text);
    });
}
function escapeQuotes(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
function closeTeamRosterModal() {
    const modal = document.getElementById('teamRosterModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
    window.removeEventListener('keydown', handleRosterModalEsc);
}
function handleRosterModalEsc(e) {
    if (e.key === 'Escape') {
        closeTeamRosterModal();
    }
}
function copySingleTeamRosterToWhatsApp(teamName) {
    const evals = getAllTeamsEvaluations();
    const teamEval = evals.find(e => e.teamName === teamName) || evals[0];
    if (!teamEval) return;
    const totalBudget = (typeof State !== 'undefined' && State.budgetTotal) ? State.budgetTotal : 1000;
    const spent = teamEval.budgetSpent || 0;
    const remaining = totalBudget - spent;
    let text = `⚽ *ROSA & CREDITI — ${teamEval.teamName.toUpperCase()}* ⚽\n`;
    text += `📊 Voto: *${teamEval.overallGrade} / 10* (${teamEval.rankBadge})\n`;
    text += `💰 Spesi: *${spent} CR* | Residui: *${remaining} CR*\n\n`;
    const roleTitles = { P: '🧤 PORTIERI', D: '🛡️ DIFENSORI', C: '🪄 CENTROCAMPISTI', A: '⚡ ATTACCANTI' };
    ['P', 'D', 'C', 'A'].forEach(rKey => {
        const list = (teamEval.roles && teamEval.roles[rKey]) ? teamEval.roles[rKey] : [];
        if (list.length > 0) {
            const roleSpent = list.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || p.prezzo_cons || 1)), 0);
            text += `*${roleTitles[rKey]} (${roleSpent} CR):*\n`;
            list.forEach(p => {
                const paid = p.paidPrice !== undefined ? p.paidPrice : (p.price || p.prezzo_cons || 1);
                text += `• ${p.name} (${p.team || ''}) — *${paid} CR*\n`;
            });
            text += `\n`;
        }
    });
    text += `_Generato con Fanta Master AI 2026/27_`;
    navigator.clipboard.writeText(text).then(() => {
        alert(`✓ Rosa di ${teamEval.teamName} copiata per WhatsApp!`);
    }).catch(() => {
        prompt("Copia la rosa:", text);
    });
}
function openTeamRosterModal(teamName) {
    const evals = getAllTeamsEvaluations();
    const teamEval = evals.find(e => e.teamName === teamName) || evals[0];
    if (!teamEval) return;
    let modal = document.getElementById('teamRosterModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'teamRosterModal';
        modal.className = 'modal-backdrop';
        modal.setAttribute('onclick', 'if(event.target === this) closeTeamRosterModal()');
        modal.innerHTML = `
            <div class="modal-card team-roster-minimal-card" id="teamRosterModalCard">
                <div id="teamRosterModalContent"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    const myName = (typeof State !== 'undefined' && State.teamName) ? State.teamName : 'La Mia Rosa';
    const isMyTeam = (teamEval.teamName === myName || teamEval.teamName === 'La Mia Rosa' || teamEval.teamName === 'Unika');
    const players = teamEval.playersList || [];
    const roleOrder = ['P', 'D', 'C', 'A'];
    const roleNames = {
        P: { name: 'Portieri', icon: '🧤', color: '#fbbf24' },
        D: { name: 'Difensori', icon: '🛡️', color: '#38bdf8' },
        C: { name: 'Centrocampisti', icon: '🪄', color: '#34d399' },
        A: { name: 'Attaccanti', icon: '⚡', color: '#f43f5e' }
    };
    const rolesMap = { P: [], D: [], C: [], A: [] };
    players.forEach(p => {
        const r = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (p.role || 'C');
        if (rolesMap[r]) rolesMap[r].push(p);
        else rolesMap.C.push(p);
    });
    Object.keys(rolesMap).forEach(r => {
        rolesMap[r].sort((a, b) => {
            const pA = a.paidPrice !== undefined ? a.paidPrice : (a.price || 0);
            const pB = b.paidPrice !== undefined ? b.paidPrice : (b.price || 0);
            if (pB !== pA) return pB - pA;
            return (b.ovr || 0) - (a.ovr || 0);
        });
    });
    const totalSpent = teamEval.budgetSpent || players.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
    const totalBudget = (typeof State !== 'undefined' && State.budgetTotal) ? State.budgetTotal : 1000;
    const remaining = totalBudget - totalSpent;
    const count = players.length;
    const rolesListHtml = roleOrder.map(rKey => {
        const rInfo = roleNames[rKey];
        const rPlayers = rolesMap[rKey] || [];
        const rSpent = rPlayers.reduce((s, p) => s + (p.paidPrice !== undefined ? p.paidPrice : (p.price || 0)), 0);
        if (rPlayers.length === 0) return '';
        const playerItems = rPlayers.map(p => {
            const paid = p.paidPrice !== undefined ? p.paidPrice : (p.price !== undefined ? p.price : (p.prezzo_cons || 1));
            const ovr = p.ovr || 70;
            const ovrColor = ovr >= 88 ? '#f59e0b' : ovr >= 80 ? '#38bdf8' : ovr >= 75 ? '#34d399' : '#94a3b8';
            const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
            const roleBadge = isMantra && p.mantra 
                ? `<span class="mantra-pill" style="font-size:9.5px;padding:1px 4px;border-radius:3px;">${p.mantra}</span>`
                : `<span class="role-badge ${p.role || 'C'}" style="font-size:9.5px;padding:1px 5px;border-radius:3px;">${p.role || 'C'}</span>`;
            let badgeIcon = '';
            if (p.is_rigorista_1) badgeIcon = '<span title="1° Rigorista" style="font-size:10px;">👑</span>';
            else if (teamEval.topPick && p.id === teamEval.topPick.id) badgeIcon = '<span title="Top Pick" style="font-size:10px;">⭐</span>';
            return `
                <div class="roster-min-item" onclick="openPlayerProfileModal(${p.id})">
                    <div style="display:flex;align-items:center;gap:7px;min-width:0;flex:1;">
                        ${roleBadge}
                        <b class="roster-min-name">${p.name}</b>
                        <span class="roster-min-team">${p.team || ''}</span>
                        ${badgeIcon}
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
                        <span class="roster-min-ovr" style="color:${ovrColor};">OVR ${ovr}</span>
                        <span class="roster-min-price ${paid >= 100 ? 'top' : paid >= 40 ? 'mid' : paid === 1 ? 'low' : ''}">
                            ${paid} CR
                        </span>
                    </div>
                </div>
            `;
        }).join('');
        return `
            <div class="roster-min-group">
                <div class="roster-min-group-head">
                    <span>${rInfo.icon} <b style="color:${rInfo.color};">${rInfo.name}</b> (${rPlayers.length})</span>
                    <span style="color:var(--text-muted);font-weight:700;">Totale: <b style="color:#fff;">${rSpent} CR</b></span>
                </div>
                <div class="roster-min-group-items">
                    ${playerItems}
                </div>
            </div>
        `;
    }).join('');
    const content = document.getElementById('teamRosterModalContent');
    if (!content) return;
    content.innerHTML = `
        <!-- MINIMAL MODAL HEAD -->
        <div class="roster-min-header">
            <div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">${teamEval.rank === 1 ? '🥇' : teamEval.rank === 2 ? '🥈' : teamEval.rank === 3 ? '🥉' : '⚽'}</span>
                    <h2 style="margin:0;font-size:18px;font-weight:900;color:${isMyTeam ? 'var(--accent-cyan)' : '#fff'};">
                        ${teamEval.teamName}
                    </h2>
                    <span class="report-rank-tag" style="background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;font-size:11px;">
                        Voto ${teamEval.overallGrade}
                    </span>
                </div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:3px;">
                    💰 Spesi: <b style="color:#f87171;">${totalSpent} CR</b> • Residui: <b style="color:#34d399;">${remaining} CR</b> • Rosa: <b>${count}/25</b>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <button class="btn-action" style="padding:4px 10px;font-size:11px;background:rgba(16,185,129,0.2);border-color:#10b981;color:#34d399;" onclick="copySingleTeamRosterToWhatsApp('${escapeQuotes(teamEval.teamName)}')">
                    📤 WhatsApp
                </button>
                <button class="sb-modal-close" style="width:28px;height:28px;border-radius:6px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#fff;font-size:14px;cursor:pointer;" onclick="closeTeamRosterModal()">✕</button>
            </div>
        </div>
        <!-- MINIMAL SCROLLABLE LIST -->
        <div class="roster-min-body">
            ${rolesListHtml}
        </div>
    `;
    modal.style.display = 'flex';
    modal.classList.add('active');
    window.addEventListener('keydown', handleRosterModalEsc);
}
function renderLeagueReportView() {
    const container = document.getElementById('viewLeagueReport');
    if (!container) return;
    const evals = getAllTeamsEvaluations();
    const myName = (typeof State !== 'undefined' && State.teamName) ? State.teamName : 'La Mia Rosa';
    const cardsHtml = evals.map(e => {
        const isMyTeam = (e.teamName === myName || e.teamName === 'La Mia Rosa' || e.teamName === 'Unika');
        const gradeClass = e.overallGrade >= 8.0 ? 'top' : e.overallGrade >= 6.8 ? 'mid' : 'low';
        const escapedName = escapeQuotes(e.teamName);
        return `
            <div class="report-card ${isMyTeam ? 'unika-highlight' : ''}" onclick="openTeamRosterModal('${escapedName}')" title="Clicca per visualizzare la rosa completa e i crediti di ${e.teamName}">
                <div class="report-card-header">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:20px;">${e.rank === 1 ? '🥇' : e.rank === 2 ? '🥈' : e.rank === 3 ? '🥉' : '⚽'}</span>
                        <div>
                            <h3 style="margin:0;font-size:16px;color:${isMyTeam ? 'var(--accent-cyan)' : '#fff'};">
                                ${isMyTeam ? `🌟 ${e.teamName} (La Tua Rosa)` : e.teamName}
                            </h3>
                            <span class="report-rank-tag">${e.rankBadge}</span>
                        </div>
                    </div>
                    <div class="report-overall-pill ${gradeClass}">
                        <span style="font-size:10px;text-transform:uppercase;letter-spacing:0.5px;">Voto</span>
                        <span style="font-size:20px;font-weight:900;">${e.overallGrade}</span>
                    </div>
                </div>
                <!-- REPARTI BAR (ALLINEAMENTO PERFETTO ORIZZONTALE) -->
                <div class="report-roles-grid">
                    <div class="report-role-item">
                        <span class="r-label" title="Porta"><span class="r-icon">🧤</span> Porta</span>
                        <b class="r-val ${e.gradeP >= 7.5 ? 'high' : ''}">${e.gradeP}</b>
                    </div>
                    <div class="report-role-item">
                        <span class="r-label" title="Difesa"><span class="r-icon">🛡️</span> Difesa</span>
                        <b class="r-val ${e.gradeD >= 7.5 ? 'high' : ''}">${e.gradeD}</b>
                    </div>
                    <div class="report-role-item">
                        <span class="r-label" title="Centrocampo"><span class="r-icon">🪄</span> Centroc.</span>
                        <b class="r-val ${e.gradeC >= 7.5 ? 'high' : ''}">${e.gradeC}</b>
                    </div>
                    <div class="report-role-item">
                        <span class="r-label" title="Attacco"><span class="r-icon">⚡</span> Attacco</span>
                        <b class="r-val ${e.gradeA >= 7.5 ? 'high' : ''}">${e.gradeA}</b>
                    </div>
                </div>
                <!-- HIGHLIGHTS: TOP PICK & FLOP RISK -->
                <div class="report-highlights">
                    ${e.topPick ? `
                        <div class="report-hl-box top">
                            <span class="hl-label">⭐ Miglior Colpo</span>
                            <div style="font-size:12.5px;font-weight:700;color:#fff;">${e.topPick.name}</div>
                            <div style="font-size:10.5px;color:var(--text-muted);">${e.topPick.team} • OVR ${e.topPick.ovr}</div>
                        </div>
                    ` : ''}
                    ${e.flopRisk ? `
                        <div class="report-hl-box risk">
                            <span class="hl-label">🎲 Rischio / Flop</span>
                            <div style="font-size:12.5px;font-weight:700;color:#fca5a5;">${e.flopRisk.name}</div>
                            <div style="font-size:10.5px;color:var(--text-muted);">${e.flopRisk.team} • Fragilità ${e.flopRisk.fragilita_val || 'M'}</div>
                        </div>
                    ` : ''}
                </div>
                <!-- AI ROAST -->
                <div class="report-roast-box">
                    <div style="font-size:11px;font-weight:800;color:#fbbf24;margin-bottom:4px;display:flex;align-items:center;gap:4px;">
                        <span>🔥</span> <span>AI ROAST:</span>
                    </div>
                    <div style="font-size:12px;font-style:italic;color:#e2e8f0;line-height:1.4;">
                        "${e.roast}"
                    </div>
                </div>
                <!-- CLICK HINT BAR -->
                <div class="report-card-action-hint">
                    <span>🔍</span> <span>Vedi Rosa e Crediti</span> <span style="margin-left:auto;">→</span>
                </div>
            </div>
        `;
    }).join('');
    container.innerHTML = `
        <div class="league-report-container">
            <!-- HEADER -->
            <div class="report-main-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:36px;">🏆</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:22px;color:var(--accent-cyan);">Pagelle Ufficiali della Lega & AI Roast</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            Classifica proiettata a ${evals.length} squadre, voti per reparto da 1 a 10 e commenti satirici AI pronti per WhatsApp. Clicca su qualsiasi squadra per vedere la rosa e i crediti.
                        </div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <button class="btn-action" style="background:linear-gradient(135deg, #10b981, #059669);color:#fff;font-weight:800;font-size:12.5px;padding:8px 16px;border:none;box-shadow:0 4px 15px rgba(16,185,129,0.35);" onclick="copyLeagueReportToWhatsApp()">
                        📤 Copia Pagelle per WhatsApp
                    </button>
                </div>
            </div>
            <!-- CARDS GRID -->
            <div class="report-grid">
                ${cardsHtml}
            </div>
        </div>
    `;
}
window.renderLeagueReportView = renderLeagueReportView;
window.copyLeagueReportToWhatsApp = copyLeagueReportToWhatsApp;
window.copySingleTeamRosterToWhatsApp = copySingleTeamRosterToWhatsApp;
window.getAllTeamsEvaluations = getAllTeamsEvaluations;
window.openTeamRosterModal = openTeamRosterModal;
window.closeTeamRosterModal = closeTeamRosterModal;