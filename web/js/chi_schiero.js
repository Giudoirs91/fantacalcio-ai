// ==============================================================================
// TOOL "CHI SCHIERO?" — HEAD-TO-HEAD WEEKEND DECISION ENGINE (1VS1)
// Serie A 2026/27 — FantaMaster AI
// ==============================================================================

window.chiSchieroState = {
    round: null,       // Calcolato dinamicamente da getUpcomingMatchdayRound()
    playerAId: null,
    playerBId: null,
    roleFilter: 'ALL',
    searchA: '',
    searchB: ''
};

function initChiSchieroState() {
    if (window.chiSchieroState.round === null) {
        if (typeof getUpcomingMatchdayRound === 'function') {
            window.chiSchieroState.round = getUpcomingMatchdayRound();
        } else {
            window.chiSchieroState.round = 6;
        }
    }

    if (!window.chiSchieroState.playerAId || !window.chiSchieroState.playerBId) {
        if (typeof PLAYERS !== 'undefined' && Array.isArray(PLAYERS) && PLAYERS.length > 0) {
            // Default di riferimento: Politano vs Orsolini (due ali offensive C da bonus)
            const pol = PLAYERS.find(p => p.name.toLowerCase().includes('politano'));
            const ors = PLAYERS.find(p => p.name.toLowerCase().includes('orsolini'));
            const lau = PLAYERS.find(p => p.name.toLowerCase().includes('martinez l'));
            const hoj = PLAYERS.find(p => p.name.toLowerCase().includes('hojlund'));

            if (pol && ors) {
                window.chiSchieroState.playerAId = pol.id;
                window.chiSchieroState.playerBId = ors.id;
            } else if (lau && hoj) {
                window.chiSchieroState.playerAId = lau.id;
                window.chiSchieroState.playerBId = hoj.id;
            } else {
                window.chiSchieroState.playerAId = PLAYERS[0].id;
                window.chiSchieroState.playerBId = PLAYERS[1].id;
            }
        }
    }
}

function getChiSchieroFixtureForPlayer(player, roundNum) {
    if (!player || !player.team) return null;
    let matchFound = null;

    if (typeof OFFICIAL_CALENDAR_2026_27 !== 'undefined' && Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        const roundData = OFFICIAL_CALENDAR_2026_27.find(r => Number(r.giornata) === Number(roundNum));
        if (roundData && Array.isArray(roundData.matches)) {
            const m = roundData.matches.find(match => match.home === player.team || match.away === player.team);
            if (m) {
                const isHome = m.home === player.team;
                const opp = isHome ? m.away : m.home;
                matchFound = {
                    home: m.home,
                    away: m.away,
                    isHome: isHome,
                    opp: opp,
                    label: isHome ? `${m.home} vs ${m.away} (Casa)` : `${m.home} vs ${m.away} (Trasferta)`,
                    shortLabel: isHome ? `vs ${m.away} 🏠` : `@ ${m.home} ✈️`
                };
            }
        }
    }
    return matchFound;
}

// ALGORITMO PREDITTIVO SCIENTIFICO CALIBRATO
function calculateChiSchieroScore(player, roundNum) {
    if (!player) return { score: 0, factors: [] };

    const fixture = getChiSchieroFixtureForPlayer(player, roundNum);
    const factors = [];

    // 1. CARATURA TECNICA & BASELINE BILANCIATA (65% xFM/FM + 35% OVR Intrinseco)
    // Un top player affermato (OVR 95+) mantiene una pericolosità superiore anche se reduce da partite transitorie
    const ovr = Number(player.ovr) || 75;
    const ovrScore = (ovr / 10.0); // es. 98 -> 9.8, 77 -> 7.7
    
    let perfScore = 6.0;
    if (player.xfm && !isNaN(player.xfm)) {
        perfScore = Number(player.xfm);
    } else if (player.fm_2627) {
        perfScore = Number(player.fm_2627);
    } else {
        perfScore = ovrScore * 0.72;
    }

    // Baseline: 65% Rendimento atteso + 35% Status/Qualità intrinseca (scala ~55-95)
    let dynamicScore = (perfScore * 6.5) + (ovrScore * 3.5);
    factors.push({ name: 'Caratura & Expected FantaMedia (xFM)', val: `${perfScore.toFixed(2)} xFM • OVR ${ovr}`, positive: true });

    // 2. TITOLARITÀ & STATUS IN ROSA
    const tit = (player.titolarita !== undefined && player.titolarita !== null) ? Number(player.titolarita) : 70;
    if (player.is_injured) {
        dynamicScore -= 32;
        factors.push({ name: 'Infortunio / Rientro da valutare', val: '-32 pt 🩹', positive: false });
    } else if (tit >= 85) {
        dynamicScore += 4;
        factors.push({ name: `Titolarissimo Garantito (${tit}%)`, val: '+4 pt 🔒', positive: true });
    } else if (tit >= 65) {
        dynamicScore += 2;
        factors.push({ name: `Titolare Affidabile (${tit}%)`, val: '+2 pt 🛡️', positive: true });
    } else if (tit >= 40) {
        // Se è un top player offensivo o rigorista, subentra quasi sempre ed è altamente pericoloso
        if (player.ovr >= 85 || player.is_rigorista_1) {
            dynamicScore -= 2;
            factors.push({ name: `Staffetta / Spezzone decisivo (${tit}%)`, val: '-2 pt ⚡', positive: false });
        } else {
            dynamicScore -= 5;
            factors.push({ name: `Ballottaggio Rischioso (${tit}%)`, val: '-5 pt 🔄', positive: false });
        }
    } else {
        dynamicScore -= 12;
        factors.push({ name: `Rischio s.v. / Panchina (<40%)`, val: '-12 pt 🪑', positive: false });
    }

    // 3. MATCHUP DIFENSIVO AVVERSARIO & FATTORE CAMPO
    if (fixture) {
        const oppStats = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[fixture.opp]) ? TEAM_STATS_DB[fixture.opp] : null;

        // Fattore Campo (+2.5 pt casa, -1.5 pt trasferta)
        if (fixture.isHome) {
            dynamicScore += 2.5;
            factors.push({ name: 'Fattore Campo (Gioca in Casa)', val: '+2.5 pt 🏠', positive: true });
        } else {
            dynamicScore -= 1.5;
            factors.push({ name: 'Impegno in Trasferta', val: '-1.5 pt ✈️', positive: false });
        }

        if (oppStats) {
            const oppXga = Number(oppStats.xga_team) || 7.0;
            const oppGc = Number(oppStats.goals_conceded_match) || 1.3;

            if (player.role === 'P') {
                // Portieri: forza d'attacco rivale
                const oppXg = Number(oppStats.xg_team) || 7.0;
                if (oppXg <= 5.5) {
                    dynamicScore += 6;
                    factors.push({ name: `Attacco rivale poco prolifico (${oppStats.squadra}: xG ${oppXg.toFixed(1)})`, val: '+6 pt 🧤', positive: true });
                } else if (oppXg >= 9.0) {
                    dynamicScore -= 6;
                    factors.push({ name: `Attacco rivale prolifico (${oppStats.squadra}: xG ${oppXg.toFixed(1)})`, val: '-6 pt ⚠️', positive: false });
                }
            } else {
                // Giocatori di movimento: vulnerabilità difesa rivale
                // es. Lecce (xGA 11.6, 2.0 gol subiti) -> Difesa Fragile (+6.5 pt)
                // es. Frosinone / Juventus (0.8 gol subiti) -> Difesa Blindata (-4 pt)
                if (oppGc <= 0.85) {
                    dynamicScore -= 4;
                    factors.push({ name: `Difesa rivale blindata (${oppStats.squadra}: solo ${oppGc.toFixed(1)} gol subiti/partita)`, val: '-4 pt 🛡️', positive: false });
                } else if (oppGc >= 1.6 || oppXga >= 9.5) {
                    dynamicScore += 6.5;
                    factors.push({ name: `Difesa rivale fragile (${oppStats.squadra}: ${oppGc.toFixed(1)} gol subiti/partita)`, val: '+6.5 pt 🎯', positive: true });
                } else if (oppGc >= 1.3 || oppXga >= 7.0) {
                    dynamicScore += 2.5;
                    factors.push({ name: `Difesa rivale permeabile (${oppStats.squadra})`, val: '+2.5 pt ⚽', positive: true });
                } else {
                    factors.push({ name: `Difesa rivale nella media (${oppStats.squadra})`, val: 'Neutro', positive: true });
                }

                // 4. POTENZIALE DI RISCATTO (Bounce-Back Factor):
                // Top player (OVR >= 85) a secco di bonus nelle prime gare che affrontano difese fragili
                if (player.ovr >= 85 && (player.gol_2627 || 0) === 0 && (oppXga >= 8.5 || oppGc >= 1.6)) {
                    dynamicScore += 4.5;
                    factors.push({ name: `Potenziale di Riscatto Elevato: Top player a secco contro retroguardia debole (${oppStats.squadra})`, val: '+4.5 pt 🚀', positive: true });
                }
            }
        }
    }

    // 5. BONUS DA FERMO (Rigori & Piazzati)
    if (player.is_rigorista_1 || player.rigorista_val === '1° Rigorista') {
        dynamicScore += 5;
        factors.push({ name: '1° Rigorista Ufficiale (+3 dal dischetto)', val: '+5 pt 👑', positive: true });
    } else if (player.is_rigorista_2 || player.rigorista_val === '2° Rigorista') {
        dynamicScore += 2;
        factors.push({ name: '2° Rigorista Designato', val: '+2 pt 🎯', positive: true });
    }

    if (player.is_punizioni || player.is_corner) {
        dynamicScore += 2.5;
        factors.push({ name: 'Specialista Piazzati & Corner (Bonus xA)', val: '+2.5 pt 📐', positive: true });
    }

    // 6. CARTELLINI & DISCIPLINA
    const amm = Number(player.amm_2627) || 0;
    const esp = Number(player.esp_2627) || 0;
    if (esp > 0) {
        dynamicScore -= 3;
        factors.push({ name: 'Rischio Malus Disciplinare (Rosso recente)', val: '-3 pt 🟥', positive: false });
    } else if (amm >= 2) {
        dynamicScore -= 1;
        factors.push({ name: 'Propenso al cartellino giallo', val: '-1 pt 🟨', positive: false });
    }

    return {
        score: Math.max(10, Math.round(dynamicScore * 10) / 10),
        factors: factors,
        fixture: fixture
    };
}

function calculateChiSchieroVerdict(playerA, playerB, roundNum) {
    if (!playerA || !playerB) return null;

    const dataA = calculateChiSchieroScore(playerA, roundNum);
    const dataB = calculateChiSchieroScore(playerB, roundNum);

    const diff = dataA.score - dataB.score;
    
    // Funzione Sigmoide Calibrata con Temperatura T = 13:
    // Evita divari assurdi (89-11) tra giocatori entrambi validi di Serie A
    // diff = 0 -> 50% vs 50%
    // diff = 3 -> 56% vs 44%
    // diff = 6 -> 61% vs 39%
    // diff = 10 -> 68% vs 32%
    // diff = 16 -> 78% vs 22%
    const probA = 1 / (1 + Math.exp(-diff / 13));
    let pctA = Math.round(probA * 100);
    pctA = Math.max(12, Math.min(88, pctA));
    const pctB = 100 - pctA;

    let verdictTitle = '';
    let verdictSubtitle = '';
    let winnerId = null;

    if (pctA >= 58) {
        verdictTitle = `🏆 CONSIGLIATO: ${playerA.name.toUpperCase()} (${pctA}%)`;
        verdictSubtitle = `L'algoritmo predittivo consiglia ${playerA.name} per la Giornata ${roundNum}, con un margine di rendimento atteso superiore.`;
        winnerId = playerA.id;
    } else if (pctB >= 58) {
        verdictTitle = `🏆 CONSIGLIATO: ${playerB.name.toUpperCase()} (${pctB}%)`;
        verdictSubtitle = `L'algoritmo predittivo consiglia ${playerB.name} per la Giornata ${roundNum}, con un margine di rendimento atteso superiore.`;
        winnerId = playerB.id;
    } else {
        verdictTitle = `⚖️ BALLOTTAGGIO EQUILIBRATO: ${playerA.name} (${pctA}%) vs ${playerB.name} (${pctB}%)`;
        verdictSubtitle = `Entrambi i profili offrono un potenziale molto vicino per la Giornata ${roundNum}. La scelta dipende dalla tua strategia di rischio.`;
        winnerId = diff >= 0 ? playerA.id : playerB.id;
    }

    // Costruzione 3 motivazioni in linguaggio naturale
    const bullets = [];
    const winnerPlayer = (winnerId === playerA.id) ? playerA : playerB;
    const loserPlayer = (winnerId === playerA.id) ? playerB : playerA;
    const winnerData = (winnerId === playerA.id) ? dataA : dataB;
    const loserData = (winnerId === playerA.id) ? dataB : dataA;

    // Bullet 1: Matchup avversario e fattore campo
    if (winnerData.fixture && loserData.fixture) {
        const oppWin = (typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[winnerData.fixture.opp]) ? TEAM_STATS_DB[winnerData.fixture.opp] : null;
        if (oppWin && (Number(oppWin.goals_conceded_match) >= 1.6 || Number(oppWin.xga_team) >= 9.0)) {
            bullets.push(`🎯 <b>Matchup Favorevole:</b> ${winnerPlayer.name} affronta la vulnerabile retroguardia del ${oppWin.squadra} (${Number(oppWin.goals_conceded_match).toFixed(1)} gol concessi/gara), con elevata probabilità di bonus.`);
        } else if (winnerData.fixture.isHome && !loserData.fixture.isHome) {
            bullets.push(`🏠 <b>Fattore Campo:</b> ${winnerPlayer.name} gioca in casa (${winnerData.fixture.shortLabel}), mentre ${loserPlayer.name} è impegnato in trasferta (${loserData.fixture.shortLabel}).`);
        } else {
            bullets.push(`⚽ <b>Incrocio di Giornata:</b> ${winnerPlayer.name} scende in campo in ${winnerData.fixture.label}, con una proiezione offensiva superiore.`);
        }
    }

    // Bullet 2: Rigori / Piazzati / Titolarità
    const isWPenalty = winnerPlayer.is_rigorista_1 || winnerPlayer.rigorista_val === '1° Rigorista';
    const isLPenalty = loserPlayer.is_rigorista_1 || loserPlayer.rigorista_val === '1° Rigorista';
    if (isWPenalty && !isLPenalty) {
        bullets.push(`👑 <b>Bonus Dischetto (+3):</b> ${winnerPlayer.name} è il 1° rigorista designato della propria squadra, garantendo un extra-valore statistico su palla inattiva.`);
    } else if (winnerPlayer.is_punizioni || winnerPlayer.is_corner) {
        bullets.push(`📐 <b>Piazzati & Assist:</b> ${winnerPlayer.name} batte calci piazzati e corner, aumentando l'Expected Assist (xA).`);
    } else if (winnerPlayer.titolarita >= 80 && loserPlayer.titolarita < 65) {
        bullets.push(`🔒 <b>Garanzia di Titolarità:</b> ${winnerPlayer.name} vanta una presenza stimata del ${winnerPlayer.titolarita}% dall'1', contro il ${loserPlayer.titolarita || 0}% di ${loserPlayer.name}.`);
    } else {
        bullets.push(`📈 <b>Indice di Impatto:</b> ${winnerPlayer.name} garantisce una continuità di rendimento superiore nelle dinamiche della partita.`);
    }

    // Bullet 3: Caratura & Expected FantaMedia (xFM)
    const xfmW = Number(winnerPlayer.xfm) || Number(winnerPlayer.fm_2627) || 6.0;
    const xfmL = Number(loserPlayer.xfm) || Number(loserPlayer.fm_2627) || 6.0;
    if (winnerPlayer.ovr >= 90 && loserPlayer.ovr < 85) {
        bullets.push(`⭐ <b>Caratura da Top Player:</b> ${winnerPlayer.name} (OVR ${winnerPlayer.ovr}) ha una qualità realizzativa superiore nel lungo termine rispetto a ${loserPlayer.name} (OVR ${loserPlayer.ovr}).`);
    } else {
        bullets.push(`💎 <b>Expected FantaMedia:</b> ${winnerPlayer.name} produce un volume di gioco atteso pari a <b>${xfmW.toFixed(2)} xFM</b> contro i ${xfmL.toFixed(2)} xFM di ${loserPlayer.name}.`);
    }

    const analysisA = buildDetailedPlayerProsAndCons(playerA, dataA);
    const analysisB = buildDetailedPlayerProsAndCons(playerB, dataB);
    const strategy = buildStrategicVerdictGuidance(playerA, dataA, playerB, dataB, roundNum);

    return {
        playerA,
        playerB,
        dataA,
        dataB,
        pctA,
        pctB,
        winnerId,
        verdictTitle,
        verdictSubtitle,
        bullets,
        analysisA,
        analysisB,
        strategy
    };
}

function buildDetailedPlayerProsAndCons(player, data) {
    const pros = [];
    const cons = [];
    const fixture = data.fixture;
    const oppStats = (fixture && typeof TEAM_STATS_DB !== 'undefined' && TEAM_STATS_DB[fixture.opp]) ? TEAM_STATS_DB[fixture.opp] : null;

    // 1. FATTORE CAMPO
    if (fixture) {
        if (fixture.isHome) {
            pros.push({
                icon: '🏠',
                title: 'Fattore Campo Favorevole',
                desc: `Gioca in casa (${fixture.shortLabel}) davanti al proprio pubblico. Storicamente le squadre di casa producono +18% di occasioni da gol.`
            });
        } else {
            cons.push({
                icon: '✈️',
                title: 'Impegno in Trasferta',
                desc: `Gioca fuori casa (${fixture.shortLabel}). Storicamente la produzione offensiva e il baricentro medio calano del 12% in trasferta.`
            });
        }

        // 2. MATCHUP DIFENSIVO AVVERSARIO
        if (oppStats) {
            const oppGc = Number(oppStats.goals_conceded_match) || 1.3;
            const oppXga = Number(oppStats.xga_team) || 7.0;

            if (player.role === 'P') {
                const oppXg = Number(oppStats.xg_team) || 7.0;
                if (oppXg <= 5.5) {
                    pros.push({
                        icon: '🧤',
                        title: 'Alta Probabilità di Clean Sheet',
                        desc: `L'attacco del ${oppStats.squadra} è tra i meno prolifici della Serie A (appena ${oppXg.toFixed(1)} xG prodotti in 5 turni).`
                    });
                } else if (oppXg >= 9.0) {
                    cons.push({
                        icon: '⚠️',
                        title: 'Rischio Malus Gol Subiti',
                        desc: `L'attacco del ${oppStats.squadra} è altamente prolifico (${oppXg.toFixed(1)} xG e ${oppStats.big_chances || 15} grandi occasioni create).`
                    });
                }
            } else {
                if (oppGc <= 0.85) {
                    cons.push({
                        icon: '🛡️',
                        title: `Muro Difensivo Rivale (${oppStats.squadra})`,
                        desc: `Il ${oppStats.squadra} è tra le difese più ermetiche della Serie A (solo ${oppGc.toFixed(1)} gol subiti a gara). Spazi ridotti al minimo per le punte.`
                    });
                } else if (oppGc >= 1.6 || oppXga >= 9.5) {
                    pros.push({
                        icon: '🎯',
                        title: `Difesa Rivale Fragile (${oppStats.squadra})`,
                        desc: `Il ${oppStats.squadra} concede ben ${oppGc.toFixed(1)} gol a partita (${oppXga.toFixed(1)} xGA): terreno ideale per colpire.`
                    });
                } else {
                    pros.push({
                        icon: '⚖️',
                        title: `Difesa Rivale nella Media (${oppStats.squadra})`,
                        desc: `Il ${oppStats.squadra} concede ${oppGc.toFixed(1)} gol a partita. Partita equilibrata con normali possibilità di manovra.`
                    });
                }
            }
        }
    }

    // 3. TITOLARITÀ E MINUTAGGIO
    const tit = (player.titolarita !== undefined && player.titolarita !== null) ? Number(player.titolarita) : 70;
    if (player.is_injured) {
        cons.push({
            icon: '🩹',
            title: 'Infortunio / Rientro Incerto',
            desc: `Calciatore alle prese con noie fisiche. Alto rischio di mancata convocazione o minutaggio nullo.`
        });
    } else if (tit >= 85) {
        pros.push({
            icon: '🔒',
            title: `Titolarità Blindata (${tit}%)`,
            desc: `Inamovibile nello scacchiere tattico, garantisce 75-90 minuti in campo senza rischio s.v.`
        });
    } else if (tit >= 40) {
        cons.push({
            icon: '🔄',
            title: `Ballottaggio / Staffetta (${tit}%)`,
            desc: `Non ha il posto garantito al 100%. Potrebbe partire dalla panchina o essere sostituito attorno al 60'.`
        });
        if (player.ovr >= 85 || player.is_rigorista_1) {
            pros.push({
                icon: '⚡',
                title: 'Super-Sub ad Alto Impatto',
                desc: `Anche subentrando a gara in corso ha la qualità e i calci piazzati per incidere sui fantavoti.`
            });
        }
    } else {
        cons.push({
            icon: '🪑',
            title: `Minutaggio a Forte Rischio (${tit}%)`,
            desc: `Parte molto indietro nelle gerarchie dell'allenatore. Concreto rischio di voto nullo senza copertura.`
        });
    }

    // 4. CALCI PIAZZATI E RIGORI
    if (player.is_rigorista_1 || player.rigorista_val === '1° Rigorista') {
        pros.push({
            icon: '👑',
            title: '1° Rigorista Designato',
            desc: `Prima scelta assoluta dal dischetto: ogni fallo da rigore conquistato dalla squadra si trasforma in una chance da +3.`
        });
    } else if (player.is_rigorista_2 || player.rigorista_val === '2° Rigorista') {
        pros.push({
            icon: '🎯',
            title: '2° Rigorista in Rosa',
            desc: `Opzione di riserva dal dischetto se il primo rigorista non è in campo o ha già calciato.`
        });
    } else if (player.role !== 'P') {
        cons.push({
            icon: '❌',
            title: 'Nessun Bonus dal Dischetto',
            desc: `Non tira i calci di rigore: i suoi bonus dipendono esclusivamente da azioni manovrate o piazzati.`
        });
    }

    if (player.is_punizioni || player.is_corner) {
        pros.push({
            icon: '📐',
            title: 'Specialista Piazzati & Corner',
            desc: `Batte corner e punizioni verso l'area: moltiplica l'Expected Assist (xA) da palla inattiva.`
        });
    }

    // 5. CARATURA E POTENZIALE RISCATTO
    const ovr = Number(player.ovr) || 75;
    if (ovr >= 90) {
        pros.push({
            icon: '⭐',
            title: `Caratura da Top Player (OVR ${ovr})`,
            desc: `Leader tecnico assoluto con 'ceiling' (tetto massimo di punti) tra i più alti della Serie A.`
        });
    }

    if (ovr >= 85 && (player.gol_2627 || 0) === 0 && oppStats && (Number(oppStats.goals_conceded_match) >= 1.5 || Number(oppStats.xga_team) >= 8.5)) {
        pros.push({
            icon: '🚀',
            title: 'Fame di Riscatto (Bounce-Back)',
            desc: `Top player incredibilmente ancora a secco di gol dopo 5 turni: l'incrocio contro una difesa colabrodo è lo scenario perfetto per sbloccarsi.`
        });
    }

    // 6. MALUS E CARTELLINI
    const amm = Number(player.amm_2627) || 0;
    const esp = Number(player.esp_2627) || 0;
    if (esp > 0 || amm >= 2) {
        cons.push({
            icon: '🟨',
            title: 'Rischio Malus Disciplinare',
            desc: `Giocatore con propensione al cartellino (${amm} ammonizioni${esp > 0 ? ', 1 espulsione' : ''}). Rischio -0.5 costante.`
        });
    }

    return { pros, cons };
}

function buildStrategicVerdictGuidance(pA, dataA, pB, dataB, round) {
    const titA = Number(pA.titolarita) || 50;
    const titB = Number(pB.titolarita) || 50;
    const ovrA = Number(pA.ovr) || 75;
    const ovrB = Number(pB.ovr) || 75;
    const fixA = dataA.fixture;
    const fixB = dataB.fixture;

    let safePlayer = pA;
    let safeReason = '';
    let upsidePlayer = pB;
    let upsideReason = '';

    if (titA >= titB && (fixA && fixA.isHome)) {
        safePlayer = pA;
        safeReason = `Parte dal 1' minuto (${titA}% titolarità) con il calore del pubblico di casa. Garantisce voto sicuro e consistenza.`;
        upsidePlayer = pB;
    } else if (titB > titA && (fixB && fixB.isHome)) {
        safePlayer = pB;
        safeReason = `Parte dal 1' minuto (${titB}% titolarità) tra le mura amiche, minimizzando i rischi di turnover.`;
        upsidePlayer = pA;
    } else if (titA >= titB) {
        safePlayer = pA;
        safeReason = `Maggiore garanzia di minutaggio rispetto all'alternativa (${titA}% vs ${titB}%).`;
        upsidePlayer = pB;
    } else {
        safePlayer = pB;
        safeReason = `Maggiore garanzia di minutaggio rispetto all'alternativa (${titB}% vs ${titA}%).`;
        upsidePlayer = pA;
    }

    const oppB = (fixB && typeof TEAM_STATS_DB !== 'undefined') ? TEAM_STATS_DB[fixB.opp] : null;
    const oppA = (fixA && typeof TEAM_STATS_DB !== 'undefined') ? TEAM_STATS_DB[fixA.opp] : null;

    if (upsidePlayer.id === pB.id) {
        let r = [];
        if (pB.is_rigorista_1) r.push('1° rigorista (+3)');
        if (ovrB >= 90) r.push(`Top Player OVR ${ovrB}`);
        if (oppB && Number(oppB.goals_conceded_match) >= 1.6) r.push(`sfida la fragile difesa del ${oppB.squadra} (${Number(oppB.goals_conceded_match).toFixed(1)} gol subiti/gara)`);
        upsideReason = r.length > 0 
            ? `Ha un 'ceiling' esplosivo: ${r.join(', ')}. Perfetto se punti a vincere la giornata con un bonus pesante.`
            : `Potenziale di bonus elevato grazie alla posizione offensiva e agli expected stats.`;
    } else {
        let r = [];
        if (pA.is_rigorista_1) r.push('1° rigorista (+3)');
        if (ovrA >= 90) r.push(`Top Player OVR ${ovrA}`);
        if (oppA && Number(oppA.goals_conceded_match) >= 1.6) r.push(`sfida la fragile difesa del ${oppA.squadra} (${Number(oppA.goals_conceded_match).toFixed(1)} gol subiti/gara)`);
        upsideReason = r.length > 0 
            ? `Ha un 'ceiling' esplosivo: ${r.join(', ')}. Perfetto se punti a vincere la giornata con un bonus pesante.`
            : `Potenziale di bonus elevato grazie alla posizione offensiva e agli expected stats.`;
    }

    let finalAiTake = '';
    if (safePlayer.id === upsidePlayer.id) {
        finalAiTake = `L'algoritmo non ha dubbi: <b>${safePlayer.name}</b> domina il confronto sia in termini di sicurezza del voto sia in potenziale di bonus (+3). Schieralo senza esitazione.`;
    } else {
        finalAiTake = `Se la tua priorità è il voto sicuro e la continuità di rendimento, <b>${safePlayer.name}</b> è la scelta più solida. Se invece la tua partita di lega richiede un exploit offensivo e ti serve un +3 pesante, punta forte su <b>${upsidePlayer.name}</b>.`;
    }

    return { safePlayer, safeReason, upsidePlayer, upsideReason, finalAiTake };
}

// Preset intelligenti e reali di Serie A
function selectChiSchieroPreset(nameA, nameB) {
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return;
    const pA = PLAYERS.find(p => p.name.toLowerCase().includes(nameA.toLowerCase()));
    const pB = PLAYERS.find(p => p.name.toLowerCase().includes(nameB.toLowerCase()));
    if (pA && pB) {
        window.chiSchieroState.playerAId = pA.id;
        window.chiSchieroState.playerBId = pB.id;
        // Allinea il filtro ruolo
        if (pA.role === pB.role) {
            window.chiSchieroState.roleFilter = pA.role;
        } else {
            window.chiSchieroState.roleFilter = 'ALL';
        }
        renderChiSchieroView();
    }
}

// Gestione selezione calciatore con vincolo ruoli (MAI Portieri vs Movimento)
function onChiSchieroPlayerSelect(slot, playerId) {
    const id = parseInt(playerId, 10);
    const chosen = PLAYERS.find(p => p.id === id);
    if (!chosen) return;

    if (slot === 'A') {
        window.chiSchieroState.playerAId = id;
        const currentB = PLAYERS.find(p => p.id === window.chiSchieroState.playerBId);

        // Se A è portiere e B non lo è, forza B a un portiere
        if (chosen.role === 'P' && (!currentB || currentB.role !== 'P')) {
            const altGk = PLAYERS.find(p => p.role === 'P' && p.id !== id);
            if (altGk) window.chiSchieroState.playerBId = altGk.id;
            window.chiSchieroState.roleFilter = 'P';
        } 
        // Se A è movimento e B è portiere, forza B a un giocatore di movimento
        else if (chosen.role !== 'P' && currentB && currentB.role === 'P') {
            const altField = PLAYERS.find(p => p.role !== 'P' && p.id !== id && (p.role === chosen.role || p.role === 'A'));
            if (altField) window.chiSchieroState.playerBId = altField.id;
            if (window.chiSchieroState.roleFilter === 'P') window.chiSchieroState.roleFilter = 'ALL';
        }
    } else {
        window.chiSchieroState.playerBId = id;
        const currentA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId);

        if (chosen.role === 'P' && (!currentA || currentA.role !== 'P')) {
            const altGk = PLAYERS.find(p => p.role === 'P' && p.id !== id);
            if (altGk) window.chiSchieroState.playerAId = altGk.id;
            window.chiSchieroState.roleFilter = 'P';
        } else if (chosen.role !== 'P' && currentA && currentA.role === 'P') {
            const altField = PLAYERS.find(p => p.role !== 'P' && p.id !== id && (p.role === chosen.role || p.role === 'A'));
            if (altField) window.chiSchieroState.playerAId = altField.id;
            if (window.chiSchieroState.roleFilter === 'P') window.chiSchieroState.roleFilter = 'ALL';
        }
    }
    renderChiSchieroView();
}

function onChiSchieroRoundChange(roundVal) {
    window.chiSchieroState.round = parseInt(roundVal, 10);
    renderChiSchieroView();
}

function onChiSchieroRoleFilterChange(role) {
    window.chiSchieroState.roleFilter = role;
    
    if (role === 'P') {
        const pA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId);
        const pB = PLAYERS.find(p => p.id === window.chiSchieroState.playerBId);
        if (!pA || pA.role !== 'P') {
            const gks = PLAYERS.filter(p => p.role === 'P');
            if (gks.length >= 2) {
                window.chiSchieroState.playerAId = gks[0].id;
                window.chiSchieroState.playerBId = gks[1].id;
            }
        }
    } else if (role !== 'ALL') {
        const eligible = PLAYERS.filter(p => p.role === role);
        if (eligible.length >= 2) {
            window.chiSchieroState.playerAId = eligible[0].id;
            window.chiSchieroState.playerBId = eligible[1].id;
        }
    } else {
        // Se era su P ed è passato a ALL, se sono portieri li lasciamo o proponiamo Politano vs Orsolini
        const pA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId);
        if (pA && pA.role === 'P') {
            const pol = PLAYERS.find(p => p.name.toLowerCase().includes('politano'));
            const ors = PLAYERS.find(p => p.name.toLowerCase().includes('orsolini'));
            if (pol && ors) {
                window.chiSchieroState.playerAId = pol.id;
                window.chiSchieroState.playerBId = ors.id;
            }
        }
    }
    renderChiSchieroView();
}

function copyChiSchieroVerdictToClipboard() {
    const pA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId);
    const pB = PLAYERS.find(p => p.id === window.chiSchieroState.playerBId);
    if (!pA || !pB) return;

    const round = window.chiSchieroState.round || 6;
    const verdict = calculateChiSchieroVerdict(pA, pB, round);
    if (!verdict) return;

    const text = `⚔️ *FANTA MASTER AI — CHI SCHIERO?* 📅 (Giornata ${round})\n\n` +
        `🥊 *${pA.name} (${pA.team})* vs *${pB.name} (${pB.team})*\n\n` +
        `🎯 *VERDETTO:* ${verdict.verdictTitle}\n` +
        `📊 Probabilità: ${pA.name} ${verdict.pctA}% ⚡ | ${pB.name} ${verdict.pctB}%\n\n` +
        `💡 *Motivazioni AI:*\n` +
        verdict.bullets.map(b => b.replace(/<[^>]+>/g, '')).join('\n') + `\n\n` +
        `👉 Risolvi i tuoi dubbi di formazione gratis su: https://fantamasterai.it/chi-schiero/`;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            alert('✅ Verdetto copiato negli appunti! Incollalo su WhatsApp o Telegram.');
        }).catch(() => {
            prompt('Copia il verdetto per WhatsApp:', text);
        });
    } else {
        prompt('Copia il verdetto per WhatsApp:', text);
    }
}

function renderChiSchieroView() {
    const container = document.getElementById('viewChiSchiero');
    if (!container) return;

    initChiSchieroState();

    const round = window.chiSchieroState.round || 6;
    let pA = PLAYERS.find(p => p.id === window.chiSchieroState.playerAId) || PLAYERS[0];
    let pB = PLAYERS.find(p => p.id === window.chiSchieroState.playerBId) || PLAYERS[1];

    // Controllo di sicurezza: se per qualsiasi motivo uno è P e l'altro no, sincronizza
    if (pA.role === 'P' && pB.role !== 'P') {
        const altGk = PLAYERS.find(p => p.role === 'P' && p.id !== pA.id);
        if (altGk) {
            pB = altGk;
            window.chiSchieroState.playerBId = altGk.id;
        }
    } else if (pA.role !== 'P' && pB.role === 'P') {
        const altField = PLAYERS.find(p => p.role !== 'P' && p.id !== pA.id);
        if (altField) {
            pB = altField;
            window.chiSchieroState.playerBId = altField.id;
        }
    }

    // Data del round dal calendario
    let roundDateStr = '';
    if (typeof OFFICIAL_CALENDAR_2026_27 !== 'undefined' && Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        const rData = OFFICIAL_CALENDAR_2026_27.find(r => Number(r.giornata) === Number(round));
        if (rData && rData.date) roundDateStr = rData.date;
    }

    const verdict = calculateChiSchieroVerdict(pA, pB, round);

    // Opzioni per il selettore turno (38 giornate)
    const upcomingRound = (typeof getUpcomingMatchdayRound === 'function') ? getUpcomingMatchdayRound() : 6;
    let roundOptionsHtml = '';
    for (let r = 1; r <= 38; r++) {
        const isUpcoming = (r === upcomingRound);
        const isSel = (r === round);
        const tag = isUpcoming ? ' ⭐ (Prossima in Arrivo)' : (r < upcomingRound ? ' (Giocata)' : '');
        roundOptionsHtml += `<option value="${r}" ${isSel ? 'selected' : ''}>Giornata ${r}${tag}</option>`;
    }

    // Filtra lista giocatori per selects (vincolo rigido: MAI Portiere vs Movimento)
    const roleFilt = window.chiSchieroState.roleFilter;
    
    // Lista eleggibile per Slot A
    const eligibleA = PLAYERS.filter(p => {
        if (roleFilt === 'ALL') return true;
        return p.role === roleFilt;
    });

    // Lista eleggibile per Slot B: rispetta la natura di A (se A è P -> solo P; se A è movimento -> solo movimento)
    const eligibleB = PLAYERS.filter(p => {
        if (pA.role === 'P') return p.role === 'P';
        if (p.role === 'P') return false; // esclude i portieri se A è movimento
        if (roleFilt !== 'ALL') return p.role === roleFilt;
        return true;
    });

    const optionsAHtml = eligibleA.map(p => `
        <option value="${p.id}" ${p.id === pA.id ? 'selected' : ''}>
            ${p.name} (${p.team} - ${p.role}) • OVR ${p.ovr}
        </option>
    `).join('');

    const optionsBHtml = eligibleB.map(p => `
        <option value="${p.id}" ${p.id === pB.id ? 'selected' : ''}>
            ${p.name} (${p.team} - ${p.role}) • OVR ${p.ovr}
        </option>
    `).join('');

    // Classi tier OVR
    const ovrClassA = typeof getOvrClass === 'function' ? getOvrClass(pA.ovr) : 'ovr-tier-elite';
    const ovrClassB = typeof getOvrClass === 'function' ? getOvrClass(pB.ovr) : 'ovr-tier-elite';

    const fixtureA = verdict.dataA.fixture;
    const fixtureB = verdict.dataB.fixture;

    const html = `
        <div class="chi-schiero-container">
            <!-- HERO HEADER -->
            <div class="chi-schiero-hero">
                <div class="cs-hero-top">
                    <div class="cs-title-box">
                        <div class="cs-badge-icon">⚔️</div>
                        <div>
                            <div class="cs-eyebrow">DECISION ENGINE 1VS1 • SERIE A 2026/27</div>
                            <h1 class="cs-main-title">TOOL "CHI SCHIERO?"</h1>
                            <div class="cs-main-desc">Il comparatore predittivo per risolvere i tuoi ballottaggi di formazione del weekend.</div>
                        </div>
                    </div>

                    <div class="cs-hero-actions">
                        <button class="cs-btn-share" onclick="copyChiSchieroVerdictToClipboard()" title="Copia per WhatsApp / Telegram">
                            <span>📲</span> Condividi Verdetto
                        </button>
                    </div>
                </div>

                <!-- CONTROLLI: GIORNATA & FILTRI -->
                <div class="cs-control-bar">
                    <div class="cs-ctrl-group">
                        <label for="selectCsRound">⚽ TURNO ANALIZZATO:</label>
                        <select id="selectCsRound" class="cs-select" onchange="onChiSchieroRoundChange(this.value)">
                            ${roundOptionsHtml}
                        </select>
                        ${roundDateStr ? `<span class="cs-date-badge">📅 ${roundDateStr}</span>` : ''}
                    </div>

                    <div class="cs-ctrl-group">
                        <label>FILTRA RUOLO:</label>
                        <div class="cs-role-filters">
                            <button class="cs-role-chip ${roleFilt === 'ALL' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('ALL')">TUTTI</button>
                            <button class="cs-role-chip ${roleFilt === 'P' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('P')">🧤 P</button>
                            <button class="cs-role-chip ${roleFilt === 'D' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('D')">🛡️ D</button>
                            <button class="cs-role-chip ${roleFilt === 'C' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('C')">🪄 C</button>
                            <button class="cs-role-chip ${roleFilt === 'A' ? 'active' : ''}" onclick="onChiSchieroRoleFilterChange('A')">⚡ A</button>
                        </div>
                    </div>
                </div>

                <!-- PRESET BALLOTTAGGI REALI & FAMOSI -->
                <div class="cs-presets-row">
                    <span class="cs-presets-title">🔥 Ballottaggi Caldi:</span>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Politano', 'Orsolini')">Politano vs Orsolini</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Politano', 'Neres')">Politano vs Neres</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Pulisic', 'Chukwueze')">Pulisic vs Chukwueze</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Dimarco', 'Carlos Augusto')">Dimarco vs C. Augusto</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Martinez L', 'Hojlund')">Lautaro vs Hojlund</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Retegui', 'Lookman')">Retegui vs Lookman</button>
                    <button class="cs-preset-pill" onclick="selectChiSchieroPreset('Svilar', 'Vicario')">Svilar vs Vicario</button>
                </div>
            </div>

            <!-- SELEZIONE DEI DUE CALCIATORI -->
            <div class="cs-duel-selectors-grid">
                <!-- SLOT A -->
                <div class="cs-player-selector-card card-a">
                    <div class="cs-slot-header">
                        <span class="cs-slot-tag tag-a">CALCIATORE A</span>
                        <span class="role-badge ${pA.role}">${pA.role}</span>
                    </div>
                    <select class="cs-player-dropdown" onchange="onChiSchieroPlayerSelect('A', this.value)">
                        ${optionsAHtml}
                    </select>
                    
                    <div class="cs-player-quick-info">
                        <div class="cs-player-identity">
                            <span class="ovr-pill ${ovrClassA}">${pA.ovr}</span>
                            <div class="cs-name-team">
                                <span class="cs-pname">${pA.name}</span>
                                <span class="cs-pteam">${pA.team}</span>
                            </div>
                        </div>
                        <div class="cs-match-pill ${fixtureA && fixtureA.isHome ? 'home' : 'away'}">
                            ${fixtureA ? fixtureA.shortLabel : 'Turno di riposo'}
                        </div>
                    </div>
                </div>

                <div class="cs-vs-divider">
                    <span>VS</span>
                </div>

                <!-- SLOT B -->
                <div class="cs-player-selector-card card-b">
                    <div class="cs-slot-header">
                        <span class="cs-slot-tag tag-b">CALCIATORE B</span>
                        <span class="role-badge ${pB.role}">${pB.role}</span>
                    </div>
                    <select class="cs-player-dropdown" onchange="onChiSchieroPlayerSelect('B', this.value)">
                        ${optionsBHtml}
                    </select>

                    <div class="cs-player-quick-info">
                        <div class="cs-player-identity">
                            <span class="ovr-pill ${ovrClassB}">${pB.ovr}</span>
                            <div class="cs-name-team">
                                <span class="cs-pname">${pB.name}</span>
                                <span class="cs-pteam">${pB.team}</span>
                            </div>
                        </div>
                        <div class="cs-match-pill ${fixtureB && fixtureB.isHome ? 'home' : 'away'}">
                            ${fixtureB ? fixtureB.shortLabel : 'Turno di riposo'}
                        </div>
                    </div>
                </div>
            </div>

            <!-- HERO VERDICT DISPLAY -->
            <div class="cs-verdict-banner">
                <div class="cs-verdict-title">${verdict.verdictTitle}</div>
                <div class="cs-verdict-subtitle">${verdict.verdictSubtitle}</div>

                <!-- PROBABILITY BAR -->
                <div class="cs-prob-bar-container">
                    <div class="cs-prob-bar-left" style="width: ${verdict.pctA}%;">
                        <span>${pA.name} ${verdict.pctA}%</span>
                    </div>
                    <div class="cs-prob-bar-right" style="width: ${verdict.pctB}%;">
                        <span>${verdict.pctB}% ${pB.name}</span>
                    </div>
                </div>
            </div>

            <!-- LA GUIDA STRATEGICA DELL'AI (DECISION COMPASS) -->
            <div class="cs-strategic-advice-card">
                <div class="cs-strategic-header">
                    <span class="cs-compass-icon">🧭</span>
                    <div>
                        <h4>LA GUIDA STRATEGICA DELL'AI</h4>
                        <div class="cs-strat-subtitle">Come orientare la tua scelta in base al piano partita della tua lega</div>
                    </div>
                </div>

                <div class="cs-strat-scenarios-grid">
                    <div class="cs-scenario-box scenario-safe">
                        <div class="cs-scen-tag">🛡️ PER IL VOTO SICURO & CONSISTENZA</div>
                        <div class="cs-scen-player">${verdict.strategy.safePlayer.name} (${verdict.strategy.safePlayer.team})</div>
                        <div class="cs-scen-desc">${verdict.strategy.safeReason}</div>
                    </div>

                    <div class="cs-scenario-box scenario-risk">
                        <div class="cs-scen-tag">🚀 PER IL BONUS PESANTE (+3 / CEILING)</div>
                        <div class="cs-scen-player">${verdict.strategy.upsidePlayer.name} (${verdict.strategy.upsidePlayer.team})</div>
                        <div class="cs-scen-desc">${verdict.strategy.upsideReason}</div>
                    </div>
                </div>

                <div class="cs-final-ai-take">
                    <span class="cs-take-badge">🤖 IL VERDETTO TATTICO:</span>
                    <span>${verdict.strategy.finalAiTake}</span>
                </div>
            </div>

            <!-- ANALISI DETTAGLIATA PRO & CONTRO PARALLELA -->
            <div class="cs-deep-analysis-section">
                <div class="cs-section-header-box">
                    <span class="cs-section-header-icon">⚖️</span>
                    <div>
                        <h2>Analisi Dettagliata Punti di Forza (Pro) &amp; Insidie (Contro)</h2>
                        <p>Trasparenza algoritmica totale: ecco tutti i fattori positivi e negativi analizzati per ciascun giocatore</p>
                    </div>
                </div>

                <div class="cs-dual-analysis-grid">
                    <!-- CARD PRO/CONTRO CALCIATORE A -->
                    <div class="cs-player-analysis-card card-a">
                        <div class="cs-ana-player-bar">
                            <div class="cs-ana-player-meta">
                                <span class="role-badge ${pA.role}">${pA.role}</span>
                                <div>
                                    <div class="cs-ana-pname">${pA.name}</div>
                                    <div class="cs-ana-pteam">${pA.team} • OVR ${pA.ovr}</div>
                                </div>
                            </div>
                            <div class="cs-ana-score-pill">Punteggio: ${verdict.dataA.score} pt</div>
                        </div>

                        <!-- PRO BLOCK A -->
                        <div class="cs-ana-block">
                            <div class="cs-ana-block-title pro">🟢 Punti a Favore (Pro)</div>
                            ${verdict.analysisA.pros.map(pr => `
                                <div class="cs-point-item pro">
                                    <span class="cs-point-icon">${pr.icon}</span>
                                    <div><b>${pr.title}:</b> ${pr.desc}</div>
                                </div>
                            `).join('')}
                        </div>

                        <!-- CONTRO BLOCK A -->
                        <div class="cs-ana-block">
                            <div class="cs-ana-block-title con">🔴 Rischi &amp; Punti Critici (Contro)</div>
                            ${verdict.analysisA.cons.map(cn => `
                                <div class="cs-point-item con">
                                    <span class="cs-point-icon">${cn.icon}</span>
                                    <div><b>${cn.title}:</b> ${cn.desc}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- CARD PRO/CONTRO CALCIATORE B -->
                    <div class="cs-player-analysis-card card-b">
                        <div class="cs-ana-player-bar">
                            <div class="cs-ana-player-meta">
                                <span class="role-badge ${pB.role}">${pB.role}</span>
                                <div>
                                    <div class="cs-ana-pname">${pB.name}</div>
                                    <div class="cs-ana-pteam">${pB.team} • OVR ${pB.ovr}</div>
                                </div>
                            </div>
                            <div class="cs-ana-score-pill">Punteggio: ${verdict.dataB.score} pt</div>
                        </div>

                        <!-- PRO BLOCK B -->
                        <div class="cs-ana-block">
                            <div class="cs-ana-block-title pro">🟢 Punti a Favore (Pro)</div>
                            ${verdict.analysisB.pros.map(pr => `
                                <div class="cs-point-item pro">
                                    <span class="cs-point-icon">${pr.icon}</span>
                                    <div><b>${pr.title}:</b> ${pr.desc}</div>
                                </div>
                            `).join('')}
                        </div>

                        <!-- CONTRO BLOCK B -->
                        <div class="cs-ana-block">
                            <div class="cs-ana-block-title con">🔴 Rischi &amp; Punti Critici (Contro)</div>
                            ${verdict.analysisB.cons.map(cn => `
                                <div class="cs-point-item con">
                                    <span class="cs-point-icon">${cn.icon}</span>
                                    <div><b>${cn.title}:</b> ${cn.desc}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAVOLA COMPARATIVA TESTA A TESTA -->
            <div class="cs-table-card">
                <div class="cs-table-header">
                    <h3>Confronto Statistico Diretto • Giornata ${round}</h3>
                </div>
                <div class="cs-table-responsive">
                    <table class="cs-comparison-table">
                        <thead>
                            <tr>
                                <th style="width:40%;text-align:left;">${pA.name} (${pA.team})</th>
                                <th style="width:20%;text-align:center;">METRICA</th>
                                <th style="width:40%;text-align:right;">${pB.name} (${pB.team})</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="col-a ${fixtureA && fixtureA.isHome ? 'stat-tier-elite' : ''}">${fixtureA ? fixtureA.label : '-'}</td>
                                <td class="col-metric">Partita & Sede</td>
                                <td class="col-b ${fixtureB && fixtureB.isHome ? 'stat-tier-elite' : ''}">${fixtureB ? fixtureB.label : '-'}</td>
                            </tr>
                            <tr>
                                <td class="col-a stat-tier-elite">${pA.ovr} OVR</td>
                                <td class="col-metric">Valutazione Globale</td>
                                <td class="col-b stat-tier-elite">${pB.ovr} OVR</td>
                            </tr>
                            <tr>
                                <td class="col-a ${pA.titolarita >= 85 ? 'stat-tier-top' : (pA.titolarita < 50 ? 'stat-tier-bench' : 'stat-tier-mid')}">${pA.titolarita || 0}%</td>
                                <td class="col-metric">Titolarità Stimata</td>
                                <td class="col-b ${pB.titolarita >= 85 ? 'stat-tier-top' : (pB.titolarita < 50 ? 'stat-tier-bench' : 'stat-tier-mid')}">${pB.titolarita || 0}%</td>
                            </tr>
                            <tr>
                                <td class="col-a stat-tier-elite">${pA.xfm ? Number(pA.xfm).toFixed(2) : (pA.fm_2627 ? Number(pA.fm_2627).toFixed(2) : '-')}</td>
                                <td class="col-metric">Expected FantaMedia (xFM)</td>
                                <td class="col-b stat-tier-elite">${pB.xfm ? Number(pB.xfm).toFixed(2) : (pB.fm_2627 ? Number(pB.fm_2627).toFixed(2) : '-')}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${pA.fm_2627 ? Number(pA.fm_2627).toFixed(2) : '-'} / ${pA.mv_2627 ? Number(pA.mv_2627).toFixed(2) : '-'}</td>
                                <td class="col-metric">FM / Media Voto 26/27</td>
                                <td class="col-b">${pB.fm_2627 ? Number(pB.fm_2627).toFixed(2) : '-'} / ${pB.mv_2627 ? Number(pB.mv_2627).toFixed(2) : '-'}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${(pA.gol_2627 || 0)}G / ${(pA.assist_2627 || 0)}A</td>
                                <td class="col-metric">Gol / Assist 26/27</td>
                                <td class="col-b">${(pB.gol_2627 || 0)}G / ${(pB.assist_2627 || 0)}A</td>
                            </tr>
                            <tr>
                                <td class="col-a">${pA.is_rigorista_1 ? '👑 1° Rigorista' : (pA.is_rigorista_2 ? '🎯 2° Rigorista' : '-')}</td>
                                <td class="col-metric">Rigorista Ufficiale</td>
                                <td class="col-b">${pB.is_rigorista_1 ? '👑 1° Rigorista' : (pB.is_rigorista_2 ? '🎯 2° Rigorista' : '-')}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${pA.is_punizioni && pA.is_corner ? '📐 Corner & Punizioni' : (pA.is_punizioni ? '📐 Punizioni' : (pA.is_corner ? '📐 Corner' : '-'))}</td>
                                <td class="col-metric">Calci Piazzati</td>
                                <td class="col-b">${pB.is_punizioni && pB.is_corner ? '📐 Corner & Punizioni' : (pB.is_punizioni ? '📐 Punizioni' : (pB.is_corner ? '📐 Corner' : '-'))}</td>
                            </tr>
                            <tr>
                                <td class="col-a">${(pA.amm_2627 || 0)} 🟨 / ${(pA.esp_2627 || 0)} 🟥</td>
                                <td class="col-metric">Cartellini / Malus</td>
                                <td class="col-b">${(pB.amm_2627 || 0)} 🟨 / ${(pB.esp_2627 || 0)} 🟥</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

window.renderChiSchieroView = renderChiSchieroView;
window.onChiSchieroPlayerSelect = onChiSchieroPlayerSelect;
window.onChiSchieroRoundChange = onChiSchieroRoundChange;
window.onChiSchieroRoleFilterChange = onChiSchieroRoleFilterChange;
window.selectChiSchieroPreset = selectChiSchieroPreset;
window.copyChiSchieroVerdictToClipboard = copyChiSchieroVerdictToClipboard;
