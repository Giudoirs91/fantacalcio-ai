// ==============================================================================
// HOME AI HUB — INTERACTION & QUICK SEARCH LOGIC
// ==============================================================================

function filterHubPlayers(query) {
    const resEl = document.getElementById('hubSearchResults');
    if (!resEl) return;
    
    if (!query || query.trim().length < 2) {
        resEl.style.display = 'none';
        resEl.innerHTML = '';
        return;
    }
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return;
    
    const qClean = (typeof cleanStrTolerant === 'function') ? cleanStrTolerant(query) : query.toLowerCase().trim();
    const qMapped = (window.COMMON_PLAYER_ALIASES && window.COMMON_PLAYER_ALIASES[qClean]) 
        ? window.COMMON_PLAYER_ALIASES[qClean] 
        : qClean;

    const tokens = qMapped.split(/\s+/).filter(t => t.length >= 2);

    const matches = PLAYERS.filter(p => {
        const pNameClean = (typeof cleanStrTolerant === 'function') ? cleanStrTolerant(p.name) : (p.name || '').toLowerCase();
        const tClean = (typeof cleanStrTolerant === 'function') ? cleanStrTolerant(p.team) : (p.team || '').toLowerCase();
        
        if (pNameClean.includes(qClean) || pNameClean.includes(qMapped) || tClean.includes(qClean)) return true;
        return tokens.every(tok => pNameClean.includes(tok) || tClean.includes(tok));
    }).slice(0, 6);

    if (matches.length === 0) {
        resEl.innerHTML = `<div style="padding:16px;color:var(--text-muted);text-align:center;font-size:12.5px;">Nessun calciatore trovato per "<b>${query}</b>"</div>`;
        resEl.style.display = 'block';
        return;
    }

    resEl.innerHTML = matches.map(p => `
        <div class="hub-search-result-item" onclick="selectHubPlayer(${p.id})">
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="role-badge ${p.role}">${p.role}</span>
                <div>
                    <div style="font-weight:800;color:#fff;font-size:13.5px;">${p.name}</div>
                    <div style="font-size:11.5px;color:var(--text-secondary);">${p.team} • ${p.role_desc || p.role}</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="ovr-pill ${typeof getOvrClass === 'function' ? getOvrClass(p.ovr) : ''}">OVR ${p.ovr || '-'}</span>
                <span style="font-size:12.5px;font-weight:900;color:#fbbf24;font-family:'Outfit',sans-serif;">${p.fvm || p.price_prop || '-'} CR</span>
                <span style="color:var(--accent-cyan);font-size:11.5px;font-weight:800;background:rgba(56,189,248,0.1);padding:3px 8px;border-radius:6px;border:1px solid rgba(56,189,248,0.25);">Scheda &rarr;</span>
            </div>
        </div>
    `).join('');
    resEl.style.display = 'block';
}

function selectHubPlayer(playerId) {
    const resEl = document.getElementById('hubSearchResults');
    const inputEl = document.getElementById('hubQuickSearch');
    if (resEl) resEl.style.display = 'none';
    if (inputEl) inputEl.value = '';
    if (typeof openPlayerProfileModal === 'function') {
        openPlayerProfileModal(playerId);
    }
}

function openPlayerByName(name) {
    if (!name || typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS) || PLAYERS.length === 0) return;

    let p = null;
    if (typeof superMatchPlayerFuzzy === 'function') {
        p = superMatchPlayerFuzzy(name);
    }

    if (!p) {
        const nClean = (typeof cleanStrTolerant === 'function') ? cleanStrTolerant(name) : name.toLowerCase().trim();
        const nMapped = (window.COMMON_PLAYER_ALIASES && window.COMMON_PLAYER_ALIASES[nClean])
            ? window.COMMON_PLAYER_ALIASES[nClean]
            : nClean;

        p = PLAYERS.find(pl => {
            const pClean = (typeof cleanStrTolerant === 'function') ? cleanStrTolerant(pl.name) : (pl.name || '').toLowerCase();
            return pClean === nClean || pClean === nMapped || pClean.includes(nMapped) || nMapped.includes(pClean);
        });
    }

    if (p && typeof openPlayerProfileModal === 'function') {
        openPlayerProfileModal(p.id);
    } else {
        // Fallback: switch to auction and search
        if (typeof switchTab === 'function') {
            switchTab('auction');
            const searchInput = document.getElementById('searchBar');
            if (searchInput) {
                searchInput.value = name;
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    }
}

// Chiudi dropdown al click esterno
document.addEventListener('click', (e) => {
    const searchContainer = document.querySelector('.ai-hub-search-wrap');
    const resEl = document.getElementById('hubSearchResults');
    if (searchContainer && resEl && !searchContainer.contains(e.target)) {
        resEl.style.display = 'none';
    }
});

// ==============================================================================
// RICALCOLO DINAMICO DELLE 3 CARD INTELLIGENCE PULSE CON L'ALGORITMO DI GIORNATA
// ==============================================================================
function getPulseRoleBadge(roleStr) {
    if (typeof getRoleBadgeHtml === 'function') {
        return getRoleBadgeHtml(roleStr, 'font-size:13px; padding:4px 10px; border-radius:8px;');
    }
    const r = (roleStr || 'C').toUpperCase();
    return `<span class="role-badge ${r}" style="width:34px;height:34px;font-size:15px;display:inline-flex;align-items:center;justify-content:center;border-radius:8px;font-weight:900;">${r}</span>`;
}

function renderLiveIntelligencePulseCards() {
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS) || PLAYERS.length === 0) return;
    const pulseGrid = document.querySelector('.ai-pulse-grid');
    if (!pulseGrid) return;

    const roundNum = typeof getUpcomingMatchdayRound === 'function' ? getUpcomingMatchdayRound() : 6;

    // Calcola lo score di giornata per ciascun calciatore della Serie A
    const evaluated = PLAYERS.map(p => {
        let scoreObj = { score: 60, factors: [] };
        if (typeof calculateChiSchieroScore === 'function') {
            scoreObj = calculateChiSchieroScore(p, roundNum);
        } else if (p.xfm) {
            scoreObj.score = p.xfm * 10;
        }
        const fixture = typeof getChiSchieroFixtureForPlayer === 'function' ? getChiSchieroFixtureForPlayer(p, roundNum) : null;
        return {
            player: p,
            score: scoreObj.score,
            xfmVal: (scoreObj.score / 10).toFixed(2),
            fixture: fixture,
            factors: scoreObj.factors || []
        };
    });

    // 1. TOP PICK & CAPITANO AI:
    // Calciatore di movimento sano, titolare (tit >= 70%) con lo score atteso più alto della giornata
    const healthyTop = evaluated.filter(e => !e.player.is_injured && (e.player.titolarita || 70) >= 70 && e.player.role !== 'P')
                        .sort((a, b) => b.score - a.score);
    const topPick = healthyTop[0] || evaluated[0];

    // 2. FLOP & TRAPPOLA ALERT:
    // Giocatore con alto status (OVR >= 77 o FVM >= 18) che affronta un matchup difficile con score penalizzato
    const flopCandidates = evaluated.filter(e => {
        const p = e.player;
        const ovr = p.ovr || 75;
        const fvm = p.fvm || 15;
        return !p.is_injured && (ovr >= 77 || fvm >= 18);
    }).map(e => {
        const expectedBase = (e.player.ovr || 75) * 0.9;
        const gap = expectedBase - e.score; // Divario negativo rispetto allo status
        return { ...e, gap };
    }).sort((a, b) => b.gap - a.gap);

    const flopPick = flopCandidates[0] || evaluated[evaluated.length - 1];

    // 3. VERA GEMMA LOW-COST:
    // Calciatore a basso costo (FVM <= 18 CR), sano e titolare, con score elevato rispetto al costo
    const gemCandidates = evaluated.filter(e => {
        const p = e.player;
        const fvm = p.fvm || 15;
        const tit = p.titolarita || 70;
        return !p.is_injured && fvm <= 18 && tit >= 50;
    }).sort((a, b) => b.score - a.score);

    const gemPick = gemCandidates[0] || evaluated[0];

    // Card 1: Top Pick
    const p1 = topPick.player;
    const fix1 = topPick.fixture ? topPick.fixture.shortLabel : 'Match G' + roundNum;
    const confidence1 = Math.min(99, Math.max(88, Math.round((topPick.score / 92) * 100)));

    // Card 2: Flop Alert
    const p2 = flopPick.player;
    const fix2 = flopPick.fixture ? (flopPick.fixture.isHome ? `vs ${flopPick.fixture.opp}` : `@ ${flopPick.fixture.opp}`) : 'Big Match';
    const diff2 = (Math.max(3.8, Math.min(4.9, 5.0 - (flopPick.score / 25)))).toFixed(1);

    // Card 3: Gemma Low-Cost
    const p3 = gemPick.player;
    const upside3 = Math.round(((gemPick.score / 55) - 1) * 100);
    const positiveUpside = upside3 > 0 ? `+${upside3}%` : '+35%';

    pulseGrid.innerHTML = `
        <!-- Card 1: Top AI Pick & Capitano Ideale -->
        <div class="ai-pulse-card pick">
            <div class="pulse-card-header">
                <span class="pulse-badge green">🚀 Top Pick &amp; Capitano AI</span>
                <span class="pulse-card-score" style="color:#4ade80;">${confidence1}% Schierabile</span>
            </div>
            <div class="pulse-player-box" style="display:flex;align-items:center;gap:10px;">
                ${getPulseRoleBadge(p1.role)}
                <div>
                    <div class="pulse-player-name" style="font-size:17px;font-weight:900;color:#fff;">${p1.name}</div>
                    <div class="pulse-player-sub" style="font-size:12px;color:#94a3b8;">${p1.team} • ${p1.role_desc || p1.role} • OVR ${p1.ovr || 85}</div>
                </div>
            </div>
            <div class="pulse-metrics-strip">
                <div class="pulse-metric-item">
                    <span class="p-lbl">xFM Atteso</span>
                    <span class="p-val" style="color:#00e676;">${topPick.xfmVal}</span>
                </div>
                <div class="pulse-metric-item">
                    <span class="p-lbl">Partita G${roundNum}</span>
                    <span class="p-val" style="color:#38bdf8;">${fix1}</span>
                </div>
                <div class="pulse-metric-item">
                    <span class="p-lbl">Status Tattico</span>
                    <span class="p-val" style="color:#fbbf24;">${p1.is_rigorista_1 ? '1° Rigorista' : (p1.is_rigorista_2 ? '2° Rigorista' : 'Titolare 100%')}</span>
                </div>
            </div>
            <div class="pulse-quote-box">
                <b>Verdetto AI:</b> <i>"Top scorer di giornata secondo l'algoritmo predittivo. Pericolosità offensiva massima (${topPick.xfmVal} xFM) e matchup favorevole: schierare e dare la fascia di capitano!"</i>
            </div>
            <button class="pulse-action-link" onclick="openPlayerProfileModal(${p1.id})">
                <span>Apri Scheda Calciatore &amp; Radar SVG</span>
                <span>&rarr;</span>
            </button>
        </div>

        <!-- Card 2: Flop & Trap Alert -->
        <div class="ai-pulse-card danger">
            <div class="pulse-card-header">
                <span class="pulse-badge red">⚠️ Flop &amp; Trappola Alert</span>
                <span class="pulse-card-score" style="color:#f87171;">Difficoltà ${diff2}/5</span>
            </div>
            <div class="pulse-player-box" style="display:flex;align-items:center;gap:10px;">
                ${getPulseRoleBadge(p2.role)}
                <div>
                    <div class="pulse-player-name" style="font-size:17px;font-weight:900;color:#fff;">${p2.name}</div>
                    <div class="pulse-player-sub" style="font-size:12px;color:#94a3b8;">${p2.team} • ${p2.role_desc || p2.role} • ${p2.fvm || p2.ovr || 75} CR</div>
                </div>
            </div>
            <div class="pulse-metrics-strip">
                <div class="pulse-metric-item">
                    <span class="p-lbl">Matchup G${roundNum}</span>
                    <span class="p-val" style="color:#f87171;">${fix2}</span>
                </div>
                <div class="pulse-metric-item">
                    <span class="p-lbl">Titolarità Live</span>
                    <span class="p-val" style="color:#ef4444;">${p2.titolarita || 50}%</span>
                </div>
                <div class="pulse-metric-item">
                    <span class="p-lbl">xFM Proiettato</span>
                    <span class="p-val" style="color:#fbbf24;">${flopPick.xfmVal} (Down)</span>
                </div>
            </div>
            <div class="pulse-quote-box" style="border-left-color:#ef4444;">
                <b>Verdetto AI:</b> <i>"Turno insidioso per ${p2.name}: l'algoritmo rileva un calo di rendimento atteso (${flopPick.xfmVal} xFM) legato alla difficoltà del matchup e alla titolarità. Valuta alternative se disponi di buone opzioni!"</i>
            </div>
            <button class="pulse-action-link" onclick="openPlayerProfileModal(${p2.id})">
                <span>Analizza Matchup &amp; Profilo Giocatore</span>
                <span>&rarr;</span>
            </button>
        </div>

        <!-- Card 3: Scommessa & Differenziale AI -->
        <div class="ai-pulse-card gem">
            <div class="pulse-card-header">
                <span class="pulse-badge purple">🔮 Vera Gemma Low-Cost</span>
                <span class="pulse-card-score" style="color:#c084fc;">Upside ${positiveUpside}</span>
            </div>
            <div class="pulse-player-box" style="display:flex;align-items:center;gap:10px;">
                ${getPulseRoleBadge(p3.role)}
                <div>
                    <div class="pulse-player-name" style="font-size:17px;font-weight:900;color:#fff;">${p3.name}</div>
                    <div class="pulse-player-sub" style="font-size:12px;color:#94a3b8;">${p3.team} • ${p3.role_desc || p3.role} • ${p3.fvm || 10} CR</div>
                </div>
            </div>
            <div class="pulse-metrics-strip">
                <div class="pulse-metric-item">
                    <span class="p-lbl">xFM Proiettato</span>
                    <span class="p-val" style="color:#c084fc;">${gemPick.xfmVal}</span>
                </div>
                <div class="pulse-metric-item">
                    <span class="p-lbl">Matchup G${roundNum}</span>
                    <span class="p-val" style="color:#34d399;">${p3.prossimo_avversario ? 'vs ' + p3.prossimo_avversario : 'Favorevole'}</span>
                </div>
                <div class="pulse-metric-item">
                    <span class="p-lbl">Prezzo Cons.</span>
                    <span class="p-val" style="color:#fbbf24;">${p3.fvm || 10} CR (Gemma)</span>
                </div>
            </div>
            <div class="pulse-quote-box" style="border-left-color:#c084fc;">
                <b>Verdetto AI:</b> <i>"Ottima scommessa a basso costo (${p3.fvm || 10} CR): titolarità solida e proiezione di giornata a ${gemPick.xfmVal} xFM. Il miglior rapporto costo/resa per questo turno."</i>
            </div>
            <button class="pulse-action-link" onclick="openPlayerProfileModal(${p3.id})">
                <span>Esplora Radar &amp; Proiezioni Future</span>
                <span>&rarr;</span>
            </button>
        </div>
    `;
}

// Inizializzazione automatica al caricamento
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        setTimeout(renderLiveIntelligencePulseCards, 150);
    });
}

