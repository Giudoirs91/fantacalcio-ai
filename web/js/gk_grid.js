// ==============================================================================
// MODULO GRIGLIA PORTIERI E ALTERNANZA CASA/TRASFERTA
// ==============================================================================

let gkSubTab = 'pairs';
let gkFiltersPopulated = false;

function switchGkSubTab(tab) {
    gkSubTab = tab;
    const btnP = document.getElementById('btnGkPairs');
    const btnM = document.getElementById('btnGkMatrix');
    if (btnP) btnP.classList.toggle('active', tab === 'pairs');
    if (btnM) btnM.classList.toggle('active', tab === 'matrix');
    
    const pView = document.getElementById('gkPairsView');
    const mView = document.getElementById('gkMatrixView');
    const fPanel = document.getElementById('gkFilterPanel');
    
    if (pView) pView.style.display = (tab === 'pairs') ? 'block' : 'none';
    if (mView) mView.style.display = (tab === 'matrix') ? 'block' : 'none';
    if (fPanel) fPanel.style.display = (tab === 'pairs') ? 'flex' : 'none';
    
    if (tab === 'matrix') {
        renderGkMatrix();
    }
}

function getPrimaryGk(teamName) {
    const teamGks = PLAYERS.filter(p => p.role === 'P' && p.team === teamName);
    if (!teamGks || teamGks.length === 0) return { name: 'Portiere ' + teamName, prezzo_cons: 1, ovr: 60 };
    teamGks.sort((a, b) => b.ovr - a.ovr);
    return teamGks[0];
}

function renderGkGrid() {
    if (!GK_DATA || !GK_DATA.pairs) return;

    const selTeam = document.getElementById('filterGkTeam');
    const selPlayer = document.getElementById('filterGkPlayer');
    if (!gkFiltersPopulated) {
        if (selTeam && GK_DATA.teams) {
            GK_DATA.teams.forEach(tm => {
                const opt = document.createElement('option');
                opt.value = tm;
                opt.textContent = tm;
                selTeam.appendChild(opt);
            });
        }
        if (selPlayer) {
            const allGks = PLAYERS.filter(p => p.role === 'P');
            allGks.sort((a, b) => b.ovr - a.ovr || a.name.localeCompare(b.name));
            allGks.forEach(gk => {
                const opt = document.createElement('option');
                opt.value = gk.id;
                opt.textContent = `${gk.name} (${gk.team}) - OVR ${gk.ovr} (${gk.prezzo_cons} CR)`;
                selPlayer.appendChild(opt);
            });
        }
        gkFiltersPopulated = true;
    }

    const selectedPlayerId = selPlayer ? selPlayer.value : 'ALL';
    let selectedTeam = selTeam ? selTeam.value : 'ALL';

    let targetPlayerTeam = null;
    if (selectedPlayerId !== 'ALL') {
        const p = PLAYERS.find(pl => pl.id === parseInt(selectedPlayerId, 10));
        if (p) targetPlayerTeam = p.team;
    }

    const filterTeam = targetPlayerTeam || selectedTeam;
    const tierEl = document.getElementById('filterGkTier');
    const selectedTier = tierEl ? tierEl.value : 'ALL';

    let filteredPairs = GK_DATA.pairs.filter(pr => {
        if (filterTeam !== 'ALL' && pr.teamA !== filterTeam && pr.teamB !== filterTeam) return false;
        if (selectedTier === 'perfect' && pr.tier !== 'perfect') return false;
        if (selectedTier === 'elite' && pr.tier !== 'elite' && pr.tier !== 'perfect') return false;
        if (selectedTier === 'optimal' && pr.tier !== 'optimal' && pr.tier !== 'elite' && pr.tier !== 'perfect') return false;
        return true;
    });

    const pairsWithGks = filteredPairs.map(pr => {
        const gkA = getPrimaryGk(pr.teamA);
        const gkB = getPrimaryGk(pr.teamB);
        const totalCost = (gkA.prezzo_cons || 1) + (gkB.prezzo_cons || 1);
        return {
            ...pr,
            gkA,
            gkB,
            totalCost
        };
    });

    const tableDiv = document.getElementById('gkGridTable');
    if (!tableDiv) return;

    if (pairsWithGks.length === 0) {
        tableDiv.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);">Nessuna combinazione trovata con i filtri selezionati.</div>';
        return;
    }

    let html = `
        <div class="table-wrapper">
            <table class="fanta-table">
                <thead>
                    <tr>
                        <th>Coppia Club 2026/27</th>
                        <th>Portieri Titolari Stimati</th>
                        <th style="text-align:center;">Gare Casa</th>
                        <th style="text-align:center;">Malus (Trasf. Insieme)</th>
                        <th style="text-align:center;">Solidità xGA Media</th>
                        <th style="text-align:center;">Costo Totale Stimato</th>
                        <th>Valutazione Alternanza</th>
                    </tr>
                </thead>
                <tbody>
    `;

    pairsWithGks.forEach(pr => {
        const tStatA = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[pr.teamA]) ? TEAM_STATS_DB[pr.teamA] : null;
        const tStatB = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[pr.teamB]) ? TEAM_STATS_DB[pr.teamB] : null;
        let xgaAvgHtml = '<span style="color:var(--text-muted);font-size:12px;">-</span>';
        if (tStatA && tStatB && tStatA.xga_team !== undefined && tStatB.xga_team !== undefined) {
            const avgXga = ((tStatA.xga_team + tStatB.xga_team) / 2.0).toFixed(2);
            const xgaColor = avgXga <= 1.5 ? '#4ade80' : (avgXga <= 3.0 ? '#38bdf8' : '#fbbf24');
            xgaAvgHtml = `<b style="color:${xgaColor};font-size:13px;">${avgXga} xGA</b><div style="font-size:10px;color:var(--text-muted);">CS: ${(tStatA.clean_sheets || 0) + (tStatB.clean_sheets || 0)}</div>`;
        }

        html += `
            <tr>
                <td>
                    <div style="font-size:14px;font-weight:900;color:#fff;">
                        <span>${pr.teamA}</span> <span style="color:var(--accent-gold);font-weight:400;">+</span> <span>${pr.teamB}</span>
                    </div>
                </td>
                <td>
                    <div style="font-size:12px;color:var(--accent-cyan);font-weight:700;">
                        ${pr.gkA.name} <span style="color:var(--text-muted);font-size:11px;">(${pr.gkA.prezzo_cons} CR)</span> • ${pr.gkB.name} <span style="color:var(--text-muted);font-size:11px;">(${pr.gkB.prezzo_cons} CR)</span>
                    </div>
                </td>
                <td style="text-align:center;">
                    <b style="color:#4ade80;font-size:14px;">${pr.home_games}</b><span style="color:var(--text-muted);font-size:11px;">/38 (${pr.pct}%)</span>
                </td>
                <td style="text-align:center;">
                    <b style="color:${pr.diff <= 4 ? 'var(--accent-green)' : (pr.diff <= 6 ? 'var(--accent-cyan)' : 'var(--accent-gold)')};">${pr.diff}</b> <span style="font-size:11px;color:var(--text-muted);">partite</span>
                </td>
                <td style="text-align:center;">
                    ${xgaAvgHtml}
                </td>
                <td style="text-align:center;">
                    <span style="color:var(--accent-gold);font-weight:800;font-size:13px;">${pr.totalCost} CR</span>
                </td>
                <td>
                    <span class="ai-advice-badge ${pr.tier === 'perfect' ? 'top' : (pr.tier === 'elite' ? 'buy' : 'lowcost')}">${pr.label}</span>
                </td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;
    tableDiv.innerHTML = html;
}

function renderGkMatrix() {
    const container = document.getElementById('gkMatrixContainer');
    if (!container || !GK_DATA || !GK_DATA.matrix || !GK_DATA.teams) return;

    const teams = GK_DATA.teams;
    let html = `
        <div class="table-wrapper">
            <table class="fanta-table" style="font-size:11px;">
                <thead>
                    <tr>
                        <th style="text-align:left;padding-left:12px;min-width:110px;">Club / Squadra</th>
    `;

    teams.forEach(t => {
        const abbr = t.substring(0, 3).toUpperCase();
        html += `<th style="text-align:center;" title="${t}">${abbr}</th>`;
    });

    html += `</tr></thead><tbody>`;

    teams.forEach(rowTeam => {
        html += `<tr><td style="font-weight:800;color:#fff;">${rowTeam}</td>`;
        teams.forEach(colTeam => {
            if (rowTeam === colTeam) {
                html += `<td style="text-align:center;color:var(--text-muted);">-</td>`;
            } else {
                const val = GK_DATA.matrix[rowTeam] ? GK_DATA.matrix[rowTeam][colTeam] : null;
                if (val === undefined || val === null) {
                    html += `<td style="text-align:center;color:var(--text-muted);">-</td>`;
                } else {
                    let color = '#f87171';
                    if (val === 0) color = '#4ade80';
                    else if (val <= 4) color = '#22c55e';
                    else if (val <= 6) color = '#00f2fe';
                    else if (val <= 8) color = '#fbbf24';
                    
                    html += `<td style="text-align:center;font-weight:800;color:${color};">${val}</td>`;
                }
            }
        });
        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}
