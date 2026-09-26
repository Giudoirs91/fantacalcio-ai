// ==============================================================================
// MODULO MATCHUP RADAR E CONFRONTO TESTA A TESTA 1VS1 (CON DATI 2025/2026 REALI)
// ==============================================================================

function initMatchupSelects() {
    const selA = document.getElementById('selectMatchupA');
    const selB = document.getElementById('selectMatchupB');
    if (!selA || !selB) return;
    
    selA.innerHTML = '';
    selB.innerHTML = '';

    PLAYERS.forEach(p => {
        const optA = document.createElement('option');
        optA.value = p.id;
        optA.textContent = `${p.name} (${p.team} - ${p.role}) - OVR ${p.ovr}`;
        if (State.matchupA && p.id === State.matchupA.id) optA.selected = true;
        selA.appendChild(optA);

        const optB = document.createElement('option');
        optB.value = p.id;
        optB.textContent = `${p.name} (${p.team} - ${p.role}) - OVR ${p.ovr}`;
        if (State.matchupB && p.id === State.matchupB.id) optB.selected = true;
        selB.appendChild(optB);
    });
}

function setMatchupFromCard(playerId) {
    const p = PLAYERS.find(pl => pl.id === playerId);
    if (!p) return;
    State.matchupB = p;
    const selB = document.getElementById('selectMatchupB');
    if (selB) selB.value = p.id;
    if (typeof switchTab === 'function') switchTab('matchup');
    updateMatchup();
}

function updateMatchup() {
    const elA = document.getElementById('selectMatchupA');
    const elB = document.getElementById('selectMatchupB');
    if (!elA || !elB) return;

    const idA = parseInt(elA.value, 10);
    const idB = parseInt(elB.value, 10);
    State.matchupA = PLAYERS.find(p => p.id === idA) || PLAYERS[0];
    State.matchupB = PLAYERS.find(p => p.id === idB) || PLAYERS[1];

    const pA = State.matchupA;
    const pB = State.matchupB;
    const container = document.getElementById('matchupComparisonContainer');
    if (!container) return;

    const numWinner = (valA, valB, higherIsBetter = true) => {
        const nA = parseFloat(valA) || 0;
        const nB = parseFloat(valB) || 0;
        if (nA === nB) return [false, false];
        if (higherIsBetter) return [nA > nB, nB > nA];
        return [nA < nB, nB < nA];
    };

    const [ovrWinA, ovrWinB] = numWinner(pA.ovr, pB.ovr);
    const [fmWinA, fmWinB] = numWinner(pA.fm, pB.fm);
    const [mvWinA, mvWinB] = numWinner(pA.mv, pB.mv);
    const [minsWinA, minsWinB] = numWinner(pA.mins_2526, pB.mins_2526);
    const [ratingWinA, ratingWinB] = numWinner(pA.rating_2526, pB.rating_2526);
    const [prcWinA, prcWinB] = numWinner(pA.prezzo_cons, pB.prezzo_cons, false);

    const slotWinA = (pA.slot_num || 99) < (pB.slot_num || 99);
    const slotWinB = (pB.slot_num || 99) < (pA.slot_num || 99);

    function getAdviceTooltipText(p) {
        const adviceType = p.ai_advice_type || 'regular';
        const adviceText = p.ai_advice || p.consiglio || '';
        if (p.ovr >= 92 || p.slot_num === 1 || adviceType === 'top' || adviceText.toLowerCase().includes('top player') || adviceText.toLowerCase().includes('top di reparto')) {
            return `👑 Top Player Assoluto: 1° slot o tra i migliori del campionato per fantamedia e bonus attesi. ${adviceText}`;
        }
        if (adviceType === 'leader' || adviceText.toLowerCase().includes('leader')) {
            return `⭐ Leader di Reparto: Titolare di altissimo livello e 2° slot d'asta con voti costanti e bonus frequenti. ${adviceText}`;
        }
        if (adviceType === 'sleeper' || adviceText.toLowerCase().includes('sleeper') || adviceText.toLowerCase().includes('scommessa')) {
            return `🔥 Scommessa ad Alto Potenziale: Calciatore dal prezzo contenuto con statistiche avanzate (xG/xA) che indicano un elevato potenziale a sorpresa. ${adviceText}`;
        }
        if (adviceType === 'buy' || adviceText.toLowerCase().includes('best value')) {
            return `🚀 Best Value: Giocatore che garantisce un rendimento statistico superiore al costo in crediti d'asta. ${adviceText}`;
        }
        if (adviceType === 'hot' || adviceText.includes('IN FORMA') || adviceText.includes('MOMENTO D\'ORO')) {
            return `🔥 In Forma / Momento d'Oro: Calciatore protagonista nelle ultime giornate di Serie A con bonus o voti eccellenti. ${adviceText}`;
        }
        if (adviceType === 'benched' || adviceText.includes('PERSO IL POSTO') || adviceText.includes('IN PANCHINA')) {
            return `🪑 In Panchina: Calciatore con status iniziale elevato ma scivolato indietro nelle gerarchie tecniche dell'allenatore. ${adviceText}`;
        }
        if (adviceType === 'supersub' || adviceText.includes('SUPER-SUB')) {
            return `⚡ Super-Sub / Spacca-Partite: Calciatore che subentra sistematicamente a gara in corso garantendo voto utile e bonus. ${adviceText}`;
        }
        if (adviceType === 'titolarissimo' || adviceText.toLowerCase().includes('titolarissimo')) {
            return `🔒 Titolarissimo (100% da Voto): Certezza assoluta di presenza dal 1' minuto in tutte le giornate disputate. ${adviceText}`;
        }
        if (adviceType === 'titolare' || adviceText.toLowerCase().includes('titolare da voto')) {
            return `🛡️ Titolare Affidabile (75-94%): Calciatore che parte titolare nella grande maggioranza delle partite con sporadico turnover. ${adviceText}`;
        }
        if (adviceType === 'lowcost' || adviceText.toLowerCase().includes('low cost')) {
            return `🪙 Low Cost da Voto: Ottimo elemento da slot finale a 1-5 crediti con titolarità garantita. ${adviceText}`;
        }
        if (adviceType === 'rotation' || adviceText.toLowerCase().includes('ballottaggio')) {
            return `🔄 In Ballottaggio: Giocatore in costante alternanza con un compagno di reparto per una maglia da titolare. ${adviceText}`;
        }
        if (adviceType === 'flop' || (adviceType === 'danger' && adviceText.toLowerCase().includes('flop'))) {
            return `⚠️ Possibile Flop: Calciatore sopravvalutato dal mercato o con rendimento al di sotto delle aspettative di spesa. ${adviceText}`;
        }
        return adviceText || 'Consiglio strategico elaborato dagli algoritmi predittivi';
    }

    const getOopTooltipText = (p) => {
        if (!p.oop_val || p.oop_val === '-') return '';
        const isGold = p.oop_tier === 'ORO' || String(p.oop_val).includes('ORO');
        const isSilver = p.oop_tier === 'ARGENTO' || String(p.oop_val).includes('ARGENTO');
        if (isGold) return "Fuori Ruolo Positivo (FRP Oro): Massima categoria FRP. Giocatore listato arretrato (es. Difensore) che gioca come ala pura d'attacco o quinto offensivo a tutta fascia (+3 facili).";
        if (isSilver) return "Fuori Ruolo Positivo (FRP Argento): Centrocampista che gioca stabilmente da trequartista o seconda punta d'incursione.";
        return "Fuori Ruolo Positivo (FRP Bronzo): Riserva offensiva listata in posizione arretrata, ottima scommessa a 1 credito.";
    };

    const oopA = (pA.oop_val && pA.oop_val !== '-') ? `<span class="oop-table-pill" style="color:#ec4899;font-weight:800;" title="${getOopTooltipText(pA)}">${pA.oop_val}</span>` : '<span style="color:var(--text-muted);">-</span>';
    const oopB = (pB.oop_val && pB.oop_val !== '-') ? `<span class="oop-table-pill" style="color:#ec4899;font-weight:800;" title="${getOopTooltipText(pB)}">${pB.oop_val}</span>` : '<span style="color:var(--text-muted);">-</span>';

    const advA = `<span class="ai-advice-badge ${pA.ai_advice_type || 'regular'}" title="${getAdviceTooltipText(pA)}">${pA.ai_advice || pA.consiglio}</span>`;
    const advB = `<span class="ai-advice-badge ${pB.ai_advice_type || 'regular'}" title="${getAdviceTooltipText(pB)}">${pB.ai_advice || pB.consiglio}</span>`;

    const isBothGK = (pA.role === 'P' && pB.role === 'P');

    let specificRows = '';

    if (isBothGK) {
        // Confronto tra Portieri
        const [gpWinA, gpWinB] = numWinner(pA.goals_prevented_2526, pB.goals_prevented_2526);
        const [csWinA, csWinB] = numWinner(pA.clean_sheets_2526, pB.clean_sheets_2526);
        const [spWinA, spWinB] = numWinner(pA.save_pct_2526, pB.save_pct_2526);
        const [gsWinA, gsWinB] = numWinner(pA.gs, pB.gs, false); // Meno gol subiti è meglio

        specificRows = `
            <tr>
                <td style="${gpWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.goals_prevented_2526 !== null && pA.goals_prevented_2526 !== undefined ? (pA.goals_prevented_2526 >= 0 ? '+' + pA.goals_prevented_2526 : pA.goals_prevented_2526) : '-'}</b></td>
                <td title="Goals Prevented: differenza tra xG concessi dagli avversari e gol effettivamente subiti. Punteggio positivo indica miracoli e parate decisive"><b>Gol Evitati / Salvati (25/26) ℹ️</b></td>
                <td style="${gpWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.goals_prevented_2526 !== null && pB.goals_prevented_2526 !== undefined ? (pB.goals_prevented_2526 >= 0 ? '+' + pB.goals_prevented_2526 : pB.goals_prevented_2526) : '-'}</b></td>
            </tr>
            <tr>
                <td style="${csWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.clean_sheets_2526 !== null ? pA.clean_sheets_2526 + ' Clean Sheets' : '-'}</b></td>
                <td title="Partite disputate senza incassare gol (fondamentale per bonus imbattibilità +1)"><b>Partite a Porta Inviolata (CS) ℹ️</b></td>
                <td style="${csWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.clean_sheets_2526 !== null ? pB.clean_sheets_2526 + ' Clean Sheets' : '-'}</b></td>
            </tr>
            <tr>
                <td style="${spWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.save_pct_2526 ? pA.save_pct_2526 + '%' : '-'}</b></td>
                <td title="Percentuale di conclusioni dirette nello specchio neutralizzate"><b>% Parate Effettuate (25/26) ℹ️</b></td>
                <td style="${spWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.save_pct_2526 ? pB.save_pct_2526 + '%' : '-'}</b></td>
            </tr>
            <tr>
                <td style="${gsWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.gs} Gol Subiti</b></td>
                <td title="Numero totale di gol subiti nella Serie A 2025/26 (meno sono, meglio è)"><b>Gol Subiti Totali 25/26 ℹ️</b></td>
                <td style="${gsWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.gs} Gol Subiti</b></td>
            </tr>
        `;
    } else {
        // Confronto tra Giocatori di Movimento (D, C, A)
        const [xg90WinA, xg90WinB] = numWinner(pA.xg90_2526, pB.xg90_2526);
        const [xgotWinA, xgotWinB] = numWinner(pA.xgot_2526, pB.xgot_2526);
        const [xa90WinA, xa90WinB] = numWinner(pA.xa90_2526, pB.xa90_2526);
        const [tklWinA, tklWinB] = numWinner(pA.tkl_int90_2526, pB.tkl_int90_2526);
        const [gfWinA, gfWinB] = numWinner(pA.gf, pB.gf);

        specificRows = `
            <tr>
                <td style="${xg90WinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.xg90_2526 !== null ? pA.xg90_2526 : '-'}</b></td>
                <td title="Expected Goals ogni 90 minuti: indice di pericolosità offensiva e probabilità statistica di segnare un gol"><b>xG ogni 90 min (Goal Threat) ℹ️</b></td>
                <td style="${xg90WinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.xg90_2526 !== null ? pB.xg90_2526 : '-'}</b></td>
            </tr>
            <tr>
                <td style="${xgotWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.xgot_2526 !== null ? pA.xgot_2526 : '-'}</b></td>
                <td title="Expected Goals on Target: misura la qualità e precisione dei tiri che centrano lo specchio della porta"><b>xGOT (Qualità Tiri Specchio) ℹ️</b></td>
                <td style="${xgotWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.xgot_2526 !== null ? pB.xgot_2526 : '-'}</b></td>
            </tr>
            <tr>
                <td style="${xa90WinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.xa90_2526 !== null ? pA.xa90_2526 : '-'}</b></td>
                <td title="Expected Assists ogni 90 minuti: misura la capacità del calciatore di creare occasioni nitide da gol per i compagni"><b>xA ogni 90 min (Creatività Assist) ℹ️</b></td>
                <td style="${xa90WinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.xa90_2526 !== null ? pB.xa90_2526 : '-'}</b></td>
            </tr>
            <tr>
                <td style="${tklWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.tkl_int90_2526 !== null ? pA.tkl_int90_2526 : '-'}</b></td>
                <td title="Contrasti vinti e palloni intercettati ogni 90 minuti: parametro cruciale per i voti alti al modificatore di difesa"><b>Tackles + Intercetti/90 ℹ️</b></td>
                <td style="${tklWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.tkl_int90_2526 !== null ? pB.tkl_int90_2526 : '-'}</b></td>
            </tr>
            <tr>
                <td style="${gfWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.gf} Gol / ${pA.ass} Assist</b></td>
                <td title="Bonus pesanti effettivi realizzati nella stagione 2025/26"><b>Gol & Assist Reali 25/26 ℹ️</b></td>
                <td style="${gfWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.gf} Gol / ${pB.ass} Assist</b></td>
            </tr>
        `;
    }

    container.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:16px;">
            <div style="background:rgba(0,242,254,0.08);border:1px solid rgba(0,242,254,0.3);border-radius:12px;padding:16px;display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="role-badge ${pA.role}" style="width:36px;height:36px;font-size:16px;">${pA.role}</div>
                    <div>
                        <h3 style="font-size:18px;color:#fff;font-weight:800;">${pA.name}</h3>
                        <div style="color:var(--text-secondary);font-size:12px;">${pA.team} • ${pA.mantra} ${pA.league_2526 && pA.league_2526 !== 'Serie A' ? '• ' + pA.league_2526 : ''}</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div class="ovr-pill top-tier" style="font-size:18px;padding:4px 10px;">${pA.ovr} OVR</div>
                    <div style="color:var(--accent-gold);font-weight:800;font-size:14px;margin-top:4px;">${pA.prezzo_cons} CR</div>
                </div>
            </div>

            <div style="background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.3);border-radius:12px;padding:16px;display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="role-badge ${pB.role}" style="width:36px;height:36px;font-size:16px;">${pB.role}</div>
                    <div>
                        <h3 style="font-size:18px;color:#fff;font-weight:800;">${pB.name}</h3>
                        <div style="color:var(--text-secondary);font-size:12px;">${pB.team} • ${pB.mantra} ${pB.league_2526 && pB.league_2526 !== 'Serie A' ? '• ' + pB.league_2526 : ''}</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div class="ovr-pill top-tier" style="font-size:18px;padding:4px 10px;">${pB.ovr} OVR</div>
                    <div style="color:var(--accent-gold);font-weight:800;font-size:14px;margin-top:4px;">${pB.prezzo_cons} CR</div>
                </div>
            </div>
        </div>

        <div class="table-wrapper">
            <table class="fanta-table" style="text-align:center;">
                <thead>
                    <tr>
                        <th style="color:var(--accent-cyan);text-align:center;width:40%;">🔵 ${pA.name}</th>
                        <th style="text-align:center;width:20%;">PARAMETRO (2025/2026)</th>
                        <th style="color:#f472b6;text-align:center;width:40%;">🔴 ${pB.name}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="${slotWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}">${pA.slot_fascia || (pA.slot_num + '° Slot')}</td>
                        <td title="Fascia d'asta consigliata per leghe a 8 partecipanti (1° Slot per i top a scendere fino alle riserve)"><b>Slot / Fascia (8 Squadre) ℹ️</b></td>
                        <td style="${slotWinB ? 'color:#f472b6;font-weight:900;' : ''}">${pB.slot_fascia || (pB.slot_num + '° Slot')}</td>
                    </tr>
                    <tr>
                        <td style="${ovrWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.ovr}</b></td>
                        <td title="Overall OVR (45-98): Valutazione predittiva complessiva elaborata dall'algoritmo AI"><b>Overall OVR ℹ️</b></td>
                        <td style="${ovrWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.ovr}</b></td>
                    </tr>
                    <tr>
                        <td style="${ratingWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.rating_2526 || '-'}</b></td>
                        <td title="Voto statistico puro oggettivo generato dall'analisi statistica Opta/SofaScore"><b>Rating Statistico 25/26 ℹ️</b></td>
                        <td style="${ratingWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.rating_2526 || '-'}</b></td>
                    </tr>
                    
                    ${specificRows}

                    <tr>
                        <td style="${fmWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.fm > 0 ? pA.fm : '-'}</b></td>
                        <td title="FantaMedia ufficiale registrata nella scorsa stagione comprensiva di bonus e malus"><b>FantaMedia 25/26 ℹ️</b></td>
                        <td style="${fmWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.fm > 0 ? pB.fm : '-'}</b></td>
                    </tr>
                    <tr>
                        <td style="${minsWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.mins_2526 ? pA.mins_2526 + "'" : '-'}</b></td>
                        <td title="Minutaggio totale giocato in campionato nella passata stagione"><b>Minuti Giocati 25/26 ℹ️</b></td>
                        <td style="${minsWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.mins_2526 ? pB.mins_2526 + "'" : '-'}</b></td>
                    </tr>
                    <tr>
                        <td><span class="fragilita-pill ${pA.fragilita_badge || 'bassa'}" title="Indice predittivo di fragilità fisica: calcolato su infortuni storici, giorni di assenza e partite saltate nell'ultimo triennio">${pA.fragilita_val || '🟢 Bassa'}</span></td>
                        <td title="Rischio infortuni predittivo basato su giorni di stop e partite saltate nell'ultimo triennio"><b>Fragilità Fisica & Infortuni ℹ️</b></td>
                        <td><span class="fragilita-pill ${pB.fragilita_badge || 'bassa'}" title="Indice predittivo di fragilità fisica: calcolato su infortuni storici, giorni di assenza e partite saltate nell'ultimo triennio">${pB.fragilita_val || '🟢 Bassa'}</span></td>
                    </tr>
                    <tr>
                        <td>${oopA}</td>
                        <td title="Fuori Ruolo Positivo (FRP): Calciatore schierato sul campo in una posizione più offensiva rispetto a quella con cui è listato (es. Difensore che gioca Ala o Centrocampista che gioca Seconda Punta), aumentando nettamente le probabilità di bonus (+3/+1)."><b>Fuori Ruolo Positivo (FRP) ℹ️</b></td>
                        <td>${oopB}</td>
                    </tr>
                    <tr>
                        <td>${advA}</td>
                        <td title="Consiglio strategico sintetico elaborato dall'intelligenza artificiale per l'asta e la gestione rosa"><b>Consiglio Strategico AI ℹ️</b></td>
                        <td>${advB}</td>
                    </tr>
                    <tr>
                        <td style="${prcWinA ? 'color:var(--accent-cyan);font-weight:900;' : ''}"><b>${pA.prezzo_cons} CR</b></td>
                        <td title="Budget razionale d'acquisto calcolato su base 1000 crediti"><b>Prezzo Consigliato (1000 CR) ℹ️</b></td>
                        <td style="${prcWinB ? 'color:#f472b6;font-weight:900;' : ''}"><b>${pB.prezzo_cons} CR</b></td>
                    </tr>
                    <tr>
                        <td>${renderUpcomingSchedulePills(pA.team)}</td>
                        <td title="Indice di difficoltà (FDR) delle prossime 5 partite di campionato (Verde = Facile, Giallo = Medio, Rosso = Difficile)"><b>Prossimi 5 Match (FDR) ℹ️</b></td>
                        <td>${renderUpcomingSchedulePills(pB.team)}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Sezione Interattiva Calendario Ufficiale 38 Giornate -->
        <div style="margin-top:32px;background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;margin-bottom:20px;">
                <div>
                    <h3 style="margin:0;font-size:18px;font-weight:900;color:#fff;display:flex;align-items:center;gap:8px;">
                        <span>📅</span> Calendario Ufficiale Serie A Enilive 2026/27
                    </h3>
                    <p style="margin:4px 0 0 0;font-size:13px;color:var(--text-secondary);">38 Giornate complete con Fixture Difficulty Rating (FDR)</p>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <label style="font-size:13px;color:var(--text-secondary);font-weight:600;">Seleziona Giornata:</label>
                    <select id="selectCalendarRound" class="fanta-select" style="min-width:140px;" onchange="renderCalendarRound(parseInt(this.value, 10))">
                        ${Array.from({length: 38}, (_, i) => i + 1).map(g => `<option value="${g}" ${g === (window.currentSelectedRound || 5) ? 'selected' : ''}>Giornata ${g}</option>`).join('')}
                    </select>
                </div>
            </div>
            <div id="calendarRoundGrid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:12px;"></div>
        </div>
    `;

    renderCalendarRound(window.currentSelectedRound || 5);
}

function getUpcomingMatchesForTeam(teamName, count = 5) {
    if (typeof OFFICIAL_CALENDAR_2026_27 === 'undefined' || !Array.isArray(OFFICIAL_CALENDAR_2026_27)) return [];
    const tClean = (teamName || '').toLowerCase();
    const upcoming = [];
    
    // Assumiamo che le prime 4 giornate siano state giocate (partiamo dalla 5)
    for (const g of OFFICIAL_CALENDAR_2026_27) {
        if (g.giornata < 5) continue;
        for (const m of (g.matches || [])) {
            if (m.home.toLowerCase() === tClean) {
                upcoming.push({ giornata: g.giornata, opponent: m.away, is_home: true });
                break;
            } else if (m.away.toLowerCase() === tClean) {
                upcoming.push({ giornata: g.giornata, opponent: m.home, is_home: false });
                break;
            }
        }
        if (upcoming.length >= count) break;
    }
    return upcoming;
}

function renderUpcomingSchedulePills(teamName) {
    const matches = getUpcomingMatchesForTeam(teamName, 5);
    if (!matches || matches.length === 0) return '<span style="color:var(--text-secondary);">-</span>';

    return `<div style="display:flex;gap:4px;justify-content:center;flex-wrap:wrap;">` +
        matches.map(m => {
            const loc = m.is_home ? 'C' : 'T';
            const oppShort = m.opponent.substring(0, 3).toUpperCase();
            // Rating visivo
            const isBig = ['Inter', 'Juventus', 'Napoli', 'Milan', 'Atalanta', 'Roma'].includes(m.opponent);
            const isEasy = ['Venezia', 'Frosinone', 'Sassuolo', 'Lecce', 'Como', 'Parma', 'Monza'].includes(m.opponent);
            const badgeBg = isBig ? 'rgba(239,68,68,0.2)' : (isEasy ? 'rgba(34,197,94,0.2)' : 'rgba(59,130,246,0.15)');
            const badgeBorder = isBig ? '#ef4444' : (isEasy ? '#22c55e' : '#3b82f6');
            const badgeColor = isBig ? '#fca5a5' : (isEasy ? '#86efac' : '#93c5fd');

            return `<span style="font-size:11px;padding:3px 6px;border-radius:6px;background:${badgeBg};border:1px solid ${badgeBorder};color:${badgeColor};font-weight:700;" title="G${m.giornata}: ${m.opponent} (${m.is_home ? 'Casa' : 'Trasferta'})">
                G${m.giornata}: ${oppShort} (${loc})
            </span>`;
        }).join('') +
    `</div>`;
}

function renderCalendarRound(roundNum) {
    window.currentSelectedRound = roundNum;
    const grid = document.getElementById('calendarRoundGrid');
    if (!grid) return;

    if (typeof OFFICIAL_CALENDAR_2026_27 === 'undefined' || !Array.isArray(OFFICIAL_CALENDAR_2026_27)) {
        grid.innerHTML = '<div style="color:var(--text-secondary);">Calendario non disponibile.</div>';
        return;
    }

    const roundData = OFFICIAL_CALENDAR_2026_27.find(g => g.giornata === roundNum);
    if (!roundData || !roundData.matches) {
        grid.innerHTML = `<div style="color:var(--text-secondary);">Nessun match trovato per la Giornata ${roundNum}.</div>`;
        return;
    }

    grid.innerHTML = roundData.matches.map(m => `
        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;transition:border-color 0.2s ease;">
            <div style="font-weight:800;font-size:14px;color:#fff;display:flex;align-items:center;gap:8px;">
                <span>${m.home}</span>
            </div>
            <span style="font-size:11px;font-weight:800;color:var(--accent-cyan);padding:2px 8px;background:rgba(0,242,254,0.1);border-radius:6px;">VS</span>
            <div style="font-weight:800;font-size:14px;color:#fff;display:flex;align-items:center;gap:8px;">
                <span>${m.away}</span>
            </div>
        </div>
    `).join('');
}

