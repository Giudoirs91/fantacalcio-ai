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
document.addEventListener('click', (e) => {
    const searchContainer = document.querySelector('.ai-hub-search-wrap');
    const resEl = document.getElementById('hubSearchResults');
    if (searchContainer && resEl && !searchContainer.contains(e.target)) {
        resEl.style.display = 'none';
    }
});
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
    const healthyTop = evaluated.filter(e => !e.player.is_injured && (e.player.titolarita || 70) >= 70 && e.player.role !== 'P')
                        .sort((a, b) => b.score - a.score);
    const topPick = healthyTop[0] || evaluated[0];
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
    const gemCandidates = evaluated.filter(e => {
        const p = e.player;
        const fvm = p.fvm || 15;
        const tit = p.titolarita || 70;
        return !p.is_injured && fvm <= 18 && tit >= 50;
    }).sort((a, b) => b.score - a.score);
    const gemPick = gemCandidates[0] || evaluated[0];
    const p1 = topPick.player;
    const fix1 = topPick.fixture ? topPick.fixture.shortLabel : 'Match G' + roundNum;
    const confidence1 = Math.min(99, Math.max(88, Math.round((topPick.score / 92) * 100)));
    const p2 = flopPick.player;
    const fix2 = flopPick.fixture ? (flopPick.fixture.isHome ? `vs ${flopPick.fixture.opp}` : `@ ${flopPick.fixture.opp}`) : 'Big Match';
    const diff2 = (Math.max(3.8, Math.min(4.9, 5.0 - (flopPick.score / 25)))).toFixed(1);
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
function renderHomeLeaders() {
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS) || PLAYERS.length === 0) return;
    const grid = document.getElementById('homeLeadersGrid');
    if (!grid) return;
    const roleMap = { 'P': 'Portiere', 'D': 'Difensore', 'C': 'Centrocampista', 'A': 'Attaccante' };
    const categories = [
        {
            title: '⚽ Più Gol Segnati',
            key: p => Number(p.gol_2627 !== undefined ? p.gol_2627 : (p.gol || 0)),
            minPres: 0,
            valStr: v => Math.round(v),
            sub: p => `${p.team || ''} • ${p.role_desc || roleMap[p.role] || 'Attaccante'}`,
            runner: (p, v) => `${p.name} (${p.team}, ${Math.round(v)} gol)`
        },
        {
            title: '🎯 Più Assist Forniti',
            key: p => Number(p.assist_2627 !== undefined ? p.assist_2627 : (p.assist || 0)),
            minPres: 0,
            valStr: v => Math.round(v),
            sub: p => `${p.team || ''} • ${p.role_desc || roleMap[p.role] || 'Centrocampista'}`,
            runner: (p, v) => `${p.name} (${p.team}, ${Math.round(v)} assist)`
        },
        {
            title: '⚡ Più xGoals (xG)',
            key: p => Number(p.xg_2627 !== undefined ? p.xg_2627 : (p.xg || 0)),
            minPres: 0,
            valStr: v => v.toFixed(1),
            sub: p => `${p.team || ''} • ${p.role_desc || roleMap[p.role] || 'Attaccante'}`,
            runner: (p, v) => `${p.name} (${p.team}, ${v.toFixed(1)} xG)`
        },
        {
            title: '🎨 Più xAssists (xA)',
            key: p => Number(p.xa_2627 !== undefined ? p.xa_2627 : (p.xa || 0)),
            minPres: 0,
            valStr: v => v.toFixed(1),
            sub: p => `${p.team || ''} • ${p.role_desc || roleMap[p.role] || 'Centrocampista'}`,
            runner: (p, v) => `${p.name} (${p.team}, ${v.toFixed(1)} xA)`
        },
        {
            title: '⭐ Miglior FantaMedia (FM)',
            key: p => Number(p.fm_2627 !== undefined ? p.fm_2627 : (p.fm || 0)),
            minPres: 4,
            valStr: v => v.toFixed(2),
            sub: p => `${p.team || ''} • FM ${Number(p.fm_2627 || p.fm || 0).toFixed(2)} (${Number(p.presenze_2627 || p.presenze || 0)} presenze)`,
            runner: (p, v) => `${p.name} (${p.team}, ${v.toFixed(2)} FM)`
        },
        {
            title: '💎 Più Bonus Totali (+Gol & +Assist)',
            key: p => Number(p.tot_bonus_2627 !== undefined ? p.tot_bonus_2627 : ((p.gol_2627 || 0) * 3 + (p.assist_2627 || 0))),
            minPres: 0,
            valStr: v => `+${v.toFixed(1)}`,
            sub: p => `${p.team || ''} • ${Number(p.gol_2627 || 0)} gol, ${Number(p.assist_2627 || 0)} assist (+${Number(p.tot_bonus_2627 || 0).toFixed(1)} pt)`,
            runner: (p, v) => `${p.name} (+${v.toFixed(1)} bonus)`
        }
    ];
    const cardsHtml = categories.map(cat => {
        const pool = PLAYERS.filter(p => Number(p.presenze_2627 || p.presenze || 0) >= cat.minPres);
        pool.sort((a, b) => cat.key(b) - cat.key(a));
        const top1 = pool[0];
        if (!top1) return '';
        const val1 = cat.key(top1);
        const p2 = pool[1];
        const p3 = pool[2];
        const r2Str = p2 ? `<span onclick="event.stopPropagation(); if (typeof openPlayerProfileModal==='function') openPlayerProfileModal(${p2.id});" style="cursor:pointer;" title="Vedi scheda ${p2.name}">2° ${cat.runner(p2, cat.key(p2))}</span>` : '';
        const r3Str = p3 ? `<span onclick="event.stopPropagation(); if (typeof openPlayerProfileModal==='function') openPlayerProfileModal(${p3.id});" style="cursor:pointer;" title="Vedi scheda ${p3.name}">3° ${cat.runner(p3, cat.key(p3))}</span>` : '';
        const runnersHtml = [r2Str, r3Str].filter(Boolean).join(' • ');
        const ovrClass = typeof getOvrClass === 'function' ? getOvrClass(top1.ovr) : 'ovr-tier-good';
        return `
            <div class="leader-card" onclick="openPlayerProfileModal(${top1.id})" style="cursor:pointer;" title="Clicca per aprire la scheda di ${top1.name}">
                <div class="leader-card-header">
                    <span class="leader-stat-badge">${cat.title}</span>
                    <span class="leader-val">${cat.valStr(val1)}</span>
                </div>
                <div class="leader-player-info">
                    <span class="role-badge ${top1.role}">${top1.role}</span>
                    <div>
                        <div class="leader-player-name">${top1.name} <span class="ovr-pill ${ovrClass}" style="font-size:10px;margin-left:4px;">OVR ${top1.ovr || '-'}</span></div>
                        <div class="leader-player-team">${cat.sub(top1)}</div>
                    </div>
                </div>
                <div class="leader-podium">
                    <strong>Inseguitori:</strong> ${runnersHtml}
                </div>
            </div>
        `;
    }).join('\n');
    grid.innerHTML = cardsHtml;
}
let _heroSlideIndex = 0;
let _heroSlideTimer = null;
function switchHeroSlide(idx) {
    _heroSlideIndex = idx;
    const s0 = document.getElementById('heroSlide0');
    const s1 = document.getElementById('heroSlide1');
    const t0 = document.getElementById('heroTab0');
    const t1 = document.getElementById('heroTab1');
    const d0 = document.getElementById('heroDot0');
    const d1 = document.getElementById('heroDot1');
    if (!s0 || !s1) return;
    if (idx === 0) {
        s0.classList.add('active');
        s1.classList.remove('active');
        if (t0) t0.classList.add('active');
        if (t1) t1.classList.remove('active');
        if (d0) d0.classList.add('active');
        if (d1) d1.classList.remove('active');
    } else {
        s1.classList.add('active');
        s0.classList.remove('active');
        if (t1) t1.classList.add('active');
        if (t0) t0.classList.remove('active');
        if (d1) d1.classList.add('active');
        if (d0) d0.classList.remove('active');
    }
}
function startHeroSlideAutoplay() {
    if (_heroSlideTimer) clearInterval(_heroSlideTimer);
    _heroSlideTimer = setInterval(() => {
        const next = _heroSlideIndex === 0 ? 1 : 0;
        switchHeroSlide(next);
    }, 6000);
}
function initHeroSlider() {
    const slider = document.getElementById('heroSocialSlider');
    if (!slider) return;
    slider.addEventListener('mouseenter', () => {
        if (_heroSlideTimer) clearInterval(_heroSlideTimer);
    });
    slider.addEventListener('mouseleave', () => {
        startHeroSlideAutoplay();
    });
    startHeroSlideAutoplay();
}
window.switchHeroSlide = switchHeroSlide;
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            renderLiveIntelligencePulseCards();
            renderHomeLeaders();
            initHeroSlider();
        }, 150);
    });
}