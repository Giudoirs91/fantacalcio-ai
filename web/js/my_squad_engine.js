// ==============================================================================
// MODULO "LA MIA ROSA & GENERATORE FORMAZIONE AI" (CLASSIC & MANTRA)
// Serie A 2026/27 — FantaMaster AI
// ==============================================================================

window.MySquadState = {
    rosterIds: [],        // Array di ID calciatori salvati nella rosa dell'utente
    systemMode: 'classic', // 'classic' | 'mantra'
    useModificatore: false, // true | false (solo per Classic 4-DEF)
    targetRound: null,     // Round stimato (default 6)
    lastGeneratedLineup: null
};

const MY_ROSTER_STORAGE_KEY = 'FANTA_MASTER_AI_MY_ROSTER_2026_27';

// ------------------------------------------------------------------------------
// 1. CARICAMENTO E PERSISTENZA LOCALSTORAGE
// ------------------------------------------------------------------------------
function loadMyRosterFromStorage() {
    try {
        const raw = localStorage.getItem(MY_ROSTER_STORAGE_KEY);
        if (raw) {
            const parsed = JSON.load ? JSON.parse(raw) : eval('(' + raw + ')');
            if (Array.isArray(parsed)) {
                window.MySquadState.rosterIds = parsed.map(Number).filter(n => !isNaN(n));
            }
        }
    } catch(e) {
        console.warn('Errore lettura myRoster da storage:', e);
    }
}

function saveMyRosterToStorage() {
    try {
        localStorage.setItem(MY_ROSTER_STORAGE_KEY, JSON.stringify(window.MySquadState.rosterIds));
    } catch(e) {
        console.warn('Errore salvataggio myRoster in storage:', e);
    }
}

// ------------------------------------------------------------------------------
// 2. IMPORTATORE FILE CSV / XML / TXT (LEGHE FANTACALCIO.IT)
// ------------------------------------------------------------------------------
function parseRosterTextContent(textContent) {
    if (!textContent || typeof textContent !== 'string') return { matched: [], unmatched: [] };
    
    const lines = textContent.split(/[\r\n]+/);
    const matchedIds = new Set();
    const unmatchedNames = [];

    lines.forEach(line => {
        let clean = line.trim();
        if (!clean || clean.startsWith('#') || clean.startsWith('//') || clean.toLowerCase().includes('ruolo;') || clean.toLowerCase().includes('calciatore;')) return;

        // Se la riga contiene separatori CSV/TSV (punto e coma, virgola, tab)
        let parts = clean.split(/[;\t,]/);
        let rawName = "";
        
        if (parts.length >= 2) {
            // Cerca la colonna che contiene il nome del calciatore
            for (let p of parts) {
                let s = p.trim().replace(/^["']|["']$/g, '');
                if (s.length >= 3 && !/^(P|D|C|A|Por|Dc|Dd|Ds|E|M|C|T|W|A|Pc|\d+)$/i.test(s)) {
                    rawName = s;
                    break;
                }
            }
            if (!rawName) rawName = parts[1].trim();
        } else {
            rawName = clean;
        }

        // Pulisce eventuali numeri o indicazioni di prezzo finali (es. "Lautaro Martinez 120" -> "Lautaro Martinez")
        rawName = rawName.replace(/\s+\d+\s*$/, '').replace(/^\d+\s+/, '').trim();

        if (rawName && typeof matchPlayerFuzzy === 'function') {
            const match = matchPlayerFuzzy(rawName);
            if (match && match.id) {
                matchedIds.add(match.id);
            } else if (rawName.length > 2) {
                unmatchedNames.push(rawName);
            }
        }
    });

    return {
        matched: Array.from(matchedIds),
        unmatched: unmatchedNames
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

// ------------------------------------------------------------------------------
// 3. ENGINE DI CALCOLO E GENERATORE FORMAZIONE PERFETTA AI
// ------------------------------------------------------------------------------
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

// ALGORITMO OTTIMIZZATORE LINEUP PER LA ROSA DELL'UTENTE
function generateOptimalLineupForUser(options = {}) {
    const roundNum = options.round || (typeof getUpcomingMatchdayRound === 'function' ? getUpcomingMatchdayRound() : 6);
    const mode = options.mode || window.MySquadState.systemMode || 'classic';
    const useModificatore = (options.useModificatore !== undefined) ? options.useModificatore : window.MySquadState.useModificatore;

    const roster = getMyRosterPlayers();
    if (!roster.length) return null;

    // 1. Calcola il rating atteso per la giornata per ogni calciatore in rosa
    const evaluatedRoster = roster.map(p => {
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

// OTTIMIZZATORE SCHEMI CLASSIC (3-4-3, 4-3-3, 3-5-2, 4-4-2, 4-5-1, 3-4-1-2, 4-2-3-1)
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

    const por = items.filter(x => x.role === 'P').sort((a,b) => b.score - a.score);
    const def = items.filter(x => x.role === 'D').sort((a,b) => b.score - a.score);
    const cen = items.filter(x => x.role === 'C').sort((a,b) => b.score - a.score);
    const att = items.filter(x => x.role === 'A').sort((a,b) => b.score - a.score);

    if (!por.length) return null;

    let bestSchemaResult = null;
    let maxTotalScore = -999;

    SCHEMAS.forEach(sch => {
        if (def.length < sch.D || cen.length < sch.C || att.length < sch.A) return;

        const starterPor = por.slice(0, 1);
        const starterDef = def.slice(0, sch.D);
        const starterCen = cen.slice(0, sch.C);
        const starterAtt = att.slice(0, sch.A);

        let totalScore = starterPor[0].score +
            starterDef.reduce((sum, x) => sum + x.score, 0) +
            starterCen.reduce((sum, x) => sum + x.score, 0) +
            starterAtt.reduce((sum, x) => sum + x.score, 0);

        // Bonus Modificatore di Difesa per schemi a 4 difensori
        if (useModificatore && sch.D >= 4) {
            const avgDefScore = starterDef.reduce((sum, x) => sum + x.score, 0) / sch.D;
            if (avgDefScore >= 75) totalScore += 18.0; // Bonus Modificatore alto
            else if (avgDefScore >= 70) totalScore += 10.0;
        }

        if (totalScore > maxTotalScore) {
            maxTotalScore = totalScore;
            
            // Costruisce Panchina Ordinata (P1, D1, D2, C1, C2, C3, A1, A2)
            const benchPor = por.slice(1);
            const benchDef = def.slice(sch.D);
            const benchCen = cen.slice(sch.C);
            const benchAtt = att.slice(sch.A);

            const bench = [
                ...benchPor.slice(0, 1),
                ...benchDef.slice(0, 3),
                ...benchCen.slice(0, 4),
                ...benchAtt.slice(0, 3)
            ];

            // Rileva Ballottaggi Interni (giocatori esclusi vicini nel punteggio a quelli titolari)
            const ballottaggi = [];
            if (benchAtt.length > 0 && starterAtt.length > 0) {
                const minStartAtt = starterAtt[starterAtt.length - 1];
                const topBenchAtt = benchAtt[0];
                if (Math.abs(minStartAtt.score - topBenchAtt.score) < 8.0) {
                    const pctStart = Math.round(50 + (minStartAtt.score - topBenchAtt.score) * 2.5);
                    ballottaggi.push({
                        role: 'Attacco',
                        playerA: minStartAtt.player,
                        playerB: topBenchAtt.player,
                        pctA: Math.min(80, Math.max(52, pctStart)),
                        pctB: 100 - Math.min(80, Math.max(52, pctStart)),
                        reason: `Ballottaggio serrato in attacco: ${minStartAtt.player.name} ha un matchup leggermente migliore di ${topBenchAtt.player.name}.`
                    });
                }
            }

            bestSchemaResult = {
                schema: sch.name,
                starters: {
                    P: starterPor,
                    D: starterDef,
                    C: starterCen,
                    A: starterAtt
                },
                bench: bench,
                totalScore: Math.round(totalScore * 10) / 10,
                ballottaggi: ballottaggi
            };
        }
    });

    return bestSchemaResult;
}

// OTTIMIZZATORE SCHEMI MANTRA (11 SCHEMI UFFICIALI)
function optimizeMantraLineup(items, roundNum) {
    if (typeof MANTRA_RAW_SCHEMAS === 'undefined') return null;

    const por = items.filter(x => x.mantra.includes('Por') || x.role === 'P').sort((a,b) => b.score - a.score);
    if (!por.length) return null;

    let bestSchemaResult = null;
    let maxTotalScore = -999;

    Object.keys(MANTRA_RAW_SCHEMAS).forEach(schKey => {
        const schema = MANTRA_RAW_SCHEMAS[schKey];
        const assignedStarters = [];
        const usedIds = new Set();

        // Assegna Portiere
        assignedStarters.push({ posLabel: 'Por', item: por[0] });
        usedIds.add(por[0].player.id);

        let validSchema = true;
        let schemaScore = por[0].score;

        // Scorre le linee tattiche dello schema dal basso verso l'alto
        schema.lines.forEach(line => {
            if (line[0].pos === 'Por') return; // già assegnato
            line.forEach(slot => {
                const candidate = items.find(x => {
                    if (usedIds.has(x.player.id)) return false;
                    const pMantraRoles = (x.player.mantra || '').split(/[\s;,\/]+/);
                    return slot.roles.some(r => pMantraRoles.includes(r));
                });

                if (candidate) {
                    usedIds.add(candidate.player.id);
                    assignedStarters.push({ posLabel: slot.pos, item: candidate });
                    schemaScore += candidate.score;
                } else {
                    validSchema = false;
                }
            });
        });

        if (validSchema && schemaScore > maxTotalScore) {
            maxTotalScore = schemaScore;
            const bench = items.filter(x => !usedIds.has(x.player.id)).sort((a,b) => b.score - a.score);

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

// ------------------------------------------------------------------------------
// 4. VISTA SEMPLIFICATA (EASY MODE) VS PRO DATA MODE
// ------------------------------------------------------------------------------
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

// ------------------------------------------------------------------------------
// 5. INIZIALIZZAZIONE & ESPORTAZIONE GLOBALE
// ------------------------------------------------------------------------------
if (typeof window !== 'undefined') {
    window.loadMyRosterFromStorage = loadMyRosterFromStorage;
    window.saveMyRosterToStorage = saveMyRosterToStorage;
    window.parseRosterTextContent = parseRosterTextContent;
    window.handleRosterFileUpload = handleRosterFileUpload;
    window.getMyRosterPlayers = getMyRosterPlayers;
    window.addPlayerToMyRoster = addPlayerToMyRoster;
    window.removePlayerFromMyRoster = removePlayerFromMyRoster;
    window.clearMyRoster = clearMyRoster;
    window.generateOptimalLineupForUser = generateOptimalLineupForUser;
    window.setDataViewMode = setDataViewMode;
    window.updateDataViewModeUI = updateDataViewModeUI;

    window.addEventListener('DOMContentLoaded', () => {
        loadMyRosterFromStorage();
        try {
            const savedMode = localStorage.getItem('FANTA_DATA_VIEW_MODE') || 'easy';
            if (typeof State !== 'undefined') State.dataViewMode = savedMode;
            updateDataViewModeUI();
        } catch(e) {}
    });
}
