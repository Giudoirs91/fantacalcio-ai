let currentMrRound = null;
let selectedMrMatchId = null;
let mrActiveDetailTab = 'tabellino'; // 'tabellino' | 'stats' | 'fisico' | 'ai'
function getAvailableMrRounds() {
    const data = (typeof MATCH_REPORTS_DATA !== 'undefined' && MATCH_REPORTS_DATA) ? MATCH_REPORTS_DATA : {};
    const rounds = Object.keys(data).map(k => parseInt(k, 10)).filter(n => !isNaN(n)).sort((a, b) => a - b);
    return rounds.length > 0 ? rounds : [8, 7, 6, 2];
}
function setMrRound(roundNum) {
    const num = parseInt(roundNum, 10);
    const available = getAvailableMrRounds();
    if (available.includes(num)) {
        currentMrRound = num;
        renderMatchReportsView();
    }
}
function setMrDetailTab(tabName) {
    mrActiveDetailTab = tabName;
    const panes = ['tabellino', 'stats', 'fisico', 'ai'];
    panes.forEach(p => {
        const paneEl = document.getElementById(`mrPane_${p}`);
        const btnEl = document.getElementById(`mrTabBtn_${p}`);
        if (paneEl) paneEl.style.display = (p === tabName) ? 'block' : 'none';
        if (btnEl) btnEl.classList.toggle('active', p === tabName);
    });
}
function openMatchReportModal(matchId) {
    selectedMrMatchId = matchId;
    mrActiveDetailTab = 'tabellino';
    renderMatchReportModalContent(matchId);
    const modal = document.getElementById('matchReportModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}
function closeMatchReportModal() {
    const modal = document.getElementById('matchReportModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
    selectedMrMatchId = null;
}
function getClubBadgeHtml(teamName) {
    const clean = (teamName || '').toLowerCase().replace(/\s+/g, '');
    return `<span class="mr-team-badge-circle" data-team="${clean}">${(teamName || '').substring(0, 3).toUpperCase()}</span>`;
}
function renderMatchReportsView() {
    const container = document.getElementById('viewMatchReports');
    if (!container) return;
    const data = (typeof MATCH_REPORTS_DATA !== 'undefined' && MATCH_REPORTS_DATA) ? MATCH_REPORTS_DATA : {};
    const availableRounds = getAvailableMrRounds();
    const latestRound = availableRounds[availableRounds.length - 1]; // es. 8
    if (currentMrRound === null || !data[currentMrRound]) {
        currentMrRound = latestRound;
    }
    const roundObj = data[currentMrRound] || { matches: [], matches_count: 0 };
    const matches = roundObj.matches || [];
    let totalGoals = 0;
    let totalCleanSheets = 0;
    let totalYellows = 0;
    let totalReds = 0;
    matches.forEach(m => {
        totalGoals += (m.score_home + m.score_away);
        (m.goalkeepers || []).forEach(gk => {
            if (gk.clean_sheet) totalCleanSheets++;
        });
        totalYellows += (m.yellow_cards || []).length;
        totalReds += (m.red_cards || []).length;
    });
    const avgGoals = matches.length > 0 ? (totalGoals / matches.length).toFixed(1) : 0;
    const roundPillsHtml = availableRounds.map(r => {
        const isCurrent = (r === currentMrRound);
        const isLatest = (r === latestRound);
        return `
            <button class="mr-round-pill ${isCurrent ? 'active' : ''}" onclick="setMrRound(${r})" title="Visualizza referti ufficiali Giornata ${r}">
                <span>G${r}</span>
                ${isLatest ? '<span class="mr-pill-badge-live">🔥 Nuovi Referti</span>' : ''}
            </button>
        `;
    }).join('');
    const matchCardsHtml = matches.map(m => {
        const homeMod = m.moduli && m.moduli[0] ? m.moduli[0] : '';
        const awayMod = m.moduli && m.moduli[1] ? m.moduli[1] : '';
        let scorersList = [];
        (m.scorers || []).forEach(s => {
            const countStr = s.goals > 1 ? ` (${s.goals})` : '';
            scorersList.push(`<strong>${s.name}</strong>${countStr} <span class="mr-scorer-team">[${s.team}]</span>`);
        });
        (m.own_goals || []).forEach(og => {
            scorersList.push(`<span class="mr-og-tag">Autogol:</span> ${og.name} [${og.team}]`);
        });
        const scorersHtml = scorersList.length > 0 
            ? scorersList.join(' • ') 
            : '<span style="color:var(--text-muted);font-style:italic;">Nessun gol segnato (0-0)</span>';
        let assistsList = [];
        (m.assisters || []).forEach(a => {
            const countStr = a.assists > 1 ? ` (${a.assists})` : '';
            assistsList.push(`${a.name}${countStr} <span class="mr-scorer-team">[${a.team}]</span>`);
        });
        const assistsHtml = assistsList.length > 0 
            ? `<div class="mr-card-event-row"><span class="mr-event-icon">🎯</span> <span>Assist: ${assistsList.join(' • ')}</span></div>` 
            : '';
        const motm = (m.ai_analysis && m.ai_analysis.man_of_the_match) ? m.ai_analysis.man_of_the_match : '';
        const keyStat = (m.ai_analysis && m.ai_analysis.key_stat) ? m.ai_analysis.key_stat : '';
        const tH = m.team_stats && m.team_stats.home ? m.team_stats.home : {};
        const tA = m.team_stats && m.team_stats.away ? m.team_stats.away : {};
        const possH = tH.possession_pct ? `${Math.round(tH.possession_pct)}%` : '50%';
        const possA = tA.possession_pct ? `${Math.round(tA.possession_pct)}%` : '50%';
        return `
            <div class="mr-match-card" onclick="openMatchReportModal('${m.match_id}')">
                <div class="mr-card-top-bar">
                    <span class="mr-card-league-badge">⚽ Serie A 2026/27 • G${m.giornata}</span>
                    <span class="mr-card-official-tag">Referto Ufficiale ✓</span>
                </div>
                <div class="mr-scoreboard">
                    <div class="mr-team mr-team-home">
                        <div class="mr-team-name">${m.home_team}</div>
                        ${homeMod ? `<span class="mr-mod-pill">${homeMod}</span>` : ''}
                    </div>
                    <div class="mr-score-display">
                        <span class="mr-score-digit">${m.score_home}</span>
                        <span class="mr-score-sep">-</span>
                        <span class="mr-score-digit">${m.score_away}</span>
                    </div>
                    <div class="mr-team mr-team-away">
                        <div class="mr-team-name">${m.away_team}</div>
                        ${awayMod ? `<span class="mr-mod-pill">${awayMod}</span>` : ''}
                    </div>
                </div>
                <div class="mr-card-events">
                    <div class="mr-card-event-row">
                        <span class="mr-event-icon">⚽</span>
                        <div class="mr-event-text">${scorersHtml}</div>
                    </div>
                    ${assistsHtml}
                </div>
                ${motm ? `
                    <div class="mr-card-motm">
                        <span class="mr-motm-icon">🌟</span>
                        <div class="mr-motm-content">
                            <span class="mr-motm-label">Migliore in Campo:</span>
                            <span class="mr-motm-name">${motm}</span>
                        </div>
                    </div>
                ` : ''}
                <div class="mr-card-quick-stats">
                    <div class="mr-qs-item">
                        <span class="mr-qs-label">Possesso</span>
                        <span class="mr-qs-val">${possH} / ${possA}</span>
                    </div>
                    <div class="mr-qs-divider"></div>
                    <div class="mr-qs-item">
                        <span class="mr-qs-label">Focus Match</span>
                        <span class="mr-qs-val" style="font-size:11px;color:#38bdf8;">${keyStat || 'Dati ufficiali'}</span>
                    </div>
                </div>
                <div class="mr-card-footer">
                    <span class="mr-card-cta">
                        <span>🔍 Apri Tabellino &amp; Analisi Tattica</span>
                        <span class="mr-cta-arrow">→</span>
                    </span>
                </div>
            </div>
        `;
    }).join('');
    container.innerHTML = `
        <div class="mr-page-wrapper">
            <!-- HEADER PRINCIPALE MATCH REPORTS -->
            <div class="mr-header-section">
                <div class="mr-header-title-group">
                    <div class="mr-header-badge">
                        <span class="mr-pulse-dot"></span>
                        <span>REFERTI UFFICIALI SERIE A 2026/2027</span>
                    </div>
                    <h1 class="mr-page-title">📑 Match Reports &amp; Analisi Partite</h1>
                    <p class="mr-page-desc">
                        Consultazione dei referti ufficiali di Lega Serie A: tabellini completi, minutaggi, formazioni iniziali, 
                        statistiche di squadra a confronto, ranking fisico-atletici e approfondimenti tattici AI per il Fantacalcio.
                    </p>
                </div>
                <div class="mr-round-selector-bar">
                    <span class="mr-selector-label">Turno di Campionato:</span>
                    <div class="mr-pills-row">
                        ${roundPillsHtml}
                    </div>
                </div>
            </div>
            <!-- STATISTICHE BANNER RIEPILOGATIVO DEL TURNO -->
            <div class="mr-summary-strip">
                <div class="mr-strip-box">
                    <span class="mr-strip-icon">🏟️</span>
                    <div>
                        <div class="mr-strip-num">${matches.length}</div>
                        <div class="mr-strip-lbl">Partite a Referto</div>
                    </div>
                </div>
                <div class="mr-strip-box highlight-cyan">
                    <span class="mr-strip-icon">⚽</span>
                    <div>
                        <div class="mr-strip-num">${totalGoals}</div>
                        <div class="mr-strip-lbl">Gol Segnati (${avgGoals}/m)</div>
                    </div>
                </div>
                <div class="mr-strip-box highlight-green">
                    <span class="mr-strip-icon">🧤</span>
                    <div>
                        <div class="mr-strip-num">${totalCleanSheets}</div>
                        <div class="mr-strip-lbl">Porte Inviolate (CS)</div>
                    </div>
                </div>
                <div class="mr-strip-box highlight-yellow">
                    <span class="mr-strip-icon">🟨</span>
                    <div>
                        <div class="mr-strip-num">${totalYellows} / ${totalReds}</div>
                        <div class="mr-strip-lbl">Ammoniti / Espulsi</div>
                    </div>
                </div>
            </div>
            <!-- GRIGLIA CARDS MATCH REPORT -->
            <div class="mr-matches-grid">
                ${matchCardsHtml}
            </div>
            ${currentMrRound === 8 && matches.length < 10 ? `
                <div class="mr-pending-matches-notice">
                    <div class="mr-notice-icon">⏳</div>
                    <div class="mr-notice-body">
                        <strong>Turno 8 in svolgimento:</strong> Attualmente sono disponibili e processati i referti ufficiali dei primi <strong>6 anticipi e posticipi</strong>. I restanti match verranno acquisiti e indicizzati automaticamente non appena pubblicati dai match report ufficiali di Lega.
                    </div>
                </div>
            ` : ''}
        </div>
        <!-- MODAL DETTAGLIO MATCH REPORT (TABELLINO, STATS, FISICO, AI) -->
        <div id="matchReportModal" class="mr-modal-backdrop" onclick="if(event.target===this) closeMatchReportModal()">
            <div class="mr-modal-container">
                <div id="matchReportModalContent"></div>
            </div>
        </div>
    `;
}
function renderMatchReportModalContent(matchId) {
    const modalContent = document.getElementById('matchReportModalContent');
    if (!modalContent) return;
    const data = (typeof MATCH_REPORTS_DATA !== 'undefined' && MATCH_REPORTS_DATA) ? MATCH_REPORTS_DATA : {};
    const roundObj = data[currentMrRound] || { matches: [] };
    const match = (roundObj.matches || []).find(m => m.match_id === matchId);
    if (!match) {
        modalContent.innerHTML = `<div style="padding:40px;text-align:center;color:#94a3b8;">Dati del match non disponibili.</div>`;
        return;
    }
    const homeMod = match.moduli && match.moduli[0] ? match.moduli[0] : '-';
    const awayMod = match.moduli && match.moduli[1] ? match.moduli[1] : '-';
    const tH = match.team_stats && match.team_stats.home ? match.team_stats.home : {};
    const tA = match.team_stats && match.team_stats.away ? match.team_stats.away : {};
    const renderPlayerRow = (p) => {
        const bonusList = [];
        if (p.goals > 0) bonusList.push(`⚽ +${p.goals * 3}`);
        if (p.assists > 0) bonusList.push(`🎯 +${p.assists}`);
        if (p.own_goals > 0) bonusList.push(`⚠️ -${p.own_goals * 2} Aut`);
        if (p.yellows > 0) bonusList.push(`🟨 -0.5`);
        if (p.reds > 0) bonusList.push(`🟥 -1.0`);
        if (p.clean_sheet && p.is_gk) bonusList.push(`🧤 +1 CS`);
        const bonusHtml = bonusList.length > 0 
            ? `<div class="mr-player-bonus-wrap">${bonusList.map(b => `<span class="mr-p-badge">${b}</span>`).join(' ')}</div>` 
            : '-';
        const roleBadge = p.is_gk ? '<span class="mr-r-badge r-p">P</span>' : '<span class="mr-r-badge r-m">MC</span>';
        return `
            <tr>
                <td class="col-shirt">${p.shirt_num}</td>
                <td class="col-name">
                    <span class="mr-p-name">${p.name}</span>
                    ${p.is_starter ? '<span class="mr-starter-tag">Tit</span>' : '<span class="mr-sub-tag">Sub</span>'}
                </td>
                <td class="col-mins">${p.minutes}'</td>
                <td class="col-shots">${p.shots_target}/${p.shots}</td>
                <td class="col-kp">${p.key_passes}</td>
                <td class="col-rec">${p.recoveries}</td>
                <td class="col-km">${p.km_distance > 0 ? `${p.km_distance} km` : '-'}</td>
                <td class="col-bonus">${bonusHtml}</td>
            </tr>
        `;
    };
    const homeStartersRows = (match.home_starters || []).map(renderPlayerRow).join('');
    const homeBenchRows = (match.home_bench || []).map(renderPlayerRow).join('');
    const awayStartersRows = (match.away_starters || []).map(renderPlayerRow).join('');
    const awayBenchRows = (match.away_bench || []).map(renderPlayerRow).join('');
    const buildStatBar = (label, valH, valA, isPct = false, suffix = '') => {
        const numH = parseFloat(valH) || 0;
        const numA = parseFloat(valA) || 0;
        const total = (numH + numA) > 0 ? (numH + numA) : 1;
        const pctH = isPct ? numH : Math.round((numH / total) * 100);
        const pctA = isPct ? numA : (100 - pctH);
        return `
            <div class="mr-comp-item">
                <div class="mr-comp-header">
                    <span class="mr-comp-val-h ${numH >= numA ? 'is-best' : ''}">${valH}${suffix}</span>
                    <span class="mr-comp-label">${label}</span>
                    <span class="mr-comp-val-a ${numA >= numH ? 'is-best' : ''}">${valA}${suffix}</span>
                </div>
                <div class="mr-comp-bar-track">
                    <div class="mr-comp-bar-fill-h" style="width:${pctH}%;"></div>
                    <div class="mr-comp-bar-fill-a" style="width:${pctA}%;"></div>
                </div>
            </div>
        `;
    };
    const statsBarsHtml = `
        <div class="mr-stats-comparison-box">
            ${buildStatBar("Possesso Palla", tH.possession_pct ? Math.round(tH.possession_pct) : 50, tA.possession_pct ? Math.round(tA.possession_pct) : 50, true, "%")}
            ${buildStatBar("Tiri Totali", tH.total_shots || 0, tA.total_shots || 0)}
            ${buildStatBar("Tiri nello Specchio", tH.shots_on_target || 0, tA.shots_on_target || 0)}
            ${buildStatBar("Occasioni / Key Passes", tH.key_passes || 0, tA.key_passes || 0)}
            ${buildStatBar("Palle Recuperate", tH.recoveries || 0, tA.recoveries || 0)}
            ${buildStatBar("Dribbling Riusciti", tH.dribbles || 0, tA.dribbles || 0)}
            ${buildStatBar("Passaggi 3/4 Riusciti", tH.passes_final_third || 0, tA.passes_final_third || 0)}
            ${buildStatBar("Km Percorsi Squadra", tH.team_distance_km ? tH.team_distance_km.toFixed(1) : 0, tA.team_distance_km ? tA.team_distance_km.toFixed(1) : 0, false, " km")}
        </div>
    `;
    const topKmPlayers = (match.physical_leaders && match.physical_leaders.top_km) ? match.physical_leaders.top_km : [];
    const topSpeedPlayers = (match.physical_leaders && match.physical_leaders.top_speed) ? match.physical_leaders.top_speed : [];
    const topKmHtml = topKmPlayers.map((p, idx) => `
        <div class="mr-phys-card">
            <span class="mr-phys-rank">#${idx + 1}</span>
            <div class="mr-phys-info">
                <span class="mr-phys-name">${p.name} <small>[${p.team}]</small></span>
                <span class="mr-phys-sub">${p.minutes} minuti giocati</span>
            </div>
            <div class="mr-phys-val">${p.km_distance} <small>km</small></div>
        </div>
    `).join('');
    const topSpeedHtml = topSpeedPlayers.map((p, idx) => `
        <div class="mr-phys-card speed-card">
            <span class="mr-phys-rank">#${idx + 1}</span>
            <div class="mr-phys-info">
                <span class="mr-phys-name">${p.name} <small>[${p.team}]</small></span>
                <span class="mr-phys-sub">Picco di sprint</span>
            </div>
            <div class="mr-phys-val">${p.sprint_speed_max} <small>km/h</small></div>
        </div>
    `).join('');
    const aiAnalysis = match.ai_analysis || {};
    modalContent.innerHTML = `
        <div class="mr-modal-header">
            <div class="mr-modal-title-wrap">
                <span class="mr-modal-subtitle">REFERTO UFFICIALE SERIE A 2026/27 • GIORNATA ${match.giornata}</span>
                <h2 class="mr-modal-title">${match.match_title}</h2>
            </div>
            <button class="mr-modal-close" onclick="closeMatchReportModal()" title="Chiudi Finestra">✕</button>
        </div>
        <!-- HERO SCOREBOARD MODAL -->
        <div class="mr-modal-hero">
            <div class="mr-hero-team mr-hero-home">
                <div class="mr-hero-team-name">${match.home_team}</div>
                <div class="mr-hero-mod-badge">Modulo Tattico: ${homeMod}</div>
            </div>
            <div class="mr-hero-score">
                <span>${match.score_home}</span>
                <span class="mr-hero-sep">:</span>
                <span>${match.score_away}</span>
            </div>
            <div class="mr-hero-team mr-hero-away">
                <div class="mr-hero-team-name">${match.away_team}</div>
                <div class="mr-hero-mod-badge">Modulo Tattico: ${awayMod}</div>
            </div>
        </div>
        <!-- NAVIGATION TABS DEL MODAL -->
        <div class="mr-modal-nav-tabs">
            <button class="mr-modal-tab active" id="mrTabBtn_tabellino" onclick="setMrDetailTab('tabellino')">📋 Tabellino &amp; Formazioni</button>
            <button class="mr-modal-tab" id="mrTabBtn_stats" onclick="setMrDetailTab('stats')">📊 Statistiche a Confronto</button>
            <button class="mr-modal-tab" id="mrTabBtn_fisico" onclick="setMrDetailTab('fisico')">⚡ Performance Fisiche</button>
            <button class="mr-modal-tab" id="mrTabBtn_ai" onclick="setMrDetailTab('ai')">🧠 Analisi Tattica &amp; Fanta AI</button>
        </div>
        <div class="mr-modal-body">
            <!-- PANE 1: TABELLINO -->
            <div id="mrPane_tabellino" class="mr-modal-pane" style="display:block;">
                <div class="mr-lineups-grid">
                    <!-- CASA -->
                    <div class="mr-lineup-column">
                        <div class="mr-col-header">
                            <span class="mr-col-team-name">🏠 ${match.home_team} (${homeMod})</span>
                            <span class="mr-col-badge">Titolari</span>
                        </div>
                        <div class="mr-table-scroll">
                            <table class="mr-player-table">
                                <thead>
                                    <tr>
                                        <th class="col-shirt">#</th>
                                        <th class="col-name">Calciatore</th>
                                        <th class="col-mins">Min</th>
                                        <th class="col-shots">Tiri</th>
                                        <th class="col-kp">KP</th>
                                        <th class="col-rec">Rec</th>
                                        <th class="col-km">Km</th>
                                        <th class="col-bonus">Bonus</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${homeStartersRows}
                                </tbody>
                            </table>
                        </div>
                        ${homeBenchRows ? `
                            <div class="mr-bench-header">Subentrati a partita in corso:</div>
                            <div class="mr-table-scroll">
                                <table class="mr-player-table mr-bench-table">
                                    <tbody>
                                        ${homeBenchRows}
                                    </tbody>
                                </table>
                            </div>
                        ` : ''}
                    </div>
                    <!-- TRASFERTA -->
                    <div class="mr-lineup-column">
                        <div class="mr-col-header">
                            <span class="mr-col-team-name">✈️ ${match.away_team} (${awayMod})</span>
                            <span class="mr-col-badge">Titolari</span>
                        </div>
                        <div class="mr-table-scroll">
                            <table class="mr-player-table">
                                <thead>
                                    <tr>
                                        <th class="col-shirt">#</th>
                                        <th class="col-name">Calciatore</th>
                                        <th class="col-mins">Min</th>
                                        <th class="col-shots">Tiri</th>
                                        <th class="col-kp">KP</th>
                                        <th class="col-rec">Rec</th>
                                        <th class="col-km">Km</th>
                                        <th class="col-bonus">Bonus</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${awayStartersRows}
                                </tbody>
                            </table>
                        </div>
                        ${awayBenchRows ? `
                            <div class="mr-bench-header">Subentrati a partita in corso:</div>
                            <div class="mr-table-scroll">
                                <table class="mr-player-table mr-bench-table">
                                    <tbody>
                                        ${awayBenchRows}
                                    </tbody>
                                </table>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
            <!-- PANE 2: STATISTICHE SQUADRA -->
            <div id="mrPane_stats" class="mr-modal-pane" style="display:none;">
                <div class="mr-pane-header-group">
                    <h3 class="mr-pane-title">Statistiche Ufficiali di Squadra a Confronto</h3>
                    <p class="mr-pane-sub">Dati aggregati estratti direttamente dai tabulati tecnici di Lega Serie A.</p>
                </div>
                ${statsBarsHtml}
            </div>
            <!-- PANE 3: FISICO-ATLETICO -->
            <div id="mrPane_fisico" class="mr-modal-pane" style="display:none;">
                <div class="mr-pane-header-group">
                    <h3 class="mr-pane-title">Performance Chilometriche &amp; Velocistiche</h3>
                    <p class="mr-pane-sub">Leader per distanza totale percorsa e picco massimo di velocità in sprint.</p>
                </div>
                <div class="mr-phys-grid">
                    <div class="mr-phys-col">
                        <div class="mr-phys-col-title">🏃 Top 3 Distanza Totale (Km)</div>
                        <div class="mr-phys-list">
                            ${topKmHtml || '<div style="color:#64748b;font-size:12px;">Dati atletici non rilevati.</div>'}
                        </div>
                    </div>
                    <div class="mr-phys-col">
                        <div class="mr-phys-col-title">⚡ Top 3 Velocità Sprint (Km/h)</div>
                        <div class="mr-phys-list">
                            ${topSpeedHtml || '<div style="color:#64748b;font-size:12px;">Dati velocistici non rilevati.</div>'}
                        </div>
                    </div>
                </div>
            </div>
            <!-- PANE 4: ANALISI TATTICA & FANTA AI -->
            <div id="mrPane_ai" class="mr-modal-pane" style="display:none;">
                <div class="mr-ai-report-card">
                    <div class="mr-ai-header">
                        <span class="mr-ai-icon">🤖</span>
                        <div>
                            <h3 class="mr-ai-title">Analisi Tattica &amp; Fantacalcistica AI</h3>
                            <span class="mr-ai-tag">Algoritmo Predittivo Fanta Master AI</span>
                        </div>
                    </div>
                    <div class="mr-ai-section">
                        <div class="mr-ai-sec-title">📝 Sintesi Tattica del Match</div>
                        <p class="mr-ai-sec-text">${aiAnalysis.summary || 'Sintesi del match non disponibile.'}</p>
                    </div>
                    <div class="mr-ai-section highlight-fanta">
                        <div class="mr-ai-sec-title">🎯 Implicazioni per il Fantacalcio</div>
                        <p class="mr-ai-sec-text">${aiAnalysis.fantacalcio_impact || 'Nessuna nota specifica registrata.'}</p>
                    </div>
                    <div class="mr-ai-split-boxes">
                        <div class="mr-ai-box">
                            <span class="mr-box-badge">⭐ MIGLIORE IN CAMPO</span>
                            <div class="mr-box-body">${aiAnalysis.man_of_the_match || 'N/D'}</div>
                        </div>
                        <div class="mr-ai-box">
                            <span class="mr-box-badge">📊 STATISTICA CHIAVE</span>
                            <div class="mr-box-body">${aiAnalysis.key_stat || 'N/D'}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
window.setMrRound = setMrRound;
window.setMrDetailTab = setMrDetailTab;
window.openMatchReportModal = openMatchReportModal;
window.closeMatchReportModal = closeMatchReportModal;
window.renderMatchReportsView = renderMatchReportsView;