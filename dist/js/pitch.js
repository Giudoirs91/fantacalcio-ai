function getPitchBandId(pos, modulo) {
    if (!pos) return 'pitchMed';
    pos = pos.toUpperCase();
    if (pos === 'P' || pos === 'POR') return 'pitchPor';
    if (pos.startsWith('PC') || pos.startsWith('PUN') || pos.startsWith('ATT') || ['SS', 'SP', 'A'].includes(pos)) {
        return 'pitchAtt';
    }
    if (pos.startsWith('TRQ')) {
        return 'pitchTrq';
    }
    if (pos === 'AD' || pos === 'AS') {
        if (modulo && (modulo.includes('4-3-3') || modulo.includes('3-4-3'))) {
            return 'pitchAtt'; // Ali d'attacco in linea con la punta
        }
        return 'pitchTrq'; // Ali / Trequartisti dietro la punta
    }
    if (['TD', 'TS', 'D'].includes(pos) || pos.startsWith('DC') || pos.startsWith('BRAC')) {
        return 'pitchDef';
    }
    if (['ED', 'ES', 'MED', 'CC', 'REG', 'C'].includes(pos) || pos.startsWith('MED') || pos.startsWith('CC') || pos.startsWith('MEZ')) {
        return 'pitchMed';
    }
    return 'pitchMed';
}
function renderPitchClubQuickBar(activeTeam) {
    const bar = document.getElementById('pitchClubQuickBar');
    if (!bar) return;
    const allTeams = Object.keys(TACTICAL_DB).sort();
    bar.innerHTML = allTeams.map(tm => {
        const isActive = tm.toLowerCase() === (activeTeam || '').toLowerCase();
        return `<button class="club-quick-btn ${isActive ? 'active' : ''}" onclick="renderPitchTeam('${tm}')">${tm}</button>`;
    }).join('');
}
function getTeamTacticalData(teamName) {
    if (!window.CUSTOM_TACTICAL_DB) {
        try {
            const saved = localStorage.getItem('FANTA_TACTICAL_DB_CUSTOM');
            window.CUSTOM_TACTICAL_DB = saved ? JSON.parse(saved) : {};
        } catch(e) {
            window.CUSTOM_TACTICAL_DB = {};
        }
    }
    return (window.CUSTOM_TACTICAL_DB && window.CUSTOM_TACTICAL_DB[teamName]) || TACTICAL_DB[teamName];
}
function getSubstituteForStarter(starter, team, teamPlayers) {
    if (starter.sub_name) {
        const subP = teamPlayers.find(pl => 
            pl.name.toLowerCase() === starter.sub_name.toLowerCase() ||
            pl.name.toLowerCase().includes(starter.sub_name.toLowerCase()) || 
            starter.sub_name.toLowerCase().includes(pl.name.toLowerCase())
        );
        return { name: starter.sub_name, role: starter.sub_role || (subP ? subP.role : starter.role) };
    }
    const sName = (starter.name || '').toLowerCase();
    if (team.ballottaggi && Array.isArray(team.ballottaggi)) {
        const b = team.ballottaggi.find(item => 
            (item.player && item.player.toLowerCase() === sName) ||
            (item.player && sName.includes(item.player.toLowerCase())) ||
            (item.player && item.player.toLowerCase().includes(sName))
        );
        if (b && b.vs) {
            const match = b.vs.match(/^([^(/\n]+)/);
            if (match) {
                const subName = match[1].trim();
                const subP = teamPlayers.find(pl => 
                    pl.name.toLowerCase() === subName.toLowerCase() ||
                    pl.name.toLowerCase().includes(subName.toLowerCase()) || 
                    subName.toLowerCase().includes(pl.name.toLowerCase())
                );
                if (subP) return { name: subP.name, role: subP.role };
                return { name: subName, role: starter.role };
            }
        }
    }
    if (starter.status) {
        const vsMatch = starter.status.match(/vs\s+([^(/\n]+)/i);
        if (vsMatch) {
            const subName = vsMatch[1].trim();
            const subP = teamPlayers.find(pl => 
                pl.name.toLowerCase() === subName.toLowerCase() ||
                pl.name.toLowerCase().includes(subName.toLowerCase()) || 
                subName.toLowerCase().includes(pl.name.toLowerCase())
            );
            if (subP) return { name: subP.name, role: subP.role };
            return { name: subName, role: starter.role };
        }
    }
    const starterNames = (team.lineup || []).map(l => (l.name || '').toLowerCase());
    const benchSameRole = teamPlayers.filter(pl => 
        !starterNames.some(sn => pl.name.toLowerCase().includes(sn) || sn.includes(pl.name.toLowerCase())) &&
        pl.role === starter.role
    ).sort((a, b) => (b.ovr || 0) - (a.ovr || 0));
    if (benchSameRole.length > 0) {
        return { name: benchSameRole[0].name, role: benchSameRole[0].role };
    }
    return null;
}
function renderPitchTeam(teamName) {
    if (!teamName) teamName = State.currentTeamPitch || 'Inter';
    State.currentTeamPitch = teamName;
    const selEl = document.getElementById('selectPitchTeam');
    if (selEl && selEl.value !== teamName) {
        selEl.value = teamName;
    }
    renderPitchClubQuickBar(teamName);
    const team = getTeamTacticalData(teamName);
    if (!team) return;
    ['pitchAtt', 'pitchTrq', 'pitchMed', 'pitchDef', 'pitchPor'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    });
    const oopPlayersList = [];
    const fpnPlayersList = [];
    const teamPlayers = PLAYERS.filter(pl => (pl.team || '').toLowerCase() === teamName.toLowerCase());
    team.lineup.forEach(p => {
        const node = document.createElement('div');
        node.className = 'pitch-player-node';
        let cardFppClass = '';
        let pillBadgeHtml = '';
        const fullP = teamPlayers.find(pl => pl.name.toLowerCase() === p.name.toLowerCase() || pl.name.toLowerCase().includes(p.name.toLowerCase()) || p.name.toLowerCase().includes(pl.name.toLowerCase()));
        const isFPP = (fullP && fullP.is_oop) || (p.fpp_fpn === 'FPP') || (p.oop && p.oop_type && p.oop_type.startsWith('FPP')) || (p.oop === true);
        const isFPN = (!isFPP) && ((fullP && fullP.fpp_fpn === 'FPN') || (p.fpp_fpn === 'FPN') || (p.oop_type && p.oop_type.startsWith('FPN')));
        const oopTier = (fullP && fullP.oop_tier) || p.oop_tier || 'ORO';
        if (isFPP) {
            oopPlayersList.push(fullP || p);
            if (oopTier === 'ORO') {
                cardFppClass = 'fpp-gold';
                pillBadgeHtml = `<div class="pitch-oop-pill oop-gold">🥇 ORO</div>`;
            } else if (oopTier === 'ARGENTO') {
                cardFppClass = 'fpp-silver';
                pillBadgeHtml = `<div class="pitch-oop-pill oop-silver">🥈 ARG</div>`;
            } else {
                cardFppClass = 'fpp-bronze';
                pillBadgeHtml = `<div class="pitch-oop-pill oop-bronze">🥉 BRZ</div>`;
            }
        } else if (isFPN) {
            fpnPlayersList.push(fullP || p);
            cardFppClass = 'fpn';
            pillBadgeHtml = `<div class="pitch-fpn-pill">FPN</div>`;
        }
        const ovrVal = fullP ? fullP.ovr : '';
        const ovrTierClass = (typeof getOvrClass === 'function' && ovrVal) ? getOvrClass(ovrVal) : '';
        const isInjured = fullP && (fullP.is_injured || (fullP.infortunio_motivo && fullP.infortunio_motivo !== ''));
        const injBadgeHtml = isInjured ? `<span class="pitch-inj-badge" title="Infortunato: ${fullP.infortunio_motivo || 'Indisponibile'} (Rientro previsto: ${fullP.infortunio_rientro || 'TBD'})">✚</span>` : '';
        const sub = getSubstituteForStarter(p, team, teamPlayers);
        const subHtml = sub ? `<div class="pitch-card-sub" title="Sostituto naturale / ballottaggio: ${sub.name} (${sub.role})"><span style="opacity:0.4;font-size:8px;">↳</span> <span style="font-weight:700;color:rgba(255,255,255,0.85);">${sub.name}</span> <span class="sub-role-badge ${sub.role}">${sub.role}</span></div>` : '';
        const pitchBadgeHtml = (typeof State !== 'undefined' && State.systemMode === 'mantra' && fullP && fullP.mantra)
            ? renderMantraRoleBadges(fullP.mantra)
            : `<div class="pitch-role-badge ${p.role}">${p.role}</div>`;
        node.innerHTML = `
            <div class="pitch-card ${cardFppClass}">
                <div class="pitch-card-header">
                    ${pitchBadgeHtml}
                    ${ovrVal ? `<span class="pitch-ovr-tag ${ovrTierClass}">${ovrVal}</span>` : ''}
                    ${pillBadgeHtml}
                    ${injBadgeHtml}
                </div>
                <div class="pitch-card-name" title="${p.name}">${p.name}</div>
                ${subHtml}
            </div>
        `;
        node.onclick = () => {
            if (fullP && typeof openPlayerProfileModal === 'function') {
                openPlayerProfileModal(fullP.id);
            }
        };
        const targetBand = getPitchBandId(p.pos, team.modulo);
        const bandEl = document.getElementById(targetBand);
        if (bandEl) bandEl.appendChild(node);
    });
    const dashboardEl = document.getElementById('teamTacticsDashboard');
    if (dashboardEl) {
        let oopSectionHtml = '';
        const teamOopPlayers = PLAYERS.filter(pl => (pl.team || '').toLowerCase() === teamName.toLowerCase() && pl.is_oop)
            .sort((a, b) => {
                const tierOrder = { 'ORO': 1, 'ARGENTO': 2, 'BRONZO': 3 };
                const ordA = tierOrder[a.oop_tier] || 4;
                const ordB = tierOrder[b.oop_tier] || 4;
                if (ordA !== ordB) return ordA - ordB;
                return (b.fvm || 0) - (a.fvm || 0);
            });
        if (teamOopPlayers.length > 0) {
            let oopItemsHtml = '';
            teamOopPlayers.forEach(op => {
                let badgeClass = 'oop-gold';
                let medalLabel = '🥇 ORO';
                if (op.oop_tier === 'ARGENTO') {
                    badgeClass = 'oop-silver';
                    medalLabel = '🥈 ARG';
                } else if (op.oop_tier === 'BRONZO') {
                    badgeClass = 'oop-bronze';
                    medalLabel = '🥉 BRZ';
                }
                const typeBadge = op.role === 'D' 
                    ? '<span style="color:#38bdf8;font-weight:800;font-size:11px;">[D ➜ Quinto]</span>' 
                    : '<span style="color:#fbbf24;font-weight:800;font-size:11px;">[C ➜ Ala/Att]</span>';
                oopItemsHtml += `
                    <div style="display:flex;align-items:center;justify-content:space-between;background:rgba(0,0,0,0.3);padding:6px 10px;border-radius:6px;border-left:3px solid ${op.oop_tier === 'ORO' ? '#fbbf24' : (op.oop_tier === 'ARGENTO' ? '#cbd5e1' : '#f97316')};">
                        <div style="display:flex;align-items:center;gap:6px;">
                            <b style="color:#fff;font-size:12.5px;cursor:pointer;" onclick="openPlayerProfileModal(${op.id})" title="Apri scheda">${op.name}</b>
                            ${op.mantra ? `<span style="font-size:10px;color:var(--text-muted);">${op.mantra}</span>` : ''}
                            ${typeBadge}
                        </div>
                        <span class="oop-tier-badge ${badgeClass}" style="font-size:9.5px;padding:2px 6px;">${medalLabel}</span>
                    </div>
                `;
            });
            oopSectionHtml = `
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:10px 12px;">
                    <div style="font-size:11px;font-weight:800;color:#fbbf24;margin-bottom:7px;display:flex;align-items:center;gap:6px;letter-spacing:0.4px;">
                        👑 CALCIATORI FUORI RUOLO (OOP)
                    </div>
                    <div style="display:flex;flex-direction:column;gap:5px;">
                        ${oopItemsHtml}
                    </div>
                </div>
            `;
        }
        let teamStatsHtml = '';
        const tStat = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[teamName]) ? TEAM_STATS_DB[teamName] : null;
        if (tStat) {
            teamStatsHtml = `
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:10px 12px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-size:10.5px;font-weight:800;color:var(--text-muted);letter-spacing:0.5px;text-transform:uppercase;">⚡ Statistiche Live (3 Giornate)</span>
                        <span style="font-size:10.5px;color:var(--text-secondary);">⚔️ <b style="color:#fbbf24;">${tStat.attacco_label || '-'}</b> • 🛡️ <b style="color:#38bdf8;">${tStat.difesa_label || '-'}</b></span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:6px;text-align:center;">
                        <div style="background:rgba(0,0,0,0.25);padding:6px 4px;border-radius:6px;">
                            <div style="font-size:9px;color:var(--text-muted);font-weight:700;">xG PRODOTTI</div>
                            <div style="font-size:13.5px;font-weight:900;color:#fff;">${tStat.xg_team}</div>
                            <div style="font-size:9px;color:#f472b6;font-weight:700;">#${tStat.xg_team_rank} in A</div>
                        </div>
                        <div style="background:rgba(0,0,0,0.25);padding:6px 4px;border-radius:6px;">
                            <div style="font-size:9px;color:var(--text-muted);font-weight:700;">xGA SUBITI</div>
                            <div style="font-size:13.5px;font-weight:900;color:#fff;">${tStat.xga_team}</div>
                            <div style="font-size:9px;color:#38bdf8;font-weight:700;">#${tStat.xga_team_rank} in A</div>
                        </div>
                        <div style="background:rgba(0,0,0,0.25);padding:6px 4px;border-radius:6px;">
                            <div style="font-size:9px;color:var(--text-muted);font-weight:700;">CLEAN SHEETS</div>
                            <div style="font-size:13.5px;font-weight:900;color:#fff;">${tStat.clean_sheets}</div>
                            <div style="font-size:9px;color:#4ade80;font-weight:700;">#${tStat.clean_sheets_rank} in A</div>
                        </div>
                    </div>
                </div>
            `;
        }
        const col1Html = `
            <div class="tactics-card-col">
                <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <h2 style="margin:0;font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.3px;">${teamName}</h2>
                            <span style="background:rgba(0,242,254,0.12);color:var(--accent-cyan);border:1px solid rgba(0,242,254,0.3);padding:2px 8px;border-radius:20px;font-size:11px;font-weight:800;">${team.modulo}</span>
                        </div>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">All. <span style="color:var(--text-secondary);font-weight:600;">${team.all}</span></div>
                    </div>
                    <div style="display:flex;gap:6px;">
                        <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);padding:3px 7px;border-radius:6px;font-size:11px;color:var(--text-secondary);">🛡️ <b style="color:#fbbf24;">${'★'.repeat(team.dif_stars || 3)}</b></span>
                        <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);padding:3px 7px;border-radius:6px;font-size:11px;color:var(--text-secondary);">⚔️ <b style="color:#fbbf24;">${'★'.repeat(team.att_stars || 3)}</b></span>
                    </div>
                </div>
                ${teamStatsHtml}
                ${oopSectionHtml}
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:10px 12px;display:flex;flex-direction:column;gap:7px;">
                    <div>
                        <div style="font-size:10px;font-weight:800;color:var(--text-muted);margin-bottom:5px;letter-spacing:0.4px;">🎯 RIGORISTI</div>
                        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
                            <span style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.35);color:#4ade80;padding:2px 8px;border-radius:5px;font-size:11.5px;font-weight:800;">1° ${team.rigoristi[0] || '-'}</span>
                            <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);color:var(--text-secondary);padding:2px 8px;border-radius:5px;font-size:11.5px;font-weight:600;">2° ${team.rigoristi[1] || '-'}</span>
                            <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);color:var(--text-muted);padding:2px 8px;border-radius:5px;font-size:11.5px;">3° ${team.rigoristi[2] || '-'}</span>
                        </div>
                    </div>
                    <div style="border-top:1px solid rgba(255,255,255,0.04);padding-top:6px;font-size:11.5px;color:var(--text-secondary);display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
                        <span><b>Punizioni:</b> ${(team.punizioni || []).join(', ') || '-'}</span>
                        <span><b>Corner:</b> ${(team.corner || []).join(', ') || '-'}</span>
                    </div>
                </div>
            </div>
        `;
        let ballottaggiHtml = '';
        if (team.ballottaggi && Array.isArray(team.ballottaggi) && team.ballottaggi.length > 0) {
            const processedPlayers = new Set();
            team.ballottaggi.forEach(b => {
                const p1Name = (b.player || '').trim();
                const p1Pct = Number(b.pct) || 50;
                const vsText = b.vs || '';
                const opponents = [];
                const chunks = vsText.split('/');
                chunks.forEach(chunk => {
                    const match = chunk.match(/(.*?)\s*\((\d+)%\)/);
                    if (match) {
                        opponents.push({
                            name: match[1].trim(),
                            pct: parseInt(match[2], 10)
                        });
                    } else if (chunk.trim()) {
                        opponents.push({
                            name: chunk.trim(),
                            pct: Math.max(0, 100 - p1Pct)
                        });
                    }
                });
                const allContenders = [{ name: p1Name, pct: p1Pct }, ...opponents];
                const alreadyRendered = allContenders.some(c => processedPlayers.has(c.name.toLowerCase()));
                if (alreadyRendered) return;
                allContenders.forEach(c => processedPlayers.add(c.name.toLowerCase()));
                if (allContenders.length === 2) {
                    const [p1, p2] = allContenders;
                    ballottaggiHtml += `
                        <div class="ballottaggio-item">
                            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:4px;min-width:0;">
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:46%;" title="${p1.name}">${p1.name} <span style="font-size:11px;color:#4ade80;font-weight:800;margin-left:2px;">${p1.pct}%</span></span>
                                <span style="font-size:9.5px;color:var(--text-muted);font-weight:700;flex-shrink:0;margin:0 4px;">vs</span>
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:46%;text-align:right;" title="${p2.name}"><span style="font-size:11px;color:#fbbf24;font-weight:800;margin-right:2px;">${p2.pct}%</span> ${p2.name}</span>
                            </div>
                            <div class="ballottaggio-bar-track">
                                <div class="ballottaggio-bar-fill-1" style="width:${p1.pct}%;"></div>
                                <div class="ballottaggio-bar-fill-2" style="width:${p2.pct}%;"></div>
                            </div>
                        </div>
                    `;
                } else if (allContenders.length >= 3) {
                    const [p1, p2, p3] = allContenders;
                    ballottaggiHtml += `
                        <div class="ballottaggio-item">
                            <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;margin-bottom:4px;min-width:0;gap:2px;">
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:32%;" title="${p1.name}">${p1.name} <span style="font-size:10px;color:#4ade80;font-weight:800;">${p1.pct}%</span></span>
                                <span style="font-size:8.5px;color:var(--text-muted);flex-shrink:0;">vs</span>
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:32%;" title="${p2.name}">${p2.name} <span style="font-size:10px;color:#fbbf24;font-weight:800;">${p2.pct}%</span></span>
                                <span style="font-size:8.5px;color:var(--text-muted);flex-shrink:0;">vs</span>
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:32%;text-align:right;" title="${p3.name}">${p3.name} <span style="font-size:10px;color:#38bdf8;font-weight:800;">${p3.pct}%</span></span>
                            </div>
                            <div class="ballottaggio-bar-track">
                                <div class="ballottaggio-bar-fill-1" style="width:${p1.pct}%;"></div>
                                <div class="ballottaggio-bar-fill-2" style="width:${p2.pct}%;"></div>
                                <div class="ballottaggio-bar-fill-3" style="width:${p3.pct}%;"></div>
                            </div>
                        </div>
                    `;
                }
            });
        } else {
            const starters = (team.lineup || []).filter(lp => lp.role !== 'P');
            const bench = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase() && !starters.some(s => s.name.toLowerCase() === p.name.toLowerCase()) && p.role !== 'P');
            const duelsCreated = [];
            starters.forEach(st => {
                const sub = bench.find(b => b.role === st.role && !duelsCreated.some(d => d.p2 === b.name));
                if (sub && duelsCreated.length < 5) {
                    duelsCreated.push({
                        pos: st.pos_label || st.pos,
                        p1: st.name,
                        pct1: 65,
                        p2: sub.name,
                        pct2: 35
                    });
                }
            });
            if (duelsCreated.length > 0) {
                duelsCreated.forEach(d => {
                    ballottaggiHtml += `
                        <div class="ballottaggio-item">
                            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:4px;min-width:0;">
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:46%;" title="${d.p1}">${d.p1} <span style="font-size:11px;color:#4ade80;font-weight:800;margin-left:2px;">${d.pct1}%</span></span>
                                <span style="font-size:9.5px;color:var(--text-muted);font-weight:700;flex-shrink:0;margin:0 4px;">vs</span>
                                <span style="font-weight:700;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:46%;text-align:right;" title="${d.p2}"><span style="font-size:11px;color:#fbbf24;font-weight:800;margin-right:2px;">${d.pct2}%</span> ${d.p2}</span>
                            </div>
                            <div class="ballottaggio-bar-track">
                                <div class="ballottaggio-bar-fill-1" style="width:${d.pct1}%;"></div>
                                <div class="ballottaggio-bar-fill-2" style="width:${d.pct2}%;"></div>
                            </div>
                        </div>
                    `;
                });
            } else {
                ballottaggiHtml = `<div style="font-size:12px;color:var(--text-muted);text-align:center;padding:20px 0;">11 titolare stabile senza ballottaggi aperti.</div>`;
            }
        }
        const col2Html = `
            <div class="tactics-card-col">
                <div class="tactics-card-col-header">
                    <h3 class="tactics-card-col-title">⚖️ I BALLOTTAGGI</h3>
                    <span style="font-size:10.5px;color:var(--text-muted);font-weight:700;">Probabilità di voto</span>
                </div>
                <div style="display:flex;flex-direction:column;gap:8px;">
                    ${ballottaggiHtml}
                </div>
            </div>
        `;
        const topBadges = (team.top || []).map(n => `<span style="background:rgba(236,72,153,0.12);border:1px solid rgba(236,72,153,0.3);color:#f472b6;padding:3px 8px;border-radius:5px;font-size:11.5px;font-weight:800;">👑 ${n}</span>`).join(' ') || '<span style="color:var(--text-muted);font-size:11.5px;">-</span>';
        const sleeperBadges = (team.sleeper || []).map(n => `<span style="background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.3);color:#c084fc;padding:3px 8px;border-radius:5px;font-size:11.5px;font-weight:800;">🚀 ${n}</span>`).join(' ') || '<span style="color:var(--text-muted);font-size:11.5px;">-</span>';
        const flopBadges = (team.flop || []).map(n => `<span style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#f87171;padding:3px 8px;border-radius:5px;font-size:11.5px;font-weight:800;">⚠️ ${n}</span>`).join(' ') || '<span style="color:var(--text-muted);font-size:11.5px;">Nessuno sconsigliato</span>';
        let predAttacco = team.att_stars >= 4 ? "Alta produzione gol grazie al gioco offensivo e ali rientranti." : "Produzione gol media; terminale centrale focalizzatore.";
        let predDifesa = team.dif_stars >= 4 ? "Solidità elevata con ottime probabilità di Clean Sheet e voti positivi." : "Linea da voto regolare; attenzione a qualche malus contro big.";
        let predAsta = `Puntare forte sui Top e sfruttare i giocatori OOP quotati C che giocano attaccanti.`;
        if (teamName === 'Bologna') {
            predAttacco = "Tridente ad alta propensione di bonus con ali molto offensive (Orsolini, Cambiaghi). Potenziale 50-55 gol.";
            predDifesa = "Linea a 4 solida di Tedesco; Theate garanzia di rendimento e modificatore.";
            predAsta = "Priorità assoluta a Orsolini (1° Slot C). Ottima la coppia Piccoli-Dovbyk per chiudere l'attacco.";
        } else if (teamName === 'Atalanta') {
            predAttacco = "Attacco dominante di Sarri con elevato volume di tiri e inserimenti delle mezzali. Potenziale 65-72 gol.";
            predDifesa = "Fase difensiva basata sul possesso; Carnesecchi e Scalvini profili top da modificatore.";
            predAsta = "De Ketelaere e Scamacca priorità; Rowe e Bernasconi sleeper eccellenti a basso costo.";
        } else if (teamName === 'Inter') {
            predAttacco = "Attacco a 2 di Chivu con Lautaro perno assoluto e Dimarco/Calhanoglu costanti distributori di bonus. Potenziale 75-80 gol.";
            predDifesa = "Difesa a 3 dominante in Serie A; Bastoni e Stones top assoluti da modificatore di difesa.";
            predAsta = "Lautaro e Calhanoglu prime scelte d'asta; Sucic ed Esposito ottime scommesse a basso prezzo.";
        } else if (teamName === 'Cagliari') {
            predAttacco = "Albero di Natale di Pisacane con Maldini e Fazzini rifinitori dietro la punta. Potenziale 38-44 gol.";
            predDifesa = "Caprile portiere affidabile da voto alto; Mina guida la linea per solidità casalinga.";
            predAsta = "Maldini (rigorista e leader) obiettivo principale; Fazzini e Kevin Carlos sleeper a pochi crediti.";
        } else if (teamName === 'Como') {
            predAttacco = "Attacco stellare di Fabregas con Nico Paz faro assoluto, Baturina e Kean finalizzatori. Potenziale 68-75 gol.";
            predDifesa = "Linea alta e propositiva; Couto garanzia di bonus, Ramon e Chalobah affidabili.";
            predAsta = "Nico Paz Top 1 assoluto C (1° Slot d'oro); Kean/Douvikas ottimi 2° Slot A; Couto tra i migliori D.";
        } else if (teamName === 'Fiorentina') {
            predAttacco = "Tridente dinamico di Grosso con Mastantuono e Goncalves ali d'alta qualità e Pellegrino/Beto centravanti. Potenziale 58-64 gol.";
            predDifesa = "De Gea leader esperto, Dragusin perno da modificatore.";
            predAsta = "Mastantuono (C rigorista) e Atta priorità; prendere la coppia Pellegrino-Beto per il centravanti titolare.";
        } else if (teamName === 'Frosinone') {
            predAttacco = "Sistema a trazione anteriore di Alvini: Raimondo perno centrale con Kvernadze e Schmid rifinitori. Potenziale 35-40 gol.";
            predDifesa = "Palmisani e Monterisi punti di riferimento; Bracaglia e Calvani giovani da voto regolare.";
            predAsta = "Calò (rigorista e piazzati) e Raimondo ottimi 4°-5° slot; Schmid scommessa low-cost.";
        } else if (teamName === 'Genoa') {
            predAttacco = "3-4-2-1 fluido di De Rossi con Baldanzi e Vitinha ad inventare dietro a Colombo. Potenziale 45-50 gol.";
            predDifesa = "Difesa rocciosa guidata da Ostigard e Vasquez; Drameh quinto a tutta fascia da bonus.";
            predAsta = "Baldanzi (rigorista) e Drameh (D da bonus) priorità; Colombo 3° slot A ideale.";
        } else if (teamName === 'Juventus') {
            predAttacco = "Attacco a 4 di Spalletti ad alta fluidità: Conceicao e Boga ali d'assalto, Kolo Muani finalizzatore. Potenziale 70-75 gol.";
            predDifesa = "Muro invalicabile guidato da Bremer e Vicario; Kalulu e Lucumì affidabili per il modificatore.";
            predAsta = "Kolo Muani (1° Slot A) e Bremer (Top 1 D) priorità; Conceicao ottimo 2° slot C e Woltemade da abbinare a Kolo Muani.";
        } else if (teamName === 'Lazio') {
            predAttacco = "Tridente aggressivo di Gattuso: Zaccagni e Gudmundsson rifinitori di lusso per Pinamonti. Potenziale 60-65 gol.";
            predDifesa = "Mandas e Sutalo pilastri difensivi; Tavares terzino ad alto potenziale di assist.";
            predAsta = "Zaccagni (1° Slot C & rigorista) e Frattesi (mezzala da bonus) obiettivi caldi; Tavares top di spesa in D.";
        } else if (teamName === 'Lecce') {
            predAttacco = "4-2-3-1 propositivo di Di Francesco: Pierotti e N'Dri ali di velocità a supporto di Stulic/Geubbels. Potenziale 38-42 gol.";
            predDifesa = "Falcone garanzia di voti alti e rigori parati; Tiago Gabriel e Gaspar coppia fisica.";
            predAsta = "Falcone ottimo portiere low-cost; Pierotti (C) e Stulic/Geubbels scommesse economiche da ultimi slot.";
        } else if (teamName === 'Milan') {
            predAttacco = "3-4-2-1 esplosivo di Ruben Amorim: Pulisic e Ramos G. terminali di livello europeo con Modric e Rabiot registi. Potenziale 78-84 gol.";
            predDifesa = "Linea a 3 fisica con Pavlovic e Gabbia; Maignan garanzia di clean sheet.";
            predAsta = "Pulisic (Top 1 C & rigorista) e Ramos G. (1° Slot A) prime scelte assolute; Chukwueze e Bartesaghi ottimi a tutta fascia.";
        } else if (teamName === 'Monza') {
            predAttacco = "3-4-2-1 aggressivo di Juric: Colpani e Ngonge rifinitori dietro a Varela. Potenziale 38-44 gol.";
            predDifesa = "Marcatura a uomo a tutto campo con Lucchesi e Ziolkowski; Birindelli e Mangas esterni fisici.";
            predAsta = "Colpani (rigorista e leader) e Varela target principali; Birindelli ottimo per completare la difesa.";
        } else if (teamName === 'Napoli') {
            predAttacco = "Tridente letale di Allegri con Hojlund finalizzatore seriale, McTominay e De Bruyne distributori di qualità. Potenziale 74-80 gol.";
            predDifesa = "Rrahmani e Badiashile coppia solida da clean sheet; Di Lorenzo certezza assoluta.";
            predAsta = "Hojlund (1° Slot A) e McTominay (Top 1 C da gol) imperdibili; Politano e De Bruyne ottimi investimenti.";
        } else if (teamName === 'Parma') {
            predAttacco = "4-3-2-1 ad albero di Natale di Cuesta con Bernabè e Fabbian incursori dietro alle punte. Potenziale 40-46 gol.";
            predDifesa = "Diego Carlos guida la retroguardia; Valeri garanzia di cross e spinta mancina.";
            predAsta = "Bernabè (rigorista e leader) 2° slot C top; Diego Carlos e Valeri tra i migliori difensori low-cost.";
        } else if (teamName === 'Roma') {
            predAttacco = "Calcio totale e ultra-offensivo di Gasperini: Malen macchina da gol, Dybala rifinitore sublime e Soulè/Mora pronti a colpire. Potenziale 80-88 gol.";
            predDifesa = "Linea a 3 aggressiva e quinto di fascia ultra-propositivo con Molina e Wesley; Svilar top tra i pali.";
            predAsta = "Malen (Top 1 A assoluto FVM 450) e Dybala prime scelte assolute; Molina e Wesley da svenarsi all'asta come D.";
        } else if (teamName === 'Sassuolo') {
            predAttacco = "Tridente spettacolare di Aquilani con Berardi e Laurientè sugli esterni a supporto di Bowie. Potenziale 52-58 gol.";
            predDifesa = "Linea a 4 organizzata con Idzes e Leysen; Doig terzino da bonus continuo.";
            predAsta = "Berardi (rigorista e stella) e Laurientè top per l'attacco; Thorstvedt e Doig acquisti d'oro.";
        } else if (teamName === 'Torino') {
            predAttacco = "3-4-2-1 di Abate con Simeone centravanti di movimento e Vlasic/Casadei incursori. Potenziale 44-50 gol.";
            predDifesa = "Linea a 3 fisica con Coco e Comuzzo; Perri portiere giovane ed affidabile.";
            predAsta = "Simeone (1° Rigorista) e Vlasic (C) certezze d'asta; Casadei e Belghali sleeper a poco prezzo.";
        } else if (teamName === 'Udinese') {
            predAttacco = "Attacco dinamico di Runjaic: Davis centravanti di peso e Zaniolo (C) seconda punta d'alta qualità. Potenziale 48-54 gol.";
            predDifesa = "Muro fisico con Solet leader difensivo; Kamara e Vojvoda costanti rifinitori sui binari.";
            predAsta = "Zaniolo (Top C da schierare in attacco) e Davis K. priorità assolute; Solet e Kamara ottimi in D.";
        } else if (teamName === 'Venezia') {
            predAttacco = "3-5-2 di Stroppa con Adams A. e Yeboah tandem offensivo supportati dagli inserimenti di Busio e Basic. Potenziale 36-42 gol.";
            predDifesa = "Bella-Kotchap guida il terzetto arretrato; Stankovic portiere da molti interventi salva-risultato.";
            predAsta = "Basic (rigorista e piazzati) e Busio ottimi per la mediana; Mazzocchi e Yeboah scommesse a 1 credito.";
        }
        const col3Html = `
            <div class="tactics-card-col">
                <div class="tactics-card-col-header">
                    <h3 class="tactics-card-col-title">🤖 CONSIGLI AI & PREVISIONI</h3>
                    <span style="font-size:10.5px;color:var(--accent-cyan);font-weight:800;background:rgba(0,242,254,0.1);padding:1px 6px;border-radius:4px;border:1px solid rgba(0,242,254,0.25);">2026/27</span>
                </div>
                <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);padding:10px 12px;border-radius:10px;display:flex;flex-direction:column;gap:7px;">
                    <div>
                        <div style="font-size:10px;font-weight:800;color:var(--text-muted);margin-bottom:4px;letter-spacing:0.4px;">TARGET TOP ASTA</div>
                        <div style="display:flex;flex-wrap:wrap;gap:4px;">${topBadges}</div>
                    </div>
                    <div>
                        <div style="font-size:10px;font-weight:800;color:var(--text-muted);margin-bottom:4px;letter-spacing:0.4px;">SLEEPER & VALUE</div>
                        <div style="display:flex;flex-wrap:wrap;gap:4px;">${sleeperBadges}</div>
                    </div>
                    <div>
                        <div style="font-size:10px;font-weight:800;color:var(--text-muted);margin-bottom:4px;letter-spacing:0.4px;">RISCHIO FLOP</div>
                        <div style="display:flex;flex-wrap:wrap;gap:4px;">${flopBadges}</div>
                    </div>
                </div>
                <div style="background:rgba(0,242,254,0.03);border:1px solid rgba(0,242,254,0.18);padding:11px 13px;border-radius:10px;display:flex;flex-direction:column;gap:7px;">
                    <div style="font-size:11px;font-weight:800;color:var(--accent-cyan);display:flex;align-items:center;gap:5px;letter-spacing:0.3px;">
                        🔮 PREVISIONI PREDITTIVE
                    </div>
                    <div style="font-size:12px;color:var(--text-secondary);line-height:1.4;">
                        ⚽ <b>Attacco:</b> ${predAttacco}
                    </div>
                    <div style="font-size:12px;color:var(--text-secondary);line-height:1.4;">
                        🛡️ <b>Difesa:</b> ${predDifesa}
                    </div>
                    <div style="font-size:12px;color:#4ade80;line-height:1.4;margin-top:2px;border-top:1px solid rgba(255,255,255,0.06);padding-top:6px;">
                        💡 <b>Strategia Budget:</b> ${predAsta}
                    </div>
                </div>
            </div>
        `;
        dashboardEl.innerHTML = col1Html + col2Html + col3Html;
    }
    renderTeamRosterTable(teamName);
}
window.pitchRosterFilters = window.pitchRosterFilters || { role: 'ALL', search: '' };
function setPitchRosterRoleFilter(role) {
    window.pitchRosterFilters.role = role;
    renderTeamRosterTable(State.currentTeamPitch);
}
function onPitchRosterSearch(query) {
    window.pitchRosterFilters.search = (query || '').trim().toLowerCase();
    renderTeamRosterTable(State.currentTeamPitch);
}
function renderTeamRosterTable(teamName) {
    const container = document.getElementById('teamRosterTableContainer');
    if (!container) return;
    const allTeamPlayers = PLAYERS.filter(p => (p.team || '').trim().toLowerCase() === (teamName || '').trim().toLowerCase())
        .sort((a, b) => {
            const roleOrder = { 'P': 1, 'D': 2, 'C': 3, 'A': 4 };
            if (roleOrder[a.role] !== roleOrder[b.role]) return roleOrder[a.role] - roleOrder[b.role];
            return b.ovr - a.ovr;
        });
    const pCount = allTeamPlayers.filter(p => p.role === 'P').length;
    const dCount = allTeamPlayers.filter(p => p.role === 'D').length;
    const cCount = allTeamPlayers.filter(p => p.role === 'C').length;
    const aCount = allTeamPlayers.filter(p => p.role === 'A').length;
    const avgOvr = allTeamPlayers.length > 0 ? (allTeamPlayers.reduce((s, p) => s + (p.ovr || 0), 0) / allTeamPlayers.length).toFixed(1) : '-';
    const totalVal = allTeamPlayers.reduce((s, p) => s + (p.prezzo_cons || 0), 0);
    const activeRole = window.pitchRosterFilters.role || 'ALL';
    const searchQuery = window.pitchRosterFilters.search || '';
    const filteredPlayers = allTeamPlayers.filter(p => {
        if (activeRole !== 'ALL' && p.role !== activeRole) return false;
        if (searchQuery && !p.name.toLowerCase().includes(searchQuery) && !(p.mantra || '').toLowerCase().includes(searchQuery)) return false;
        return true;
    });
    let rowsHtml = '';
    filteredPlayers.forEach(p => {
        const isBought = isPlayerBought(p.id);
        const isTaken = isPlayerTakenByOther(p.id);
        const isFav = typeof isPlayerFavorite === 'function' ? isPlayerFavorite(p.id) : (State.favorites && State.favorites.includes(p.id));
        const trClass = isBought ? 'bought-row' : (isTaken ? 'taken-row' : '');
        const slotClass = p.slot_num === 1 ? 'slot-1' : (p.slot_num === 2 ? 'slot-2' : (p.slot_num === 3 ? 'slot-3' : 'slot-other'));
        const topOvrClass = getOvrClass(p.ovr);
        const fragIcon = p.fragilita_badge === 'alta' ? '🔴' : (p.fragilita_badge === 'media' ? '🟡' : '🟢');
        const fragilitaHtml = `<span class="fragilita-dot" title="Fragilità: ${p.fragilita_val || ''} | ${p.fragilita_dettaglio || ''}" style="cursor:help;font-size:14px;">${fragIcon}</span>`;
        let oopHtml = `<span style="color:var(--text-muted);font-size:11px;">-</span>`;
        if (p.oop_val && p.oop_val !== '-') {
            let badgeClass = 'oop-gold';
            if (p.oop_tier === 'ARGENTO' || (p.oop_val && p.oop_val.includes('ARGENTO'))) badgeClass = 'oop-silver';
            else if (p.oop_tier === 'BRONZO' || (p.oop_val && p.oop_val.includes('BRONZO'))) badgeClass = 'oop-bronze';
            oopHtml = `<span class="oop-tier-badge ${badgeClass}" title="${p.oop_desc || p.oop_val}">${p.oop_val}</span>`;
        }
        const rigHtml = (p.rigorista_val && p.rigorista_val !== '-') ? `<span style="color:#fbbf24;font-weight:700;">${p.rigorista_val}</span>` : '-';
        let col1Html = `<span style="color:var(--text-muted);font-size:11px;">-</span>`;
        let col2Html = `<span style="color:var(--text-muted);font-size:11px;">-</span>`;
        let col3Html = `<span style="color:var(--text-muted);font-size:11px;">-</span>`;
        let ratingHtml = `<span style="color:var(--text-muted);font-size:11px;">-</span>`;
        let minsHtml = `<span style="color:var(--text-muted);font-size:11px;">-</span>`;
        if (p.has_data_2526) {
            ratingHtml = p.rating_2526 ? `<span class="ovr-pill ${p.rating_2526 >= 7.0 ? 'top-tier' : ''}">${p.rating_2526}</span>` : '-';
            minsHtml = p.mins_2526 ? `${p.mins_2526}'` : '-';
            if (p.role === 'P') {
                const gp = p.goals_prevented_2526;
                col1Html = (gp !== null && gp !== undefined && gp !== 0) ? 
                    (gp > 0 ? `<b style="color:#4ade80;" title="Gol Evitati / Salvati">+${gp} Salvati</b>` : `<span style="color:#f87171;" title="Gol Evitati">${gp}</span>`) : 
                    `<span style="color:var(--text-muted);">-</span>`;
                col2Html = (p.clean_sheets_2526 !== null && p.clean_sheets_2526 !== undefined && p.clean_sheets_2526 > 0) ? 
                    `<b style="color:#38bdf8;" title="Clean Sheets (Porta Inviolata)">${p.clean_sheets_2526} CS</b>` : 
                    `<span style="color:var(--text-muted);">-</span>`;
                col3Html = (p.save_pct_2526 && p.save_pct_2526 > 0) ? 
                    `<b style="color:#fbbf24;" title="% Parate Effettuate">${p.save_pct_2526}%</b>` : 
                    `<span style="color:var(--text-muted);">-</span>`;
            } else {
                col1Html = p.xg90_2526 > 0 ? `<b style="color:#f472b6;" title="Expected Goals ogni 90 min">${p.xg90_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
                col2Html = p.xgot_2526 > 0 ? `<b style="color:#fbbf24;" title="Expected Goals on Target (Qualità Conclusione)">${p.xgot_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
                col3Html = p.xa90_2526 > 0 ? `<b style="color:#38bdf8;" title="Expected Assists ogni 90 min">${p.xa90_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
            }
        } else {
            ratingHtml = `<span style="font-size:10px;color:#a78bfa;background:rgba(139,92,246,0.15);padding:2px 5px;border-radius:4px;">Nuovo 26/27</span>`;
        }
        let ga2627Html = `<span style="color:var(--text-muted);font-size:11px;">0 / 0</span>`;
        if (p.role === 'P') {
            if (p.has_data_2627 && p.presenze_2627 > 0) {
                ga2627Html = `<span style="color:#f87171;font-weight:700;">${p.gol_subiti_2627 || 0}</span> <small style="color:#38bdf8;">(${p.clean_sheets_2627 || 0} CS)</small>`;
            } else {
                ga2627Html = `<span style="color:var(--text-muted);font-size:11px;">0</span>`;
            }
        } else {
            if (p.has_data_2627 && p.presenze_2627 > 0) {
                const gText = p.gol_2627 > 0 ? `<b style="color:#fbbf24;font-size:12.5px;">${p.gol_2627}</b>` : `<span style="color:var(--text-muted);">0</span>`;
                const aText = p.assist_2627 > 0 ? `<b style="color:#38bdf8;font-size:12.5px;">${p.assist_2627}</b>` : `<span style="color:var(--text-muted);">0</span>`;
                ga2627Html = `${gText} / ${aText}`;
            } else {
                ga2627Html = `<span style="color:var(--text-muted);font-size:11px;">0 / 0</span>`;
            }
        }
        let titColor = '#94a3b8';
        let titBg = 'rgba(148,163,184,0.1)';
        let titBorder = 'rgba(148,163,184,0.2)';
        if (p.titolarita >= 85) {
            titColor = '#4ade80';
            titBg = 'rgba(34,197,94,0.15)';
            titBorder = 'rgba(34,197,94,0.35)';
        } else if (p.titolarita >= 68) {
            titColor = '#facc15';
            titBg = 'rgba(234,179,8,0.15)';
            titBorder = 'rgba(234,179,8,0.35)';
        }
        const titDesc = p.titolarita_desc_2627 && p.titolarita_desc_2627 !== '0 Presenze' ? `<div style="font-size:9.5px;color:var(--text-muted);margin-top:1px;">${p.titolarita_desc_2627}</div>` : '';
        const titHtml = `<div style="display:flex;flex-direction:column;align-items:center;">
            <span style="display:inline-block;padding:2px 6px;border-radius:5px;font-size:11px;font-weight:800;color:${titColor};background:${titBg};border:1px solid ${titBorder};">${p.titolarita || 0}%</span>
            ${titDesc}
        </div>`;
        let actionCellHtml = '';
        if (isBought) {
            actionCellHtml = `<span style="color:#4ade80;font-weight:800;font-size:11px;">✓ MIA ROSA</span>`;
        } else if (isTaken) {
            actionCellHtml = `
                <div style="display:flex;align-items:center;gap:4px;">
                    <span style="color:#ef4444;font-weight:800;font-size:10.5px;">⛔ ALTRI</span>
                    <button class="roster-del-btn" title="Annulla e rendi di nuovo disponibile" onclick="unmarkPlayerTaken(${p.id}); renderTeamRosterTable('${teamName}');">↩️</button>
                </div>
            `;
        } else {
            actionCellHtml = `
                <div style="display:flex;align-items:center;gap:4px;">
                    <button class="btn-action" style="padding:4px 7px;font-size:11px;background:rgba(0,242,254,0.15);border-color:var(--accent-cyan);" onclick="buyPlayer(${p.id}); renderTeamRosterTable('${teamName}');" title="Compra per la tua rosa">+ Compra</button>
                    <button class="btn-action" style="padding:4px 6px;font-size:10px;background:rgba(239,68,68,0.15);border-color:rgba(239,68,68,0.4);color:#ef4444;" title="Assegna a squadra rivale" onclick="openRivalAssignModal(${p.id})">⛔</button>
                </div>
            `;
        }
        let injBadge = '';
        if (p.is_injured) {
            const isOrange = (p.infortunio_severity === 'orange');
            const colorHex = isOrange ? '#f59e0b' : '#ef4444';
            const classBadge = isOrange ? 'inj-cross-badge orange' : 'inj-cross-badge red';
            const statusTitle = isOrange ? 'PROSSIMO AL RIENTRO' : 'LUNGA DEGENZA';
            injBadge = `<span class="${classBadge}" title="${statusTitle}&#10;Motivo: ${p.infortunio_motivo || 'Indisponibile'}&#10;Rientro previsto: ${p.infortunio_rientro || 'TBD'}"><svg viewBox="0 0 24 24" width="12" height="12" fill="${colorHex}" style="vertical-align:middle;"><path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6V3z"/></svg></span>`;
        }
        const rosterRoleBadge = (typeof State !== 'undefined' && State.systemMode === 'mantra')
            ? renderMantraRoleBadges(p.mantra)
            : `<span class="role-badge ${p.role}">${p.role}</span>`;
        rowsHtml += `
            <tr class="${trClass}">
                <td style="min-width:38px;text-align:center;">${rosterRoleBadge}</td>
                <td style="min-width:240px;max-width:340px;text-align:left;">
                    <div style="display:flex;align-items:center;gap:6px;flex-wrap:nowrap;">
                        <button onclick="openEditPlayerModal(${p.id})" title="Personalizza Slot, OOP e Consiglio AI (Solo Admin)" class="creator-only-control" style="background:none;border:none;cursor:pointer;font-size:13px;padding:0 2px;opacity:0.85;transition:transform 0.15s ease;" onmouseover="this.style.transform='scale(1.25)'" onmouseout="this.style.transform='scale(1)'">✏️</button>
                        <button onclick="toggleFavorite(${p.id}); renderTeamRosterTable('${teamName}');" title="${isFav ? 'Rimuovi dai Preferiti' : 'Aggiungi ai Preferiti'}" style="background:none;border:none;cursor:pointer;font-size:13px;padding:0 2px;opacity:${isFav ? '1' : '0.4'};transition:transform 0.15s ease;" onmouseover="this.style.transform='scale(1.25)'" onmouseout="this.style.transform='scale(1)'">${isFav ? '⭐' : '☆'}</button>
                        <b style="color:#fff;font-size:13px;cursor:pointer;text-decoration:underline;text-decoration-color:rgba(0,242,254,0.4);white-space:nowrap;" onclick="openPlayerProfileModal(${p.id})" title="Apri Scheda Calciatore: ${p.name}">${p.name}</b>
                        ${injBadge}
                        ${(p.mantra && (typeof State === 'undefined' || State.systemMode === 'classic')) ? `<span style="font-size:10.5px;color:var(--text-muted);background:rgba(255,255,255,0.06);padding:1px 5px;border-radius:3px;margin-left:2px;">${p.mantra}</span>` : ''}
                        ${p.is_custom_edited ? `<span style="font-size:9px;background:rgba(139,92,246,0.25);color:#c084fc;padding:1px 4px;border-radius:3px;border:1px solid rgba(139,92,246,0.4);" title="Calciatore personalizzato">Modificato</span>` : ''}
                    </div>
                </td>
                <td style="width:52px;text-align:center;"><span class="ovr-pill ${topOvrClass}">${p.ovr}</span></td>
                <td style="text-align:center;">${titHtml}</td>
                <td style="text-align:center;"><span class="price-pill">${p.prezzo_cons} CR</span></td>
                <td style="text-align:center;"><span style="color:var(--text-muted);">${p.max_bid} CR</span></td>
                <td style="text-align:center;"><span class="slot-pill-badge ${slotClass}">${p.slot_fascia}</span></td>
                <td style="text-align:center;">${fragilitaHtml}</td>
                <td style="text-align:center;">${oopHtml}</td>
                <td style="text-align:center;">${rigHtml}</td>
                <td style="text-align:center;"><span class="ai-advice-badge ${p.ai_advice_type || 'regular'}">${p.ai_advice || p.consiglio}</span></td>
                <td style="text-align:center;">${ratingHtml}</td>
                <td style="text-align:center;">${col1Html}</td>
                <td style="text-align:center;">${col2Html}</td>
                <td style="text-align:center;">${col3Html}</td>
                <td style="text-align:center;"><b>${p.fm > 0 ? p.fm : '-'}</b></td>
                <td style="text-align:center;">${ga2627Html}</td>
                <td style="text-align:center;font-size:11.5px;color:var(--text-secondary);">${minsHtml}</td>
                <td style="text-align:center;">${actionCellHtml}</td>
            </tr>
        `;
    });
    if (filteredPlayers.length === 0) {
        rowsHtml = `<tr><td colspan="19" style="text-align:center;padding:24px;color:var(--text-muted);">Nessun calciatore trovato con i filtri selezionati.</td></tr>`;
    }
    container.innerHTML = `
        <div class="team-roster-section" style="margin-top:24px;">
            <!-- Barra di Riepilogo e Controlli Avanzati della Rosa -->
            <div class="team-roster-summary-bar">
                <div class="team-roster-summary-top">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:24px;">📋</span>
                        <div>
                            <h3 style="margin:0;font-size:17px;font-weight:800;color:var(--accent-cyan);letter-spacing:0.3px;">Tutta la Rosa del Club: ${teamName} (${allTeamPlayers.length} Calciatori)</h3>
                            <p style="margin:2px 0 0 0;font-size:12px;color:var(--text-secondary);">Statistiche avanzate, titolarità, quotazioni 26/27, e modifica rapida Slot / OOP / Consiglio AI</p>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <button class="btn-action creator-only-control" style="font-size:11px;background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.35);color:#f87171;" onclick="resetTeamOverrides('${teamName}')" title="Ripristina valori predefiniti per tutti i calciatori di questa squadra">🔄 Reset Modifiche</button>
                        <div class="creator-only-block" style="font-size:11.5px;color:var(--text-muted);">
                            💡 Clicca su <b>✏️</b> per modificare o su <b>Nome</b> per la scheda completa.
                        </div>
                        <div class="visitor-only-item" style="font-size:11.5px;color:var(--text-muted);">
                            💡 Clicca sul <b>Nome</b> per aprire la scheda completa del calciatore.
                        </div>
                    </div>
                </div>
                <div class="team-roster-metrics">
                    <span class="team-roster-metric-chip">⭐ OVR Medio: <b>${avgOvr}</b></span>
                    <span class="team-roster-metric-chip">💰 Valore Rosa: <b>${totalVal} CR</b></span>
                    <span class="team-roster-metric-chip">🧤 Portieri: <b>${pCount}</b></span>
                    <span class="team-roster-metric-chip">🛡️ Difensori: <b>${dCount}</b></span>
                    <span class="team-roster-metric-chip">⚙️ Centrocampisti: <b>${cCount}</b></span>
                    <span class="team-roster-metric-chip">🎯 Attaccanti: <b>${aCount}</b></span>
                </div>
                <div class="team-roster-controls-bottom">
                    <div class="roster-role-pills">
                        <span style="font-size:11px;font-weight:800;color:var(--text-muted);margin-right:4px;">FILTRA RUOLO:</span>
                        <button class="roster-filter-btn ${activeRole === 'ALL' ? 'active' : ''}" onclick="setPitchRosterRoleFilter('ALL')">Tutti (${allTeamPlayers.length})</button>
                        <button class="roster-filter-btn ${activeRole === 'P' ? 'active' : ''}" onclick="setPitchRosterRoleFilter('P')">P (${pCount})</button>
                        <button class="roster-filter-btn ${activeRole === 'D' ? 'active' : ''}" onclick="setPitchRosterRoleFilter('D')">D (${dCount})</button>
                        <button class="roster-filter-btn ${activeRole === 'C' ? 'active' : ''}" onclick="setPitchRosterRoleFilter('C')">C (${cCount})</button>
                        <button class="roster-filter-btn ${activeRole === 'A' ? 'active' : ''}" onclick="setPitchRosterRoleFilter('A')">A (${aCount})</button>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <input type="text" placeholder="🔍 Cerca calciatore o mantra..." value="${searchQuery}" oninput="onPitchRosterSearch(this.value)" style="background:rgba(0,0,0,0.45);border:1px solid rgba(255,255,255,0.18);color:#fff;padding:5px 11px;border-radius:6px;font-size:12px;outline:none;width:220px;" />
                        ${searchQuery ? `<button class="btn-action" style="padding:4px 8px;font-size:11px;" onclick="onPitchRosterSearch('')">✕</button>` : ''}
                    </div>
                </div>
            </div>
            <div class="table-wrapper">
                <table class="fanta-table team-roster-table">
                    <thead>
                        <tr>
                            <th style="width:38px;text-align:center;">R</th>
                            <th style="min-width:240px;text-align:left;">Calciatore</th>
                            <th style="width:52px;text-align:center;">OVR</th>
                            <th style="min-width:90px;text-align:center;" title="Percentuale di Titolarità Calcolata e Status 2026/27">Titolarità</th>
                            <th style="min-width:75px;text-align:center;">Prezzo Cons.</th>
                            <th style="min-width:75px;text-align:center;">Max Bid</th>
                            <th style="min-width:95px;text-align:center;">Slot</th>
                            <th style="width:50px;text-align:center;" title="Livello di Fragilità Fisica">Frag.</th>
                            <th style="min-width:110px;text-align:center;">OOP</th>
                            <th style="min-width:65px;text-align:center;">Rigori</th>
                            <th style="min-width:140px;text-align:center;">Consiglio AI</th>
                            <th style="min-width:75px;text-align:center;" title="Rating Statistico 25/26">⭐ Rating 25/26</th>
                            <th style="min-width:90px;text-align:center;" title="xG ogni 90 min o Gol Evitati">xG90 / G.Salvati</th>
                            <th style="min-width:75px;text-align:center;" title="Expected Goals on Target o Clean Sheets">xGOT / CS</th>
                            <th style="min-width:85px;text-align:center;" title="Expected Assists o % Parate">xA90 / % Parate</th>
                            <th style="min-width:65px;text-align:center;" title="Fantamedia 25/26">FM 25/26</th>
                            <th style="min-width:80px;text-align:center;" title="Gol e Assist Reali Stagione 2026/2027 (3 Giornate)">⚽ G / A (26/27)</th>
                            <th style="min-width:75px;text-align:center;">Minuti 25/26</th>
                            <th style="min-width:130px;text-align:center;">Azione</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}
function onAdvicePresetChange(val) {
    const customInp = document.getElementById('editPlayerAdviceCustom');
    if (customInp) {
        if (val === 'CUSTOM') {
            customInp.style.display = 'block';
            customInp.focus();
        } else {
            customInp.style.display = 'none';
            customInp.value = val;
        }
    }
}
function openEditPlayerModal(playerId) {
    if (typeof isCreatorModeActive === 'function' && !isCreatorModeActive()) {
        alert("🔒 Questa funzione di modifica parametri è riservata esclusivamente all'amministratore del sito.");
        return;
    }
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;
    const modal = document.getElementById('editPlayerModal');
    const body = document.getElementById('editPlayerModalBody');
    if (!modal || !body) return;
    const isCustom = !!p.is_custom_edited;
    const slotOptions = [
        '1° Slot (Top Assoluto)',
        '2° Slot (Semi-Top / Titolare di Lusso)',
        '3° Slot (Ottimo Titolare)',
        '4° Slot (Titolare / Copertura)',
        '5° Slot (Scommessa / Alternativa)',
        '6° Slot (Low Cost)',
        '7° Slot (Tappabuchi / Slot 1 Credito)',
        '8° Slot (Ultimo Slot 1 Credito)'
    ];
    const oopOptions = [
        { label: 'Nessuno (-)', val: '-' },
        { label: '⭐ Quinto (D ➜ C)', val: '⚡ Quinto' },
        { label: '⭐ Ala / Trequartista (C ➜ A)', val: '⭐ Ala/Trequartista' },
        { label: '⭐ Avanzato / Seconda Punta', val: '⭐ Avanzato' },
        { label: '⚠️ Arretrato (FPN)', val: '⚠️ Arretrato' }
    ];
    const adviceOptions = [
        { label: '👑 Top Player Assoluto', val: 'Top Player Assoluto', type: 'top' },
        { label: '⭐ Leader di Squadra', val: 'Leader di Squadra', type: 'leader' },
        { label: '🚀 Best Value / Da Acquistare', val: 'Best Value / Da Acquistare', type: 'buy' },
        { label: '🔒 Titolarissimo da Voto', val: 'Titolarissimo da Voto', type: 'titolarissimo' },
        { label: '🔄 Rotazione / Ballottaggio', val: 'Rotazione', type: 'rotation' },
        { label: '🔥 Scommessa / Sleeper', val: 'Scommessa / Sleeper', type: 'sleeper' },
        { label: '🛡️ Low Cost Modificatore', val: 'Low Cost Modificatore', type: 'lowcost' },
        { label: '⚠️ Possibile Flop / Fragile', val: 'Possibile Flop / Fragile', type: 'flop' },
        { label: '⛔ Da Evitare', val: 'Da Evitare', type: 'avoid' }
    ];
    const isCustomAdvice = !adviceOptions.some(a => a.val === (p.ai_advice || p.consiglio));
    body.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:16px;">
            <!-- Player Info Header -->
            <div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.03);border:1px solid var(--border-glass);padding:12px 16px;border-radius:10px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span class="role-badge ${p.role}" style="font-size:13px;width:26px;height:26px;">${p.role}</span>
                    <div>
                        <div style="font-size:16px;font-weight:800;color:#fff;">${p.name} <span style="font-size:12px;color:var(--text-muted);font-weight:400;">(${p.mantra || ''})</span></div>
                        <div style="font-size:12px;color:var(--text-secondary);">${p.team} &nbsp;•&nbsp; OVR: <b style="color:var(--accent-cyan);">${p.ovr}</b> &nbsp;•&nbsp; Prezzo Cons.: <b style="color:var(--accent-gold);">${p.prezzo_cons} CR</b> &nbsp;•&nbsp; Titolarità: <b style="color:#4ade80;">${p.titolarita}%</b></div>
                    </div>
                </div>
                ${isCustom ? `<span style="font-size:11px;background:rgba(139,92,246,0.2);color:#c084fc;padding:3px 8px;border-radius:6px;border:1px solid rgba(139,92,246,0.4);font-weight:700;">✏️ Personalizzato</span>` : ''}
            </div>
            <!-- Field 1: Slot / Fascia -->
            <div style="display:flex;flex-direction:column;gap:6px;">
                <label style="font-size:12px;font-weight:800;color:var(--accent-cyan);display:flex;align-items:center;gap:6px;">
                    🎯 SLOT / FASCIA ASTA:
                </label>
                <select id="editPlayerSlot" class="select-filter" style="width:100%;background:rgba(0,0,0,0.4);border-color:rgba(0,242,254,0.35);">
                    ${slotOptions.map(s => `<option value="${s}" ${p.slot_fascia.startsWith(s.split(' ')[0]) || p.slot_fascia === s ? 'selected' : ''}>${s}</option>`).join('')}
                </select>
                <div style="font-size:11px;color:var(--text-muted);">Assegna a quale slot d'asta appartiene il calciatore (1° Slot, 2° Slot, ecc.).</div>
            </div>
            <!-- Field 2: OOP (Fuori Ruolo) -->
            <div style="display:flex;flex-direction:column;gap:6px;">
                <label style="font-size:12px;font-weight:800;color:#ec4899;display:flex;align-items:center;gap:6px;">
                    ⚡ FUORI RUOLO (OOP / FPP):
                </label>
                <select id="editPlayerOop" class="select-filter" style="width:100%;background:rgba(0,0,0,0.4);border-color:rgba(236,72,153,0.35);">
                    ${oopOptions.map(o => `<option value="${o.val}" ${p.oop_val === o.val ? 'selected' : ''}>${o.label}</option>`).join('')}
                </select>
                <div style="font-size:11px;color:var(--text-muted);">Indica se il giocatore gioca in una posizione più avanzata rispetto alla quotazione listone.</div>
            </div>
            <!-- Field 3: Consiglio AI -->
            <div style="display:flex;flex-direction:column;gap:6px;">
                <label style="font-size:12px;font-weight:800;color:var(--accent-gold);display:flex;align-items:center;gap:6px;">
                    💡 CONSIGLIO STRATEGICO AI:
                </label>
                <select id="editPlayerAdvicePreset" class="select-filter" style="width:100%;background:rgba(0,0,0,0.4);border-color:rgba(251,191,36,0.35);" onchange="onAdvicePresetChange(this.value)">
                    ${adviceOptions.map(a => `<option value="${a.val}" data-type="${a.type}" ${p.ai_advice === a.val || p.consiglio === a.val ? 'selected' : ''}>${a.label}</option>`).join('')}
                    <option value="CUSTOM" ${isCustomAdvice ? 'selected' : ''}>✍️ Testo Personalizzato...</option>
                </select>
                <input type="text" id="editPlayerAdviceCustom" class="input-search" style="width:100%;margin-top:6px;display:${isCustomAdvice ? 'block' : 'none'};background:rgba(0,0,0,0.4);" value="${p.ai_advice || p.consiglio || ''}" placeholder="Scrivi il tuo consiglio personalizzato...">
            </div>
            <!-- Modal Action Buttons -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;border-top:1px solid var(--border-glass);padding-top:14px;">
                <button class="btn-action" style="background:rgba(239,68,68,0.15);border-color:#ef4444;color:#f87171;" onclick="resetPlayerEditModal(${p.id})">🔄 Ripristina Default</button>
                <div style="display:flex;gap:8px;">
                    <button class="btn-action" onclick="closeEditPlayerModal()">Annulla</button>
                    <button class="btn-action" style="background:linear-gradient(135deg, #0284c7, #38bdf8);color:#fff;font-weight:800;border:none;" onclick="saveEditPlayerModal(${p.id})">💾 Salva Modifiche</button>
                </div>
            </div>
        </div>
    `;
    modal.classList.add('active');
}
function closeEditPlayerModal() {
    const modal = document.getElementById('editPlayerModal');
    if (modal) modal.classList.remove('active');
}
function saveEditPlayerModal(playerId) {
    const slotEl = document.getElementById('editPlayerSlot');
    const oopEl = document.getElementById('editPlayerOop');
    const advicePresetEl = document.getElementById('editPlayerAdvicePreset');
    const adviceCustomEl = document.getElementById('editPlayerAdviceCustom');
    if (!slotEl || !oopEl || !advicePresetEl) return;
    const slotVal = slotEl.value;
    const slotNum = parseInt(slotVal.split('°')[0]) || 1;
    const oopVal = oopEl.value;
    let adviceVal = advicePresetEl.value;
    let adviceType = 'regular';
    if (adviceVal === 'CUSTOM') {
        adviceVal = adviceCustomEl ? adviceCustomEl.value.trim() : 'Personalizzato';
        adviceType = 'regular';
    } else {
        const selectedOpt = advicePresetEl.options[advicePresetEl.selectedIndex];
        adviceType = selectedOpt ? selectedOpt.getAttribute('data-type') || 'regular' : 'regular';
    }
    setPlayerOverride(playerId, {
        slot_fascia: slotVal,
        slot_num: slotNum,
        oop_val: oopVal,
        is_oop: oopVal !== '-',
        fpp_fpn: oopVal !== '-' ? 'FPP' : 'NONE',
        ai_advice: adviceVal,
        consiglio: adviceVal,
        ai_advice_type: adviceType
    });
    closeEditPlayerModal();
}
function resetPlayerEditModal(playerId) {
    resetPlayerOverride(playerId);
    closeEditPlayerModal();
}
const MODULO_TEMPLATES = {
    '3-5-2': [
        { pos: 'POR', pos_label: 'Portiere', defaultRole: 'P' },
        { pos: 'DC_S', pos_label: 'Braccetto SX', defaultRole: 'D' },
        { pos: 'DC_C', pos_label: 'Centrale Difesa', defaultRole: 'D' },
        { pos: 'DC_D', pos_label: 'Braccetto DX', defaultRole: 'D' },
        { pos: 'ES', pos_label: 'Esterno SX', defaultRole: 'D' },
        { pos: 'CC_S', pos_label: 'Mezzala SX', defaultRole: 'C' },
        { pos: 'MED', pos_label: 'Regista', defaultRole: 'C' },
        { pos: 'CC_D', pos_label: 'Mezzala DX', defaultRole: 'C' },
        { pos: 'ED', pos_label: 'Esterno DX', defaultRole: 'D' },
        { pos: 'PC_S', pos_label: 'Punta SX', defaultRole: 'A' },
        { pos: 'PC_D', pos_label: 'Punta DX', defaultRole: 'A' }
    ],
    '4-3-3': [
        { pos: 'POR', pos_label: 'Portiere', defaultRole: 'P' },
        { pos: 'TS', pos_label: 'Terzino SX', defaultRole: 'D' },
        { pos: 'DC_S', pos_label: 'Centrale SX', defaultRole: 'D' },
        { pos: 'DC_D', pos_label: 'Centrale DX', defaultRole: 'D' },
        { pos: 'TD', pos_label: 'Terzino DX', defaultRole: 'D' },
        { pos: 'MEZ_S', pos_label: 'Mezzala SX', defaultRole: 'C' },
        { pos: 'REG', pos_label: 'Regista', defaultRole: 'C' },
        { pos: 'MEZ_D', pos_label: 'Mezzala DX', defaultRole: 'C' },
        { pos: 'AS', pos_label: 'Ala Sinistra', defaultRole: 'A' },
        { pos: 'PC', pos_label: 'Punta Centrale', defaultRole: 'A' },
        { pos: 'AD', pos_label: 'Ala Destra', defaultRole: 'A' }
    ],
    '3-4-2-1': [
        { pos: 'POR', pos_label: 'Portiere', defaultRole: 'P' },
        { pos: 'DC_S', pos_label: 'Braccetto SX', defaultRole: 'D' },
        { pos: 'DC_C', pos_label: 'Centrale Difesa', defaultRole: 'D' },
        { pos: 'DC_D', pos_label: 'Braccetto DX', defaultRole: 'D' },
        { pos: 'ES', pos_label: 'Esterno SX', defaultRole: 'D' },
        { pos: 'MED_S', pos_label: 'Mediano SX', defaultRole: 'C' },
        { pos: 'MED_D', pos_label: 'Mediano DX', defaultRole: 'C' },
        { pos: 'ED', pos_label: 'Esterno DX', defaultRole: 'D' },
        { pos: 'TRQ_S', pos_label: 'Trequartista SX', defaultRole: 'C' },
        { pos: 'TRQ_D', pos_label: 'Trequartista DX', defaultRole: 'C' },
        { pos: 'PC', pos_label: 'Punta Centrale', defaultRole: 'A' }
    ],
    '4-2-3-1': [
        { pos: 'POR', pos_label: 'Portiere', defaultRole: 'P' },
        { pos: 'TS', pos_label: 'Terzino SX', defaultRole: 'D' },
        { pos: 'DC_S', pos_label: 'Centrale SX', defaultRole: 'D' },
        { pos: 'DC_D', pos_label: 'Centrale DX', defaultRole: 'D' },
        { pos: 'TD', pos_label: 'Terzino DX', defaultRole: 'D' },
        { pos: 'MED_S', pos_label: 'Mediano SX', defaultRole: 'C' },
        { pos: 'MED_D', pos_label: 'Mediano DX', defaultRole: 'C' },
        { pos: 'AS', pos_label: 'Ala Sinistra', defaultRole: 'C' },
        { pos: 'TRQ', pos_label: 'Trequartista', defaultRole: 'C' },
        { pos: 'AD', pos_label: 'Ala Destra', defaultRole: 'C' },
        { pos: 'PC', pos_label: 'Punta Centrale', defaultRole: 'A' }
    ],
    '3-4-1-2': [
        { pos: 'POR', pos_label: 'Portiere', defaultRole: 'P' },
        { pos: 'DC_S', pos_label: 'Braccetto SX', defaultRole: 'D' },
        { pos: 'DC_C', pos_label: 'Centrale Difesa', defaultRole: 'D' },
        { pos: 'DC_D', pos_label: 'Braccetto DX', defaultRole: 'D' },
        { pos: 'ES', pos_label: 'Esterno SX', defaultRole: 'D' },
        { pos: 'MED_S', pos_label: 'Mediano SX', defaultRole: 'C' },
        { pos: 'MED_D', pos_label: 'Mediano DX', defaultRole: 'C' },
        { pos: 'ED', pos_label: 'Esterno DX', defaultRole: 'D' },
        { pos: 'TRQ', pos_label: 'Trequartista', defaultRole: 'C' },
        { pos: 'PC_S', pos_label: 'Punta SX', defaultRole: 'A' },
        { pos: 'PC_D', pos_label: 'Punta DX', defaultRole: 'A' }
    ],
    '4-4-2': [
        { pos: 'POR', pos_label: 'Portiere', defaultRole: 'P' },
        { pos: 'TS', pos_label: 'Terzino SX', defaultRole: 'D' },
        { pos: 'DC_S', pos_label: 'Centrale SX', defaultRole: 'D' },
        { pos: 'DC_D', pos_label: 'Centrale DX', defaultRole: 'D' },
        { pos: 'TD', pos_label: 'Terzino DX', defaultRole: 'D' },
        { pos: 'ES', pos_label: 'Esterno SX', defaultRole: 'C' },
        { pos: 'CC_S', pos_label: 'Centrocampista SX', defaultRole: 'C' },
        { pos: 'CC_D', pos_label: 'Centrocampista DX', defaultRole: 'C' },
        { pos: 'ED', pos_label: 'Esterno DX', defaultRole: 'C' },
        { pos: 'PC_S', pos_label: 'Punta SX', defaultRole: 'A' },
        { pos: 'PC_D', pos_label: 'Punta DX', defaultRole: 'A' }
    ]
};
window.currentEditorSlots = [];
function openTacticalEditorModal(teamName) {
    if (!teamName) teamName = State.currentTeamPitch || 'Inter';
    State.currentTeamPitch = teamName;
    const modal = document.getElementById('tacticalEditorModal');
    const body = document.getElementById('tacticalEditorModalBody');
    const titleEl = document.getElementById('tacticalEditorTitle');
    if (!modal || !body) return;
    if (titleEl) {
        titleEl.innerHTML = `⚙️ Editor Formazione & Sostituti — <span style="color:#fff;">${teamName}</span>`;
    }
    const team = getTeamTacticalData(teamName);
    if (!team) return;
    const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase())
        .sort((a, b) => {
            const rOrd = { 'P': 1, 'D': 2, 'C': 3, 'A': 4 };
            if (rOrd[a.role] !== rOrd[b.role]) return rOrd[a.role] - rOrd[b.role];
            return (b.ovr || 0) - (a.ovr || 0);
        });
    const currentModulo = team.modulo || '3-5-2';
    window.currentEditorSlots = (team.lineup || []).map((lp, idx) => {
        const sub = getSubstituteForStarter(lp, team, teamPlayers);
        let pct = 85;
        if (lp.status && lp.status.includes('%')) {
            const m = lp.status.match(/(\d+)%/);
            if (m) pct = parseInt(m[1], 10);
        } else if (team.ballottaggi) {
            const b = team.ballottaggi.find(item => (item.player || '').toLowerCase() === (lp.name || '').toLowerCase());
            if (b && b.pct) pct = b.pct;
        }
        return {
            pos: lp.pos,
            pos_label: lp.pos_label || lp.pos,
            starterName: lp.name,
            starterRole: lp.role,
            subName: lp.sub_name || (sub ? sub.name : ''),
            subRole: lp.sub_role || (sub ? sub.role : lp.role),
            pct: pct,
            fpp_fpn: lp.fpp_fpn || 'NONE',
            oop: !!lp.oop,
            oop_type: lp.oop_type,
            oop_desc: lp.oop_desc
        };
    });
    renderTacticalEditorBody(teamName, currentModulo, team.all, teamPlayers, team);
    modal.style.display = 'flex';
}
function renderTacticalEditorBody(teamName, modulo, coach, teamPlayers, team) {
    const body = document.getElementById('tacticalEditorModalBody');
    if (!body) return;
    const moduloOptions = Object.keys(MODULO_TEMPLATES);
    if (!moduloOptions.includes(modulo)) moduloOptions.unshift(modulo);
    let slotsHtml = '';
    window.currentEditorSlots.forEach((slot, idx) => {
        const starterOpts = teamPlayers.map(pl => {
            const isSel = (pl.name.toLowerCase() === (slot.starterName || '').toLowerCase());
            return `<option value="${pl.name}" data-role="${pl.role}" ${isSel ? 'selected' : ''}>[${pl.role}] ${pl.name} (OVR ${pl.ovr} - ${pl.prezzo_cons}CR)</option>`;
        }).join('');
        const subOpts = [`<option value="">-- Nessun sostituto diretto --</option>`].concat(
            teamPlayers.map(pl => {
                const isSel = (pl.name.toLowerCase() === (slot.subName || '').toLowerCase());
                return `<option value="${pl.name}" data-role="${pl.role}" ${isSel ? 'selected' : ''}>[${pl.role}] ${pl.name} (OVR ${pl.ovr})</option>`;
            })
        ).join('');
        const pctOpts = [
            { val: 100, label: '100% Inamovibile (0% Sub)' },
            { val: 85, label: '85% Titolare fisso (15% Rotazione)' },
            { val: 75, label: '75% Titolare primario (25% Sub)' },
            { val: 65, label: '65% Titolare (35% Ballottaggio)' },
            { val: 50, label: '50% vs 50% (Pari Merito)' }
        ].map(p => `<option value="${p.val}" ${slot.pct === p.val ? 'selected' : ''}>${p.label}</option>`).join('');
        slotsHtml += `
            <div class="tactical-slot-row">
                <div class="tactical-slot-pos">
                    <span class="tactical-slot-pos-badge ${slot.starterRole}">${slot.starterRole}</span>
                    <div>
                        <div class="tactical-slot-pos-label">${slot.pos_label}</div>
                        <div style="font-size:9.5px;color:var(--text-muted);">${slot.pos}</div>
                    </div>
                </div>
                <div>
                    <div style="font-size:10px;font-weight:800;color:var(--accent-cyan);margin-bottom:3px;">⚽ TITOLARE:</div>
                    <select class="tactical-select" onchange="onEditorStarterChange(${idx}, this.value)">
                        ${starterOpts}
                    </select>
                </div>
                <div>
                    <div style="font-size:10px;font-weight:800;color:#fbbf24;margin-bottom:3px;">↳ SOSTITUTO / VICE DIRETTO:</div>
                    <select class="tactical-select" onchange="onEditorSubChange(${idx}, this.value)">
                        ${subOpts}
                    </select>
                </div>
                <div>
                    <div style="font-size:10px;font-weight:800;color:#4ade80;margin-bottom:3px;">⚖️ TITOLARITÀ:</div>
                    <select class="tactical-select" onchange="onEditorPctChange(${idx}, this.value)">
                        ${pctOpts}
                    </select>
                </div>
            </div>
        `;
    });
    const rigoristi = team.rigoristi || [];
    const r1Opts = teamPlayers.map(p => `<option value="${p.name}" ${rigoristi[0] === p.name ? 'selected' : ''}>${p.name} (${p.role})</option>`).join('');
    const r2Opts = teamPlayers.map(p => `<option value="${p.name}" ${rigoristi[1] === p.name ? 'selected' : ''}>${p.name} (${p.role})</option>`).join('');
    const r3Opts = teamPlayers.map(p => `<option value="${p.name}" ${rigoristi[2] === p.name ? 'selected' : ''}>${p.name} (${p.role})</option>`).join('');
    body.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:14px;">
            <!-- Controlli Modulo & Allenatore -->
            <div class="tactical-editor-header-controls">
                <div style="display:flex;align-items:center;gap:10px;">
                    <label style="font-size:12px;font-weight:800;color:var(--accent-cyan);">📐 MODULO:</label>
                    <select id="editorModuloSelect" class="tactical-select" style="width:130px;font-weight:800;" onchange="onEditorModuloChange(this.value, '${teamName}')">
                        ${moduloOptions.map(m => `<option value="${m}" ${m === modulo ? 'selected' : ''}>${m}</option>`).join('')}
                    </select>
                </div>
                <div style="display:flex;align-items:center;gap:10px;flex:1;max-width:320px;">
                    <label style="font-size:12px;font-weight:800;color:var(--text-secondary);">👔 ALLENATORE:</label>
                    <input type="text" id="editorCoachInput" class="tactical-select" value="${coach || ''}" style="flex:1;" />
                </div>
                <div style="font-size:11.5px;color:var(--text-muted);background:rgba(0,0,0,0.3);padding:6px 10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);">
                    🛡️ Difesa: <b style="color:#fbbf24;">${team.dif_stars || 3}★</b> &nbsp;•&nbsp; ⚔️ Attacco: <b style="color:#fbbf24;">${team.att_stars || 3}★</b>
                </div>
            </div>
            <!-- Avviso Sincronizzazione Listone -->
            <div style="background:rgba(0,242,254,0.06);border:1px solid rgba(0,242,254,0.2);padding:9px 14px;border-radius:8px;font-size:11.5px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">💡</span>
                <span>Assegnare un sostituto (es. <b>Zielinski per Calhanoglu</b>) aggiorna il campo 2D, crea il ballottaggio e <b>ricalcola automaticamente la titolarità, il prezzo consigliato e lo slot nel Listone</b>.</span>
            </div>
            <!-- Lista degli 11 Slot di Campo -->
            <div class="tactical-slots-list" id="tacticalSlotsContainer">
                ${slotsHtml}
            </div>
            <!-- Gestione Rigoristi -->
            <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:12px 14px;">
                <div style="font-size:11px;font-weight:800;color:#fbbf24;margin-bottom:8px;letter-spacing:0.4px;">🎯 GERARCHIA RIGORISTI UFFICIALE:</div>
                <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px;">
                    <div>
                        <span style="font-size:10px;color:#4ade80;font-weight:800;">1° RIGORISTA</span>
                        <select id="editorRigorista1" class="tactical-select" style="margin-top:2px;">${r1Opts}</select>
                    </div>
                    <div>
                        <span style="font-size:10px;color:var(--text-secondary);font-weight:800;">2° RIGORISTA</span>
                        <select id="editorRigorista2" class="tactical-select" style="margin-top:2px;">${r2Opts}</select>
                    </div>
                    <div>
                        <span style="font-size:10px;color:var(--text-muted);font-weight:800;">3° RIGORISTA</span>
                        <select id="editorRigorista3" class="tactical-select" style="margin-top:2px;">${r3Opts}</select>
                    </div>
                </div>
            </div>
            <!-- Footer Azioni -->
            <div class="tactical-editor-footer">
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <button class="btn-action" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%);color:#fff;font-weight:900;border:none;padding:9px 18px;font-size:12.5px;box-shadow:0 0 16px rgba(16,185,129,0.35);" onclick="saveTacticalEditor('${teamName}')">
                        💾 Salva Formazione Ufficiale & Ricalcola Listone
                    </button>
                    <button class="btn-action" style="background:linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);color:#fff;font-weight:900;border:none;padding:9px 18px;font-size:12.5px;box-shadow:0 0 16px rgba(139,92,246,0.35);" onclick="autoFillLineupFromTitolarita('${teamName}')" title="Popola automaticamente titolari e sostituti basandosi sui dati reali 2026/27 (presenze, titolarità, starts)">
                        🤖 Auto-Fill da Titolarità Reale 26/27
                    </button>
                    <button class="btn-action" style="background:rgba(0,242,254,0.1);border-color:var(--accent-cyan);color:var(--accent-cyan);font-weight:700;padding:8px 14px;font-size:12px;" onclick="exportTacticalDbJson()">
                        📥 Esporta Database (.json)
                    </button>
                </div>
                <div style="display:flex;gap:8px;">
                    <button class="btn-action" style="background:rgba(239,68,68,0.1);border-color:rgba(239,68,68,0.3);color:#f87171;font-size:11.5px;" onclick="resetTacticalEditor('${teamName}')">
                        🔄 Ripristina Default Serie A
                    </button>
                    <button class="btn-action" style="font-size:11.5px;" onclick="closeTacticalEditorModal()">
                        Annulla
                    </button>
                </div>
            </div>
        </div>
    `;
}
function onEditorStarterChange(slotIdx, newStarterName) {
    if (!window.currentEditorSlots[slotIdx]) return;
    const p = PLAYERS.find(pl => pl.name.toLowerCase() === newStarterName.toLowerCase());
    window.currentEditorSlots[slotIdx].starterName = newStarterName;
    if (p) window.currentEditorSlots[slotIdx].starterRole = p.role;
}
function onEditorSubChange(slotIdx, newSubName) {
    if (!window.currentEditorSlots[slotIdx]) return;
    const p = PLAYERS.find(pl => pl.name.toLowerCase() === (newSubName || '').toLowerCase());
    window.currentEditorSlots[slotIdx].subName = newSubName || '';
    if (p) {
        window.currentEditorSlots[slotIdx].subRole = p.role;
    } else {
        window.currentEditorSlots[slotIdx].subRole = window.currentEditorSlots[slotIdx].starterRole;
    }
}
function onEditorPctChange(slotIdx, newPct) {
    if (!window.currentEditorSlots[slotIdx]) return;
    window.currentEditorSlots[slotIdx].pct = parseInt(newPct, 10) || 85;
}
function onEditorModuloChange(newModulo, teamName) {
    const template = MODULO_TEMPLATES[newModulo];
    if (!template) return;
    const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase());
    const oldSlots = window.currentEditorSlots || [];
    window.currentEditorSlots = template.map((tpl, idx) => {
        const matchingOld = oldSlots.find(os => os.starterRole === tpl.defaultRole && !oldSlots.slice(0, idx).some(prev => prev.starterName === os.starterName));
        const starter = matchingOld ? matchingOld.starterName : (teamPlayers.find(p => p.role === tpl.defaultRole) || teamPlayers[0]).name;
        const pObj = teamPlayers.find(p => p.name === starter);
        const sub = matchingOld ? matchingOld.subName : '';
        return {
            pos: tpl.pos,
            pos_label: tpl.pos_label,
            starterName: starter,
            starterRole: pObj ? pObj.role : tpl.defaultRole,
            subName: sub,
            subRole: matchingOld ? matchingOld.subRole : (pObj ? pObj.role : tpl.defaultRole),
            pct: matchingOld ? matchingOld.pct : 85,
            fpp_fpn: matchingOld ? matchingOld.fpp_fpn : 'NONE',
            oop: matchingOld ? matchingOld.oop : false
        };
    });
    const coach = document.getElementById('editorCoachInput') ? document.getElementById('editorCoachInput').value : '';
    const team = getTeamTacticalData(teamName);
    renderTacticalEditorBody(teamName, newModulo, coach, teamPlayers, team);
}
function closeTacticalEditorModal() {
    const modal = document.getElementById('tacticalEditorModal');
    if (modal) modal.style.display = 'none';
}
function autoFillLineupFromTitolarita(teamName) {
    if (!teamName) teamName = State.currentTeamPitch || 'Inter';
    const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase())
        .map(p => ({ ...p })); // Clone leggero per non alterare PLAYERS
    if (teamPlayers.length === 0) {
        alert(`Nessun giocatore trovato per ${teamName}.`);
        return;
    }
    const rankPlayer = (p) => {
        const starts = p.starts_2627 || 0;
        const pres = p.presenze_2627 || 0;
        const tit = p.titolarita || 0;
        const ovr = p.ovr || 0;
        return starts * 1000 + pres * 100 + tit * 10 + ovr;
    };
    const byRole = { P: [], D: [], C: [], A: [] };
    teamPlayers.forEach(p => {
        if (byRole[p.role]) {
            byRole[p.role].push(p);
        }
    });
    Object.keys(byRole).forEach(r => {
        byRole[r].sort((a, b) => rankPlayer(b) - rankPlayer(a));
    });
    const usedPlayerNames = new Set(); // Evita duplicati
    const slots = window.currentEditorSlots;
    if (!slots || slots.length === 0) {
        alert('Apri prima l\'editor formazione per usare Auto-Fill.');
        return;
    }
    const roleIdx = { P: 0, D: 0, C: 0, A: 0 };
    slots.forEach((slot, idx) => {
        const role = slot.starterRole || 'C';
        const candidates = byRole[role] || [];
        let chosen = null;
        for (const c of candidates) {
            if (!usedPlayerNames.has(c.name.toLowerCase())) {
                chosen = c;
                break;
            }
        }
        if (chosen) {
            usedPlayerNames.add(chosen.name.toLowerCase());
            slot.starterName = chosen.name;
            slot.starterRole = chosen.role;
        }
    });
    const usedAsSub = new Set();
    slots.forEach((slot, idx) => {
        const role = slot.starterRole || 'C';
        const candidates = byRole[role] || [];
        const starterName = (slot.starterName || '').toLowerCase();
        let sub = null;
        for (const c of candidates) {
            const cLower = c.name.toLowerCase();
            if (cLower !== starterName && !usedPlayerNames.has(cLower) && !usedAsSub.has(cLower)) {
                sub = c;
                break;
            }
        }
        if (!sub) {
            for (const c of candidates) {
                const cLower = c.name.toLowerCase();
                if (cLower !== starterName && !usedAsSub.has(cLower)) {
                    sub = c;
                    break;
                }
            }
        }
        if (sub) {
            usedAsSub.add(sub.name.toLowerCase());
            slot.subName = sub.name;
            slot.subRole = sub.role;
            const starterObj = teamPlayers.find(p => p.name.toLowerCase() === starterName);
            const starterStarts = starterObj ? (starterObj.starts_2627 || 0) : 0;
            const subStarts = sub.starts_2627 || 0;
            const totalStarts = starterStarts + subStarts;
            if (totalStarts > 0) {
                const realPct = Math.round((starterStarts / totalStarts) * 100);
                const presets = [100, 85, 75, 65, 50];
                slot.pct = presets.reduce((prev, curr) =>
                    Math.abs(curr - realPct) < Math.abs(prev - realPct) ? curr : prev
                );
            } else {
                const starterTit = starterObj ? (starterObj.titolarita || 50) : 50;
                if (starterTit >= 90) slot.pct = 100;
                else if (starterTit >= 80) slot.pct = 85;
                else if (starterTit >= 70) slot.pct = 75;
                else if (starterTit >= 55) slot.pct = 65;
                else slot.pct = 50;
            }
        } else {
            slot.subName = '';
            slot.subRole = role;
            slot.pct = 100; // Nessun sostituto diretto → titolarissimo
        }
    });
    const team = getTeamTacticalData(teamName);
    const modulo = document.getElementById('editorModuloSelect') ? document.getElementById('editorModuloSelect').value : (team.modulo || '3-5-2');
    const coach = document.getElementById('editorCoachInput') ? document.getElementById('editorCoachInput').value : (team.all || '');
    renderTacticalEditorBody(teamName, modulo, coach, 
        PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase())
            .sort((a, b) => {
                const rOrd = { 'P': 1, 'D': 2, 'C': 3, 'A': 4 };
                if (rOrd[a.role] !== rOrd[b.role]) return rOrd[a.role] - rOrd[b.role];
                return (b.ovr || 0) - (a.ovr || 0);
            }),
        team
    );
    const filledCount = slots.filter(s => s.starterName).length;
    const subCount = slots.filter(s => s.subName).length;
    const withRealData = slots.filter(s => {
        const p = teamPlayers.find(tp => tp.name.toLowerCase() === (s.starterName || '').toLowerCase());
        return p && (p.starts_2627 || 0) > 0;
    }).length;
    if (typeof showSyncToast === 'function') {
        showSyncToast(`🤖 Auto-Fill: ${filledCount} titolari + ${subCount} sostituti assegnati per ${teamName} (${withRealData} con dati reali 26/27). Verifica e salva!`);
    } else {
        alert(`🤖 Auto-Fill completato per ${teamName}!\n• ${filledCount} titolari assegnati\n• ${subCount} sostituti dello stesso ruolo\n• ${withRealData} con dati reali 26/27\n\nVerifica le assegnazioni e premi "Salva" per confermare.`);
    }
}
function saveTacticalEditor(teamName) {
    if (!teamName) teamName = State.currentTeamPitch || 'Inter';
    const moduloEl = document.getElementById('editorModuloSelect');
    const coachEl = document.getElementById('editorCoachInput');
    const r1El = document.getElementById('editorRigorista1');
    const r2El = document.getElementById('editorRigorista2');
    const r3El = document.getElementById('editorRigorista3');
    const newModulo = moduloEl ? moduloEl.value : '3-5-2';
    const newCoach = coachEl ? coachEl.value.trim() : '';
    const newRigoristi = [
        r1El ? r1El.value : '',
        r2El ? r2El.value : '',
        r3El ? r3El.value : ''
    ].filter(Boolean);
    const team = getTeamTacticalData(teamName);
    const newLineup = window.currentEditorSlots.map(s => {
        let statusText = s.pct >= 95 ? 'Titolare Inamovibile (100% Tit)' : `Titolare (${s.pct}% vs ${s.subName || 'Sub'} ${100 - s.pct}%)`;
        return {
            pos: s.pos,
            pos_label: s.pos_label,
            name: s.starterName,
            role: s.starterRole,
            sub_name: s.subName || null,
            sub_role: s.subRole || s.starterRole,
            status: statusText,
            pct: s.pct,
            fpp_fpn: s.fpp_fpn || 'NONE',
            oop: !!s.oop,
            oop_type: s.oop_type,
            oop_desc: s.oop_desc
        };
    });
    const newBallottaggi = [];
    newLineup.forEach(lp => {
        if (lp.sub_name && lp.pct < 95) {
            newBallottaggi.push({
                player: lp.name,
                pct: lp.pct,
                vs: `${lp.sub_name} (${100 - lp.pct}%)`
            });
            newBallottaggi.push({
                player: lp.sub_name,
                pct: 100 - lp.pct,
                vs: `${lp.name} (${lp.pct}%)`
            });
        }
    });
    const updatedTeam = {
        ...team,
        modulo: newModulo,
        all: newCoach || team.all,
        rigoristi: newRigoristi.length > 0 ? newRigoristi : team.rigoristi,
        lineup: newLineup,
        ballottaggi: newBallottaggi
    };
    TACTICAL_DB[teamName] = updatedTeam;
    if (!window.CUSTOM_TACTICAL_DB) window.CUSTOM_TACTICAL_DB = {};
    window.CUSTOM_TACTICAL_DB[teamName] = updatedTeam;
    try {
        localStorage.setItem('FANTA_TACTICAL_DB_CUSTOM', JSON.stringify(window.CUSTOM_TACTICAL_DB));
    } catch(e) {
        console.warn('Errore salvataggio LocalStorage:', e);
    }
    applyTacticalChangesToPlayers(teamName, updatedTeam);
    if (typeof syncSocket !== 'undefined' && syncSocket && syncSocket.readyState === WebSocket.OPEN) {
        try {
            syncSocket.send(JSON.stringify({
                type: 'SAVE_TACTICAL_DB',
                team: teamName,
                data: updatedTeam
            }));
        } catch(e) {}
    }
    closeTacticalEditorModal();
    renderPitchTeam(teamName);
    renderTeamRosterTable(teamName);
    if (typeof renderTable === 'function') {
        renderTable();
    }
    if (typeof showSyncToast === 'function') {
        showSyncToast(`✓ Formazione di ${teamName} salvata come Ufficiale e Listone ricalcolato!`);
    } else {
        alert(`✓ Formazione e Sostituti di ${teamName} salvati con successo come UFFICIALI!\nLe valutazioni del Listone sono state aggiornate.`);
    }
}
function applyTacticalChangesToPlayers(teamName, updatedTeam) {
    const starterNames = (updatedTeam.lineup || []).map(lp => (lp.name || '').toLowerCase());
    const subMap = {};
    (updatedTeam.lineup || []).forEach(lp => {
        if (lp.sub_name) {
            subMap[lp.sub_name.toLowerCase()] = {
                starterName: lp.name,
                starterRole: lp.role,
                subRole: lp.sub_role || lp.role,
                pct: lp.pct || 85,
                pos_label: lp.pos_label
            };
        }
    });
    const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase());
    teamPlayers.forEach(p => {
        const pLower = p.name.toLowerCase();
        const isStarter = starterNames.includes(pLower);
        const subInfo = subMap[pLower];
        let overrides = {};
        if (isStarter) {
            p.is_in_11 = true;
            const lp = updatedTeam.lineup.find(l => l.name.toLowerCase() === pLower);
            const duelPct = lp ? (lp.pct || 85) : 85;
            if (duelPct >= 95) p.titolarita = Math.max(92, p.titolarita || 92);
            else if (duelPct >= 80) p.titolarita = Math.max(85, p.titolarita || 85);
            else if (duelPct >= 65) p.titolarita = Math.max(72, p.titolarita || 72);
            else p.titolarita = Math.max(55, p.titolarita || 55);
            overrides.is_in_11 = true;
            overrides.titolarita = p.titolarita;
            if (subInfo) {
                p.ai_advice = 'Titolare & Vice Regista (Polivalente)';
                p.consiglio = p.ai_advice;
                p.ai_advice_type = 'top';
                overrides.ai_advice = p.ai_advice;
                overrides.consiglio = p.consiglio;
                overrides.ai_advice_type = 'top';
            }
        } else if (subInfo) {
            p.is_in_11 = false;
            const subPct = Math.max(25, 100 - subInfo.pct);
            p.titolarita = Math.max(subPct, p.titolarita || 30);
            p.ai_advice = `Rotazione / Vice ${subInfo.pos_label || subInfo.starterName}`;
            p.consiglio = p.ai_advice;
            p.ai_advice_type = 'rotation';
            if (p.prezzo_cons < 8 && ['Inter', 'Milan', 'Juventus', 'Napoli', 'Roma', 'Atalanta'].includes(teamName)) {
                p.prezzo_cons = Math.min(22, Math.max(8, Math.round(p.ovr * 0.16)));
                p.max_bid = Math.round(p.prezzo_cons * 1.15);
            }
            if (p.slot_num > 5) {
                p.slot_num = 4;
                p.slot_fascia = `4° Slot ${p.role} (Rotazione)`;
            }
            overrides.is_in_11 = false;
            overrides.titolarita = p.titolarita;
            overrides.ai_advice = p.ai_advice;
            overrides.consiglio = p.consiglio;
            overrides.ai_advice_type = 'rotation';
            overrides.prezzo_cons = p.prezzo_cons;
            overrides.max_bid = p.max_bid;
            overrides.slot_num = p.slot_num;
            overrides.slot_fascia = p.slot_fascia;
        } else {
            p.is_in_11 = false;
            if (p.titolarita > 35) {
                p.titolarita = 25;
                overrides.titolarita = 25;
            }
        }
        if (Object.keys(overrides).length > 0 && typeof setPlayerOverride === 'function') {
            setPlayerOverride(p.id, overrides);
        }
    });
}
function resetTacticalEditor(teamName) {
    if (!teamName) teamName = State.currentTeamPitch || 'Inter';
    if (confirm(`Sei sicuro di voler ripristinare la formazione e i ballottaggi predefiniti per ${teamName}?`)) {
        if (window.CUSTOM_TACTICAL_DB && window.CUSTOM_TACTICAL_DB[teamName]) {
            delete window.CUSTOM_TACTICAL_DB[teamName];
            try {
                localStorage.setItem('FANTA_TACTICAL_DB_CUSTOM', JSON.stringify(window.CUSTOM_TACTICAL_DB));
            } catch(e) {}
        }
        closeTacticalEditorModal();
        renderPitchTeam(teamName);
        renderTeamRosterTable(teamName);
        if (typeof renderTable === 'function') renderTable();
        alert(`✓ Formazione di ${teamName} ripristinata al valore ufficiale predefinito.`);
    }
}
function exportTacticalDbJson() {
    const fullDb = {};
    const allTeams = Object.keys(TACTICAL_DB);
    allTeams.forEach(tm => {
        fullDb[tm] = getTeamTacticalData(tm);
    });
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(fullDb, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", "tactical_db.json");
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
}
function autoFillAndSaveCurrentTeam() {
    const teamName = State.currentTeamPitch || 'Inter';
    if (!confirm(`🤖 Vuoi auto-compilare Titolari e Sostituti per ${teamName} basandoti sui dati reali 2026/27?\n\nQuesto sovrascriverà la formazione attuale.`)) {
        return;
    }
    const team = getTeamTacticalData(teamName);
    if (!team) return;
    const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase())
        .sort((a, b) => {
            const rOrd = { 'P': 1, 'D': 2, 'C': 3, 'A': 4 };
            if (rOrd[a.role] !== rOrd[b.role]) return rOrd[a.role] - rOrd[b.role];
            return (b.ovr || 0) - (a.ovr || 0);
        });
    window.currentEditorSlots = (team.lineup || []).map((lp, idx) => {
        const sub = getSubstituteForStarter(lp, team, teamPlayers);
        let pct = 85;
        if (lp.status && lp.status.includes('%')) {
            const m = lp.status.match(/(\d+)%/);
            if (m) pct = parseInt(m[1], 10);
        } else if (team.ballottaggi) {
            const b = team.ballottaggi.find(item => (item.player || '').toLowerCase() === (lp.name || '').toLowerCase());
            if (b && b.pct) pct = b.pct;
        }
        return {
            pos: lp.pos,
            pos_label: lp.pos_label || lp.pos,
            starterName: lp.name,
            starterRole: lp.role,
            subName: lp.sub_name || (sub ? sub.name : ''),
            subRole: lp.sub_role || (sub ? sub.role : lp.role),
            pct: pct,
            fpp_fpn: lp.fpp_fpn || 'NONE',
            oop: !!lp.oop,
            oop_type: lp.oop_type,
            oop_desc: lp.oop_desc
        };
    });
    _autoFillSlots(teamName);
    _saveFromSlots(teamName, team);
    renderPitchTeam(teamName);
    renderTeamRosterTable(teamName);
    if (typeof renderTable === 'function') renderTable();
    if (typeof showSyncToast === 'function') {
        showSyncToast(`🤖 Auto-Fill: formazione di ${teamName} aggiornata e salvata con dati reali 26/27!`);
    }
}
function autoFillAllTeams() {
    if (!confirm('🤖 Vuoi auto-compilare Titolari e Sostituti per TUTTE le 20 squadre?\n\nQuesto sovrascriverà tutte le formazioni con i dati reali 2026/27.')) {
        return;
    }
    const allTeams = Object.keys(TACTICAL_DB).sort();
    let successCount = 0;
    allTeams.forEach(teamName => {
        try {
            const team = getTeamTacticalData(teamName);
            if (!team || !team.lineup || team.lineup.length === 0) return;
            const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase())
                .sort((a, b) => {
                    const rOrd = { 'P': 1, 'D': 2, 'C': 3, 'A': 4 };
                    if (rOrd[a.role] !== rOrd[b.role]) return rOrd[a.role] - rOrd[b.role];
                    return (b.ovr || 0) - (a.ovr || 0);
                });
            window.currentEditorSlots = (team.lineup || []).map((lp) => {
                const sub = getSubstituteForStarter(lp, team, teamPlayers);
                let pct = 85;
                if (lp.status && lp.status.includes('%')) {
                    const m = lp.status.match(/(\d+)%/);
                    if (m) pct = parseInt(m[1], 10);
                } else if (team.ballottaggi) {
                    const b = team.ballottaggi.find(item => (item.player || '').toLowerCase() === (lp.name || '').toLowerCase());
                    if (b && b.pct) pct = b.pct;
                }
                return {
                    pos: lp.pos, pos_label: lp.pos_label || lp.pos,
                    starterName: lp.name, starterRole: lp.role,
                    subName: lp.sub_name || (sub ? sub.name : ''),
                    subRole: lp.sub_role || (sub ? sub.role : lp.role),
                    pct, fpp_fpn: lp.fpp_fpn || 'NONE',
                    oop: !!lp.oop, oop_type: lp.oop_type, oop_desc: lp.oop_desc
                };
            });
            _autoFillSlots(teamName);
            _saveFromSlots(teamName, team);
            successCount++;
        } catch(e) {
            console.warn(`Auto-Fill fallito per ${teamName}:`, e);
        }
    });
    const current = State.currentTeamPitch || 'Inter';
    renderPitchTeam(current);
    renderTeamRosterTable(current);
    if (typeof renderTable === 'function') renderTable();
    if (typeof showSyncToast === 'function') {
        showSyncToast(`🤖 Auto-Fill completato per ${successCount}/${allTeams.length} squadre! Formazioni aggiornate con dati reali 26/27.`);
    } else {
        alert(`🤖 Auto-Fill completato per ${successCount}/${allTeams.length} squadre!\nTutte le formazioni sono state aggiornate con dati reali 2026/27.`);
    }
}
function _autoFillSlots(teamName) {
    const teamPlayers = PLAYERS.filter(p => (p.team || '').toLowerCase() === teamName.toLowerCase())
        .map(p => ({ ...p }));
    const rankPlayer = (p) => {
        return (p.starts_2627 || 0) * 1000 + (p.presenze_2627 || 0) * 100 + (p.titolarita || 0) * 10 + (p.ovr || 0);
    };
    const byRole = { P: [], D: [], C: [], A: [] };
    teamPlayers.forEach(p => { if (byRole[p.role]) byRole[p.role].push(p); });
    Object.keys(byRole).forEach(r => byRole[r].sort((a, b) => rankPlayer(b) - rankPlayer(a)));
    const usedPlayerNames = new Set();
    const slots = window.currentEditorSlots;
    slots.forEach(slot => {
        const role = slot.starterRole || 'C';
        const candidates = byRole[role] || [];
        for (const c of candidates) {
            if (!usedPlayerNames.has(c.name.toLowerCase())) {
                usedPlayerNames.add(c.name.toLowerCase());
                slot.starterName = c.name;
                slot.starterRole = c.role;
                break;
            }
        }
    });
    const usedAsSub = new Set();
    slots.forEach(slot => {
        const role = slot.starterRole || 'C';
        const candidates = byRole[role] || [];
        const starterName = (slot.starterName || '').toLowerCase();
        let sub = null;
        for (const c of candidates) {
            const cLower = c.name.toLowerCase();
            if (cLower !== starterName && !usedPlayerNames.has(cLower) && !usedAsSub.has(cLower)) {
                sub = c; break;
            }
        }
        if (!sub) {
            for (const c of candidates) {
                const cLower = c.name.toLowerCase();
                if (cLower !== starterName && !usedAsSub.has(cLower)) { sub = c; break; }
            }
        }
        if (sub) {
            usedAsSub.add(sub.name.toLowerCase());
            slot.subName = sub.name;
            slot.subRole = sub.role;
            const starterObj = teamPlayers.find(p => p.name.toLowerCase() === starterName);
            const starterStarts = starterObj ? (starterObj.starts_2627 || 0) : 0;
            const subStarts = sub.starts_2627 || 0;
            const totalStarts = starterStarts + subStarts;
            if (totalStarts > 0) {
                const realPct = Math.round((starterStarts / totalStarts) * 100);
                const presets = [100, 85, 75, 65, 50];
                slot.pct = presets.reduce((prev, curr) =>
                    Math.abs(curr - realPct) < Math.abs(prev - realPct) ? curr : prev
                );
            } else {
                const starterTit = starterObj ? (starterObj.titolarita || 50) : 50;
                if (starterTit >= 90) slot.pct = 100;
                else if (starterTit >= 80) slot.pct = 85;
                else if (starterTit >= 70) slot.pct = 75;
                else if (starterTit >= 55) slot.pct = 65;
                else slot.pct = 50;
            }
        } else {
            slot.subName = '';
            slot.subRole = role;
            slot.pct = 100;
        }
    });
}
function _saveFromSlots(teamName, team) {
    const moduloEl = document.getElementById('editorModuloSelect');
    const newModulo = moduloEl ? moduloEl.value : (team.modulo || '3-5-2');
    const newLineup = window.currentEditorSlots.map(s => {
        let statusText = s.pct >= 95 ? 'Titolare Inamovibile (100% Tit)' : `Titolare (${s.pct}% vs ${s.subName || 'Sub'} ${100 - s.pct}%)`;
        return {
            pos: s.pos, pos_label: s.pos_label,
            name: s.starterName, role: s.starterRole,
            sub_name: s.subName || null, sub_role: s.subRole || s.starterRole,
            status: statusText, pct: s.pct,
            fpp_fpn: s.fpp_fpn || 'NONE', oop: !!s.oop,
            oop_type: s.oop_type, oop_desc: s.oop_desc
        };
    });
    const newBallottaggi = [];
    newLineup.forEach(lp => {
        if (lp.sub_name && lp.pct < 95) {
            newBallottaggi.push({ player: lp.name, pct: lp.pct, vs: `${lp.sub_name} (${100 - lp.pct}%)` });
            newBallottaggi.push({ player: lp.sub_name, pct: 100 - lp.pct, vs: `${lp.name} (${lp.pct}%)` });
        }
    });
    const updatedTeam = { ...team, modulo: newModulo, lineup: newLineup, ballottaggi: newBallottaggi };
    TACTICAL_DB[teamName] = updatedTeam;
    if (!window.CUSTOM_TACTICAL_DB) window.CUSTOM_TACTICAL_DB = {};
    window.CUSTOM_TACTICAL_DB[teamName] = updatedTeam;
    try {
        localStorage.setItem('FANTA_TACTICAL_DB_CUSTOM', JSON.stringify(window.CUSTOM_TACTICAL_DB));
    } catch(e) {}
    applyTacticalChangesToPlayers(teamName, updatedTeam);
}