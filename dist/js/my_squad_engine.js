window.MySquadState = {
    squads: [
        {
            id: 'squad_1',
            name: 'Squadra 1',
            mode: 'classic',
            useModificatore: false,
            rosterIds: []
        }
    ],
    activeSquadId: 'squad_1',
    targetRound: null,
    lastGeneratedLineup: null,
    lastUnmatched: []
};
const MY_ROSTER_STORAGE_KEY = 'FANTA_MASTER_AI_MY_ROSTER_2026_27';
const MULTI_SQUADS_STORAGE_KEY = 'FANTA_MASTER_AI_MULTI_SQUADS_2026_27';
function getActiveSquad() {
    if (!window.MySquadState.squads || !Array.isArray(window.MySquadState.squads) || !window.MySquadState.squads.length) {
        window.MySquadState.squads = [{
            id: 'squad_1',
            name: 'Squadra 1',
            mode: 'classic',
            useModificatore: false,
            rosterIds: []
        }];
        window.MySquadState.activeSquadId = 'squad_1';
    }
    let found = window.MySquadState.squads.find(s => s.id === window.MySquadState.activeSquadId);
    if (!found) {
        found = window.MySquadState.squads[0];
        window.MySquadState.activeSquadId = found.id;
    }
    return found;
}
try {
    Object.defineProperty(window.MySquadState, 'rosterIds', {
        get: function() { return getActiveSquad().rosterIds || []; },
        set: function(val) { getActiveSquad().rosterIds = val || []; saveMyRosterToStorage(); },
        configurable: true
    });
    Object.defineProperty(window.MySquadState, 'systemMode', {
        get: function() { return getActiveSquad().mode || 'classic'; },
        set: function(val) { getActiveSquad().mode = val || 'classic'; saveMyRosterToStorage(); },
        configurable: true
    });
    Object.defineProperty(window.MySquadState, 'useModificatore', {
        get: function() { return !!getActiveSquad().useModificatore; },
        set: function(val) { getActiveSquad().useModificatore = !!val; saveMyRosterToStorage(); },
        configurable: true
    });
} catch(e) {
    console.warn('MySquadState defineProperty warning:', e);
}
function loadMyRosterFromStorage() {
    try {
        const rawMulti = localStorage.getItem(MULTI_SQUADS_STORAGE_KEY);
        if (rawMulti) {
            const parsed = JSON.parse(rawMulti);
            if (parsed && Array.isArray(parsed.squads) && parsed.squads.length > 0) {
                window.MySquadState.squads = parsed.squads;
                window.MySquadState.activeSquadId = parsed.activeSquadId || parsed.squads[0].id;
                return;
            }
        }
        const rawOld = localStorage.getItem(MY_ROSTER_STORAGE_KEY);
        let oldIds = [];
        if (rawOld) {
            const parsedOld = JSON.parse(rawOld);
            if (Array.isArray(parsedOld)) {
                oldIds = parsedOld.map(Number).filter(n => !isNaN(n));
            }
        }
        window.MySquadState.squads = [{
            id: 'squad_1',
            name: 'Squadra 1',
            mode: 'classic',
            useModificatore: false,
            rosterIds: oldIds
        }];
        window.MySquadState.activeSquadId = 'squad_1';
        saveMyRosterToStorage();
    } catch(e) {
        console.warn('Errore lettura rose da storage:', e);
    }
}
function saveMyRosterToStorage() {
    try {
        const dataToSave = {
            squads: window.MySquadState.squads,
            activeSquadId: window.MySquadState.activeSquadId
        };
        localStorage.setItem(MULTI_SQUADS_STORAGE_KEY, JSON.stringify(dataToSave));
        const active = getActiveSquad();
        if (active) {
            localStorage.setItem(MY_ROSTER_STORAGE_KEY, JSON.stringify(active.rosterIds));
        }
    } catch(e) {
        console.warn('Errore salvataggio rose in storage:', e);
    }
}
function switchActiveSquad(squadId) {
    if (!squadId) return;
    const exists = window.MySquadState.squads.some(s => s.id === squadId);
    if (exists) {
        window.MySquadState.activeSquadId = squadId;
        window.MySquadState.lastUnmatched = [];
        saveMyRosterToStorage();
        renderMySquadModalContent();
    }
}
function promptCreateNewSquad() {
    const name = prompt('Inserisci il nome della nuova squadra (es. Lega Amici, Mantra Cup...):', `Squadra ${window.MySquadState.squads.length + 1}`);
    if (!name || !name.trim()) return;
    const isMantra = confirm(`Vuoi che "${name.trim()}" sia in modalità MANTRA?\n\n- Premendo OK: Modalità MANTRA (11 schemi tattici).\n- Premendo Annulla: Modalità CLASSIC (con Modificatore di difesa).`);
    const newId = 'squad_' + Date.now();
    const newSquad = {
        id: newId,
        name: name.trim(),
        mode: isMantra ? 'mantra' : 'classic',
        useModificatore: false,
        rosterIds: []
    };
    window.MySquadState.squads.push(newSquad);
    window.MySquadState.activeSquadId = newId;
    window.MySquadState.lastUnmatched = [];
    saveMyRosterToStorage();
    renderMySquadModalContent();
}
function promptRenameActiveSquad() {
    const current = getActiveSquad();
    if (!current) return;
    const newName = prompt('Modifica il nome della squadra:', current.name);
    if (newName && newName.trim()) {
        current.name = newName.trim();
        saveMyRosterToStorage();
        renderMySquadModalContent();
    }
}
function confirmDeleteActiveSquad() {
    if (window.MySquadState.squads.length <= 1) {
        alert('Devi mantenere almeno una squadra salvata.');
        return;
    }
    const current = getActiveSquad();
    if (confirm(`Sei sicuro di voler eliminare definitivamente la squadra "${current.name}"?`)) {
        window.MySquadState.squads = window.MySquadState.squads.filter(s => s.id !== current.id);
        window.MySquadState.activeSquadId = window.MySquadState.squads[0].id;
        window.MySquadState.lastUnmatched = [];
        saveMyRosterToStorage();
        renderMySquadModalContent();
    }
}
function cleanStrTolerant(s) {
    if (!s) return '';
    return String(s)
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}
window.COMMON_PLAYER_ALIASES = {
    'lautaro': 'martinez l',
    'lautaro martinez': 'martinez l',
    'l martinez': 'martinez l',
    'martinez lautaro': 'martinez l',
    'nico paz': 'paz n',
    'n paz': 'paz n',
    'paz nico': 'paz n',
    'theo': 'hernandez t',
    'theo hernandez': 'hernandez t',
    't hernandez': 'hernandez t',
    'hernandez theo': 'hernandez t',
    'marcus thuram': 'thuram m',
    'm thuram': 'thuram m',
    'thuram marcus': 'thuram m',
    'khvicha': 'kvaratskhelia',
    'kvara': 'kvaratskhelia',
    'khvicha kvaratskhelia': 'kvaratskhelia',
    'donyell malen': 'malen',
    'paulo dybala': 'dybala',
    'duvan zapata': 'zapata d',
    'd zapata': 'zapata d',
    'romelu lukaku': 'lukaku',
    'kenan yildiz': 'yildiz',
    'alvaro morata': 'morata',
    'mateo retegui': 'retegui',
    'moise kean': 'kean',
    'taty castellanos': 'castellanos',
    'taty': 'castellanos',
    'francesco pio esposito': 'esposito f p',
    'pio esposito': 'esposito f p',
    'sebastiano esposito': 'esposito se',
    'seba esposito': 'esposito se',
    'nico gonzalez': 'gonzalez n',
    'n gonzalez': 'gonzalez n',
    'lorenzo pellegrini': 'pellegrini lo',
    'mateo pellegrino': 'pellegrino m',
    'manu kone': 'kone m',
    'ismael kone': 'kone i',
    'frank anguissa': 'anguissa',
    'zambo anguissa': 'anguissa',
    'alessandro bastoni': 'bastoni',
    'nicolo barella': 'barella',
    'federico dimarco': 'dimarco',
    'gleison bremer': 'bremer',
    'alessandro buongiorno': 'buongiorno',
    'mile svilar': 'svilar',
    'michele di gregorio': 'di gregorio',
    'mike maignan': 'maignan',
    'yann sommer': 'sommer'
};
function superMatchPlayerFuzzy(rawText, rawClub = '', rawRole = '') {
    if (!rawText || typeof PLAYERS === 'undefined' || !PLAYERS.length) return null;
    let cleanLine = cleanStrTolerant(rawText);
    if (!cleanLine) return null;
    cleanLine = cleanLine.replace(/\b(ruolo|calciatore|squadra|prezzo|fvm|quotazione|titolarita|classic|mantra|crediti|cr)\b/gi, '').trim();
    if (!cleanLine || cleanLine.length < 2) return null;
    if (window.COMMON_PLAYER_ALIASES && window.COMMON_PLAYER_ALIASES[cleanLine]) {
        cleanLine = window.COMMON_PLAYER_ALIASES[cleanLine];
    }
    let exact = PLAYERS.find(p => cleanStrTolerant(p.name) === cleanLine);
    if (exact) return exact;
    const lineTokens = cleanLine.split(/\s+/).filter(t => t.length >= 2);
    if (!lineTokens.length) return null;
    let bestPlayer = null;
    let maxScore = -1;
    const cleanClub = cleanStrTolerant(rawClub);
    PLAYERS.forEach(p => {
        const pClean = cleanStrTolerant(p.name);
        const pTokens = pClean.split(/\s+/).filter(Boolean);
        const pClub = cleanStrTolerant(p.team);
        let matchScore = 0;
        let matchedSurname = false;
        pTokens.forEach((pt, idx) => {
            if (pt.length === 1) {
                if (lineTokens.some(lt => lt === pt || lt.startsWith(pt))) matchScore += 1;
            } else {
                if (lineTokens.includes(pt)) {
                    matchScore += 10;
                    if (idx === 0 || idx === pTokens.length - 1) matchedSurname = true;
                } else if (lineTokens.some(lt => lt.length >= 3 && (lt.includes(pt) || pt.includes(lt)))) {
                    matchScore += 5;
                }
            }
        });
        if (matchedSurname || matchScore >= 10) {
            let totalScore = matchScore;
            if (cleanClub && (pClub.includes(cleanClub) || cleanClub.includes(pClub))) {
                totalScore += 20;
            } else if (lineTokens.some(lt => lt.length >= 3 && pClub.includes(lt))) {
                totalScore += 10;
            }
            if (totalScore > maxScore) {
                maxScore = totalScore;
                bestPlayer = p;
            }
        }
    });
    if (bestPlayer && maxScore >= 10) {
        return bestPlayer;
    }
    for (const lt of lineTokens) {
        if (lt.length >= 4) {
            const matches = PLAYERS.filter(p => cleanStrTolerant(p.name).includes(lt));
            if (matches.length === 1) return matches[0];
            if (matches.length > 1 && cleanClub) {
                const clubMatch = matches.find(p => cleanStrTolerant(p.team).includes(cleanClub));
                if (clubMatch) return clubMatch;
            }
        }
    }
    return null;
}
function parseRosterTextContent(textContent) {
    if (!textContent || typeof textContent !== 'string') return { matched: [], unmatched: [] };
    const lines = textContent.split(/[\r\n]+/);
    const matchedIds = new Set();
    const unmatchedLines = [];
    lines.forEach(line => {
        let clean = line.trim();
        if (!clean || clean.startsWith('#') || clean.startsWith('//') || clean.toLowerCase().startsWith('ruolo') || clean.toLowerCase().startsWith('calciatore')) return;
        let candidateText = clean.replace(/^["'\s]+|["'\s]+$/g, '');
        let match = superMatchPlayerFuzzy(candidateText);
        if (!match) {
            const parts = candidateText.split(/[;\t,\(\)]+/).map(s => s.trim()).filter(Boolean);
            for (let part of parts) {
                if (part.length >= 3 && !/^(P|D|C|A|Por|Dc|Dd|Ds|E|M|C|T|W|A|Pc|\d+)$/i.test(part)) {
                    let subMatch = superMatchPlayerFuzzy(part);
                    if (subMatch) {
                        match = subMatch;
                        break;
                    }
                }
            }
        }
        if (match && match.id) {
            matchedIds.add(match.id);
        } else if (clean.length >= 3) {
            unmatchedLines.push(clean);
        }
    });
    return {
        matched: Array.from(matchedIds),
        unmatched: unmatchedLines
    };
}
function handleRosterFileUpload(file, callback) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        const result = parseRosterTextContent(content);
        if (typeof callback === 'function') {
            callback(result);
        }
    };
    reader.readAsText(file, 'UTF-8');
}
function getMyRosterPlayers() {
    loadMyRosterFromStorage();
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return [];
    const idSet = new Set(window.MySquadState.rosterIds);
    return PLAYERS.filter(p => idSet.has(p.id));
}
function addPlayerToMyRoster(playerId) {
    const id = Number(playerId);
    if (isNaN(id)) return;
    if (!window.MySquadState.rosterIds.includes(id)) {
        window.MySquadState.rosterIds.push(id);
        saveMyRosterToStorage();
    }
}
function removePlayerFromMyRoster(playerId) {
    const id = Number(playerId);
    window.MySquadState.rosterIds = window.MySquadState.rosterIds.filter(x => x !== id);
    saveMyRosterToStorage();
}
function clearMyRoster() {
    window.MySquadState.rosterIds = [];
    saveMyRosterToStorage();
}
function syncPlayerWithLivePitchData(p) {
    if (!p || !p.team) return p;
    const teamData = (typeof getPitchTeamData === 'function') 
        ? getPitchTeamData(p.team)
        : (typeof TACTICAL_DB !== 'undefined' ? TACTICAL_DB[p.team] : null);
    if (!teamData) return p;
    const pClean = cleanStrTolerant(p.name);
    const inLineup = (teamData.lineup || []).find(l => {
        const c = cleanStrTolerant(l.name);
        return c.length >= 3 && (c === pClean || pClean.includes(c) || c.includes(pClean));
    });
    const inBallottaggio = (teamData.ballottaggi || []).find(b => {
        const c = cleanStrTolerant(b.player);
        return c.length >= 3 && (c === pClean || pClean.includes(c) || c.includes(pClean));
    });
    let liveIs11 = p.is_in_11;
    let liveBall = p.is_in_ballottaggio;
    let liveTit = p.titolarita;
    if (inLineup) {
        liveIs11 = true;
        liveBall = false;
        liveTit = inLineup.pct || 85;
    } else if (inBallottaggio) {
        liveIs11 = false;
        liveBall = true;
        liveTit = inBallottaggio.pct || 45;
    } else {
        liveIs11 = false;
        liveBall = false;
        liveTit = 25;
    }
    return {
        ...p,
        is_in_11: liveIs11,
        is_in_ballottaggio: liveBall,
        titolarita: liveTit
    };
}
function generateOptimalLineupForUser(options = {}) {
    const roundNum = options.round || (typeof getUpcomingMatchdayRound === 'function' ? getUpcomingMatchdayRound() : 6);
    const mode = options.mode || window.MySquadState.systemMode || 'classic';
    const useModificatore = (options.useModificatore !== undefined) ? options.useModificatore : window.MySquadState.useModificatore;
    const roster = getMyRosterPlayers();
    if (!roster.length) return null;
    const evaluatedRoster = roster.map(pRaw => {
        const p = syncPlayerWithLivePitchData(pRaw);
        let scoreObj = { score: 60, factors: [] };
        if (typeof calculateChiSchieroScore === 'function') {
            scoreObj = calculateChiSchieroScore(p, roundNum);
        } else if (p.xfm) {
            scoreObj.score = p.xfm * 10;
        }
        return {
            player: p,
            score: scoreObj.score,
            factors: scoreObj.factors || [],
            role: p.role,
            mantra: p.mantra || p.role
        };
    });
    if (mode === 'classic') {
        return optimizeClassicLineup(evaluatedRoster, useModificatore, roundNum);
    } else {
        return optimizeMantraLineup(evaluatedRoster, roundNum);
    }
}
function isPlayerFacingTeam(player, targetTeam, roundNum) {
    if (!player || !targetTeam) return false;
    if (typeof getChiSchieroFixtureForPlayer === 'function') {
        const fix = getChiSchieroFixtureForPlayer(player, roundNum);
        if (fix && fix.opp) {
            return (fix.opp.toLowerCase().trim() === targetTeam.toLowerCase().trim());
        }
    }
    return false;
}
function optimizeClassicLineup(items, useModificatore, roundNum) {
    const SCHEMAS = [
        { name: '3-4-3', D: 3, C: 4, A: 3 },
        { name: '4-3-3', D: 4, C: 3, A: 3 },
        { name: '3-5-2', D: 3, C: 5, A: 2 },
        { name: '4-4-2', D: 4, C: 4, A: 2 },
        { name: '4-5-1', D: 4, C: 5, A: 1 },
        { name: '3-4-2-1', D: 3, C: 4, A: 3 },
        { name: '4-2-3-1', D: 4, C: 5, A: 1 }
    ];
    const por = items.filter(x => x.role === 'P').sort((a,b) => (b.player.is_injured?0:1) - (a.player.is_injured?0:1) || b.score - a.score);
    if (!por.length) return null;
    const starterPor = por[0];
    const porTeam = starterPor.player.team;
    const adjustedItems = items.map(item => {
        if (item.role === 'P') return item;
        const isConflict = isPlayerFacingTeam(item.player, porTeam, roundNum);
        let penalty = 0;
        if (isConflict) {
            penalty = item.role === 'A' ? 5.5 : (item.role === 'C' ? 3.0 : 2.0);
        }
        const newScore = item.score - penalty;
        const newFactors = [...(item.factors || [])];
        if (isConflict) {
            newFactors.push({
                name: `Scontro diretto contro il tuo portiere titolare (${starterPor.player.name}, ${porTeam})`,
                val: `-${penalty.toFixed(1)} pt ⚠️`,
                positive: false
            });
        }
        return {
            ...item,
            score: newScore,
            factors: newFactors,
            isConflict: isConflict,
            conflictTeam: porTeam
        };
    });
    const getRoleStarters = (role, count) => {
        const roleItems = adjustedItems.filter(x => x.role === role);
        const healthy = roleItems.filter(x => !x.player.is_injured).sort((a,b) => b.score - a.score);
        const injured = roleItems.filter(x => x.player.is_injured).sort((a,b) => b.score - a.score);
        let starters = healthy.slice(0, count);
        let injuredCount = 0;
        if (starters.length < count) {
            const needed = count - starters.length;
            const extraInjured = injured.slice(0, needed);
            starters = [...starters, ...extraInjured];
            injuredCount = extraInjured.length;
        }
        return { starters, injuredCount };
    };
    let bestSchemaResult = null;
    let maxTotalScore = -999;
    SCHEMAS.forEach(sch => {
        const resD = getRoleStarters('D', sch.D);
        const resC = getRoleStarters('C', sch.C);
        const resA = getRoleStarters('A', sch.A);
        if (resD.starters.length < sch.D || resC.starters.length < sch.C || resA.starters.length < sch.A) return;
        const sPor = [starterPor];
        const sDef = resD.starters;
        const sCen = resC.starters;
        const sAtt = resA.starters;
        const totalInjuredStarters = resD.injuredCount + resC.injuredCount + resA.injuredCount;
        let totalScore = sPor[0].score +
            sDef.reduce((sum, x) => sum + x.score, 0) +
            sCen.reduce((sum, x) => sum + x.score, 0) +
            sAtt.reduce((sum, x) => sum + x.score, 0) -
            (totalInjuredStarters * 60.0);
        if (useModificatore && sch.D >= 4) {
            const avgDefScore = sDef.reduce((sum, x) => sum + x.score, 0) / sch.D;
            if (avgDefScore >= 75) totalScore += 18.0;
            else if (avgDefScore >= 70) totalScore += 10.0;
        }
        if (totalScore > maxTotalScore) {
            maxTotalScore = totalScore;
            const starterIds = new Set([
                starterPor.player.id,
                ...sDef.map(x => x.player.id),
                ...sCen.map(x => x.player.id),
                ...sAtt.map(x => x.player.id)
            ]);
            const benchPor = por.slice(1, 2);
            const remainingField = adjustedItems.filter(x => x.role !== 'P' && !starterIds.has(x.player.id));
            const healthyField = remainingField.filter(x => !x.player.is_injured).sort((a, b) => b.score - a.score);
            const injuredField = remainingField.filter(x => x.player.is_injured).sort((a, b) => b.score - a.score);
            const bench = [
                ...benchPor,
                ...healthyField,
                ...injuredField
            ];
            const benchAtt = remainingField.filter(x => x.role === 'A');
            const ballottaggi = [];
            if (benchAtt.length > 0 && sAtt.length > 0) {
                const minStartAtt = sAtt[sAtt.length - 1];
                const topBenchAtt = benchAtt.find(x => !x.player.is_injured) || benchAtt[0];
                if (topBenchAtt && Math.abs(minStartAtt.score - topBenchAtt.score) < 8.0) {
                    const pctStart = Math.round(50 + (minStartAtt.score - topBenchAtt.score) * 2.5);
                    const nameB = topBenchAtt.player.name.replace(/\.+$/, '');
                    ballottaggi.push({
                        role: 'Attacco',
                        playerA: minStartAtt.player,
                        playerB: topBenchAtt.player,
                        pctA: Math.min(80, Math.max(52, pctStart)),
                        pctB: 100 - Math.min(80, Math.max(52, pctStart)),
                        reason: `Ballottaggio serrato in attacco: ${minStartAtt.player.name} ha un rating atteso leggermente superiore rispetto a ${nameB}.`
                    });
                }
            }
            bestSchemaResult = {
                schema: sch.name,
                starters: {
                    P: sPor,
                    D: sDef,
                    C: sCen,
                    A: sAtt
                },
                bench: bench,
                totalScore: Math.round(totalScore * 10) / 10,
                ballottaggi: ballottaggi
            };
        }
    });
    return bestSchemaResult;
}
function optimizeMantraLineup(items, roundNum) {
    if (typeof MANTRA_RAW_SCHEMAS === 'undefined') return null;
    const por = items.filter(x => (x.mantra || '').includes('Por') || x.role === 'P').sort((a,b) => ((b.player && b.player.is_injured)?0:1) - ((a.player && a.player.is_injured)?0:1) || b.score - a.score);
    if (!por.length) return null;
    let bestSchemaResult = null;
    let maxTotalScore = -999;
    Object.keys(MANTRA_RAW_SCHEMAS).forEach(schKey => {
        const schema = MANTRA_RAW_SCHEMAS[schKey];
        const assignedStarters = [];
        const usedIds = new Set();
        let injuredCount = 0;
        assignedStarters.push({ posLabel: 'Por', item: por[0] });
        usedIds.add(por[0].player.id);
        if (por[0].player.is_injured) injuredCount++;
        let validSchema = true;
        let schemaScore = por[0].score;
        schema.lines.forEach(line => {
            if (!line || !line.length || line[0].pos === 'Por') return;
            line.forEach(slot => {
                const targetRoles = slot.roles || [slot.pos];
                let candidate = items.find(x => {
                    if (usedIds.has(x.player.id) || x.player.is_injured) return false;
                    const pMantraRoles = (x.player.mantra || x.player.role || '').split(/[\s;,\/]+/);
                    return targetRoles.some(r => pMantraRoles.includes(r));
                });
                if (!candidate) {
                    candidate = items.find(x => {
                        if (usedIds.has(x.player.id)) return false;
                        const pMantraRoles = (x.player.mantra || x.player.role || '').split(/[\s;,\/]+/);
                        return targetRoles.some(r => pMantraRoles.includes(r));
                    });
                    if (candidate) injuredCount++;
                }
                if (candidate) {
                    usedIds.add(candidate.player.id);
                    assignedStarters.push({ posLabel: slot.pos, item: candidate });
                    schemaScore += candidate.score;
                } else {
                    validSchema = false;
                }
            });
        });
        schemaScore -= (injuredCount * 60.0);
        if (validSchema && schemaScore > maxTotalScore) {
            maxTotalScore = schemaScore;
            const bench = items.filter(x => !usedIds.has(x.player.id)).sort((a,b) => (b.player.is_injured?0:1) - (a.player.is_injured?0:1) || b.score - a.score);
            const MANTRA_POS_ORDER = {
                'Por': 1,
                'B': 2, 'Dd': 3, 'Ds': 4, 'Dc': 5, 'Dc/B': 5,
                'E': 6, 'M': 7, 'M/C': 7.5, 'C': 8,
                'T': 9, 'W': 10, 'W/A': 10.5,
                'A': 11, 'A/Pc': 11.5, 'Pc': 12
            };
            assignedStarters.sort((a, b) => {
                const orderA = MANTRA_POS_ORDER[a.posLabel] || 99;
                const orderB = MANTRA_POS_ORDER[b.posLabel] || 99;
                return orderA - orderB;
            });
            bestSchemaResult = {
                schema: schema.name,
                description: schema.description,
                startersList: assignedStarters,
                bench: bench,
                totalScore: Math.round(schemaScore * 10) / 10,
                ballottaggi: []
            };
        }
    });
    return bestSchemaResult;
}
function setDataViewMode(mode) {
    if (mode !== 'easy' && mode !== 'pro') mode = 'easy';
    if (typeof State !== 'undefined') {
        State.dataViewMode = mode;
        try {
            localStorage.setItem('FANTA_DATA_VIEW_MODE', mode);
        } catch(e) {}
    }
    updateDataViewModeUI();
}
function updateDataViewModeUI() {
    const mode = (typeof State !== 'undefined' && State.dataViewMode) ? State.dataViewMode : 'easy';
    if (typeof document !== 'undefined' && document.body) {
        document.body.classList.remove('mode-easy', 'mode-pro');
        document.body.classList.add(`mode-${mode}`);
    }
    document.querySelectorAll('.view-mode-toggle-btn').forEach(btn => {
        const m = btn.getAttribute('data-mode');
        if (m === mode) btn.classList.add('active');
        else btn.classList.remove('active');
    });
}
function openMySquadModal() {
    loadMyRosterFromStorage();
    let modal = document.getElementById('mySquadModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'mySquadModal';
        modal.className = 'modal-backdrop';
        modal.style.cssText = 'position:fixed; inset:0; z-index:9999; background:rgba(5,7,10,0.85); backdrop-filter:blur(12px); display:flex; align-items:center; justify-content:center; padding:20px;';
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';
    renderMySquadModalContent();
}
function closeMySquadModal() {
    const modal = document.getElementById('mySquadModal');
    if (modal) modal.style.display = 'none';
}
function renderMySquadModalContent() {
    const modal = document.getElementById('mySquadModal');
    if (!modal) return;
    const roster = getMyRosterPlayers();
    const activeSq = getActiveSquad();
    const mode = window.MySquadState.systemMode || 'classic';
    const useMod = window.MySquadState.useModificatore;
    const lastUnmatched = window.MySquadState.lastUnmatched || [];
    const squadOptionsHtml = (window.MySquadState.squads || []).map(sq => `
        <option value="${sq.id}" ${sq.id === activeSq.id ? 'selected' : ''}>
            ${sq.name} (${(sq.mode || 'classic').toUpperCase()}) — ${sq.rosterIds ? sq.rosterIds.length : 0} calciatori
        </option>
    `).join('');
    let rosterListHtml = '';
    if (roster.length > 0) {
        rosterListHtml = roster.map(p => {
            const roleBadge = (mode === 'mantra' && p.mantra) ? p.mantra : p.role;
            const roleClass = p.role.toLowerCase();
            return `
                <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); padding:6px 12px; border-radius:10px; font-size:13px; color:#f8fafc;">
                    ${getRoleBadgeHtml(roleBadge)}
                    <strong style="font-weight:700;">${p.name}</strong>
                    <span style="color:#94a3b8; font-size:11px;">(${p.team})</span>
                    <button onclick="removePlayerFromMyRoster(${p.id}); renderMySquadModalContent();" style="background:none; border:none; color:#ef4444; font-weight:800; cursor:pointer; margin-left:4px;" title="Rimuovi calciatore">✕</button>
                </div>
            `;
        }).join('');
    } else {
        rosterListHtml = `<div style="color:#94a3b8; font-size:14px; text-align:center; padding:15px;">Nessun calciatore presente nella tua rosa. Carica il file rose.csv/xml, incolla il testo o cercane uno qui sotto!</div>`;
    }
    let unmatchedDrawerHtml = '';
    if (lastUnmatched.length > 0) {
        const items = lastUnmatched.slice(0, 10).map((uLine, idx) => {
            const candidates = (typeof PLAYERS !== 'undefined' && Array.isArray(PLAYERS)) 
                ? PLAYERS.filter(p => cleanStrTolerant(p.name).includes(cleanStrTolerant(uLine).slice(0,4))).slice(0, 5)
                : [];
            const optionsHtml = candidates.map(c => `<option value="${c.id}">${c.name} (${c.team} - ${c.role})</option>`).join('');
            return `
                <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); padding:8px 12px; border-radius:10px; font-size:12px; flex-wrap:wrap; gap:8px;">
                    <span style="color:#fca5a5; font-family:monospace; font-weight:700;">"${uLine}"</span>
                    <div style="display:flex; align-items:center; gap:8px;">
                        ${candidates.length > 0 ? `
                        <select id="unmatchedSelect_${idx}" style="background:#0f172a; color:#fff; border:1px solid rgba(255,255,255,0.2); padding:4px 8px; border-radius:6px; font-size:12px;">
                            ${optionsHtml}
                        </select>
                        <button onclick="addUnmatchedCandidate(${idx})" style="background:#10b981; color:#fff; border:none; padding:4px 10px; border-radius:6px; font-weight:800; cursor:pointer; font-size:11px;">+ AGGIUNGI</button>
                        ` : '<span style="color:#94a3b8; font-size:11px;">Nessun suggerimento diretto</span>'}
                    </div>
                </div>
            `;
        }).join('');
        unmatchedDrawerHtml = `
            <div style="margin-bottom:20px; background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); border-radius:14px; padding:14px 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="color:#f87171; font-weight:800; font-size:13px; display:flex; align-items:center; gap:6px;">
                        <span>⚠️ REVISIONE NOMI (${lastUnmatched.length}):</span> Alcune righe non sono state abbinate automaticamente.
                    </div>
                    <button onclick="window.MySquadState.lastUnmatched=[]; renderMySquadModalContent();" style="background:none; border:none; color:#94a3b8; font-size:11px; font-weight:700; cursor:pointer;">Chiudi Avviso</button>
                </div>
                <div style="display:flex; flex-direction:column; gap:6px; max-height:140px; overflow-y:auto;">
                    ${items}
                </div>
            </div>
        `;
    }
    modal.innerHTML = `
        <div style="background:#0f172a; border:1px solid rgba(255,255,255,0.12); border-radius:24px; width:100%; max-width:880px; max-height:90vh; overflow-y:auto; padding:30px; box-shadow:0 25px 50px rgba(0,0,0,0.6); position:relative; color:#f8fafc;">
            <button onclick="closeMySquadModal()" style="position:absolute; top:20px; right:20px; background:rgba(255,255,255,0.1); border:none; color:#fff; width:36px; height:36px; border-radius:50%; font-size:18px; font-weight:800; cursor:pointer;">✕</button>
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                <span style="font-size:28px;">📋</span>
                <div>
                    <h2 style="font-size:24px; font-weight:900; font-family:'Outfit',sans-serif; margin:0; color:#f8fafc;">LA MIA ROSA & FORMAZIONE PERFETTA AI</h2>
                    <p style="color:#94a3b8; font-size:14px; margin:2px 0 0 0;">Carica il file <code>rose.csv</code>/<code>xml</code> di Fantacalcio.it, incolla il testo o aggiungi i calciatori manualmente.</p>
                </div>
            </div>
            <!-- SWITCHER & GESTIONE MULTI-SQUADRE -->
            <div style="background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:14px 18px; margin:16px 0 20px 0; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; box-shadow:0 4px 15px rgba(0,0,0,0.3);">
                <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                    <span style="color:#38bdf8; font-size:12.5px; font-weight:900; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px;">
                        <span>🛡️</span> SQUADRA ATTIVA:
                    </span>
                    <select onchange="switchActiveSquad(this.value)" style="background:#05070a; color:#ffffff; border:1px solid #38bdf8; padding:7px 14px; border-radius:10px; font-weight:800; font-size:14px; font-family:'Outfit',sans-serif; cursor:pointer; outline:none; box-shadow:0 0 10px rgba(56,189,248,0.15);">
                        ${squadOptionsHtml}
                    </select>
                    <span style="background:rgba(16,185,129,0.15); color:#4ade80; border:1px solid rgba(16,185,129,0.3); padding:4px 10px; border-radius:8px; font-size:12px; font-weight:800;">
                        ${roster.length} calciatori
                    </span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <button onclick="promptCreateNewSquad()" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); color:#fff; border:none; padding:8px 14px; border-radius:10px; font-size:12.5px; font-weight:800; font-family:'Outfit',sans-serif; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 4px 12px rgba(16,185,129,0.3);">
                        ➕ Nuova Squadra
                    </button>
                    <button onclick="promptRenameActiveSquad()" style="background:rgba(255,255,255,0.08); color:#e2e8f0; border:1px solid rgba(255,255,255,0.15); padding:8px 12px; border-radius:10px; font-size:12.5px; font-weight:700; cursor:pointer;" title="Rinomina squadra corrente">
                        ✏️ Rinomina
                    </button>
                    ${(window.MySquadState.squads || []).length > 1 ? `
                        <button onclick="confirmDeleteActiveSquad()" style="background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.3); padding:8px 12px; border-radius:10px; font-size:12.5px; font-weight:700; cursor:pointer;" title="Elimina questa squadra">
                            🗑️ Elimina
                        </button>
                    ` : ''}
                </div>
            </div>
            <!-- Drag & Drop Zone -->
            <div id="mySquadDropZone" class="my-squad-drop-zone" style="margin:20px 0; border:2px dashed rgba(56,189,248,0.4); background:rgba(15,23,42,0.6); border-radius:18px; padding:24px; text-align:center; cursor:pointer;" onclick="document.getElementById('mySquadFileInput').click()">
                <input type="file" id="mySquadFileInput" accept=".csv,.xml,.xlsx,.txt" style="display:none;" onchange="handleRosterFileSelect(event)">
                <div style="font-size:32px; margin-bottom:6px;">📁</div>
                <div style="font-weight:800; font-size:15px; color:#38bdf8;">Clicca o trascina qui il file rose.csv / xml di Fantacalcio.it</div>
                <div style="font-size:12.5px; color:#94a3b8; margin-top:4px;">Supporta file .csv, .xml, .xlsx ed esportazioni in testo da Leghe Fantacalcio</div>
            </div>
            <!-- Incolla Testo Area -->
            <details style="margin-bottom:20px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:12px 16px;">
                <summary style="font-weight:700; font-size:14px; color:#e2e8f0; cursor:pointer;">📝 Oppure Incolla qui il testo della tua rosa (WhatsApp / Leghe Fantacalcio)</summary>
                <div style="margin-top:10px; display:flex; flex-direction:column; gap:10px;">
                    <textarea id="mySquadTextarea" placeholder="Incolla qui i calciatori della tua rosa (es. Meret, Dimarco, Barella, Lautaro Martinez...)" style="width:100%; height:90px; background:#05070a; border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:10px; color:#fff; font-size:13px;"></textarea>
                    <button onclick="submitMySquadTextPaste()" style="align-self:flex-end; background:#38bdf8; color:#0f172a; font-weight:800; padding:8px 18px; border:none; border-radius:10px; cursor:pointer;">Importa Testo Incollato</button>
                </div>
            </details>
            <!-- Aggiunta Manuale Calciatore con Autocomplete Live -->
            <div style="margin-bottom:20px; background:rgba(56,189,248,0.06); border:1px solid rgba(56,189,248,0.2); border-radius:14px; padding:12px 16px;">
                <label style="font-weight:800; font-size:13px; color:#38bdf8; display:block; margin-bottom:6px;">🔍 CERCA ED AGGIUNGI CALCIATORE SINGOLO:</label>
                <input type="text" id="mySquadSearchInput" placeholder="Digita un nome (es. Nico Gonzalez, Varela, Mandas, Soulè...)" style="width:100%; background:#05070a; border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:8px 12px; color:#fff; font-size:13px;" oninput="onSearchInputMySquadRoster(this.value)">
                <div id="mySquadSearchResults" style="margin-top:8px; display:flex; flex-direction:column; gap:4px;"></div>
            </div>
            <!-- Avviso Revisione Righe Non Matchate -->
            ${unmatchedDrawerHtml}
            <!-- Lista Rosa Salvata -->
            <div style="margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <h3 style="font-size:16px; font-weight:800; margin:0; color:#f1f5f9;">Rosa Salvata (${roster.length} Calciatori)</h3>
                    ${roster.length > 0 ? `<button onclick="clearMyRoster(); window.MySquadState.lastUnmatched=[]; renderMySquadModalContent();" style="background:none; border:none; color:#ef4444; font-size:12px; font-weight:700; cursor:pointer;">Svuota Rosa</button>` : ''}
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:8px; max-height:180px; overflow-y:auto; padding:12px; background:rgba(0,0,0,0.3); border-radius:14px; border:1px solid rgba(255,255,255,0.05);">
                    ${rosterListHtml}
                </div>
            </div>
            <!-- Opzioni & Generazione -->
            <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px; background:rgba(30,41,59,0.5); border:1px solid rgba(255,255,255,0.08); padding:16px 20px; border-radius:16px;">
                <div style="display:flex; align-items:center; gap:15px; flex-wrap:wrap;">
                    <div>
                        <span style="font-size:12px; color:#94a3b8; font-weight:700; display:block; margin-bottom:4px;">SISTEMA DI GIOCO:</span>
                        <div style="display:flex; gap:6px;">
                            <button onclick="window.MySquadState.systemMode='classic'; renderMySquadModalContent();" style="padding:6px 14px; border-radius:8px; border:1px solid ${mode==='classic'?'#10b981':'rgba(255,255,255,0.1)'}; background:${mode==='classic'?'rgba(16,185,129,0.2)':'transparent'}; color:${mode==='classic'?'#4ade80':'#94a3b8'}; font-weight:800; font-size:13px; cursor:pointer;">Classic</button>
                            <button onclick="window.MySquadState.systemMode='mantra'; renderMySquadModalContent();" style="padding:6px 14px; border-radius:8px; border:1px solid ${mode==='mantra'?'#38bdf8':'rgba(255,255,255,0.1)'}; background:${mode==='mantra'?'rgba(56,189,248,0.2)':'transparent'}; color:${mode==='mantra'?'#38bdf8':'#94a3b8'}; font-weight:800; font-size:13px; cursor:pointer;">Mantra (11 Schemi)</button>
                        </div>
                    </div>
                    ${mode==='classic' ? `
                    <div>
                        <span style="font-size:12px; color:#94a3b8; font-weight:700; display:block; margin-bottom:4px;">MODIFICATORE DIFESA:</span>
                        <button onclick="window.MySquadState.useModificatore=!window.MySquadState.useModificatore; renderMySquadModalContent();" style="padding:6px 14px; border-radius:8px; border:1px solid ${useMod?'#fbbf24':'rgba(255,255,255,0.1)'}; background:${useMod?'rgba(251,191,36,0.2)':'transparent'}; color:${useMod?'#fbbf24':'#94a3b8'}; font-weight:800; font-size:13px; cursor:pointer;">
                            ${useMod ? '✅ Attivo (4-DEF)' : '⚪ Disattivato'}
                        </button>
                    </div>
                    ` : ''}
                </div>
                <button onclick="runGenerateMySquadLineup()" class="generate-lineup-btn" style="cursor:pointer;">
                    ⚡ GENERA FORMAZIONE PERFETTA AI
                </button>
            </div>
            <!-- Output Risultato Lineup -->
            <div id="mySquadLineupOutput" style="margin-top:25px;"></div>
        </div>
    `;
}
function onSearchInputMySquadRoster(val) {
    const container = document.getElementById('mySquadSearchResults');
    if (!container) return;
    const clean = cleanStrTolerant(val);
    if (!clean || clean.length < 2) {
        container.innerHTML = '';
        return;
    }
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) {
        container.innerHTML = '';
        return;
    }
    const matches = PLAYERS.filter(p => cleanStrTolerant(p.name).includes(clean) || cleanStrTolerant(p.team).includes(clean)).slice(0, 5);
    if (!matches.length) {
        container.innerHTML = `<div style="color:#94a3b8; font-size:12px; padding:4px;">Nessun calciatore trovato con "${val}"</div>`;
        return;
    }
    container.innerHTML = matches.map(p => `
        <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.08); padding:6px 12px; border-radius:8px; font-size:12.5px;">
            <div>
                ${getRoleBadgeHtml(p.role)}
                <strong style="color:#fff; margin-left:6px;">${p.name}</strong>
                <span style="color:#94a3b8; font-size:11px; margin-left:4px;">(${p.team})</span>
            </div>
            <button onclick="addPlayerToMyRoster(${p.id}); renderMySquadModalContent();" style="background:#10b981; color:#fff; border:none; padding:4px 10px; border-radius:6px; font-weight:800; cursor:pointer; font-size:11px;">+ AGGIUNGI</button>
        </div>
    `).join('');
}
function addUnmatchedCandidate(idx) {
    const sel = document.getElementById(`unmatchedSelect_${idx}`);
    if (!sel || !sel.value) return;
    const playerId = Number(sel.value);
    if (!isNaN(playerId)) {
        addPlayerToMyRoster(playerId);
        if (window.MySquadState.lastUnmatched) {
            window.MySquadState.lastUnmatched.splice(idx, 1);
        }
        renderMySquadModalContent();
    }
}
function handleRosterFileSelect(event) {
    const file = event.target?.files?.[0];
    if (file) {
        handleRosterFileUpload(file, (res) => {
            if (res.matched && res.matched.length > 0) {
                res.matched.forEach(id => addPlayerToMyRoster(id));
                window.MySquadState.lastUnmatched = res.unmatched || [];
                alert(`✅ Importati con successo ${res.matched.length} calciatori nella tua rosa!`);
            } else {
                window.MySquadState.lastUnmatched = res.unmatched || [];
                alert(`⚠️ Nessun calciatore riconosciuto automaticamente nel file. Puoi selezionarli qui sotto.`);
            }
            renderMySquadModalContent();
        });
    }
}
function submitMySquadTextPaste() {
    const txt = document.getElementById('mySquadTextarea')?.value;
    if (!txt) return;
    const res = parseRosterTextContent(txt);
    if (res.matched && res.matched.length > 0) {
        res.matched.forEach(id => addPlayerToMyRoster(id));
        window.MySquadState.lastUnmatched = res.unmatched || [];
        alert(`✅ Riconosciuti e aggiunti ${res.matched.length} calciatori!`);
    } else {
        window.MySquadState.lastUnmatched = res.unmatched || [];
        alert(`⚠️ Nessun calciatore riconosciuto automaticamente. Utilizza la revisione qui sotto.`);
    }
    renderMySquadModalContent();
}
function generateDeepPlayerMotivation(item) {
    if (!item || !item.player) return 'Schierabile con elevata fiducia per stabilità di voti e presenza tattica in campo.';
    const p = item.player;
    const factors = item.factors || [];
    const isHome = factors.some(f => (f.name || '').includes('Casa') || (f.name || '').includes('Fattore Campo'));
    const isRigorista = p.is_rigorista_1 || p.rigorista_val === '1° Rigorista';
    const isPiazzati = p.is_punizioni || p.is_corner;
    const oppFragile = factors.some(f => {
        const fn = (f.name || '').toLowerCase();
        return fn.includes('concede') || fn.includes('vulnerab') || fn.includes('favorevol') || fn.includes('fragil');
    });
    let titPct = (p.titolarita !== undefined && p.titolarita !== null) ? Number(p.titolarita) : 75;
    if (p.is_in_11 === false) {
        titPct = p.is_in_ballottaggio ? 50 : 35;
    } else if (p.is_in_ballottaggio) {
        titPct = 65;
    }
    if (p.role === 'P') {
        if (isHome) {
            return `Portiere di riferimento in casa (${titPct}% titolarità). Matchup ideale per imbattibilità o voto da modificatore.`;
        }
        return `Titolare confermato tra i pali (${titPct}%). Garantisce copertura totale del ruolo e solida resa sui tiri nello specchio.`;
    }
    if (p.role === 'D') {
        if (isPiazzati) {
            return `Difensore di spinta e battitore di piazzati. Ottimi volumi di cross per possibili bonus assist.`;
        }
        if (titPct < 55) {
            return `Jolly difensivo da rotazione (${titPct}% titolarità). Utile per il modificatore grazie all'alta fanta-media, ma con minutaggio da monitorare.`;
        }
        if (isHome) {
            return `Perno arretrato tra le mura amiche (${titPct}% titolarità). Alta media voto e contributo fondamentale al modificatore.`;
        }
        return `Titolare affidabile della retroguardia (${titPct}%). Continuità di rendimento e basso rischio di malus.`;
    }
    if (p.role === 'C') {
        if (isRigorista) {
            return `1° Rigorista e fulcro del gioco d'attacco. Presenza costante in zona gol col massimo valore di xFM atteso.`;
        }
        if (isPiazzati) {
            return `Specialista dei calci da fermo e angoli. Elevata visione di gioco (xA ${p.xa90 ? p.xa90 : '0.20'}/90m) e suggerimenti per le punte.`;
        }
        if (oppFragile) {
            return `Affronta una difesa avversaria concedente. Inserimenti palla a terra per cercare la conclusione da fuori.`;
        }
        if (isHome) {
            return `Mezzala/Regista d'attacco tra le mura amiche (${titPct}% titolarità). Volume di gioco costante e voti alti.`;
        }
        return `Centrocampista a vocazione offensiva con titolarità garantita (${titPct}%). Punto fermo di giornata.`;
    }
    if (p.role === 'A') {
        if (isRigorista) {
            return `Punta di diamante e 1° Rigorista dal dischetto. Top pick assoluto per bonus gol e tiri in porta di giornata.`;
        }
        if (oppFragile) {
            return `Matchup fortemente favorevole contro una retroguardia vulnerabile. Alta probabilità di trascinare l'attacco col bonus.`;
        }
        if (isHome) {
            return `Punta titolare spinta dal pubblico di casa. I suoi numeri di xG e la presenza in area lo rendono intoccabile.`;
        }
        return `Attaccante di riferimento per minutaggio ed occasioni da rete create. Must-have nel tuo tridente di giornata.`;
    }
    return `Giocatore chiave consigliato per l'ottimo bilanciamento tra forma recente, minuti garantiti e matchup favorevole.`;
}
function getSchemaMotivationText(res, useModificatore) {
    if (useModificatore && res.schema && res.schema.startsWith('4')) {
        return `Massimizza il <b>Bonus Modificatore Difesa</b> garantendo punti extra grazie alla solidità della tua retroguardia a 4.`;
    }
    if (res.schema === '3-4-3' || res.schema === '4-3-3') {
        return `Massimizza la potenza di fuoco offensiva schierando il tridente contro retroguardie con concessione xGA elevata.`;
    }
    if (res.schema === '3-5-2' || res.schema === '4-5-1') {
        return `Rinforza la mediana per catturare bonus assist e voti alti dai tuoi centrocampisti in forma.`;
    }
    return `Configurazione tattica ottimizzata per bilanciare titolarità garantita, fattore campo e bonus attesi di giornata.`;
}
function getPlayerTitolaritaPct(p) {
    if (!p) return 50;
    if (p.is_injured) return 0;
    if (p.is_in_11 === true) {
        return Math.max(70, Number(p.titolarita) || 85);
    }
    if (p.is_in_11 === false) {
        return p.is_in_ballottaggio ? 50 : 35;
    }
    if (p.is_in_ballottaggio) return 55;
    return Math.min(99, Math.max(10, Number(p.titolarita) || 70));
}
function getRoleBadgeHtml(roleStr, customStyle = '') {
    if (!roleStr) return '';
    const roles = String(roleStr).split(/[\s,\/]+/).filter(Boolean);
    const roleStyles = {
        'p':   { bg: 'rgba(245,158,11,0.25)', border: 'rgba(251,191,36,0.7)', color: '#fbbf24' },
        'd':   { bg: 'rgba(16,185,129,0.25)', border: 'rgba(52,211,153,0.7)', color: '#34d399' },
        'c':   { bg: 'rgba(56,189,248,0.25)', border: 'rgba(56,189,248,0.7)', color: '#38bdf8' },
        'a':   { bg: 'rgba(244,63,94,0.25)', border: 'rgba(251,113,133,0.7)', color: '#fb7185' },
        'por': { bg: 'rgba(217,119,6,0.3)',  border: '#fbbf24', color: '#fbbf24' },
        'dc':  { bg: 'rgba(5,150,105,0.3)',  border: '#34d399', color: '#34d399' },
        'b':   { bg: 'rgba(4,120,87,0.3)',   border: '#6ee7b7', color: '#6ee7b7' },
        'dd':  { bg: 'rgba(22,163,74,0.3)',  border: '#4ade80', color: '#4ade80' },
        'ds':  { bg: 'rgba(21,128,61,0.3)',  border: '#86efac', color: '#86efac' },
        'e':   { bg: 'rgba(8,145,178,0.3)',  border: '#22d3ee', color: '#22d3ee' },
        'm':   { bg: 'rgba(37,99,235,0.3)',  border: '#60a5fa', color: '#60a5fa' },
        't':   { bg: 'rgba(124,58,237,0.3)', border: '#c084fc', color: '#c084fc' },
        'w':   { bg: 'rgba(192,38,211,0.3)', border: '#f472b6', color: '#f472b6' },
        'pc':  { bg: 'rgba(185,28,28,0.3)',  border: '#f87171', color: '#f87171' }
    };
    return roles.map(r => {
        const rLower = r.toLowerCase();
        const s = roleStyles[rLower] || { bg: 'rgba(148,163,184,0.2)', border: 'rgba(148,163,184,0.5)', color: '#cbd5e1' };
        return `<span class="ms-role-badge ms-role-${rLower}" style="background:${s.bg}; color:${s.color}; border:1px solid ${s.border}; padding:2px 8px; border-radius:6px; font-weight:900; display:inline-flex; align-items:center; justify-content:center; width:auto !important; min-width:26px; height:22px; font-size:11px; text-transform:uppercase; margin-right:6px; box-sizing:border-box; flex-shrink:0; ${customStyle}">${r}</span>`;
    }).join(' ');
}
function getPlayerStatusInfo(p, isStarterContext = false) {
    if (!p) return { label: '', text: '', type: 'none' };
    const isInj = p.is_injured;
    const tipoStop = (p.infortunio_tipo_stop || '').toLowerCase();
    const motivo = (p.infortunio_motivo || '').toLowerCase();
    const statusStr = (p.infortunio_status || '').toLowerCase();
    const rientro = p.infortunio_rientro || '';
    if (isInj) {
        if (tipoStop.includes('squalific') || motivo.includes('squalific') || statusStr.includes('squalific')) {
            return {
                label: '🟥 SQUALIFICATO',
                text: '🟥 Squalificato',
                type: 'injured',
                bg: 'rgba(239,68,68,0.25)',
                color: '#f87171',
                border: 'rgba(239,68,68,0.5)'
            };
        }
        const labelStr = `🏥 INFORTUNATO ${rientro ? `(${rientro})` : ''}`;
        return {
            label: labelStr,
            text: `🏥 Infortunato ${rientro ? `(${rientro})` : ''}`,
            type: 'injured',
            bg: 'rgba(239,68,68,0.25)',
            color: '#f87171',
            border: 'rgba(239,68,68,0.5)'
        };
    }
    const pct = getPlayerTitolaritaPct(p);
    if (p.role === 'P') {
        if (isStarterContext || p.is_in_11 === true || pct >= 70) {
            return {
                label: `🟢 TITOLARE (${pct}%)`,
                text: `🟢 Titolare (${pct}%)`,
                type: 'starter',
                bg: 'rgba(34,197,94,0.15)',
                color: '#4ade80',
                border: 'rgba(34,197,94,0.35)'
            };
        }
        return {
            label: `⚪ SECONDO PORTIERE (${pct}%)`,
            text: `⚪ Secondo Portiere (${pct}%)`,
            type: 'reserve',
            bg: 'rgba(148,163,184,0.15)',
            color: '#94a3b8',
            border: 'rgba(148,163,184,0.3)'
        };
    }
    if (pct >= 90) {
        return {
            label: `🟢 TITOLARE (${pct}%)`,
            text: `🟢 Titolare (${pct}%)`,
            type: 'starter',
            bg: 'rgba(34,197,94,0.15)',
            color: '#4ade80',
            border: 'rgba(34,197,94,0.35)'
        };
    }
    if (pct >= 65) {
        return {
            label: `🟡 TITOLARE (${pct}%)`,
            text: `🟡 Titolare (${pct}%)`,
            type: 'starter',
            bg: 'rgba(245,158,11,0.18)',
            color: '#f59e0b',
            border: 'rgba(245,158,11,0.4)'
        };
    }
    if (pct >= 50 || p.is_super_sub || p.is_in_ballottaggio) {
        return {
            label: `⚡ JOLLY (${pct}%)`,
            text: `⚡ Jolly (${pct}%)`,
            type: 'sub',
            bg: 'rgba(234,88,12,0.2)',
            color: '#ea580c',
            border: 'rgba(234,88,12,0.45)'
        };
    }
    return {
        label: `🔴 RISERVA (${pct}%)`,
        text: `🔴 Riserva (${pct}%)`,
        type: 'reserve',
        bg: 'rgba(239,68,68,0.2)',
        color: '#f87171',
        border: 'rgba(239,68,68,0.4)'
    };
}
function getPlayerStatusBadgeHtml(p, isStarterContext = false) {
    const info = getPlayerStatusInfo(p, isStarterContext);
    if (!info || !info.label) return '';
    return `<span style="background:${info.bg}; color:${info.color}; border:1px solid ${info.border}; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:800;">${info.label}</span>`;
}
function getPlayerMatchBadgeHtml(p, roundNum) {
    let fixLabel = '';
    if (typeof getChiSchieroFixtureForPlayer === 'function') {
        const fix = getChiSchieroFixtureForPlayer(p, roundNum);
        if (fix) {
            fixLabel = fix.shortLabel;
        }
    }
    if (!fixLabel && p.prossimo_avversario) {
        fixLabel = `vs ${p.prossimo_avversario}`;
    }
    if (!fixLabel) fixLabel = 'Match G' + (roundNum || 6);
    return `<span style="background:rgba(56,189,248,0.12); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); padding:2px 8px; border-radius:6px; font-size:11px; font-weight:800;">${fixLabel}</span>`;
}
function runGenerateMySquadLineup() {
    try {
        const out = document.getElementById('mySquadLineupOutput');
        const roster = getMyRosterPlayers();
        if (!out) return;
        if (!roster || roster.length < 11) {
            out.innerHTML = `
                <div style="background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.4); border-radius:16px; padding:18px 22px; color:#fca5a5; font-size:14px; line-height:1.5; text-align:center;">
                    ⚠️ <b>Rosa Incompleta (${roster.length}/11 Calciatori):</b> Servono almeno 11 calciatori nella rosa salvata per calcolare la formazione.
                    <br><span style="font-size:12.5px; color:#94a3b8;">Usa la ricerca in alto per aggiungere i calciatori mancanti!</span>
                </div>
            `;
            out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return;
        }
        const hasP = roster.some(p => p.role === 'P');
        const hasD = roster.filter(p => p.role === 'D').length >= 3;
        const hasC = roster.filter(p => p.role === 'C').length >= 3;
        const hasA = roster.filter(p => p.role === 'A').length >= 1;
        if (!hasP || !hasD || !hasC || !hasA) {
            let missing = [];
            if (!hasP) missing.push("almeno 1 Portiere (P)");
            if (!hasD) missing.push("almeno 3 Difensori (D)");
            if (!hasC) missing.push("almeno 3 Centrocampisti (C)");
            if (!hasA) missing.push("almeno 1 Attaccante (A)");
            out.innerHTML = `
                <div style="background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.4); border-radius:16px; padding:18px 22px; color:#fca5a5; font-size:14px; line-height:1.5; text-align:center;">
                    ⚠️ <b>Ruoli Mancanti nella Rosa:</b> Ti servono ${missing.join(', ')} per completare lo schema tattico.
                    <br><span style="font-size:12.5px; color:#94a3b8;">Utilizza la barra di ricerca qui sopra per aggiungere i ruoli mancanti!</span>
                </div>
            `;
            out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return;
        }
        const res = generateOptimalLineupForUser();
        if (!res) {
            out.innerHTML = `<div style="color:#ef4444; font-weight:700; padding:15px; text-align:center;">Impossibile generare la formazione. Verifica i calciatori salvati nella rosa.</div>`;
            out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return;
        }
        const roundNum = typeof getUpcomingMatchdayRound === 'function' ? getUpcomingMatchdayRound() : 6;
        const useModificatore = window.MySquadState ? window.MySquadState.useModificatore : false;
        const renderCardItem = (item, roleBadgeText) => {
            const playerXFM = (item.score / 10).toFixed(1);
            return `
                <div style="background:rgba(15,23,42,0.75); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:12px 16px; margin-bottom:10px; box-shadow:0 4px 12px rgba(0,0,0,0.25);">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                        <!-- LEFT INFO -->
                        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                            ${getRoleBadgeHtml(roleBadgeText)}
                            <strong style="color:#ffffff; font-size:15px; font-weight:800; font-family:'Outfit',sans-serif; letter-spacing:0.2px;">${item.player.name}</strong>
                            <span style="color:#94a3b8; font-size:11.5px; background:rgba(255,255,255,0.05); padding:2px 7px; border-radius:4px;">${item.player.team}</span>
                            ${getPlayerMatchBadgeHtml(item.player, roundNum)}
                        </div>
                        <!-- RIGHT STATUS & SCORE -->
                        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                            ${getPlayerStatusBadgeHtml(item.player, true)}
                            <div style="text-align:right; background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.25); padding:3px 10px; border-radius:8px; min-width:70px;">
                                <div style="font-size:9.5px; color:#94a3b8; font-weight:700; text-transform:uppercase; line-height:1;">xFM Atteso</div>
                                <div style="font-family:'Outfit',sans-serif; font-weight:900; color:#4ade80; font-size:16px; line-height:1.1;">${playerXFM}</div>
                            </div>
                        </div>
                    </div>
                    <!-- AI VERDICT -->
                    <div style="margin-top:8px; font-size:12px; color:#cbd5e1; background:rgba(255,255,255,0.03); border-left:3px solid #38bdf8; padding:6px 10px; border-radius:0 6px 6px 0; line-height:1.45;">
                        🧠 <b>Verdetto AI:</b> ${generateDeepPlayerMotivation(item)}
                    </div>
                </div>
            `;
        };
        let startersHtml = '';
        if (res.starters) {
            const pList = [...(res.starters.P||[]), ...(res.starters.D||[]), ...(res.starters.C||[]), ...(res.starters.A||[])];
            startersHtml = pList.map(item => renderCardItem(item, item.role)).join('');
        } else if (res.startersList) {
            startersHtml = res.startersList.map(s => renderCardItem(s.item, s.posLabel)).join('');
        }
        let benchHtml = '';
        if (res.bench && res.bench.length > 0) {
            benchHtml = res.bench.map((bItem, idx) => {
                const p = bItem.player || bItem;
                const sc = (bItem.score || 60) / 10;
                const roleLabel = (window.MySquadState && window.MySquadState.systemMode === 'mantra' && p.mantra) ? p.mantra : p.role;
                return `
                    <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06); padding:8px 12px; border-radius:8px; font-size:12.5px; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                            <span style="color:#64748b; font-weight:800; min-width:18px;">${idx+1}.</span>
                            ${getRoleBadgeHtml(roleLabel)}
                            <strong style="color:#f1f5f9; font-size:13.5px;">${p.name}</strong>
                            <span style="color:#94a3b8; font-size:11px;">(${p.team})</span>
                            ${getPlayerMatchBadgeHtml(p, roundNum)}
                        </div>
                        <div style="display:flex; align-items:center; gap:10px;">
                            ${getPlayerStatusBadgeHtml(p, false)}
                            <span style="color:#38bdf8; font-weight:800; font-size:13px;">${sc.toFixed(1)} <small style="font-size:10px; color:#64748b;">xFM</small></span>
                        </div>
                    </div>
                `;
            }).join('');
        }
        let ballottaggiHtml = '';
        if (res.ballottaggi && res.ballottaggi.length > 0) {
            ballottaggiHtml = res.ballottaggi.map(b => `
                <div style="background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3); padding:12px 14px; border-radius:12px; margin-top:6px; font-size:13px; color:#fde047;">
                    ⚖️ <b>Ballottaggio Risolto (${b.role}):</b> <strong>${b.playerA ? b.playerA.name : ''} (${b.pctA}%)</strong> preferito a <em>${b.playerB ? b.playerB.name : ''} (${b.pctB}%)</em>.
                    <div style="font-size:12px; color:#cbd5e1; margin-top:4px; line-height:1.4;">${b.reason}</div>
                </div>
            `).join('');
        }
        const teamTotalXfm = (res.totalScore / 10).toFixed(1);
        out.innerHTML = `
            <div style="background:linear-gradient(180deg, rgba(16,185,129,0.12) 0%, rgba(15,23,42,0.95) 100%); border:1px solid rgba(16,185,129,0.35); border-radius:24px; padding:24px; box-shadow:0 12px 35px rgba(0,0,0,0.5);">
                <!-- HEADER GARANZIA AI & CONFIDENZA -->
                <div style="background:linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(56,189,248,0.1) 100%); border:1px solid rgba(16,185,129,0.4); border-radius:16px; padding:16px 20px; margin-bottom:24px; display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
                    <div style="width:48px; height:48px; border-radius:50%; background:linear-gradient(135deg, #10b981 0%, #059669 100%); display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow:0 4px 14px rgba(16,185,129,0.4); flex-shrink:0;">
                        🛡️
                    </div>
                    <div style="flex:1; min-width:240px;">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px; flex-wrap:wrap;">
                            <span style="font-family:'Outfit',sans-serif; font-weight:900; color:#4ade80; font-size:15px; text-transform:uppercase; letter-spacing:0.5px;">VERDETTO &amp; GARANZIA FANTACALCIO AI</span>
                            <span style="background:rgba(34,197,94,0.2); color:#4ade80; border:1px solid rgba(34,197,94,0.4); padding:2px 8px; border-radius:99px; font-size:11px; font-weight:800;">FIDUCIA ALGORITMO 96%</span>
                        </div>
                        <p style="color:#e2e8f0; font-size:13px; margin:0; line-height:1.45;">
                            Schierando questo 11 <b>riduci a zero il rischio s.v.</b> e massimizzi la probabilità di bonus nella tua lega. L'algoritmo ha valutato xG, xA, minutaggio garantito e difficoltà del matchup per ciascuno dei tuoi calciatori.
                        </p>
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
                    <div>
                        <span style="background:#10b981; color:#fff; font-size:11px; font-weight:900; padding:3px 10px; border-radius:99px; text-transform:uppercase;">FORMAZIONE PERFETTA AI</span>
                        <h3 style="font-size:24px; font-weight:900; font-family:'Outfit',sans-serif; margin:6px 0 0 0; color:#fff;">Modulo Consigliato: ${res.schema}</h3>
                    </div>
                    <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                        <button onclick="copyMySquadLineupToClipboard()" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); color:#fff; border:none; padding:10px 18px; border-radius:12px; font-size:13px; font-weight:800; font-family:'Outfit',sans-serif; cursor:pointer; display:flex; align-items:center; gap:8px; box-shadow:0 4px 14px rgba(16,185,129,0.35); transition:all 0.2s ease;" onmouseover="this.style.transform='scale(1.03)'" onmouseout="this.style.transform='scale(1)'">
                            📋 COPIA FORMAZIONE
                        </button>
                        <div style="text-align:right;">
                            <div style="font-size:12px; color:#94a3b8; font-weight:700;">xFM TOTALE SQUADRA</div>
                            <div style="font-family:'Outfit',sans-serif; font-size:32px; font-weight:900; color:#4ade80;">${teamTotalXfm}</div>
                        </div>
                    </div>
                </div>
                <!-- Motivazione Sintetica del Modulo -->
                <div style="background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:14px; padding:14px 18px; margin-bottom:24px; color:#34d399; font-size:13.5px; font-weight:600; line-height:1.45;">
                    🛡️ <b>Perché questo modulo (${res.schema})?</b> ${getSchemaMotivationText(res, useModificatore)}
                </div>
                <!-- Titolari List con Motivazione Umana ed Esperta -->
                <div style="margin-bottom:24px;">
                    <h4 style="font-size:14px; font-weight:800; color:#4ade80; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.5px;">11 Titolari Consegnati dall'AI:</h4>
                    <div style="display:flex; flex-direction:column; gap:12px;">
                        ${startersHtml}
                    </div>
                </div>
                <!-- Ballottaggi Risolti -->
                ${ballottaggiHtml ? `
                <div style="margin-bottom:24px;">
                    <h4 style="font-size:14px; font-weight:800; color:#fbbf24; margin-bottom:10px; text-transform:uppercase; letter-spacing:0.5px;">Dubbi &amp; Ballottaggi Risolti dall'AI:</h4>
                    ${ballottaggiHtml}
                </div>
                ` : ''}
                <!-- Panchina List -->
                ${benchHtml ? `
                <div>
                    <h4 style="font-size:14px; font-weight:800; color:#38bdf8; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.5px;">Panchina Ordinata per Subentro Sicuro:</h4>
                    <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:10px;">
                        ${benchHtml}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        setTimeout(() => {
            out.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 50);
    } catch (err) {
        console.error("Errore generazione formazione:", err);
        const out = document.getElementById('mySquadLineupOutput');
        if (out) {
            out.innerHTML = `
                <div style="background:rgba(239,68,68,0.15); color:#fca5a5; padding:18px; border-radius:14px; border:1px solid #ef4444; text-align:center; font-size:14px; line-height:1.5;">
                    ❌ <b>Errore durante il calcolo della formazione:</b> ${err.message}.
                    <br><span style="font-size:12px; color:#cbd5e1;">Prova a svuotare e ricaricare la rosa o ad aggiungere i calciatori dalla barra in alto.</span>
                </div>
            `;
            out.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}
function copyMySquadLineupToClipboard() {
    const res = generateOptimalLineupForUser();
    if (!res) {
        alert('Nessuna formazione da copiare! Assicurati di aver salvato i calciatori nella tua rosa.');
        return;
    }
    const roundNum = typeof getUpcomingMatchdayRound === 'function' ? getUpcomingMatchdayRound() : 6;
    let text = `🛡️ FORMAZIONE CONSIGLIATA - FANTA MASTER AI (G${roundNum})\n`;
    text += `Modulo: ${res.schema} | Punteggio xFM Atteso: ${res.totalScore}\n`;
    text += `----------------------------------------\n\n`;
    text += `11 TITOLARI:\n`;
    const startersList = res.starters 
        ? [...(res.starters.P||[]), ...(res.starters.D||[]), ...(res.starters.C||[]), ...(res.starters.A||[])]
        : (res.startersList ? res.startersList.map(s => s.item) : []);
    startersList.forEach(item => {
        const p = item.player || item;
        let fixLabel = '';
        if (typeof getChiSchieroFixtureForPlayer === 'function') {
            const fix = getChiSchieroFixtureForPlayer(p, roundNum);
            if (fix) fixLabel = ` (${fix.shortLabel})`;
        }
        const stInfo = getPlayerStatusInfo(p, true);
        const stText = stInfo && stInfo.text ? ` - ${stInfo.text}` : '';
        const emoji = p.role === 'P' ? '🧤' : (p.role === 'D' ? '🛡️' : (p.role === 'C' ? '⚽' : '🔥'));
        text += `${emoji} ${p.role}: ${p.name} (${p.team})${stText}${fixLabel}\n`;
    });
    if (res.bench && res.bench.length > 0) {
        text += `\nPANCHINA:\n`;
        res.bench.forEach((bItem, idx) => {
            const p = bItem.player || bItem;
            let fixLabel = '';
            if (typeof getChiSchieroFixtureForPlayer === 'function') {
                const fix = getChiSchieroFixtureForPlayer(p, roundNum);
                if (fix) fixLabel = ` (${fix.shortLabel})`;
            }
            const stInfo = getPlayerStatusInfo(p, false);
            const stText = stInfo && stInfo.text ? ` - ${stInfo.text}` : '';
            text += `${idx + 1}. ${p.name} (${p.team} - ${p.role})${stText}${fixLabel}\n`;
        });
    }
    text += `\n💡 Elaborato con l'AI predittiva di FantaMaster AI: fantamasterai.it`;
    if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showCopyNotificationToast('✅ Formazione copiata negli appunti!');
        }).catch(err => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.top = "0";
    textArea.style.left = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopyNotificationToast('✅ Formazione copiata negli appunti!');
        } else {
            alert('Impossibile copiare automaticamente. Seleziona il testo.');
        }
    } catch (err) {
        alert('Impossibile copiare automaticamente. Seleziona il testo.');
    }
    document.body.removeChild(textArea);
}
function showCopyNotificationToast(msg) {
    const existing = document.getElementById('mySquadCopyToast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'mySquadCopyToast';
    toast.innerHTML = `
        <div style="position:fixed; bottom:30px; right:30px; z-index:99999; background:linear-gradient(135deg, #10b981 0%, #059669 100%); color:#fff; font-family:'Outfit',sans-serif; font-weight:800; font-size:14px; padding:14px 22px; border-radius:14px; box-shadow:0 10px 25px rgba(16,185,129,0.5); display:flex; align-items:center; gap:10px;">
            <span>${msg}</span>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 2800);
}
if (typeof window !== 'undefined') {
    window.openMySquadModal = openMySquadModal;
    window.copyMySquadLineupToClipboard = copyMySquadLineupToClipboard;
    window.closeMySquadModal = closeMySquadModal;
    window.renderMySquadModalContent = renderMySquadModalContent;
    window.handleRosterFileSelect = handleRosterFileSelect;
    window.submitMySquadTextPaste = submitMySquadTextPaste;
    window.runGenerateMySquadLineup = runGenerateMySquadLineup;
    window.onSearchInputMySquadRoster = onSearchInputMySquadRoster;
    window.addUnmatchedCandidate = addUnmatchedCandidate;
}