// --- top_flop.js ---
// Vista Top & Flop per Giornata con navigazione fluida (Mobile & Desktop)
// Default automatico all'ultima giornata disputata, navigazione rapida tra tutti i turni
// e layout card a piena larghezza per smartphone con commenti completi e leggibili.

let currentTopFlopRound = null;
let topFlopActiveTab = 'ALL'; // 'ALL' | 'TOP' | 'FLOP'

function getAvailableTopFlopRounds() {
    const data = (typeof TOP_FLOP_DATA !== 'undefined' && TOP_FLOP_DATA) ? TOP_FLOP_DATA : {};
    const rounds = Object.keys(data).map(k => parseInt(k, 10)).filter(n => !isNaN(n)).sort((a, b) => a - b);
    return rounds.length > 0 ? rounds : [1, 2, 3, 4, 5, 6];
}

function setTopFlopRound(roundNum) {
    const num = parseInt(roundNum, 10);
    const available = getAvailableTopFlopRounds();
    if (available.includes(num)) {
        currentTopFlopRound = num;
        renderTopFlopView();
    }
}

function setTopFlopMobileTab(tab) {
    topFlopActiveTab = tab;
    const colTop = document.getElementById('tfColTop');
    const colFlop = document.getElementById('tfColFlop');
    const btnAll = document.getElementById('tfMobTabAll');
    const btnTop = document.getElementById('tfMobTabTop');
    const btnFlop = document.getElementById('tfMobTabFlop');

    if (btnAll) btnAll.classList.toggle('active', tab === 'ALL');
    if (btnTop) btnTop.classList.toggle('active', tab === 'TOP');
    if (btnFlop) btnFlop.classList.toggle('active', tab === 'FLOP');

    if (colTop) colTop.style.display = (tab === 'ALL' || tab === 'TOP') ? 'block' : 'none';
    if (colFlop) colFlop.style.display = (tab === 'ALL' || tab === 'FLOP') ? 'block' : 'none';
}

function renderTopFlopView() {
    const container = document.getElementById('viewTopFlop');
    if (!container) return;

    const data = (typeof TOP_FLOP_DATA !== 'undefined' && TOP_FLOP_DATA) ? TOP_FLOP_DATA : {};
    const availableRounds = getAvailableTopFlopRounds();
    const latestPlayedRound = availableRounds[availableRounds.length - 1];

    // Se non ancora impostato manualmente, controlla eventuale parametro URL ?giornata=X o ?g=X
    if (currentTopFlopRound === null) {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const rParam = urlParams.get('giornata') || urlParams.get('g');
            if (rParam) {
                const parsed = parseInt(rParam, 10);
                if (availableRounds.includes(parsed)) {
                    currentTopFlopRound = parsed;
                }
            }
        } catch (e) {}
    }

    // Se ancora nullo o non valido, default AUTOMATICO all'ULTIMA GIORNATA DISPUTATA
    if (currentTopFlopRound === null || !data[currentTopFlopRound]) {
        currentTopFlopRound = latestPlayedRound;
    }

    const roundInfo = data[currentTopFlopRound] || { top: [], flop: [], total_players_voted: 0 };
    const topList = roundInfo.top || [];
    const flopList = roundInfo.flop || [];

    // Tasti Precedente e Successivo
    const prevRound = currentTopFlopRound - 1;
    const nextRound = currentTopFlopRound + 1;
    const hasPrev = availableRounds.includes(prevRound);
    const hasNext = availableRounds.includes(nextRound);

    // Bottoni Pills orizzontali
    const roundPillsHtml = availableRounds.map(r => {
        const isCurrent = (r === currentTopFlopRound);
        const isLatest = (r === latestPlayedRound);
        return `
            <button class="tf-pill-btn ${isCurrent ? 'active' : ''}" 
                    data-round="${r}"
                    onclick="setTopFlopRound(${r})"
                    title="Visualizza Top & Flop Giornata ${r}">
                <span>G${r}</span>
                ${isLatest ? '<span class="tf-pill-badge-ultima">🔥 Ultima</span>' : ''}
            </button>
        `;
    }).join('');

    // Dropdown veloce per smartphone
    const selectOptionsHtml = availableRounds.map(r => {
        const isCurrent = (r === currentTopFlopRound);
        const isLatest = (r === latestPlayedRound);
        return `<option value="${r}" ${isCurrent ? 'selected' : ''}>⚽ Giornata ${r} ${isLatest ? '🔥 (Ultima Conclusa)' : '(Conclusa)'}</option>`;
    }).join('');

    // Render Cards TOP
    const topCardsHtml = topList.map((p, idx) => {
        const roleClass = p.role || 'C';
        const teamText = p.team ? `${p.role} • ${p.team}` : p.role;
        const commentText = p.commento || p.motivo || 'Prestazione di altissimo livello.';
        const matchLabel = p.match || (p.opponent ? `vs ${p.opponent}` : '');
        return `
            <div class="tf-card top-card" 
                 onclick="openPlayerProfileModal(${p.cod})" 
                 title="Clicca per aprire la scheda di ${p.name}">
                
                <!-- Intestazione Card: Dati Calciatore e Punteggi -->
                <div class="tf-card-header">
                    <div class="tf-card-player-group">
                        <span class="tf-rank-badge top-rank">#${idx + 1}</span>
                        <span class="role-badge ${roleClass}">${p.role}</span>
                        <div class="tf-name-and-club">
                            <span class="tf-player-name">${p.name}</span>
                            <span class="tf-player-club">${teamText}</span>
                        </div>
                    </div>

                    <div class="tf-card-scores-group">
                        <div class="tf-vote-pill">
                            <span class="tf-score-label">VOTO</span>
                            <span class="tf-vote-num">${p.voto}</span>
                        </div>
                        <div class="tf-fantavoto-pill top-fv">
                            <span class="tf-fv-label">FANTAVOTO</span>
                            <span class="tf-fv-num">${p.fantavoto}</span>
                        </div>
                    </div>
                </div>

                <!-- Dettaglio Bonus / Match -->
                <div class="tf-card-motivo-row">
                    <span class="tf-motivo-tag top-motivo">✨ ${p.motivo}</span>
                    ${matchLabel ? `<span class="tf-match-tag">(${matchLabel})</span>` : ''}
                </div>

                <!-- Commento Narrativo a Piena Larghezza -->
                <div class="tf-card-comment-box top-comment">
                    “${commentText}”
                </div>

                <!-- Link Scheda Calciatore -->
                <div class="tf-card-footer">
                    <span class="tf-card-footer-link">Apri scheda calciatore ➔</span>
                </div>
            </div>
        `;
    }).join('');

    // Render Cards FLOP
    const flopCardsHtml = flopList.map((p, idx) => {
        const roleClass = p.role || 'C';
        const teamText = p.team ? `${p.role} • ${p.team}` : p.role;
        const commentText = p.commento || p.motivo || 'Prestazione insufficiente.';
        const matchLabel = p.match || (p.opponent ? `vs ${p.opponent}` : '');
        return `
            <div class="tf-card flop-card" 
                 onclick="openPlayerProfileModal(${p.cod})" 
                 title="Clicca per aprire la scheda di ${p.name}">
                
                <!-- Intestazione Card: Dati Calciatore e Punteggi -->
                <div class="tf-card-header">
                    <div class="tf-card-player-group">
                        <span class="tf-rank-badge flop-rank">#${idx + 1}</span>
                        <span class="role-badge ${roleClass}">${p.role}</span>
                        <div class="tf-name-and-club">
                            <span class="tf-player-name">${p.name}</span>
                            <span class="tf-player-club">${teamText}</span>
                        </div>
                    </div>

                    <div class="tf-card-scores-group">
                        <div class="tf-vote-pill">
                            <span class="tf-score-label">VOTO</span>
                            <span class="tf-vote-num">${p.voto}</span>
                        </div>
                        <div class="tf-fantavoto-pill flop-fv">
                            <span class="tf-fv-label">FANTAVOTO</span>
                            <span class="tf-fv-num">${p.fantavoto}</span>
                        </div>
                    </div>
                </div>

                <!-- Dettaglio Malus / Match -->
                <div class="tf-card-motivo-row">
                    <span class="tf-motivo-tag flop-motivo">⚠️ ${p.motivo}</span>
                    ${matchLabel ? `<span class="tf-match-tag">(${matchLabel})</span>` : ''}
                </div>

                <!-- Commento Narrativo a Piena Larghezza -->
                <div class="tf-card-comment-box flop-comment">
                    “${commentText}”
                </div>

                <!-- Link Scheda Calciatore -->
                <div class="tf-card-footer">
                    <span class="tf-card-footer-link">Apri scheda calciatore ➔</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div class="top-flop-container">
            <!-- HEADER PRINCIPALE -->
            <div class="tf-header-card">
                <div class="tf-header-title-row">
                    <span class="tf-header-icon">⚡</span>
                    <div>
                        <h2 class="tf-header-h2">Top & Flop Ufficiali Serie A</h2>
                        <div class="tf-header-desc">
                            I migliori exploit con bonus e i tracolli fantacalcistici con pagelle e commento dettagliato.
                        </div>
                    </div>
                </div>

                <!-- BARRA NAVIGAZIONE GIORNATE (Prev / Scroll / Next) -->
                <div class="tf-nav-bar">
                    <button class="tf-nav-btn" 
                            ${!hasPrev ? 'disabled' : ''} 
                            onclick="setTopFlopRound(${prevRound})"
                            title="Vai alla giornata precedente">
                        ◀ Prec
                    </button>

                    <div class="tf-pills-scroll" id="tfPillsScroll">
                        ${roundPillsHtml}
                    </div>

                    <button class="tf-nav-btn" 
                            ${!hasNext ? 'disabled' : ''} 
                            onclick="setTopFlopRound(${nextRound})"
                            title="Vai alla giornata successiva">
                        Succ ▶
                    </button>
                </div>

                <!-- SELECTOR ALTERNATIVO PER SMARTPHONE -->
                <div class="tf-mobile-select-wrapper">
                    <select class="tf-mobile-round-select" onchange="setTopFlopRound(this.value)">
                        ${selectOptionsHtml}
                    </select>
                </div>
            </div>

            <!-- RIEPILOGO TURNO BADGE -->
            <div class="tf-meta-banner">
                <div class="tf-meta-left">
                    <span>📅 Verdetto Turno:</span>
                    <span class="tf-meta-round-tag">GIORNATA ${currentTopFlopRound}</span>
                    ${currentTopFlopRound === latestPlayedRound ? '<span class="tf-pill-badge-ultima">🔥 Ultima Conclusa</span>' : ''}
                </div>
                <div class="tf-meta-right">
                    Calciatori a voto: <b style="color:#fff;">${roundInfo.total_players_voted || 0}</b> &nbsp;•&nbsp;
                    <span style="color:var(--accent-cyan);">💡 Clicca su una scheda per aprirla</span>
                </div>
            </div>

            <!-- TAB SWITCHER MOBILE (Solo Top / Solo Flop / Tutti) -->
            <div class="tf-mobile-view-tabs">
                <button id="tfMobTabAll" class="tf-mob-tab-btn ${topFlopActiveTab === 'ALL' ? 'active' : ''}" onclick="setTopFlopMobileTab('ALL')">
                    ⚡ Tutti
                </button>
                <button id="tfMobTabTop" class="tf-mob-tab-btn top ${topFlopActiveTab === 'TOP' ? 'active' : ''}" onclick="setTopFlopMobileTab('TOP')">
                    🔥 Solo Top (UP)
                </button>
                <button id="tfMobTabFlop" class="tf-mob-tab-btn flop ${topFlopActiveTab === 'FLOP' ? 'active' : ''}" onclick="setTopFlopMobileTab('FLOP')">
                    ❄️ Solo Flop (DOWN)
                </button>
            </div>

            <!-- GRIGLIA 2 COLONNE: TOP (VERDE) & FLOP (ROSSO) -->
            <div class="tf-grid-columns">
                <!-- COLONNA TOP -->
                <div id="tfColTop" class="tf-column-box top-col" style="${(topFlopActiveTab === 'FLOP') ? 'display:none;' : ''}">
                    <div class="tf-col-header top-head">
                        <span style="font-size:24px;">🔥</span>
                        <div>
                            <h3 class="tf-col-title top-title">I MIGLIORI DELLA GIORNATA (UP)</h3>
                            <div class="tf-col-sub">Bonus gol, assist e voti top con commenti e pagelle</div>
                        </div>
                    </div>
                    ${topCardsHtml || '<div style="color:var(--text-muted);font-size:12.5px;padding:20px;text-align:center;">Nessun dato registrato per questo turno.</div>'}
                </div>

                <!-- COLONNA FLOP -->
                <div id="tfColFlop" class="tf-column-box flop-col" style="${(topFlopActiveTab === 'TOP') ? 'display:none;' : ''}">
                    <div class="tf-col-header flop-head">
                        <span style="font-size:24px;">❄️</span>
                        <div>
                            <h3 class="tf-col-title flop-title">I PEGGIORI DELLA GIORNATA (DOWN)</h3>
                            <div class="tf-col-sub">Insufficienze, malus, rigori falliti e disattenzioni</div>
                        </div>
                    </div>
                    ${flopCardsHtml || '<div style="color:var(--text-muted);font-size:12.5px;padding:20px;text-align:center;">Nessun dato registrato per questo turno.</div>'}
                </div>
            </div>
        </div>
    `;

    // Auto-scroll del pill attivo al centro del viewport orizzontale su smartphone
    try {
        setTimeout(() => {
            const activePill = container.querySelector('.tf-pill-btn.active');
            if (activePill && typeof activePill.scrollIntoView === 'function') {
                activePill.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            }
        }, 50);
    } catch (e) {}
}

window.setTopFlopRound = setTopFlopRound;
window.setTopFlopMobileTab = setTopFlopMobileTab;
window.renderTopFlopView = renderTopFlopView;
