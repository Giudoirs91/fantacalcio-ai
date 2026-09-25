const AnalyticsMatrixState = {
    preset: 'under_over', // 'under_over', 'bonus_engine', 'value_money', 'gk_matrix'
    season: '2627',       // '2627' (Live) o '2526' (Storico)
    roleFilter: 'ALL',    // 'ALL', 'P', 'D', 'C', 'A'
    teamFilter: 'ALL',
    minMinutes: 45,
    searchQuery: '',
    highlightedPlayerId: null,
    isExpanded: false
};
const MATRIX_PRESETS = {
    under_over: {
        title: "Gol Reali vs Expected Goals (Under/Overperformance)",
        sub: "Confronto tra volume di occasioni create (xG) e gol effettivi. Riconosci le scommesse sfortunate pronte a esplodere e i pericoli di bolla.",
        xKey: (p, s) => s === '2627' ? (p.xg_2627 !== null && p.xg_2627 !== undefined ? p.xg_2627 : (p.xg90_2627 ? +(p.xg90_2627 * (p.minuti_2627 || 90) / 90).toFixed(2) : 0)) : +(p.xg_2526 || (p.xg90_2526 ? (p.xg90_2526 * (p.mins_2526 || 900) / 90) : 0)).toFixed(2),
        xLabel: "Expected Goals (xG)",
        yKey: (p, s) => s === '2627' ? (p.gol_2627 || 0) : (p.gf || 0),
        yLabel: "Gol Reali Segnati",
        defaultRoles: ['A', 'C', 'D'],
        qTopLeft: { 
            title: "SOPRAVVALUTATI", 
            badge: "⚠️ Overperformance", 
            sub: "Tanti gol su pochi xG: rischio bolla / da cedere all'apice", 
            color: "#f87171",
            bg: "rgba(239, 68, 68, 0.06)"
        },
        qTopRight: { 
            title: "BOMBER D'ÉLITE", 
            badge: "👑 Top Player", 
            sub: "Altissimo volume offensivo e finalizzazione da fuoriclasse", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.06)"
        },
        qBottomRight: { 
            title: "SCOMMESSE D'ORO", 
            badge: "💎 Underperformance", 
            sub: "Altissimi xG ma 0-1 gol (pali/sfortuna): COMPRA SUBITO!", 
            color: "#4ade80",
            bg: "rgba(34, 197, 94, 0.06)"
        },
        qBottomLeft: { 
            title: "BASSO VOLUME", 
            badge: "🪙 Occasioni Ridotte", 
            sub: "Pochi tiri ed xG bassi: rendimento standard", 
            color: "#94a3b8",
            bg: "rgba(148, 163, 184, 0.03)"
        }
    },
    bonus_engine: {
        title: "Mappa Generazione Bonus (xG/90 vs xA/90)",
        sub: "Produzione offensiva standardizzata su 90 minuti (minaccia al tiro + qualità rifinitura assist) depurata dal minutaggio.",
        xKey: (p, s) => s === '2627' ? +(p.xa90_2627 || 0).toFixed(2) : +(p.xa90_2526 || 0).toFixed(2),
        xLabel: "Expected Assists / 90' (xA/90)",
        yKey: (p, s) => s === '2627' ? +(p.xg90_2627 || 0).toFixed(2) : +(p.xg90_2526 || 0).toFixed(2),
        yLabel: "Expected Goals / 90' (xG/90)",
        defaultRoles: ['A', 'C', 'D'],
        qTopLeft: { 
            title: "FINALIZZATORI PURI", 
            badge: "🎯 Punte d'Area", 
            sub: "Centravanti puri, vivono di gol su azione", 
            color: "#fbbf24",
            bg: "rgba(251, 191, 36, 0.06)"
        },
        qTopRight: { 
            title: "TOTAL BONUS MONSTERS", 
            badge: "🌟 Fuoriclasse Assoluti", 
            sub: "Altissimi sia al tiro che all'assist: i veri crack del fanta", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.06)"
        },
        qBottomRight: { 
            title: "RIFINITORI D'ÉLITE", 
            badge: "🪄 Re degli Assist", 
            sub: "Ali e trequartisti che sfornano grandi occasioni da gol", 
            color: "#c084fc",
            bg: "rgba(192, 132, 252, 0.06)"
        },
        qBottomLeft: { 
            title: "CONTENIMENTO", 
            badge: "⚙️ Lavoro Oscuro", 
            sub: "Mediani e difensori bloccati, rari bonus pesanti", 
            color: "#94a3b8",
            bg: "rgba(148, 163, 184, 0.03)"
        }
    },
    value_money: {
        title: "Rapporto Efficienza / Costo (Minaccia xG+xA vs Quotazione FVM)",
        sub: "Individua chi produce più bonus potenziale per ogni singolo credito speso d'asta (FVM).",
        xKey: (p) => Number(p.fvm || p.qta || 1),
        xLabel: "Fanta Valore di Mercato (FVM in Crediti)",
        yKey: (p, s) => {
            const xg = s === '2627' ? (p.xg90_2627 || 0) : (p.xg90_2526 || 0);
            const xa = s === '2627' ? (p.xa90_2627 || 0) : (p.xa90_2526 || 0);
            return +((xg + xa)).toFixed(2);
        },
        yLabel: "Minaccia Totale (xG/90 + xA/90)",
        defaultRoles: ['A', 'C', 'D'],
        qTopLeft: { 
            title: "VALUE GEMS (Affari)", 
            badge: "🚀 Occasioni d'Oro", 
            sub: "Altissima minaccia a prezzo stracciato: PRENDILI ALL'ASTA!", 
            color: "#4ade80",
            bg: "rgba(34, 197, 94, 0.06)"
        },
        qTopRight: { 
            title: "TOP PLAYER CERTIFICATI", 
            badge: "👑 Investimenti Sicuri", 
            sub: "Produzione altissima che ripaga l'esborso pesante", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.06)"
        },
        qBottomRight: { 
            title: "SOVRAPPREZZATI", 
            badge: "⚠️ Prezzo Eccessivo", 
            sub: "Costo spropositato rispetto alla reale produzione", 
            color: "#f87171",
            bg: "rgba(239, 68, 68, 0.06)"
        },
        qBottomLeft: { 
            title: "LOW COST DI ROTAZIONE", 
            badge: "🎟️ Tappabuchi", 
            sub: "Prezzo minimo per completare la rosa", 
            color: "#94a3b8",
            bg: "rgba(148, 163, 184, 0.03)"
        }
    },
    gk_matrix: {
        title: "Affidabilità Portieri (Gol Evitati vs % Parate)",
        sub: "Isola il rendimento puro tra i pali dei portieri di Serie A, separando i meriti individuali dalla tenuta della difesa.",
        xKey: (p, s) => s === '2627' ? +(p.save_pct_2627 || 0).toFixed(1) : +(p.save_pct_2526 || 0).toFixed(1),
        xLabel: "% Parate Effettuate (Save %)",
        yKey: (p, s) => s === '2627' ? +(p.goals_prevented_2627 || 0).toFixed(2) : +(p.goals_prevented_2526 || 0).toFixed(2),
        yLabel: "Gol Evitati / Salvati (Goals Prevented)",
        defaultRoles: ['P'],
        qTopLeft: { 
            title: "PORTIERI SOTTO ASSEDIO", 
            badge: "🧤 Eroi da Modificatore", 
            sub: "Tanti salvataggi decisivi su difese traballanti (Top MV)", 
            color: "#fbbf24",
            bg: "rgba(251, 191, 36, 0.06)"
        },
        qTopRight: { 
            title: "SARACINESCHE D'ÉLITE", 
            badge: "🛡️ I Migliori in Assoluto", 
            sub: "Top % parate e saldo positivo (Massima sicurezza)", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.06)"
        },
        qBottomRight: { 
            title: "DIFESA BLINDATA", 
            badge: "🔒 Clean Sheet Facili", 
            sub: "Pochi tiri subiti, rendimento affidabile", 
            color: "#4ade80",
            bg: "rgba(34, 197, 94, 0.06)"
        },
        qBottomLeft: { 
            title: "A RISCHIO MALUS", 
            badge: "⚠️ Passivo Pesante", 
            sub: "Poche parate decisive e tanti gol subiti: evitare", 
            color: "#f87171",
            bg: "rgba(239, 68, 68, 0.06)"
        }
    }
};
function initAnalyticsMatrix() {
    renderAnalyticsMatrixView();
}
function setMatrixPreset(presetKey) {
    if (!MATRIX_PRESETS[presetKey]) return;
    AnalyticsMatrixState.preset = presetKey;
    if (presetKey === 'gk_matrix') {
        AnalyticsMatrixState.roleFilter = 'P';
    } else if (AnalyticsMatrixState.roleFilter === 'P') {
        AnalyticsMatrixState.roleFilter = 'ALL';
    }
    renderAnalyticsMatrixView();
}
function setMatrixSeason(seasonKey) {
    AnalyticsMatrixState.season = seasonKey;
    renderAnalyticsMatrixView();
}
function setMatrixRoleFilter(role) {
    AnalyticsMatrixState.roleFilter = role;
    renderAnalyticsMatrixView();
}
function setMatrixTeamFilter(team) {
    AnalyticsMatrixState.teamFilter = team;
    renderAnalyticsMatrixView();
}
function setMatrixMinMinutes(mins) {
    AnalyticsMatrixState.minMinutes = parseInt(mins, 10) || 0;
    renderAnalyticsMatrixView();
}
function setMatrixSearch(query) {
    AnalyticsMatrixState.searchQuery = query.toLowerCase().trim();
    renderAnalyticsMatrixView();
}
function toggleMatrixExpand() {
    AnalyticsMatrixState.isExpanded = !AnalyticsMatrixState.isExpanded;
    renderAnalyticsMatrixView();
}
function formatMatrixPlayerName(fullName) {
    if (!fullName) return '';
    fullName = fullName.trim();
    const parts = fullName.split(/\s+/);
    if (parts.length <= 1) return fullName;
    const last = parts[parts.length - 1];
    if (last.endsWith('.') || last.length <= 2) {
        return fullName;
    }
    const secondLast = parts[parts.length - 2].toLowerCase();
    if (['de', 'di', 'da', 'del', 'della', 'van', 'von', 'le', 'la', 'el', 'al', 'kolo', 'san', 'mc'].includes(secondLast)) {
        return `${parts[parts.length - 2]} ${parts[parts.length - 1]}`;
    }
    return last;
}
function highlightMatrixDot(playerId) {
    AnalyticsMatrixState.highlightedPlayerId = playerId;
    const dots = document.querySelectorAll('.matrix-dot-circle');
    dots.forEach(d => {
        const id = Number(d.getAttribute('data-id'));
        if (id === playerId) {
            d.setAttribute('stroke', '#fbbf24');
            d.setAttribute('stroke-width', '3.5');
            d.classList.add('pulse-dot');
        } else {
            const originalR = d.getAttribute('data-orig-r') || '5.5';
            d.setAttribute('r', originalR);
            d.setAttribute('stroke', d.getAttribute('data-orig-stroke') || 'rgba(255,255,255,0.75)');
            d.setAttribute('stroke-width', d.getAttribute('data-orig-sw') || '1.5');
            d.classList.remove('pulse-dot');
        }
    });
}
function unhighlightMatrixDot() {
    AnalyticsMatrixState.highlightedPlayerId = null;
    const dots = document.querySelectorAll('.matrix-dot-circle');
    dots.forEach(d => {
        const originalR = d.getAttribute('data-orig-r') || '5.5';
        d.setAttribute('r', originalR);
        d.setAttribute('stroke', d.getAttribute('data-orig-stroke') || 'rgba(255,255,255,0.75)');
        d.setAttribute('stroke-width', d.getAttribute('data-orig-sw') || '1.5');
        d.classList.remove('pulse-dot');
    });
}
function computeMatrixInsights(mapped, presetKey, season) {
    if (!mapped || mapped.length === 0) return { under: [], over: [], elite: [], gems: [] };
    if (presetKey === 'under_over') {
        const under = [...mapped]
            .filter(d => (d.y - d.x) <= -0.30 && d.x >= 0.7)
            .sort((a, b) => (a.y - a.x) - (b.y - b.x))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "🔥 SCOMMESSA D'ORO",
                badgeClass: "badge-under",
                statLabel: `${d.player.gol_2627 || 0} Gol su ${d.x.toFixed(2)} xG`,
                deltaLabel: `Δ ${(d.y - d.x).toFixed(2)} xG`,
                advice: `Ha generato ${d.x.toFixed(2)} xG senza raccogliere i meritati gol (pali o sfortuna). I bonus arriveranno: compralo ora prima che il prezzo schizzi!`
            }));
        const over = [...mapped]
            .filter(d => (d.y - d.x) >= 0.9)
            .sort((a, b) => (b.y - b.x) - (a.y - a.x))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "⚠️ RISCHIO BOLLA / DA CEDERE",
                badgeClass: "badge-over",
                statLabel: `${d.y} Gol su soli ${d.x.toFixed(2)} xG`,
                deltaLabel: `+${(d.y - d.x).toFixed(2)} surplus`,
                advice: `Ha segnato ${d.y} gol a fronte di soli ${d.x.toFixed(2)} xG. Rendimento insostenibile nel lungo periodo: è il momento migliore per scambiarlo al valore massimo!`
            }));
        const elite = [...mapped]
            .filter(d => d.x >= 1.2 && d.y >= 2)
            .sort((a, b) => b.y - a.y)
            .slice(0, 3)
            .map(d => ({
                player: d.player,
                badge: "👑 BOMBER CERTEZZA",
                badgeClass: "badge-elite",
                statLabel: `${d.y} Gol (${d.x.toFixed(2)} xG)`,
                deltaLabel: `OVR ${d.player.ovr}`,
                advice: `Volume devastante (${d.x.toFixed(2)} xG) e conversione clinica. Pilastro intoccabile del reparto d'attacco.`
            }));
        return { under, over, elite, gems: [] };
    } 
    if (presetKey === 'bonus_engine') {
        const totalMonsters = [...mapped]
            .filter(d => d.x >= 0.18 && d.y >= 0.30)
            .sort((a, b) => (b.x + b.y) - (a.x + a.y))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "🌟 TOTAL BONUS MONSTER",
                badgeClass: "badge-elite",
                statLabel: `${d.y.toFixed(2)} xG/90 + ${d.x.toFixed(2)} xA/90`,
                deltaLabel: `Tot ${(d.x + d.y).toFixed(2)}/90'`,
                advice: `Coinvolto in tutte le occasioni da gol del club. Tira e serve assist: garanzia matematica di bonus ogni turno.`
            }));
        const playmakers = [...mapped]
            .filter(d => d.x >= 0.22 && d.y < 0.30)
            .sort((a, b) => b.x - a.x)
            .slice(0, 3)
            .map(d => ({
                player: d.player,
                badge: "🪄 RIFINITORE D'ÉLITE",
                badgeClass: "badge-gem",
                statLabel: `${d.x.toFixed(2)} xA/90 (${d.player.assist_2627 || 0} assist)`,
                deltaLabel: `FVM ${d.player.fvm} CR`,
                advice: `Fantasista o esterno dai piedi d'oro. Sforna grandi occasioni da gol ad altissima frequenza.`
            }));
        const pureStrikers = [...mapped]
            .filter(d => d.y >= 0.40 && d.x < 0.15)
            .sort((a, b) => b.y - a.y)
            .slice(0, 3)
            .map(d => ({
                player: d.player,
                badge: "🎯 PUNTA PURA D'AREA",
                badgeClass: "badge-under",
                statLabel: `${d.y.toFixed(2)} xG/90`,
                deltaLabel: `FM ${d.player.fm || '-'}`,
                advice: `Finalizzatore puro. Pochi passaggi chiave ma altissima pericolosità al tiro dentro i sedici metri.`
            }));
        return { elite: totalMonsters, under: playmakers, over: pureStrikers, gems: [] };
    }
    if (presetKey === 'value_money') {
        const gems = [...mapped]
            .filter(d => d.player.fvm <= 28 && d.y >= 0.28)
            .sort((a, b) => (b.y / Math.max(1, b.player.fvm)) - (a.y / Math.max(1, a.player.fvm)))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "🚀 VALUE GEM D'ASTA",
                badgeClass: "badge-gem",
                statLabel: `${d.y.toFixed(2)} Minaccia/90' a ${d.player.fvm} CR`,
                deltaLabel: `Affare Fanta`,
                advice: `Produzione offensiva da semitop pagata a prezzi di saldo. Da prendere all'asta a tutti i costi!`
            }));
        const overpriced = [...mapped]
            .filter(d => d.player.fvm >= 35 && d.y < 0.32)
            .sort((a, b) => (a.y / Math.max(1, a.player.fvm)) - (b.y / Math.max(1, b.player.fvm)))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "⚠️ SOVRASTIMATO / RISCHIO",
                badgeClass: "badge-over",
                statLabel: `FVM ${d.player.fvm} CR per ${d.y.toFixed(2)} Minaccia`,
                deltaLabel: `Bassa Resa`,
                advice: `Quotazione elevata che non corrisponde alla reale minaccia prodotta. Non strapagarlo nelle aste.`
            }));
        return { elite: gems, over: overpriced, under: [], gems: [] };
    }
    const topGk = [...mapped]
        .filter(d => d.y >= 0.4 && d.x >= 70)
        .sort((a, b) => b.y - a.y)
        .slice(0, 3)
        .map(d => ({
            player: d.player,
            badge: "🛡️ SARACINESCA TOP",
            badgeClass: "badge-elite",
            statLabel: `+${d.y.toFixed(2)} Gol Salvati (${d.x}% Parate)`,
            deltaLabel: `MV ${d.player.mv || '-'}`,
            advice: `Portiere superbo: salva gol già fatti e garantisce voti alti costanti per il modificatore di difesa.`
        }));
    const underSiege = [...mapped]
        .filter(d => d.y >= 0.7 && d.x < 70)
        .sort((a, b) => b.y - a.y)
        .slice(0, 3)
        .map(d => ({
            player: d.player,
            badge: "🧤 HERO DA MODIFICATORE",
            badgeClass: "badge-gem",
            statLabel: `+${d.y.toFixed(2)} Gol Evitati`,
            deltaLabel: `FVM ${d.player.fvm} CR`,
            advice: `Subisce molti tiri ma fa parate spettacolari. Ottimo rapporto qualità/prezzo per leghe a modificatore.`
        }));
    return { elite: topGk, under: underSiege, over: [], gems: [] };
}
function renderAnalyticsMatrixView() {
    const container = document.getElementById('viewMatrix');
    if (!container) return;
    const preset = MATRIX_PRESETS[AnalyticsMatrixState.preset];
    const season = AnalyticsMatrixState.season;
    const isExpanded = AnalyticsMatrixState.isExpanded;
    let dataset = PLAYERS.filter(p => {
        if (AnalyticsMatrixState.roleFilter !== 'ALL' && p.role !== AnalyticsMatrixState.roleFilter) return false;
        if (AnalyticsMatrixState.teamFilter !== 'ALL' && p.team !== AnalyticsMatrixState.teamFilter) return false;
        const minutes = season === '2627' ? (p.minuti_2627 || 0) : (p.mins_2526 || 0);
        if (minutes < AnalyticsMatrixState.minMinutes) return false;
        if (AnalyticsMatrixState.searchQuery) {
            const q = AnalyticsMatrixState.searchQuery;
            const matchName = p.name.toLowerCase().includes(q);
            const matchTeam = p.team.toLowerCase().includes(q);
            if (!matchName && !matchTeam) return false;
        }
        return true;
    });
    const allMapped = dataset.map(p => {
        const rawX = Number(preset.xKey(p, season)) || 0;
        const rawY = Number(preset.yKey(p, season)) || 0;
        return { player: p, x: rawX, y: rawY };
    }).filter(d => !isNaN(d.x) && !isNaN(d.y));
    let minX = 0, maxX = 1, minY = 0, maxY = 1;
    if (allMapped.length > 0) {
        minX = Math.min(...allMapped.map(d => d.x));
        maxX = Math.max(...allMapped.map(d => d.x));
        minY = Math.min(...allMapped.map(d => d.y));
        maxY = Math.max(...allMapped.map(d => d.y));
    }
    const marginX = Math.max(0.2, (maxX - minX) * 0.08);
    const marginY = Math.max(0.2, (maxY - minY) * 0.08);
    const plotMinX = Math.max(0, minX - marginX);
    const plotMaxX = Math.max(plotMinX + 0.8, maxX + marginX);
    const plotMinY = Math.min(0, minY - marginY);
    const plotMaxY = Math.max(plotMinY + 0.8, maxY + marginY);
    const midX = (plotMinX + plotMaxX) / 2;
    const midY = (plotMinY + plotMaxY) / 2;
    const isSpecificFilterActive = AnalyticsMatrixState.searchQuery || AnalyticsMatrixState.teamFilter !== 'ALL';
    let mapped = [];
    if (isSpecificFilterActive) {
        mapped = allMapped;
    } else {
        const keyQuadrantsPoints = [];
        const greyQuadrantPoints = [];
        allMapped.forEach(d => {
            const isGrey = (d.x < midX && d.y < midY);
            const isBought = typeof isPlayerBought === 'function' ? isPlayerBought(d.player.id) : false;
            const isFav = typeof isFavorite === 'function' ? isFavorite(d.player.id) : false;
            if (!isGrey || isBought || isFav) {
                keyQuadrantsPoints.push(d);
            } else {
                greyQuadrantPoints.push(d);
            }
        });
        greyQuadrantPoints.sort((a, b) => (b.player.ovr || 0) - (a.player.ovr || 0));
        const cappedGreyPoints = greyQuadrantPoints.slice(0, 30);
        mapped = [...keyQuadrantsPoints, ...cappedGreyPoints];
    }
    const width = isExpanded ? 980 : 760;
    const height = isExpanded ? 580 : 500;
    const padL = 55;
    const padR = 30;
    const padT = 35;
    const padB = 45;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;
    const scaleX = (val) => padL + ((val - plotMinX) / (plotMaxX - plotMinX || 1)) * plotW;
    const scaleY = (val) => padT + plotH - ((val - plotMinY) / (plotMaxY - plotMinY || 1)) * plotH;
    const midScreenX = scaleX(midX);
    const midScreenY = scaleY(midY);
    const coordCounts = {};
    mapped.forEach(d => {
        const key = `${d.x.toFixed(2)}_${d.y.toFixed(2)}`;
        coordCounts[key] = (coordCounts[key] || 0) + 1;
    });
    const seenCoords = {};
    const dotsSvgHtml = mapped.map((d, index) => {
        const key = `${d.x.toFixed(2)}_${d.y.toFixed(2)}`;
        const count = coordCounts[key] || 1;
        const seenIdx = seenCoords[key] || 0;
        seenCoords[key] = seenIdx + 1;
        let offsetX = 0;
        let offsetY = 0;
        if (count > 1) {
            const angle = (seenIdx / count) * 2 * Math.PI;
            const jitterRadius = Math.min(8, count * 1.5);
            offsetX = Math.cos(angle) * jitterRadius;
            offsetY = Math.sin(angle) * jitterRadius;
        }
        const cx = scaleX(d.x) + offsetX;
        const cy = scaleY(d.y) + offsetY;
        const roleColors = { P: '#f59e0b', D: '#10b981', C: '#38bdf8', A: '#f43f5e' };
        const dotColor = roleColors[d.player.role] || '#38bdf8';
        const isBought = typeof isPlayerBought === 'function' ? isPlayerBought(d.player.id) : false;
        const isFav = typeof isFavorite === 'function' ? isFavorite(d.player.id) : false;
        const strokeColor = isBought ? '#4ade80' : (isFav ? '#fbbf24' : 'rgba(255,255,255,0.8)');
        const strokeWidth = isBought || isFav ? 2.5 : 1.2;
        const radius = d.player.ovr >= 88 ? 7 : (d.player.ovr >= 80 ? 5.5 : 4.5);
        const isGreyQuadrant = (d.x < midX && d.y < midY);
        let labelHtml = '';
        if (!isGreyQuadrant) {
            const displayName = formatMatrixPlayerName(d.player.name);
            const textX = cx > (padL + plotW - 80) ? cx - 8 : cx + 8;
            const textY = cy < padT + 20 ? cy + 13 : (index % 2 === 0 ? cy - 5 : cy + 13);
            const anchor = cx > (padL + plotW - 80) ? 'end' : 'start';
            labelHtml = `
                <text x="${textX}" y="${textY}" fill="#ffffff" font-size="10.5" font-weight="900" text-anchor="${anchor}" style="text-shadow: 0 1px 4px #000, 0 0 8px #000, 0 0 12px #000;" pointer-events="none">
                    ${displayName}
                </text>
            `;
        }
        return `
            <g class="matrix-dot-group" onclick="openPlayerProfileModal(${d.player.id})" onmouseenter="highlightMatrixDot(${d.player.id})" onmouseleave="unhighlightMatrixDot()" style="cursor:pointer;">
                <circle class="matrix-dot-circle" data-id="${d.player.id}" data-orig-r="${radius}" data-orig-stroke="${strokeColor}" data-orig-sw="${strokeWidth}" cx="${cx}" cy="${cy}" r="${radius}" fill="${dotColor}" stroke="${strokeColor}" stroke-width="${strokeWidth}" opacity="0.92">
                    <title>${d.player.name} (${d.player.team})&#10;${preset.xLabel}: ${d.x}&#10;${preset.yLabel}: ${d.y}&#10;OVR: ${d.player.ovr} | FVM: ${d.player.fvm} CR&#10;Clicca per aprire la Scheda Giocatore</title>
                </circle>
                ${labelHtml}
            </g>
        `;
    }).join('');
    const insights = computeMatrixInsights(allMapped, AnalyticsMatrixState.preset, season);
    const renderInsightCards = (list, sectionTitle, sectionIcon, sectionColor) => {
        if (!list || list.length === 0) return '';
        const cardsHtml = list.map(item => `
            <div class="fanta-insight-card" onclick="openPlayerProfileModal(${item.player.id})" onmouseenter="highlightMatrixDot(${item.player.id})" onmouseleave="unhighlightMatrixDot()">
                <div class="fanta-insight-top">
                    <div style="display:flex;align-items:center;gap:7px;">
                        <span class="role-badge ${item.player.role}" style="font-size:10px;padding:1px 5px;">${item.player.role}</span>
                        <b style="color:#fff;font-size:13.5px;">${item.player.name}</b>
                        <span style="font-size:11.5px;color:var(--text-muted);">(${item.player.team})</span>
                    </div>
                    <span class="insight-pill ${item.badgeClass}">${item.deltaLabel}</span>
                </div>
                <div class="fanta-insight-stats">
                    <span style="color:var(--accent-cyan);font-weight:700;">📊 ${item.statLabel}</span>
                    <span style="color:var(--text-muted);">•</span>
                    <span>FVM: <b>${item.player.fvm || '-'} CR</b></span>
                    <span style="color:var(--text-muted);">•</span>
                    <span>OVR: <b>${item.player.ovr}</b></span>
                </div>
                <div class="fanta-insight-advice">
                    💡 <b>Consiglio Fanta:</b> ${item.advice}
                </div>
            </div>
        `).join('');
        return `
            <div class="insight-group">
                <div class="insight-group-header" style="border-left: 3px solid ${sectionColor};">
                    <span>${sectionIcon}</span>
                    <span style="color:${sectionColor};font-weight:800;font-size:13px;">${sectionTitle}</span>
                </div>
                ${cardsHtml}
            </div>
        `;
    };
    const teamsList = (typeof TACTICAL_DB !== 'undefined' ? Object.keys(TACTICAL_DB).sort() : []);
    let teamsOptionsHtml = `<option value="ALL">Tutti i 20 Club</option>`;
    teamsList.forEach(t => {
        teamsOptionsHtml += `<option value="${t}" ${AnalyticsMatrixState.teamFilter === t ? 'selected' : ''}>${t}</option>`;
    });
    const presetButtonsHtml = Object.keys(MATRIX_PRESETS).map(key => {
        const pInfo = MATRIX_PRESETS[key];
        const isActive = AnalyticsMatrixState.preset === key;
        const icons = { under_over: '⚖️', bonus_engine: '⚡', value_money: '💎', gk_matrix: '🧤' };
        const shortTitles = {
            under_over: 'Gol vs xG (Sotto/Sopraperformance)',
            bonus_engine: 'xG vs xA (Generatore di Bonus)',
            value_money: 'Minaccia xG+xA vs FVM (Occasioni)',
            gk_matrix: 'Portieri (Gol Evitati vs % Parate)'
        };
        return `
            <button class="matrix-preset-pill ${isActive ? 'active' : ''}" onclick="setMatrixPreset('${key}')">
                <span>${icons[key] || '📊'}</span>
                <span>${shortTitles[key]}</span>
            </button>
        `;
    }).join('');
    const rolesChipsHtml = ['ALL', 'P', 'D', 'C', 'A'].map(r => {
        const isActive = AnalyticsMatrixState.roleFilter === r;
        const labels = { ALL: 'TUTTI', P: '🧤 P', D: '🛡️ D', C: '🪄 C', A: '⚡ A' };
        return `<button class="role-chip ${r} ${isActive ? 'active' : ''}" onclick="setMatrixRoleFilter('${r}')">${labels[r]}</button>`;
    }).join('');
    container.innerHTML = `
        <div class="matrix-view-layout ${isExpanded ? 'is-expanded-layout' : ''}">
            <!-- Header Bar -->
            <div class="matrix-header-bar">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:24px;">📊</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:19px;color:#fff;">Football Analytics & Scatter Matrix</h2>
                        <div style="font-size:12px;color:var(--text-secondary);margin-top:2px;">Metodologia Sportellate / "Numero!" • Statistiche attese incrociate con guida pratica all'Asta & Scambi</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <!-- Bottoncino Espandi / Riduci Schermo -->
                    <button class="btn-expand-matrix" onclick="toggleMatrixExpand()" title="${isExpanded ? 'Torna alla vista affiancata' : 'Ingrandisci il grafico a schermo pieno'}">
                        ${isExpanded ? '⤓ Vista Standard' : '⛶ Estendi Grafico'}
                    </button>
                    <div class="matrix-season-toggle">
                        <button class="matrix-season-btn ${season === '2627' ? 'active' : ''}" onclick="setMatrixSeason('2627')">⚡ Live 2026/27</button>
                        <button class="matrix-season-btn ${season === '2526' ? 'active' : ''}" onclick="setMatrixSeason('2526')">📊 Storico 2025/26</button>
                    </div>
                </div>
            </div>
            <!-- Presets Navigation Strip -->
            <div class="matrix-presets-strip">
                ${presetButtonsHtml}
            </div>
            <!-- Filter Controls Toolbar -->
            <div class="matrix-filter-toolbar">
                <div class="role-chip-group">
                    ${rolesChipsHtml}
                </div>
                <select class="clean-select" style="max-width:145px;font-size:12px;padding:5px 10px;" onchange="setMatrixTeamFilter(this.value)">
                    ${teamsOptionsHtml}
                </select>
                <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);">
                    <span>Minuti:</span>
                    <select class="clean-select" style="padding:5px 8px;font-size:11.5px;" onchange="setMatrixMinMinutes(this.value)">
                        <option value="0" ${AnalyticsMatrixState.minMinutes === 0 ? 'selected' : ''}>Tutti i minuti</option>
                        <option value="45" ${AnalyticsMatrixState.minMinutes === 45 ? 'selected' : ''}>≥ 45'</option>
                        <option value="90" ${AnalyticsMatrixState.minMinutes === 90 ? 'selected' : ''}>≥ 90'</option>
                        <option value="180" ${AnalyticsMatrixState.minMinutes === 180 ? 'selected' : ''}>≥ 180' (Titolari)</option>
                    </select>
                </div>
                <div style="flex:1;min-width:160px;margin-left:auto;">
                    <input type="text" class="clean-input-search" placeholder="🔍 Cerca calciatore o club..." value="${AnalyticsMatrixState.searchQuery}" oninput="setMatrixSearch(this.value)" style="padding:5px 12px;font-size:12px;">
                </div>
                <div style="font-size:11.5px;font-weight:700;color:var(--accent-cyan);padding:5px 10px;background:rgba(0,242,254,0.1);border-radius:6px;white-space:nowrap;">
                    ${mapped.length} Giocatori nel Grafico
                </div>
            </div>
            <!-- WORKSPACE (2-COLUMN OPPURE FULL-WIDTH EXPANDED) -->
            <div class="${isExpanded ? 'matrix-expanded-workspace' : 'matrix-two-column-workspace'}">
                <!-- CHART COLUMN -->
                <div class="matrix-chart-column">
                    <div class="matrix-canvas-card">
                        <!-- Quadrants Top Header Indicator -->
                        <div class="matrix-quadrant-indicators">
                            <div class="quad-badge top-left" style="color:${preset.qTopLeft.color};border-color:${preset.qTopLeft.color}40;background:${preset.qTopLeft.bg};">
                                <b>↖ ${preset.qTopLeft.title}</b>
                                <span>${preset.qTopLeft.sub}</span>
                            </div>
                            <div class="quad-badge top-right" style="color:${preset.qTopRight.color};border-color:${preset.qTopRight.color}40;background:${preset.qTopRight.bg};">
                                <b>↗ ${preset.qTopRight.title}</b>
                                <span>${preset.qTopRight.sub}</span>
                            </div>
                        </div>
                        <svg viewBox="0 0 ${width} ${height}" class="matrix-svg-plot ${isExpanded ? 'svg-expanded' : ''}">
                            <!-- Quadrant Background Tints -->
                            <rect x="${padL}" y="${padT}" width="${midScreenX - padL}" height="${midScreenY - padT}" fill="${preset.qTopLeft.bg}" />
                            <rect x="${midScreenX}" y="${padT}" width="${padL + plotW - midScreenX}" height="${midScreenY - padT}" fill="${preset.qTopRight.bg}" />
                            <rect x="${padL}" y="${midScreenY}" width="${midScreenX - padL}" height="${padT + plotH - midScreenY}" fill="${preset.qBottomLeft.bg}" />
                            <rect x="${midScreenX}" y="${midScreenY}" width="${padL + plotW - midScreenX}" height="${padT + plotH - midScreenY}" fill="${preset.qBottomRight.bg}" />
                            <!-- Main Axes -->
                            <line x1="${padL}" y1="${padT + plotH}" x2="${padL + plotW}" y2="${padT + plotH}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
                            <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${padT + plotH}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
                            <!-- Medians / Crosshair -->
                            <line x1="${midScreenX}" y1="${padT}" x2="${midScreenX}" y2="${padT + plotH}" stroke="rgba(255,255,255,0.15)" stroke-dasharray="4,4" />
                            <line x1="${padL}" y1="${midScreenY}" x2="${padL + plotW}" y2="${midScreenY}" stroke="rgba(255,255,255,0.15)" stroke-dasharray="4,4" />
                            <!-- Diagonal Line (Gol = xG) for Under/Overperformance -->
                            ${AnalyticsMatrixState.preset === 'under_over' ? `
                                <line x1="${scaleX(0)}" y1="${scaleY(0)}" x2="${scaleX(Math.min(plotMaxX, plotMaxY))}" y2="${scaleY(Math.min(plotMaxX, plotMaxY))}" stroke="rgba(251, 191, 36, 0.4)" stroke-dasharray="6,4" stroke-width="1.5" />
                                <text x="${scaleX(Math.min(plotMaxX, plotMaxY) * 0.72)}" y="${scaleY(Math.min(plotMaxX, plotMaxY) * 0.72) - 8}" fill="#fbbf24" font-size="9.5" font-weight="800" opacity="0.85">Linea Equilibrio (Gol = xG)</text>
                            ` : ''}
                            <!-- Axis Labels -->
                            <text x="${padL + plotW / 2}" y="${height - 12}" text-anchor="middle" fill="var(--accent-cyan)" font-size="11.5" font-weight="800">${preset.xLabel} ➔</text>
                            <text x="16" y="${padT + plotH / 2}" text-anchor="middle" fill="var(--accent-cyan)" font-size="11.5" font-weight="800" transform="rotate(-90 16 ${padT + plotH / 2})">➔ ${preset.yLabel}</text>
                            <!-- Axis Min / Mid / Max Ticks -->
                            <text x="${padL}" y="${padT + plotH + 16}" fill="var(--text-muted)" font-size="9.5" text-anchor="middle">${plotMinX.toFixed(1)}</text>
                            <text x="${midScreenX}" y="${padT + plotH + 16}" fill="var(--text-muted)" font-size="9.5" text-anchor="middle">${midX.toFixed(1)}</text>
                            <text x="${padL + plotW}" y="${padT + plotH + 16}" fill="var(--text-muted)" font-size="9.5" text-anchor="middle">${plotMaxX.toFixed(1)}</text>
                            <text x="${padL - 8}" y="${padT + plotH}" fill="var(--text-muted)" font-size="9.5" text-anchor="end">${plotMinY.toFixed(1)}</text>
                            <text x="${padL - 8}" y="${midScreenY}" fill="var(--text-muted)" font-size="9.5" text-anchor="end">${midY.toFixed(1)}</text>
                            <text x="${padL - 8}" y="${padT + 8}" fill="var(--text-muted)" font-size="9.5" text-anchor="end">${plotMaxY.toFixed(1)}</text>
                            <!-- Scatter Dots -->
                            ${dotsSvgHtml}
                        </svg>
                        <!-- Quadrants Bottom Header Indicator -->
                        <div class="matrix-quadrant-indicators">
                            <div class="quad-badge bottom-left" style="color:${preset.qBottomLeft.color};border-color:${preset.qBottomLeft.color}40;background:${preset.qBottomLeft.bg};">
                                <b>↙ ${preset.qBottomLeft.title}</b>
                                <span>${preset.qBottomLeft.sub}</span>
                            </div>
                            <div class="quad-badge bottom-right" style="color:${preset.qBottomRight.color};border-color:${preset.qBottomRight.color}40;background:${preset.qBottomRight.bg};">
                                <b>↘ ${preset.qBottomRight.title}</b>
                                <span>${preset.qBottomRight.sub}</span>
                            </div>
                        </div>
                    </div>
                    <div style="font-size:11.5px;color:var(--text-secondary);display:flex;align-items:center;justify-content:space-between;padding:4px 8px;">
                        <span>💡 Passa il mouse su una card per illuminare il pallino. Clicca per aprire la scheda calciatore.</span>
                        <div style="display:flex;gap:10px;">
                            <span style="color:#f43f5e;font-weight:700;">● Attaccanti</span>
                            <span style="color:#38bdf8;font-weight:700;">● Centrocampisti</span>
                            <span style="color:#10b981;font-weight:700;">● Difensori</span>
                            <span style="color:#f59e0b;font-weight:700;">● Portieri</span>
                        </div>
                    </div>
                </div>
                <!-- EDITORIAL FANTA INSIGHTS & ACTIONABLE RECOMMENDATIONS -->
                <div class="${isExpanded ? 'matrix-expanded-insights-grid' : 'matrix-insights-column'}">
                    <div class="insights-panel-header">
                        <span style="font-size:18px;">🎯</span>
                        <h3 style="margin:0;font-size:15px;color:#fff;font-family:'Outfit',sans-serif;">Verdetti & Consigli Fanta Chiave</h3>
                    </div>
                    <div class="${isExpanded ? 'insights-expanded-cards-container' : 'insights-scrollable-list'}">
                        ${renderInsightCards(insights.under, "Occasioni d'Oro (Sotto la Lente)", "🔥", "#4ade80")}
                        ${renderInsightCards(insights.over, "Rischio Bolla (Cedi all'Apice)", "⚠️", "#f87171")}
                        ${renderInsightCards(insights.elite, "I Fuoriclasse del Grafico", "👑", "#38bdf8")}
                        ${renderInsightCards(insights.gems, "Value Gems a Basso Costo", "🚀", "#c084fc")}
                    </div>
                </div>
            </div>
        </div>
    `;
}