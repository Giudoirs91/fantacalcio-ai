function getMatchInfoForTeamAndRound(teamName, roundNum) {
    if (typeof OFFICIAL_CALENDAR_2026_27 === 'undefined' || !Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        return null;
    }
    const rObj = OFFICIAL_CALENDAR_2026_27.find(r => r.giornata === roundNum);
    if (!rObj || !rObj.matches) return null;
    const tClean = (teamName || '').toUpperCase().trim();
    for (const m of rObj.matches) {
        const hClean = (m.home || '').toUpperCase().trim();
        const aClean = (m.away || '').toUpperCase().trim();
        if (hClean === tClean) {
            return {
                opponent: m.away,
                is_home: true,
                match_str: `${m.home} vs ${m.away}`,
                date: rObj.date || ''
            };
        }
        if (aClean === tClean) {
            return {
                opponent: m.home,
                is_home: false,
                match_str: `${m.away} @ ${m.home}`,
                date: rObj.date || ''
            };
        }
    }
    return null;
}
function computeBonusMalusStr(v) {
    if (!v) return '-';
    if (v.bonus_malus_str && v.bonus_malus_str !== '-' && v.bonus_malus_str !== 'Nessun bonus' && !v.bonus_malus_str.includes('undefined')) {
        return v.bonus_malus_str;
    }
    const parts = [];
    const gf = v.gf || 0;
    const ass = v.ass || 0;
    const rp = v.rp || 0;
    const gs = v.gs || 0;
    const rs = v.rs || 0;
    const au = v.au || 0;
    const amm = v.amm || 0;
    const esp = v.esp || 0;
    if (gf > 0) parts.push(`+${Math.round(gf * 3)} (${Math.round(gf)}G)`);
    if (ass > 0) parts.push(`+${Math.round(ass)} (${Math.round(ass)}A)`);
    if (rp > 0) parts.push(`+${Math.round(rp * 3)} (Rig.Par)`);
    if (gs > 0) parts.push(`-${Math.round(gs)} (${Math.round(gs)}GS)`);
    if (rs > 0) parts.push(`-3 (Rig.Sbagliato)`);
    if (au > 0) parts.push(`-${Math.round(au * 2)} (Autogol)`);
    if (amm > 0) parts.push(`-0.5 (Amm)`);
    if (esp > 0) parts.push(`-1 (Esp)`);
    if (parts.length > 0) return parts.join(', ');
    if (v.voto !== null && v.voto !== undefined) return 'Nessun bonus';
    return '-';
}
function renderMantraQuickBadges(mantraStr) {
    if (!mantraStr || mantraStr === '-' || mantraStr === 'null' || mantraStr === 'undefined') {
        return `<span style="color:var(--text-muted);font-size:12px;font-weight:600;">-</span>`;
    }
    const roles = mantraStr.split(/[;,/ ]+/).filter(Boolean);
    if (roles.length === 0) return `<span style="color:var(--text-muted);font-size:12px;font-weight:600;">-</span>`;
    return roles.map(r => `<span class="mantra-pill ${r.toLowerCase()}">${r}</span>`).join('');
}
function switchProfileTab(tabName) {
    const tabs = ['overview', 'advanced', 'tactics'];
    tabs.forEach(t => {
        const pane = document.getElementById(`profileTabPane_${t}`);
        const btn = document.getElementById(`profileTabBtn_${t}`);
        if (pane) pane.style.display = (t === tabName) ? 'block' : 'none';
        if (btn) btn.classList.toggle('active', t === tabName);
    });
}
function calculatePercentile(val, allVals) {
    if (!allVals || allVals.length === 0 || val === null || val === undefined) return 50;
    const sorted = [...allVals].filter(v => v !== null && v !== undefined && !isNaN(v)).sort((a, b) => a - b);
    if (sorted.length === 0) return 50;
    const countBelow = sorted.filter(v => v < val).length;
    return Math.round((countBelow / sorted.length) * 100);
}
function generateRadarChartSvg(player) {
    const role = player.role;
    const sameRolePlayers = PLAYERS.filter(p => p.role === role);
    let axes = [];
    if (role === 'P') {
        const csVals = sameRolePlayers.map(p => p.clean_sheets_2627 || p.clean_sheets_2526 || 0);
        const saveVals = sameRolePlayers.map(p => p.save_pct_2627 || p.save_pct_2526 || 0);
        const gpVals = sameRolePlayers.map(p => p.goals_prevented_2627 || p.goals_prevented_2526 || 0);
        const mvVals = sameRolePlayers.map(p => p.mv_2627 || p.mv || 6.0);
        const titVals = sameRolePlayers.map(p => p.titolarita || 50);
        const parateVals = sameRolePlayers.map(p => p.parate_2627 || 0);
        axes = [
            { label: 'Clean Sheets', pct: calculatePercentile(player.clean_sheets_2627 || player.clean_sheets_2526 || 0, csVals), raw: `${player.clean_sheets_2627 || player.clean_sheets_2526 || 0} CS` },
            { label: '% Parate', pct: calculatePercentile(player.save_pct_2627 || player.save_pct_2526 || 0, saveVals), raw: `${player.save_pct_2627 || player.save_pct_2526 || 0}%` },
            { label: 'Gol Evitati', pct: calculatePercentile(player.goals_prevented_2627 || player.goals_prevented_2526 || 0, gpVals), raw: `${player.goals_prevented_2627 || player.goals_prevented_2526 || 0} GP` },
            { label: 'Media Voto (MV)', pct: calculatePercentile(player.mv_2627 || player.mv || 6.0, mvVals), raw: `${(player.mv_2627 || player.mv || 6.0).toFixed(2)}` },
            { label: 'Titolarità', pct: calculatePercentile(player.titolarita || 50, titVals), raw: `${player.titolarita || 50}%` },
            { label: 'Volume Parate', pct: calculatePercentile(player.parate_2627 || 0, parateVals), raw: `${player.parate_2627 || 0}` }
        ];
    } else if (role === 'D') {
        const xgVals = sameRolePlayers.map(p => p.xg90_2627 || p.xg90_2526 || 0);
        const xaVals = sameRolePlayers.map(p => p.xa90_2627 || p.xa90_2526 || 0);
        const recVals = sameRolePlayers.map(p => p.recuperi_2627 || 0);
        const mvVals = sameRolePlayers.map(p => p.mv_2627 || p.mv || 6.0);
        const titVals = sameRolePlayers.map(p => p.titolarita || 50);
        const kpVals = sameRolePlayers.map(p => p.chances_created_2627 || p.key_passes_2526 || 0);
        axes = [
            { label: 'Spinta Off. (xG/90)', pct: calculatePercentile(player.xg90_2627 || player.xg90_2526 || 0, xgVals), raw: `${player.xg90_2627 || player.xg90_2526 || 0}` },
            { label: 'Cross & Assist (xA/90)', pct: calculatePercentile(player.xa90_2627 || player.xa90_2526 || 0, xaVals), raw: `${player.xa90_2627 || player.xa90_2526 || 0}` },
            { label: 'Occasioni Create (KP)', pct: calculatePercentile(player.chances_created_2627 || player.key_passes_2526 || 0, kpVals), raw: `${player.chances_created_2627 || player.key_passes_2526 || 0}` },
            { label: 'Recuperi Palla (Mod)', pct: calculatePercentile(player.recuperi_2627 || 0, recVals), raw: `${player.recuperi_2627 || 0}` },
            { label: 'Media Voto (MV)', pct: calculatePercentile(player.mv_2627 || player.mv || 6.0, mvVals), raw: `${(player.mv_2627 || player.mv || 6.0).toFixed(2)}` },
            { label: 'Titolarità', pct: calculatePercentile(player.titolarita || 50, titVals), raw: `${player.titolarita || 50}%` }
        ];
    } else {
        const xgVals = sameRolePlayers.map(p => p.xg90_2627 || p.xg90_2526 || 0);
        const xgotVals = sameRolePlayers.map(p => p.xgot_2627 || p.xgot_2526 || 0);
        const xaVals = sameRolePlayers.map(p => p.xa90_2627 || p.xa90_2526 || 0);
        const bcVals = sameRolePlayers.map(p => p.big_chances_created_2627 || p.big_chances_created_2526 || 0);
        const dribVals = sameRolePlayers.map(p => p.won_contest_2627 || 0);
        const fmVals = sameRolePlayers.map(p => p.fm_2627 || p.fm || 6.0);
        axes = [
            { label: 'Pericolosità (xG/90)', pct: calculatePercentile(player.xg90_2627 || player.xg90_2526 || 0, xgVals), raw: `${player.xg90_2627 || player.xg90_2526 || 0}` },
            { label: 'Qualità Tiro (xGOT)', pct: calculatePercentile(player.xgot_2627 || player.xgot_2526 || 0, xgotVals), raw: `${player.xgot_2627 || player.xgot_2526 || 0}` },
            { label: 'Rifinitura (xA/90)', pct: calculatePercentile(player.xa90_2627 || player.xa90_2526 || 0, xaVals), raw: `${player.xa90_2627 || player.xa90_2526 || 0}` },
            { label: 'Grandi Occasioni', pct: calculatePercentile(player.big_chances_created_2627 || player.big_chances_created_2526 || 0, bcVals), raw: `${player.big_chances_created_2627 || player.big_chances_created_2526 || 0}` },
            { label: '1vs1 & Dribbling', pct: calculatePercentile(player.won_contest_2627 || 0, dribVals), raw: `${player.won_contest_2627 || 0}/90` },
            { label: 'FantaMedia (FM)', pct: calculatePercentile(player.fm_2627 || player.fm || 6.0, fmVals), raw: `${(player.fm_2627 || player.fm || 6.0).toFixed(2)}` }
        ];
    }
    const size = 360;
    const center = size / 2;
    const radius = 96;
    const numAxes = axes.length;
    const angleStep = (Math.PI * 2) / numAxes;
    let webCirclesHtml = '';
    [0.25, 0.50, 0.75, 1.0].forEach(level => {
        const pts = [];
        for (let i = 0; i < numAxes; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const r = radius * level;
            pts.push(`${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`);
        }
        webCirclesHtml += `<polygon points="${pts.join(' ')}" fill="none" stroke="rgba(255,255,255,${level === 0.5 ? '0.18' : '0.08'})" stroke-width="${level === 0.5 ? '1.5' : '1'}" stroke-dasharray="${level === 0.5 ? '3,3' : 'none'}" />`;
    });
    let axisLinesHtml = '';
    let axisLabelsHtml = '';
    const polyPoints = [];
    axes.forEach((axis, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const x2 = center + radius * Math.cos(angle);
        const y2 = center + radius * Math.sin(angle);
        axisLinesHtml += `<line x1="${center}" y1="${center}" x2="${x2}" y2="${y2}" stroke="rgba(255,255,255,0.12)" stroke-width="1" />`;
        const pctClamped = Math.max(12, Math.min(98, axis.pct));
        const dataR = (radius * pctClamped) / 100;
        const dataX = center + dataR * Math.cos(angle);
        const dataY = center + dataR * Math.sin(angle);
        polyPoints.push(`${dataX},${dataY}`);
        const labelR = radius + 22;
        const labelX = center + labelR * Math.cos(angle);
        const labelY = center + labelR * Math.sin(angle) + 4;
        let textAnchor = 'middle';
        if (Math.cos(angle) > 0.3) textAnchor = 'start';
        else if (Math.cos(angle) < -0.3) textAnchor = 'end';
        axisLabelsHtml += `
            <text x="${labelX}" y="${labelY}" text-anchor="${textAnchor}" fill="var(--text-secondary)" font-size="9" font-weight="700">
                ${axis.label}
            </text>
            <text x="${labelX}" y="${labelY + 11}" text-anchor="${textAnchor}" fill="var(--accent-cyan)" font-size="9" font-weight="800">
                P${axis.pct} <tspan fill="var(--text-muted)" font-size="8">(${axis.raw})</tspan>
            </text>
        `;
    });
    const roleColors = { P: '#f59e0b', D: '#10b981', C: '#38bdf8', A: '#f43f5e' };
    const polyColor = roleColors[role] || '#38bdf8';
    return `
        <div class="radar-chart-wrapper">
            <div class="radar-title-bar">
                <div>
                    <b style="color:#fff;font-size:12.5px;">Radar Percentilare a 6 Assi (vs Pari-Ruolo Serie A)</b>
                    <div style="font-size:10.5px;color:var(--text-muted);">Percentile 0-100: più l'area è espansa, più il calciatore è dominante nel reparto</div>
                </div>
                <span class="role-badge ${role}" style="font-size:10px;padding:2px 6px;">${role}</span>
            </div>
            <div style="display:flex;justify-content:center;align-items:center;padding:10px 0;">
                <svg viewBox="0 0 ${size} 330" class="radar-svg-canvas">
                    ${webCirclesHtml}
                    ${axisLinesHtml}
                    <!-- Data Polygon -->
                    <polygon points="${polyPoints.join(' ')}" fill="${polyColor}" fill-opacity="0.25" stroke="${polyColor}" stroke-width="2.5" />
                    <!-- Axis Labels -->
                    ${axisLabelsHtml}
                </svg>
            </div>
        </div>
    `;
}
function computeExpectedFantaMedia(player) {
    const has2627 = player.has_data_2627 && player.presenze_2627 > 0;
    const presenze = has2627 ? player.presenze_2627 : (player.presenze || 1);
    const mv = has2627 ? (player.mv_2627 || 6.0) : (player.mv || 6.0);
    const realFm = has2627 ? (player.fm_2627 || mv) : (player.fm || mv);
    if (player.xfm !== undefined && player.xfm !== null) {
        const xfm = Number(player.xfm);
        const delta = +(Number(realFm) - xfm).toFixed(2);
        return { xfm, realFm: +Number(realFm).toFixed(2), delta, has2627 };
    }
    let xg = 0, xa = 0, malus = 0;
    if (player.role === 'P') {
        const gs = has2627 ? (player.gol_subiti_2627 || 0) : (player.gs || 0);
        const cs = has2627 ? (player.clean_sheets_2627 || 0) : (player.clean_sheets_2526 || 0);
        const xfm = +(mv - (gs / presenze) + (cs * 0.5 / presenze)).toFixed(2);
        const delta = +(realFm - xfm).toFixed(2);
        return { xfm, realFm: +realFm.toFixed(2), delta, has2627 };
    } else {
        xg = has2627 ? (player.xg_2627 || (player.xg90_2627 ? player.xg90_2627 * (player.minuti_2627 || 90) / 90 : 0)) : (player.xg_2526 || (player.xg90_2526 ? player.xg90_2526 * (player.mins_2526 || 900) / 90 : 0));
        xa = has2627 ? (player.xa_2627 || (player.xa90_2627 ? player.xa90_2627 * (player.minuti_2627 || 90) / 90 : 0)) : (player.xa_2526 || (player.xa90_2526 ? player.xa90_2526 * (player.mins_2526 || 900) / 90 : 0));
        malus = has2627 ? ((player.amm_2627 || 0) * 0.5 + (player.esp_2627 || 0) * 1.0) : ((player.amm || 0) * 0.5 + (player.esp || 0) * 1.0);
        const xgot = has2627 ? (player.xgot_2627 || xg) : (player.xgot_2526 || xg);
        let shotPlacementMult = 1.0;
        if ((player.role === 'A' || player.role === 'C') && xgot !== undefined && xgot !== null && xg >= 0.8) {
            try {
                const ratio = Number(xgot) / Number(xg);
                shotPlacementMult = Math.max(0.90, Math.min(1.10, ratio));
            } catch (e) {
                shotPlacementMult = 1.0;
            }
        }
        const bonusAttesi = (xg * shotPlacementMult * 3.0) + (xa * 1.0);
        const xfm = +(mv + ((bonusAttesi - malus) / presenze)).toFixed(2);
        const delta = +(realFm - xfm).toFixed(2);
        return { xfm, realFm: +realFm.toFixed(2), delta, has2627 };
    }
}
function generateInjuryHistoryCardHtml(p) {
    const fragScore = p.fragility_score !== undefined && p.fragility_score !== null ? p.fragility_score : 20;
    const fragTier = p.fragility_tier || (fragScore < 25 ? '🟢 Roccia (Massima Affidabilità)' : (fragScore < 45 ? '🟢 Stabile (Basso Rischio)' : (fragScore < 65 ? '🟡 Attenzione (Qualche Acciacco)' : (fragScore < 80 ? '🟠 Fragile (Frequenti Stop)' : '🔴 Cristallo (Rischio Altissimo)'))));
    const dispPct = p.disponibilita_pct !== undefined && p.disponibilita_pct !== null ? p.disponibilita_pct : 95.0;
    const partitePerse = p.partite_saltate_totali !== undefined && p.partite_saltate_totali !== null ? p.partite_saltate_totali : 0;
    const giorniStop = p.giorni_stop_totali !== undefined && p.giorni_stop_totali !== null ? p.giorni_stop_totali : 0;
    const recidive = p.recidive_muscolari !== undefined && p.recidive_muscolari !== null ? p.recidive_muscolari : 0;
    const cronistoria = p.cronistoria_infortuni || [];
    const medicalAdvice = p.consiglio_medico_ai || (p.is_injured ? `Attualmente indisponibile per ${p.infortunio_motivo || 'infortunio'}. Rientro stimato: ${p.infortunio_rientro || 'TBD'}.` : 'Calciatore con eccellente tenuta atletica e ridottissima incidenza di infortuni muscolari.');
    let tierColor = '#34d399';
    if (fragScore >= 80) { tierColor = '#f87171'; }
    else if (fragScore >= 60) { tierColor = '#fb923c'; }
    else if (fragScore >= 40) { tierColor = '#fbbf24'; }
    else if (fragScore >= 25) { tierColor = '#60a5fa'; }
    let dispColor = '#10b981';
    if (dispPct < 75) dispColor = '#ef4444';
    else if (dispPct < 85) dispColor = '#f59e0b';
    let seasonAccordionHtml = '';
    if (cronistoria && cronistoria.length > 0) {
        const seasonsMap = {};
        cronistoria.forEach(inj => {
            let s = (inj.stagione || 'Altro').trim();
            if (!seasonsMap[s]) {
                seasonsMap[s] = {
                    stagione: s,
                    infortuni: [],
                    tot_giorni: 0,
                    tot_partite_perse: 0,
                    has_in_corso: false
                };
            }
            seasonsMap[s].infortuni.push(inj);
            seasonsMap[s].tot_giorni += (parseInt(inj.giorni || inj.giorni_stop || 0, 10) || 0);
            seasonsMap[s].tot_partite_perse += (parseInt(inj.partite_perse || 0, 10) || 0);
            if (inj.in_corso) {
                seasonsMap[s].has_in_corso = true;
            }
        });
        const sortedSeasons = Object.values(seasonsMap).sort((a, b) => {
            const parseYear = (str) => {
                const m = str.match(/(\d+)/);
                return m ? parseInt(m[1], 10) : 0;
            };
            return parseYear(b.stagione) - parseYear(a.stagione);
        });
        seasonAccordionHtml = `
            <div class="injury-seasons-accordion">
                ${sortedSeasons.map((sGroup, idx) => {
                    const isDefaultExpanded = sGroup.has_in_corso || idx === 0;
                    const expandedClass = isDefaultExpanded ? 'expanded' : '';
                    const subRows = sGroup.infortuni.map(inj => {
                        const badgeClass = (inj.tipo || 'muscolare').toLowerCase();
                        const isCur = inj.in_corso;
                        return `
                            <tr>
                                <td style="font-weight:600;color:#fff;">
                                    ${inj.diagnosi || 'Infortunio'}
                                    ${isCur ? '<span class="season-active-chip" style="margin-left:6px;font-size:9.5px;padding:1px 5px;">🔴 In corso</span>' : ''}
                                </td>
                                <td><span class="injury-type-pill ${badgeClass}">${inj.tipo || 'generico'}</span></td>
                                <td style="color:#f87171;font-weight:700;">${inj.giorni || inj.giorni_stop || 0} gg</td>
                                <td style="color:#fbbf24;font-weight:800;text-align:center;">${inj.partite_perse || 0}</td>
                                <td style="color:var(--text-muted);font-size:11px;">${inj.data_inizio || '-'} → ${inj.data_fine || '-'}</td>
                            </tr>
                        `;
                    }).join('');
                    return `
                        <div class="injury-season-card ${expandedClass}">
                            <div class="injury-season-header" onclick="toggleSeasonInjuryDetail(this)">
                                <div class="season-header-left">
                                    <span class="season-pill">${sGroup.stagione}</span>
                                    ${sGroup.has_in_corso ? '<span class="season-active-chip">🔴 In corso</span>' : ''}
                                    <div class="season-stats-badges">
                                        <span class="season-stat-item">
                                            <b>${sGroup.infortuni.length}</b> ${sGroup.infortuni.length === 1 ? 'infortunio' : 'infortuni'}
                                        </span>
                                        <span class="season-stat-item stop">
                                            <b>${sGroup.tot_giorni} gg</b> stop
                                        </span>
                                        <span class="season-stat-item missed">
                                            <b>${sGroup.tot_partite_perse}</b> ${sGroup.tot_partite_perse === 1 ? 'gara persa' : 'gare perse'}
                                        </span>
                                    </div>
                                </div>
                                <div class="season-detail-btn">
                                    <span>Dettaglio</span>
                                    <span class="season-chevron">▼</span>
                                </div>
                            </div>
                            <div class="injury-season-detail">
                                <table class="injury-history-subtable">
                                    <thead>
                                        <tr>
                                            <th>Diagnosi Infortunio</th>
                                            <th>Tipo</th>
                                            <th>Stop</th>
                                            <th style="text-align:center;">Gare Perse</th>
                                            <th>Periodo</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${subRows}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    return `
        <div class="injury-history-container">
            <div class="injury-history-header">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <span style="font-size:18px;">🩺</span>
                    <h3 style="margin:0;font-size:13.5px;font-weight:800;color:#fff;letter-spacing:0.3px;">Storico Infortuni & Affidabilità Fisica (Multi-Stagione)</h3>
                    <span class="injury-tier-chip" style="background:rgba(255,255,255,0.06);border:1px solid ${tierColor};color:${tierColor};">
                        ${fragTier}
                    </span>
                </div>
                <div style="font-size:11.5px;color:var(--text-muted);">
                    Indice Fragilità AI: <b style="color:${tierColor};font-size:13px;">${fragScore}/100</b>
                </div>
            </div>
            <!-- Health KPI & Gauge Row -->
            <div class="injury-metrics-grid">
                <div class="injury-metric-card">
                    <span class="lbl">Disponibilità Storica</span>
                    <div style="display:flex;align-items:baseline;gap:6px;margin:4px 0;">
                        <b class="val" style="color:${dispColor};font-size:19px;">${dispPct}%</b>
                        <small style="color:var(--text-muted);font-size:10.5px;">su 3 stagioni</small>
                    </div>
                    <div class="injury-progress-bar-bg">
                        <div class="injury-progress-bar-fill" style="width:${dispPct}%;background:${dispColor};"></div>
                    </div>
                </div>
                <div class="injury-metric-card">
                    <span class="lbl">Partite Perse Totali</span>
                    <b class="val" style="color:#fbbf24;font-size:19px;margin-top:4px;">${partitePerse} <small style="font-size:11px;color:var(--text-muted);font-weight:normal;">gare</small></b>
                    <span style="font-size:10.5px;color:var(--text-secondary);">${giorniStop} giorni di stop</span>
                </div>
                <div class="injury-metric-card">
                    <span class="lbl">Recidive Muscolari</span>
                    <b class="val" style="color:${recidive > 1 ? '#ef4444' : (recidive === 1 ? '#f59e0b' : '#34d399')};font-size:19px;margin-top:4px;">
                        ${recidive} <small style="font-size:11px;color:var(--text-muted);font-weight:normal;">eventi</small>
                    </b>
                    <span style="font-size:10.5px;color:var(--text-secondary);">${recidive > 1 ? '⚠️ Rischio ricadute' : 'Tenuta muscolare solida'}</span>
                </div>
                <div class="injury-metric-card">
                    <span class="lbl">Stato Attuale</span>
                    <div style="margin-top:4px;">
                        ${p.is_injured 
                            ? `<span class="health-current-tag injured">🩹 ${p.infortunio_motivo || 'Indisponibile'} (${p.infortunio_rientro || 'TBD'})</span>`
                            : `<span class="health-current-tag healthy">🟢 Pienamente Disponibile</span>`
                        }
                    </div>
                    <span style="font-size:10.5px;color:var(--text-muted);">Serie A 2026/27</span>
                </div>
            </div>
            <!-- Medical AI Advice Box -->
            <div class="injury-advice-box">
                <div style="display:flex;align-items:flex-start;gap:8px;">
                    <span style="font-size:15px;line-height:1.2;">💡</span>
                    <div>
                        <b style="color:var(--accent-cyan);font-size:11px;text-transform:uppercase;letter-spacing:0.4px;">Analisi Medica & Consigli Asta AI:</b>
                        <p style="margin:2px 0 0 0;font-size:11.5px;color:var(--text-secondary);line-height:1.45;">${medicalAdvice}</p>
                    </div>
                </div>
            </div>
            <!-- Season Accordion List -->
            ${cronistoria.length > 0 ? seasonAccordionHtml : `
                <div class="injury-empty-banner">
                    <span style="font-size:16px;">🛡️</span>
                    <span><b>Integrità Fisica Impeccabile:</b> Nessun infortunio significativo registrato negli ultimi 3 anni. Calciatore integro ad alta affidabilità.</span>
                </div>
            `}
        </div>
    `;
}
window.toggleSeasonInjuryDetail = function(headerEl) {
    if (!headerEl) return;
    const card = headerEl.closest('.injury-season-card');
    if (!card) return;
    card.classList.toggle('expanded');
};
function generateAiStrengthsAndWeaknessesHtml(p) {
    const strengths = [];
    const weaknesses = [];
    if (p.is_rigorista_1 || p.rigorista_val === '1° Rigorista') {
        strengths.push('👑 <b>1° Rigorista Ufficiale</b>: Massima priorità dal dischetto nel club');
    } else if (p.is_rigorista_2 || p.rigorista_val === '2° Rigorista') {
        strengths.push('🎯 <b>2° Rigorista in Gerarchia</b>: Opportunità di bonus dagli undici metri');
    }
    if (p.is_punizioni || p.is_corner || (p.piazzati_val && p.piazzati_val !== '-')) {
        strengths.push('📐 <b>Specialista Piazzati</b>: Incaricato di corner e punizioni dirette/indirette');
    }
    if (p.role === 'P') {
        const cs = p.clean_sheets_2627 !== undefined ? p.clean_sheets_2627 : (p.clean_sheets_2526 || 0);
        if (cs >= 2 || (p.clean_sheets_2526 || 0) >= 8) {
            strengths.push(`🧤 <b>Solidità Porta & Clean Sheet</b>: Già ${cs} gare a rete inviolata registrate`);
        }
        const savePct = p.save_pct_2627 || p.save_pct_2526 || 72;
        if (savePct >= 74) {
            strengths.push(`🧱 <b>Reattività tra i Pali</b>: Percentuale parate elevata (${savePct}%)`);
        }
        if ((p.goals_prevented_2627 || p.goals_prevented_2526 || 0) > 0.4) {
            strengths.push(`⚡ <b>Gol Evitati (Post-Shot xG)</b>: Salva regolarmente il risultato oltre la media`);
        }
        if (p.rigori_parati_totali > 0 || (p.rp && p.rp > 0)) {
            strengths.push(`🎯 <b>Specialista Para-Rigori</b>: Ottimo intuito sui penalty avversari`);
        }
        const mv = p.mv_2627 || p.mv || 6.0;
        if (mv >= 6.3) {
            strengths.push(`📈 <b>Media Voto Eccellente</b>: MV ${mv.toFixed(2)} tra le più alte del campionato`);
        }
        const pres = p.presenze_2627 || p.presenze || 1;
        const gs = p.gol_subiti_2627 !== undefined ? p.gol_subiti_2627 : (p.gs || 0);
        const gsPerGame = gs / pres;
        if (gsPerGame >= 1.4) {
            weaknesses.push(`⚠️ <b>Media Gol Subiti Elevata</b>: Concede circa ${gsPerGame.toFixed(1)} reti a partita`);
        }
        if (p.titolarita >= 82) {
            strengths.push(`👑 <b>Numero 1 Indiscusso</b>: Titolare inamovibile della porta (${p.titolarita}% titolarità, nessuna staffetta)`);
        } else if (p.titolarita >= 68) {
            strengths.push(`🧤 <b>Titolare Designato</b>: Prima scelta tra i pali (${p.titolarita}% presenze stimate)`);
        } else if (p.titolarita <= 35) {
            weaknesses.push(`⬇️ <b>Secondo Portiere / Riserva</b>: Impiego occasionale, scende in campo solo in assenza del titolare (${p.coppia_nome || '1° portiere'})`);
        } else {
            weaknesses.push(`⚖️ <b>Vero Ballottaggio Aperto</b>: Staffetta serrata per la porta con ${p.coppia_nome || 'secondo portiere'} (${p.titolarita}% titolarità)`);
        }
    } else if (p.role === 'D') {
        const xg = p.xg_2627 || (p.xg90_2627 ? p.xg90_2627 * (p.minuti_2627 || 90) / 90 : 0);
        if (xg >= 0.35 || (p.gol_2627 || 0) >= 1 || (p.gf || 0) >= 2) {
            strengths.push('⚽ <b>Pericolosità da Bonus</b>: Inserimenti puntuali e stacco aereo da palla inattiva');
        }
        const xa = p.xa_2627 || (p.xa90_2627 ? p.xa90_2627 * (p.minuti_2627 || 90) / 90 : 0);
        if (xa >= 0.25 || (p.assist_2627 || 0) >= 1 || (p.chances_created_2627 || 0) >= 4) {
            strengths.push('🪄 <b>Corsia di Spinta & Assist</b>: Attivo nella rifinitura e cross dal fondo');
        }
        if ((p.recuperi_2627 || 0) >= 18) {
            strengths.push(`🛡️ <b>Dominanza nei Duelli</b>: Già ${p.recuperi_2627} palloni recuperati con tackle puliti`);
        }
        const mv = p.mv_2627 || p.mv || 6.0;
        if (mv >= 6.2) {
            strengths.push(`💎 <b>Pilastro da Modificatore</b>: Media voto affidabile (${mv.toFixed(2)}) e sufficienze garantite`);
        }
        const amm = p.amm_2627 || 0;
        if (amm >= 2 || (p.amm || 0) >= 7 || (p.esp_2627 || 0) > 0) {
            weaknesses.push(`🟨 <b>Frequenza di Malus Cartellini</b>: Giocatore incline all'intervento falloso (${amm} ammonizioni)`);
        }
        if ((p.xg_2627 || 0) === 0 && (p.gol_2627 || 0) === 0 && (p.gf || 0) === 0 && (p.chances_created_2627 || 0) <= 1) {
            weaknesses.push('🛡️ <b>Bassa Propensione Offensiva</b>: Difensore di contenimento, bonus pesanti rari');
        }
        if (p.titolarita < 70) {
            weaknesses.push(`🔄 <b>Rotazioni nel Reparto</b>: Titolarità al ${p.titolarita}% con frequenti turnover`);
        }
    } else if (p.role === 'C') {
        const xg = p.xg_2627 || (p.xg90_2627 ? p.xg90_2627 * (p.minuti_2627 || 90) / 90 : 0);
        if (xg >= 0.7 || (p.gol_2627 || 0) >= 1 || (p.gf || 0) >= 4) {
            strengths.push('⚡ <b>Incursore d\'Area di Rigore</b>: Tiro da fuori e inserimenti costanti a ridosso delle punte');
        }
        const chances = p.chances_created_2627 || p.key_passes_2627 || 0;
        if (chances >= 6 || (p.assist_2627 || 0) >= 1 || (p.ass || 0) >= 4) {
            strengths.push(`🪄 <b>Regia & Visione di Gioco</b>: Generatore di occasioni da rete (${chances} passaggi chiave)`);
        }
        if (p.oop_val && p.oop_val !== '-') {
            strengths.push(`💎 <b>Giocatore Fuori Ruolo (OOP)</b>: Schierato avanzato rispetto alla posizione del listone`);
        }
        if (p.xfm && p.xfm >= 6.8) {
            strengths.push(`🚀 <b>Expected FantaMedia d\'Élite</b>: xFM attesa pari a ${p.xfm} su base dati avanzati`);
        }
        if ((p.amm_2627 || 0) >= 2 || (p.amm || 0) >= 8) {
            weaknesses.push(`🟨 <b>Pressione & Ammonizioni</b>: Gioco ruvido in mediana con costante rischio cartellino`);
        }
        if ((p.xfm || 0) < 6.2 && (p.gol_2627 || 0) === 0 && (p.gf || 0) <= 1) {
            weaknesses.push('⏳ <b>Basso Volume di Bonus</b>: Mediano puro votato all\'equilibrio, fantamedia legata al solo voto base');
        }
        if (p.titolarita < 68) {
            weaknesses.push(`🔄 <b>Concorrenza Serrata a Centrocampo</b>: Minutaggio soggetto a ballottaggi continui`);
        }
    } else if (p.role === 'A') {
        const xg = p.xg_2627 || (p.xg90_2627 ? p.xg90_2627 * (p.minuti_2627 || 90) / 90 : 0);
        if (xg >= 1.2 || (p.gol_2627 || 0) >= 2 || (p.gf || 0) >= 10) {
            strengths.push('🎯 <b>Volume Tiri & xG da Bomber</b>: Terminale offensivo con alta frequenza di finalizzazione');
        }
        if ((p.tiri_porta_2627 || 0) >= 5 || (p.tiri_2627 || 0) >= 12) {
            strengths.push('💥 <b>Costante Tiro verso lo Specchio</b>: Cerca con insistenza la porta avversaria');
        }
        if (p.ovr >= 86) {
            strengths.push(`👑 <b>Top Player di Reparto</b>: OVR ${p.ovr}, trascinatore offensivo assoluto`);
        }
        if ((p.big_chances_created_2627 || 0) >= 2 || (p.assist_2627 || 0) >= 2) {
            strengths.push('🤝 <b>Assistman & Raccordo</b>: Sa liberare i compagni davanti alla porta');
        }
        if ((p.big_chance_missed_2627 || 0) >= 2) {
            weaknesses.push(`❌ <b>Cinismo da Perfezionare</b>: ${p.big_chance_missed_2627} grandi occasioni fallite sotto porta`);
        }
        if (p.titolarita < 70) {
            weaknesses.push(`🔄 <b>Alternanza in Attacco</b>: Subentro frequente a gara in corso o staffetta di reparto`);
        }
        if (p.diff_q !== undefined && p.diff_q < 0) {
            weaknesses.push('📉 <b>Flessione di Quotazione</b>: Rendimento recente al di sotto delle aspettative');
        }
    }
    if (p.titolarita >= 90) {
        strengths.push(`🔒 <b>Inamovibile</b>: Garanzia di voto e presenza costante nello scacchiere titolare (${p.titolarita}%)`);
    }
    const disp = p.disponibilita_pct !== undefined ? p.disponibilita_pct : (100 - (p.fragility_score || 20));
    if (disp >= 95) {
        strengths.push('🟢 <b>Tenuta Atletica Impeccabile</b>: Nessuno stop muscolare significativo registrato');
    } else if (p.fragility_score >= 55 || (p.partite_saltate_totali || 0) >= 5) {
        weaknesses.push(`🩹 <b>Rischio Fragilità Fisica</b>: Storico di infortuni che ne condiziona la continuità (${p.fragility_tier || 'Attenzione'})`);
    }
    if (p.is_injured) {
        weaknesses.push(`🔴 <b>Attualmente Indisponibile</b>: ${p.infortunio_motivo || 'Infortunio in corso'} (Rientro: ${p.infortunio_rientro || 'TBD'})`);
    }
    if (p.delta_xfm !== undefined && p.delta_xfm >= 0.65) {
        weaknesses.push(`📈 <b>Possibile Regressione Statistica</b>: Ha raccolto più bonus rispetto al volume di gioco (delta +${p.delta_xfm.toFixed(2)})`);
    } else if (p.delta_xfm !== undefined && p.delta_xfm <= -0.45) {
        strengths.push(`💎 <b>Occasione Sottovalutata</b>: Volume di gioco superiore ai bonus raccolti (delta ${p.delta_xfm.toFixed(2)}), bonus imminenti`);
    }
    if (strengths.length === 0) {
        strengths.push('⭐ Calciatore con rendimento regolare e buona collocazione nello scacchiere della squadra');
    }
    if (weaknesses.length === 0) {
        weaknesses.push('⚖️ Profilo equilibrato: nessun punto debole strutturale evidente nei dati storici');
    }
    return `
        <div class="ai-strengths-weaknesses-container">
            <div class="ai-sw-card strengths">
                <div class="ai-sw-header">
                    <span class="sw-badge-icon">🟢</span>
                    <div class="sw-header-title">
                        <b>Punti di Forza Algoritmici (AI)</b>
                        <small>Analisi predittiva su metriche reali</small>
                    </div>
                </div>
                <ul class="ai-sw-list">
                    ${strengths.slice(0, 4).map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            <div class="ai-sw-card weaknesses">
                <div class="ai-sw-header">
                    <span class="sw-badge-icon">🔴</span>
                    <div class="sw-header-title">
                        <b>Punti Deboli & Rischi Asta (AI)</b>
                        <small>Fattori di rischio e criticità</small>
                    </div>
                </div>
                <ul class="ai-sw-list">
                    ${weaknesses.slice(0, 4).map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}
function openPlayerProfileModal(playerId) {
    window._currentOpenPlayerId = playerId;
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;
    const modal = document.getElementById('playerDetailModal');
    const modalBody = document.getElementById('playerDetailModalBody');
    if (!modal || !modalBody) return;
    const teamTac = (typeof TACTICAL_DB !== 'undefined' && TACTICAL_DB[p.team]) ? TACTICAL_DB[p.team] : null;
    const isBought = typeof isPlayerBought === 'function' ? isPlayerBought(p.id) : false;
    const isTaken = typeof isPlayerTakenByOther === 'function' ? isPlayerTakenByOther(p.id) : false;
    const isFav = typeof isFavorite === 'function' ? isFavorite(p.id) : false;
    let titColor = '#4ade80';
    if (p.titolarita < 68) titColor = '#f59e0b';
    else if (p.titolarita < 50) titColor = '#ef4444';
    const injBadge = p.is_injured 
        ? `<span class="badge-tag red" title="${p.infortunio_motivo || ''}">🩹 Rientro: ${p.infortunio_rientro || 'TBD'}</span>`
        : `<span class="badge-tag green">🟢 Integro</span>`;
    let rigoristaBadge = '';
    if (p.is_rigorista_1) rigoristaBadge = `<span class="badge-tag gold">👑 1° Rigorista</span>`;
    else if (p.is_rigorista_2) rigoristaBadge = `<span class="badge-tag gold">🎯 2° Rigorista</span>`;
    else if (p.is_rigorista_3) rigoristaBadge = `<span class="badge-tag blue">🎯 3° Rigorista</span>`;
    else if (p.is_punizioni || p.is_corner) rigoristaBadge = `<span class="badge-tag cyan">📐 Piazzati</span>`;
    let coppiaBadge = '';
    if (p.coppia_nome && p.coppia_nome !== '-') {
        const clickAttr = p.coppia_id ? `onclick="openPlayerProfileModal(${p.coppia_id})" style="cursor:pointer;"` : '';
        let icon = '🔄 Staffetta';
        if (p.role === 'P') {
            if (p.titolarita >= 82) {
                icon = '🛡️ Vice';
            } else if (p.titolarita >= 68) {
                icon = '🧤 Riserva';
            } else if (p.titolarita <= 38) {
                icon = '⬆️ 1° Portiere';
            } else {
                icon = '⚖️ Staffetta';
            }
        } else {
            if (p.titolarita >= 75) {
                icon = '⬇️ Riserva';
            } else if (p.titolarita <= 35) {
                icon = '⬆️ Titolare';
            } else {
                icon = '🔄 Staffetta';
            }
        }
        coppiaBadge = `<span class="badge-tag blue" ${clickAttr} title="${p.coppia_dettaglio || ''}">${icon}: <b>${p.coppia_nome}</b></span>`;
    }
    let oopBadge = '';
    if (p.oop_val && p.oop_val !== '-') {
        const oopColor = p.oop_tier === 'ORO' ? '#f59e0b' : (p.oop_tier === 'ARGENTO' ? '#cbd5e1' : '#d97706');
        oopBadge = `<span class="badge-tag oop" style="border-color:${oopColor};color:${oopColor};" title="${p.oop_desc || ''}">💎 ${p.oop_val}</span>`;
    }
    let actionButtonsHtml = '';
    if (isBought) {
        actionButtonsHtml = `
            <div class="profile-action-status-row bought">
                <span class="action-status-badge bought">✓ NELLA TUA ROSA</span>
                <button class="btn-action btn-danger-soft" onclick="unmarkPlayerTaken(${p.id}); closePlayerProfileModal(); updateAllViews();">Rimuovi ✕</button>
            </div>
        `;
    } else if (isTaken) {
        actionButtonsHtml = `
            <div class="profile-action-status-row taken">
                <span class="action-status-badge taken">⛔ ASSEGNATO AD UN RIVALE</span>
                <button class="btn-action btn-restore" onclick="unmarkPlayerTaken(${p.id}); closePlayerProfileModal(); updateAllViews();">Rendi Disponibile ↩️</button>
            </div>
        `;
    } else {
        actionButtonsHtml = `
            <div class="profile-action-grid">
                <button class="btn-action btn-action-squad" onclick="showComingSoonModal('Creazione Squadra & Asta Live')" title="Aste estive concluse. La creazione della rosa riaprirà per l'asta di riparazione!">
                    🔒 Crea Squadra
                </button>
                <button class="btn-action btn-action-rival" onclick="showComingSoonModal('Assegnazione Squadre & Asta Live')">
                    🔒 Assegna Rivale
                </button>
                <button class="btn-action btn-action-compare" onclick="setMatchupFromCard(${p.id}); switchTab('matchup'); closePlayerProfileModal();">
                    ⚔️ Confronta 1vs1
                </button>
            </div>
        `;
    }
    const xfmData = computeExpectedFantaMedia(p);
    let xfmAlertHtml = '';
    const isElitePerformer = (xfmData.xfm >= 7.8 || (p.ovr >= 86 && xfmData.xfm >= 7.2)) && xfmData.realFm >= 7.8;
    if (isElitePerformer && xfmData.delta >= 0.20) {
        xfmAlertHtml = `
            <div class="xfm-alert-box under" style="background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.35);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:18px;">🔥</span>
                    <div>
                        <div style="font-weight:800;color:var(--accent-cyan);font-size:12px;">STATO DI GRAZIA / TOP ASSOLUTO (Efficacia Straordinaria)</div>
                        <div style="font-size:11px;color:var(--text-secondary);">FM Reale: <b>${xfmData.realFm}</b> • xFM Attesa: <b>${xfmData.xfm}</b> (Delta: <b style="color:var(--accent-cyan);">+${xfmData.delta}</b>). Straordinaria efficacia realizzativa su una mole di occasioni creata d'élite. Titolare inamovibile da schierare sempre!</div>
                    </div>
                </div>
            </div>
        `;
    } else if (xfmData.delta <= -0.40) {
        xfmAlertHtml = `
            <div class="xfm-alert-box under">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:18px;">💎</span>
                    <div>
                        <div style="font-weight:800;color:#34d399;font-size:12px;">SOTTO-RENDIMENTO STATISTICO (Occasione di Mercato / Bonus Imminenti)</div>
                        <div style="font-size:11px;color:var(--text-secondary);">FM Reale: <b>${xfmData.realFm}</b> vs xFM Attesa: <b>${xfmData.xfm}</b> (Delta: <b style="color:#34d399;">${xfmData.delta}</b>). Produce un volume elevato di occasioni (xG/xA) ma ha raccolto meno del dovuto per sfortuna temporanea. COMPRA ALL'ASTA O SCAMBIA!</div>
                    </div>
                </div>
            </div>
        `;
    } else if (xfmData.delta >= 0.60) {
        xfmAlertHtml = `
            <div class="xfm-alert-box over">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:18px;">📈</span>
                    <div>
                        <div style="font-weight:800;color:#fbbf24;font-size:12px;">SOVRA-RENDIMENTO DA EPISODI (Possibile Regressione Fisiologica)</div>
                        <div style="font-size:11px;color:var(--text-secondary);">FM Reale: <b>${xfmData.realFm}</b> vs xFM Attesa: <b>${xfmData.xfm}</b> (Delta: <b style="color:#f87171;">+${xfmData.delta}</b>). Ha raccolto più bonus rispetto al volume effettivo di occasioni create: possibile flessione. Ottimo per scambi al massimo valore.</div>
                    </div>
                </div>
            </div>
        `;
    } else {
        xfmAlertHtml = `
            <div class="xfm-alert-box balanced">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:16px;">⚖️</span>
                    <div style="font-size:11.5px;color:var(--text-secondary);">
                        FM Reale (<b>${xfmData.realFm}</b>) in perfetto equilibrio con la FantaMedia Attesa xFM (<b>${xfmData.xfm}</b>). Rendimento costante e sostenibile.
                    </div>
                </div>
            </div>
        `;
    }
    const votiList = (p.voti_dettaglio_2627 && p.voti_dettaglio_2627.length > 0) ? p.voti_dettaglio_2627 : [];
    const validVoti = votiList.filter(v => v.voto !== null && v.voto !== undefined);
    const validFv = votiList.filter(v => v.fantavoto !== null && v.fantavoto !== undefined);
    let smartTrend = { label: '⚖️ Costante', color: '#38bdf8', bg: 'transparent', desc: 'Rendimento regolare e affidabile' };
    if (validFv.length > 0) {
        const last3Fv = validFv.slice(-3).map(v => v.fantavoto);
        const mean3Fv = last3Fv.reduce((a, b) => a + b, 0) / last3Fv.length;
        const lastGoals = votiList.slice(-3).reduce((sum, v) => sum + (v.gf || 0), 0);
        const lastAssists = votiList.slice(-3).reduce((sum, v) => sum + (v.ass || 0), 0);
        const currFm = p.fm_2627 || (validFv.reduce((a, b) => a + b.fantavoto, 0) / validFv.length);
        if (mean3Fv >= 8.0 || lastGoals >= 2 || (currFm >= 7.5 && last3Fv[last3Fv.length - 1] >= 7.0)) {
            smartTrend = { label: '🔥 On Fire', color: '#f59e0b', bg: 'transparent', desc: 'Rendimento devastante con bonus a raffica' };
        } else if ((mean3Fv - currFm >= 0.4) || (validFv.length >= 2 && last3Fv[last3Fv.length - 1] > last3Fv[last3Fv.length - 2] + 1.0)) {
            smartTrend = { label: '📈 In Crescita', color: '#10b981', bg: 'transparent', desc: 'Forma e fantavoti in netta ascesa' };
        } else if (currFm - mean3Fv >= 0.75 && lastGoals === 0 && lastAssists === 0 && mean3Fv < 6.0) {
            smartTrend = { label: '❄️ In Flessione', color: '#f87171', bg: 'transparent', desc: 'Flessione recente di rendimento e voti' };
        } else if (['A', 'C'].includes(p.role) && lastGoals === 0 && lastAssists === 0 && validVoti.length >= 3 && mean3Fv <= 6.2) {
            smartTrend = { label: '⏳ A Secco', color: '#fbbf24', bg: 'transparent', desc: 'Voti regolari ma a secco di bonus recenti' };
        }
    }
    const totalRounds = 38;
    const maxPlayedRound = votiList.length > 0 ? Math.max(...votiList.map(v => v.giornata)) : 0;
    const sufficiencyCount = validVoti.filter(v => v.voto >= 6.0).length;
    const sufficiencyPct = validVoti.length > 0 ? Math.round((sufficiencyCount / validVoti.length) * 100) : 0;
    const curBudgetTotal = (typeof State !== 'undefined' && State.budgetTotal) ? State.budgetTotal : 1000;
    const curRatio = (typeof getGlobalBudgetRatio === 'function') ? getGlobalBudgetRatio() : (curBudgetTotal / 1000);
    const scaledPrice = Math.max(1, Math.round((p.prezzo_cons || 1) * curRatio));
    const scaledMaxBid = Math.max(1, Math.round((p.max_bid || p.prezzo_cons || 1) * curRatio));
    const scaledFvm = (p.fvm !== undefined && p.fvm !== null) ? Math.max(1, Math.round(p.fvm * curRatio)) : '-';
    const budgetPct = (((p.prezzo_cons || 1) / 1000) * 100).toFixed(1);
    const stealLimit = Math.max(1, Math.round(scaledPrice * 0.75));
    const fairPriceMin = Math.max(1, Math.round(scaledPrice * 0.85));
    const titVal = Math.min(100, Math.max(0, p.titolarita !== undefined ? p.titolarita : 50));
    const suffPct = validVoti.length > 0 ? sufficiencyPct : (p.rating_2526 ? Math.min(95, Math.round(p.rating_2526 * 12)) : 75);
    const integritaVal = Math.min(100, Math.max(0, p.disponibilita_pct !== undefined && p.disponibilita_pct !== null ? Math.round(p.disponibilita_pct) : Math.round(100 - (p.fragility_score || 20))));
    let dispColor = '#10b981';
    if (integritaVal < 75) dispColor = '#ef4444';
    else if (integritaVal < 88) dispColor = '#f59e0b';
    let affColor = '#38bdf8';
    if (suffPct >= 75) affColor = '#34d399';
    else if (suffPct < 55) affColor = '#f59e0b';
    const quickGaugesHtml = `
        <div class="profile-quick-gauges-bar">
            <div class="quick-gauge-item">
                <div class="gauge-header">
                    <span class="gauge-lbl">Titolarità</span>
                    <b class="gauge-val" style="color:${titColor};">${titVal}%</b>
                </div>
                <div class="gauge-track"><div class="gauge-fill" style="width:${titVal}%;background:${titColor};"></div></div>
                <span class="gauge-sub">${p.titolarita_desc_2627 || (p.is_in_11 ? '11 Titolare' : (titVal >= 70 ? 'Titolare' : 'Rotazione'))}</span>
            </div>
            <div class="quick-gauge-item">
                <div class="gauge-header">
                    <span class="gauge-lbl">Affidabilità Voto</span>
                    <b class="gauge-val" style="color:${affColor};">${suffPct}%</b>
                </div>
                <div class="gauge-track"><div class="gauge-fill" style="width:${suffPct}%;background:${affColor};"></div></div>
                <span class="gauge-sub">${validVoti.length > 0 ? `${sufficiencyCount}/${validVoti.length} gare sufficienza` : 'Stabilità media voto'}</span>
            </div>
            <div class="quick-gauge-item">
                <div class="gauge-header">
                    <span class="gauge-lbl">Integrità Fisica</span>
                    <b class="gauge-val" style="color:${dispColor};">${integritaVal}%</b>
                </div>
                <div class="gauge-track"><div class="gauge-fill" style="width:${integritaVal}%;background:${dispColor};"></div></div>
                <span class="gauge-sub">${p.partite_saltate_totali !== undefined ? `${p.partite_saltate_totali} gare perse storiche` : (p.is_injured ? 'Infortunato' : 'Tenuta solida')}</span>
            </div>
        </div>
    `;
    const aiStrengthsWeaknessesHtml = generateAiStrengthsAndWeaknessesHtml(p);
    const auctionRoadmapHtml = `
        <div class="profile-auction-roadmap">
            <div class="roadmap-header">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:15px;">🏷️</span>
                    <b style="color:#fff;font-size:12px;">Strategia & Fasce d'Asta AI (su ${curBudgetTotal} CR)</b>
                </div>
                <span class="roadmap-meta-budget">Prezzo Equo: <b style="color:#fbbf24;">${scaledPrice} CR</b> (<b>${budgetPct}%</b> budget)</span>
            </div>
            <div class="roadmap-grid">
                <div class="roadmap-box steal">
                    <div class="r-badge">🟢 AFFARE (STEAL)</div>
                    <b class="r-range">&lt; ${stealLimit} CR</b>
                    <span class="r-desc">Acquisto super conveniente: rendimento sul capitale garantito</span>
                </div>
                <div class="roadmap-box fair">
                    <div class="r-badge">🟡 PREZZO EQUO</div>
                    <b class="r-range">${fairPriceMin} - ${scaledPrice} CR</b>
                    <span class="r-desc">Puntata sostenibile: riflette il valore reale atteso sul campo</span>
                </div>
                <div class="roadmap-box overpay">
                    <div class="r-badge">🔴 ALLARME OVERPAY</div>
                    <b class="r-range">&gt; ${scaledMaxBid} CR</b>
                    <span class="r-desc">Oltre questa soglia il rischio di pagare in eccesso è troppo alto</span>
                </div>
            </div>
        </div>
    `;
    let tandemCardHtml = '';
    if (p.coppia_nome && p.coppia_nome !== '-') {
        const partner = PLAYERS.find(pl => (pl.name && pl.name.toLowerCase() === p.coppia_nome.toLowerCase()) || (p.coppia_id && pl.id === p.coppia_id));
        const partnerScaled = partner ? Math.max(1, Math.round((partner.prezzo_cons || 1) * curRatio)) : Math.max(1, Math.round(10 * curRatio));
        const combined = scaledPrice + partnerScaled;
        const combinedPct = ((((p.prezzo_cons || 1) + (partner ? (partner.prezzo_cons || 1) : 10)) / 1000) * 100).toFixed(1);
        let adviceText = '';
        let tandemTitle = '';
        if (p.role === 'P') {
            if (p.titolarita >= 82) {
                tandemTitle = `Gerarchia Porta ${p.team} (Titolare Blindato)`;
                adviceText = `Gerarchia definita: <b>${p.name}</b> è il Numero 1 indiscusso (${p.titolarita}% presenze stimate, nessuna staffetta). Acquistare <b>${p.coppia_nome}</b> a 1 credito serve unicamente come copertura anti-infortunio / squalifica.`;
            } else if (p.titolarita <= 38) {
                tandemTitle = `Gerarchia Porta ${p.team} (Secondo Portiere)`;
                adviceText = `Ruolo di riserva: <b>${p.name}</b> è il secondo portiere (${p.titolarita}% presenze). Va acquistato a 1 credito solo per completare il blocco porta insieme al titolare <b>${p.coppia_nome}</b>.`;
            } else {
                tandemTitle = `Staffetta Aperta Porta ${p.team}`;
                adviceText = `Staffetta reale: la porta di <b>${p.team}</b> è in ballottaggio alternato (${p.name} al ${p.titolarita}%). Acquisto obbligato di entrambi i portieri per non rischiare di giocare in inferiorità numerica.`;
            }
        } else {
            if (p.titolarita >= 75) {
                tandemTitle = `Gerarchia di Reparto ${p.team}`;
                adviceText = `Titolare affidabile (${p.titolarita}%): ${p.coppia_nome} è l'alternativa naturale in panchina per le rotazioni a gara in corso.`;
            } else if (p.titolarita <= 35) {
                tandemTitle = `Gerarchia di Reparto ${p.team}`;
                adviceText = `Riserva tattica: subentra tipicamente a gara in corso al posto del titolare ${p.coppia_nome}.`;
            } else {
                tandemTitle = `Ballottaggio di Reparto ${p.team}`;
                adviceText = `Ballottaggio aperto (${p.titolarita}% vs rotazioni): acquisto in coppia raccomandato se cerchi la certezza del voto nel reparto.`;
            }
        }
        tandemCardHtml = `
            <div class="profile-tandem-card">
                <div class="tandem-card-header">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:16px;">${p.role === 'P' ? '🧤' : '🔄'}</span>
                        <b style="color:#fff;font-size:12.5px;">${tandemTitle}</b>
                    </div>
                    <span class="tandem-budget-chip">Spesa Coppia: <b>${combined} CR</b> (${combinedPct}% budget)</span>
                </div>
                <div class="tandem-players-row">
                    <div class="tandem-player-chip active">
                        <span class="t-role">${p.role}</span>
                        <span class="t-name"><b>${p.name}</b> (${p.titolarita}% tit)</span>
                        <span class="t-price">${scaledPrice} CR</span>
                    </div>
                    <span class="tandem-plus">+</span>
                    <div class="tandem-player-chip partner" ${pClick} title="Apri scheda di ${p.coppia_nome}">
                        <span class="t-role">${partner ? partner.role : p.role}</span>
                        <span class="t-name"><b>${p.coppia_nome}</b> ${partner ? `(${partner.titolarita}% tit)` : ''} ↗</span>
                        <span class="t-price">${partnerScaled} CR</span>
                    </div>
                </div>
                <div class="tandem-advice-sub">${adviceText}</div>
            </div>
        `;
    }
    const svgW = 760;
    const svgH = 165;
    const padL = 38;
    const padR = 20;
    const padT = 24;
    const padB = 30;
    const drawW = svgW - padL - padR;
    const drawH = svgH - padT - padB;
    const colStep = drawW / totalRounds;
    const maxVal = 18.0; // Max Fantavoto scale ceiling
    const getY = (val) => padT + (1 - Math.min(maxVal, Math.max(0, val)) / maxVal) * drawH;
    const y6 = getY(6.0);
    const y10 = getY(10.0);
    const yPlayerFm = (p.fm_2627 && p.fm_2627 > 0) ? getY(p.fm_2627) : null;
    let gridLinesSvg = `
        <!-- Reference Grid -->
        <line x1="${padL}" y1="${getY(0)}" x2="${padL + drawW}" y2="${getY(0)}" stroke="rgba(255,255,255,0.15)" stroke-width="1" />
        <line x1="${padL}" y1="${y6}" x2="${padL + drawW}" y2="${y6}" stroke="rgba(56,189,248,0.3)" stroke-width="1" stroke-dasharray="3,3" />
        <text x="${padL - 6}" y="${y6 + 3}" text-anchor="end" fill="#38bdf8" font-size="8.5" font-weight="700">6.0</text>
        <line x1="${padL}" y1="${y10}" x2="${padL + drawW}" y2="${y10}" stroke="rgba(251,191,36,0.25)" stroke-width="1" stroke-dasharray="3,3" />
        <text x="${padL - 6}" y="${y10 + 3}" text-anchor="end" fill="#fbbf24" font-size="8.5" font-weight="700">10.0</text>
    `;
    if (yPlayerFm) {
        gridLinesSvg += `
            <line x1="${padL}" y1="${yPlayerFm}" x2="${padL + drawW}" y2="${yPlayerFm}" stroke="rgba(234,179,8,0.55)" stroke-width="1.2" stroke-dasharray="4,2" />
            <text x="${padL + drawW + 4}" y="${yPlayerFm + 3}" fill="#fbbf24" font-size="8" font-weight="800">FM ${(p.fm_2627).toFixed(1)}</text>
        `;
    }
    let barsSvg = '';
    let xLabelsSvg = '';
    let polyPoints = [];
    let nodesSvg = '';
    for (let g = 1; g <= totalRounds; g++) {
        const cx = padL + (g - 1) * colStep + colStep / 2;
        const barW = Math.max(9, colStep * 0.72);
        const barX = cx - barW / 2;
        if (g === 1 || g === 5 || g === 10 || g === 15 || g === 20 || g === 25 || g === 30 || g === 35 || g === 38 || g === maxPlayedRound) {
            const isPlayed = g <= maxPlayedRound;
            xLabelsSvg += `<text x="${cx}" y="${svgH - 10}" text-anchor="middle" fill="${isPlayed ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.3)'}" font-size="8.5" font-weight="${isPlayed ? '800' : '500'}">G${g}</text>`;
        }
        const match = votiList.find(v => v.giornata === g);
        if (match && match.voto !== null && match.voto !== undefined) {
            const vVal = match.voto;
            const fvVal = match.fantavoto !== null && match.fantavoto !== undefined ? match.fantavoto : vVal;
            const baseY = getY(vVal);
            const baseH = getY(0) - baseY;
            let baseFill = '#38bdf8';
            if (vVal >= 7.0) baseFill = '#10b981';
            else if (vVal >= 6.0) baseFill = '#0284c7';
            else if (vVal >= 5.5) baseFill = '#f59e0b';
            else baseFill = '#ef4444';
            barsSvg += `
                <g class="season-match-bar-group" onclick="selectSeasonRound(${p.id}, ${g})" onmouseenter="previewSeasonRound(${p.id}, ${g})" style="cursor:pointer;">
                    <rect x="${barX}" y="${baseY}" width="${barW}" height="${Math.max(2, baseH)}" rx="2" fill="${baseFill}" opacity="0.85">
                        <title>G${g}: Voto ${vVal} | FV ${fvVal}</title>
                    </rect>
            `;
            if (fvVal > vVal) {
                const bonusY = getY(fvVal);
                const bonusH = baseY - bonusY;
                barsSvg += `
                    <rect x="${barX}" y="${bonusY}" width="${barW}" height="${Math.max(2, bonusH)}" rx="2" fill="url(#bonusGradient)" stroke="#fde047" stroke-width="0.8" opacity="0.95" />
                `;
            } else if (fvVal < vVal) {
                barsSvg += `
                    <rect x="${barX}" y="${baseY}" width="${barW}" height="3" rx="1" fill="#f43f5e" />
                `;
            }
            barsSvg += `</g>`;
            const ptY = getY(fvVal);
            polyPoints.push(`${cx},${ptY}`);
            nodesSvg += `
                <circle cx="${cx}" cy="${ptY}" r="3.5" fill="#fde047" stroke="#0f172a" stroke-width="1.5" class="match-node-dot" onclick="selectSeasonRound(${p.id}, ${g})" onmouseenter="previewSeasonRound(${p.id}, ${g})" style="cursor:pointer;">
                    <title>G${g}: FantaVoto ${fvVal}</title>
                </circle>
            `;
        } else if (g <= maxPlayedRound) {
            barsSvg += `
                <g class="season-match-bar-group" onclick="selectSeasonRound(${p.id}, ${g})" onmouseenter="previewSeasonRound(${p.id}, ${g})" style="cursor:pointer;">
                    <rect x="${barX}" y="${getY(4.0)}" width="${barW}" height="${getY(0) - getY(4.0)}" rx="2" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.15)" stroke-dasharray="2,2" />
                    <text x="${cx}" y="${getY(2.0)}" text-anchor="middle" fill="var(--text-muted)" font-size="7.5" font-weight="700">s.v.</text>
                </g>
            `;
        } else {
            barsSvg += `
                <rect x="${barX}" y="${padT}" width="${barW}" height="${drawH}" rx="2" fill="none" stroke="rgba(255,255,255,0.04)" stroke-dasharray="2,3" />
            `;
        }
    }
    let trendLineSvg = '';
    if (polyPoints.length > 1) {
        trendLineSvg = `
            <polyline points="${polyPoints.join(' ')}" fill="none" stroke="rgba(251,191,36,0.85)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        `;
    }
    const seasonChartSvg = `
        <svg viewBox="0 0 ${svgW} ${svgH}" class="season-trend-svg-canvas">
            <defs>
                <linearGradient id="bonusGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#34d399" />
                    <stop offset="100%" stop-color="#fbbf24" />
                </linearGradient>
            </defs>
            ${gridLinesSvg}
            ${barsSvg}
            ${trendLineSvg}
            ${nodesSvg}
            ${xLabelsSvg}
        </svg>
    `;
    const latestMatch = votiList.length > 0 ? votiList[votiList.length - 1] : null;
    let initialInspectorHtml = '';
    if (latestMatch) {
        const calInfo = getMatchInfoForTeamAndRound(p.team, latestMatch.giornata);
        const isHome = latestMatch.is_home !== undefined ? latestMatch.is_home : (calInfo ? calInfo.is_home : true);
        const homeTag = isHome ? '🏠 Casa' : '✈️ Fuori';
        const oppName = (latestMatch.opponent && latestMatch.opponent !== '-' && latestMatch.opponent !== 'undefined') ? latestMatch.opponent : (calInfo ? calInfo.opponent : 'Avversario');
        const matchTitle = (latestMatch.match && !latestMatch.match.includes('undefined') && latestMatch.match !== 'vs -') ? latestMatch.match : (calInfo ? calInfo.match_str : `vs ${oppName}`);
        const bmStr = computeBonusMalusStr(latestMatch);
        const hasV = latestMatch.voto !== null && latestMatch.voto !== undefined;
        const vColor = hasV ? (latestMatch.voto >= 7 ? '#34d399' : (latestMatch.voto >= 6 ? '#38bdf8' : (latestMatch.voto >= 5.5 ? '#fbbf24' : '#f87171'))) : 'var(--text-muted)';
        const fvColor = latestMatch.fantavoto !== null && latestMatch.fantavoto !== undefined ? (latestMatch.fantavoto >= 10 ? '#10b981' : (latestMatch.fantavoto >= 7 ? '#38bdf8' : (latestMatch.fantavoto < 5 ? '#f87171' : '#fbbf24'))) : 'var(--text-muted)';
        initialInspectorHtml = `
            <div class="match-inspector-card" id="seasonMatchInspectorCard">
                <div class="inspector-header">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                        <span class="inspector-badge">GIORNATA ${latestMatch.giornata}</span>
                        <span class="inspector-venue">${homeTag}</span>
                        <b class="inspector-match-title">${matchTitle}</b>
                    </div>
                    <span class="inspector-hint-text"><span class="hint-desktop">Passa il mouse</span><span class="hint-mobile">Tocca</span> sulle barre per ispezionare</span>
                </div>
                <div class="inspector-body-grid">
                    <div class="inspector-metric">
                        <span class="lbl">Voto Base</span>
                        <b class="val" style="color:${vColor};">${hasV ? latestMatch.voto : 's.v.'}</b>
                    </div>
                    <div class="inspector-metric highlight">
                        <span class="lbl">FantaVoto</span>
                        <b class="val" style="color:${fvColor};font-size:17px;">${latestMatch.fantavoto !== null && latestMatch.fantavoto !== undefined ? latestMatch.fantavoto : '-'}</b>
                    </div>
                    <div class="inspector-metric">
                        <span class="lbl">Bonus / Malus</span>
                        <span class="val-bonus">${bmStr}</span>
                    </div>
                    <div class="inspector-metric">
                        <span class="lbl">Gol / Assist</span>
                        <b class="val">${latestMatch.gf || 0} Gol • ${latestMatch.ass || 0} Ass</b>
                    </div>
                    <div class="inspector-metric">
                        <span class="lbl">Disciplina</span>
                        <span class="val" style="color:${(latestMatch.amm || 0) > 0 ? '#ef4444' : 'var(--text-secondary)'};">${latestMatch.amm || 0} Amm • ${latestMatch.esp || 0} Esp</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        const nextMatch = getMatchInfoForTeamAndRound(p.team, 1);
        initialInspectorHtml = `
            <div class="match-inspector-card" id="seasonMatchInspectorCard">
                <div class="inspector-header">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                        <span class="inspector-badge" style="background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.3);color:var(--accent-cyan);">GIORNATA 1</span>
                        <span class="inspector-venue">${nextMatch ? (nextMatch.is_home ? '🏠 Casa' : '✈️ Fuori') : 'Serie A'}</span>
                        <b class="inspector-match-title">${nextMatch ? nextMatch.match_str : 'Gara in Programma'}</b>
                    </div>
                    <span style="font-size:10.5px;color:var(--text-muted);">${nextMatch && nextMatch.date ? 'Data: ' + nextMatch.date : 'Stagione 2026/27'}</span>
                </div>
                <div style="font-size:11.5px;color:var(--text-secondary);padding:6px 0;">Nessun voto registrato finora per questa stagione.</div>
            </div>
        `;
    }
    let tableRowsHtml = '';
    if (votiList.length > 0) {
        tableRowsHtml = votiList.map(v => {
            const hasV = v.voto !== null && v.voto !== undefined;
            const vC = hasV ? (v.voto >= 7 ? '#34d399' : (v.voto >= 6 ? '#38bdf8' : (v.voto >= 5.5 ? '#fbbf24' : '#f87171'))) : 'var(--text-muted)';
            const fvC = v.fantavoto !== null && v.fantavoto !== undefined ? (v.fantavoto >= 10 ? '#10b981' : (v.fantavoto >= 7 ? '#38bdf8' : (v.fantavoto < 5 ? '#f87171' : '#fbbf24'))) : 'var(--text-muted)';
            const calInfo = getMatchInfoForTeamAndRound(p.team, v.giornata);
            const isHome = v.is_home !== undefined ? v.is_home : (calInfo ? calInfo.is_home : true);
            const oppName = (v.opponent && v.opponent !== '-' && v.opponent !== 'undefined') ? v.opponent : (calInfo ? calInfo.opponent : 'Avversario');
            const matchTitle = (v.match && !v.match.includes('undefined') && v.match !== 'vs -') ? v.match : (calInfo ? calInfo.match_str : `vs ${oppName}`);
            const bmStr = computeBonusMalusStr(v);
            return `
                <tr>
                    <td style="font-weight:900;color:var(--accent-cyan);">G${v.giornata}</td>
                    <td style="font-weight:700;color:#fff;">${matchTitle}</td>
                    <td style="color:var(--text-muted);font-size:11px;">${isHome ? '🏠 Casa' : '✈️ Fuori'}</td>
                    <td style="font-weight:900;color:${vC};">${hasV ? v.voto : 's.v.'}</td>
                    <td><span class="table-bonus-tag">${bmStr}</span></td>
                    <td style="font-weight:900;color:${fvC};font-size:13px;">${v.fantavoto !== null && v.fantavoto !== undefined ? v.fantavoto : '-'}</td>
                </tr>
            `;
        }).join('');
    } else {
        tableRowsHtml = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:12px;">Nessun dato registrato</td></tr>`;
    }
    const fmVal = p.fm_2627 ? p.fm_2627.toFixed(2) : '-';
    const mvVal = p.mv_2627 ? p.mv_2627.toFixed(2) : '-';
    const tabOverviewHtml = `
        <div id="profileTabPane_overview" class="profile-tab-pane" style="display:block;">
            <!-- 3 Pill Bar Gauges (Titolarità, Affidabilità Voto, Integrità Fisica) -->
            ${quickGaugesHtml}
            <!-- Live Season Summary Bar -->
            <div class="profile-season-summary-bar">
                <div class="profile-season-header-row">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:16px;">📈</span>
                        <span style="font-size:13px;font-weight:800;color:#fff;">Rendimento Live 2026/27</span>
                    </div>
                    ${smartTrend ? `<span class="trend-badge-clean" style="color:${smartTrend.color};font-weight:800;font-size:12px;" title="${smartTrend.desc}">${smartTrend.label}</span>` : ''}
                </div>
                <div class="summary-kpis-grid">
                    <div class="kpi-mini-card">
                        <span class="kpi-mini-lbl">FM</span>
                        <b class="kpi-mini-val" style="color:#fbbf24;">${fmVal}</b>
                    </div>
                    <div class="kpi-mini-card">
                        <span class="kpi-mini-lbl">MV</span>
                        <b class="kpi-mini-val" style="color:#4ade80;">${mvVal}</b>
                    </div>
                    <div class="kpi-mini-card">
                        <span class="kpi-mini-lbl">xFM</span>
                        <b class="kpi-mini-val" style="color:var(--accent-cyan);">${xfmData.xfm}</b>
                    </div>
                    <div class="kpi-mini-card">
                        <span class="kpi-mini-lbl">Sufficienze</span>
                        <b class="kpi-mini-val" style="color:#38bdf8;">${sufficiencyPct}% <small style="font-size:9.5px;font-weight:600;color:var(--text-muted);">(${sufficiencyCount}/${validVoti.length})</small></b>
                    </div>
                    <div class="kpi-mini-card">
                        <span class="kpi-mini-lbl">Bonus Tot</span>
                        <b class="kpi-mini-val" style="color:#fde047;">+${p.tot_bonus_2627 || 0}</b>
                    </div>
                    <div class="kpi-mini-card">
                        <span class="kpi-mini-lbl">Minuti</span>
                        <b class="kpi-mini-val" style="color:#fff;">${p.minuti_2627 || 0}'</b>
                    </div>
                </div>
            </div>
            <!-- Regression Alert Banner -->
            ${xfmAlertHtml}
            <!-- AI Strengths & Weaknesses (100% Free & Transparent) -->
            ${aiStrengthsWeaknessesHtml}
            <!-- Strategic Auction Roadmap -->
            ${auctionRoadmapHtml}
            <!-- Tandem / Coppia Card (if applicable) -->
            ${tandemCardHtml}
            <!-- 38-ROUND SEASON PERFORMANCE HUB -->
            <div class="profile-andamento-container">
                <div class="andamento-title">
                    <div class="andamento-title-group">
                        <span class="andamento-main-title">📊 Rendimento Stagionale</span>
                        <span class="andamento-sub-info">(G1-G${maxPlayedRound} Giocate • G${maxPlayedRound+1}-G38 In Arrivo)</span>
                    </div>
                    <div class="season-view-toggle">
                        <button id="btnSeasonView_chart" class="season-toggle-btn active" onclick="switchSeasonView('chart')">📈 Grafico</button>
                        <button id="btnSeasonView_table" class="season-toggle-btn" onclick="switchSeasonView('table')">📋 Tabella</button>
                    </div>
                </div>
                <!-- Legend & Reference -->
                <div class="season-chart-legend">
                    <span class="legend-item"><span class="legend-box green"></span> Voto Base</span>
                    <span class="legend-item"><span class="legend-box gold"></span> Bonus (+Gol/Assist)</span>
                    <span class="legend-item"><span class="legend-box red"></span> Malus Concesso</span>
                    <span class="legend-item"><span class="legend-line"></span> FantaVoto Finale</span>
                    <span class="legend-item"><span class="legend-line dashed cyan"></span> Sufficienza (6.0)</span>
                </div>
                <!-- View 1: 38-Round SVG Chart -->
                <div id="seasonPerformanceView_chart" class="season-chart-box" style="display:block;">
                    <div class="season-svg-scroll-wrapper">
                        ${seasonChartSvg}
                    </div>
                    ${initialInspectorHtml}
                </div>
                <!-- View 2: Full Table -->
                <div id="seasonPerformanceView_table" class="season-table-box" style="display:none;">
                    <div class="season-table-scroll">
                        <table class="season-voti-table">
                            <thead>
                                <tr>
                                    <th>G</th>
                                    <th>Partita</th>
                                    <th>Luogo</th>
                                    <th>Voto Base</th>
                                    <th>Bonus / Malus</th>
                                    <th>FantaVoto</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <!-- Key Quick Info (4-card Executive Grid) -->
            <div class="profile-quick-info-grid">
                <div class="quick-info-box card-advice">
                    <div class="quick-info-header">
                        <span class="quick-info-icon">💡</span>
                        <span class="lbl">Consiglio Strategico AI</span>
                    </div>
                    <div class="quick-info-content">
                        <span class="quick-badge advice-badge ${p.ai_advice_type || 'regular'}">${p.ai_advice || p.consiglio || '-'}</span>
                    </div>
                </div>
                <div class="quick-info-box card-slot">
                    <div class="quick-info-header">
                        <span class="quick-info-icon">🎯</span>
                        <span class="lbl">Gerarchia & Slot</span>
                    </div>
                    <div class="quick-info-content">
                        <span class="quick-badge slot-badge">${p.slot_fascia || (p.slot_num ? p.slot_num + '° Slot' : 'Slot -')}</span>
                    </div>
                </div>
                <div class="quick-info-box card-injury">
                    <div class="quick-info-header">
                        <span class="quick-info-icon">🩺</span>
                        <span class="lbl">Integrità Fisica</span>
                    </div>
                    <div class="quick-info-content">
                        <span class="quick-badge health-badge ${p.is_injured ? 'injured' : 'healthy'}">
                            ${p.is_injured ? `🩹 Infortunato (${p.infortunio_rientro || 'TBD'})` : '🟢 Integro (Basso Rischio)'}
                        </span>
                    </div>
                </div>
                <div class="quick-info-box card-mantra">
                    <div class="quick-info-header">
                        <span class="quick-info-icon">💎</span>
                        <span class="lbl">Ruoli Mantra</span>
                    </div>
                    <div class="quick-info-content">
                        <div class="mantra-badges-container">
                            ${renderMantraQuickBadges(p.mantra)}
                        </div>
                    </div>
                </div>
            </div>
            <!-- Multi-Season Injury & Physical Reliability Hub -->
            ${generateInjuryHistoryCardHtml(p)}
        </div>
    `;
    const radarChartHtml = generateRadarChartSvg(p);
    let advancedContentHtml = '';
    if (p.role === 'P') {
        advancedContentHtml = `
            <div class="profile-pillars-row">
                <div class="profile-pillar-card pillar-gk">
                    <div class="pillar-title"><span>🧤 DIFESA & PASSIVO</span><span class="source-tag">Statistiche</span></div>
                    <div class="pillar-hero-stat">
                        <span class="hero-label">GOL SUBITI 26/27</span>
                        <span class="hero-val" style="color:#ef4444;">${p.gol_subiti_2627 || 0} <small>(${p.clean_sheets_2627 || 0} CS)</small></span>
                    </div>
                    <div class="pillar-stat-list">
                        <div class="pillar-stat-item"><span class="stat-name">% Parate</span><span class="stat-num" style="color:#38bdf8;">${p.save_pct_2627 ? p.save_pct_2627 + '%' : '-'}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Parate Effettuate</span><span class="stat-num" style="color:#4ade80;">${p.parate_2627 || 0}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Gol Evitati (Goals Prevented)</span><span class="stat-num" style="color:${(p.goals_prevented_2627 || 0) >= 0 ? '#10b981' : '#f87171'};font-weight:800;">${(p.goals_prevented_2627 || 0) > 0 ? '+' : ''}${p.goals_prevented_2627 || 0}</span></div>
                    </div>
                    <div class="pillar-comparison-chip">
                        <span>Storico 2025/26</span><b>${p.gs || 0} GS • ${p.clean_sheets_2526 || 0} Clean Sheet</b>
                    </div>
                </div>
                <div class="profile-pillar-card pillar-ratings">
                    <div class="pillar-title"><span>📊 RENDIMENTO & MODIFICATORE</span><span class="source-tag">Prestazioni</span></div>
                    <div class="pillar-hero-stat">
                        <span class="hero-label">MEDIA VOTO PURA</span>
                        <span class="hero-val" style="color:#4ade80;">${mvVal}</span>
                    </div>
                    <div class="pillar-stat-list">
                        <div class="pillar-stat-item"><span class="stat-name">FantaMedia Ufficiale</span><span class="stat-num" style="color:#fbbf24;">${fmVal}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Expected FantaMedia (xFM)</span><span class="stat-num" style="color:var(--accent-cyan);font-weight:900;">${xfmData.xfm}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Match Rating Statistico</span><span class="stat-num" style="color:#38bdf8;">${p.rating_live_2627 ? p.rating_live_2627.toFixed(2) : '-'}</span></div>
                    </div>
                    <div class="pillar-comparison-chip">
                        <span>Storico 2025/26</span><b>MV ${p.mv > 0 ? p.mv : '-'} • FM ${p.fm > 0 ? p.fm : '-'}</b>
                    </div>
                </div>
                <div class="profile-pillar-card pillar-assists">
                    <div class="pillar-title"><span>⏱️ MINUTAGGIO & PRESENZA</span><span class="source-tag">Stagione</span></div>
                    <div class="pillar-hero-stat">
                        <span class="hero-label">MINUTI GIOCATI</span>
                        <span class="hero-val">${p.minuti_2627 || 0}'</span>
                    </div>
                    <div class="pillar-stat-list">
                        <div class="pillar-stat-item"><span class="stat-name">Presenze / Titolarità</span><span class="stat-num">${p.presenze_2627 || 0} (${p.starts_2627 || 0} tit)</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Status Tattico</span><span class="stat-num" style="color:#4ade80;">${p.titolarita_desc_2627 || 'Titolare'}</span></div>
                    </div>
                    <div class="pillar-comparison-chip">
                        <span>Storico 2025/26</span><b>${p.presenze || 0} presenze a voto</b>
                    </div>
                </div>
            </div>
        `;
    } else {
        advancedContentHtml = `
            <div class="profile-pillars-row">
                <div class="profile-pillar-card pillar-goals">
                    <div class="pillar-title"><span>⚽ ATTACCO & TIRO</span><span class="source-tag">Volume</span></div>
                    <div class="pillar-hero-stat">
                        <span class="hero-label">GOL SEGNATI 26/27</span>
                        <span class="hero-val" style="color:#fbbf24;">${p.gol_2627 || 0} Gol <small>(${p.xg_2627 !== null && p.xg_2627 !== undefined ? p.xg_2627 + ' xG' : (p.xg90_2627 ? p.xg90_2627 + ' xG/90' : '-')})</small></span>
                    </div>
                    <div class="pillar-stat-list">
                        <div class="pillar-stat-item"><span class="stat-name">Tiri Totali</span><span class="stat-num">${p.tiri_2627 || (p.total_scoring_att_2627 ? p.total_scoring_att_2627 + '/90' : 0)}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Qualità Tiro (xGOT)</span><span class="stat-num" style="color:#f472b6;">${p.xgot_2627 !== null && p.xgot_2627 !== undefined ? p.xgot_2627 : '-'}</span></div>
                        ${(p.big_chance_missed_2627 || 0) > 0 ? `<div class="pillar-stat-item"><span class="stat-name">Grandi Occasioni Fallite</span><span class="stat-num" style="color:#f87171;">${p.big_chance_missed_2627}</span></div>` : ''}
                    </div>
                    <div class="pillar-comparison-chip">
                        <span>Storico 2025/26</span><b>${p.gf || 0} Gol (${p.xg90_2526 || 0} xG/90)</b>
                    </div>
                </div>
                <div class="profile-pillar-card pillar-assists">
                    <div class="pillar-title"><span>🪄 CREATIVITÀ & ASSIST</span><span class="source-tag">Rifinitura</span></div>
                    <div class="pillar-hero-stat">
                        <span class="hero-label">ASSIST FORNITI 26/27</span>
                        <span class="hero-val" style="color:#00f2fe;">${p.assist_2627 || 0} Assist <small>(${p.xa90_2627 ? p.xa90_2627 + ' xA/90' : '-'})</small></span>
                    </div>
                    <div class="pillar-stat-list">
                        <div class="pillar-stat-item"><span class="stat-name">Occasioni Create (Key Passes)</span><span class="stat-num">${p.chances_created_2627 || p.key_passes_2627 || 0}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Grandi Occasioni Create</span><span class="stat-num" style="color:#fbbf24;">${p.big_chances_created_2627 || 0}</span></div>
                        ${p.won_contest_2627 ? `<div class="pillar-stat-item"><span class="stat-name">Dribbling Vinti /90</span><span class="stat-num" style="color:#38bdf8;">${p.won_contest_2627}</span></div>` : ''}
                    </div>
                    <div class="pillar-comparison-chip">
                        <span>Storico 2025/26</span><b>${p.ass || 0} Assist (${p.xa90_2526 || 0} xA/90)</b>
                    </div>
                </div>
                <div class="profile-pillar-card pillar-ratings">
                    <div class="pillar-title"><span>🛡️ PRESENZA & RENDIMENTO</span><span class="source-tag">Sul Campo</span></div>
                    <div class="pillar-hero-stat">
                        <span class="hero-label">MINUTI GIOCATI</span>
                        <span class="hero-val">${p.minuti_2627 || 0}' <small>(${p.starts_2627 || 0} tit)</small></span>
                    </div>
                    <div class="pillar-stat-list">
                        <div class="pillar-stat-item"><span class="stat-name">Palle Recuperate</span><span class="stat-num">${p.recuperi_2627 || 0}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Expected FantaMedia (xFM)</span><span class="stat-num" style="color:var(--accent-cyan);font-weight:900;">${xfmData.xfm}</span></div>
                        <div class="pillar-stat-item"><span class="stat-name">Disciplina (Amm/Esp)</span><span class="stat-num" style="color:${p.amm_2627 > 0 ? '#ef4444' : 'var(--text-muted)'};">${p.amm_2627 || 0} Amm • ${p.esp_2627 || 0} Esp</span></div>
                    </div>
                    <div class="pillar-comparison-chip">
                        <span>Storico 2025/26</span><b>MV ${p.mv > 0 ? p.mv : '-'} • FM ${p.fm > 0 ? p.fm : '-'}</b>
                    </div>
                </div>
            </div>
        `;
    }
    const tCtx = p.team_context || (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[p.team]) || {};
    const teamStatsHtml = tCtx && tCtx.xg_team ? `
        <div class="team-ecosystem-bar">
            <div style="display:flex;align-items:center;gap:6px;">
                <span>🏟️</span>
                <b>Ecosistema ${p.team}:</b>
                <span>Attacco: <b style="color:#f472b6;">#${tCtx.xg_team_rank || '-'}</b> (${tCtx.xg_team || 0} xG • ${tCtx.big_chances_team || 0} occ.)</span>
                <span>•</span>
                <span>Difesa: <b style="color:#38bdf8;">#${tCtx.xga_team_rank || '-'}</b> (${tCtx.xga_team || 0} xGA • ${tCtx.clean_sheets_team || 0} CS)</span>
            </div>
            <div style="font-size:11px;color:var(--text-muted);">Statistiche Live 2026/27</div>
        </div>
    ` : '';
    const tabAdvancedHtml = `
        <div id="profileTabPane_advanced" class="profile-tab-pane" style="display:none;">
            <!-- Radar Chart Section -->
            ${radarChartHtml}
            <!-- 3 Pillars Row -->
            ${advancedContentHtml}
            <!-- Team Ecosystem -->
            ${teamStatsHtml}
        </div>
    `;
    let tacticsContentHtml = '';
    if (teamTac) {
        tacticsContentHtml = `
            <div class="tactics-overview-grid">
                <div class="tactics-card">
                    <div class="tactics-card-header">
                        <span style="font-size:16px;">👔</span>
                        <h4>Guida Tecnica & Assetto</h4>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">Allenatore:</span>
                        <b class="val" style="color:#fff;">${teamTac.all || '-'}</b>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">Modulo Base:</span>
                        <b class="val" style="color:var(--accent-cyan);">${teamTac.modulo || '-'}</b>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">Stile Tattico:</span>
                        <span class="val" style="color:var(--text-secondary);font-size:11.5px;">${teamTac.stile || 'Costruzione dal basso, pressing organizzato'}</span>
                    </div>
                </div>
                <div class="tactics-card">
                    <div class="tactics-card-header">
                        <span style="font-size:16px;">🎯</span>
                        <h4>Calci Piazzati & Gerarchie</h4>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">1° Rigorista:</span>
                        <b class="val" style="color:#fbbf24;">${teamTac.rigorista_1 || p.rigorista_val || '-'}</b>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">2°/3° Rigorista:</span>
                        <span class="val">${teamTac.rigorista_2 || '-'} / ${teamTac.rigorista_3 || '-'}</span>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">Corner & Punizioni:</span>
                        <span class="val" style="color:#38bdf8;">${teamTac.punizioni || teamTac.corner || '-'}</span>
                    </div>
                </div>
                <div class="tactics-card">
                    <div class="tactics-card-header">
                        <span style="font-size:16px;">${p.role === 'P' ? '🧤' : '🔄'}</span>
                        <h4>${p.role === 'P' ? 'Gerarchia Porta & Copertura' : 'Ballottaggio & Copertura'}</h4>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">Titolarità Stimata:</span>
                        <b class="val" style="color:${titColor};">${p.titolarita || 0}% (${p.role === 'P' ? (p.titolarita >= 82 ? 'Numero 1 Indiscusso' : (p.titolarita <= 38 ? 'Secondo Portiere' : 'Ballottaggio Aperto')) : (p.titolarita_desc_2627 || (p.titolarita >= 75 ? 'Titolare' : 'Rotazione'))})</b>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">${p.role === 'P' ? (p.titolarita >= 68 ? 'Secondo Portiere:' : 'Primo Portiere:') : 'Compagno di Reparto:'}</span>
                        <b class="val" style="color:#38bdf8;">${p.coppia_nome || 'Nessun compagno diretto'}</b>
                    </div>
                    <div class="tactics-meta-row">
                        <span class="lbl">Tipo Alternanza:</span>
                        <span class="val">${p.role === 'P' ? (p.titolarita >= 82 ? 'Nessuna staffetta (titolare fisso, vice per copertura)' : (p.titolarita <= 38 ? 'Secondo portiere (gioca solo se manca il 1°)' : 'Staffetta / Ballottaggio Aperto')) : (p.titolarita >= 75 ? 'Titolare solido (rotazioni a partita in corso)' : (p.titolarita <= 35 ? 'Riserva' : 'Ballottaggio aperto'))}</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        tacticsContentHtml = `
            <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border-glass);padding:16px;border-radius:10px;text-align:center;color:var(--text-muted);font-size:12.5px;">
                Dati tattici di club non disponibili per ${p.team}.
            </div>
        `;
    }
    let mantraFormationsHtml = '';
    if (typeof State !== 'undefined' && State.systemMode === 'mantra' && typeof MANTRA_FORMATIONS !== 'undefined') {
        const pRoles = (p.mantra || '').split(';').map(r => r.trim());
        const fittingMods = Object.keys(MANTRA_FORMATIONS).filter(m => {
            const sch = MANTRA_FORMATIONS[m];
            return sch.slots.some(slot => slot.roles.some(r => pRoles.includes(r)));
        });
        if (fittingMods.length > 0) {
            mantraFormationsHtml = `
                <div style="margin-top:14px;background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.25);border-radius:10px;padding:12px 14px;">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;font-size:12px;color:var(--accent-purple);font-weight:800;">
                        <span>💎</span> Schemi Mantra Compatibili (${fittingMods.length}/11):
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;">
                        ${fittingMods.map(m => `<span class="mantra-schema-chip">${m}</span>`).join('')}
                    </div>
                </div>
            `;
        }
    }
    const tabTacticsHtml = `
        <div id="profileTabPane_tactics" class="profile-tab-pane" style="display:none;">
            ${tacticsContentHtml}
            ${mantraFormationsHtml}
        </div>
    `;
    const diffQStr = (p.diff_q !== undefined && p.diff_q !== 0) ? (p.diff_q > 0 ? '+' + p.diff_q : p.diff_q) : '';
    modalBody.innerHTML = `
        <!-- Profile Header -->
        <div class="profile-header-container">
            <div class="profile-hero-left">
                ${(typeof State !== 'undefined' && State.systemMode === 'mantra') 
                    ? `<div class="profile-mantra-roles">${renderMantraRoleBadges(p.mantra)}</div>`
                    : `<div class="profile-role-circle ${p.role}">${p.role}</div>`
                }
                <div class="profile-hero-info">
                    <div class="profile-hero-title-row">
                        <h1 class="profile-player-name">${p.name}</h1>
                        <div class="profile-title-actions">
                            <button class="sb-star-toggle ${isFav ? 'active' : ''}" onclick="toggleFavorite(${p.id}); openPlayerProfileModal(${p.id});" title="Aggiungi ai Preferiti">${isFav ? '⭐' : '☆'}</button>
                            <button onclick="openEditPlayerModal(${p.id})" title="Personalizza (Solo Admin)" class="btn-player-edit creator-only-control">✏️</button>
                        </div>
                    </div>
                    <div class="profile-player-meta">
                        <b class="player-meta-team">${p.team}</b> • Mister: <b>${teamTac ? teamTac.all : '-'}</b> <span style="color:var(--text-muted);">(${teamTac ? teamTac.modulo : '-'})</span>
                    </div>
                    <div class="profile-badges-wrapper">
                        <div class="profile-primary-badges">
                            <span class="ai-advice-badge ${p.ai_advice_type || 'regular'}">${p.ai_advice || p.consiglio}</span>
                            <span class="badge-tag gold">${p.slot_fascia || (p.slot_num ? p.slot_num + '° Slot' : '')}</span>
                        </div>
                        <div class="profile-tactical-pills">
                            ${injBadge}
                            ${rigoristaBadge}
                            ${coppiaBadge}
                            ${oopBadge}
                        </div>
                    </div>
                </div>
            </div>
            <!-- Hero Metrics Deck -->
            <div class="profile-hero-metrics-section">
                <div class="profile-hero-triple-cards">
                    <div class="profile-hero-metric-card card-ovr">
                        <span class="hero-card-label">OVR RATING</span>
                        <div class="hero-card-value ovr-text ${getOvrClass(p.ovr)}">${p.ovr}</div>
                        <span class="hero-card-sub">${p.ovr >= 90 ? 'Top Assoluto' : (p.ovr >= 82 ? 'Titolare Top' : 'Rotazione')}</span>
                    </div>
                    <div class="profile-hero-metric-card card-titolarita">
                        <span class="hero-card-label">TITOLARITÀ</span>
                        <div class="hero-card-value" style="color:${titColor};">${p.titolarita}%</div>
                        <span class="hero-card-sub" style="color:${titColor};">${p.titolarita_desc_2627 || (p.is_in_11 ? '11 Tit' : 'Rotaz.')}</span>
                    </div>
                    <div class="profile-hero-metric-card card-price">
                        <span class="hero-card-label">PREZZO (${curBudgetTotal} CR)</span>
                        <div class="hero-card-value price-text">${scaledPrice} <span style="font-size:11px;color:rgba(255,255,255,0.6);">CR</span></div>
                        <span class="hero-card-sub" style="color:#fbbf24;">🎯 <b>${budgetPct}%</b> budget</span>
                    </div>
                </div>
                <div class="profile-hero-sub-strip">
                    <div class="sub-stat-chip">
                        <span class="sub-stat-lbl">FVM (${curBudgetTotal} CR):</span>
                        <b class="sub-stat-val text-cyan">${scaledFvm} CR</b>
                    </div>
                    <span class="sub-stat-dot">•</span>
                    <div class="sub-stat-chip">
                        <span class="sub-stat-lbl">Max Rilancio:</span>
                        <b class="sub-stat-val" style="color:#f43f5e;">${scaledMaxBid} CR</b>
                    </div>
                    <span class="sub-stat-dot">•</span>
                    <div class="sub-stat-chip">
                        <span class="sub-stat-lbl">Quotazione:</span>
                        <b class="sub-stat-val text-purple">${p.qta || '-'}</b>
                        ${diffQStr ? `<small class="sub-stat-diff ${p.diff_q > 0 ? 'pos' : (p.diff_q < 0 ? 'neg' : '')}">${diffQStr}</small>` : ''}
                    </div>
                </div>
            </div>
        </div>
        <!-- Quick Action Bar -->
        <div class="profile-action-bar">
            ${actionButtonsHtml}
        </div>
        <!-- Clean 3-Tab Controls -->
        <div class="profile-3tabs-nav">
            <button id="profileTabBtn_overview" class="profile-3tab-btn active" onclick="switchProfileTab('overview')">
                <span class="tab-icon">📋</span>
                <span class="tab-txt-desktop">Panoramica & Voti</span>
                <span class="tab-txt-mobile">Panoramica</span>
            </button>
            <button id="profileTabBtn_advanced" class="profile-3tab-btn" onclick="switchProfileTab('advanced')">
                <span class="tab-icon">📊</span>
                <span class="tab-txt-desktop">Statistiche Avanzate & Radar</span>
                <span class="tab-txt-mobile">Statistiche</span>
            </button>
            <button id="profileTabBtn_tactics" class="profile-3tab-btn" onclick="switchProfileTab('tactics')">
                <span class="tab-icon">🛡️</span>
                <span class="tab-txt-desktop">Tattica & Contesto Club</span>
                <span class="tab-txt-mobile">Tattica</span>
            </button>
        </div>
        <!-- Tab Panes -->
        ${tabOverviewHtml}
        ${tabAdvancedHtml}
        ${tabTacticsHtml}
    `;
    modal.classList.add('active');
    modal.style.display = 'flex';
}
function closePlayerProfileModal() {
    const modal = document.getElementById('playerDetailModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
}
function switchSeasonView(viewType) {
    const chartView = document.getElementById('seasonPerformanceView_chart');
    const tableView = document.getElementById('seasonPerformanceView_table');
    const btnChart = document.getElementById('btnSeasonView_chart');
    const btnTable = document.getElementById('btnSeasonView_table');
    if (viewType === 'chart') {
        if (chartView) chartView.style.display = 'block';
        if (tableView) tableView.style.display = 'none';
        if (btnChart) btnChart.classList.add('active');
        if (btnTable) btnTable.classList.remove('active');
    } else {
        if (chartView) chartView.style.display = 'none';
        if (tableView) tableView.style.display = 'block';
        if (btnChart) btnChart.classList.remove('active');
        if (btnTable) btnTable.classList.add('active');
    }
}
function previewSeasonRound(playerId, roundNum) {
    updateSeasonInspector(playerId, roundNum);
}
function selectSeasonRound(playerId, roundNum) {
    updateSeasonInspector(playerId, roundNum);
}
function updateSeasonInspector(playerId, roundNum) {
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;
    const votiList = p.voti_dettaglio_2627 || [];
    const match = votiList.find(v => v.giornata === roundNum);
    const inspectorEl = document.getElementById('seasonMatchInspectorCard');
    if (!inspectorEl) return;
    if (match) {
        const calInfo = getMatchInfoForTeamAndRound(p.team, match.giornata);
        const isHome = match.is_home !== undefined ? match.is_home : (calInfo ? calInfo.is_home : true);
        const homeTag = isHome ? '🏠 Casa' : '✈️ Fuori';
        const oppName = (match.opponent && match.opponent !== '-' && match.opponent !== 'undefined') ? match.opponent : (calInfo ? calInfo.opponent : 'Avversario');
        const matchTitle = (match.match && !match.match.includes('undefined') && match.match !== 'vs -') ? match.match : (calInfo ? calInfo.match_str : `vs ${oppName}`);
        const bmStr = computeBonusMalusStr(match);
        const hasV = match.voto !== null && match.voto !== undefined;
        const vColor = hasV ? (match.voto >= 7 ? '#34d399' : (match.voto >= 6 ? '#38bdf8' : (match.voto >= 5.5 ? '#fbbf24' : '#f87171'))) : 'var(--text-muted)';
        const fvColor = match.fantavoto !== null && match.fantavoto !== undefined ? (match.fantavoto >= 10 ? '#10b981' : (match.fantavoto >= 7 ? '#38bdf8' : (match.fantavoto < 5 ? '#f87171' : '#fbbf24'))) : 'var(--text-muted)';
        inspectorEl.innerHTML = `
            <div class="inspector-header">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="inspector-badge">GIORNATA ${match.giornata}</span>
                    <span class="inspector-venue">${homeTag}</span>
                    <b class="inspector-match-title">${matchTitle}</b>
                </div>
                <span style="font-size:10.5px;color:var(--text-muted);">Dettaglio match disputato</span>
            </div>
            <div class="inspector-body-grid">
                <div class="inspector-metric">
                    <span class="lbl">Voto Base</span>
                    <b class="val" style="color:${vColor};">${hasV ? match.voto : 's.v.'}</b>
                </div>
                <div class="inspector-metric highlight">
                    <span class="lbl">FantaVoto</span>
                    <b class="val" style="color:${fvColor};font-size:17px;">${match.fantavoto !== null && match.fantavoto !== undefined ? match.fantavoto : '-'}</b>
                </div>
                <div class="inspector-metric">
                    <span class="lbl">Bonus / Malus</span>
                    <span class="val-bonus">${bmStr}</span>
                </div>
                <div class="inspector-metric">
                    <span class="lbl">Gol / Assist</span>
                    <b class="val">${match.gf || 0} Gol • ${match.ass || 0} Ass</b>
                </div>
                <div class="inspector-metric">
                    <span class="lbl">Disciplina</span>
                    <span class="val" style="color:${(match.amm || 0) > 0 ? '#ef4444' : 'var(--text-secondary)'};">${match.amm || 0} Amm • ${match.esp || 0} Esp</span>
                </div>
            </div>
        `;
    } else {
        const calInfo = getMatchInfoForTeamAndRound(p.team, roundNum);
        if (calInfo) {
            const homeTag = calInfo.is_home ? '🏠 Casa' : '✈️ Fuori';
            inspectorEl.innerHTML = `
                <div class="inspector-header">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span class="inspector-badge" style="background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.3);color:var(--accent-cyan);">GIORNATA ${roundNum}</span>
                        <span class="inspector-venue">${homeTag}</span>
                        <b class="inspector-match-title" style="color:#fff;">${calInfo.match_str}</b>
                    </div>
                    <span style="font-size:10.5px;color:var(--text-muted);">${calInfo.date ? 'Data: ' + calInfo.date : 'Prossimo Turno'}</span>
                </div>
                <div style="font-size:11.5px;color:var(--text-secondary);padding:6px 0;display:flex;align-items:center;gap:8px;">
                    <span>🗓️ Gara in Calendario Serie A: <b>${p.team}</b> affronterà il <b>${calInfo.opponent}</b> (${calInfo.is_home ? 'in casa' : 'in trasferta'}). Voti e fantavoti verranno registrati al termine del turno.</span>
                </div>
            `;
        } else {
            inspectorEl.innerHTML = `
                <div class="inspector-header">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span class="inspector-badge" style="background:rgba(255,255,255,0.08);border-color:rgba(255,255,255,0.15);color:var(--text-muted);">GIORNATA ${roundNum}</span>
                        <b class="inspector-match-title" style="color:var(--text-muted);">Gara Futura / In Arrivo</b>
                    </div>
                </div>
                <div style="font-size:11.5px;color:var(--text-muted);padding:6px 0;">Questa giornata fa parte del calendario stagionale a 38 turni e verrà valorizzata automaticamente non appena saranno disponibili i voti ufficiali.</div>
            `;
        }
    }
}
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closePlayerProfileModal();
    }
});