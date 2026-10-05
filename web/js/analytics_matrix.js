// ==============================================================================
// MODULO ADVANCED FOOTBALL ANALYTICS & SCATTER PLOT A 4 QUADRANTI
// METODOLOGIA ISPIRATA A SPORTELLATE / "NUMERO!" (NICOLA SANTOLINI)
// ==============================================================================

const AnalyticsMatrixState = {
    preset: 'under_over',      // 'under_over', 'bonus_engine', 'value_money', 'gk_matrix'
    season: '2627',            // '2627' (Live) o '2526' (Storico)
    roleFilter: 'ALL',         // 'ALL', 'P', 'D', 'C', 'A'
    teamFilter: 'ALL',
    minMinutes: 45,
    searchQuery: '',
    highlightedPlayerId: null,
    isExpanded: false,
    quadrantFilter: 'ALL'      // 'ALL', 'top_left', 'top_right', 'bottom_right', 'bottom_left'
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
            key: "top_left",
            title: "SOPRAVVALUTATI", 
            badge: "⚠️ Overperformance", 
            sub: "Tanti gol su pochi xG: rischio bolla / da cedere all'apice", 
            color: "#f87171",
            bg: "rgba(239, 68, 68, 0.08)"
        },
        qTopRight: { 
            key: "top_right",
            title: "BOMBER D'ÉLITE", 
            badge: "👑 Top Player", 
            sub: "Altissimo volume offensivo e finalizzazione da fuoriclasse", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.08)"
        },
        qBottomRight: { 
            key: "bottom_right",
            title: "SCOMMESSE D'ORO", 
            badge: "💎 Underperformance", 
            sub: "Altissimi xG ma 0-1 gol (pali/sfortuna): COMPRA SUBITO!", 
            color: "#4ade80",
            bg: "rgba(34, 197, 94, 0.08)"
        },
        qBottomLeft: { 
            key: "bottom_left",
            title: "BASSO VOLUME", 
            badge: "🪙 Occasioni Ridotte", 
            sub: "Pochi tiri ed xG bassi: rendimento standard", 
            color: "#94a3b8",
            bg: "rgba(148, 163, 184, 0.04)"
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
            key: "top_left",
            title: "FINALIZZATORI PURI", 
            badge: "🎯 Punte d'Area", 
            sub: "Centravanti puri, vivono di gol su azione", 
            color: "#fbbf24",
            bg: "rgba(251, 191, 36, 0.08)"
        },
        qTopRight: { 
            key: "top_right",
            title: "TOTAL BONUS MONSTERS", 
            badge: "🌟 Fuoriclasse Assoluti", 
            sub: "Altissimi sia al tiro che all'assist: i veri crack del fanta", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.08)"
        },
        qBottomRight: { 
            key: "bottom_right",
            title: "RIFINITORI D'ÉLITE", 
            badge: "🪄 Re degli Assist", 
            sub: "Ali e trequartisti che sfornano grandi occasioni da gol", 
            color: "#c084fc",
            bg: "rgba(192, 132, 252, 0.08)"
        },
        qBottomLeft: { 
            key: "bottom_left",
            title: "CONTENIMENTO", 
            badge: "⚙️ Lavoro Oscuro", 
            sub: "Mediani e difensori bloccati, rari bonus pesanti", 
            color: "#94a3b8",
            bg: "rgba(148, 163, 184, 0.04)"
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
            key: "top_left",
            title: "VALUE GEMS (Affari)", 
            badge: "🚀 Occasioni d'Oro", 
            sub: "Altissima minaccia a prezzo stracciato: PRENDILI ALL'ASTA!", 
            color: "#4ade80",
            bg: "rgba(34, 197, 94, 0.08)"
        },
        qTopRight: { 
            key: "top_right",
            title: "TOP PLAYER CERTIFICATI", 
            badge: "👑 Investimenti Sicuri", 
            sub: "Produzione altissima che ripaga l'esborso pesante", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.08)"
        },
        qBottomRight: { 
            key: "bottom_right",
            title: "SOVRAPPREZZATI", 
            badge: "⚠️ Prezzo Eccessivo", 
            sub: "Costo spropositato rispetto alla reale produzione", 
            color: "#f87171",
            bg: "rgba(239, 68, 68, 0.08)"
        },
        qBottomLeft: { 
            key: "bottom_left",
            title: "LOW COST DI ROTAZIONE", 
            badge: "🎟️ Tappabuchi", 
            sub: "Prezzo minimo per completare la rosa", 
            color: "#94a3b8",
            bg: "rgba(148, 163, 184, 0.04)"
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
            key: "top_left",
            title: "PORTIERI SOTTO ASSEDIO", 
            badge: "🧤 Eroi da Modificatore", 
            sub: "Tanti salvataggi decisivi su difese traballanti (Top MV)", 
            color: "#fbbf24",
            bg: "rgba(251, 191, 36, 0.08)"
        },
        qTopRight: { 
            key: "top_right",
            title: "SARACINESCHE D'ÉLITE", 
            badge: "🛡️ I Migliori in Assoluto", 
            sub: "Top % parate e saldo positivo (Massima sicurezza)", 
            color: "#38bdf8",
            bg: "rgba(56, 189, 248, 0.08)"
        },
        qBottomRight: { 
            key: "bottom_right",
            title: "DIFESA BLINDATA", 
            badge: "🔒 Clean Sheet Facili", 
            sub: "Pochi tiri subiti, rendimento affidabile", 
            color: "#4ade80",
            bg: "rgba(34, 197, 94, 0.08)"
        },
        qBottomLeft: { 
            key: "bottom_left",
            title: "A RISCHIO MALUS", 
            badge: "⚠️ Passivo Pesante", 
            sub: "Poche parate decisive e tanti gol subiti: evitare", 
            color: "#f87171",
            bg: "rgba(239, 68, 68, 0.08)"
        }
    }
};

function initAnalyticsMatrix() {
    renderAnalyticsMatrixView();
}

function setMatrixPreset(presetKey) {
    if (!MATRIX_PRESETS[presetKey]) return;
    AnalyticsMatrixState.preset = presetKey;
    AnalyticsMatrixState.quadrantFilter = 'ALL';
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

function setMatrixQuadrantFilter(qKey) {
    if (AnalyticsMatrixState.quadrantFilter === qKey) {
        AnalyticsMatrixState.quadrantFilter = 'ALL';
    } else {
        AnalyticsMatrixState.quadrantFilter = qKey;
    }
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
            d.setAttribute('stroke-width', '4');
            d.classList.add('pulse-dot');
            const g = d.closest('.matrix-dot-group');
            if (g && g.parentNode) g.parentNode.appendChild(g); // Portalo in primo piano
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

// Floating Tooltip Handlers
function showMatrixTooltip(e, id, name, team, role, xVal, yVal, ovr, fvm, deltaLabel, advice) {
    let tooltip = document.getElementById('matrixTooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'matrixTooltip';
        tooltip.className = 'matrix-floating-tooltip';
        document.body.appendChild(tooltip);
    }
    const preset = MATRIX_PRESETS[AnalyticsMatrixState.preset];
    const roleColors = { P: '#f59e0b', D: '#10b981', C: '#38bdf8', A: '#f43f5e' };
    const rColor = roleColors[role] || '#38bdf8';
    
    tooltip.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:6px;">
            <div style="display:flex;align-items:center;gap:6px;">
                <span class="role-badge ${role}" style="font-size:9.5px;padding:1px 5px;background:${rColor}25;color:${rColor};border:1px solid ${rColor}50;">${role}</span>
                <b style="color:#fff;font-size:13.5px;">${name}</b>
                <span style="font-size:11px;color:#94a3b8;">(${team})</span>
            </div>
            <span style="font-size:10px;font-weight:800;color:#94a3b8;background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:4px;">OVR ${ovr || '-'}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11.5px;color:#cbd5e1;margin-top:2px;">
            <span>${preset.xLabel}: <b style="color:#fff;">${xVal}</b></span>
            <span>${preset.yLabel}: <b style="color:#fff;">${yVal}</b></span>
        </div>
        ${deltaLabel ? `<div style="font-size:11px;font-weight:700;color:${deltaLabel.includes('+') ? '#f87171' : '#4ade80'};">${deltaLabel}</div>` : ''}
        ${advice ? `<div style="font-size:11px;color:#cbd5e1;line-height:1.35;background:rgba(0,0,0,0.3);padding:5px 8px;border-radius:6px;border-left:2px solid #fbbf24;">💡 ${advice}</div>` : ''}
        <div style="font-size:9.5px;color:#64748b;text-align:right;margin-top:2px;">Clicca per scheda giocatore ➔</div>
    `;
    tooltip.style.display = 'flex';
    moveMatrixTooltip(e);
}

function moveMatrixTooltip(e) {
    const tooltip = document.getElementById('matrixTooltip');
    if (!tooltip) return;
    const x = e.clientX + 16;
    const y = e.clientY - 20;
    const maxX = window.innerWidth - 320;
    if (x > maxX) {
        tooltip.style.left = (e.clientX - 290) + 'px';
    } else {
        tooltip.style.left = x + 'px';
    }
    tooltip.style.top = Math.max(10, Math.min(window.innerHeight - 180, y)) + 'px';
}

function hideMatrixTooltip() {
    const tooltip = document.getElementById('matrixTooltip');
    if (tooltip) tooltip.style.display = 'none';
}

// Generatore di Consigli Fanta Intelligenti e Realistici
function getTailoredUnderAdvice(p, xg, gol) {
    const diff = (xg - gol).toFixed(2);
    if (p.role === 'A') {
        if (gol === 0) {
            return `Ha collezionato ben ${xg.toFixed(2)} xG senza sbloccarsi: pali, parate o sfortuna. La matematica predice gol a brevissimo: compralo ora prima che esploda!`;
        }
        return `Volume offensivo devastante (${xg.toFixed(2)} xG) con soli ${gol} gol. I bonus pesanti sono solo questione di tempo: giocatore da blindare assolutamente.`;
    } else if (p.role === 'C') {
        return `Centrocampista con inserimenti continui nell'area rivale (${xg.toFixed(2)} xG). Con questi numeri è destinato a scalare le gerarchie e portare gol a raffica.`;
    } else {
        return `Difensore pericolosissimo sui calci piazzati (${xg.toFixed(2)} xG). Il bonus pesante di testa è imminente, ottima pedina da modificatore.`;
    }
}

function getTailoredOverAdvice(p, xg, gol) {
    const diff = (gol - xg).toFixed(2);
    if (gol >= 3 && xg < 1.0) {
        return `Ha segnato ${gol} gol con soli ${xg.toFixed(2)} xG (conversione oltre il 300%). Rendimento statisticamente insostenibile a lungo termine: scambialo adesso all'apice dell'hype!`;
    }
    return `Rendimento sopra le righe (+${diff} gol oltre l'atteso). Ottimo momento di forma, ma è la finestra ideale per massimizzare il suo valore sul mercato degli scambi.`;
}

function getTailoredEliteAdvice(p, xg, gol) {
    return `Pilastro offensivo assoluto: abbina un volume di tiri spaventoso (${xg.toFixed(2)} xG) a una conversione chirurgica (${gol} gol). È un fuoriclasse intoccabile.`;
}

// Calcolo Fanta Insights & Decisioni Operative
function computeMatrixInsights(mapped, presetKey, season) {
    if (!mapped || mapped.length === 0) return { under: [], over: [], elite: [], gems: [] };

    if (presetKey === 'under_over') {
        const under = [...mapped]
            .filter(d => (d.y - d.x) <= -0.25 && d.x >= 0.7)
            .sort((a, b) => (a.y - a.x) - (b.y - b.x))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "🔥 SCOMMESSA D'ORO",
                badgeClass: "badge-under",
                statLabel: `${d.player.gol_2627 || 0} Gol su ${d.x.toFixed(2)} xG`,
                deltaLabel: `Δ ${(d.y - d.x).toFixed(2)} xG`,
                advice: getTailoredUnderAdvice(d.player, d.x, d.y)
            }));

        const over = [...mapped]
            .filter(d => (d.y - d.x) >= 0.85)
            .sort((a, b) => (b.y - b.x) - (a.y - a.x))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "⚠️ RISCHIO BOLLA / DA CEDERE",
                badgeClass: "badge-over",
                statLabel: `${d.y} Gol su soli ${d.x.toFixed(2)} xG`,
                deltaLabel: `+${(d.y - d.x).toFixed(2)} surplus`,
                advice: getTailoredOverAdvice(d.player, d.x, d.y)
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
                advice: getTailoredEliteAdvice(d.player, d.x, d.y)
            }));

        return { under, over, elite, gems: [] };
    } 
    
    if (presetKey === 'bonus_engine') {
        const totalMonsters = [...mapped]
            .filter(d => d.x >= 0.18 && d.y >= 0.28)
            .sort((a, b) => (b.x + b.y) - (a.x + a.y))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "🌟 TOTAL BONUS MONSTER",
                badgeClass: "badge-elite",
                statLabel: `${d.y.toFixed(2)} xG/90 + ${d.x.toFixed(2)} xA/90`,
                deltaLabel: `Tot ${(d.x + d.y).toFixed(2)}/90'`,
                advice: `Partecipazione attiva a ogni manovra da gol. Conclude in porta e sforna assist: garanzia matematica di bonus costanti.`
            }));

        const playmakers = [...mapped]
            .filter(d => d.x >= 0.22 && d.y < 0.28)
            .sort((a, b) => b.x - a.x)
            .slice(0, 3)
            .map(d => ({
                player: d.player,
                badge: "🪄 RIFINITORE D'ÉLITE",
                badgeClass: "badge-gem",
                statLabel: `${d.x.toFixed(2)} xA/90 (${d.player.assist_2627 || 0} assist)`,
                deltaLabel: `FVM ${d.player.fvm} CR`,
                advice: `Esterno o trequartista dai piedi fatati. Crea occasioni nitide ad altissima frequenza, ideale per chi cerca assistman affidabili.`
            }));

        const pureStrikers = [...mapped]
            .filter(d => d.y >= 0.38 && d.x < 0.16)
            .sort((a, b) => b.y - a.y)
            .slice(0, 3)
            .map(d => ({
                player: d.player,
                badge: "🎯 PUNTA PURA D'AREA",
                badgeClass: "badge-under",
                statLabel: `${d.y.toFixed(2)} xG/90`,
                deltaLabel: `FM ${d.player.fm ? Number(d.player.fm).toFixed(2) : '-'}`,
                advice: `Centravanti di manovra ridotta ma micidiale nei 16 metri. Finalizza tutto ciò che gli arriva sui piedi.`
            }));

        return { elite: totalMonsters, under: playmakers, over: pureStrikers, gems: [] };
    }

    if (presetKey === 'value_money') {
        const gems = [...mapped]
            .filter(d => d.player.fvm <= 30 && d.y >= 0.26)
            .sort((a, b) => (b.y / Math.max(1, b.player.fvm)) - (a.y / Math.max(1, a.player.fvm)))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "🚀 VALUE GEM D'ASTA",
                badgeClass: "badge-gem",
                statLabel: `${d.y.toFixed(2)} Minaccia/90' a ${d.player.fvm} CR`,
                deltaLabel: `Affare Fanta`,
                advice: `Produzione offensiva da semitop acquistabile a cifre contenute. Da comprare assolutamente nelle aste di riparazione.`
            }));

        const overpriced = [...mapped]
            .filter(d => d.player.fvm >= 35 && d.y < 0.30)
            .sort((a, b) => (a.y / Math.max(1, a.player.fvm)) - (b.y / Math.max(1, b.player.fvm)))
            .slice(0, 4)
            .map(d => ({
                player: d.player,
                badge: "⚠️ SOVRASTIMATO / RISCHIO",
                badgeClass: "badge-over",
                statLabel: `FVM ${d.player.fvm} CR per ${d.y.toFixed(2)} Minaccia`,
                deltaLabel: `Bassa Resa`,
                advice: `Quotazione elevata a fronte di occasioni create modeste. Evita di strapagarlo: c'è di molto meglio a parità di crediti.`
            }));

        return { elite: gems, over: overpriced, under: [], gems: [] };
    }

    // Portieri
    const topGk = [...mapped]
        .filter(d => d.y >= 0.35 && d.x >= 70)
        .sort((a, b) => b.y - a.y)
        .slice(0, 3)
        .map(d => ({
            player: d.player,
            badge: "🛡️ SARACINESCA TOP",
            badgeClass: "badge-elite",
            statLabel: `+${d.y.toFixed(2)} Gol Salvati (${d.x}% Parate)`,
            deltaLabel: `MV ${d.player.mv ? Number(d.player.mv).toFixed(2) : '-'}`,
            advice: `Portiere superbo: para oltre le aspettative e regala voti altissimi utili per il modificatore di difesa.`
        }));

    const underSiege = [...mapped]
        .filter(d => d.y >= 0.6 && d.x < 70)
        .sort((a, b) => b.y - a.y)
        .slice(0, 3)
        .map(d => ({
            player: d.player,
            badge: "🧤 HERO DA MODIFICATORE",
            badgeClass: "badge-gem",
            statLabel: `+${d.y.toFixed(2)} Gol Evitati`,
            deltaLabel: `FVM ${d.player.fvm} CR`,
            advice: `Difesa traballante ma portiere dai riflessi felini: compie prodezze costanti, garanzia di 6.5 e 7 in pagella.`
        }));

    return { elite: topGk, under: underSiege, over: [], gems: [] };
}

function renderAnalyticsMatrixView() {
    const container = document.getElementById('viewMatrix');
    if (!container) return;

    const presetKey = AnalyticsMatrixState.preset || 'under_over';
    const preset = MATRIX_PRESETS[presetKey];
    if (!preset) return;
    const season = AnalyticsMatrixState.season || '2627';
    const isExpanded = AnalyticsMatrixState.isExpanded;
    const qFilter = AnalyticsMatrixState.quadrantFilter;

    // Filtro base calciatori
    let dataset = PLAYERS.filter(p => {
        if (AnalyticsMatrixState.roleFilter !== 'ALL' && p.role !== AnalyticsMatrixState.roleFilter) return false;
        if (AnalyticsMatrixState.teamFilter !== 'ALL' && p.team !== AnalyticsMatrixState.teamFilter) return false;
        
        const minutes = season === '2627' ? (p.minuti_2627 || 0) : (p.mins_2526 || 0);
        if (minutes < AnalyticsMatrixState.minMinutes) return false;

        if (AnalyticsMatrixState.searchQuery) {
            const q = AnalyticsMatrixState.searchQuery;
            const matchName = (p.name || '').toLowerCase().includes(q);
            const matchTeam = (p.team || '').toLowerCase().includes(q);
            if (!matchName && !matchTeam) return false;
        }

        return true;
    });

    // Calcola coordinate X e Y per ciascun giocatore
    const allMapped = dataset.map(p => {
        const rawX = Number(preset.xKey(p, season)) || 0;
        const rawY = Number(preset.yKey(p, season)) || 0;
        return { player: p, x: rawX, y: rawY };
    }).filter(d => !isNaN(d.x) && !isNaN(d.y));

    // Determina min, max e mediane globali per scaling coerente
    let minX = 0, maxX = 1, minY = 0, maxY = 1;
    if (allMapped.length > 0) {
        minX = Math.min(...allMapped.map(d => d.x));
        maxX = Math.max(...allMapped.map(d => d.x));
        minY = Math.min(...allMapped.map(d => d.y));
        maxY = Math.max(...allMapped.map(d => d.y));
    }

    // Margine generoso per dare respiro al grafico
    const marginX = Math.max(0.2, (maxX - minX) * 0.08);
    const marginY = Math.max(0.2, (maxY - minY) * 0.08);
    const plotMinX = Math.max(0, minX - marginX);
    const plotMaxX = Math.max(plotMinX + 0.8, maxX + marginX);
    const plotMinY = Math.min(0, minY - marginY);
    const plotMaxY = Math.max(plotMinY + 0.8, maxY + marginY);

    const midX = (plotMinX + plotMaxX) / 2;
    const midY = (plotMinY + plotMaxY) / 2;

    // Dimensioni Generose Canvas
    const width = isExpanded ? 1040 : 840;
    const height = isExpanded ? 640 : 520;
    const padL = 60;
    const padR = 35;
    const padT = 40;
    const padB = 48;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const scaleX = (val) => padL + ((val - plotMinX) / (plotMaxX - plotMinX || 1)) * plotW;
    const scaleY = (val) => padT + plotH - ((val - plotMinY) / (plotMaxY - plotMinY || 1)) * plotH;

    const midScreenX = scaleX(midX);
    const midScreenY = scaleY(midY);

    // Funzione per determinare il quadrante di un punto
    const getPointQuadrant = (d) => {
        if (d.x >= midX && d.y >= midY) return 'top_right';
        if (d.x < midX && d.y >= midY) return 'top_left';
        if (d.x >= midX && d.y < midY) return 'bottom_right';
        return 'bottom_left';
    };

    // Conteggi per quadrante
    const quadCounts = {
        top_left: allMapped.filter(d => getPointQuadrant(d) === 'top_left').length,
        top_right: allMapped.filter(d => getPointQuadrant(d) === 'top_right').length,
        bottom_right: allMapped.filter(d => getPointQuadrant(d) === 'bottom_right').length,
        bottom_left: allMapped.filter(d => getPointQuadrant(d) === 'bottom_left').length
    };

    // OTTIMIZZAZIONE ANTI-AMMASSAMENTO
    const isSpecificFilterActive = AnalyticsMatrixState.searchQuery || AnalyticsMatrixState.teamFilter !== 'ALL';
    let mapped = [];
    if (isSpecificFilterActive) {
        mapped = allMapped;
    } else {
        const keyPoints = [];
        const greyPoints = [];
        allMapped.forEach(d => {
            const isGrey = (d.x < midX && d.y < midY);
            if (!isGrey) {
                keyPoints.push(d);
            } else {
                greyPoints.push(d);
            }
        });
        greyPoints.sort((a, b) => (b.player.ovr || 0) - (a.player.ovr || 0));
        mapped = [...keyPoints, ...greyPoints.slice(0, 35)];
    }

    // Identifica i Top Outliers Unici da etichettare direttamente sul grafico (Max 6 per evitare sovrapposizioni)
    const outlierIds = new Set();
    if (allMapped.length > 0) {
        // 1. Top 2 xG (volume massimo)
        [...allMapped].sort((a, b) => b.x - a.x).slice(0, 2).forEach(d => outlierIds.add(d.player.id));
        // 2. Top 2 Gol (finalizzazione massima)
        [...allMapped].sort((a, b) => b.y - a.y).slice(0, 2).forEach(d => outlierIds.add(d.player.id));
        // 3. Top 2 Underperformance (scommesse assolute)
        [...allMapped].sort((a, b) => (a.y - a.x) - (b.y - b.x)).slice(0, 2).forEach(d => outlierIds.add(d.player.id));
        // 4. Top 1 Overperformance (bolla)
        [...allMapped].sort((a, b) => (b.y - b.x) - (a.y - a.x)).slice(0, 1).forEach(d => outlierIds.add(d.player.id));
    }

    // Se c'è una ricerca attiva, etichetta i calciatori trovati
    if (AnalyticsMatrixState.searchQuery) {
        mapped.forEach(d => outlierIds.add(d.player.id));
    }

    // Gestione micro-jitter per coordinate identiche
    const coordCounts = {};
    mapped.forEach(d => {
        const key = `${d.x.toFixed(2)}_${d.y.toFixed(2)}`;
        coordCounts[key] = (coordCounts[key] || 0) + 1;
    });
    const seenCoords = {};

    // Generazione Punti Scatter & Etichette Callout Outliers
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
        const strokeColor = isBought ? '#4ade80' : (isFav ? '#fbbf24' : 'rgba(255,255,255,0.85)');
        const strokeWidth = isBought || isFav ? 2.5 : 1.2;
        const radius = d.player.ovr >= 88 ? 7.5 : (d.player.ovr >= 80 ? 6 : 4.8);

        // Controllo filtro quadrante
        const pQuad = getPointQuadrant(d);
        const isFadedByQuad = (qFilter !== 'ALL' && pQuad !== qFilter);
        const dotOpacity = isFadedByQuad ? 0.12 : 0.92;

        // Etichetta Outlier elegante con badge arrotondato scuro di sfondo (zero sovrapposizioni)
        let labelHtml = '';
        const isOutlier = outlierIds.has(d.player.id);
        if (isOutlier && !isFadedByQuad) {
            const displayName = formatMatrixPlayerName(d.player.name);
            const labelWidth = Math.max(54, displayName.length * 6.8 + 14);
            const isNearRightEdge = cx > (padL + plotW - 90);
            const rectX = isNearRightEdge ? (cx - labelWidth - 8) : (cx + 8);
            const rectY = cy - 9;
            const textX = rectX + labelWidth / 2;
            const textY = cy + 3.5;

            labelHtml = `
                <g class="matrix-outlier-callout" style="pointer-events:none;">
                    <rect x="${rectX}" y="${rectY}" width="${labelWidth}" height="18" rx="5" ry="5" fill="rgba(10, 15, 28, 0.9)" stroke="${strokeColor}" stroke-width="1.2" filter="drop-shadow(0 2px 6px rgba(0,0,0,0.6))" />
                    <text x="${textX}" y="${textY}" fill="#ffffff" font-size="10.5" font-weight="900" text-anchor="middle" font-family="'Outfit', sans-serif">
                        ${displayName}
                    </text>
                </g>
            `;
        }

        // Calcolo delta label per tooltip
        let deltaLabel = '';
        if (presetKey === 'under_over') {
            const diff = d.y - d.x;
            deltaLabel = diff < 0 ? `Δ ${diff.toFixed(2)} xG (Underperformance)` : `+${diff.toFixed(2)} surplus (Overperformance)`;
        } else if (presetKey === 'bonus_engine') {
            deltaLabel = `Totale Minaccia: ${(d.x + d.y).toFixed(2)} /90'`;
        }

        const safeAdvice = (d.y - d.x < 0) 
            ? getTailoredUnderAdvice(d.player, d.x, d.y) 
            : getTailoredOverAdvice(d.player, d.x, d.y);

        const escapedName = (d.player.name || '').replace(/'/g, "\\'");
        const escapedTeam = (d.player.team || '').replace(/'/g, "\\'");
        const escapedAdvice = safeAdvice.replace(/'/g, "\\'").replace(/"/g, '&quot;');

        return `
            <g class="matrix-dot-group" 
               data-id="${d.player.id}"
               onclick="openPlayerProfileModal(${d.player.id})" 
               onmouseenter="highlightMatrixDot(${d.player.id}); showMatrixTooltip(event, ${d.player.id}, '${escapedName}', '${escapedTeam}', '${d.player.role}', '${d.x}', '${d.y}', '${d.player.ovr || '-'}', '${d.player.fvm || '-'}', '${deltaLabel}', '${escapedAdvice}')" 
               onmousemove="moveMatrixTooltip(event)"
               onmouseleave="unhighlightMatrixDot(); hideMatrixTooltip()" 
               style="cursor:pointer;">
                <circle class="matrix-dot-circle" 
                        data-id="${d.player.id}" 
                        data-orig-r="${radius}" 
                        data-orig-stroke="${strokeColor}" 
                        data-orig-sw="${strokeWidth}" 
                        cx="${cx}" cy="${cy}" r="${radius}" 
                        fill="${dotColor}" 
                        stroke="${strokeColor}" 
                        stroke-width="${strokeWidth}" 
                        opacity="${dotOpacity}">
                </circle>
                ${labelHtml}
            </g>
        `;
    }).join('');

    // Calcolo Fanta Insights per il pannello laterale
    const insights = computeMatrixInsights(allMapped, AnalyticsMatrixState.preset, season);

    const renderInsightCards = (list, sectionTitle, sectionIcon, sectionColor) => {
        if (!list || list.length === 0) return '';
        const cardsHtml = list.map(item => `
            <div class="fanta-insight-card" 
                 onclick="openPlayerProfileModal(${item.player.id})" 
                 onmouseenter="highlightMatrixDot(${item.player.id})" 
                 onmouseleave="unhighlightMatrixDot()">
                <div class="fanta-insight-top">
                    <div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;">
                        <span class="role-badge ${item.player.role}" style="font-size:10px;padding:1px 6px;flex-shrink:0;">${item.player.role}</span>
                        <b style="color:#fff;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${item.player.name}</b>
                        <span style="font-size:11.5px;color:var(--text-muted);flex-shrink:0;">(${item.player.team})</span>
                    </div>
                    <span class="insight-pill ${item.badgeClass}">${item.deltaLabel}</span>
                </div>
                <div class="fanta-insight-stats">
                    <span style="color:var(--accent-cyan);font-weight:800;">📊 ${item.statLabel}</span>
                    <span style="color:rgba(255,255,255,0.2);">•</span>
                    <span>FVM: <b style="color:#fff;">${item.player.fvm || '-'} CR</b></span>
                    <span style="color:rgba(255,255,255,0.2);">•</span>
                    <span>OVR: <b style="color:#fff;">${item.player.ovr}</b></span>
                </div>
                <div class="fanta-insight-advice">
                    💡 <b>Consiglio Fanta:</b> ${item.advice}
                </div>
            </div>
        `).join('');

        return `
            <div class="insight-group">
                <div class="insight-group-header" style="border-left: 3px solid ${sectionColor};">
                    <span style="font-size:14px;">${sectionIcon}</span>
                    <span style="color:${sectionColor};font-weight:800;font-size:13px;letter-spacing:-0.2px;">${sectionTitle}</span>
                    <span style="margin-left:auto;font-size:10px;color:var(--text-muted);font-weight:700;">${list.length} GIOCATORI</span>
                </div>
                ${cardsHtml}
            </div>
        `;
    };

    // Toolbar Options
    const teamsList = (typeof TACTICAL_DB !== 'undefined' ? Object.keys(TACTICAL_DB).sort() : []);
    let teamsOptionsHtml = `<option value="ALL">Tutti i 20 Club</option>`;
    teamsList.forEach(t => {
        teamsOptionsHtml += `<option value="${t}" ${AnalyticsMatrixState.teamFilter === t ? 'selected' : ''}>${t}</option>`;
    });

    const presetButtonsHtml = Object.keys(MATRIX_PRESETS).map(key => {
        const isActive = AnalyticsMatrixState.preset === key;
        const icons = { under_over: '⚽', bonus_engine: '⚡', value_money: '💎', gk_matrix: '🧤' };
        const shortTitles = {
            under_over: 'Gol vs xG (Sotto/Sopraperformance)',
            bonus_engine: 'xG vs xA (Generatore di Bonus)',
            value_money: 'Minaccia xG+xA vs FVM (Occasioni & Costo)',
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
        const labels = { ALL: 'Tutti i Ruoli', P: '🧤 Portieri', D: '🛡️ Difensori', C: '🪄 Centrocampisti', A: '⚡ Attaccanti' };
        return `<button class="role-chip ${r} ${isActive ? 'active' : ''}" style="padding:5px 12px;font-size:11.5px;border-radius:8px;" onclick="setMatrixRoleFilter('${r}')">${labels[r]}</button>`;
    }).join('');

    container.innerHTML = `
        <div class="matrix-view-layout ${isExpanded ? 'is-expanded-layout' : ''}">
            <!-- Header Bar -->
            <div class="matrix-header-bar">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:28px;line-height:1;">📊</span>
                    <div>
                        <h2 class="font-title" style="margin:0;font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.3px;">Football Analytics & Scatter Matrix</h2>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                            ${preset.title} — Metodologia "Numero!" e Sportellate: statistiche attese incrociate con guida tattica ad Asta e Scambi.
                        </div>
                    </div>
                </div>

                <div style="display:flex;align-items:center;gap:10px;">
                    <!-- Bottoncino Espandi / Riduci Schermo -->
                    <button class="btn-expand-matrix" onclick="toggleMatrixExpand()" title="${isExpanded ? 'Torna alla vista affiancata' : 'Ingrandisci il grafico a schermo pieno'}">
                        ${isExpanded ? '⤓ Vista Affiancata' : '⛶ Estendi Grafico'}
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
                <div class="role-chip-group" style="display:flex;gap:6px;flex-wrap:wrap;">
                    ${rolesChipsHtml}
                </div>

                <div class="filter-chip-group" style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:11.5px;color:#94a3b8;font-weight:700;">Club:</span>
                    <select class="clean-select" style="max-width:150px;font-size:12px;padding:4px 8px;border-radius:6px;" onchange="setMatrixTeamFilter(this.value)">
                        ${teamsOptionsHtml}
                    </select>
                </div>

                <div class="filter-chip-group" style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:11.5px;color:#94a3b8;font-weight:700;">Minuti:</span>
                    <select class="clean-select" style="padding:4px 8px;font-size:12px;border-radius:6px;" onchange="setMatrixMinMinutes(this.value)">
                        <option value="0" ${AnalyticsMatrixState.minMinutes === 0 ? 'selected' : ''}>Tutti i minuti</option>
                        <option value="45" ${AnalyticsMatrixState.minMinutes === 45 ? 'selected' : ''}>≥ 45'</option>
                        <option value="90" ${AnalyticsMatrixState.minMinutes === 90 ? 'selected' : ''}>≥ 90'</option>
                        <option value="180" ${AnalyticsMatrixState.minMinutes === 180 ? 'selected' : ''}>≥ 180' (Titolari)</option>
                    </select>
                </div>

                <div style="flex:1;min-width:180px;max-width:320px;position:relative;">
                    <input type="text" 
                           class="clean-input-search" 
                           placeholder="🔍 Cerca calciatore o club..." 
                           value="${AnalyticsMatrixState.searchQuery}" 
                           oninput="setMatrixSearch(this.value)" 
                           style="width:100%;padding:6px 12px;font-size:12px;border-radius:8px;">
                </div>

                <div style="font-size:11.5px;font-weight:800;color:var(--accent-cyan);padding:5px 12px;background:rgba(0,242,254,0.1);border:1px solid rgba(0,242,254,0.25);border-radius:8px;white-space:nowrap;margin-left:auto;">
                    ${mapped.length} Giocatori nel Grafico
                </div>
            </div>

            <!-- WORKSPACE (2-COLUMN OPPURE FULL-WIDTH EXPANDED) -->
            <div class="${isExpanded ? 'matrix-expanded-workspace' : 'matrix-two-column-workspace'}">
                <!-- CHART COLUMN -->
                <div class="matrix-chart-column">
                    <div class="matrix-canvas-card">
                        <!-- Quadrants Top Header Indicator (Interactive Click-to-Filter) -->
                        <div class="matrix-quadrant-indicators">
                            <div class="quad-badge top-left ${qFilter === 'top_left' ? 'active-filter' : ''}" 
                                 onclick="setMatrixQuadrantFilter('top_left')" 
                                 title="Clicca per filtrare/evidenziare solo questo quadrante" 
                                 style="color:${preset.qTopLeft.color};border-color:${preset.qTopLeft.color}50;background:${preset.qTopLeft.bg};">
                                <div style="display:flex;align-items:center;justify-content:space-between;">
                                    <b>↖ ${preset.qTopLeft.title}</b>
                                    <span style="font-weight:800;opacity:0.9;">${quadCounts.top_left}</span>
                                </div>
                                <span>${preset.qTopLeft.sub}</span>
                            </div>
                            <div class="quad-badge top-right ${qFilter === 'top_right' ? 'active-filter' : ''}" 
                                 onclick="setMatrixQuadrantFilter('top_right')" 
                                 title="Clicca per filtrare/evidenziare solo questo quadrante" 
                                 style="color:${preset.qTopRight.color};border-color:${preset.qTopRight.color}50;background:${preset.qTopRight.bg};">
                                <div style="display:flex;align-items:center;justify-content:space-between;">
                                    <b>↗ ${preset.qTopRight.title}</b>
                                    <span style="font-weight:800;opacity:0.9;">${quadCounts.top_right}</span>
                                </div>
                                <span>${preset.qTopRight.sub}</span>
                            </div>
                        </div>

                        <!-- SVG SCATTER PLOT -->
                        <svg viewBox="0 0 ${width} ${height}" class="matrix-svg-plot ${isExpanded ? 'svg-expanded' : ''}">
                            <!-- Quadrant Background Tints -->
                            <rect x="${padL}" y="${padT}" width="${midScreenX - padL}" height="${midScreenY - padT}" fill="${preset.qTopLeft.bg}" />
                            <rect x="${midScreenX}" y="${padT}" width="${padL + plotW - midScreenX}" height="${midScreenY - padT}" fill="${preset.qTopRight.bg}" />
                            <rect x="${padL}" y="${midScreenY}" width="${midScreenX - padL}" height="${padT + plotH - midScreenY}" fill="${preset.qBottomLeft.bg}" />
                            <rect x="${midScreenX}" y="${midScreenY}" width="${padL + plotW - midScreenX}" height="${padT + plotH - midScreenY}" fill="${preset.qBottomRight.bg}" />

                            <!-- Quadrant Watermarks inside Canvas -->
                            <text x="${(padL + midScreenX) / 2}" y="${padT + 30}" text-anchor="middle" fill="${preset.qTopLeft.color}" opacity="0.22" font-size="14" font-weight="900" font-family="'Outfit', sans-serif" pointer-events="none">
                                ⚠️ ${preset.qTopLeft.title}
                            </text>
                            <text x="${(midScreenX + padL + plotW) / 2}" y="${padT + 30}" text-anchor="middle" fill="${preset.qTopRight.color}" opacity="0.22" font-size="14" font-weight="900" font-family="'Outfit', sans-serif" pointer-events="none">
                                👑 ${preset.qTopRight.title}
                            </text>
                            <text x="${(midScreenX + padL + plotW) / 2}" y="${padT + plotH - 14}" text-anchor="middle" fill="${preset.qBottomRight.color}" opacity="0.22" font-size="14" font-weight="900" font-family="'Outfit', sans-serif" pointer-events="none">
                                💎 ${preset.qBottomRight.title}
                            </text>
                            <text x="${(padL + midScreenX) / 2}" y="${padT + plotH - 14}" text-anchor="middle" fill="${preset.qBottomLeft.color}" opacity="0.16" font-size="14" font-weight="900" font-family="'Outfit', sans-serif" pointer-events="none">
                                🪙 ${preset.qBottomLeft.title}
                            </text>

                            <!-- Main Axes -->
                            <line x1="${padL}" y1="${padT + plotH}" x2="${padL + plotW}" y2="${padT + plotH}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
                            <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${padT + plotH}" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />

                            <!-- Medians / Crosshair -->
                            <line x1="${midScreenX}" y1="${padT}" x2="${midScreenX}" y2="${padT + plotH}" stroke="rgba(255,255,255,0.18)" stroke-dasharray="5,4" />
                            <line x1="${padL}" y1="${midScreenY}" x2="${padL + plotW}" y2="${midScreenY}" stroke="rgba(255,255,255,0.18)" stroke-dasharray="5,4" />

                            <!-- Diagonal Line (Gol = xG) for Under/Overperformance -->
                            ${AnalyticsMatrixState.preset === 'under_over' ? `
                                <line x1="${scaleX(0)}" y1="${scaleY(0)}" x2="${scaleX(Math.min(plotMaxX, plotMaxY))}" y2="${scaleY(Math.min(plotMaxX, plotMaxY))}" stroke="rgba(251, 191, 36, 0.45)" stroke-dasharray="6,4" stroke-width="1.5" />
                                <text x="${scaleX(Math.min(plotMaxX, plotMaxY) * 0.72)}" y="${scaleY(Math.min(plotMaxX, plotMaxY) * 0.72) - 8}" fill="#fbbf24" font-size="10" font-weight="800" opacity="0.85">Linea Equilibrio (Gol = xG)</text>
                            ` : ''}

                            <!-- Axis Labels -->
                            <text x="${padL + plotW / 2}" y="${height - 12}" text-anchor="middle" fill="var(--accent-cyan)" font-size="12" font-weight="850">${preset.xLabel} ➔</text>
                            <text x="18" y="${padT + plotH / 2}" text-anchor="middle" fill="var(--accent-cyan)" font-size="12" font-weight="850" transform="rotate(-90 18 ${padT + plotH / 2})">➔ ${preset.yLabel}</text>

                            <!-- Axis Min / Mid / Max Ticks -->
                            <text x="${padL}" y="${padT + plotH + 18}" fill="var(--text-muted)" font-size="10" text-anchor="middle">${plotMinX.toFixed(1)}</text>
                            <text x="${midScreenX}" y="${padT + plotH + 18}" fill="var(--text-muted)" font-size="10" text-anchor="middle">${midX.toFixed(1)}</text>
                            <text x="${padL + plotW}" y="${padT + plotH + 18}" fill="var(--text-muted)" font-size="10" text-anchor="middle">${plotMaxX.toFixed(1)}</text>

                            <text x="${padL - 8}" y="${padT + plotH}" fill="var(--text-muted)" font-size="10" text-anchor="end">${plotMinY.toFixed(1)}</text>
                            <text x="${padL - 8}" y="${midScreenY}" fill="var(--text-muted)" font-size="10" text-anchor="end">${midY.toFixed(1)}</text>
                            <text x="${padL - 8}" y="${padT + 8}" fill="var(--text-muted)" font-size="10" text-anchor="end">${plotMaxY.toFixed(1)}</text>

                            <!-- Scatter Dots -->
                            ${dotsSvgHtml}
                        </svg>

                        <!-- Quadrants Bottom Header Indicator (Interactive Click-to-Filter) -->
                        <div class="matrix-quadrant-indicators">
                            <div class="quad-badge bottom-left ${qFilter === 'bottom_left' ? 'active-filter' : ''}" 
                                 onclick="setMatrixQuadrantFilter('bottom_left')" 
                                 title="Clicca per filtrare/evidenziare solo questo quadrante" 
                                 style="color:${preset.qBottomLeft.color};border-color:${preset.qBottomLeft.color}50;background:${preset.qBottomLeft.bg};">
                                <div style="display:flex;align-items:center;justify-content:space-between;">
                                    <b>↙ ${preset.qBottomLeft.title}</b>
                                    <span style="font-weight:800;opacity:0.9;">${quadCounts.bottom_left}</span>
                                </div>
                                <span>${preset.qBottomLeft.sub}</span>
                            </div>
                            <div class="quad-badge bottom-right ${qFilter === 'bottom_right' ? 'active-filter' : ''}" 
                                 onclick="setMatrixQuadrantFilter('bottom_right')" 
                                 title="Clicca per filtrare/evidenziare solo questo quadrante" 
                                 style="color:${preset.qBottomRight.color};border-color:${preset.qBottomRight.color}50;background:${preset.qBottomRight.bg};">
                                <div style="display:flex;align-items:center;justify-content:space-between;">
                                    <b>↘ ${preset.qBottomRight.title}</b>
                                    <span style="font-weight:800;opacity:0.9;">${quadCounts.bottom_right}</span>
                                </div>
                                <span>${preset.qBottomRight.sub}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Legend & Interaction Hint -->
                    <div style="font-size:12px;color:var(--text-secondary);display:flex;align-items:center;justify-content:space-between;padding:6px 10px;background:rgba(255,255,255,0.02);border-radius:8px;">
                        <span>💡 <b>Interazione Grafico:</b> Passa il mouse su qualsiasi punto per aprire il tooltip dettagliato. Clicca sui quadranti per filtrarli.</span>
                        <div style="display:flex;gap:12px;font-weight:700;">
                            <span style="color:#f43f5e;">● Attaccanti</span>
                            <span style="color:#38bdf8;">● Centrocampisti</span>
                            <span style="color:#10b981;">● Difensori</span>
                            <span style="color:#f59e0b;">● Portieri</span>
                        </div>
                    </div>
                </div>

                <!-- EDITORIAL FANTA INSIGHTS & ACTIONABLE RECOMMENDATIONS -->
                <div class="${isExpanded ? 'matrix-expanded-insights-grid' : 'matrix-insights-column'}">
                    <div class="insights-panel-header">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:20px;">🎯</span>
                            <div>
                                <h3 style="margin:0;font-size:15.5px;font-weight:850;color:#fff;font-family:'Outfit',sans-serif;">Verdetti & Consigli Fanta Chiave</h3>
                                <div style="font-size:11px;color:var(--text-muted);">Decisioni operative per Asta & Scambi calcolate dall'algoritmo predittivo</div>
                            </div>
                        </div>
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

// Esporta globalmente
window.initAnalyticsMatrix = initAnalyticsMatrix;
window.setMatrixPreset = setMatrixPreset;
window.setMatrixSeason = setMatrixSeason;
window.setMatrixRoleFilter = setMatrixRoleFilter;
window.setMatrixTeamFilter = setMatrixTeamFilter;
window.setMatrixMinMinutes = setMatrixMinMinutes;
window.setMatrixSearch = setMatrixSearch;
window.toggleMatrixExpand = toggleMatrixExpand;
window.setMatrixQuadrantFilter = setMatrixQuadrantFilter;
window.highlightMatrixDot = highlightMatrixDot;
window.unhighlightMatrixDot = unhighlightMatrixDot;
window.showMatrixTooltip = showMatrixTooltip;
window.moveMatrixTooltip = moveMatrixTooltip;
window.hideMatrixTooltip = hideMatrixTooltip;
window.renderAnalyticsMatrixView = renderAnalyticsMatrixView;
