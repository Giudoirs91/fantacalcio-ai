// ==============================================================================
// GESTIONE STATO GLOBALE E PERSISTENZA LOCALSTORAGE (CON PREFERITI & RADAR RIVALI)
// ==============================================================================

// ==============================================================================
// MODALITÀ CREATORE (ACCESSO RISERVATO CRITTOGRAFATO SHA-256)
// ==============================================================================
let _logoClicks = 0;
let _logoClickTimer = null;

function handleBrandSecretClick() {
    _logoClicks++;
    clearTimeout(_logoClickTimer);
    _logoClickTimer = setTimeout(() => { _logoClicks = 0; }, 2500);
    if (_logoClicks >= 5) {
        _logoClicks = 0;
        openCreatorAuthModal();
    }
}

// Scorciatoia da tastiera per creatore (Ctrl + Shift + K)
if (typeof window !== 'undefined') {
    window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'K' || e.key === 'k')) {
            e.preventDefault();
            openCreatorAuthModal();
        }
    });
}

function isCreatorModeActive() {
    try {
        return localStorage.getItem('FANTA_CREATOR_MODE') === 'true';
    } catch(e) {
        return false;
    }
}

function setCreatorMode(active) {
    try {
        if (active) {
            localStorage.setItem('FANTA_CREATOR_MODE', 'true');
        } else {
            localStorage.removeItem('FANTA_CREATOR_MODE');
        }
    } catch(e) {}
    updateCreatorModeUI();
}

function updateCreatorModeUI() {
    const active = isCreatorModeActive();
    if (typeof document !== 'undefined' && document.body) {
        if (active) {
            document.body.classList.add('creator-mode-active');
        } else {
            document.body.classList.remove('creator-mode-active');
        }
    }
    const badge = document.getElementById('creatorStatusBadge');
    if (badge) {
        badge.style.display = active ? 'inline-flex' : 'none';
    }
}

function openCreatorAuthModal() {
    if (isCreatorModeActive()) {
        const confirmExit = confirm("👑 Sei attualmente in Modalità Creatore.\n\nVuoi disattivarla e tornare alla vista visitatore ordinario?");
        if (confirmExit) {
            setCreatorMode(false);
            window.location.reload();
        }
        return;
    }
    const modal = document.getElementById('creatorAuthModal');
    const input = document.getElementById('creatorPasswordInput');
    const err = document.getElementById('creatorAuthError');
    if (err) err.style.display = 'none';
    if (input) input.value = '';
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => { if (input) input.focus(); }, 150);
    }
}

function closeCreatorAuthModal() {
    const modal = document.getElementById('creatorAuthModal');
    if (modal) modal.style.display = 'none';
}

async function hashSha256(str) {
    const buffer = new TextEncoder().encode(str);
    const hash = await crypto.subtle.digest('SHA-256', buffer);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function submitCreatorAuth() {
    const input = document.getElementById('creatorPasswordInput');
    const err = document.getElementById('creatorAuthError');
    if (!input) return;
    const pwd = input.value.trim();
    if (!pwd) return;

    const hash = await hashSha256(pwd);
    const customHash = localStorage.getItem('FANTA_CREATOR_PWD_HASH');
    
    // Hash SHA-256 autorizzati (crittografati, nessuna password visibile in chiaro)
    const ALLOWED_HASHES = [
        '4be6e680a6dd2ee9957770984dd0c7f2dd8be7c703b44b80b7d7809630c8225d', // hash 1991
        '56a4221a71ca2eb05b76c8c4a45a19fe99ba28d9ffb4b4d7fca1caec83a31c59'  // hash fantapass2026
    ];
    if (customHash) ALLOWED_HASHES.push(customHash);

    if (ALLOWED_HASHES.includes(hash)) {
        closeCreatorAuthModal();
        setCreatorMode(true);
        window.location.reload();
    } else {
        if (err) {
            err.textContent = '❌ Password non corretta';
            err.style.display = 'block';
        }
        input.value = '';
        input.focus();
    }
}

// Parametro URL ?login=creator apre la finestra di login crittografata
(function checkCreatorUrlParams() {
    try {
        if (typeof window !== 'undefined' && window.location) {
            const params = new URLSearchParams(window.location.search);
            if (params.get('login') === 'creator') {
                window.addEventListener('DOMContentLoaded', () => {
                    setTimeout(openCreatorAuthModal, 300);
                });
            }
        }
    } catch(e) {}
})();

if (typeof window !== 'undefined') {
    window.isCreatorModeActive = isCreatorModeActive;
    window.setCreatorMode = setCreatorMode;
    window.updateCreatorModeUI = updateCreatorModeUI;
    window.openCreatorAuthModal = openCreatorAuthModal;
    window.closeCreatorAuthModal = closeCreatorAuthModal;
    window.submitCreatorAuth = submitCreatorAuth;
    window.handleBrandSecretClick = handleBrandSecretClick;
    window.addEventListener('DOMContentLoaded', updateCreatorModeUI);
}

const STORAGE_KEY = 'FANTA_MASTER_AI_STATE_2026_27';

const RIVALS_TEMPLATE = {
    'Squadra A': { manager: 'Manager 1', tendency: 'Aggressivo su 1° Portiere e Super Bomber', budget: 1000, spent: 0, players: [] },
    'Squadra B': { manager: 'Manager 2', tendency: 'All-in su Attaccanti e Modificatore Difesa', budget: 1000, spent: 0, players: [] },
    'Squadra C': { manager: 'Manager 3', tendency: 'Equilibrato, caccia ai terzini da assist', budget: 1000, spent: 0, players: [] },
    'Squadra D': { manager: 'Manager 4', tendency: 'Risparmio dietro, all-in su 2 Top Attaccanti', budget: 1000, spent: 0, players: [] },
    'Squadra E': { manager: 'Manager 5', tendency: 'Focus su rigoristi e incursori', budget: 1000, spent: 0, players: [] },
    'Squadra F': { manager: 'Manager 6', tendency: 'Low cost a 1 CR e accumulo budget per le punte', budget: 1000, spent: 0, players: [] },
    'Squadra G': { manager: 'Manager 7', tendency: 'Spesa mirata su centrocampo e scommesse offensive', budget: 1000, spent: 0, players: [] }
};

const DefaultState = {
    teamName: 'La Mia Rosa',
    budgetTotal: 1000,
    budgetSpent: 0,
    slots: {
        P: { max: 3, players: [] },
        D: { max: 8, players: [] },
        C: { max: 8, players: [] },
        A: { max: 6, players: [] }
    },
    favorites: [], // Array di ID calciatori preferiti (⭐)
    takenByOthers: [], // Array di ID calciatori presi da altri
    rivalAssignments: {}, // { playerId: { rival: 'Squadra A', price: 45 } }
    rivals: JSON.parse(JSON.stringify(RIVALS_TEMPLATE)),
    playerOverrides: {}, // { [playerId]: { slot_fascia, slot_num, oop_val, is_oop, fpp_fpn, ai_advice, consiglio, ai_advice_type } }
    
    systemMode: 'classic', // 'classic' o 'mantra'
    
    // Filtri per Creazione Squadra Unificata
    sbRole: 'ALL', // 'ALL', 'P', 'D', 'C', 'A' o Ruolo Mantra
    sbAdvice: 'ALL',
    sbOnlyFav: false,
    sbOnlyAvail: true,
    sbQuery: '',
    sbViewMode: 'list', // 'list' o 'grid'

    activeTab: 'auction',
    currentTeamPitch: 'Inter',
    filterRole: 'ALL',
    filterTeam: 'ALL',
    filterSlot: 'ALL',
    filterAdvice: 'ALL',
    filterFragilita: 'ALL',
    filterRigoristi: 'ALL',
    filterTitolarita: 'ALL',
    filterPriceRange: 'ALL',
    filterOop: false,
    filterInjured: false,
    filterHealthy: false,
    filterOnlyAvailable: false,
    filterOnlyFavorites: false,
    searchQuery: '',
    sortBy: 'ovr',
    sortAsc: false,
    matchupA: null,
    matchupB: null
};

let State = { ...DefaultState };

// ==============================================================================
// METADATA & 11 SCHEMI UFFICIALI SISTEMA MANTRA (FANTACALCIO.IT)
// ==============================================================================
const MANTRA_ROLES_META = {
    'Por': { name: 'Portiere', dept: 'Por', color: '#d97706', border: '#fbbf24', order: 1 },
    'Dc':  { name: 'Difensore Centrale', dept: 'Dif', color: '#059669', border: '#34d399', order: 2 },
    'B':   { name: 'Braccetto / Terzo di Difesa', dept: 'Dif', color: '#047857', border: '#6ee7b7', order: 3 },
    'Dd':  { name: 'Terzino Destro', dept: 'Dif', color: '#16a34a', border: '#4ade80', order: 4 },
    'Ds':  { name: 'Terzino Sinistro', dept: 'Dif', color: '#15803d', border: '#86efac', order: 5 },
    'E':   { name: 'Esterno a Tutta Fascia', dept: 'Med', color: '#0891b2', border: '#22d3ee', order: 6 },
    'M':   { name: 'Mediano Difensivo / Interdittore', dept: 'Med', color: '#2563eb', border: '#60a5fa', order: 7 },
    'C':   { name: 'Centrocampista Centrale / Mezzala', dept: 'Med', color: '#0284c7', border: '#38bdf8', order: 8 },
    'T':   { name: 'Trequartista / Fantasista', dept: 'Att', color: '#7c3aed', border: '#c084fc', order: 9 },
    'W':   { name: 'Ala Offensiva Pura', dept: 'Att', color: '#c026d3', border: '#f472b6', order: 10 },
    'A':   { name: 'Seconda Punta / Attaccante Raccordo', dept: 'Att', color: '#e11d48', border: '#fb7185', order: 11 },
    'Pc':  { name: 'Punta Centrale / Centravanti', dept: 'Att', color: '#b91c1c', border: '#f87171', order: 12 }
};

const MANTRA_RAW_SCHEMAS = {
    '3-4-3': {
        name: '3-4-3',
        description: 'Difesa a 3 (2 Dc + 1 Dc/B), Centrocampo (E - M/C - C - E), Tridente Offensivo (W/A - A/Pc - W/A)',
        defCount: 3,
        lines: [
            [ { pos: 'W/A', roles: ['W', 'A'] }, { pos: 'A/Pc', roles: ['A', 'Pc'] }, { pos: 'W/A', roles: ['W', 'A'] } ],
            [ { pos: 'E', roles: ['E'] }, { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'C', roles: ['C'] }, { pos: 'E', roles: ['E'] } ],
            [ { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc/B', roles: ['Dc', 'B'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '3-4-1-2': {
        name: '3-4-1-2',
        description: 'Difesa a 3 (2 Dc + 1 Dc/B), Centrocampo (E - M/C - C - E), Trequartista T e Coppia d\'Attacco (2 A/Pc)',
        defCount: 3,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] }, { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'T', roles: ['T'] } ],
            [ { pos: 'E', roles: ['E'] }, { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'C', roles: ['C'] }, { pos: 'E', roles: ['E'] } ],
            [ { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc/B', roles: ['Dc', 'B'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '3-4-2-1': {
        name: '3-4-2-1',
        description: 'Difesa a 3 (2 Dc + 1 Dc/B), Centrocampo (E/W - M - M/C - E), Due Trequartisti (T e T/A) e 1 A/Pc',
        defCount: 3,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'T', roles: ['T'] }, { pos: 'T/A', roles: ['T', 'A'] } ],
            [ { pos: 'E/W', roles: ['E', 'W'] }, { pos: 'M', roles: ['M'] }, { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'E', roles: ['E'] } ],
            [ { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc/B', roles: ['Dc', 'B'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '3-5-2': {
        name: '3-5-2',
        description: 'Difesa a 3 (2 Dc + 1 Dc/B), Centrocampo a 5 (E/W - M/C - M - C - E) e Coppia d\'Attacco (2 A/Pc)',
        defCount: 3,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] }, { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'E/W', roles: ['E', 'W'] }, { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'M', roles: ['M'] }, { pos: 'C', roles: ['C'] }, { pos: 'E', roles: ['E'] } ],
            [ { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc/B', roles: ['Dc', 'B'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '3-5-1-1': {
        name: '3-5-1-1',
        description: 'Difesa a 3 (2 Dc + 1 Dc/B), Centrocampo a 5 (E/W - M - C - M - E/W), Trequartista T/A e 1 A/Pc',
        defCount: 3,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'T/A', roles: ['T', 'A'] } ],
            [ { pos: 'E/W', roles: ['E', 'W'] }, { pos: 'M', roles: ['M'] }, { pos: 'C', roles: ['C'] }, { pos: 'M', roles: ['M'] }, { pos: 'E/W', roles: ['E', 'W'] } ],
            [ { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc/B', roles: ['Dc', 'B'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '4-3-3': {
        name: '4-3-3',
        description: 'Difesa a 4 (Dd - 2 Dc - Ds), Centrocampo a 3 (M/C - M - C), Tridente (W/A - A/Pc - W/A)',
        defCount: 4,
        lines: [
            [ { pos: 'W/A', roles: ['W', 'A'] }, { pos: 'A/Pc', roles: ['A', 'Pc'] }, { pos: 'W/A', roles: ['W', 'A'] } ],
            [ { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'M', roles: ['M'] }, { pos: 'C', roles: ['C'] } ],
            [ { pos: 'Ds', roles: ['Ds'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dd', roles: ['Dd'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '4-3-1-2': {
        name: '4-3-1-2',
        description: 'Difesa a 4 (Dd - 2 Dc - Ds), Centrocampo a 3 (M/C - M - C), Trequartista T e Coppia d\'Attacco (T/A/Pc + A/Pc)',
        defCount: 4,
        lines: [
            [ { pos: 'T/A/Pc', roles: ['T', 'A', 'Pc'] }, { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'T', roles: ['T'] } ],
            [ { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'M', roles: ['M'] }, { pos: 'C', roles: ['C'] } ],
            [ { pos: 'Ds', roles: ['Ds'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dd', roles: ['Dd'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '4-4-2': {
        name: '4-4-2',
        description: 'Difesa a 4 (Dd - 2 Dc - Ds), Centrocampo (E/W - M/C - C - E) e Due Punte (2 A/Pc)',
        defCount: 4,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] }, { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'E/W', roles: ['E', 'W'] }, { pos: 'M/C', roles: ['M', 'C'] }, { pos: 'C', roles: ['C'] }, { pos: 'E', roles: ['E'] } ],
            [ { pos: 'Ds', roles: ['Ds'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dd', roles: ['Dd'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '4-1-4-1': {
        name: '4-1-4-1',
        description: 'Difesa a 4 (Dd - 2 Dc - Ds), Mediano M, Linea a 4 (E/W - C/T - T - W) e 1 A/Pc',
        defCount: 4,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'E/W', roles: ['E', 'W'] }, { pos: 'C/T', roles: ['C', 'T'] }, { pos: 'T', roles: ['T'] }, { pos: 'W', roles: ['W'] } ],
            [ { pos: 'M', roles: ['M'] } ],
            [ { pos: 'Ds', roles: ['Ds'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dd', roles: ['Dd'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '4-4-1-1': {
        name: '4-4-1-1',
        description: 'Difesa a 4 (Dd - 2 Dc - Ds), Centrocampo (E/W - M - C - E/W), Trequartista T/A e 1 A/Pc',
        defCount: 4,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'T/A', roles: ['T', 'A'] } ],
            [ { pos: 'E/W', roles: ['E', 'W'] }, { pos: 'M', roles: ['M'] }, { pos: 'C', roles: ['C'] }, { pos: 'E/W', roles: ['E', 'W'] } ],
            [ { pos: 'Ds', roles: ['Ds'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dd', roles: ['Dd'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    },
    '4-2-3-1': {
        name: '4-2-3-1',
        description: 'Difesa a 4 (Dd - 2 Dc - Ds), Doppia Mediana (M + M/C), Trequarti (W/T - T - W/A) e 1 A/Pc',
        defCount: 4,
        lines: [
            [ { pos: 'A/Pc', roles: ['A', 'Pc'] } ],
            [ { pos: 'W/T', roles: ['W', 'T'] }, { pos: 'T', roles: ['T'] }, { pos: 'W/A', roles: ['W', 'A'] } ],
            [ { pos: 'M', roles: ['M'] }, { pos: 'M/C', roles: ['M', 'C'] } ],
            [ { pos: 'Ds', roles: ['Ds'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dc', roles: ['Dc'] }, { pos: 'Dd', roles: ['Dd'] } ],
            [ { pos: 'Por', roles: ['Por'] } ]
        ]
    }
};

// Costruisci MANTRA_FORMATIONS assicurando retrocompatibilità completa con 'slots'
const MANTRA_FORMATIONS = {};
for (const [key, val] of Object.entries(MANTRA_RAW_SCHEMAS)) {
    MANTRA_FORMATIONS[key] = {
        ...val,
        slots: val.lines.flat()
    };
}

function renderMantraRoleBadges(mantraStr, extraClass = '') {
    if (!mantraStr) return '<span class="mantra-badge" style="background:#475569;color:#fff;">-</span>';
    const subroles = String(mantraStr).split(';').map(s => s.trim()).filter(Boolean);
    if (subroles.length === 0) return '<span class="mantra-badge" style="background:#475569;color:#fff;">-</span>';
    
    const badgesHtml = subroles.map(sr => {
        const key = sr.toLowerCase();
        const meta = MANTRA_ROLES_META[sr] || { name: sr };
        return `<span class="mantra-badge ${key} ${extraClass}" title="${meta.name || sr}">${sr}</span>`;
    }).join('');

    return `<div class="mantra-badge-group">${badgesHtml}</div>`;
}

function getMantraHierarchyScore(mantraStr) {
    if (!mantraStr) return 999;
    const subroles = String(mantraStr).split(';').map(s => s.trim()).filter(Boolean);
    if (subroles.length === 0) return 999;
    let minOrder = 999;
    subroles.forEach(sr => {
        const ord = (MANTRA_ROLES_META[sr] && MANTRA_ROLES_META[sr].order) || 50;
        if (ord < minOrder) minOrder = ord;
    });
    return minOrder;
}

function isPlayerEligibleForMantraRole(player, roleFilter) {
    if (!roleFilter || roleFilter === 'ALL') return true;
    const pMantra = String(player.mantra || '').split(';').map(s => s.trim().toUpperCase()).filter(Boolean);
    
    if (roleFilter === 'MULTI') {
        return pMantra.length >= 2;
    }
    if (roleFilter === 'DEF_ALL') {
        return pMantra.some(r => ['DC', 'B', 'DD', 'DS'].includes(r));
    }
    if (roleFilter === 'MID_ALL') {
        return pMantra.some(r => ['E', 'M', 'C'].includes(r));
    }
    if (roleFilter === 'ATT_ALL') {
        return pMantra.some(r => ['T', 'W', 'A', 'PC'].includes(r));
    }
    
    const target = roleFilter.toUpperCase();
    return pMantra.includes(target);
}

function getSystemMode() {
    return State.systemMode || 'classic';
}

function setSystemMode(mode, save = true) {
    const validMode = (mode === 'mantra') ? 'mantra' : 'classic';
    State.systemMode = validMode;
    
    // Aggiorna anche la modalità nella lega attiva persistita
    if (typeof LeaguesManager !== 'undefined' && typeof LeaguesManager.getActive === 'function') {
        const leagues = LeaguesManager.getAll();
        const activeId = LeaguesManager.getActiveId();
        const currentLeague = leagues.find(l => l.id === activeId);
        if (currentLeague && currentLeague.systemMode !== validMode) {
            currentLeague.systemMode = validMode;
            LeaguesManager.saveAll(leagues);
        }
    }
    
    // Aggiorna classi bottoni header
    const btnClassic = document.getElementById('btnModeClassic');
    const btnMantra = document.getElementById('btnModeMantra');
    if (btnClassic) {
        if (validMode === 'classic') btnClassic.classList.add('active');
        else btnClassic.classList.remove('active');
    }
    if (btnMantra) {
        if (validMode === 'mantra') btnMantra.classList.add('active');
        else btnMantra.classList.remove('active');
    }

    // Aggiorna tracker budget in alto
    const classicTracker = document.getElementById('classicSlotsTracker');
    const mantraTracker = document.getElementById('mantraSlotsTracker');
    if (classicTracker && mantraTracker) {
        if (validMode === 'mantra') {
            classicTracker.style.display = 'none';
            mantraTracker.style.display = 'flex';
        } else {
            classicTracker.style.display = 'flex';
            mantraTracker.style.display = 'none';
        }
    }

    // Aggiorna intestazione colonna Ruolo
    const thRole = document.getElementById('thRoleHeader');
    if (thRole) {
        thRole.textContent = (validMode === 'mantra') ? 'R. Mantra' : 'R';
        thRole.title = (validMode === 'mantra') ? 'Ruoli Ufficiali Mantra (clicca per ordinare)' : 'Ruolo Classic (P, D, C, A)';
    }

    // Aggiorna opzioni selettore Ruolo nel pannello filtri asta
    if (typeof updateRoleFilterOptionsUI === 'function') {
        updateRoleFilterOptionsUI();
    }

    // Salva preferenza se richiesto
    if (save) {
        saveStateToStorage();
    }

    // Notifica ed aggiorna tutte le viste attive
    onSystemModeChanged();
}

function onSystemModeChanged() {
    if (typeof updateBudgetUI === 'function') updateBudgetUI();
    if (typeof renderTable === 'function') renderTable();
    if (typeof renderSidebarRoster === 'function') renderSidebarRoster();
    if (typeof renderSquadBuilder === 'function' && State.activeTab === 'squad_builder') renderSquadBuilder();
    if (typeof renderAiSquads === 'function' && State.activeTab === 'ai_squads') renderAiSquads();
    if (typeof renderPitchTeam === 'function' && State.activeTab === 'pitch') renderPitchTeam(State.currentTeamPitch);
    if (typeof renderGemsView === 'function' && State.activeTab === 'gems') renderGemsView();
    // Fix: use actual tab IDs ('trade' and 'repair') matching switchTab() in dashboard
    if (typeof renderTradeMachineView === 'function' && State.activeTab === 'trade') renderTradeMachineView();
    if (typeof renderRepairAuctionView === 'function' && State.activeTab === 'repair') renderRepairAuctionView();
    if (typeof initMatchupSelects === 'function' && State.activeTab === 'matchup') initMatchupSelects();
    if (typeof renderLeagueReportView === 'function' && State.activeTab === 'report') renderLeagueReportView();
    if (typeof renderMatchdayAdviceView === 'function' && State.activeTab === 'matchday_advice') renderMatchdayAdviceView();
    if (typeof renderHeaderLeagueDropdown === 'function') renderHeaderLeagueDropdown();
}

function getOvrClass(ovr) {
    const val = Number(ovr) || 0;
    if (val >= 90) return 'ovr-tier-elite';
    if (val >= 85) return 'ovr-tier-top';
    if (val >= 80) return 'ovr-tier-high';
    if (val >= 75) return 'ovr-tier-good';
    if (val >= 70) return 'ovr-tier-mid';
    if (val >= 65) return 'ovr-tier-low';
    return 'ovr-tier-bench';
}

function applyPlayerOverrides() {
    if (typeof PLAYERS === 'undefined' || !Array.isArray(PLAYERS)) return;
    
    PLAYERS.forEach(p => {
        // Salva valori originali una sola volta
        if (p._orig_slot_fascia === undefined) {
            p._orig_slot_fascia = p.slot_fascia || '';
            p._orig_slot_num = p.slot_num || 1;
            p._orig_oop_val = p.oop_val || '-';
            p._orig_is_oop = !!p.is_oop;
            p._orig_fpp_fpn = p.fpp_fpn || 'NONE';
            p._orig_ai_advice = p.ai_advice || p.consiglio || '';
            p._orig_consiglio = p.consiglio || p.ai_advice || '';
            p._orig_ai_advice_type = p.ai_advice_type || 'regular';
        }

        const ovr = State.playerOverrides && State.playerOverrides[p.id];
        if (ovr) {
            if (ovr.slot_fascia !== undefined) {
                p.slot_fascia = ovr.slot_fascia;
                p.slot_num = ovr.slot_num || (parseInt(ovr.slot_fascia) || 1);
            }
            if (ovr.oop_val !== undefined) {
                p.oop_val = ovr.oop_val;
                p.is_oop = ovr.oop_val && ovr.oop_val !== '-';
                p.fpp_fpn = p.is_oop ? 'FPP' : 'NONE';
            }
            if (ovr.ai_advice !== undefined) {
                p.ai_advice = ovr.ai_advice;
                p.consiglio = ovr.ai_advice;
                p.ai_advice_type = ovr.ai_advice_type || 'regular';
            }
            p.is_custom_edited = true;
        } else {
            p.slot_fascia = p._orig_slot_fascia;
            p.slot_num = p._orig_slot_num;
            p.oop_val = p._orig_oop_val;
            p.is_oop = p._orig_is_oop;
            p.fpp_fpn = p._orig_fpp_fpn;
            p.ai_advice = p._orig_ai_advice;
            p.consiglio = p._orig_consiglio;
            p.ai_advice_type = p._orig_ai_advice_type;
            p.is_custom_edited = false;
        }
    });
}

function setPlayerOverride(playerId, overrides) {
    if (!State.playerOverrides) State.playerOverrides = {};
    State.playerOverrides[playerId] = { ...(State.playerOverrides[playerId] || {}), ...overrides };
    applyPlayerOverrides();
    saveStateToStorage();
    updateAllViews();
}

function resetPlayerOverride(playerId) {
    if (State.playerOverrides && State.playerOverrides[playerId]) {
        delete State.playerOverrides[playerId];
        applyPlayerOverrides();
        saveStateToStorage();
        updateAllViews();
    }
}

function resetTeamOverrides(teamName) {
    if (!State.playerOverrides || typeof PLAYERS === 'undefined') return;
    const teamPlayerIds = PLAYERS.filter(p => p.team === teamName).map(p => p.id);
    let changed = false;
    teamPlayerIds.forEach(id => {
        if (State.playerOverrides[id]) {
            delete State.playerOverrides[id];
            changed = true;
        }
    });
    if (changed) {
        applyPlayerOverrides();
        saveStateToStorage();
        updateAllViews();
    }
}

const LEAGUES_STORAGE_KEY = 'FANTA_MASTER_LEAGUES_COLLECTION_2026_27';
const ACTIVE_LEAGUE_ID_KEY = 'FANTA_MASTER_ACTIVE_LEAGUE_ID_2026_27';

const LeaguesManager = {
    getAll() {
        try {
            const raw = localStorage.getItem(LEAGUES_STORAGE_KEY);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    let changed = false;
                    parsed.forEach(l => {
                        if (l.name && (l.name.includes('Amici') || l.name.includes('Ferrovia') || l.name.includes('Lega Principale'))) {
                            l.name = 'La Mia Lega';
                            changed = true;
                        }
                        if (l.myTeamName && (l.myTeamName.includes('Unika') || l.myTeamName.includes('Giuseppe'))) {
                            l.myTeamName = 'La Mia Rosa';
                            changed = true;
                        }
                        if (l.rivals) {
                            const rKeys = Object.keys(l.rivals);
                            const hasPersonalNames = rKeys.some(k => k.includes('Davide') || k.includes('Alessandro') || k.includes('Enrico') || k.includes('Rosario') || k.includes('Michele') || k.includes('Ilario') || k.includes('Valerio') || k.includes('President') || k.includes('Phoenix'));
                            if (hasPersonalNames) {
                                const newR = JSON.parse(JSON.stringify(RIVALS_TEMPLATE));
                                const templateKeys = Object.keys(newR);
                                let idx = 0;
                                rKeys.forEach(oldKey => {
                                    const tKey = templateKeys[idx % templateKeys.length];
                                    if (l.rivals[oldKey] && l.rivals[oldKey].players && l.rivals[oldKey].players.length > 0) {
                                        newR[tKey].players = l.rivals[oldKey].players;
                                        newR[tKey].spent = l.rivals[oldKey].spent;
                                    }
                                    idx++;
                                });
                                l.rivals = newR;
                                changed = true;
                            }
                        }
                    });
                    if (changed) {
                        this.saveAll(parsed);
                    }
                    return parsed;
                }
            }
        } catch (e) {
            console.warn('Errore lettura leghe:', e);
        }
        return [];
    },

    saveAll(leagues) {
        try {
            localStorage.setItem(LEAGUES_STORAGE_KEY, JSON.stringify(leagues));
        } catch (e) {
            console.error('Errore salvataggio leghe:', e);
        }
    },

    getActiveId() {
        return localStorage.getItem(ACTIVE_LEAGUE_ID_KEY) || 'league_default';
    },

    setActiveId(id) {
        localStorage.setItem(ACTIVE_LEAGUE_ID_KEY, id);
    },

    getActive() {
        const leagues = this.getAll();
        const activeId = this.getActiveId();
        return leagues.find(l => l.id === activeId) || leagues[0] || null;
    },

    createLeague(opts = {}) {
        // 1. Salva sempre prima lo stato della lega attualmente attiva!
        this.saveCurrentStateToActiveLeague();

        const leagues = this.getAll();
        const id = 'league_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
        const name = opts.name || `Lega #${leagues.length + 1}`;
        const myTeamName = opts.myTeamName || 'La Mia Rosa';
        const systemMode = opts.systemMode || 'classic';
        const budgetTotal = opts.budgetTotal || 1000;
        const numTeams = opts.numTeams || 8;
        
        const isMantra = (systemMode === 'mantra');
        const slotsP = opts.slotsP || 3;
        const slotsD = opts.slotsD || (isMantra ? 0 : 8);
        const slotsC = opts.slotsC || (isMantra ? 0 : 8);
        const slotsA = opts.slotsA || (isMantra ? 0 : 6);
        const maxRoster = opts.maxRosterSize || (isMantra ? 30 : (slotsP + slotsD + slotsC + slotsA));
        const minRoster = opts.minRosterSize || (isMantra ? 25 : maxRoster);

        let rivals = opts.rivals;
        if (!rivals) {
            const templateKeys = Object.keys(RIVALS_TEMPLATE);
            rivals = {};
            const neededRivals = Math.max(1, numTeams - 1);
            for (let i = 0; i < neededRivals; i++) {
                const k = templateKeys[i] || `Rivale_${i + 1}`;
                const tmpl = RIVALS_TEMPLATE[k] || {
                    name: `Rivale ${i + 1}`,
                    spent: 0,
                    budget: budgetTotal,
                    players: []
                };
                rivals[k] = JSON.parse(JSON.stringify(tmpl));
                rivals[k].budget = budgetTotal;
                rivals[k].spent = 0;
                rivals[k].players = [];
            }
        } else {
            rivals = JSON.parse(JSON.stringify(rivals));
        }

        const rules = {
            systemMode,
            minRosterSize: minRoster,
            maxRosterSize: maxRoster,
            minKeepers: opts.minKeepers || slotsP,
            maxKeepers: opts.maxKeepers || slotsP,
            modificatoreDifesa: opts.modificatoreDifesa !== undefined ? opts.modificatoreDifesa : (systemMode === 'classic'),
            slotsP,
            slotsD,
            slotsC,
            slotsA
        };

        const newLeague = {
            id,
            name,
            myTeamName,
            systemMode,
            budgetTotal,
            budgetSpent: 0,
            numTeams,
            slots: {
                P: { max: slotsP, players: [] },
                D: { max: slotsD, players: [] },
                C: { max: slotsC, players: [] },
                A: { max: slotsA, players: [] }
            },
            rules,
            favorites: [],
            takenByOthers: [],
            rivalAssignments: {},
            rivals,
            playerOverrides: {},
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        leagues.push(newLeague);
        this.saveAll(leagues);
        this.setActiveId(id);
        this.loadLeagueIntoState(newLeague);
        return newLeague;
    },

    switchLeague(leagueId) {
        const leagues = this.getAll();
        const target = leagues.find(l => l.id === leagueId);
        if (!target) return false;
        
        // Salva prima la lega corrente nello storage
        this.saveCurrentStateToActiveLeague();

        // Poi imposta e carica la nuova lega
        this.setActiveId(leagueId);
        this.loadLeagueIntoState(target);

        // Mantieni aggiornato anche STORAGE_KEY per compatibilità
        const toSave = {
            leagueId: State.activeLeagueId,
            leagueName: State.leagueName,
            teamName: State.teamName,
            systemMode: State.systemMode,
            budgetTotal: State.budgetTotal,
            budgetSpent: State.budgetSpent,
            slots: State.slots,
            rules: State.rules,
            favorites: State.favorites,
            takenByOthers: State.takenByOthers,
            rivalAssignments: State.rivalAssignments,
            rivals: State.rivals,
            playerOverrides: State.playerOverrides
        };
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
        } catch(e) {}

        if (typeof updateAllViews === 'function') updateAllViews();
        if (typeof renderHeaderLeagueDropdown === 'function') renderHeaderLeagueDropdown();
        if (State.activeTab === 'home' && typeof renderHomeHubView === 'function') {
            renderHomeHubView();
        }
        return true;
    },

    deleteLeague(leagueId) {
        let leagues = this.getAll();
        if (leagues.length <= 1) {
            alert("Non puoi eliminare l'unica lega presente. Creane prima un'altra.");
            return false;
        }

        leagues = leagues.filter(l => l.id !== leagueId);
        this.saveAll(leagues);

        if (this.getActiveId() === leagueId) {
            this.setActiveId(leagues[0].id);
            this.loadLeagueIntoState(leagues[0]);
        }

        if (typeof updateAllViews === 'function') updateAllViews();
        if (typeof renderHeaderLeagueDropdown === 'function') renderHeaderLeagueDropdown();
        if (typeof renderHomeHubView === 'function') renderHomeHubView();
        return true;
    },

    saveCurrentStateToActiveLeague() {
        const leagues = this.getAll();
        const activeId = this.getActiveId();
        const idx = leagues.findIndex(l => l.id === activeId);
        if (idx === -1) return;

        leagues[idx].name = State.leagueName || leagues[idx].name;
        leagues[idx].myTeamName = State.teamName || leagues[idx].myTeamName;
        leagues[idx].systemMode = State.systemMode || leagues[idx].systemMode;
        leagues[idx].budgetTotal = Number(State.budgetTotal) || leagues[idx].budgetTotal || 1000;
        leagues[idx].budgetSpent = Number(State.budgetSpent) || 0;
        leagues[idx].slots = JSON.parse(JSON.stringify(State.slots || {}));
        leagues[idx].rules = JSON.parse(JSON.stringify(State.rules || leagues[idx].rules || {}));
        leagues[idx].favorites = JSON.parse(JSON.stringify(State.favorites || []));
        leagues[idx].takenByOthers = JSON.parse(JSON.stringify(State.takenByOthers || []));
        leagues[idx].rivalAssignments = JSON.parse(JSON.stringify(State.rivalAssignments || {}));
        leagues[idx].rivals = JSON.parse(JSON.stringify(State.rivals || {}));
        leagues[idx].playerOverrides = JSON.parse(JSON.stringify(State.playerOverrides || {}));
        leagues[idx].updatedAt = new Date().toISOString();

        this.saveAll(leagues);
    },

    loadLeagueIntoState(league) {
        if (!league) return;

        State.activeLeagueId = league.id || 'league_default';
        State.leagueName = (league.name && !league.name.includes('Amici') && !league.name.includes('Ferrovia')) ? league.name : 'La Mia Lega';
        State.teamName = (league.myTeamName && !league.myTeamName.includes('Unika') && !league.myTeamName.includes('Giuseppe')) ? league.myTeamName : 'La Mia Rosa';
        State.systemMode = league.systemMode || 'classic';
        State.budgetTotal = Number(league.budgetTotal) || 1000;
        State.budgetSpent = Number(league.budgetSpent) || 0;

        // Deep clone slots per evitare contaminazioni tra leghe
        if (league.slots) {
            State.slots = JSON.parse(JSON.stringify(league.slots));
        } else {
            const isM = (State.systemMode === 'mantra');
            State.slots = {
                P: { max: 3, players: [] },
                D: { max: isM ? 0 : 8, players: [] },
                C: { max: isM ? 0 : 8, players: [] },
                A: { max: isM ? 0 : 6, players: [] }
            };
        }

        // Deep clone rules
        State.rules = league.rules ? JSON.parse(JSON.stringify(league.rules)) : {
            systemMode: league.systemMode || 'classic',
            minRosterSize: (league.systemMode === 'mantra' ? 25 : 25),
            maxRosterSize: (league.systemMode === 'mantra' ? 30 : 25),
            minKeepers: 3,
            maxKeepers: 3,
            modificatoreDifesa: (league.systemMode === 'classic'),
            slotsP: 3,
            slotsD: 8,
            slotsC: 8,
            slotsA: 6
        };

        // Deep clone favorites, takenByOthers, rivalAssignments, rivals, playerOverrides
        State.favorites = Array.isArray(league.favorites) ? JSON.parse(JSON.stringify(league.favorites)) : [];
        State.takenByOthers = Array.isArray(league.takenByOthers) ? JSON.parse(JSON.stringify(league.takenByOthers)) : [];
        State.rivalAssignments = league.rivalAssignments ? JSON.parse(JSON.stringify(league.rivalAssignments)) : {};
        State.rivals = league.rivals ? JSON.parse(JSON.stringify(league.rivals)) : JSON.parse(JSON.stringify(RIVALS_TEMPLATE));
        State.playerOverrides = league.playerOverrides ? JSON.parse(JSON.stringify(league.playerOverrides)) : {};

        // Reset stati transitori viste specifiche per evitare residui dalla lega precedente
        State.matchupA = null;
        State.matchupB = null;
        if (typeof tradeMachineState !== 'undefined') {
            tradeMachineState.selectedRival = null;
            tradeMachineState.givingPlayerIds = [];
            tradeMachineState.receivingPlayerIds = [];
        }
        if (typeof repairAuctionState !== 'undefined') {
            repairAuctionState.selectedCutIds = [];
        }

        applyPlayerOverrides();
        setSystemMode(league.systemMode || 'classic', false);
    }
};

window.LeaguesManager = LeaguesManager;

function loadStateFromStorage() {
    try {
        let leagues = LeaguesManager.getAll();

        // Auto-migrazione da versione precedente a singolo stato monolitico
        if (!leagues || leagues.length === 0) {
            const oldSaved = localStorage.getItem(STORAGE_KEY);
            let initialLeague;

            if (oldSaved) {
                const parsed = JSON.parse(oldSaved);
                initialLeague = {
                    id: 'league_default',
                    name: 'La Mia Lega',
                    myTeamName: 'La Mia Rosa',
                    systemMode: parsed.systemMode || 'classic',
                    budgetTotal: parsed.budgetTotal || 1000,
                    budgetSpent: parsed.budgetSpent || 0,
                    numTeams: 8,
                    slots: parsed.slots || DefaultState.slots,
                    favorites: parsed.favorites || [],
                    takenByOthers: parsed.takenByOthers || [],
                    rivalAssignments: parsed.rivalAssignments || {},
                    rivals: parsed.rivals || JSON.parse(JSON.stringify(RIVALS_TEMPLATE)),
                    playerOverrides: parsed.playerOverrides || {},
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };
            } else {
                initialLeague = {
                    id: 'league_default',
                    name: 'La Mia Lega',
                    myTeamName: 'La Mia Rosa',
                    systemMode: 'classic',
                    budgetTotal: 1000,
                    budgetSpent: 0,
                    numTeams: 8,
                    slots: DefaultState.slots,
                    favorites: [],
                    takenByOthers: [],
                    rivalAssignments: {},
                    rivals: JSON.parse(JSON.stringify(RIVALS_TEMPLATE)),
                    playerOverrides: {},
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };
            }

            leagues = [initialLeague];
            LeaguesManager.saveAll(leagues);
            LeaguesManager.setActiveId('league_default');
        }

        const active = LeaguesManager.getActive();
        if (active) {
            LeaguesManager.loadLeagueIntoState(active);
            console.log(`-> Lega attiva caricata con successo: "${active.name}" (${active.id}).`);
        }

        if (State.teamName && (State.teamName.includes('Unika') || State.teamName.includes('Giuseppe'))) {
            State.teamName = 'La Mia Rosa';
        }
        if (State.leagueName && (State.leagueName.includes('Amici') || State.leagueName.includes('Ferrovia') || State.leagueName.includes('Lega Principale'))) {
            State.leagueName = 'La Mia Lega';
        }
    } catch (e) {
        console.warn("Errore lettura leghe da localStorage:", e);
    }
}

function saveStateToStorage() {
    try {
        LeaguesManager.saveCurrentStateToActiveLeague();

        // Mantieni aggiornato anche STORAGE_KEY per compatibilità
        const toSave = {
            leagueId: State.activeLeagueId || LeaguesManager.getActiveId(),
            leagueName: State.leagueName,
            teamName: State.teamName,
            systemMode: State.systemMode || 'classic',
            budgetTotal: State.budgetTotal,
            budgetSpent: State.budgetSpent,
            slots: State.slots,
            rules: State.rules,
            favorites: State.favorites,
            takenByOthers: State.takenByOthers,
            rivalAssignments: State.rivalAssignments,
            rivals: State.rivals,
            playerOverrides: State.playerOverrides
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));

        if (typeof broadcastStateUpdate === 'function') {
            broadcastStateUpdate(toSave);
        }
    } catch (e) {
        console.warn("Errore salvataggio localStorage:", e);
    }
}

function isPlayerBought(playerId) {
    return Object.values(State.slots).some(slot => slot.players.some(p => p.id === playerId));
}

function removePlayerById(playerId) {
    for (let r of ['P', 'D', 'C', 'A']) {
        if (!State.slots[r] || !State.slots[r].players) continue;
        const idx = State.slots[r].players.findIndex(p => p.id === playerId);
        if (idx !== -1) {
            const removed = State.slots[r].players.splice(idx, 1)[0];
            if (removed) {
                State.budgetSpent = Math.max(0, State.budgetSpent - (removed.paidPrice || 0));
                saveStateToStorage();
                updateAllViews();
            }
            return removed;
        }
    }
    return null;
}

function isPlayerTakenByOther(playerId) {
    return State.takenByOthers && State.takenByOthers.includes(playerId);
}

function isPlayerAvailable(playerId) {
    return !isPlayerBought(playerId) && !isPlayerTakenByOther(playerId);
}

function isFavorite(playerId) {
    return State.favorites && State.favorites.includes(playerId);
}

function toggleFavorite(playerId) {
    if (!State.favorites) State.favorites = [];
    const idx = State.favorites.indexOf(playerId);
    if (idx === -1) {
        State.favorites.push(playerId);
    } else {
        State.favorites.splice(idx, 1);
    }
    saveStateToStorage();
    updateAllViews();
}

function markPlayerTaken(playerId, rivalName = null, price = null) {
    if (!State.takenByOthers.includes(playerId)) {
        State.takenByOthers.push(playerId);
    }

    if (rivalName && State.rivals[rivalName]) {
        const p = PLAYERS.find(pl => pl.id === playerId);
        const finalPrice = price !== null ? price : (p ? p.prezzo_cons : 1);
        State.rivalAssignments[playerId] = { rival: rivalName, price: finalPrice };
        
        if (!State.rivals[rivalName].players.some(pl => pl.id === playerId)) {
            State.rivals[rivalName].players.push({ id: playerId, price: finalPrice });
            State.rivals[rivalName].spent += finalPrice;
        }
    }

    saveStateToStorage();
    updateAllViews();
}

function unmarkPlayerTaken(playerId) {
    const idx = State.takenByOthers.indexOf(playerId);
    if (idx !== -1) {
        State.takenByOthers.splice(idx, 1);
    }

    if (State.rivalAssignments[playerId]) {
        const assign = State.rivalAssignments[playerId];
        const rName = assign.rival;
        if (State.rivals[rName]) {
            const pIdx = State.rivals[rName].players.findIndex(pl => pl.id === playerId);
            if (pIdx !== -1) {
                State.rivals[rName].spent -= State.rivals[rName].players[pIdx].price;
                State.rivals[rName].players.splice(pIdx, 1);
            }
        }
        delete State.rivalAssignments[playerId];
    }

    saveStateToStorage();
    updateAllViews();
}

function updateAllViews() {
    if (typeof updateBudgetUI === 'function') updateBudgetUI();
    if (typeof renderTable === 'function') renderTable();
    if (typeof renderSidebarRoster === 'function') renderSidebarRoster();
    if (typeof renderSquadBuilder === 'function' && State.activeTab === 'squad_builder') renderSquadBuilder();
    if (typeof renderPitchTeam === 'function' && State.activeTab === 'pitch') renderPitchTeam(State.currentTeamPitch);
    if (typeof renderGemsView === 'function' && State.activeTab === 'gems') renderGemsView();
    if (typeof renderTradeMachineView === 'function' && State.activeTab === 'trade') renderTradeMachineView();
    if (typeof renderRepairAuctionView === 'function' && State.activeTab === 'repair') renderRepairAuctionView();
    if (typeof renderLeagueReportView === 'function' && State.activeTab === 'report') renderLeagueReportView();
    if (typeof renderMatchdayAdviceView === 'function' && State.activeTab === 'matchday_advice') renderMatchdayAdviceView();
    if (typeof renderHeaderLeagueDropdown === 'function') renderHeaderLeagueDropdown();
}

function clearStorageState() {
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (e) {}
}
