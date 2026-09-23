// --- stats_seriea.js ---
// Pagina Statistiche & Leaderboard Serie A 2026/2027
// Include classifiche per: Gol, Assist, xG, xA, Gol Subiti Portieri, Clean Sheet,
// Bonus, Malus, Cartellini Gialli/Rossi, FantaMedia, Media Voto, Palle Recuperate e Big Chances.

let statsFilterRole = 'ALL';
let statsFilterTeam = 'ALL';
let statsSearchQuery = '';
let statsViewCategory = 'ALL'; // 'ALL', 'goals', 'assists', 'xg_xa', 'gk', 'bonus_malus', 'cards', 'ratings', 'advanced'
let statsLimit = 10; // 10, 20, 50

function setStatsCategory(cat) {
    statsViewCategory = cat;
    renderStatsSerieAView();
}

function setStatsLimit(lim) {
    statsLimit = parseInt(lim, 10) || 10;
    renderStatsSerieAView();
}

function renderStatsSerieAView() {
    const container = document.getElementById('viewStats');
    if (!container) return;

    if (typeof PLAYERS === 'undefined' || !PLAYERS || PLAYERS.length === 0) {
        container.innerHTML = `<div style="padding:40px;text-align:center;color:var(--text-muted);">Caricamento dati statistiche in corso...</div>`;
        return;
    }

    // Filtra la platea dei calciatori secondo i filtri globali della pagina
    let pool = PLAYERS.filter(p => {
        if (statsFilterRole !== 'ALL' && p.role !== statsFilterRole) return false;
        if (statsFilterTeam !== 'ALL' && p.team !== statsFilterTeam) return false;
        if (statsSearchQuery) {
            const q = statsSearchQuery.toLowerCase().trim();
            const nm = (p.name || '').toLowerCase();
            const tm = (p.team || '').toLowerCase();
            if (!nm.includes(q) && !tm.includes(q)) return false;
        }
        return true;
    });

    // Helper per costruire tabella classifica per una metrica
    const buildLeaderboardCard = (title, icon, subtitle, playerList, valExtractor, secDetailExtractor, highlightColor = 'var(--accent-cyan)', suffix = '', options = {}) => {
        const allowNegative = !!options.allowNegative;
        const sortAsc = !!options.sortAsc;
        const valFormatter = options.valFormatter || (v => `${v}${suffix}`);

        const sorted = playerList
            .filter(p => {
                const val = valExtractor(p);
                if (val === null || val === undefined || isNaN(val)) return false;
                if (!allowNegative && val <= 0) return false;
                return true;
            })
            .sort((a, b) => sortAsc ? (valExtractor(a) - valExtractor(b)) : (valExtractor(b) - valExtractor(a)))
            .slice(0, statsLimit);

        let rowsHtml = '';
        if (sorted.length === 0) {
            rowsHtml = `<div style="padding:16px;text-align:center;font-size:12px;color:var(--text-muted);">Nessun dato per i filtri selezionati.</div>`;
        } else {
            rowsHtml = sorted.map((p, idx) => {
                const rawVal = valExtractor(p);
                const displayVal = valFormatter(rawVal);
                const sec = secDetailExtractor ? secDetailExtractor(p) : '';
                let rankBadge = `<span style="font-size:11.5px;font-weight:900;color:var(--text-muted);width:26px;text-align:center;">#${idx + 1}</span>`;
                if (idx === 0) rankBadge = `<span style="font-size:14px;width:26px;text-align:center;">🥇</span>`;
                else if (idx === 1) rankBadge = `<span style="font-size:14px;width:26px;text-align:center;">🥈</span>`;
                else if (idx === 2) rankBadge = `<span style="font-size:14px;width:26px;text-align:center;">🥉</span>`;

                return `
                    <div class="stats-row" 
                         onclick="openPlayerProfileModal(${p.id})" 
                         title="Clicca per aprire la scheda di ${p.name}" 
                         style="cursor:pointer;display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-radius:8px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);margin-bottom:6px;transition:all 0.15s ease;">
                        <div style="display:flex;align-items:center;gap:8px;overflow:hidden;flex:1;min-width:0;">
                            ${rankBadge}
                            <span class="role-badge ${p.role}" style="font-size:10px;padding:1px 5px;">${p.role}</span>
                            <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                                <div style="font-size:13px;font-weight:800;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${p.name}</div>
                                <div style="font-size:10.5px;color:var(--text-muted);">${p.team}${sec ? ` • <span style="color:var(--text-secondary);">${sec}</span>` : ''}</div>
                            </div>
                        </div>

                        <div style="display:flex;align-items:center;gap:8px;padding-left:10px;">
                            <span style="font-size:16px;font-weight:900;color:${highlightColor};text-align:right;min-width:32px;letter-spacing:0.3px;">
                                ${displayVal}
                            </span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        return `
            <div class="stats-card" style="background:rgba(18,24,38,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;box-shadow:0 8px 24px rgba(0,0,0,0.35);">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.07);padding-bottom:10px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:20px;">${icon}</span>
                        <div>
                            <h3 style="margin:0;font-size:14.5px;font-weight:900;color:#fff;">${title}</h3>
                            <div style="font-size:10.5px;color:var(--text-muted);">${subtitle}</div>
                        </div>
                    </div>
                    <span style="font-size:10px;color:var(--text-muted);text-transform:uppercase;font-weight:700;">Top ${statsLimit}</span>
                </div>
                <div style="flex:1;display:flex;flex-direction:column;">
                    ${rowsHtml}
                </div>
            </div>
        `;
    };

    // 1. GOL (MARCATORI)
    const cardGoals = buildLeaderboardCard(
        'Classifica Marcatori', '⚽', 'Gol segnati in Serie A 2026/27',
        pool,
        p => p.gol_2627 || 0,
        p => `${p.presenze_2627 || 0} gare`,
        '#fbbf24', ''
    );

    // 2. ASSIST
    const cardAssists = buildLeaderboardCard(
        'Classifica Assist', '🪄', 'Assist vincenti forniti ai compagni',
        pool,
        p => p.assist_2627 || 0,
        p => `${p.presenze_2627 || 0} gare`,
        '#00f2fe', ''
    );

    // 3. EXPECTED GOALS (xG)
    const cardXg = buildLeaderboardCard(
        'Expected Goals (xG)', '🎯', 'Qualità e volume tiri generati',
        pool,
        p => p.xg_2627 !== null && p.xg_2627 !== undefined ? p.xg_2627 : (p.xg90_2627 ? parseFloat(p.xg90_2627) : 0),
        p => p.xg90_2627 ? `${p.xg90_2627} xG/90` : '',
        '#f472b6', ''
    );

    // 4. EXPECTED ASSISTS (xA)
    const cardXa = buildLeaderboardCard(
        'Expected Assists (xA)', '🪄', 'Pericolosità passaggi e occasioni create',
        pool,
        p => p.xa_2627 !== null && p.xa_2627 !== undefined ? p.xa_2627 : (p.xa90_2627 ? parseFloat(p.xa90_2627) : 0),
        p => p.xa90_2627 ? `${p.xa90_2627} xA/90` : '',
        '#38bdf8', ''
    );

    // 5. GOL SUBITI (PORTIERI)
    const poolGk = pool.filter(p => p.role === 'P');
    const cardGkGs = buildLeaderboardCard(
        'Gol Subiti (Portieri)', '🧤', 'Reti incassate complessive',
        poolGk,
        p => p.gol_subiti_2627 || 0,
        p => `CS: ${p.clean_sheets_2627 || 0} • Par: ${p.parate_2627 || 0}`,
        '#ef4444', ''
    );

    // 6. CLEAN SHEETS PORTIERI
    const cardGkCs = buildLeaderboardCard(
        'Clean Sheets (Portieri)', '🛡️', 'Partite a porta inviolata',
        poolGk,
        p => (p.clean_sheets_2627 !== undefined && p.clean_sheets_2627 > 0) ? p.clean_sheets_2627 : (p.clean_sheet_stat_2627 || 0),
        p => `${p.presenze_2627 || 0} gare • ${p.parate_2627 || 0} parate`,
        '#4ade80', ''
    );

    // 7. FANTABONUS TOTALI
    const cardBonus = buildLeaderboardCard(
        'Top FantaBonus (+)', '🎁', 'Punti bonus accumulati (+3 Gol, +1 Assist, +3 Rigore Par.)',
        pool,
        p => (p.tot_bonus_2627 !== undefined && p.tot_bonus_2627 > 0) ? p.tot_bonus_2627 : ((p.gol_2627 || 0) * 3 + (p.assist_2627 || 0)),
        p => `${p.gol_2627 || 0}G • ${p.assist_2627 || 0}A`,
        '#10b981', ' pt'
    );

    // 8. FANTAMALUS TOTALI
    const cardMalus = buildLeaderboardCard(
        'Top FantaMalus (-)', '⚠️', 'Punti malus subiti (Gol subiti, Rig. falliti, Amm, Esp, Aut)',
        pool,
        p => (p.tot_malus_2627 !== undefined && p.tot_malus_2627 > 0) ? p.tot_malus_2627 : ((p.gol_subiti_2627 || 0) + (p.amm_2627 || 0) * 0.5 + (p.esp_2627 || 0)),
        p => `${p.gol_subiti_2627 ? p.gol_subiti_2627 + ' GS • ' : ''}${p.amm_2627 || 0} Amm`,
        '#f87171', ' pt'
    );

    // 9. CARTELLINI GIALLI (AMMONIZIONI)
    const cardAmm = buildLeaderboardCard(
        'Cartellini Gialli', '🟨', 'Classifica ammonizioni Serie A',
        pool,
        p => p.amm_2627 || 0,
        p => `${p.falli_subiti_2627 || 0} falli subiti`,
        '#fbbf24', ''
    );

    // 10. CARTELLINI ROSSI (ESPULSIONI)
    const cardEsp = buildLeaderboardCard(
        'Cartellini Rossi', '🟥', 'Classifica espulsioni Serie A',
        pool,
        p => p.esp_2627 || 0,
        p => `${p.amm_2627 || 0} gialli`,
        '#ef4444', ''
    );

    // 11. FANTAMEDIA UFFICIALE (min 2 gare)
    const poolVoted2 = pool.filter(p => (p.presenze_2627 || p.partite_voto_2627 || 0) >= 2 || (p.minuti_stat_2627 || 0) >= 90);
    const getXfmObj = (p) => {
        if (p.xfm !== undefined && p.xfm !== null && p.delta_xfm !== undefined && p.delta_xfm !== null) {
            return { xfm: Number(p.xfm), delta: Number(p.delta_xfm) };
        }
        if (typeof computeExpectedFantaMedia === 'function') {
            const res = computeExpectedFantaMedia(p);
            return { xfm: Number(res.xfm), delta: Number(res.delta) };
        }
        return { xfm: 6.0, delta: 0.0 };
    };

    const cardFm = buildLeaderboardCard(
        'Top FantaMedia (FM)', '📈', 'Miglior rendimento con bonus (min. 2 gare)',
        poolVoted2,
        p => p.fm_2627 || 0,
        p => `${p.presenze_2627 || 0} gare a voto`,
        '#fbbf24', '',
        { valFormatter: v => Number(v).toFixed(2) }
    );

    // 11b. EXPECTED FANTAMEDIA (xFM)
    const cardXfm = buildLeaderboardCard(
        'Top Expected FantaMedia (xFM)', '🔮', 'FantaMedia attesa da modello xG/xA/Clean Sheet',
        poolVoted2,
        p => getXfmObj(p).xfm,
        p => `FM Reale: ${p.fm_2627 ? p.fm_2627.toFixed(2) : '-'} • ${p.presenze_2627 || 0} gare`,
        'var(--accent-cyan)', '',
        { valFormatter: v => Number(v).toFixed(2) }
    );

    // 11c. OCCASIONI DI MERCATO / SOTTO-PERFORMANCE (FM < xFM)
    const cardUnderperformers = buildLeaderboardCard(
        'Occasioni di Mercato (Sleeper 💎)', '💎', 'Producono tanto xG/xA ma hanno raccolto meno bonus (Da Comprare!)',
        poolVoted2.filter(p => getXfmObj(p).delta < -0.15),
        p => getXfmObj(p).delta,
        p => `xFM ${getXfmObj(p).xfm.toFixed(2)} vs FM ${p.fm_2627 ? p.fm_2627.toFixed(2) : '-'}`,
        '#fbbf24', '',
        { allowNegative: true, sortAsc: true, valFormatter: v => `${Number(v).toFixed(2)}` }
    );

    // 11d. RISCHIO REGRESSIONE / OVERPERFORMANCE (FM > xFM)
    const cardOverperformers = buildLeaderboardCard(
        'Rischio Regressione (Overperformance)', '⚠️', 'Hanno raccolto più bonus rispetto al volume di occasioni create',
        poolVoted2.filter(p => getXfmObj(p).delta > 0.15),
        p => getXfmObj(p).delta,
        p => `FM ${p.fm_2627 ? p.fm_2627.toFixed(2) : '-'} vs xFM ${getXfmObj(p).xfm.toFixed(2)}`,
        '#f87171', '',
        { allowNegative: true, sortAsc: false, valFormatter: v => `+${Number(v).toFixed(2)}` }
    );

    // 12. MEDIA VOTO PURA (min 2 gare)
    const cardMv = buildLeaderboardCard(
        'Top Media Voto (MV)', '📊', 'Miglior media voto dei pagellisti (senza bonus)',
        poolVoted2,
        p => p.mv_2627 || 0,
        p => `${p.presenze_2627 || 0} gare a voto`,
        '#4ade80', '',
        { valFormatter: v => Number(v).toFixed(2) }
    );

    // 13. PALLE RECUPERATE (DIFENSORI / MEDIANI PER MODIFICATORE)
    const cardRecoveries = buildLeaderboardCard(
        'Palle Recuperate', '🛡️', 'Contrasti vinti e recuperi (Modificatore Difesa)',
        pool,
        p => p.recuperi_2627 || p.ball_recovery_stat_2627 || 0,
        p => `${p.presenze_2627 || 0} presenze`,
        '#38bdf8', ''
    );

    // 14. GRANDI OCCASIONI CREATE (BIG CHANCES)
    const cardBigChances = buildLeaderboardCard(
        'Grandi Occasioni Create', '⚡', 'Palle gol nitide regalate ai compagni',
        pool,
        p => p.big_chances_created_2627 || p.chances_created_2627 || 0,
        p => `${p.assist_2627 || 0} assist reali`,
        '#c084fc', ''
    );

    // 15. RATING STATISTICO (min 2 gare)
    const cardRating = buildLeaderboardCard(
        'Rating Statistico', '⭐', 'Media voto oggettiva e rendimento (min. 2 gare)',
        poolVoted2,
        p => p.rating_live_2627 || 0,
        p => `${p.presenze_2627 || 0} gare a voto`,
        '#38bdf8', ''
    );

    // 16. EXPECTED GOALS ON TARGET (xGOT)
    const cardXgot = buildLeaderboardCard(
        'Expected Goals on Target (xGOT)', '🎯', 'Qualità e precisione tiri nello specchio',
        pool,
        p => p.xgot_2627 || 0,
        p => `${p.gol_2627 || 0} gol segnati`,
        '#ec4899', ''
    );

    // 17. GRANDI OCCASIONI FALLITE (BIG CHANCES MISSED)
    const cardBigChancesMissed = buildLeaderboardCard(
        'Occasioni Nitide Fallite', '❌', 'Grandi occasioni da gol non concretizzate',
        pool,
        p => p.big_chance_missed_2627 || 0,
        p => `${p.gol_2627 || 0} gol realizzati`,
        '#f87171', ''
    );

    // 18. TIRI NELLO SPECCHIO PER 90
    const cardShotsOnTarget = buildLeaderboardCard(
        'Tiri in Porta /90', '🎯', 'Frequenza conclusioni nello specchio ogni 90 min',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.ontarget_scoring_att_2627 || 0,
        p => `${p.gol_2627 || 0} gol`,
        '#fbbf24', ''
    );

    // 19. GOL EVITATI PORTIERI (GOALS PREVENTED)
    const cardGoalsPrevented = buildLeaderboardCard(
        'Gol Evitati (Goals Prevented)', '🧤', 'Miracoli e gol salvati rispetto ai tiri subiti',
        poolGk,
        p => p.goals_prevented_2627 !== null && p.goals_prevented_2627 !== undefined ? p.goals_prevented_2627 : 0,
        p => `Par: ${p.parate_2627 || 0} • GS: ${p.gol_subiti_2627 || 0}`,
        '#10b981', ''
    );

    // 20. % PARATE PORTIERI
    const cardSavePct = buildLeaderboardCard(
        '% Parate Effettuate', '🛡️', 'Percentuale tiri respinti (min. 2 gare)',
        poolGk.filter(p => (p.presenze_2627 || p.minuti_stat_2627 ? 1 : 0) >= 1),
        p => p.save_pct_2627 || 0,
        p => `${p.parate_2627 || 0} parate • ${p.clean_sheets_2627 || 0} CS`,
        '#4ade80', '%'
    );

    // 21. CONTRASTI VINTI /90 (TACKLES)
    const cardTackles = buildLeaderboardCard(
        'Contrasti Vinti /90', '⚔️', 'Tackle riusciti per gara (Interdizione e Modificatore)',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.total_tackle_2627 || 0,
        p => `${p.recuperi_2627 || p.ball_recovery_stat_2627 || 0} recuperi`,
        '#38bdf8', ''
    );

    // 22. DRIBBLING RIUSCITI /90
    const cardDribbles = buildLeaderboardCard(
        'Dribbling Riusciti /90', '🪄', 'Superiorità numerica e dribbling vinti per 90 min',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.won_contest_2627 || 0,
        p => `${p.assist_2627 || 0} assist`,
        '#c084fc', ''
    );

    // 23. FALLI COMMESSI /90
    const cardFouls = buildLeaderboardCard(
        'Falli Commessi /90', '⚠️', 'Giocatori più fallosi per gara (Rischio Malus)',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.fouls_2627 || 0,
        p => `${p.amm_2627 || 0} ammonizioni`,
        '#f87171', ''
    );

    // Selezione layout delle sezioni in base a statsViewCategory
    let sectionsHtml = '';
    if (statsViewCategory === 'ALL') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:20px;">
                ${cardGoals}
                ${cardAssists}
                ${cardFm}
                ${cardXfm}
                ${cardUnderperformers}
                ${cardOverperformers}
                ${cardMv}
                ${cardRating}
                ${cardXg}
                ${cardXa}
                ${cardXgot}
                ${cardGoalsPrevented}
                ${cardGkCs}
                ${cardBigChances}
                ${cardBigChancesMissed}
                ${cardRecoveries}
                ${cardTackles}
                ${cardBonus}
                ${cardMalus}
            </div>
        `;
    } else if (statsViewCategory === 'xfm_delta') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardXfm}
                ${cardUnderperformers}
                ${cardOverperformers}
                ${cardFm}
                ${cardXg}
                ${cardXa}
            </div>
        `;
    } else if (statsViewCategory === 'goals') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardGoals}
                ${cardXg}
                ${cardXgot}
                ${cardShotsOnTarget}
                ${cardBigChancesMissed}
                ${cardBonus}
            </div>
        `;
    } else if (statsViewCategory === 'assists') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardAssists}
                ${cardXa}
                ${cardBigChances}
                ${cardDribbles}
            </div>
        `;
    } else if (statsViewCategory === 'gk') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardGoalsPrevented}
                ${cardGkCs}
                ${cardSavePct}
                ${cardGkGs}
            </div>
        `;
    } else if (statsViewCategory === 'defense') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardRecoveries}
                ${cardTackles}
                ${cardGkCs}
            </div>
        `;
    } else if (statsViewCategory === 'bonus_malus') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardBonus}
                ${cardMalus}
            </div>
        `;
    } else if (statsViewCategory === 'cards') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardAmm}
                ${cardEsp}
                ${cardFouls}
                ${cardMalus}
            </div>
        `;
    } else if (statsViewCategory === 'ratings') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardFm}
                ${cardXfm}
                ${cardUnderperformers}
                ${cardOverperformers}
                ${cardMv}
                ${cardRating}
            </div>
        `;
    } else if (statsViewCategory === 'xg_xa') {
        sectionsHtml = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:20px;">
                ${cardXg}
                ${cardXa}
                ${cardXgot}
                ${cardBigChances}
                ${cardXfm}
            </div>
        `;
    }

    // Costruzione Selettore Club
    const teamsList = Array.from(new Set(PLAYERS.map(p => p.team))).filter(Boolean).sort();
    const teamOptions = teamsList.map(tm => `<option value="${tm}" ${statsFilterTeam === tm ? 'selected' : ''}>${tm}</option>`).join('');

    container.innerHTML = `
        <div class="stats-page-container" style="max-width:1380px;margin:0 auto;padding:16px 20px;">
            <!-- HEADER -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:14px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:36px;">📊</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:20px;color:#fff;">Statistiche & Leaderboard Serie A 2026/27</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            Classifiche ufficiali: Gol, Assist, xG/xA, Portieri, Bonus, Malus, Cartellini e Medie Voto. Clicca su qualsiasi calciatore per aprire la sua scheda.
                        </div>
                    </div>
                </div>

                <div style="display:flex;align-items:center;gap:10px;">
                    <!-- TOP N SELECTOR -->
                    <div style="display:flex;align-items:center;gap:4px;background:rgba(0,0,0,0.3);padding:3px 6px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);">
                        <span style="font-size:11px;color:var(--text-muted);font-weight:700;margin-right:4px;">Righe:</span>
                        <button class="btn-action ${statsLimit === 10 ? 'active' : ''}" style="padding:4px 10px;font-size:11px;" onclick="setStatsLimit(10)">Top 10</button>
                        <button class="btn-action ${statsLimit === 20 ? 'active' : ''}" style="padding:4px 10px;font-size:11px;" onclick="setStatsLimit(20)">Top 20</button>
                        <button class="btn-action ${statsLimit === 50 ? 'active' : ''}" style="padding:4px 10px;font-size:11px;" onclick="setStatsLimit(50)">Top 50</button>
                    </div>
                </div>
            </div>

            <!-- BARRA FILTRI E RICERCA -->
            <div class="filter-panel stats-filter-panel">
                <div class="stats-search-box">
                    <input type="text" 
                           id="inputStatsSearch" 
                           class="input-search"
                           placeholder="🔍 Cerca calciatore nelle classifiche..." 
                           value="${statsSearchQuery}" 
                           oninput="statsSearchQuery = this.value; renderStatsSerieAView();">
                </div>

                <div class="stats-select-group">
                    <span style="font-size:11.5px;color:var(--text-muted);font-weight:700;">Ruolo:</span>
                    <select class="select-filter" onchange="statsFilterRole = this.value; renderStatsSerieAView();">
                        <option value="ALL" ${statsFilterRole === 'ALL' ? 'selected' : ''}>Tutti i Ruoli</option>
                        <option value="P" ${statsFilterRole === 'P' ? 'selected' : ''}>Portieri (P)</option>
                        <option value="D" ${statsFilterRole === 'D' ? 'selected' : ''}>Difensori (D)</option>
                        <option value="C" ${statsFilterRole === 'C' ? 'selected' : ''}>Centrocampisti (C)</option>
                        <option value="A" ${statsFilterRole === 'A' ? 'selected' : ''}>Attaccanti (A)</option>
                    </select>
                </div>

                <div class="stats-select-group">
                    <span style="font-size:11.5px;color:var(--text-muted);font-weight:700;">Club:</span>
                    <select class="select-filter" onchange="statsFilterTeam = this.value; renderStatsSerieAView();">
                        <option value="ALL" ${statsFilterTeam === 'ALL' ? 'selected' : ''}>Tutti i Club</option>
                        ${teamOptions}
                    </select>
                </div>

                ${(statsSearchQuery || statsFilterRole !== 'ALL' || statsFilterTeam !== 'ALL') ? `
                    <button class="btn-action" style="padding:5px 10px;font-size:11.5px;background:rgba(239,68,68,0.15);color:#f87171;border-color:rgba(239,68,68,0.3);" onclick="statsSearchQuery = ''; statsFilterRole = 'ALL'; statsFilterTeam = 'ALL'; renderStatsSerieAView();">
                        Reset Filtri ✕
                    </button>
                ` : ''}
            </div>

            <!-- PILLOLE CATEGORIE VELOCI -->
            <div class="stats-pills-bar">
                <button class="btn-action ${statsViewCategory === 'ALL' ? 'active' : ''}" onclick="setStatsCategory('ALL')">🌟 Panoramica Griglie</button>
                <button class="btn-action ${statsViewCategory === 'xfm_delta' ? 'active' : ''}" onclick="setStatsCategory('xfm_delta')">🔮 Expected FantaMedia (xFM) & Occasioni</button>
                <button class="btn-action ${statsViewCategory === 'goals' ? 'active' : ''}" onclick="setStatsCategory('goals')">⚽ Gol & Attacco</button>
                <button class="btn-action ${statsViewCategory === 'assists' ? 'active' : ''}" onclick="setStatsCategory('assists')">🪄 Assist & Rifinitura</button>
                <button class="btn-action ${statsViewCategory === 'xg_xa' ? 'active' : ''}" onclick="setStatsCategory('xg_xa')">🎯 Expected Metrics (xG / xA)</button>
                <button class="btn-action ${statsViewCategory === 'gk' ? 'active' : ''}" onclick="setStatsCategory('gk')">🧤 Portieri</button>
                <button class="btn-action ${statsViewCategory === 'defense' ? 'active' : ''}" onclick="setStatsCategory('defense')">🛡️ Difesa & Modificatore</button>
                <button class="btn-action ${statsViewCategory === 'bonus_malus' ? 'active' : ''}" onclick="setStatsCategory('bonus_malus')">🎁 Bonus & Malus</button>
                <button class="btn-action ${statsViewCategory === 'cards' ? 'active' : ''}" onclick="setStatsCategory('cards')">🟨 Cartellini & Disciplina</button>
                <button class="btn-action ${statsViewCategory === 'ratings' ? 'active' : ''}" onclick="setStatsCategory('ratings')">📈 FantaMedia & Media Voto</button>
            </div>

            <!-- GRIGLIA CLASSIFICHE -->
            ${sectionsHtml}
        </div>
    `;
}

window.setStatsCategory = setStatsCategory;
window.setStatsLimit = setStatsLimit;
window.renderStatsSerieAView = renderStatsSerieAView;
