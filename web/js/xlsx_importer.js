// --- xlsx_importer.js ---
// Motore di caricamento e importazione file Excel (.xlsx / .xls) per intera lega
// Supporta formato standard Leghe Fantacalcio a colonne affiancate

let xlsxImportState = {
    fileName: '',
    detectedTeams: {}, // { teamName: [ { rawName, rawRole, rawClub, price, matchedPlayer } ] }
    myTeamKey: '',
    leagueName: 'La Mia Lega',
    targetAction: 'new_league', // 'new_league' | 'update_current'
    expandedTeams: {}
};

function openXlsxImportModal() {
    if (typeof showComingSoonModal === 'function') {
        showComingSoonModal('Importazione Rose da Excel');
        return;
    }
    const modal = document.getElementById('xlsxImportModal');
    if (!modal) return;
    modal.style.display = 'flex';
    modal.classList.add('active');
    renderXlsxImportModalContent();
}

function closeXlsxImportModal() {
    const modal = document.getElementById('xlsxImportModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function handleXlsxFileSelect(event) {
    const file = event.target?.files?.[0];
    if (file) {
        readXlsxFile(file);
    }
}

function handleXlsxDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    const zone = document.getElementById('xlsxDropZone');
    if (zone) zone.classList.add('dragover');
}

function handleXlsxDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    const zone = document.getElementById('xlsxDropZone');
    if (zone) zone.classList.remove('dragover');
    if (event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files.length > 0) {
        const file = event.dataTransfer.files[0];
        readXlsxFile(file);
    }
}

function cleanStr(s) {
    if (!s) return '';
    return String(s)
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

// Algoritmo di fuzzy matching per i calciatori di Serie A
function matchPlayerFuzzy(rawName, rawClub, rawRole) {
    if (!rawName || typeof PLAYERS === 'undefined' || !PLAYERS.length) return null;
    const cQ = cleanStr(rawName);
    if (!cQ) return null;

    // 1. Match esatto nome normalizzato
    let match = PLAYERS.find(p => cleanStr(p.name) === cQ);
    if (match) return match;

    const qParts = cQ.split(' ').filter(Boolean);
    const surname = qParts[0];

    // 2. Candidati per cognome esatto (es. "Svilar", "Vicario", "Skorupski", "Martinez Jo.")
    const surnameCandidates = PLAYERS.filter(p => {
        const cp = cleanStr(p.name);
        return cp === surname || cp.startsWith(surname + ' ') || cp.split(' ').includes(surname);
    });

    if (surnameCandidates.length === 1) {
        return surnameCandidates[0];
    } else if (surnameCandidates.length > 1) {
        // Se è presente una seconda parte / iniziale (es. "Jo." -> 'j', "F." -> 'f', "V." -> 'v')
        if (qParts.length > 1) {
            const secondPart = qParts[1];
            const init = secondPart[0];
            const byInit = surnameCandidates.find(p => {
                const parts = cleanStr(p.name).split(' ');
                return parts.length > 1 && parts[1].startsWith(init);
            });
            if (byInit) return byInit;
        }
        return surnameCandidates[0];
    }

    // 3. Match sottostringa (es. cognomi composti o doppi nomi)
    if (cQ.length >= 4) {
        const subMatch = PLAYERS.find(p => {
            const cp = cleanStr(p.name);
            return cp.includes(cQ) || cQ.includes(cp);
        });
        if (subMatch) return subMatch;
    }

    // 4. Token del master contenuto nella query
    for (const p of PLAYERS) {
        const parts = cleanStr(p.name).split(' ');
        if (parts.length > 0 && parts[0].length >= 4 && cQ.includes(parts[0])) {
            return p;
        }
    }

    return null;
}

function readXlsxFile(file) {
    xlsxImportState.fileName = file.name;
    const baseName = file.name.replace(/\.[^/.]+$/, '').replace(/[_ -]+/g, ' ');
    xlsxImportState.leagueName = `Lega ${baseName}`;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            if (typeof XLSX === 'undefined') {
                alert("Libreria Excel in caricamento... riprova tra un secondo.");
                return;
            }
            const workbook = XLSX.read(data, { type: 'array' });
            processXlsxWorkbook(workbook);
        } catch (err) {
            console.error("Errore lettura file Excel:", err);
            alert("Errore durante la lettura del file Excel: " + err.message);
        }
    };
    reader.readAsArrayBuffer(file);
}

// Caricamento diretto del file reale fantarefri-rosters-1789316126497.xlsx (se presente)
function loadSampleFantarefriRosters() {
    if (typeof SAMPLE_FANTAREFRI_B64 === 'undefined' || !SAMPLE_FANTAREFRI_B64) {
        alert("File di esempio non disponibile. Trascina direttamente il tuo file fantarefri-rosters-1789316126497.xlsx.");
        return;
    }
    try {
        const binaryStr = atob(SAMPLE_FANTAREFRI_B64);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {
            bytes[i] = binaryStr.charCodeAt(i);
        }
        xlsxImportState.fileName = 'rose-lega-esempio.xlsx';
        xlsxImportState.leagueName = 'Lega Serie A';
        const workbook = XLSX.read(bytes, { type: 'array' });
        processXlsxWorkbook(workbook);
    } catch (err) {
        console.error("Errore caricamento sample Excel:", err);
        alert("Errore caricamento sample: " + err.message);
    }
}

// Strategia C: Riconoscimento colonne affiancate (Standard Leghe Fantacalcio)
// Riga 0: [Team1, costo, '', Team2, costo, '', Team3, costo, ...]
function tryParseColumnarTeams(rows) {
    if (!rows || rows.length < 2) return null;
    const headerRow = rows[0];
    const teams = {};
    const teamCols = [];

    for (let c = 0; c < headerRow.length; c++) {
        const val = headerRow[c];
        if (!val) continue;
        const sVal = String(val).trim();
        const cVal = cleanStr(sVal);
        if (!cVal || ['costo', 'prezzo', 'ruolo', 'r', 'cr', 'quotazione', 'totale', 'squadra', 'none', 'null'].includes(cVal)) {
            continue;
        }

        // Cerca colonna costo adiacente
        let costCol = -1;
        if (c + 1 < headerRow.length) {
            const nextHeader = cleanStr(headerRow[c + 1]);
            if (['costo', 'prezzo', 'cr', 'pagato', 'spesa'].includes(nextHeader)) {
                costCol = c + 1;
            }
        }
        if (costCol === -1 && c + 1 < headerRow.length) {
            let numCount = 0;
            for (let r = 1; r < Math.min(6, rows.length); r++) {
                const cell = rows[r] ? rows[r][c + 1] : null;
                if (cell !== undefined && cell !== null && !isNaN(Number(cell))) numCount++;
            }
            if (numCount >= 2) costCol = c + 1;
        }

        teamCols.push({
            teamName: sVal,
            nameCol: c,
            costCol: costCol
        });
    }

    if (teamCols.length < 2) return null; // Devono esserci almeno 2 squadre affiancate

    teamCols.forEach(tc => {
        const playersFound = [];
        for (let r = 1; r < rows.length; r++) {
            const row = rows[r];
            if (!row || tc.nameCol >= row.length) continue;
            const pVal = row[tc.nameCol];
            if (pVal === null || pVal === undefined) continue;
            const rawName = String(pVal).trim();
            if (!rawName || rawName.length < 2) continue;

            const cName = cleanStr(rawName);
            if (['totale', 'total', 'tot', 'crediti', 'budget', 'spesi', 'residui'].includes(cName)) {
                continue; // Riga di riepilogo a fine lista
            }

            let price = 1;
            if (tc.costCol !== -1 && tc.costCol < row.length) {
                const costCell = row[tc.costCol];
                if (costCell !== undefined && costCell !== null) {
                    const parsed = parseInt(String(costCell).replace(/[^0-9]/g, ''), 10);
                    if (!isNaN(parsed) && parsed >= 0) price = parsed;
                }
            }

            const matched = matchPlayerFuzzy(rawName);
            playersFound.push({
                rawName,
                rawRole: matched ? matched.role : '',
                rawClub: matched ? matched.team : '',
                price,
                matchedPlayer: matched
            });
        }

        if (playersFound.length > 0) {
            teams[tc.teamName] = playersFound;
        }
    });

    return Object.keys(teams).length >= 2 ? teams : null;
}

function processXlsxWorkbook(workbook) {
    let teams = {};

    // 1. Prima verifica se uno dei fogli usa il formato standard a colonne affiancate
    for (const sheetName of workbook.SheetNames) {
        const sheet = workbook.Sheets[sheetName];
        const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
        const columnarResult = tryParseColumnarTeams(rows);
        if (columnarResult && Object.keys(columnarResult).length >= 2) {
            teams = columnarResult;
            break;
        }
    }

    // 2. Strategia A: Più fogli, ciascuno intitolato col nome di una squadra
    if (Object.keys(teams).length === 0 && workbook.SheetNames.length > 1 && !workbook.SheetNames.includes('Rose') && !workbook.SheetNames.includes('Foglio1')) {
        workbook.SheetNames.forEach(sheetName => {
            const sheet = workbook.Sheets[sheetName];
            const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
            const parsed = parseSheetRows(rows, sheetName);
            if (parsed.length > 0) {
                teams[sheetName.trim()] = parsed;
            }
        });
    }

    // 3. Strategia B: Singolo foglio con colonna "Squadra"
    if (Object.keys(teams).length === 0) {
        const firstSheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[firstSheetName];
        const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });

        if (rows.length > 0) {
            const headerRow = rows[0].map(c => cleanStr(c));
            let teamColIdx = headerRow.findIndex(c => ['squadra', 'team', 'club', 'proprietario', 'fantasquadra'].includes(c));

            if (teamColIdx !== -1) {
                const teamGroups = {};
                for (let i = 1; i < rows.length; i++) {
                    const row = rows[i];
                    if (!row || row.length === 0) continue;
                    const tName = String(row[teamColIdx] || '').trim();
                    if (!tName) continue;
                    if (!teamGroups[tName]) teamGroups[tName] = [rows[0]];
                    teamGroups[tName].push(row);
                }

                Object.keys(teamGroups).forEach(tName => {
                    const parsed = parseSheetRows(teamGroups[tName], tName);
                    if (parsed.length > 0) {
                        teams[tName] = parsed;
                    }
                });
            } else {
                const parsed = parseSheetRows(rows, 'La Mia Rosa');
                if (parsed.length > 0) {
                    teams['La Mia Rosa'] = parsed;
                }
            }
        }
    }

    if (Object.keys(teams).length === 0) {
        alert("Nessun dato valido trovato nel file Excel. Verifica che contenga calciatori e prezzi.");
        return;
    }

    xlsxImportState.detectedTeams = teams;
    const teamKeys = Object.keys(teams);
    xlsxImportState.myTeamKey = teamKeys[0]; // Predefinita prima squadra
    xlsxImportState.expandedTeams = {};

    renderXlsxImportModalContent();
}

function parseSheetRows(rows, teamName) {
    if (!rows || rows.length < 2) return [];

    const header = rows[0].map(c => cleanStr(c));
    let nameIdx = -1, roleIdx = -1, priceIdx = -1, clubIdx = -1;

    for (let i = 0; i < header.length; i++) {
        const col = header[i];
        if (['calciatore', 'nome', 'player', 'giocatore', 'atleta'].includes(col)) nameIdx = i;
        else if (['ruolo', 'r', 'role', 'pos', 'ruolo classic', 'ruolo mantra'].includes(col) && roleIdx === -1) roleIdx = i;
        else if (['prezzo', 'costo', 'pagato', 'prezzo pagato', 'cr', 'quotazione', 'qta'].includes(col) && priceIdx === -1) priceIdx = i;
        else if (['club', 'squadra reale', 'squadra serie a'].includes(col)) clubIdx = i;
    }

    if (nameIdx === -1) nameIdx = 1;
    if (roleIdx === -1) roleIdx = 0;
    if (priceIdx === -1) priceIdx = 2;

    const playersFound = [];
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || row.length === 0) continue;

        const rawName = String(row[nameIdx] || '').trim().replace(/^"|"$/g, '');
        if (!rawName || rawName.length < 2) continue;

        const rawRole = String(row[roleIdx] || '').trim().toUpperCase();
        let price = 1;
        if (priceIdx !== -1 && row[priceIdx] !== undefined) {
            const parsedPrice = parseInt(String(row[priceIdx]).replace(/[^0-9]/g, ''), 10);
            if (!isNaN(parsedPrice) && parsedPrice >= 0) price = parsedPrice;
        }

        const rawClub = (clubIdx !== -1) ? String(row[clubIdx] || '').trim() : '';

        const matched = matchPlayerFuzzy(rawName, rawClub, rawRole);

        playersFound.push({
            rawName,
            rawRole: matched ? matched.role : rawRole,
            rawClub: matched ? matched.team : rawClub,
            price,
            matchedPlayer: matched
        });
    }

    return playersFound;
}

function setXlsxMyTeam(teamKey) {
    xlsxImportState.myTeamKey = teamKey;
    renderXlsxImportModalContent();
}

function toggleXlsxTeamExpand(teamKey, e) {
    if (e) {
        e.stopPropagation();
    }
    xlsxImportState.expandedTeams[teamKey] = !xlsxImportState.expandedTeams[teamKey];
    renderXlsxImportModalContent();
}

function setXlsxTargetAction(action) {
    xlsxImportState.targetAction = action;
    renderXlsxImportModalContent();
}

// Rendering UI Modale con la domanda chiave: "Quale tra queste è la tua rosa?"
function renderXlsxImportModalContent() {
    const container = document.getElementById('xlsxImportModalContent');
    if (!container) return;

    const teams = xlsxImportState.detectedTeams;
    const teamKeys = Object.keys(teams);

    let previewHtml = '';
    if (teamKeys.length > 0) {
        let totalPlayersAll = 0;
        let totalRecognizedAll = 0;

        const teamCardsHtml = teamKeys.map((tName, idx) => {
            const plist = teams[tName];
            const recognized = plist.filter(p => p.matchedPlayer).length;
            const spent = plist.reduce((s, p) => s + (p.price || 1), 0);
            totalPlayersAll += plist.length;
            totalRecognizedAll += recognized;

            const isMyTeam = (tName === xlsxImportState.myTeamKey);
            const isExpanded = !!xlsxImportState.expandedTeams[tName];

            // Conteggio per ruolo
            const pCount = plist.filter(p => p.matchedPlayer?.role === 'P' || p.rawRole === 'P').length;
            const dCount = plist.filter(p => p.matchedPlayer?.role === 'D' || p.rawRole === 'D').length;
            const cCount = plist.filter(p => p.matchedPlayer?.role === 'C' || p.rawRole === 'C').length;
            const aCount = plist.filter(p => p.matchedPlayer?.role === 'A' || p.rawRole === 'A').length;

            // Media OVR
            const matchedPlayers = plist.filter(p => p.matchedPlayer).map(p => p.matchedPlayer);
            const avgOvr = matchedPlayers.length > 0
                ? (matchedPlayers.reduce((s, p) => s + (p.ovr || 70), 0) / matchedPlayers.length).toFixed(1)
                : '-';

            // Anteprima lista giocatori
            const playersListHtml = isExpanded ? `
                <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.1);max-height:160px;overflow-y:auto;display:flex;flex-direction:column;gap:3px;">
                    ${plist.map(p => `
                        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;padding:2px 4px;border-radius:4px;background:rgba(255,255,255,0.03);">
                            <div style="display:flex;align-items:center;gap:6px;">
                                <span class="slot-pill ${p.matchedPlayer?.role || 'C'}" style="padding:0px 4px;font-size:9px;border-radius:3px;">${p.matchedPlayer?.role || '?'}</span>
                                <span style="color:#fff;font-weight:600;">${p.matchedPlayer ? p.matchedPlayer.name : p.rawName}</span>
                                ${p.matchedPlayer ? `<span style="color:var(--text-muted);font-size:10px;">(${p.matchedPlayer.team})</span>` : '<span style="color:#f87171;font-size:10px;">(non trovato)</span>'}
                            </div>
                            <span style="color:var(--accent-gold);font-weight:700;">${p.price} CR</span>
                        </div>
                    `).join('')}
                </div>
            ` : '';

            return `
                <div class="xlsx-team-card ${isMyTeam ? 'is-my-team' : ''}" onclick="setXlsxMyTeam('${tName}')" style="cursor:pointer;position:relative;border:2px solid ${isMyTeam ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.08)'};background:${isMyTeam ? 'linear-gradient(135deg, rgba(0,242,254,0.14), rgba(18,24,38,0.98))' : 'rgba(255,255,255,0.03)'};border-radius:12px;padding:14px;box-shadow:${isMyTeam ? '0 0 24px rgba(0,242,254,0.3)' : 'none'};transition:all 0.2s ease;">
                    
                    <!-- BADGE STATO SQUADRA -->
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-size:11px;font-weight:900;padding:3px 8px;border-radius:6px;letter-spacing:0.3px;${isMyTeam ? 'background:#00f2fe;color:#031327;' : 'background:rgba(255,255,255,0.08);color:var(--text-muted);'}">
                            ${isMyTeam ? '🌟 QUESTA È LA TUA ROSA ✓' : `👥 AVVERSARIO #${idx + 1}`}
                        </span>

                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="radio" name="xlsxMyTeamRadio" value="${tName}" ${isMyTeam ? 'checked' : ''} style="width:18px;height:18px;accent-color:var(--accent-cyan);cursor:pointer;">
                        </div>
                    </div>

                    <!-- NOME SQUADRA -->
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                        <span style="font-size:22px;">${isMyTeam ? '👑' : '🛡️'}</span>
                        <h4 style="margin:0;font-size:16px;font-weight:900;color:#fff;">${tName}</h4>
                    </div>

                    <!-- METRICHE SQUADRA -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:8px 0;font-size:11.5px;">
                        <div style="background:rgba(0,0,0,0.25);padding:5px 8px;border-radius:6px;">
                            <span style="color:var(--text-muted);">Calciatori:</span>
                            <b style="color:#fff;margin-left:4px;">${plist.length}</b>
                            <span style="color:${recognized === plist.length ? '#34d399' : '#fbbf24'};font-size:10px;">(${recognized}/${plist.length})</span>
                        </div>
                        <div style="background:rgba(0,0,0,0.25);padding:5px 8px;border-radius:6px;">
                            <span style="color:var(--text-muted);">Crediti Spesi:</span>
                            <b style="color:var(--accent-cyan);margin-left:4px;">${spent} CR</b>
                        </div>
                    </div>

                    <!-- REPARTI -->
                    <div style="display:flex;align-items:center;justify-content:space-between;font-size:11px;color:var(--text-secondary);background:rgba(255,255,255,0.02);padding:4px 8px;border-radius:6px;">
                        <span>🧤 P: <b style="color:#fff;">${pCount}</b></span>
                        <span>🛡️ D: <b style="color:#fff;">${dCount}</b></span>
                        <span>🪄 C: <b style="color:#fff;">${cCount}</b></span>
                        <span>⚡ A: <b style="color:#fff;">${aCount}</b></span>
                        <span style="color:var(--accent-gold);font-weight:700;">OVR ${avgOvr}</span>
                    </div>

                    <!-- EXPAND BUTTON -->
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
                        <button type="button" onclick="toggleXlsxTeamExpand('${tName}', event)" style="background:none;border:none;color:var(--accent-cyan);font-size:11px;font-weight:700;cursor:pointer;padding:0;display:flex;align-items:center;gap:4px;">
                            ${isExpanded ? '▲ Nascondi Rosa' : '▼ Visualizza Rosa Completa'}
                        </button>

                        <span style="font-size:10.5px;color:${isMyTeam ? 'var(--accent-cyan)' : 'var(--text-muted)'};">
                            ${isMyTeam ? 'Selezionata' : 'Clicca per selezionare'}
                        </span>
                    </div>

                    ${playersListHtml}
                </div>
            `;
        }).join('');

        const selectedTeam = teams[xlsxImportState.myTeamKey] || [];
        const selectedSpent = selectedTeam.reduce((s, p) => s + (p.price || 1), 0);
        const suggestedBudget = Math.max(1000, Math.ceil((selectedSpent + 20) / 100) * 100);

        previewHtml = `
            <div style="margin-top:18px;">
                <!-- PROMINENT QUESTION BANNER -->
                <div style="display:flex;align-items:center;gap:14px;background:linear-gradient(135deg, rgba(0,242,254,0.18), rgba(2,132,199,0.3));border:2px solid var(--accent-cyan);border-radius:14px;padding:16px 20px;box-shadow:0 0 25px rgba(0,242,254,0.2);margin-bottom:18px;">
                    <span style="font-size:36px;">🎯</span>
                    <div style="flex:1;">
                        <h3 style="margin:0;font-size:19px;font-weight:900;color:#fff;letter-spacing:0.3px;">
                            Quale tra queste è la tua rosa?
                        </h3>
                        <div style="font-size:12.5px;color:#cbd5e1;margin-top:4px;">
                            Abbiamo rilevato <b>${teamKeys.length} squadre complete</b> (${totalRecognizedAll}/${totalPlayersAll} calciatori di Serie A abbinati al 100%). Clicca sulla scheda della tua squadra: tutte le altre verranno assegnate come avversari!
                        </div>
                    </div>
                    <div style="background:rgba(0,242,254,0.15);border:1px solid var(--accent-cyan);padding:8px 14px;border-radius:10px;text-align:center;">
                        <div style="font-size:11px;color:var(--accent-cyan);font-weight:800;text-transform:uppercase;">Rosa Selezionata</div>
                        <div style="font-size:15px;font-weight:900;color:#fff;margin-top:2px;">🌟 ${xlsxImportState.myTeamKey}</div>
                    </div>
                </div>

                <!-- SELECTION GRID -->
                <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(310px, 1fr));gap:14px;max-height:420px;overflow-y:auto;padding-right:6px;">
                    ${teamCardsHtml}
                </div>

                <!-- CONFIGURAZIONE CAMPIONATO -->
                <div style="margin-top:18px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);padding:16px;border-radius:12px;">
                    <div style="font-size:12px;font-weight:800;color:var(--accent-cyan);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">
                        ⚙️ Configurazione Campionato da Creare
                    </div>

                    <div style="display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:14px;align-items:flex-end;">
                        <div>
                            <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Nome della Lega / Campionato</label>
                            <input type="text" id="xlsxNewLeagueName" value="${xlsxImportState.leagueName}" style="width:100%;box-sizing:border-box;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px 12px;font-size:13px;">
                        </div>

                        <div>
                            <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Budget Iniziale</label>
                            <select id="xlsxBudgetSelect" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px;font-size:13px;">
                                <option value="1000" ${suggestedBudget <= 1000 ? 'selected' : ''}>1000 Crediti</option>
                                <option value="2000" ${suggestedBudget > 1000 ? 'selected' : ''}>2000 Crediti</option>
                                <option value="500">500 Crediti</option>
                                <option value="600">600 Crediti</option>
                                <option value="800">800 Crediti</option>
                            </select>
                        </div>

                        <div>
                            <label style="display:block;font-size:11px;color:var(--text-muted);font-weight:700;margin-bottom:4px;text-transform:uppercase;">Modalità</label>
                            <select id="xlsxModeSelect" style="width:100%;background:rgba(10,14,23,0.9);border:1px solid rgba(255,255,255,0.15);color:#fff;border-radius:8px;padding:9px;font-size:13px;">
                                <option value="classic">⚡ Classic</option>
                                <option value="mantra">🔮 Mantra</option>
                            </select>
                        </div>
                    </div>

                    <div style="display:flex;gap:20px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">
                        <label style="display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:#fff;cursor:pointer;">
                            <input type="radio" name="xlsxTargetAction" value="new_league" ${xlsxImportState.targetAction === 'new_league' ? 'checked' : ''} onchange="setXlsxTargetAction('new_league')">
                            <span><b>Crea Nuovo Campionato Indipendente</b> (consigliato: ogni lega è un mondo a sé)</span>
                        </label>
                        <label style="display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:var(--text-secondary);cursor:pointer;">
                            <input type="radio" name="xlsxTargetAction" value="update_current" ${xlsxImportState.targetAction === 'update_current' ? 'checked' : ''} onchange="setXlsxTargetAction('update_current')">
                            <span>Sovrascrivi Campionato Attivo</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        <!-- HEADER -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:28px;">📥</span>
                <div>
                    <h3 class="font-title" style="color:var(--accent-cyan);font-size:19px;margin:0;">Importatore Rose da Excel (.xlsx / .xls)</h3>
                    <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">
                        Carica il file Excel delle rose (formato Leghe Fantacalcio o personalizzato). Ti verrà chiesto quale sia la tua squadra tra tutte quelle presenti.
                    </div>
                </div>
            </div>
            <button class="btn-action" style="padding:4px 10px;font-size:12px;" onclick="closeXlsxImportModal()">Chiudi ✕</button>
        </div>

        <!-- DROP ZONE -->
        <div class="csv-drop-zone" id="xlsxDropZone" ondragover="handleXlsxDragOver(event)" ondrop="handleXlsxDrop(event)" onclick="document.getElementById('xlsxFileInput').click()" style="background:rgba(15,23,42,0.6);border:2px dashed rgba(0,242,254,0.3);border-radius:14px;padding:20px;text-align:center;cursor:pointer;transition:all 0.2s ease;">
            <div style="font-size:32px;margin-bottom:6px;">📊</div>
            <div style="font-size:14px;font-weight:700;color:var(--accent-cyan);">
                ${xlsxImportState.fileName ? `File caricato: <b>${xlsxImportState.fileName}</b>` : 'Trascina qui il file Excel (.xlsx o .xls) oppure clicca per selezionarlo'}
            </div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">
                Supporta il formato a colonne Leghe Fantacalcio, fogli singoli o cartelle con fogli separati per squadra
            </div>
            <input type="file" id="xlsxFileInput" accept=".xlsx, .xls, .csv" style="display:none;" onchange="handleXlsxFileSelect(event)">
        </div>

        <!-- QUICK BUTTON PER FILE REALE DI PROVA -->
        <div style="display:flex;justify-content:center;margin-top:10px;">
            <button type="button" class="btn-action" onclick="loadSampleFantarefriRosters()" style="background:rgba(0,242,254,0.1);border:1px solid rgba(0,242,254,0.4);color:var(--accent-cyan);font-weight:800;font-size:12px;padding:7px 16px;border-radius:8px;display:flex;align-items:center;gap:7px;cursor:pointer;transition:all 0.2s ease;">
                <span style="font-size:15px;">⚡</span> Carica file di esempio: <b>rose-lega-esempio.xlsx (10 Squadre)</b>
            </button>
        </div>

        <!-- PREVIEW & SELECTION -->
        ${previewHtml}

        <!-- FOOTER ACTIONS -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;border-top:1px solid rgba(255,255,255,0.08);padding-top:12px;">
            <button class="btn-action" style="padding:8px 16px;font-size:12px;" onclick="closeXlsxImportModal()">Annulla</button>
            <button class="btn-action" style="background:linear-gradient(135deg, #10b981, #059669);color:#fff;font-weight:900;padding:10px 24px;font-size:13.5px;border:none;border-radius:8px;box-shadow:0 4px 15px rgba(16,185,129,0.35);${teamKeys.length === 0 ? 'opacity:0.4;cursor:not-allowed;' : 'cursor:pointer;'}" ${teamKeys.length === 0 ? 'disabled' : ''} onclick="confirmApplyXlsxLeague()">
                ✓ Conferma e Importa Campionato (${teamKeys.length} Squadre)
            </button>
        </div>
    `;
}

function confirmApplyXlsxLeague() {
    const teams = xlsxImportState.detectedTeams;
    const teamKeys = Object.keys(teams);
    if (teamKeys.length === 0) return;

    const myTeamKey = xlsxImportState.myTeamKey || teamKeys[0];
    const isNewLeague = (xlsxImportState.targetAction === 'new_league');
    const leagueNameInput = document.getElementById('xlsxNewLeagueName')?.value.trim();
    const finalLeagueName = leagueNameInput || xlsxImportState.leagueName || 'Nuova Lega Excel';

    const budgetVal = parseInt(document.getElementById('xlsxBudgetSelect')?.value, 10) || 1000;
    const modeVal = document.getElementById('xlsxModeSelect')?.value || 'classic';

    // 1. Prepara i dati di tutti i rivali
    const rivalsObj = {};
    teamKeys.forEach(tName => {
        if (tName !== myTeamKey) {
            rivalsObj[tName] = {
                manager: tName,
                tendency: 'Importato da Excel',
                budget: budgetVal,
                spent: 0,
                players: []
            };
        }
    });

    if (isNewLeague) {
        // Crea nuova lega completamente isolata
        LeaguesManager.createLeague({
            name: finalLeagueName,
            myTeamName: myTeamKey,
            systemMode: modeVal,
            budgetTotal: budgetVal,
            numTeams: teamKeys.length,
            rivals: rivalsObj
        });
    } else {
        // Aggiorna la lega attiva
        State.teamName = myTeamKey;
        State.rivals = rivalsObj;
        State.systemMode = modeVal;
        State.budgetTotal = budgetVal;
        State.slots.P.players = [];
        State.slots.D.players = [];
        State.slots.C.players = [];
        State.slots.A.players = [];
        State.budgetSpent = 0;
        State.takenByOthers = [];
        State.rivalAssignments = {};
    }

    // 2. Popola la rosa del giocatore (myTeamKey)
    const myPlayers = teams[myTeamKey] || [];
    myPlayers.forEach(item => {
        if (!item.matchedPlayer) return;
        const p = item.matchedPlayer;
        const price = Math.max(1, item.price || 1);
        const slotKey = (p.role === 'P' || (p.mantra && String(p.mantra).toUpperCase().includes('POR'))) ? 'P' : (State.slots[p.role] ? p.role : 'C');
        State.slots[slotKey].players.push({ ...p, paidPrice: price });
        State.budgetSpent += price;
    });

    // 3. Popola i calciatori acquistati dagli avversari (Rivali)
    teamKeys.forEach(tName => {
        if (tName === myTeamKey) return;
        const rPlayers = teams[tName] || [];
        rPlayers.forEach(item => {
            if (!item.matchedPlayer) return;
            const p = item.matchedPlayer;
            const price = Math.max(1, item.price || 1);
            markPlayerTaken(p.id, tName, price);
        });
    });

    // 4. Salva e sincronizza tutto lo stato
    saveStateToStorage();
    updateAllViews();
    renderHeaderLeagueDropdown();
    closeXlsxImportModal();

    switchTab('auction');

    const toastMsg = `🏆 Campionato "${finalLeagueName}" importato con successo!\n🌟 La tua rosa è: ${myTeamKey} (${myPlayers.length} calciatori)\n👥 ${teamKeys.length - 1} Squadre rivali configurate con tutte le rose!`;
    if (typeof showSyncToast === 'function') {
        showSyncToast(toastMsg);
    } else {
        alert(toastMsg);
    }
}

window.openXlsxImportModal = openXlsxImportModal;
window.closeXlsxImportModal = closeXlsxImportModal;
window.handleXlsxFileSelect = handleXlsxFileSelect;
window.handleXlsxDragOver = handleXlsxDragOver;
window.handleXlsxDrop = handleXlsxDrop;
window.setXlsxMyTeam = setXlsxMyTeam;
window.toggleXlsxTeamExpand = toggleXlsxTeamExpand;
window.setXlsxTargetAction = setXlsxTargetAction;
window.confirmApplyXlsxLeague = confirmApplyXlsxLeague;
window.loadSampleFantarefriRosters = loadSampleFantarefriRosters;
