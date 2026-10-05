let statsFilterRole = 'ALL';
let statsFilterTeam = 'ALL';
let statsSearchQuery = '';
let statsViewCategory = 'ALL'; // 'ALL', 'xfm_delta', 'goals', 'assists', 'defense', 'discipline'
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
        container.innerHTML = `<div style="padding:60px;text-align:center;color:var(--text-muted);font-size:14px;">Caricamento dati statistiche in corso...</div>`;
        return;
    }
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
    const buildLeaderboardCard = (title, icon, subtitle, playerList, valExtractor, secDetailExtractor, highlightColor = 'var(--accent-cyan)', suffix = '', options = {}) => {
        const allowNegative = !!options.allowNegative;
        const sortAsc = !!options.sortAsc;
        const valFormatter = options.valFormatter || (v => `${v}${suffix}`);
        const unitLabel = options.unitLabel || '';
        const sorted = playerList
            .filter(p => {
                const val = valExtractor(p);
                if (val === null || val === undefined || isNaN(val)) return false;
                if (!allowNegative && val <= 0) return false;
                return true;
            })
            .sort((a, b) => sortAsc ? (valExtractor(a) - valExtractor(b)) : (valExtractor(b) - valExtractor(a)))
            .slice(0, statsLimit);
        if (sorted.length === 0) {
            return `
                <div class="stats-card">
                    <div class="stats-card-header">
                        <div class="stats-card-title-group">
                            <span class="stats-card-icon">${icon}</span>
                            <div>
                                <h4 class="stats-card-title">${title}</h4>
                                <div class="stats-card-sub">${subtitle}</div>
                            </div>
                        </div>
                        <span class="stats-card-limit-tag">TOP ${statsLimit}</span>
                    </div>
                    <div style="padding:32px 16px;text-align:center;font-size:12px;color:#64748b;">
                        Nessun dato per i filtri selezionati.
                    </div>
                </div>
            `;
        }
        const leader = sorted[0];
        const leaderRawVal = valExtractor(leader);
        const leaderDisplayVal = valFormatter(leaderRawVal);
        const leaderSec = secDetailExtractor ? secDetailExtractor(leader) : '';
        const leaderMaxVal = Math.abs(leaderRawVal) || 1;
        const leaderSpotlightHtml = `
            <div class="leader-spotlight" onclick="openPlayerProfileModal(${leader.id})" title="Apri scheda di ${leader.name}" style="border-left: 3px solid ${highlightColor};">
                <div style="position:absolute;right:-15px;top:-15px;width:120px;height:120px;background:radial-gradient(circle, ${highlightColor}20 0%, transparent 70%);pointer-events:none;"></div>
                <div style="display:flex;align-items:center;min-width:0;flex:1;gap:10px;">
                    <div class="leader-crown-badge">
                        <span style="font-size:16px;line-height:1;">👑</span>
                    </div>
                    <div class="leader-info" style="min-width:0;flex:1;">
                        <div class="leader-top-line" style="display:flex;align-items:center;gap:7px;margin-bottom:2px;">
                            <span class="role-badge ${leader.role}" style="font-size:10px;padding:1px 6px;font-weight:800;flex-shrink:0;">${leader.role}</span>
                            <span class="leader-name" style="font-size:15px;font-weight:900;color:#fff;letter-spacing:-0.2px;">${leader.name}</span>
                        </div>
                        <div class="leader-meta" style="font-size:11.5px;color:#94a3b8;display:flex;align-items:center;gap:5px;flex-wrap:wrap;">
                            <span style="color:#cbd5e1;font-weight:700;">${leader.team}</span>
                            ${leaderSec ? `<span style="opacity:0.4;">•</span><span>${leaderSec}</span>` : ''}
                        </div>
                    </div>
                </div>
                <div class="leader-stat-box" style="text-align:right;padding-left:10px;flex-shrink:0;">
                    <div class="leader-stat-val" style="color:${highlightColor};font-size:22px;font-weight:950;letter-spacing:-0.5px;text-shadow:0 0 16px ${highlightColor}40;">
                        ${leaderDisplayVal}
                    </div>
                    ${unitLabel ? `<div class="leader-metric-unit" style="font-size:9.5px;font-weight:800;color:#64748b;text-transform:uppercase;margin-top:2px;letter-spacing:0.5px;">${unitLabel}</div>` : ''}
                </div>
            </div>
        `;
        const remaining = sorted.slice(1);
        let rowsHtml = '';
        if (remaining.length > 0) {
            rowsHtml = `
                <div class="stats-rows-list">
                    ${remaining.map((p, idx) => {
                        const rawVal = valExtractor(p);
                        const displayVal = valFormatter(rawVal);
                        const sec = secDetailExtractor ? secDetailExtractor(p) : '';
                        const rankNum = idx + 2;
                        const rankClass = rankNum === 2 ? 'rank-2' : (rankNum === 3 ? 'rank-3' : '');
                        const pct = leaderMaxVal > 0 
                            ? Math.max(8, Math.min(100, Math.round((Math.abs(rawVal) / leaderMaxVal) * 100))) 
                            : 50;
                        return `
                            <div class="stats-row" onclick="openPlayerProfileModal(${p.id})" title="Clicca per aprire la scheda di ${p.name}">
                                <div class="stats-row-main">
                                    <div class="stats-row-left">
                                        <span class="stats-rank-num ${rankClass}">#${rankNum}</span>
                                        <span class="role-badge ${p.role}" style="font-size:9.5px;padding:1px 5px;">${p.role}</span>
                                        <div class="stats-player-info">
                                            <span class="stats-player-name">${p.name}</span>
                                            <span class="stats-player-meta">${p.team}${sec ? ` • ${sec}` : ''}</span>
                                        </div>
                                    </div>
                                    <div class="stats-row-right">
                                        <span class="stats-val" style="color:${highlightColor};">
                                            ${displayVal}
                                        </span>
                                    </div>
                                </div>
                                <div class="stats-bar-track">
                                    <div class="stats-bar-fill" style="width:${pct}%;background:linear-gradient(90deg, ${highlightColor}50, ${highlightColor});"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }
        return `
            <div class="stats-card">
                <div class="stats-card-header">
                    <div class="stats-card-title-group">
                        <span class="stats-card-icon">${icon}</span>
                        <div>
                            <h4 class="stats-card-title">${title}</h4>
                            <div class="stats-card-sub">${subtitle}</div>
                        </div>
                    </div>
                    <span class="stats-card-limit-tag">TOP ${statsLimit}</span>
                </div>
                ${leaderSpotlightHtml}
                ${rowsHtml}
            </div>
        `;
    };
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
    const poolVoted2 = pool.filter(p => (p.presenze_2627 || p.partite_voto_2627 || 0) >= 2 || (p.minuti_stat_2627 || 0) >= 90);
    const poolGk = pool.filter(p => p.role === 'P');
    const cardXfm = buildLeaderboardCard(
        'Top Expected FantaMedia (xFM)', '🔮', 'FantaMedia attesa da modello xG/xA/CS',
        poolVoted2,
        p => getXfmObj(p).xfm,
        p => `FM: ${p.fm_2627 ? p.fm_2627.toFixed(2) : '-'} • ${p.presenze_2627 || 0}g`,
        '#00f2fe', '',
        { valFormatter: v => Number(v).toFixed(2), unitLabel: 'xFM' }
    );
    const cardUnderperformers = buildLeaderboardCard(
        'Occasioni di Mercato (Scommesse 💎)', '💎', 'Producono tanto xG/xA con meno bonus raccolti (Da Comprare)',
        poolVoted2.filter(p => getXfmObj(p).delta < -0.15),
        p => getXfmObj(p).delta,
        p => `xFM ${getXfmObj(p).xfm.toFixed(2)} vs FM ${p.fm_2627 ? p.fm_2627.toFixed(2) : '-'}`,
        '#10b981', '',
        { allowNegative: true, sortAsc: true, valFormatter: v => `${Number(v).toFixed(2)}`, unitLabel: 'Delta' }
    );
    const cardOverperformers = buildLeaderboardCard(
        'Rischio Regressione ⚠️', '⚠️', 'Hanno raccolto più bonus rispetto al volume di occasioni create',
        poolVoted2.filter(p => getXfmObj(p).delta > 0.15),
        p => getXfmObj(p).delta,
        p => `FM ${p.fm_2627 ? p.fm_2627.toFixed(2) : '-'} vs xFM ${getXfmObj(p).xfm.toFixed(2)}`,
        '#f87171', '',
        { allowNegative: true, sortAsc: false, valFormatter: v => `+${Number(v).toFixed(2)}`, unitLabel: 'Delta' }
    );
    const cardFm = buildLeaderboardCard(
        'Top FantaMedia Reale (FM)', '📈', 'Miglior rendimento con bonus (min. 2 gare)',
        poolVoted2,
        p => p.fm_2627 || 0,
        p => `${p.presenze_2627 || 0} gare a voto`,
        '#fbbf24', '',
        { valFormatter: v => Number(v).toFixed(2), unitLabel: 'FM' }
    );
    const cardMv = buildLeaderboardCard(
        'Top Media Voto Pura (MV)', '📊', 'Miglior media voto senza bonus (min. 2 gare)',
        poolVoted2,
        p => p.mv_2627 || 0,
        p => `${p.presenze_2627 || 0} gare a voto`,
        '#4ade80', '',
        { valFormatter: v => Number(v).toFixed(2), unitLabel: 'MV' }
    );
    const cardRating = buildLeaderboardCard(
        'Rating Statistico Live', '⭐', 'Media voto oggettiva basata su metriche live',
        poolVoted2,
        p => p.rating_live_2627 || 0,
        p => `${p.presenze_2627 || 0} gare a voto`,
        '#a78bfa', '',
        { unitLabel: 'Rating' }
    );
    const cardGoals = buildLeaderboardCard(
        'Classifica Marcatori', '⚽', 'Gol segnati in Serie A 2026/27',
        pool,
        p => p.gol_2627 || 0,
        p => `${p.presenze_2627 || 0} gare`,
        '#fbbf24', '',
        { unitLabel: 'GOL' }
    );
    const cardXg = buildLeaderboardCard(
        'Expected Goals (xG)', '🎯', 'Qualità e volume tiri generati',
        pool,
        p => p.xg_2627 !== null && p.xg_2627 !== undefined ? p.xg_2627 : (p.xg90_2627 ? parseFloat(p.xg90_2627) : 0),
        p => p.xg90_2627 ? `${p.xg90_2627} xG/90` : `${p.gol_2627 || 0} gol`,
        '#f472b6', '',
        { unitLabel: 'xG' }
    );
    const cardShotsOnTarget = buildLeaderboardCard(
        'Tiri nello Specchio /90', '🎯', 'Frequenza conclusioni in porta ogni 90 min',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.ontarget_scoring_att_2627 || 0,
        p => `${p.gol_2627 || 0} gol realizzati`,
        '#38bdf8', '',
        { unitLabel: 'Tiri/90' }
    );
    const cardXgot = buildLeaderboardCard(
        'Expected Goals on Target (xGOT)', '🎯', 'Precisione e pericolosità tiri nello specchio',
        pool,
        p => p.xgot_2627 || 0,
        p => `${p.gol_2627 || 0} gol segnati`,
        '#ec4899', '',
        { unitLabel: 'xGOT' }
    );
    const cardBigChancesMissed = buildLeaderboardCard(
        'Occasioni Nitide Fallite', '❌', 'Grandi occasioni da gol non concretizzate',
        pool,
        p => p.big_chance_missed_2627 || 0,
        p => `${p.gol_2627 || 0} gol realizzati`,
        '#f87171', '',
        { unitLabel: 'Fallite' }
    );
    const cardAssists = buildLeaderboardCard(
        'Classifica Assist', '🪄', 'Assist vincenti forniti ai compagni',
        pool,
        p => p.assist_2627 || 0,
        p => `${p.presenze_2627 || 0} gare`,
        '#00f2fe', '',
        { unitLabel: 'ASSIST' }
    );
    const cardXa = buildLeaderboardCard(
        'Expected Assists (xA)', '🪄', 'Pericolosità passaggi e rifinitura',
        pool,
        p => p.xa_2627 !== null && p.xa_2627 !== undefined ? p.xa_2627 : (p.xa90_2627 ? parseFloat(p.xa90_2627) : 0),
        p => p.xa90_2627 ? `${p.xa90_2627} xA/90` : `${p.assist_2627 || 0} assist`,
        '#38bdf8', '',
        { unitLabel: 'xA' }
    );
    const cardBigChances = buildLeaderboardCard(
        'Grandi Occasioni Create', '⚡', 'Palle gol nitide regalate ai compagni',
        pool,
        p => p.big_chances_created_2627 || p.chances_created_2627 || 0,
        p => `${p.assist_2627 || 0} assist reali`,
        '#c084fc', '',
        { unitLabel: 'Chances' }
    );
    const cardDribbles = buildLeaderboardCard(
        'Dribbling Riusciti /90', '💫', 'Superiorità numerica e dribbling vinti',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.won_contest_2627 || 0,
        p => `${p.assist_2627 || 0} assist`,
        '#818cf8', '',
        { unitLabel: 'Dribbling' }
    );
    const cardGkCs = buildLeaderboardCard(
        'Clean Sheets (Portieri)', '🛡️', 'Partite a porta inviolata',
        poolGk,
        p => (p.clean_sheets_2627 !== undefined && p.clean_sheets_2627 > 0) ? p.clean_sheets_2627 : (p.clean_sheet_stat_2627 || 0),
        p => `${p.presenze_2627 || 0} gare • ${p.parate_2627 || 0} parate`,
        '#4ade80', '',
        { unitLabel: 'Clean Sheet' }
    );
    const cardGoalsPrevented = buildLeaderboardCard(
        'Gol Evitati (Goals Prevented)', '🧤', 'Miracoli e gol salvati oltre l\'atteso',
        poolGk,
        p => p.goals_prevented_2627 !== null && p.goals_prevented_2627 !== undefined ? p.goals_prevented_2627 : 0,
        p => `Parate: ${p.parate_2627 || 0} • GS: ${p.gol_subiti_2627 || 0}`,
        '#10b981', '',
        { unitLabel: 'Evitati' }
    );
    const cardSavePct = buildLeaderboardCard(
        '% Parate Effettuate', '🛡️', 'Percentuale tiri respinti (min. 1 gara)',
        poolGk.filter(p => (p.presenze_2627 || p.minuti_stat_2627 ? 1 : 0) >= 1),
        p => p.save_pct_2627 || 0,
        p => `${p.parate_2627 || 0} parate • ${p.clean_sheets_2627 || 0} CS`,
        '#22d3ee', '%',
        { unitLabel: '% Parate' }
    );
    const cardRecoveries = buildLeaderboardCard(
        'Palle Recuperate (Modificatore)', '🛡️', 'Contrasti vinti e recuperi difensivi',
        pool,
        p => p.recuperi_2627 || p.ball_recovery_stat_2627 || 0,
        p => `${p.presenze_2627 || 0} presenze`,
        '#38bdf8', '',
        { unitLabel: 'Recuperi' }
    );
    const cardTackles = buildLeaderboardCard(
        'Contrasti Vinti /90', '⚔️', 'Tackle riusciti per gara (Interdizione)',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.total_tackle_2627 || 0,
        p => `${p.recuperi_2627 || p.ball_recovery_stat_2627 || 0} recuperi`,
        '#60a5fa', '',
        { unitLabel: 'Tackles' }
    );
    const cardGkGs = buildLeaderboardCard(
        'Gol Subiti (Portieri)', '🧤', 'Reti incassate complessive',
        poolGk,
        p => p.gol_subiti_2627 || 0,
        p => `CS: ${p.clean_sheets_2627 || 0} • Par: ${p.parate_2627 || 0}`,
        '#ef4444', '',
        { unitLabel: 'Gol Subiti' }
    );
    const cardBonus = buildLeaderboardCard(
        'Top FantaBonus (+)', '🎁', 'Punti bonus accumulati (+3 Gol, +1 Assist, +3 Rig.)',
        pool,
        p => (p.tot_bonus_2627 !== undefined && p.tot_bonus_2627 > 0) ? p.tot_bonus_2627 : ((p.gol_2627 || 0) * 3 + (p.assist_2627 || 0)),
        p => `${p.gol_2627 || 0}G • ${p.assist_2627 || 0}A`,
        '#10b981', ' pt',
        { unitLabel: 'Bonus' }
    );
    const cardMalus = buildLeaderboardCard(
        'Top FantaMalus (-)', '⚠️', 'Punti malus subiti (Gol subiti, Rig. falliti, Amm, Esp)',
        pool,
        p => (p.tot_malus_2627 !== undefined && p.tot_malus_2627 > 0) ? p.tot_malus_2627 : ((p.gol_subiti_2627 || 0) + (p.amm_2627 || 0) * 0.5 + (p.esp_2627 || 0)),
        p => `${p.gol_subiti_2627 ? p.gol_subiti_2627 + ' GS • ' : ''}${p.amm_2627 || 0} Amm`,
        '#f87171', ' pt',
        { unitLabel: 'Malus' }
    );
    const cardAmm = buildLeaderboardCard(
        'Cartellini Gialli', '🟨', 'Classifica ammonizioni Serie A',
        pool,
        p => p.amm_2627 || 0,
        p => `${p.falli_subiti_2627 || 0} falli subiti`,
        '#fbbf24', '',
        { unitLabel: 'Gialli' }
    );
    const cardEsp = buildLeaderboardCard(
        'Cartellini Rossi', '🟥', 'Classifica espulsioni Serie A',
        pool,
        p => p.esp_2627 || 0,
        p => `${p.amm_2627 || 0} gialli`,
        '#ef4444', '',
        { unitLabel: 'Rossi' }
    );
    const cardFouls = buildLeaderboardCard(
        'Falli Commessi /90', '⚠️', 'Giocatori più fallosi per gara (Rischio Malus)',
        pool.filter(p => (p.minuti_2627 || p.minuti_stat_2627 || 0) >= 45),
        p => p.fouls_2627 || 0,
        p => `${p.amm_2627 || 0} ammonizioni`,
        '#fb923c', '',
        { unitLabel: 'Falli/90' }
    );
    const buildSectionGroup = (icon, title, badge, desc, cardsArray) => {
        return `
            <div class="stats-section-group">
                <div class="stats-section-header">
                    <div class="stats-section-title-wrap">
                        <span class="stats-section-icon">${icon}</span>
                        <div>
                            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                <h3 class="stats-section-title">${title}</h3>
                                <span class="stats-section-badge">${badge}</span>
                            </div>
                            <p class="stats-section-desc">${desc}</p>
                        </div>
                    </div>
                </div>
                <div class="stats-cards-grid">
                    ${cardsArray.join('')}
                </div>
            </div>
        `;
    };
    const secValore = buildSectionGroup(
        '🔮',
        'Expected FantaMedia (xFM) & Analisi Valore',
        'AI PREDITTIVA',
        'Il cuore predittivo del fantacalcio: chi produce fanta-valore reale e chi è destinato a esplodere o calare.',
        [cardXfm, cardUnderperformers, cardOverperformers, cardFm, cardMv, cardRating]
    );
    const secAttacco = buildSectionGroup(
        '⚽',
        'Attacco, Gol & Finalizzazione',
        'RETI & VOLUME',
        'I bomber della Serie A, la qualità del tiro (xG) e la freddezza sotto porta.',
        [cardGoals, cardXg, cardShotsOnTarget, cardXgot, cardBigChancesMissed]
    );
    const secAssist = buildSectionGroup(
        '🪄',
        'Creatività, Assist & Grandi Occasioni',
        'FANTASIA & REGIA',
        'I maestri dell\'assist, visione di gioco ed Expected Assists (xA) forniti ai compagni.',
        [cardAssists, cardXa, cardBigChances, cardDribbles]
    );
    const secDifesa = buildSectionGroup(
        '🧤',
        'Portieri, Clean Sheet & Modificatore Difesa',
        'PORTA & CONTRASTI',
        'I migliori interpreti difensivi: reti inviolate, miracoli tra i pali e contrasti vinti.',
        [cardGkCs, cardGoalsPrevented, cardSavePct, cardRecoveries, cardTackles, cardGkGs]
    );
    const secDisciplina = buildSectionGroup(
        '⚖️',
        'FantaBonus, Malus & Disciplina',
        'SALDO PUNTI & CARTELLINI',
        'Impatto complessivo di bonus (+3, +1) contro le penalità da cartellini e gol subiti.',
        [cardBonus, cardMalus, cardAmm, cardEsp, cardFouls]
    );
    let sectionsHtml = '';
    if (statsViewCategory === 'ALL') {
        sectionsHtml = `${secValore} ${secAttacco} ${secAssist} ${secDifesa} ${secDisciplina}`;
    } else if (statsViewCategory === 'xfm_delta' || statsViewCategory === 'ratings') {
        sectionsHtml = secValore;
    } else if (statsViewCategory === 'goals') {
        sectionsHtml = secAttacco;
    } else if (statsViewCategory === 'assists') {
        sectionsHtml = secAssist;
    } else if (statsViewCategory === 'defense' || statsViewCategory === 'gk') {
        sectionsHtml = secDifesa;
    } else if (['discipline', 'cards', 'bonus_malus'].includes(statsViewCategory)) {
        sectionsHtml = secDisciplina;
    } else if (statsViewCategory === 'xg_xa') {
        sectionsHtml = `${secAttacco} ${secAssist}`;
    } else {
        sectionsHtml = `${secValore} ${secAttacco} ${secAssist} ${secDifesa} ${secDisciplina}`;
    }
    const teamsList = Array.from(new Set(PLAYERS.map(p => p.team))).filter(Boolean).sort();
    const teamOptions = teamsList.map(tm => `<option value="${tm}" ${statsFilterTeam === tm ? 'selected' : ''}>${tm}</option>`).join('');
    container.innerHTML = `
        <div class="stats-page-container">
            <!-- HEADER -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:14px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:32px;line-height:1;">📊</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.3px;">Statistiche & Leaderboard Serie A 2026/27</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            Classifiche ufficiali e avanzate: Gol, Assist, xG/xA, Portieri, Bonus, Malus e Modelli Predittivi xFM. Clicca su qualsiasi riga per aprire la scheda del calciatore.
                        </div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;background:rgba(0,0,0,0.3);padding:3px 6px;border-radius:10px;border:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:11px;color:var(--text-muted);font-weight:800;margin-right:4px;">Righe:</span>
                    <button class="btn-action ${statsLimit === 10 ? 'active' : ''}" style="padding:4px 10px;font-size:11px;border-radius:6px;" onclick="setStatsLimit(10)">Top 10</button>
                    <button class="btn-action ${statsLimit === 20 ? 'active' : ''}" style="padding:4px 10px;font-size:11px;border-radius:6px;" onclick="setStatsLimit(20)">Top 20</button>
                    <button class="btn-action ${statsLimit === 50 ? 'active' : ''}" style="padding:4px 10px;font-size:11px;border-radius:6px;" onclick="setStatsLimit(50)">Top 50</button>
                </div>
            </div>
            <!-- MACRO NAVIGATION SWITCHER -->
            <div class="stats-macro-nav">
                <button class="stats-macro-btn ${statsViewCategory === 'ALL' ? 'active' : ''}" onclick="setStatsCategory('ALL')">
                    <span class="macro-icon">🌟</span>
                    <span class="macro-label">Panoramica Completa</span>
                </button>
                <button class="stats-macro-btn ${['xfm_delta', 'ratings'].includes(statsViewCategory) ? 'active' : ''}" onclick="setStatsCategory('xfm_delta')">
                    <span class="macro-icon">🔮</span>
                    <span class="macro-label">FantaMedia & xFM</span>
                </button>
                <button class="stats-macro-btn ${statsViewCategory === 'goals' ? 'active' : ''}" onclick="setStatsCategory('goals')">
                    <span class="macro-icon">⚽</span>
                    <span class="macro-label">Attacco & Gol</span>
                </button>
                <button class="stats-macro-btn ${statsViewCategory === 'assists' ? 'active' : ''}" onclick="setStatsCategory('assists')">
                    <span class="macro-icon">🪄</span>
                    <span class="macro-label">Assist & Rifinitura</span>
                </button>
                <button class="stats-macro-btn ${['defense', 'gk'].includes(statsViewCategory) ? 'active' : ''}" onclick="setStatsCategory('defense')">
                    <span class="macro-icon">🧤</span>
                    <span class="macro-label">Portieri & Difesa</span>
                </button>
                <button class="stats-macro-btn ${['discipline', 'cards', 'bonus_malus'].includes(statsViewCategory) ? 'active' : ''}" onclick="setStatsCategory('discipline')">
                    <span class="macro-icon">⚖️</span>
                    <span class="macro-label">Bonus & Disciplina</span>
                </button>
            </div>
            <!-- BARRA FILTRI E RICERCA -->
            <div class="stats-filter-bar">
                <div class="stats-search-wrapper">
                    <span style="font-size:13px;color:#64748b;">🔍</span>
                    <input type="text" 
                           id="inputStatsSearch" 
                           placeholder="Cerca calciatore o squadra..." 
                           value="${statsSearchQuery}" 
                           oninput="statsSearchQuery = this.value; renderStatsSerieAView();">
                    ${statsSearchQuery ? `
                        <button onclick="statsSearchQuery = ''; renderStatsSerieAView();" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:12px;padding:0 4px;" title="Cancella ricerca">✕</button>
                    ` : ''}
                </div>
                <div class="stats-filter-controls">
                    <div class="filter-chip-group">
                        <span class="filter-chip-label">Ruolo:</span>
                        <select onchange="statsFilterRole = this.value; renderStatsSerieAView();">
                            <option value="ALL" ${statsFilterRole === 'ALL' ? 'selected' : ''}>Tutti i Ruoli</option>
                            <option value="P" ${statsFilterRole === 'P' ? 'selected' : ''}>Portieri (P)</option>
                            <option value="D" ${statsFilterRole === 'D' ? 'selected' : ''}>Difensori (D)</option>
                            <option value="C" ${statsFilterRole === 'C' ? 'selected' : ''}>Centrocampisti (C)</option>
                            <option value="A" ${statsFilterRole === 'A' ? 'selected' : ''}>Attaccanti (A)</option>
                        </select>
                    </div>
                    <div class="filter-chip-group">
                        <span class="filter-chip-label">Club:</span>
                        <select onchange="statsFilterTeam = this.value; renderStatsSerieAView();">
                            <option value="ALL" ${statsFilterTeam === 'ALL' ? 'selected' : ''}>Tutti i Club</option>
                            ${teamOptions}
                        </select>
                    </div>
                    ${(statsSearchQuery || statsFilterRole !== 'ALL' || statsFilterTeam !== 'ALL') ? `
                        <button class="btn-action" style="padding:5px 12px;font-size:11px;background:rgba(239,68,68,0.15);color:#f87171;border-color:rgba(239,68,68,0.3);border-radius:8px;" onclick="statsSearchQuery = ''; statsFilterRole = 'ALL'; statsFilterTeam = 'ALL'; renderStatsSerieAView();">
                            Reset Filtri ✕
                        </button>
                    ` : ''}
                </div>
            </div>
            <!-- GRIGLIA SEZIONI CONCETTUALI -->
            ${sectionsHtml}
        </div>
    `;
}
window.setStatsCategory = setStatsCategory;
window.setStatsLimit = setStatsLimit;
window.renderStatsSerieAView = renderStatsSerieAView;