// ==============================================================================
// TOOL "CHI SCHIERO?" — HEAD-TO-HEAD WEEKEND DECISION ENGINE (1VS1)
// Serie A 2026/27 — FantaMaster AI
// ==============================================================================

window.chiSchieroState = {
    round: null,       // Calcolato dinamicamente da getUpcomingMatchdayRound()
    playerAId: null,
    playerBId: null,
    roleFilter: 'ALL',
    searchA: '',
    searchB: ''
};

function initChiSchieroState() {
    if (window.chiSchieroState.round === null) {
        if (typeof getUpcomingMatchdayRound === 'function') {
            window.chiSchieroState.round = getUpcomingMatchdayRound();
        } else {
            window.chiSchieroState.round = 6;
        }
    }

    if (!window.chiSchieroState.playerAId || !window.chiSchieroState.playerBId) {
        if (typeof PLAYERS !== 'undefined' && Array.isArray(PLAYERS) && PLAYERS.length > 0) {
            // Cerca default accattivanti: Politano vs Orsolini o Malen vs Martinez
            const pol = PLAYERS.find(p => p.name.toLowerCase().includes('politano'));
            const ors = PLAYERS.find(p => p.name.toLowerCase().includes('orsolini'));
            const mal = PLAYERS.find(p => p.name.toLowerCase().includes('malen'));
            const mar = PLAYERS.find(p => p.name.toLowerCase().includes('martinez l'));

            if (pol && ors) {
                window.chiSchieroState.playerAId = pol.id;
                window.chiSchieroState.playerBId = ors.id;
            } else if (mal && mar) {
                window.chiSchieroState.playerAId = mal.id;
                window.chiSchieroState.playerBId = mar.id;
            } else {
                window.chiSchieroState.playerAId = PLAYERS[0].id;
                window.chiSchieroState.playerBId = PLAYERS[1].id;
            }
        }
    }
}

function getChiSchieroFixtureForPlayer(player, roundNum) {
    if (!player || !player.team) return null;
    let matchFound = null;

    if (typeof OFFICIAL_CALENDAR_2026_27 !== 'undefined' && Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        const roundData = OFFICIAL_CALENDAR_2026_27.find(r => Number(r.giornata) === Number(roundNum));
        if (roundData && Array.isArray(roundData.matches)) {
            const m = roundData.matches.find(match => match.home === player.team || match.away === player.team);
            if (m) {
                const isHome = m.home === player.team;
                const opp = isHome ? m.away : m.home;
                matchFound = {
                    home: m.home,
                    away: m.away,
                    isHome: isHome,
                    opp: opp,
                    label: isHome ? `${m.home} vs ${m.away} (Casa)` : `${m.home} vs ${m.away} (Trasferta)`,
                    shortLabel: isHome ? `vs ${m.away} 🏠` : `@ ${m.home} ✈️`
                };
            }
        }
    }
    return matchFound;
}

function calculateChiSchieroScore(player, roundNum) {
    if (!player) return { score: 0, factors: [] };

    const fixture = getChiSchieroFixtureForPlayer(player, roundNum);
    const factors = [];

    // Base: Expected FantaMedia (xFM) o FM
    let baseRating = 6.0;
    if (player.xfm && !isNaN(player.xfm)) {
        baseRating = Number(player.xfm);
        factors.push({ name: 'Expected FantaMedia (xFM)', val: `+${baseRating.toFixed(2)}`, weight: 1.0, positive: baseRating >= 6.5 });
    } else if (player.fm_2627) {
        baseRating = Number(player.fm_2627);
        factors.push({ name: 'FantaMedia Reale 26/27', val: `+${baseRating.toFixed(2)}`, weight: 1.0, positive: baseRating >= 6.5 });
    } else {
        baseRating = Number(player.ovr) ? (player.ovr / 13.5) : 6.0;
        factors.push({ name: 'Overall AI Scalato', val: `${baseRating.toFixed(2)}`, weight: 1.0, positive: true });
    }

    let dynamicScore = baseRating * 10; // scala ~60-100

    // 1. Titolarità stimata
    const tit = (player.titolarita !== undefined && player.titolarita !== null) ? Number(player.titolarita) : 70;
    if (player.is_injured) {
        dynamicScore -= 45;
        factors.push({ name: 'Infortunio / Rientro TBD', val: '-45 pt 🩹', positive: false });
    } else if (tit >= 90) {
        dynamicScore += 6;
        factors.push({ name: 'Titolarissimo Inamovibile (90-100%)', val: '+6 pt 🔒', positive: true });
    } else if (tit >= 75) {
        dynamicScore += 3;
        factors.push({ name: 'Titolare Affidabile (75-89%)', val: '+3 pt 🛡️', positive: true });
    } else if (tit >= 50) {
        dynamicScore -= 2;
        factors.push({ name: 'Ballottaggio Aperto (50-74%)', val: '-2 pt 🔄', positive: false });
    } else {
        dynamicScore -= 18;
        factors.push({ name: 'Panchina / Rischio S.V. (<50%)', val: '-18 pt 🪑', positive: false });
    }

    // 2. Matchup & Vulnerabilità Difesa Avversaria
    if (fixture) {
        const oppStats = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[fixture.opp]) ? TEAM_STATS_DB[fixture.opp] : null;
        
        // Fattore Campo
        if (fixture.isHome) {
            dynamicScore += 4;
            factors.push({ name: 'Fattore Campo (Gioca in Casa)', val: '+4 pt 🏠', positive: true });
        } else {
            dynamicScore -= 2;
            factors.push({ name: 'Trasferta Insidiosa', val: '-2 pt ✈️', positive: false });
        }

        if (oppStats) {
            const xga = Number(oppStats.xga_team) || 7.0;
            const gcMatch = Number(oppStats.goals_conceded_match) || 1.3;

            if (player.role === 'P') {
                // Per i portieri, conta la debolezza dell'attacco avversario
                const oppXg = Number(oppStats.xg_team) || 7.0;
                if (oppXg < 6.0) {
                    dynamicScore += 8;
                    factors.push({ name: `Attacco avversario sterile (${oppStats.squadra}: xG ${oppXg.toFixed(1)})`, val: '+8 pt 🧤', positive: true });
                } else if (oppXg > 9.0) {
                    dynamicScore -= 10;
                    factors.push({ name: `Attacco avversario prolifico (${oppStats.squadra}: xG ${oppXg.toFixed(1)})`, val: '-10 pt ⚠️', positive: false });
                }
            } else {
                // Per giocatori di movimento, conta la fragilità della difesa avversaria
                if (xga >= 8.5 || gcMatch >= 1.8) {
                    dynamicScore += 8;
                    factors.push({ name: `Difesa rivale fragile (${oppStats.squadra}: ${gcMatch.toFixed(1)} gol subiti/partita)`, val: '+8 pt 🎯', positive: true });
                } else if (xga <= 5.0 || gcMatch <= 0.8) {
                    dynamicScore -= 8;
                    factors.push({ name: `Muro difensivo rivale (${oppStats.squadra}: solo ${gcMatch.toFixed(1)} gol subiti/partita)`, val: '-8 pt 🛡️', positive: false });
                } else {
                    factors.push({ name: `Difesa rivale nella media (${oppStats.squadra})`, val: 'Neutro', positive: true });
                }
            }
        }
    }

    // 3. Status Tiratore (Rigori & Piazzati)
    if (player.is_rigorista_1 || player.rigorista_val === '1° Rigorista') {
        dynamicScore += 8;
        factors.push({ name: '1° Rigorista Ufficiale', val: '+8 pt 👑 (+3 dal dischetto)', positive: true });
    } else if (player.is_rigorista_2 || player.rigorista_val === '2° Rigorista') {
        dynamicScore += 3;
        factors.push({ name: '2° Rigorista Designato', val: '+3 pt 🎯', positive: true });
    }

    if (player.is_punizioni || player.is_corner) {
        dynamicScore += 4;
        factors.push({ name: 'Specialista Calci Piazzati (Corner/Punizioni)', val: '+4 pt 📐 (+1 assist probabile)', positive: true });
    }

    // 4. Cartellini e Disciplina
    const amm = Number(player.amm_2627) || 0;
    const esp = Number(player.esp_2627) || 0;
    if (esp > 0) {
        dynamicScore -= 4;
        factors.push({ name: 'Rischio Malus Disciplinare (Espulsioni pregresse)', val: '-4 pt 🟥', positive: false });
    } else if (amm >= 2) {
        dynamicScore -= 2;
        factors.push({ name: 'Propenso al cartellino giallo', val: '-2 pt 🟨', positive: false });
    }

    return {
        score: Math.max(10, Math.round(dynamicScore * 10) / 10),
        factors: factors,
        fixture: fixture
    };
}

function calculateChiSchieroVerdict(playerA, playerB, roundNum) {
    if (!playerA || !playerB) return null;

    const dataA = calculateChiSchieroScore(playerA, roundNum);
    const dataB = calculateChiSchieroScore(playerB, roundNum);

    const diff = dataA.score - dataB.score;
    let pctA = 50 + Math.round(diff * 1.5);
    pctA = Math.max(10, Math.min(90, pctA));
    const pctB = 100 - pctA;

    let verdictTitle = '';
    let verdictSubtitle = '';
    let winnerId = null;

    if (pctA >= 60) {
        verdictTitle = `🏆 CONSIGLIATO: ${playerA.name.toUpperCase()} (${pctA}%)`;
        verdictSubtitle = `L'algoritmo predittivo consiglia nettamente di schierare ${playerA.name} per la Giornata ${roundNum}.`;
        winnerId = playerA.id;
    } else if (pctB >= 60) {
        verdictTitle = `🏆 CONSIGLIATO: ${playerB.name.toUpperCase()} (${pctB}%)`;
        verdictSubtitle = `L'algoritmo predittivo consiglia nettamente di schierare ${playerB.name} per la Giornata ${roundNum}.`;
        winnerId = playerB.id;
    } else {
        verdictTitle = `⚖️ BALLOTTAGGIO EQUO: ${playerA.name} (${pctA}%) vs ${playerB.name} (${pctB}%)`;
        verdictSubtitle = `Entrambi i profili offrono un rendimento atteso molto simile per la Giornata ${roundNum}. Piccoli dettagli faranno la differenza.`;
        winnerId = diff >= 0 ? playerA.id : playerB.id;
    }

    // Costruzione 3 bullets chiave in linguaggio naturale
    const bullets = [];
    const winnerPlayer = (winnerId === playerA.id) ? playerA : playerB;
    const loserPlayer = (winnerId === playerA.id) ? playerB : playerA;
    const winnerData = (winnerId === playerA.id) ? dataA : dataB;
    const loserData = (winnerId === playerA.id) ? dataB : dataA;

    // Bullet 1: Matchup e fattore campo
    if (winnerData.fixture && loserData.fixture) {
        if (winnerData.fixture.isHome && !loserData.fixture.isHome) {
            bullets.push(`🏠 <b>Fattore Campo Favorevole:</b> ${winnerPlayer.name} gioca in casa (${winnerData.fixture.shortLabel}), mentre ${loserPlayer.name} è impegnato in trasferta (${loserData.fixture.shortLabel}).`);
        } else {
            bullets.push(`⚽ <b>Incrocio di Giornata:</b> ${winnerPlayer.name} scende in campo in ${winnerData.fixture.label}, con una proiezione offensiva superiore.`);
        }
    }

    // Bullet 2: Status bonus e dischetto
    const isWPenalty = winnerPlayer.is_rigorista_1 || winnerPlayer.rigorista_val === '1° Rigorista';
    const isLPenalty = loserPlayer.is_rigorista_1 || loserPlayer.rigorista_val === '1° Rigorista';
    if (isWPenalty && !isLPenalty) {
        bullets.push(`👑 <b>Bonus Dischetto (+3):</b> ${winnerPlayer.name} è il 1° rigorista ufficiale della propria squadra, garantendo un extra-valore statistico su palla inattiva.`);
    } else if (winnerPlayer.is_punizioni || winnerPlayer.is_corner) {
        bullets.push(`📐 <b>Piazzati & Assist:</b> ${winnerPlayer.name} batte calci piazzati e corner, aumentando sensibilmente l'Expected Assist (xA).`);
    } else {
        bullets.push(`📈 <b>Indice di Titolarità:</b> ${winnerPlayer.name} vanta una presenza attesa del ${winnerPlayer.titolarita || 0}% dall'1', riducendo a zero il rischio s.v.`);
    }

    // Bullet 3: Rendimento xFM
    const xfmW = Number(winnerPlayer.xfm) || Number(winnerPlayer.fm_2627) || 6.0;
    const xfmL = Number(loserPlayer.xfm) || Number(loserPlayer.fm_2627) || 6.0;
    bullets.push(`💎 <b>Expected FantaMedia:</b> ${winnerPlayer.name} produce un volume di gioco atteso pari a <b>${xfmW.toFixed(2)} xFM</b> contro i ${xfmL.toFixed(2)} xFM di ${loserPlayer.name}.`);

    return {
        playerA,
        playerB,
        dataA,
        dataB,
        pctA,
        pctB,
        winnerId,
        verdictTitle,
        verdictSubtitle,
        bullets
    };
}

function selectChiSchieroPreset(nameA, nameB) {
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return;
    const pA = PLAYERS.find(p => p.name.toLowerCase().includes(nameA.toLowerCase()));
    const pB = PLAYERS.find(p => p.name.toLowerCase().includes(nameB.toLowerCase()));
    if (pA && pB) {
        window.chiSchieroState.playerAId = pA.id;
        window.chiSchieroState.playerBId = pB.id;
        renderChiSchieroView();
    }
}

function onChiSchieroPlayerSelect(slot, playerId) {
    if (slot === 'A') {
        window.chiSchieroState.playerAId = parseInt(playerId, 10);
    } else {
        window.chiSchieroState.playerBId = parseInt(playerId, 10);
    }
    renderChiSchieroView();
}

function onChiSchieroRoundChange(roundVal) {
    window.chiSchieroState.round = parseInt(roundVal, 10);
    renderChiSchieroView();
}

function onChiSchieroRoleFilterChange(role) {
    window.chiSchieroState.roleFilter = role;
    renderChiSchieroView();
}

function copyChiSchieroVerdictToClipboard() {
    const pA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId);
    const pB = PLAYERS.find(p => p.id === window.chiSchieroState.playerBId);
    if (!pA || !pB) return;

    const round = window.chiSchieroState.round || 6;
    const verdict = calculateChiSchieroVerdict(pA, pB, round);
    if (!verdict) return;

    const text = `⚔️ *FANTA MASTER AI — CHI SCHIERO?* 📅 (Giornata ${round})\n\n` +
        `🥊 *${pA.name} (${pA.team})* vs *${pB.name} (${pB.team})*\n\n` +
        `🎯 *VERDETTO:* ${verdict.verdictTitle}\n` +
        `📊 Percentuali: ${pA.name} ${verdict.pctA}% ⚡ | ${pB.name} ${verdict.pctB}%\n\n` +
        `💡 *Motivazioni AI:*\n` +
        verdict.bullets.map(b => b.replace(/\*\*/g, '')).join('\n') + `\n\n` +
        `👉 Risolvi i tuoi dubbi di formazione gratis su: https://fantamasterai.it/chi-schiero/`;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            alert('✅ Verdetto copiato negli appunti! Incollalo su WhatsApp o Telegram.');
        }).catch(() => {
            prompt('Copia il verdetto per WhatsApp:', text);
        });
    } else {
        prompt('Copia il verdetto per WhatsApp:', text);
    }
}

function renderChiSchieroView() {
    const container = document.getElementById('viewChiSchiero');
    if (!container) return;

    initChiSchieroState();

    const round = window.chiSchieroState.round || 6;
    const pA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId) || PLAYERS[0];
    const pB = PLAYERS.find(p => p.id === window.chiSchieroState.playerBId) || PLAYERS[1];

    // Data del round dal calendario
    let roundDateStr = '';
    if (typeof OFFICIAL_CALENDAR_2026_27 !== 'undefined' && Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        const rData = OFFICIAL_CALENDAR_2026_27.find(r => Number(r.giornata) === Number(round));
        if (rData && rData.date) roundDateStr = rData.date;
    }

    const verdict = calculateChiSchieroVerdict(pA, pB, round);

    // Opzioni per il selettore turno (38 giornate)
    const upcomingRound = (typeof getUpcomingMatchdayRound === 'function') ? getUpcomingMatchdayRound() : 6;
    let roundOptionsHtml = '';
    for (let r = 1; r <= 38; r++) {
        const isUpcoming = (r === upcomingRound);
        const isSel = (r === round);
        const tag = isUpcoming ? ' ⭐ (Prossima in Arrivo)' : (r < upcomingRound ? ' (Giocata)' : '');
        roundOptionsHtml += `<option value="${r}" ${isSel ? 'selected' : ''}>Giornata ${r}${tag}</option>`;
    }

    // Filtra lista giocatori per selects
    const roleFilt = window.chiSchieroState.roleFilter;
    const eligiblePlayers = PLAYERS.filter(p => {
        if (roleFilt === 'ALL') return true;
        return p.role === roleFilt;
    });

    const optionsAHtml = eligiblePlayers.map(p => `
        <option value="${p.id}" ${p.id === pA.id ? 'selected' : ''}>
            ${p.name} (${p.team} - ${p.role}) • OVR ${p.ovr}
        </option>
    `).join('');

    const optionsBHtml = eligiblePlayers.map(p => `
        <option value="${p.id}" ${p.id === pB.id ? 'selected' : ''}>
            ${p.name} (${p.team} - ${p.role}) • OVR ${p.ovr}
        </option>
    `).join('');

    // Classi tier OVR
    const ovrClassA = typeof getOvrClass === 'function' ? getOvrClass(pA.ovr) : 'ovr-tier-elite';
    const ovrClassB = typeof getOvrClass === 'function' ? getOvrClass(pB.ovr) : 'ovr-tier-elite';

    const fixtureA = verdict.dataA.fixture;
    const fixtureB = verdict.dataB.fixture;

    const html = `
        <div class="chi-schiero-container">
            <!-- HERO HEADER -->
            <div class="chi-schiero-hero">
                <div class="cs-hero-top">
                    <div class="cs-title-box">
                        <div class="cs-badge-icon">⚔️</div>
                        <div>
                            <div class="cs-eyebrow">DECISION ENGINE 1VS1 • SERIE A 2026/27</div>
                            <h1 class="cs-main-title">TOOL "CHI SCHIERO?"</h1>
                            <div class="cs-main-desc">Il comparatore predittivo per risolvere i tuoi ballottaggi di formazione del weekend.</div>
                        </div>
                    </div>

                    <div class="cs-hero-actions">
                        <button class="cs-btn-share" onclick="copyChiSchieroVerdictToClipboard()" title="Copia per WhatsApp / Telegram">
                            <span>📲</span> Condividi Verdetto
                        </button>
                    </div>
                </div>

                <!-- CONTROLLI: GIORNATA & FILTRI -->
                <div class="cs-control-bar">
                    <div class="cs-ctrl-group">
                        <label for="selectCsRound">⚽ TURNO ANALIZZATO:</label>
                        <select id="selectCsRound" class="cs-select" onchange="onChiSchieroRoundChange(this.value)">
                            ${roundOptionsHtml}
                        </select>
                        ${roundDateStr ? `<span class="cs-date-badge">📅 ${roundDateStr}</span>` : ''}
                    </div>

                    <div class="cs-ctrl-group">
                        <label>FILTRA RUOLO:</label>
                        <div class="cs-role-filters">
                            <button class="cs-role-chip ${roleFilt === 'ALL' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('ALL')">TUTTI</button>
                            <button class="cs-role-chip ${roleFilt === 'P' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('P')">P</button>
                            <button class="cs-role-chip ${roleFilt === 'D' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('D')">D</button>
                            <button class="cs-role-chip ${roleFilt === 'C' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('C')">C</button>
                            <button class="cs-role-chip ${roleFilt === 'A' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('A')">A</button>
                        </div>
                    </div>
                </div>

                <!-- PRESET BALLOTTAGGI FAMOSI -->
                <div class="cs-presets-row">
                    <span class="cs-presets-title">🔥 Ballottaggi Caldi:</span>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Politano', 'Orsolini')">Politano vs Orsolini</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Malen', 'Castro S.')">Malen vs Castro S.</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Martinez L', 'Hojlund')">Lautaro vs Hojlund</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Pulisic', 'Chukwueze')">Pulisic vs Chukwueze</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Dimarco', 'Carlos Augusto')">Dimarco vs C. Augusto</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Svilar', 'Vicario')">Svilar vs Vicario</button>
                </div>
            </div>

            <!-- SELEZIONE DEI DUE CALCIATORI -->
            <div class="cs-duel-selectors-grid">
                <!-- SLOT A -->
                <div class="cs-player-selector-card card-a">
                    <div class="cs-slot-header">
                        <span class="cs-slot-tag tag-a">CALCIATORE A</span>
                        <span class="role-badge ${pA.role}">${pA.role}</span>
                    </div>
                    <select class="cs-player-dropdown" onchange="onChiSchieroPlayerSelect('A', this.value)">
                        ${optionsAHtml}
                    </select>
                    
                    <div class="cs-player-quick-info">
                        <div class="cs-player-identity">
                            <span class="ovr-pill ${ovrClassA}">${pA.ovr}</span>
                            <div class="cs-name-team">
                                <span class="cs-pname">${pA.name}</span>
                                <span class="cs-pteam">${pA.team}</span>
                            </div>
                        </div>
                        <div class="cs-match-pill ${fixtureA && fixtureA.isHome ? 'home' : 'away'}">
                            ${fixtureA ? fixtureA.shortLabel : 'Turno di riposo'}
                        </div>
                    </div>
                </div>

                <div class="cs-vs-divider">
                    <span>VS</span>
                </div>

                <!-- SLOT B -->
                <div class="cs-player-selector-card card-b">
                    <div class="cs-slot-header">
                        <span class="cs-slot-tag tag-b">CALCIATORE B</span>
                        <span class="role-badge ${pB.role}">${pB.role}</span>
                    </div>
                    <select class="cs-player-dropdown" onchange="onChiSchieroPlayerSelect('B', this.value)">
                        ${optionsBHtml}
                    </select>

                    <div class="cs-player-quick-info">
                        <div class="cs-player-identity">
                            <span class="ovr-pill ${ovrClassB}">${pB.ovr}</span>
                            <div class="cs-name-team">
                                <span class="cs-pname">${pB.name}</span>
                                <span class="cs-pteam">${pB.team}</span>
                            </div>
                        </div>
                        <div class="cs-match-pill ${fixtureB && fixtureB.isHome ? 'home' : 'away'}">
                            ${fixtureB ? fixtureB.shortLabel : 'Turno di riposo'}
                        </div>
                    </div>
                </div>
            </div>

            <!-- HERO VERDICT DISPLAY -->
            <div class="cs-verdict-banner">
                <div class="cs-verdict-title">${verdict.verdictTitle}</div>
                <div class="cs-verdict-subtitle">${verdict.verdictSubtitle}</div>

                <!-- PROBABILITY BAR -->
                <div class="cs-prob-bar-container">
                    <div class="cs-prob-bar-left" style="width: ${verdict.pctA}%;">
                        <span>${pA.name} ${verdict.pctA}%</span>
                    </div>
                    <div class="cs-prob-bar-right" style="width: ${verdict.pctB}%;">
                        <span>${verdict.pctB}% ${pB.name}</span>
                    </div>
                </div>
            </div>

            <!-- MOTIVAZIONI AI (DECISION ENGINE BULLETS) -->
            <div class="cs-reasons-card">
                <div class="cs-reasons-header">
                    <span class="cs-reasons-icon">💡</span>
                    <h3>Perché l'Algoritmo Consiglia Questo Esito?</h3>
                </div>
                <div class="cs-reasons-list">
                    ${verdict.bullets.map(b => `
                        <div class="cs-reason-item">
                            <span class="cs-check-icon">✓</span>
                            <div>${b}</div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- TAVOLA COMPARATIVA TESTA A TESTA -->
            <div class="cs-table-card">
                <div class="cs-table-header">
                    <h3>Confronto Statistico Diretto • Giornata ${round}</h3>
                </div>
                <div class="cs-table-responsive">
                    <table class="cs-comparison-table">
                        <thead>
                            <tr>
                                <th style="width:40%;text-align:left;">${pA.name} (${pA.team})</th>
                                <th style="width:20%;text-align:center;">METRICA</th>
                                <th style="width:40%;text-align:right;">${pB.name} (${pB.team})</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="col-a ${fixtureA && fixtureA.isHome ? 'stat-tier-elite' : ''}">${fixtureA ? fixtureA.label : '-'}</td>
                                <td class="col-metric">Partita & Sede</td>
                                <td class="col-b ${fixtureB && fixtureB.isHome ? 'stat-tier-elite' : ''}">${fixtureB ? fixtureB.label : '-'}</td>
                            </tr>
                            <tr>
                                <td class="col-a stat-tier-elite">${pA.ovr} OVR</td>
                                <td class="col-metric">Valutazione Globale</td>
                                <td class="col-b stat-tier-elite">${pB.ovr} OVR</td>
                            </tr>
                            <tr>
                                <td class="col-a ${pA.titolarita >= 85 ? 'stat-tier-top' : (pA.titolarita < 50 ? 'stat-tier-bench' : 'stat-tier-mid')}">${pA.titolarita || 0}%</td>
                                <td class="col-metric">Titolarità Stimata</td>
                                <td class="col-b ${pB.titolarita >= 85 ? 'stat-tier-top' : (pB.titolarita < 50 ? 'stat-tier-bench' : 'stat-tier-mid')}">${pB.titolarita || 0}%</td>
                            </tr>
                            <tr>
                                <td class="col-a stat-tier-elite">${pA.xfm ? Number(pA.xfm).toFixed(2) : (pA.fm_2627 ? Number(pA.fm_2627).toFixed(2) : '-')}</td>
                                <td class="col-metric">Expected FantaMedia (xFM)</td>
                                <td class="col-b stat-tier-elite">${pB.xfm ? Number(pB.xfm).toFixed(2) : (pB.fm_2627 ? Number(pB.fm_2627).toFixed(2) : '-')}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${pA.fm_2627 ? Number(pA.fm_2627).toFixed(2) : '-'} / ${pA.mv_2627 ? Number(pA.mv_2627).toFixed(2) : '-'}</td>
                                <td class="col-metric">FM / Media Voto 26/27</td>
                                <td class="col-b">${pB.fm_2627 ? Number(pB.fm_2627).toFixed(2) : '-'} / ${pB.mv_2627 ? Number(pB.mv_2627).toFixed(2) : '-'}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${(pA.gol_2627 || 0)}G / ${(pA.assist_2627 || 0)}A</td>
                                <td class="col-metric">Gol / Assist 26/27</td>
                                <td class="col-b">${(pB.gol_2627 || 0)}G / ${(pB.assist_2627 || 0)}A</td>
                            </tr>
                            <tr>
                                <td class="col-a">${pA.is_rigorista_1 ? '👑 1° Rigorista' : (pA.is_rigorista_2 ? '🎯 2° Rigorista' : '-')}</td>
                                <td class="col-metric">Rigorista Ufficiale</td>
                                <td class="col-b">${pB.is_rigorista_1 ? '👑 1° Rigorista' : (pB.is_rigorista_2 ? '🎯 2° Rigorista' : '-')}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${pA.is_punizioni && pA.is_corner ? '📐 Corner & Punizioni' : (pA.is_punizioni ? '📐 Punizioni' : (pA.is_corner ? '📐 Corner' : '-'))}</td>
                                <td class="col-metric">Calci Piazzati</td>
                                <td class="col-b">${pB.is_punizioni && pB.is_corner ? '📐 Corner & Punizioni' : (pB.is_punizioni ? '📐 Punizioni' : (pB.is_corner ? '📐 Corner' : '-'))}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${(pA.amm_2627 || 0)} 🟨 / ${(pA.esp_2627 || 0)} 🟥</td>
                                <td class="col-metric">Cartellini / Malus</td>
                                <td class="col-b">${(pB.amm_2627 || 0)} 🟨 / ${(pB.esp_2627 || 0)} 🟥</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

window.renderChiSchieroView = renderChiSchieroView;
window.onChiSchieroPlayerSelect = onChiSchieroPlayerSelect;
window.onChiSchieroRoundChange = onChiSchieroRoundChange;
window.onChiSchieroRoleFilterChange = onChiSchieroRoleFilterChange;
window.selectChiSchieroPreset = selectChiSchieroPreset;
window.copyChiSchieroVerdictToClipboard = copyChiSchieroVerdictToClipboard;
