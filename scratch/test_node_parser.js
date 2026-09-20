const XLSX = require('../web/js/vendor/xlsx.full.min.js');
const fs = require('fs');

const PLAYERS = JSON.parse(fs.readFileSync('data/processed/processed_players_master.json', 'utf8'));

function cleanStr(s) {
    if (!s) return '';
    return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, ' ').replace(/\s+/g, ' ').trim();
}

function matchPlayerFuzzy(rawName) {
    if (!rawName || !PLAYERS || !PLAYERS.length) return null;
    const cQ = cleanStr(rawName);
    if (!cQ) return null;

    let match = PLAYERS.find(p => cleanStr(p.name) === cQ);
    if (match) return match;

    const qParts = cQ.split(' ').filter(Boolean);
    const surname = qParts[0];

    const surnameCandidates = PLAYERS.filter(p => {
        const cp = cleanStr(p.name);
        return cp === surname || cp.startsWith(surname + ' ') || cp.split(' ').includes(surname);
    });

    if (surnameCandidates.length === 1) {
        return surnameCandidates[0];
    } else if (surnameCandidates.length > 1) {
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

    if (cQ.length >= 4) {
        const subMatch = PLAYERS.find(p => {
            const cp = cleanStr(p.name);
            return cp.includes(cQ) || cQ.includes(cp);
        });
        if (subMatch) return subMatch;
    }

    for (const p of PLAYERS) {
        const parts = cleanStr(p.name).split(' ');
        if (parts.length > 0 && parts[0].length >= 4 && cQ.includes(parts[0])) {
            return p;
        }
    }
    return null;
}

const buf = fs.readFileSync('data/raw/fantarefri-rosters-1789316126497.xlsx');
const wb = XLSX.read(buf, { type: 'buffer' });
const sheet = wb.Sheets[wb.SheetNames[0]];
const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });

const headerRow = rows[0];
const teamCols = [];
for (let c = 0; c < headerRow.length; c++) {
    const val = headerRow[c];
    if (!val) continue;
    const sVal = String(val).trim();
    const cVal = cleanStr(sVal);
    if (!cVal || ['costo', 'prezzo', 'ruolo', 'r', 'cr', 'quotazione', 'totale', 'squadra', 'none', 'null'].includes(cVal)) continue;
    let costCol = -1;
    if (c + 1 < headerRow.length && ['costo', 'prezzo', 'cr'].includes(cleanStr(headerRow[c + 1]))) {
        costCol = c + 1;
    }
    teamCols.push({ teamName: sVal, nameCol: c, costCol });
}

console.log('Detected teams:', teamCols.length);
let total = 0, matched = 0;
teamCols.forEach(tc => {
    let tPlayers = 0, tMatched = 0, spent = 0;
    for (let r = 1; r < rows.length; r++) {
        const pVal = rows[r][tc.nameCol];
        if (!pVal) continue;
        const raw = String(pVal).trim();
        if (['totale', 'total', 'tot', 'crediti', 'budget', 'spesi', 'residui'].includes(cleanStr(raw))) continue;
        const cost = parseInt(String(rows[r][tc.costCol] || 1).replace(/[^0-9]/g, ''), 10) || 1;
        total++;
        tPlayers++;
        spent += cost;
        const m = matchPlayerFuzzy(raw);
        if (m) {
            matched++;
            tMatched++;
        } else {
            console.log('Unmatched:', tc.teamName, raw);
        }
    }
    console.log(`Team: ${tc.teamName} -> ${tMatched}/${tPlayers} matched, ${spent} CR spent`);
});
console.log(`TOTAL: ${matched}/${total} (${(matched/total*100).toFixed(1)}%)`);
