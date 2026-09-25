let currentTopFlopRound = 4;
function setTopFlopRound(roundNum) {
    currentTopFlopRound = parseInt(roundNum, 10) || 4;
    renderTopFlopView();
}
function renderTopFlopView() {
    const container = document.getElementById('viewTopFlop');
    if (!container) return;
    const data = (typeof TOP_FLOP_DATA !== 'undefined') ? TOP_FLOP_DATA : {};
    const availableRounds = Object.keys(data).map(k => parseInt(k, 10)).sort((a, b) => a - b);
    if (!currentTopFlopRound || !data[currentTopFlopRound]) {
        currentTopFlopRound = availableRounds.length > 0 ? availableRounds[availableRounds.length - 1] : 4;
    }
    const roundInfo = data[currentTopFlopRound] || { top: [], flop: [], total_players_voted: 0 };
    const topList = roundInfo.top || [];
    const flopList = roundInfo.flop || [];
    const roundButtonsHtml = availableRounds.map(r => {
        const isCurrent = (r === currentTopFlopRound);
        return `
            <button class="btn-action ${isCurrent ? 'active' : ''}" 
                    style="${isCurrent ? 'background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#031327;font-weight:900;box-shadow:0 0 12px rgba(0,242,254,0.4);' : 'background:rgba(255,255,255,0.05);color:var(--text-secondary);border:1px solid rgba(255,255,255,0.1);'}padding:7px 16px;border-radius:8px;font-size:12.5px;cursor:pointer;transition:all 0.15s ease;" 
                    onclick="setTopFlopRound(${r})">
                Giornata ${r} ${r === availableRounds[availableRounds.length - 1] ? '🔥 (Ultima)' : ''}
            </button>
        `;
    }).join('');
    const topCardsHtml = topList.map((p, idx) => {
        const roleClass = p.role || 'C';
        const teamText = p.team ? `${p.role} - ${p.team}` : p.role;
        const commentText = p.commento || p.motivo || 'Prestazione di altissimo livello.';
        return `
            <div class="top-flop-row top-row" 
                 onclick="openPlayerProfileModal(${p.cod})" 
                 title="Clicca per aprire la scheda di ${p.name}" 
                 style="cursor:pointer;padding:12px 14px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.22);border-radius:12px;margin-bottom:10px;transition:all 0.2s ease;">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
                    <div style="display:flex;align-items:flex-start;gap:10px;flex:1;">
                        <span style="font-size:14px;font-weight:900;color:#10b981;width:24px;text-align:center;margin-top:2px;">#${idx + 1}</span>
                        <span class="role-badge ${roleClass}" style="font-size:11px;padding:2px 7px;margin-top:2px;">${p.role}</span>
                        <div style="flex:1;">
                            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                <span style="font-size:14px;font-weight:800;color:#fff;" class="player-link">${p.name}</span>
                                <span style="font-size:11.5px;color:var(--text-muted);font-weight:600;">(${teamText})</span>
                                <span style="font-size:11px;background:rgba(16,185,129,0.2);color:#34d399;padding:1px 6px;border-radius:4px;font-weight:700;">✨ ${p.motivo}</span>
                            </div>
                            <!-- Commento Giornalistico / Fantacalcistico -->
                            <div style="margin-top:6px;font-size:12px;color:#d1fae5;line-height:1.45;background:rgba(0,0,0,0.3);padding:7px 10px;border-radius:7px;border-left:3px solid #10b981;">
                                “${commentText}”
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;min-width:90px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="text-align:right;">
                                <span style="font-size:9.5px;color:var(--text-muted);text-transform:uppercase;display:block;">Voto</span>
                                <b style="font-size:13.5px;color:#e2e8f0;">${p.voto}</b>
                            </div>
                            <div style="text-align:right;background:rgba(16,185,129,0.2);padding:3px 8px;border-radius:6px;border:1px solid rgba(16,185,129,0.45);">
                                <span style="font-size:9px;color:#34d399;text-transform:uppercase;display:block;font-weight:700;">FantaVoto</span>
                                <b style="font-size:15px;color:#10b981;font-weight:900;">${p.fantavoto}</b>
                            </div>
                        </div>
                        <div style="font-size:10.5px;color:var(--accent-cyan);display:flex;align-items:center;gap:4px;opacity:0.85;margin-top:2px;">
                            <span>Apri scheda</span> <span style="font-size:11px;">➔</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    const flopCardsHtml = flopList.map((p, idx) => {
        const roleClass = p.role || 'C';
        const teamText = p.team ? `${p.role} - ${p.team}` : p.role;
        const commentText = p.commento || p.motivo || 'Prestazione insufficiente.';
        return `
            <div class="top-flop-row flop-row" 
                 onclick="openPlayerProfileModal(${p.cod})" 
                 title="Clicca per aprire la scheda di ${p.name}" 
                 style="cursor:pointer;padding:12px 14px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.22);border-radius:12px;margin-bottom:10px;transition:all 0.2s ease;">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
                    <div style="display:flex;align-items:flex-start;gap:10px;flex:1;">
                        <span style="font-size:14px;font-weight:900;color:#f87171;width:24px;text-align:center;margin-top:2px;">#${idx + 1}</span>
                        <span class="role-badge ${roleClass}" style="font-size:11px;padding:2px 7px;margin-top:2px;">${p.role}</span>
                        <div style="flex:1;">
                            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                <span style="font-size:14px;font-weight:800;color:#fff;" class="player-link">${p.name}</span>
                                <span style="font-size:11.5px;color:var(--text-muted);font-weight:600;">(${teamText})</span>
                                <span style="font-size:11px;background:rgba(239,68,68,0.2);color:#fca5a5;padding:1px 6px;border-radius:4px;font-weight:700;">⚠️ ${p.motivo}</span>
                            </div>
                            <!-- Commento Giornalistico / Fantacalcistico -->
                            <div style="margin-top:6px;font-size:12px;color:#fee2e2;line-height:1.45;background:rgba(0,0,0,0.3);padding:7px 10px;border-radius:7px;border-left:3px solid #ef4444;">
                                “${commentText}”
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;min-width:90px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="text-align:right;">
                                <span style="font-size:9.5px;color:var(--text-muted);text-transform:uppercase;display:block;">Voto</span>
                                <b style="font-size:13.5px;color:#e2e8f0;">${p.voto}</b>
                            </div>
                            <div style="text-align:right;background:rgba(239,68,68,0.2);padding:3px 8px;border-radius:6px;border:1px solid rgba(239,68,68,0.45);">
                                <span style="font-size:9px;color:#fca5a5;text-transform:uppercase;display:block;font-weight:700;">FantaVoto</span>
                                <b style="font-size:15px;color:#f87171;font-weight:900;">${p.fantavoto}</b>
                            </div>
                        </div>
                        <div style="font-size:10.5px;color:var(--accent-cyan);display:flex;align-items:center;gap:4px;opacity:0.85;margin-top:2px;">
                            <span>Apri scheda</span> <span style="font-size:11px;">➔</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    container.innerHTML = `
        <div class="top-flop-container" style="max-width:1240px;margin:0 auto;padding:16px 20px;">
            <!-- HEADER -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:14px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:36px;">⚡</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:22px;color:var(--accent-cyan);">Top & Flop Ufficiali Serie A</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            I migliori exploit con bonus e i tracolli fantacalcistici con commento dettagliato. Clicca su qualsiasi calciatore per aprire la sua scheda e analizzare l'andamento.
                        </div>
                    </div>
                </div>
                <!-- SELECTOR GIORNATA -->
                <div style="display:flex;align-items:center;gap:8px;background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:10px;border:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:11.5px;color:var(--text-muted);font-weight:700;margin-right:4px;">Seleziona Turno:</span>
                    ${roundButtonsHtml}
                </div>
            </div>
            <!-- RIEPILOGO TURNO BADGE -->
            <div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.02);padding:10px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);margin-bottom:20px;">
                <span style="font-size:13px;font-weight:800;color:#fff;">
                    📅 Analisi Dettagliata: <span style="color:var(--accent-cyan);">GIORNATA ${currentTopFlopRound}</span>
                </span>
                <span style="font-size:12px;color:var(--text-secondary);">
                    Calciatori a voto nel turno: <b style="color:#fff;">${roundInfo.total_players_voted}</b> &nbsp;•&nbsp; 
                    <span style="color:var(--accent-cyan);">💡 Clicca su un calciatore per aprire la scheda e vedere l'andamento</span>
                </span>
            </div>
            <!-- GRIGLIA 2 COLONNE: TOP (VERDE) & FLOP (ROSSO) -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                <!-- COLONNA TOP -->
                <div style="background:rgba(18,24,38,0.7);border:1px solid rgba(16,185,129,0.3);border-radius:14px;padding:18px;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;border-bottom:1px solid rgba(16,185,129,0.2);padding-bottom:10px;">
                        <span style="font-size:22px;">🔥</span>
                        <div>
                            <h3 style="margin:0;font-size:16px;font-weight:900;color:#34d399;">I MIGLIORI DELLA GIORNATA (UP)</h3>
                            <div style="font-size:11px;color:var(--text-muted);">Bonus gol, assist e voti top con commenti e pagelle</div>
                        </div>
                    </div>
                    ${topCardsHtml || '<div style="color:var(--text-muted);font-size:12px;">Nessun dato per questo turno.</div>'}
                </div>
                <!-- COLONNA FLOP -->
                <div style="background:rgba(18,24,38,0.7);border:1px solid rgba(239,68,68,0.3);border-radius:14px;padding:18px;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;border-bottom:1px solid rgba(239,68,68,0.2);padding-bottom:10px;">
                        <span style="font-size:22px;">❄️</span>
                        <div>
                            <h3 style="margin:0;font-size:16px;font-weight:900;color:#f87171;">I PEGGIORI DELLA GIORNATA (DOWN)</h3>
                            <div style="font-size:11px;color:var(--text-muted);">Insufficienze, malus, rigori falliti e disattenzioni</div>
                        </div>
                    </div>
                    ${flopCardsHtml || '<div style="color:var(--text-muted);font-size:12px;">Nessun dato per questo turno.</div>'}
                </div>
            </div>
        </div>
    `;
}
window.setTopFlopRound = setTopFlopRound;
window.renderTopFlopView = renderTopFlopView;