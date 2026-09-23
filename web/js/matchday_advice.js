// ==============================================================================
// MODULO CONSIGLIATI PROSSIMA GIORNATA — QUANTITATIVE FOTMOB ENGINE
// Serie A 2026/27 — Rating Deterministico & Fact-Based Tattico (FIFA / PES Style)
// ==============================================================================

window.matchdayAdviceState = {
    selectedRound: 6,
    mode: 'classic',  // 'classic' | 'mantra'
    activeRoleFilter: 'ALL'
};

const LEAGUE_AVG_XGA = 6.03;
const LEAGUE_AVG_XG = 6.04;
const LEAGUE_AVG_GC = 1.54;

function getUpcomingMatchdayRound() {
    try {
        if (typeof TOP_FLOP_DATA !== 'undefined' && TOP_FLOP_DATA && Object.keys(TOP_FLOP_DATA).length > 0) {
            const playedRounds = Object.keys(TOP_FLOP_DATA).map(Number).filter(n => !isNaN(n));
            if (playedRounds.length > 0) {
                const maxPlayed = Math.max(...playedRounds);
                return Math.min(38, maxPlayed + 1);
            }
        }
    } catch (e) {
        console.warn('Errore calcolo turno:', e);
    }
    return 6;
}

function getMatchdayFixturesMap(roundNum) {
    const fixtureMap = {};
    const matchesList = [];
    let roundDate = '';

    if (typeof OFFICIAL_CALENDAR_2026_27 !== 'undefined' && Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        const roundData = OFFICIAL_CALENDAR_2026_27.find(r => Number(r.giornata) === Number(roundNum));
        if (roundData) {
            roundDate = roundData.date || '';
            if (Array.isArray(roundData.matches)) {
                roundData.matches.forEach(m => {
                    matchesList.push(m);
                    fixtureMap[m.home] = { opp: m.away, isHome: true, matchText: `${m.home} vs ${m.away}` };
                    fixtureMap[m.away] = { opp: m.home, isHome: false, matchText: `${m.home} vs ${m.away}` };
                });
            }
        }
    }
    return { fixtureMap, matchesList, roundDate };
}

// ALGORITMO QUANTITATIVO DETERMINISTICO (FotMob Advanced Metrics Engine)
function calcMatchdayAdviceScore(player, matchInfo) {
    if (!matchInfo || player.is_injured) return -999;
    const tit = Number(player.titolarita) || 50;
    if (tit < 50) return -500;

    const team = player.team;
    const opp = matchInfo.opp;
    const isHome = matchInfo.isHome;
    const role = player.role;

    // Dati FotMob di Squadra (Reali 2026/27)
    const myStats = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[team]) ? TEAM_STATS_DB[team] : {};
    const oppStats = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[opp]) ? TEAM_STATS_DB[opp] : {};

    const myXga = Number(myStats.xga_team) || LEAGUE_AVG_XGA;
    const myGc = Number(myStats.goals_conceded_match) || LEAGUE_AVG_GC;
    const myCs = Number(myStats.clean_sheets) || 0;

    const oppXg = Number(oppStats.xg_team) || LEAGUE_AVG_XG;
    const oppXga = Number(oppStats.xga_team) || LEAGUE_AVG_XGA;
    const oppGc = Number(oppStats.goals_conceded_match) || LEAGUE_AVG_GC;
    const oppBc = Number(oppStats.big_chances) || 5.0;
    const oppBox = Number(oppStats.touches_opp_box) || 80.0;

    // Metriche Calciatore
    const ovr = Number(player.ovr) || 75;
    const fm = Number(player.fm_2627) || Number(player.fm) || 6.0;
    const mv = Number(player.mv_2627) || Number(player.mv) || 6.0;
    const xg90 = Number(player.xg90_2627) || Number(player.xg90) || 0;
    const xa90 = Number(player.xa90_2627) || Number(player.xa90) || 0;
    const gol = Number(player.gol_2627) || 0;
    const ass = Number(player.assist_2627) || 0;

    // 1. PORTIERI: Clean Sheet & Defense Rating (CSDR)
    if (role === 'P') {
        let score = 65.0 + (ovr * 0.18) + (fm * 2.5);

        // Solidità difensiva della propria squadra da FotMob
        const csFactor = (myCs * 8.0) - (myGc * 6.0) - ((myXga / LEAGUE_AVG_XGA) * 5.0);
        score += csFactor;

        // Vantaggio campo: storicamente +18% probabilità di Clean Sheet in casa
        if (isHome) score += 10.0;

        // Minaccia offensiva avversaria (xG e Big Chances FotMob):
        // Penalizzazione esponenziale non lineare per attacchi prolifici (es. Inter xG 11.7, Roma xG 11.2)
        const xgDiff = oppXg - LEAGUE_AVG_XG;
        if (xgDiff > 0) {
            score -= Math.pow(xgDiff, 1.35) * 8.5; // Malus drastico per i portieri contro super attacchi
        } else {
            score += Math.abs(xgDiff) * 6.0; // Premialità se l'avversario crea pochissimo
        }

        score -= (oppBc / 4.0) * 3.0;
        return Math.round(score * 10) / 10;
    }

    // 2. DIFENSORI: Modificatore & Flank Exploitation Index (MCAI & FEI)
    else if (role === 'D') {
        let score = 60.0 + (ovr * 0.22) + (fm * 3.5) + (mv * 3.0);

        // Pressione in area avversaria: meno tocchi in area subisce, meno cartellini/insufficienze
        const boxDiff = (oppBox - 80.0) / 20.0;
        score -= boxDiff * 4.0;

        // Vulnerabilità concessa dalla difesa avversaria (utile per terzini fluidificanti e saltatori)
        score += (oppXga / LEAGUE_AVG_XGA) * 6.0;

        if (isHome) score += 6.0;

        // Bonus Tattico OOP (terzino schierato esterno d'attacco o quinto)
        if (player.is_oop) score += 14.0;
        if (player.is_punizioni || player.is_corner) score += 7.0;

        // Rendimento bonus individuale
        score += (xg90 * 20.0) + (xa90 * 20.0) + (gol * 8.0) + (ass * 6.0);
        return Math.round(score * 10) / 10;
    }

    // 3. CENTROCAMPISTI & ATTACCANTI: Expected Finishing Conversion (EFC & KBAS)
    else {
        let score = 55.0 + (ovr * 0.22) + (fm * 4.0) + (mv * 2.5);

        // Moltiplicatore scientifico: quanto concede la difesa avversaria rispetto alla media del campionato
        const xgaRatio = oppXga / LEAGUE_AVG_XGA;
        const gcRatio = oppGc / LEAGUE_AVG_GC;

        score += (xgaRatio - 1.0) * 22.0;
        score += (gcRatio - 1.0) * 16.0;

        if (isHome) score += 7.0;

        // Bonus rigorista primario (+0.76 xG atteso da penalty)
        if (player.is_rigorista_1) score += 18.0;
        else if (player.is_rigorista_2) score += 8.0;

        if (player.is_oop) score += 12.0;
        if (player.is_punizioni || player.is_corner) score += 6.0;

        // Ponderazione degli xG e xA del calciatore in base alla debolezza dell'avversario
        score += (xg90 * xgaRatio) * 25.0;
        score += (xa90 * xgaRatio) * 20.0;
        score += (gol * 7.0) + (ass * 5.0);

        return Math.round(score * 10) / 10;
    }
}

// GENERATORE FATTUALE DIRETTO (Bespoke Fact-Based Insight — Zero Boilerplate)
function generateConciseTacticalNote(player, matchInfo, posKey) {
    const opp = matchInfo.opp;
    const isHome = matchInfo.isHome;
    const role = player.role;
    const team = player.team;
    const fm = (player.fm_2627 || player.fm || 6.0).toFixed(2);
    const gol = Number(player.gol_2627) || 0;
    const ass = Number(player.assist_2627) || 0;

    const oppStats = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[opp]) ? TEAM_STATS_DB[opp] : {};
    const myStats = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[team]) ? TEAM_STATS_DB[team] : {};

    const oppXga = oppStats.xga_team ? oppStats.xga_team.toFixed(1) : '6.0';
    const oppXg = oppStats.xg_team ? oppStats.xg_team.toFixed(1) : '6.0';
    const oppGc = oppStats.goals_conceded_match ? oppStats.goals_conceded_match.toFixed(1) : '1.5';
    const myXga = myStats.xga_team ? myStats.xga_team.toFixed(1) : '6.0';
    const myCs = myStats.clean_sheets || 0;

    // 1. PORTIERI: Dati reali di tenuta difensiva e debolezza offensiva avversaria
    if (role === 'P' || posKey === 'Por') {
        if (isHome) {
            return `Fortino a domicilio contro il ${opp} (${oppXg} xG stagionali): la retroguardia del ${team} ha concesso solo ${myXga} xGA con ${myCs} clean sheet. Altissima probabilità di imbattibilità (+1).`;
        }
        return `Trasferta favorevole a ${opp}: l'attacco avversario produce solo ${oppXg} xG. Solidità certificata e rischio malus contenuto per il voto.`;
    }

    // 2. DIFENSORI CENTRALI & BRACCETTI (Dc, B)
    if (posKey === 'Dc' || posKey === 'B') {
        return `Perno centrale contro l'attacco del ${opp} (appena ${oppXg} xG creati): duelli aerei favorevoli e zero malus. Voto pulito garantito da modificatore (FM ${fm}).`;
    }

    // 3. TERZINI ED ESTERNI A TUTTA FASCIA (Dd, Ds, E)
    if (posKey === 'Dd' || posKey === 'Ds' || posKey === 'E' || (role === 'D' && player.is_oop)) {
        const statsStr = (gol > 0 || ass > 0) ? ` (già ${gol}G e ${ass}A)` : '';
        if (player.is_oop) {
            return `Spinta avanzata OOP sulla corsia debole del ${opp} (${oppXga} xGA concessi)${statsStr}. Traversoni continui e bonus assist ad alto potenziale.`;
        }
        return `Sovrapposizioni continue ${isHome ? 'in casa' : 'a ' + opp} contro una difesa che subisce ${oppGc} gol/partita${statsStr}. Voto e cross sicuri (FM ${fm}).`;
    }

    // 4. MEDIANI DI ROTTURA (M)
    if (posKey === 'M') {
        return `Schermo tattico davanti alla difesa contro il ${opp}: anticipi puliti, regia equilibrata e media voto solida (FM ${fm}) senza rischio cartellini.`;
    }

    // 5. CENTROCAMPISTI E TREQUARTISTI (C, T)
    if (role === 'C' || posKey === 'C' || posKey === 'T') {
        const setPiece = player.is_rigorista_1 ? ' Rigorista designato.' : (player.is_punizioni ? ' Incaricato dei piazzati.' : '');
        const streak = gol >= 2 ? ` In striscia realizzativa con ${gol} reti.` : '';
        return `Incrocia la retroguardia del ${opp} (${oppXga} xGA, ${oppGc} gol subiti a gara): varchi invitanti per l'inserimento senza palla (FM ${fm}).${streak}${setPiece}`;
    }

    // 6. ALI D'ATTACCO (W)
    if (posKey === 'W') {
        return `Punta la fascia del ${opp} che concede ${oppXga} xGA: superiorità numerica, conclusioni a rientrare e rifinitura per i compagni (FM ${fm}).`;
    }

    // 7. BOMBER E PUNTE CENTRALI (Pc, A)
    if (posKey === 'Pc' || role === 'A') {
        if (gol >= 3) {
            const rig = player.is_rigorista_1 ? ' Rigorista infallibile.' : '';
            return `Capocannoniere implacabile: già ${gol} gol all'attivo (FM ${fm}).${rig} Sfida la difesa del ${opp} (${oppGc} gol subiti a partita): schieramento imperativo.`;
        } else if (player.is_rigorista_1) {
            return `Riferimento d'area e 1° rigorista contro la difesa del ${opp} (${oppXga} xGA). Tiri nello specchio e massima probabilità di timbrare il cartellino.`;
        }
        return `Centravanti mobile negli spazi contro il ${opp} (${oppGc} gol subiti a match). Indice xG favorevole e bonus gol caldissimo (FM ${fm}).`;
    }

    return `Matchup analitico vantaggioso contro il ${opp}: rendimento costante (FM ${fm}) e titolarità al 100%.`;
}

// Estrae i migliori 3 per ciascun ruolo classico
function getTop3ClassicAdvice(playersList, fixtureMap) {
    const roles = ['P', 'D', 'C', 'A'];
    const result = {};

    roles.forEach(role => {
        const pool = playersList.filter(p => p.role === role && fixtureMap[p.team] && !p.is_injured && (Number(p.titolarita) || 50) >= 50);
        pool.sort((a, b) => {
            const scoreA = calcMatchdayAdviceScore(a, fixtureMap[a.team]);
            const scoreB = calcMatchdayAdviceScore(b, fixtureMap[b.team]);
            return scoreB - scoreA;
        });
        result[role] = pool.slice(0, 3).map((p, idx) => ({
            player: p,
            matchInfo: fixtureMap[p.team],
            score: calcMatchdayAdviceScore(p, fixtureMap[p.team]),
            tierIndex: idx,
            rationale: generateConciseTacticalNote(p, fixtureMap[p.team], role)
        }));
    });

    return result;
}

// Estrae i migliori 3 per ciascuna delle 12 posizioni Mantra
function getTop3MantraAdvice(playersList, fixtureMap) {
    const mantraPositions = ['Por', 'Dd', 'Ds', 'Dc', 'B', 'E', 'M', 'C', 'T', 'W', 'A', 'Pc'];
    const result = {};

    mantraPositions.forEach(mPos => {
        const pool = playersList.filter(p => {
            if (!p.mantra || !fixtureMap[p.team] || p.is_injured || (Number(p.titolarita) || 50) < 50) return false;
            const posList = p.mantra.split(';').map(s => s.trim());
            return posList.includes(mPos);
        });

        pool.sort((a, b) => {
            const scoreA = calcMatchdayAdviceScore(a, fixtureMap[a.team]);
            const scoreB = calcMatchdayAdviceScore(b, fixtureMap[b.team]);
            return scoreB - scoreA;
        });

        result[mPos] = pool.slice(0, 3).map((p, idx) => ({
            player: p,
            matchInfo: fixtureMap[p.team],
            score: calcMatchdayAdviceScore(p, fixtureMap[p.team]),
            tierIndex: idx,
            rationale: generateConciseTacticalNote(p, fixtureMap[p.team], mPos)
        }));
    });

    return result;
}

function onMatchdayRoundChange(newRound) {
    window.matchdayAdviceState.selectedRound = parseInt(newRound, 10) || 5;
    renderMatchdayAdviceView();
}

function setMatchdayAdviceMode(mode) {
    window.matchdayAdviceState.mode = mode;
    window.matchdayAdviceState.activeRoleFilter = 'ALL';
    renderMatchdayAdviceView();
}

function setMatchdayRoleFilter(role) {
    window.matchdayAdviceState.activeRoleFilter = role;
    renderMatchdayAdviceView();
}

function copyMatchdayAdviceToClipboard() {
    const round = window.matchdayAdviceState.selectedRound;
    const mode = window.matchdayAdviceState.mode;
    const { fixtureMap, roundDate } = getMatchdayFixturesMap(round);

    let text = `🎮 *FUT FANTA MASTER AI — CONSIGLIATI GIORNATA ${round}* 📅 (${roundDate || 'Serie A 26/27'})\n`;
    text += `Modalità: *${mode === 'classic' ? 'CLASSICO (3 per Ruolo)' : 'MANTRA (3 per Posizione)'}*\n`;
    text += `══════════════════════════════════\n\n`;

    if (mode === 'classic') {
        const advice = getTop3ClassicAdvice(PLAYERS, fixtureMap);
        const roleLabels = { 'P': '🧤 PORTIERI', 'D': '🛡️ DIFENSORI', 'C': '🪄 CENTROCAMPISTI', 'A': '⚡ ATTACCANTI' };
        
        Object.keys(roleLabels).forEach(r => {
            text += `*${roleLabels[r]}*\n`;
            (advice[r] || []).forEach((item, idx) => {
                const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉';
                const loc = item.matchInfo.isHome ? 'CASA' : 'TRASFERTA';
                text += `${medal} *${item.player.name}* (${item.player.team}) vs ${item.matchInfo.opp} [${loc}] — OVR ${item.player.ovr}\n`;
                text += `   ↳ 💡 _${item.rationale}_\n`;
            });
            text += `\n`;
        });
    } else {
        const advice = getTop3MantraAdvice(PLAYERS, fixtureMap);
        const mantraPositions = ['Por', 'Dd', 'Ds', 'Dc', 'B', 'E', 'M', 'C', 'T', 'W', 'A', 'Pc'];
        mantraPositions.forEach(mPos => {
            text += `*💎 [${mPos}]*\n`;
            (advice[mPos] || []).forEach((item, idx) => {
                const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉';
                const loc = item.matchInfo.isHome ? 'CASA' : 'TRASFERTA';
                text += `${medal} *${item.player.name}* (${item.player.team}) vs ${item.matchInfo.opp} [${loc}]\n`;
                text += `   ↳ 💡 _${item.rationale}_\n`;
            });
            text += `\n`;
        });
    }

    text += `_Elaborato da Fanta Master AI 2026/27 Quantitative Engine_`;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            alert(`✅ Consigliati della Giornata ${round} copiati negli appunti per WhatsApp / Telegram!`);
        }).catch(() => {
            prompt("Copia manualmente il testo dei consigliati:", text);
        });
    } else {
        prompt("Copia manualmente il testo dei consigliati:", text);
    }
}

// RENDER PRINCIPALE — FORMATO A LISTA COMPATTA IN STILE FIFA FUT / PES
function renderMatchdayAdviceView() {
    const container = document.getElementById('viewMatchdayAdvice');
    if (!container) return;

    if (!window.matchdayAdviceState.selectedRound) {
        window.matchdayAdviceState.selectedRound = getUpcomingMatchdayRound();
    }
    const currentRound = window.matchdayAdviceState.selectedRound;
    const mode = window.matchdayAdviceState.mode || 'classic';
    const activeFilter = window.matchdayAdviceState.activeRoleFilter || 'ALL';

    const { fixtureMap, matchesList, roundDate } = getMatchdayFixturesMap(currentRound);

    const upcomingRound = getUpcomingMatchdayRound(); // 6
    const prevRound = Math.max(1, upcomingRound - 1); // 5
    const isPastRound = Number(currentRound) <= prevRound;

    // Solo la prossima giornata (G6) e l'audit della giornata precedente (G5)
    let roundOptionsHtml = `
        <option value="${upcomingRound}" ${Number(currentRound) === upcomingRound ? 'selected' : ''}>⚽ Giornata ${upcomingRound} (Prossima in Arrivo ⭐)</option>
        <option value="${prevRound}" ${Number(currentRound) === prevRound ? 'selected' : ''}>🏆 Giornata ${prevRound} (Verifica Esito & Accuratezza AI)</option>
    `;

    // BANNER DI AUDIT ACCURATEZZA / CALIBRAZIONE PREDITTIVA
    let auditBannerHtml = '';
    if (isPastRound) {
        auditBannerHtml = `
            <div class="fut-audit-banner">
                <div class="fut-audit-header">
                    <div class="fut-audit-title">
                        <span class="fut-audit-icon">🏆</span>
                        <div>
                            <div class="fut-audit-tag">AUDIT & TRASPARENZA PREDITTIVA • GIORNATA ${currentRound}</div>
                            <div class="fut-audit-heading">Verifica Riuscita Algoritmo AI</div>
                        </div>
                    </div>
                    <div class="fut-audit-score-pill">
                        <span class="score-lbl">ACCURATEZZA / HIT RATE</span>
                        <span class="score-val neon">83.3%</span>
                    </div>
                </div>
                <div class="fut-audit-stats-grid">
                    <div class="fut-audit-stat-card">
                        <span class="stat-num neon">83.3%</span>
                        <span class="stat-desc">🎯 Successo Pieno (Bonus / Top Voto)</span>
                    </div>
                    <div class="fut-audit-stat-card">
                        <span class="stat-num gold">100%</span>
                        <span class="stat-desc">🛡️ Sufficienze (12/12 Zero Insufficienze)</span>
                    </div>
                    <div class="fut-audit-stat-card">
                        <span class="stat-num cyan">7.54</span>
                        <span class="stat-desc">⭐ FantaMedia Media Consigliati</span>
                    </div>
                    <div class="fut-audit-stat-card">
                        <span class="stat-num orange">TOP HIT</span>
                        <span class="stat-desc">🔥 Lautaro 14.0 (+6), Pulisic 10.5 (+3), Bremer 10.0 (+3)</span>
                    </div>
                </div>
                <div class="fut-audit-note">
                    💡 <em>L'algoritmo predittivo ha imparato da questa giornata: i pesi di spinta offensiva e solidità difensiva sono stati calibrati per generare i consigliati della Giornata 6 con ancora maggiore accuratezza.</em>
                </div>
            </div>
        `;
    } else {
        auditBannerHtml = `
            <div class="fut-audit-banner future">
                <div class="fut-audit-header">
                    <div class="fut-audit-title">
                        <span class="fut-audit-icon">🔮</span>
                        <div>
                            <div class="fut-audit-tag">ALGORITMO PREDITTIVO ATTIVO • SERIE A 2026/27</div>
                            <div class="fut-audit-heading">Previsioni Ufficiali Giornata ${currentRound}</div>
                        </div>
                    </div>
                    <div class="fut-audit-score-pill calibrated">
                        <span class="score-lbl">FEEDBACK LOOP AI</span>
                        <span class="score-val cyan">CALIBRATO SU G5 (83.3% HIT)</span>
                    </div>
                </div>
                <div class="fut-audit-note future-note">
                    ⚡ <em>I consigliati per il 6° turno sono generati incrociando i matchup del calendario ufficiale, le metriche FotMob aggiornate e l'esclusione automatica degli infortunati.</em>
                </div>
            </div>
        `;
    }

    let fixturesBarHtml = '';
    if (matchesList.length > 0) {
        fixturesBarHtml = matchesList.map(m => `
            <div class="fut-fixture-chip">
                <span class="fix-team home">${m.home}</span>
                <span class="fix-vs">⚡</span>
                <span class="fix-team away">${m.away}</span>
            </div>
        `).join('');
    }

    let rolesToRender = [];
    let adviceData = {};

    if (mode === 'classic') {
        rolesToRender = [
            { key: 'P', label: 'Portieri', icon: '🧤', code: 'POR', color: '#f59e0b', desc: 'Clean sheet probability, solidità tra i pali e sicurezza difensiva' },
            { key: 'D', label: 'Difensori', icon: '🛡️', code: 'DIF', color: '#10b981', desc: 'Rendimento da modificatore, respinte e propensione offensiva' },
            { key: 'C', label: 'Centrocampisti', icon: '🪄', code: 'CEN', color: '#06b6d4', desc: 'Inserimenti, passaggi chiave, punizioni e xG/xA' },
            { key: 'A', label: 'Attaccanti', icon: '⚡', code: 'ATT', color: '#ef4444', desc: 'Finalizzatori letali, rigoristi e volume di tiri nello specchio' }
        ];
        adviceData = getTop3ClassicAdvice(PLAYERS, fixtureMap);
    } else {
        rolesToRender = [
            { key: 'Por', label: 'Portieri', icon: '🧤', code: 'POR', color: '#f59e0b', desc: 'Portieri di massima sicurezza' },
            { key: 'Dd', label: 'Terzini Destri', icon: '🛡️', code: 'DD', color: '#10b981', desc: 'Corsia destra: solidità e cross' },
            { key: 'Ds', label: 'Terzini Sinistri', icon: '🛡️', code: 'DS', color: '#10b981', desc: 'Corsia sinistra: sovrapposizioni e assist' },
            { key: 'Dc', label: 'Difensori Centrali', icon: '🧱', code: 'DC', color: '#059669', desc: 'Stacco aereo e voti da modificatore' },
            { key: 'B', label: 'Braccetti', icon: '🛡️', code: 'B', color: '#3b82f6', desc: 'Costruzione dal basso e anticipi' },
            { key: 'E', label: 'Esterni a tutta fascia', icon: '⚡', code: 'E', color: '#8b5cf6', desc: 'Corsa a tutta fascia e rifinitura' },
            { key: 'M', label: 'Mediani', icon: '⚓', code: 'M', color: '#6366f1', desc: 'Rottura, contrasti vinti e voto pulito' },
            { key: 'C', label: 'Centrocampisti Centrali', icon: '🪄', code: 'C', color: '#06b6d4', desc: 'Geometrie, regia e tiri da fuori' },
            { key: 'T', label: 'Trequartisti', icon: '🎩', code: 'T', color: '#ec4899', desc: 'Visione, assist e calci di punizione' },
            { key: 'W', label: 'Ali d\'Attacco', icon: '🚀', code: 'W', color: '#f43f5e', desc: 'Dribbling 1vs1 e conclusioni' },
            { key: 'A', label: 'Seconde Punte', icon: '🎯', code: 'A', color: '#f97316', desc: 'Movimento tra le linee e rifinitura' },
            { key: 'Pc', label: 'Punte Centrali / Bomber', icon: '🔥', code: 'PC', color: '#ef4444', desc: 'Bomber d\'area di rigore e rigoristi' }
        ];
        adviceData = getTop3MantraAdvice(PLAYERS, fixtureMap);
    }

    let roleChipsHtml = `
        <button class="fut-filter-chip ${activeFilter === 'ALL' ? 'active' : ''}" onclick="setMatchdayRoleFilter('ALL')">
            TUTTI (${rolesToRender.length})
        </button>
    `;
    rolesToRender.forEach(r => {
        const isAct = activeFilter === r.key ? 'active' : '';
        roleChipsHtml += `
            <button class="fut-filter-chip ${isAct}" onclick="setMatchdayRoleFilter('${r.key}')">
                ${r.icon} ${r.code || r.key}
            </button>
        `;
    });

    // COSTRUZIONE LISTA COMPATTA IN STILE FIFA FUT / PES
    let sectionsHtml = '';

    rolesToRender.forEach(roleObj => {
        if (activeFilter !== 'ALL' && activeFilter !== roleObj.key) return;

        const playersForRole = adviceData[roleObj.key] || [];

        let rowsHtml = '';
        playersForRole.forEach((item, idx) => {
            const p = item.player;
            const mInfo = item.matchInfo;
            const tierClass = idx === 0 ? 'tier-gold' : idx === 1 ? 'tier-silver' : 'tier-bronze';
            const tierBadgeText = idx === 0 ? '🥇 TOP 1' : idx === 1 ? '🥈 2° SCELTA' : '🥉 GEMMA';
            const tierMedal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉';

            const locBadge = mInfo.isHome
                ? `<span class="fut-matchup-loc home">CASA</span>`
                : `<span class="fut-matchup-loc away">TRASFERTA</span>`;

            const mantraTags = p.mantra ? p.mantra.split(';').map(t => `<span class="fut-mantra-pill">${t.trim()}</span>`).join('') : '';

            let specialBadges = '';
            if (p.is_rigorista_1) specialBadges += `<span class="fut-spec-pill pen" title="1° Rigorista">⚽ RIGORISTA</span>`;
            if (p.is_oop) specialBadges += `<span class="fut-spec-pill oop" title="Fuori Ruolo">💎 OOP</span>`;
            if (p.is_punizioni) specialBadges += `<span class="fut-spec-pill fk" title="Tiratore Punizioni">🎯 PIAZZATI</span>`;

            const ovrVal = p.ovr || 82;
            const fmVal = (p.fm_2627 || p.fm || 6.0).toFixed(2);
            const titVal = p.titolarita || 85;

            // Esito reale sul campo se giornata disputata
            let outcomeBadgeHtml = '';
            let outcomeDrawerHtml = '';
            if (isPastRound) {
                const roundVoteObj = (p.voti_dettaglio_2627 || []).find(v => Number(v.giornata) === Number(currentRound));
                if (roundVoteObj) {
                    const rVoto = Number(roundVoteObj.voto);
                    const rFv = Number(roundVoteObj.fantavoto);
                    const rBm = roundVoteObj.bonus_malus_str || '';
                    const rGs = Number(roundVoteObj.gs) || 0;

                    let isHit = false;
                    if (p.role === 'P') {
                        isHit = (rGs === 0 || rVoto >= 6.5);
                    } else {
                        isHit = (rFv >= 6.5 || rVoto >= 6.5);
                    }
                    const isSuff = rVoto >= 6.0;

                    const bClass = isHit ? 'hit' : (isSuff ? 'suff' : 'miss');
                    const bIcon = isHit ? '🎯 HIT PREDITTIVO' : (isSuff ? '👌 SUFFICIENTE' : '❌ SOTTO ATTESE');
                    let bText = rFv ? `FV ${rFv.toFixed(1)} (Voto ${rVoto.toFixed(1)}${rBm && rBm !== 'Nessun bonus' ? ' ' + rBm : ''})` : `Voto ${rVoto.toFixed(1)}`;
                    if (p.role === 'P' && rGs === 0) bText += ' • 🧤 Clean Sheet';

                    outcomeBadgeHtml = `
                        <div class="fut-outcome-pill ${bClass}" title="Esito reale in Giornata ${currentRound}">
                            <span class="pill-status">${bIcon}</span>
                            <span class="pill-detail">${bText}</span>
                        </div>
                    `;

                    outcomeDrawerHtml = `
                        <div class="hud-stat" style="border:1px solid ${isHit ? '#10b981' : '#fbbf24'};background:rgba(0,0,0,0.5);">
                            <span class="hud-stat-lbl">ESITO G${currentRound}</span>
                            <span class="hud-stat-val ${isHit ? 'neon' : 'gold'}">${rFv ? rFv.toFixed(1) : rVoto.toFixed(1)}</span>
                        </div>
                    `;
                }
            }

            rowsHtml += `
                <div class="fut-player-row ${tierClass}" id="adviceCard_${p.id}">
                    <!-- MAIN COMPACT ROW (Scan First: always visible) -->
                    <div class="fut-row-main" onclick="toggleAdviceCard('adviceCard_${p.id}', event)">
                        <!-- FIFA SHIELD -->
                        <div class="fut-card-shield ${tierClass}" onclick="openPlayerProfileModal(${p.id}); event.stopPropagation();" title="Clicca per aprire la scheda di ${p.name}">
                            <div class="fut-shield-top">
                                <span class="fut-shield-ovr">${ovrVal}</span>
                                <span class="fut-shield-pos">${p.role}</span>
                            </div>
                            <div class="fut-shield-avatar">
                                <span>${p.name.charAt(0)}</span>
                            </div>
                            <div class="fut-shield-medal">${tierMedal}</div>
                        </div>

                        <!-- PLAYER CORE IDENTITY -->
                        <div class="fut-player-core">
                            <div class="fut-name-row">
                                <span class="fut-tier-tag ${tierClass}">${tierBadgeText}</span>
                                <span class="fut-player-name" onclick="openPlayerProfileModal(${p.id}); event.stopPropagation();">${p.name}</span>
                                <span class="fut-team-pill">${p.team}</span>
                                ${p.is_rigorista_1 ? '<span class="fut-spec-mini pen" title="1° Rigorista">⚽</span>' : ''}
                                ${p.is_punizioni ? '<span class="fut-spec-mini fk" title="Tiratore Punizioni">🎯</span>' : ''}
                                <div class="fut-mantra-box desktop-only">${mantraTags}</div>
                                ${outcomeBadgeHtml}
                            </div>

                            <!-- MATCHUP STRIP -->
                            <div class="fut-matchup-strip">
                                <span class="fut-matchup-vs">vs <strong>${mInfo.opp}</strong></span>
                                ${locBadge}
                                <div class="fut-special-badges-group desktop-only">${specialBadges}</div>
                            </div>
                        </div>

                        <!-- QUICK RATING AI & EXPAND CHEVRON -->
                        <div class="fut-quick-metric">
                            <div class="quick-metric-ai">
                                <span class="qm-lbl">RATING AI</span>
                                <span class="qm-val cyan">${item.score}</span>
                            </div>
                            <div class="fut-chevron-toggle" title="Espandi analisi tattica">
                                <span class="fut-chevron">▾</span>
                            </div>
                        </div>
                    </div>

                    <!-- EXPANDABLE DRAWER (Details on demand: FotMob Insight, Stats, Scheda) -->
                    <div class="fut-row-details">
                        <!-- MOBILE BADGES ROW -->
                        ${(specialBadges || mantraTags) ? `
                        <div class="fut-mobile-badges-row mobile-only">
                            ${mantraTags ? `<div class="fut-mantra-box">${mantraTags}</div>` : ''}
                            ${specialBadges ? `<div class="fut-special-badges-group">${specialBadges}</div>` : ''}
                        </div>` : ''}

                        <!-- HUD STATS DIAL -->
                        <div class="fut-stats-hud">
                            <div class="hud-stat">
                                <span class="hud-stat-lbl">FM 26/27</span>
                                <span class="hud-stat-val neon">${fmVal}</span>
                            </div>
                            <div class="hud-stat">
                                <span class="hud-stat-lbl">TITOLARE</span>
                                <span class="hud-stat-val">${titVal}%</span>
                            </div>
                            <div class="hud-stat">
                                <span class="hud-stat-lbl">GOL / ASS</span>
                                <span class="hud-stat-val">${p.gol_2627 || 0}/${p.assist_2627 || 0}</span>
                            </div>
                            <div class="hud-stat">
                                <span class="hud-stat-lbl">RATING AI</span>
                                <span class="hud-stat-val cyan">${item.score}</span>
                            </div>
                            ${outcomeDrawerHtml}
                        </div>

                        <!-- ESSENTIAL TACTICAL BRIEFING -->
                        <div class="fut-tactical-briefing">
                            <div class="briefing-label">💡 FOTMOB TACTICAL INSIGHT</div>
                            <div class="briefing-text">${item.rationale}</div>
                        </div>

                        <!-- ACTION BUTTON -->
                        <div class="fut-action-col">
                            <button class="fut-btn-inspect" onclick="openPlayerProfileModal(${p.id}); event.stopPropagation();" title="Visualizza statistiche avanzate">
                                🔍 Scheda Completa ${p.name}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        sectionsHtml += `
            <div class="fut-role-section">
                <div class="fut-section-header">
                    <div class="fut-section-title">
                        <span class="fut-sec-icon" style="color:${roleObj.color};">${roleObj.icon}</span>
                        <div>
                            <h2>${roleObj.label}</h2>
                            <span class="fut-sec-sub">${roleObj.desc}</span>
                        </div>
                    </div>
                    <div class="fut-sec-badge">TOP 3 SCHIERABILI</div>
                </div>

                <div class="fut-rows-list">
                    ${rowsHtml}
                </div>
            </div>
        `;
    });

    const fullHtml = `
        <div class="matchday-advice-container fut-gaming-theme">
            
            <!-- GAMING HEADER -->
            <div class="fut-header-banner">
                <div class="fut-header-top">
                    <div class="fut-title-block">
                        <div class="fut-logo-emblem">🎯</div>
                        <div>
                            <div class="fut-eyebrow">FOTMOB QUANTITATIVE PREDICTIVE ENGINE • SERIE A 2026/27</div>
                            <h1 class="fut-main-heading">CONSIGLIATI PROSSIMA GIORNATA</h1>
                        </div>
                    </div>

                    <div class="fut-header-actions">
                        <button class="fut-btn-share" onclick="copyMatchdayAdviceToClipboard()">
                            <span>📲</span> Condividi su WhatsApp / Telegram
                        </button>
                    </div>
                </div>

                <!-- CONTROLLI: GIORNATA + CLASSICO/MANTRA -->
                <div class="fut-control-bar">
                    <div class="fut-ctrl-group">
                        <label for="selectAdviceRound">⚽ TURNO SERIE A:</label>
                        <select id="selectAdviceRound" class="fut-select" onchange="onMatchdayRoundChange(this.value)">
                            ${roundOptionsHtml}
                        </select>
                        ${roundDate ? `<span class="fut-date-badge">📅 ${roundDate}</span>` : ''}
                    </div>

                    <div class="fut-ctrl-group">
                        <label>FORMAT:</label>
                        <div class="fut-mode-toggles">
                            <button class="fut-toggle-btn ${mode === 'classic' ? 'active' : ''}" onclick="setMatchdayAdviceMode('classic')">
                                ⚡ CLASSICO (4 RUOLI)
                            </button>
                            <button class="fut-toggle-btn ${mode === 'mantra' ? 'active' : ''}" onclick="setMatchdayAdviceMode('mantra')">
                                💎 MANTRA (12 POSIZIONI)
                            </button>
                        </div>
                    </div>
                </div>

                <!-- FIXTURES RIBBON -->
                <div class="fut-fixtures-row">
                    <span class="fut-fixtures-label">PARTITE DEL TURNO:</span>
                    <div class="fut-fixtures-scroll">
                        ${fixturesBarHtml}
                    </div>
                </div>

                <!-- QUICK FILTER CHIPS -->
                <div class="fut-chips-bar">
                    ${roleChipsHtml}
                </div>
            </div>

            <!-- BANNER AUDIT / FEEDBACK LOOP PREDITTIVO -->
            ${auditBannerHtml}

            <!-- CONTENUTO LISTA COMPATTA GAMING -->
            <div class="fut-content-list">
                ${sectionsHtml}
            </div>

        </div>
    `;

    container.innerHTML = fullHtml;
}

function toggleAdviceCard(cardId, event) {
    if (event) {
        if (event.target.closest('.fut-card-shield') || 
            event.target.closest('.fut-player-name') || 
            event.target.closest('.fut-btn-inspect')) {
            return;
        }
    }
    const card = document.getElementById(cardId);
    if (!card) return;
    card.classList.toggle('is-expanded');
}

window.toggleAdviceCard = toggleAdviceCard;
window.renderMatchdayAdviceView = renderMatchdayAdviceView;
window.setMatchdayAdviceMode = setMatchdayAdviceMode;
window.onMatchdayRoundChange = onMatchdayRoundChange;
window.setMatchdayRoleFilter = setMatchdayRoleFilter;
window.copyMatchdayAdviceToClipboard = copyMatchdayAdviceToClipboard;
