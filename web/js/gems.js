// ==============================================================================
// MODULO PREDITTIVO AI: GEMME NASCOSTE, SLEEPER & CLUB RATING >= 7.0
// ==============================================================================

window.gemsState = {
    roleFilter: 'ALL',
    clusterFilter: 'ALL',
    sortFilter: 'AI_SCORE',
    searchQuery: '',
    viewMode: 'LIST'
};

function getPredictiveSleeperScore(p) {
    const role = p.role;
    const xg90 = Number(p.xg90_2526) || 0;
    const xa90 = Number(p.xa90_2526) || 0;
    const shots90 = Number(p.shots90_2526) || 0;
    const rating = Number(p.rating_2526) || 0;
    const isOop = !!p.is_oop;
    const tit = Number(p.titolarita) || 50;
    const g26 = Number(p.gol_2627) || 0;
    const a26 = Number(p.assist_2627) || 0;
    const pres26 = Number(p.presenze_2627) || 0;
    const price = Number(p.prezzo_cons) || 1;

    let score = 0;

    // 1. Contesto offensivo di squadra
    let attBonus = 0;
    if (typeof TACTICAL_DB !== 'undefined' && TACTICAL_DB[p.team]) {
        const attStars = TACTICAL_DB[p.team].att_stars || 3;
        attBonus = (attStars - 2) * 5;
    }

    // 2. Metriche per Ruolo
    if (role === 'A') {
        score = (xg90 * 60) + (xa90 * 30) + (shots90 * 8) + (g26 * 15) + (a26 * 8) + attBonus;
        if (rating >= 6.8) score += (rating - 6.5) * 20;
    } else if (role === 'C') {
        score = (xg90 * 50) + (xa90 * 55) + (shots90 * 6) + (g26 * 18) + (a26 * 14) + attBonus;
        if (isOop) score += 22; // Bonus enorme per ali/trequartisti quotati C
        if (rating >= 6.8) score += (rating - 6.5) * 24;
    } else if (role === 'D') {
        score = (xg90 * 35) + (xa90 * 50) + (shots90 * 4) + (g26 * 20) + (a26 * 16);
        if (isOop) score += 25; // Bonus enorme per quinti/terzini fluidificanti
        if (rating >= 6.9) score += (rating - 6.7) * 35; // Alta propensione da modificatore
    } else if (role === 'P') {
        const gp = Number(p.goals_prevented_2526) || 0;
        const cs = Number(p.clean_sheets_2526) || 0;
        score = (rating >= 6.8 ? (rating - 6.5) * 30 : 0) + (gp * 3) + (cs * 2);
    }

    // 3. Titolarità & Affidabilità
    if (tit >= 80) score += 12;
    else if (tit >= 65) score += 8;
    else if (tit >= 50) score += 4;

    // 4. Rapporto Qualità/Prezzo (Underdog Efficiency)
    // Più il prezzo è contenuto rispetto alle metriche, più è una gemma insospettabile!
    if (price <= 5) score += 15;
    else if (price <= 12) score += 10;
    else if (price <= 20) score += 5;

    return Math.round(score * 10) / 10;
}

function getAIPredictionDetails(p) {
    const name = p.name;
    const team = p.team;
    const role = p.role;
    const xg90 = Number(p.xg90_2526) || 0;
    const xa90 = Number(p.xa90_2526) || 0;
    const rating = Number(p.rating_2526) || 0;
    const isOop = !!p.is_oop;
    const g26 = Number(p.gol_2627) || 0;
    const a26 = Number(p.assist_2627) || 0;

    // Cluster e motivazione personalizzata
    let cluster = 'REGULAR';
    let clusterLabel = '💎 Gemma Nascosta';
    let predictionText = '';
    let projectedBonus = 'Bonus Costanti (3-5 gol/assist)';

    if (rating >= 7.0 || (rating >= 6.95 && p.mins_2526 >= 1500)) {
        cluster = 'RATING_7';
        clusterLabel = '🌟 Club Media Voto ≥ 7.0';
    } else if (isOop) {
        cluster = 'OOP';
        clusterLabel = '⚡ Jolly Fuori Ruolo (OOP)';
    } else if (xa90 >= 0.18 || (role === 'C' && xa90 >= 0.14)) {
        cluster = 'ASSIST_MACHINE';
        clusterLabel = '🎯 Macchina da Assist (High xA)';
    } else if (xg90 >= 0.22 || g26 >= 1) {
        cluster = 'SNIPER';
        clusterLabel = '🚀 Cecchino Low Cost (High xG)';
    }

    // Motivazioni sartoriali per i profili di spicco
    if (name === 'Schmid') {
        predictionText = "Numeri da trequartista d'alta classifica: con 0.24 xG90 e 0.31 xA90 genera occasioni da gol ogni partita. Alvini lo impiega stabilmente dietro le punte; a questo costo è il miglior affare del Frosinone.";
        projectedBonus = "Proiezione: 5-7 Gol + 6-8 Assist";
    } else if (name.includes('Kamara') && team === 'Udinese') {
        predictionText = "Quinto a tutta fascia che chiude spesso l'azione sul secondo palo nel sistema di Runjaic. Con 2 gol e 1 assist in sole 3 giornate conferma una spinta offensiva letale pagata 1 credito.";
        projectedBonus = "Proiezione: 4-6 Gol + 4-6 Assist (Top D)";
    } else if (name === 'Chukwueze') {
        predictionText = "Nel 3-4-2-1 di Ruben Amorim ha licenza di spingere e puntare l'uomo. Ha già servito 2 assist in 3 giornate con un xA90 di 0.28: se trova continuità fisica produrrà bonus seriali.";
        projectedBonus = "Proiezione: 6-8 Gol + 7-9 Assist";
    } else if (name === 'Saelemaekers') {
        predictionText = "Rating mostruoso di 7.37: abbina una fase difensiva impeccabile da 7 in pagella ad inserimenti puntuali con assist e conclusioni. Garanzia sia per il modificatore che per i bonus.";
        projectedBonus = "Candidato fermo al Club Rating ≥ 7.0";
    } else if (name === 'Piccoli') {
        predictionText = "Perno centrale del tridente spregiudicato di Tedesco a Bologna. Con 0.35 xG90 riceve un volume altissimo di cross e palloni lavorabili: titolare economico da doppia cifra potenziale.";
        projectedBonus = "Proiezione: 10-13 Gol in Serie A";
    } else if (name.includes('Varela') && team === 'Monza') {
        predictionText = "Attaccante di grande dinamismo e strappi feroci agli ordini di Juric. Ha un xG90 sbalorditivo di 0.44 e 2 reti all'attivo: focalizza tutta la manovra offensiva brianzola.";
        projectedBonus = "Proiezione: 11-14 Gol";
    } else if (name === 'Bernardeschi') {
        predictionText = "Schierato ala offensiva nel 4-3-3 di Tedesco con compiti di rifinitura e tiri da fuori. Statistiche avanzate da 0.22 xG90 e 0.17 xA90: a soli 8 CR è un furto d'asta legalizzato.";
        projectedBonus = "Proiezione: 6-8 Gol + 5-7 Assist";
    } else if (name === 'Milla') {
        predictionText = "Mezzala di inserimento arrembante nel Como spettacolare di Fabregas. 0.32 xG90 per un centrocampista centrale è un dato d'élite europea: segna e calcia costantemente.";
        projectedBonus = "Proiezione: 5-7 Gol pesanti";
    } else if (name === 'Kaiki') {
        predictionText = "Terzino sinistro di grande velocità con un rating oggettivo fenomenale di 7.34. Perfetto per il modificatore di difesa e con cross sempre precisi.";
        projectedBonus = "Rating previsto ≥ 7.10 + 4-5 Assist";
    } else if (name === 'Zalewski') {
        predictionText = "Sarri lo impiega stabilmente come ala d'attacco nel tridente dell'Atalanta. 0.21 xA90 e 7.01 di rating: quotato centrocampista ma con compiti da punta a 1 credito.";
        projectedBonus = "Proiezione: 4-6 Gol + 5-7 Assist (Jolly ORO)";
    } else if (name === 'Adams C.') {
        predictionText = "Coppia d'attacco fisica e rapida nel Torino di Abate. Con 2 gol già a referto e 0.27 xG90 rappresenta la concretezza che manca a molte prime punte ben più costose.";
        projectedBonus = "Proiezione: 9-12 Gol";
    } else if (name === 'Geubbels') {
        predictionText = "Fisicità e progressione straripante a Lecce: xG90 mostruoso di 0.51 ogni 90 minuti. Se aggiusta la mira è la sorpresa assoluta tra gli attaccanti a basso costo.";
        projectedBonus = "Proiezione: 7-10 Gol da scommessa pura";
    } else if (name === 'Volpato') {
        predictionText = "Trequartista di grandissima inventiva con Aquilani al Sassuolo. Gioca vicino alla porta e dialoga con Berardi: già a segno, destinato a salire di valore.";
        projectedBonus = "Proiezione: 5-7 Gol + 5-7 Assist";
    } else if (name === 'Bernasconi') {
        predictionText = "Esterno mancino con qualità di cross impressionante: 0.20 xA90 e 7.02 di rating nell'Atalanta. Costante dispensatore di bonus assist.";
        projectedBonus = "Proiezione: 5-8 Assist stagionali";
    } else if (name === 'Vojvoda') {
        predictionText = "Padrone della corsia destra friulana, 92% di titolarità e 0.15 xA90. Spinge con continuità e calcia i piazzati indiretti.";
        projectedBonus = "Rendimento garantito + 4-6 Assist";
    } else if (name === 'Muric') {
        predictionText = "Rating 7.29 con una percentuale di parate salva-risultato tra le più alte d'Europa. Portiere da modificatore assoluto a costi contenuti.";
        projectedBonus = "Media Voto prevista ≥ 6.45 con picchi da 7.5";
    } else if (name === 'Diogo Leite') {
        predictionText = "Nuovo perno difensivo della Lazio di Gattuso: forte nel gioco aereo e roccioso nei duelli (rating 7.08 in Bundesliga). Riforma la coppia dell'Union con Doekhi.";
        projectedBonus = "Garanzia Modificatore (Media Voto ≥ 6.35) + 1-2 Gol da corner";
    } else {
        if (cluster === 'RATING_7') {
            predictionText = `Costanza di rendimento eccezionale (${rating} di rating): vince duelli, sbaglia pochissimi palloni ed è amatissimo dai pagellisti. Pilastro da modificatore.`;
            projectedBonus = "Alta probabilità di media voto finale ≥ 7.0";
        } else if (cluster === 'OOP') {
            predictionText = `Schierato in posizione avanzata rispetto al ruolo d'asta: sfrutta il baricentro alto della squadra per entrare regolarmente in area di rigore.`;
            projectedBonus = "Bonus costanti e presenze ad alto impatto";
        } else if (cluster === 'ASSIST_MACHINE') {
            predictionText = `Specialista dei passaggi chiave con un impressionante xA90 di ${xa90}: serve palloni d'oro per le punte e calcia spesso i calci da fermo.`;
            projectedBonus = "Proiezione: 5-8 Assist stagionali";
        } else if (cluster === 'SNIPER') {
            predictionText = `Attaccante con alto indice di pericolosità (${xg90} xG ogni 90 min). Tira molto e gioca in un sistema propositivo a prezzo d'affare.`;
            projectedBonus = "Finalizzatore concreto da 7-11 bonus";
        } else {
            predictionText = `Incrocio favorevole tra minutaggio, metriche avanzate e ruolo tattico con ${team}. Sleeper eccellente da prendere a pochi crediti.`;
            projectedBonus = "Ottimo rapporto rendimento / crediti spesi";
        }
    }

    return { cluster, clusterLabel, predictionText, projectedBonus };
}

function renderGemsRoleBadge(p) {
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    if (isMantra && p.mantra) {
        return `<span class="mantra-pill" style="font-size:10px;padding:2px 6px;background:rgba(0,242,254,0.15);border:1px solid var(--accent-cyan);color:var(--accent-cyan);border-radius:4px;font-weight:800;letter-spacing:0.3px;">${p.mantra}</span>`;
    }
    return `<span class="role-badge ${p.role}" style="font-size:11px;width:22px;height:22px;">${p.role}</span>`;
}

function renderGemsView() {
    const container = document.getElementById('viewGems');
    if (!container) return;

    // Filtra tutti i giocatori del database per estrarre gli insospettabili
    // Soglie di prezzo: A <= 35, C <= 26, D <= 25, P <= 15
    const maxPrices = { 'A': 35, 'C': 26, 'D': 25, 'P': 15 };
    
    let candidates = PLAYERS.filter(p => {
        const maxP = maxPrices[p.role] || 25;
        if ((p.prezzo_cons || 1) > maxP) return false;
        if ((p.titolarita || 0) < 45) return false;
        
        // Calcola punteggio predittivo
        p._sleeperScore = getPredictiveSleeperScore(p);
        p._aiPrediction = getAIPredictionDetails(p);

        // Deve avere almeno qualche dato favorevole o xG/xA o OOP o Rating alto o gol recenti
        const hasNumbers = (p.xg90_2526 > 0.05) || (p.xa90_2526 > 0.05) || (p.rating_2526 >= 6.8) || (p.is_oop) || (p.gol_2627 > 0) || (p.assist_2627 > 0);
        return hasNumbers && p._sleeperScore >= 28;
    });

    // Applica filtri UI
    const isMantra = (typeof State !== 'undefined' && State.systemMode === 'mantra');
    const rFilt = window.gemsState.roleFilter;
    const cFilt = window.gemsState.clusterFilter;
    const sFilt = window.gemsState.sortFilter;
    const qFilt = (window.gemsState.searchQuery || '').trim().toLowerCase();

    if (rFilt !== 'ALL') {
        if (isMantra) {
            const rf = rFilt.toUpperCase();
            candidates = candidates.filter(p => {
                if (!p.mantra) return false;
                const mRoles = String(p.mantra).toUpperCase().split(/[,;/]+/).map(s => s.trim());
                if (rf === 'DIF') return mRoles.some(r => ['DC', 'B', 'DD', 'DS'].includes(r));
                if (rf === 'MED') return mRoles.some(r => ['E', 'M', 'C'].includes(r));
                if (rf === 'ATT') return mRoles.some(r => ['T', 'W', 'A', 'PC'].includes(r));
                return mRoles.includes(rf);
            });
        } else {
            candidates = candidates.filter(p => p.role === rFilt);
        }
    }
    if (cFilt !== 'ALL') {
        candidates = candidates.filter(p => p._aiPrediction.cluster === cFilt);
    }
    if (qFilt) {
        candidates = candidates.filter(p => p.name.toLowerCase().includes(qFilt) || p.team.toLowerCase().includes(qFilt) || (p.mantra || '').toLowerCase().includes(qFilt));
    }

    // Ordinamento
    if (sFilt === 'AI_SCORE') {
        candidates.sort((a, b) => b._sleeperScore - a._sleeperScore);
    } else if (sFilt === 'PRICE_ASC') {
        candidates.sort((a, b) => (a.prezzo_cons || 1) - (b.prezzo_cons || 1));
    } else if (sFilt === 'RATING_DESC') {
        candidates.sort((a, b) => (b.rating_2526 || 0) - (a.rating_2526 || 0));
    } else if (sFilt === 'BONUS_DESC') {
        candidates.sort((a, b) => ((b.xg90_2526 || 0) + (b.xa90_2526 || 0)) - ((a.xg90_2526 || 0) + (a.xa90_2526 || 0)));
    }

    // Costruzione Visualizzazione (Lista Tabellare o Schede)
    const vMode = window.gemsState.viewMode || 'LIST';
    let mainContentHtml = '';

    if (candidates.length === 0) {
        mainContentHtml = `
            <div style="text-align:center;padding:48px 20px;background:rgba(255,255,255,0.02);border-radius:12px;border:1px dashed rgba(255,255,255,0.08);color:var(--text-muted);">
                <span style="font-size:32px;">🔍</span>
                <p style="margin:8px 0 0 0;font-size:14px;">Nessun calciatore corrisponde ai filtri selezionati.</p>
            </div>
        `;
    } else if (vMode === 'LIST') {
        let rowsHtml = '';
        candidates.forEach((p, idx) => {
            const isBought = isPlayerBought(p.id);
            const isTaken = isPlayerTakenByOther(p.id);
            const pred = p._aiPrediction;

            let clusterBadgeStyle = 'background:rgba(139,92,246,0.15);border-color:rgba(139,92,246,0.4);color:#c084fc;';
            if (pred.cluster === 'RATING_7') {
                clusterBadgeStyle = 'background:rgba(251,191,36,0.15);border-color:rgba(251,191,36,0.4);color:#fbbf24;box-shadow:0 0 8px rgba(251,191,36,0.2);';
            } else if (pred.cluster === 'OOP') {
                clusterBadgeStyle = 'background:rgba(236,72,153,0.15);border-color:rgba(236,72,153,0.4);color:#f472b6;';
            } else if (pred.cluster === 'ASSIST_MACHINE') {
                clusterBadgeStyle = 'background:rgba(0,242,254,0.15);border-color:rgba(0,242,254,0.4);color:var(--accent-cyan);';
            } else if (pred.cluster === 'SNIPER') {
                clusterBadgeStyle = 'background:rgba(239,68,68,0.15);border-color:rgba(239,68,68,0.4);color:#f87171;';
            }

            let injBadge = '';
            let injTextDesc = '';
            if (p.is_injured) {
                const isOrange = (p.infortunio_severity === 'orange');
                const colorHex = isOrange ? '#f59e0b' : '#ef4444';
                const classBadge = isOrange ? 'inj-cross-badge orange' : 'inj-cross-badge red';
                const statusTitle = isOrange ? 'PROSSIMO AL RIENTRO' : 'LUNGA DEGENZA';
                injBadge = `<span class="${classBadge}" title="${statusTitle}&#10;Motivo: ${p.infortunio_motivo || 'Indisponibile'}&#10;Rientro previsto: ${p.infortunio_rientro || 'TBD'}"><svg viewBox="0 0 24 24" width="12" height="12" fill="${colorHex}" style="vertical-align:middle;"><path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6V3z"/></svg></span>`;
                injTextDesc = `<span style="font-size:10px;font-weight:700;color:${colorHex};background:${isOrange ? 'rgba(245,158,11,0.15)' : 'rgba(239,68,68,0.15)'};border:1px solid ${isOrange ? 'rgba(245,158,11,0.35)' : 'rgba(239,68,68,0.35)'};padding:1px 5px;border-radius:4px;" title="${p.infortunio_motivo || ''}">🏥 ${p.infortunio_rientro || 'Stop'}</span>`;
            }

            const ratingVal = p.rating_2526 ? `<b style="color:#fbbf24;font-size:13px;">${p.rating_2526}</b>` : `<span style="color:var(--text-muted);">-</span>`;
            const xgVal = p.xg90_2526 > 0 ? `<b style="color:#f472b6;font-size:12.5px;">${p.xg90_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
            const xaVal = p.xa90_2526 > 0 ? `<b style="color:var(--accent-cyan);font-size:12.5px;">${p.xa90_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
            
            let gaVal = `<span style="color:var(--text-muted);font-size:11px;">0G / 0A</span>`;
            if (p.gol_2627 > 0 || p.assist_2627 > 0) {
                gaVal = `<span style="color:#4ade80;font-weight:800;font-size:12px;">${p.gol_2627}G / ${p.assist_2627}A</span>`;
            }

            let actionHtml = '';
            if (isBought) {
                actionHtml = `<span style="color:#4ade80;font-weight:800;font-size:11px;">✓ IN ROSA</span>`;
            } else if (isTaken) {
                actionHtml = `<span style="color:#ef4444;font-weight:700;font-size:10.5px;">⛔ PRESO</span>`;
            } else {
                actionHtml = `
                    <button class="btn-action" style="padding:4px 9px;font-size:11px;background:rgba(0,242,254,0.15);border-color:var(--accent-cyan);color:#fff;" onclick="event.stopPropagation(); buyPlayer(${p.id}); renderGemsTab();" title="Compra subito per la tua rosa">
                        + Compra (${p.prezzo_cons} CR)
                    </button>
                `;
            }

            rowsHtml += `
                <tr class="${pred.cluster === 'RATING_7' ? 'gem-row-gold' : ''}" onclick="openPlayerProfileModal(${p.id})">
                    <td style="text-align:center;">
                        ${renderGemsRoleBadge(p)}
                    </td>
                    <td>
                        <div style="font-weight:800;color:#fff;font-size:13px;display:flex;align-items:center;gap:5px;flex-wrap:wrap;">
                            ${p.name}
                            ${injBadge}
                            ${p.mantra ? `<span style="font-size:9.5px;color:var(--text-muted);background:rgba(255,255,255,0.06);padding:1px 4px;border-radius:3px;">${p.mantra}</span>` : ''}
                            ${injTextDesc}
                        </div>
                        <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">
                            ${p.team} &nbsp;•&nbsp; <span style="color:var(--text-muted);">${p.slot_fascia.split('(')[0]}</span>
                        </div>
                    </td>
                    <td>
                        <span style="border:1px solid;padding:2px 7px;border-radius:12px;font-size:10px;font-weight:800;display:inline-block;white-space:nowrap;${clusterBadgeStyle}">
                            ${pred.clusterLabel}
                        </span>
                    </td>
                    <td style="text-align:center;">
                        <span class="price-pill" style="font-size:11px;padding:2px 7px;font-weight:800;">${p.prezzo_cons} CR</span>
                    </td>
                    <td style="text-align:center;">
                        <span style="font-size:11.5px;font-weight:800;color:#4ade80;">${p.titolarita}%</span>
                    </td>
                    <td style="text-align:center;">
                        ${ratingVal}
                    </td>
                    <td style="text-align:center;">
                        ${xgVal}
                    </td>
                    <td style="text-align:center;">
                        ${xaVal}
                    </td>
                    <td style="text-align:center;">
                        ${gaVal}
                    </td>
                    <td class="gem-col-pred">
                        <div style="font-size:11px;color:var(--text-secondary);line-height:1.35;">
                            ${pred.predictionText}
                        </div>
                        <div style="font-size:10px;font-weight:800;color:#fbbf24;margin-top:2px;">
                            ⚡ ${pred.projectedBonus}
                        </div>
                    </td>
                    <td style="text-align:center;" onclick="event.stopPropagation();">
                        ${actionHtml}
                    </td>
                </tr>
            `;
        });

        mainContentHtml = `
            <div class="gems-table-container">
                <table class="gems-table">
                    <thead>
                        <tr>
                            <th style="width:36px;text-align:center;">R</th>
                            <th>Calciatore & Club</th>
                            <th>Cluster AI</th>
                            <th style="text-align:center;">Prezzo</th>
                            <th style="text-align:center;">Titolarità</th>
                            <th style="text-align:center;">Rating</th>
                            <th style="text-align:center;">xG/90</th>
                            <th style="text-align:center;">xA/90</th>
                            <th style="text-align:center;">Live 26/27</th>
                            <th>Analisi Predittiva & Proiezione</th>
                            <th style="text-align:center;width:115px;">Azione</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        `;
    } else {
        let cardsHtml = '';
        candidates.forEach((p, idx) => {
            const isBought = isPlayerBought(p.id);
            const isTaken = isPlayerTakenByOther(p.id);
            const pred = p._aiPrediction;

            let clusterBadgeStyle = 'background:rgba(139,92,246,0.15);border-color:rgba(139,92,246,0.4);color:#c084fc;';
            if (pred.cluster === 'RATING_7') {
                clusterBadgeStyle = 'background:rgba(251,191,36,0.15);border-color:rgba(251,191,36,0.4);color:#fbbf24;box-shadow:0 0 10px rgba(251,191,36,0.2);';
            } else if (pred.cluster === 'OOP') {
                clusterBadgeStyle = 'background:rgba(236,72,153,0.15);border-color:rgba(236,72,153,0.4);color:#f472b6;';
            } else if (pred.cluster === 'ASSIST_MACHINE') {
                clusterBadgeStyle = 'background:rgba(0,242,254,0.15);border-color:rgba(0,242,254,0.4);color:var(--accent-cyan);';
            } else if (pred.cluster === 'SNIPER') {
                clusterBadgeStyle = 'background:rgba(239,68,68,0.15);border-color:rgba(239,68,68,0.4);color:#f87171;';
            }

            let injBadge = '';
            let injCardBanner = '';
            if (p.is_injured) {
                const isOrange = (p.infortunio_severity === 'orange');
                const colorHex = isOrange ? '#f59e0b' : '#ef4444';
                const classBadge = isOrange ? 'inj-cross-badge orange' : 'inj-cross-badge red';
                const statusTitle = isOrange ? 'PROSSIMO AL RIENTRO' : 'LUNGA DEGENZA';
                injBadge = `<span class="${classBadge}" title="${statusTitle}&#10;Motivo: ${p.infortunio_motivo || 'Indisponibile'}&#10;Rientro previsto: ${p.infortunio_rientro || 'TBD'}"><svg viewBox="0 0 24 24" width="12" height="12" fill="${colorHex}" style="vertical-align:middle;"><path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6V3z"/></svg></span>`;
                injCardBanner = `
                    <div style="background:${isOrange ? 'rgba(245,158,11,0.12)' : 'rgba(239,68,68,0.12)'};border:1px solid ${isOrange ? 'rgba(245,158,11,0.3)' : 'rgba(239,68,68,0.3)'};color:${colorHex};font-size:11px;font-weight:700;padding:4px 8px;border-radius:6px;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
                        ${injBadge} <span>${p.infortunio_motivo || 'Infortunato'} • Rientro: <b>${p.infortunio_rientro || 'TBD'}</b></span>
                    </div>
                `;
            }

            const ratingVal = p.rating_2526 ? `<b style="color:#fbbf24;font-size:13.5px;">${p.rating_2526}</b>` : `<span style="color:var(--text-muted);">-</span>`;
            const xgVal = p.xg90_2526 > 0 ? `<b style="color:#f472b6;font-size:13px;">${p.xg90_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
            const xaVal = p.xa90_2526 > 0 ? `<b style="color:var(--accent-cyan);font-size:13px;">${p.xa90_2526}</b>` : `<span style="color:var(--text-muted);">0.0</span>`;
            
            let gaVal = `<span style="color:var(--text-muted);font-size:11px;">0G / 0A</span>`;
            if (p.gol_2627 > 0 || p.assist_2627 > 0) {
                gaVal = `<span style="color:#4ade80;font-weight:800;font-size:12px;">${p.gol_2627}G / ${p.assist_2627}A</span>`;
            }

            let actionHtml = '';
            if (isBought) {
                actionHtml = `<span style="color:#4ade80;font-weight:800;font-size:11.5px;display:flex;align-items:center;gap:4px;">✓ NELLA TUA ROSA</span>`;
            } else if (isTaken) {
                actionHtml = `<span style="color:#ef4444;font-weight:700;font-size:11px;">⛔ PRESO DA ALTRI</span>`;
            } else {
                actionHtml = `
                    <button class="btn-action" style="padding:5px 11px;font-size:11.5px;background:rgba(0,242,254,0.15);border-color:var(--accent-cyan);color:#fff;" onclick="event.stopPropagation(); buyPlayer(${p.id}); renderGemsTab();" title="Compra subito per la tua rosa">
                        + Compra (${p.prezzo_cons} CR)
                    </button>
                `;
            }

            cardsHtml += `
                <div class="gem-card ${pred.cluster === 'RATING_7' ? 'gem-card-gold' : ''}" onclick="openPlayerProfileModal(${p.id})">
                    <!-- Header Card: Nome, Squadra, Prezzo, Ruolo -->
                    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            ${renderGemsRoleBadge(p)}
                            <div>
                                <div style="font-size:15px;font-weight:800;color:#fff;display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                                    ${p.name}
                                    ${injBadge}
                                    ${p.mantra ? `<span style="font-size:10px;color:var(--text-muted);background:rgba(255,255,255,0.06);padding:1px 5px;border-radius:3px;">${p.mantra}</span>` : ''}
                                </div>
                                <div style="font-size:11.5px;color:var(--text-secondary);margin-top:1px;">
                                    ${p.team} &nbsp;•&nbsp; Titolarità: <b style="color:#4ade80;">${p.titolarita}%</b>
                                </div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div class="price-pill" style="font-size:12px;padding:3px 8px;font-weight:800;">${p.prezzo_cons} CR</div>
                            <div style="font-size:10px;color:var(--text-muted);margin-top:2px;">${p.slot_fascia.split('(')[0]}</div>
                        </div>
                    </div>

                    <!-- Cluster Badge & Eventuale Banner Infortunio -->
                    <div style="margin-bottom:10px;">
                        <span style="border:1px solid;padding:2px 8px;border-radius:20px;font-size:10.5px;font-weight:800;display:inline-block;${clusterBadgeStyle}">
                            ${pred.clusterLabel}
                        </span>
                    </div>

                    ${injCardBanner}

                    <!-- Metriche Chiave a 4 Riquadri -->
                    <div class="gem-metrics-grid">
                        <div class="gem-metric-box">
                            <span class="gem-metric-lbl">RATING MEDIO</span>
                            <span class="gem-metric-val">${ratingVal}</span>
                        </div>
                        <div class="gem-metric-box">
                            <span class="gem-metric-lbl">xG / 90 MIN</span>
                            <span class="gem-metric-val">${xgVal}</span>
                        </div>
                        <div class="gem-metric-box">
                            <span class="gem-metric-lbl">xA / 90 MIN</span>
                            <span class="gem-metric-val">${xaVal}</span>
                        </div>
                        <div class="gem-metric-box">
                            <span class="gem-metric-lbl">2026/27 LIVE</span>
                            <span class="gem-metric-val">${gaVal}</span>
                        </div>
                    </div>

                    <!-- Analisi Predittiva Testuale Sartoriale -->
                    <div class="gem-prediction-box">
                        <div style="font-size:10.5px;font-weight:800;color:var(--accent-cyan);margin-bottom:3px;display:flex;align-items:center;gap:4px;">
                            🧠 ANALISI PREDITTIVA ALGORITMO:
                        </div>
                        <p style="margin:0;font-size:11.5px;color:var(--text-secondary);line-height:1.45;">
                            ${pred.predictionText}
                        </p>
                        <div style="margin-top:6px;font-size:11px;font-weight:800;color:#fbbf24;border-top:1px dashed rgba(255,255,255,0.08);padding-top:5px;">
                            ⚡ ${pred.projectedBonus}
                        </div>
                    </div>

                    <!-- Footer Azioni -->
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-top:auto;padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">
                        <span style="font-size:10.5px;color:var(--text-muted);cursor:pointer;" onclick="event.stopPropagation(); openPlayerProfileModal(${p.id});">
                            🔍 Apri Scheda Radar ➜
                        </span>
                        <div>
                            ${actionHtml}
                        </div>
                    </div>
                </div>
            `;
        });

        mainContentHtml = `
            <div class="gems-cards-grid">
                ${cardsHtml}
            </div>
        `;
    }

    container.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:18px;">
            <!-- Header Banner Predittivo -->
            <div class="gems-hero-banner">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;">
                    <div style="max-width:720px;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                            <span style="font-size:26px;">🔮</span>
                            <h2 style="margin:0;font-size:22px;font-weight:900;color:#fff;letter-spacing:-0.4px;">
                                Algoritmo Predittivo: <span style="color:var(--accent-cyan);">Gemme Nascoste & Sleeper AI</span>
                            </h2>
                            <span style="background:rgba(251,191,36,0.15);border:1px solid rgba(251,191,36,0.4);color:#fbbf24;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:800;">
                                Serie A 2026/27
                            </span>
                        </div>
                        <p style="margin:0;font-size:13px;color:var(--text-secondary);line-height:1.5;">
                            Incrocio multidimensionale tra <b>Metriche Statistiche Avanzate</b> (xG, xA, tiri/90), <b>Posizione Tattica Reale (OOP)</b> e <b>Stile Offensivo della Squadra</b>. Calciatori insospettabili a basso-medio costo proiettati ad una stagione di bonus e voti superiori al 7.
                        </p>
                    </div>

                    <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px 16px;text-align:right;">
                        <div style="font-size:11px;color:var(--text-muted);font-weight:700;">GEMME IDENTIFICATE</div>
                        <div style="font-size:24px;font-weight:900;color:#fff;font-family:'Outfit',sans-serif;">${candidates.length} <span style="font-size:13px;color:var(--accent-cyan);">Profili</span></div>
                    </div>
                </div>

                <!-- Pannello Filtri Rapidi & Cluster -->
                <div class="gems-filters-bar">
                    <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                        <span style="font-size:11px;font-weight:800;color:var(--text-muted);margin-right:4px;">RUOLO:</span>
                        ${(isMantra ? [
                            { id: 'ALL', label: 'Tutti' },
                            { id: 'Por', label: '🧤 Por' },
                            { id: 'Dc', label: '🛡️ Dc' },
                            { id: 'DIF', label: '🛡️ Terzini (Dd/Ds)' },
                            { id: 'E', label: '⚡ Esterni (E)' },
                            { id: 'MED', label: '⚙️ Mediana (M/C)' },
                            { id: 'T', label: '🪄 Trequarti (T/W)' },
                            { id: 'Pc', label: '🎯 Punte (A/Pc)' }
                        ] : [
                            { id: 'ALL', label: 'Tutti' },
                            { id: 'P', label: '🧤 Portieri' },
                            { id: 'D', label: '🛡️ Difensori' },
                            { id: 'C', label: '⚙️ Centrocampisti' },
                            { id: 'A', label: '🎯 Attaccanti' }
                        ]).map(pill => `
                            <button class="gems-filter-pill ${rFilt === pill.id ? 'active' : ''}" onclick="setGemsFilter('role', '${pill.id}')">
                                ${pill.label}
                            </button>
                        `).join('')}
                    </div>

                    <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;border-left:1px solid rgba(255,255,255,0.08);padding-left:12px;">
                        <span style="font-size:11px;font-weight:800;color:var(--text-muted);margin-right:4px;">CLUSTER AI:</span>
                        <button class="gems-filter-pill ${cFilt === 'ALL' ? 'active' : ''}" onclick="setGemsFilter('cluster', 'ALL')">Tutti i Cluster</button>
                        <button class="gems-filter-pill ${cFilt === 'RATING_7' ? 'active' : ''}" onclick="setGemsFilter('cluster', 'RATING_7')">🌟 Media Voto ≥ 7.0</button>
                        <button class="gems-filter-pill ${cFilt === 'OOP' ? 'active' : ''}" onclick="setGemsFilter('cluster', 'OOP')">⚡ Jolly Fuori Ruolo</button>
                        <button class="gems-filter-pill ${cFilt === 'ASSIST_MACHINE' ? 'active' : ''}" onclick="setGemsFilter('cluster', 'ASSIST_MACHINE')">🎯 Macchine da Assist</button>
                        <button class="gems-filter-pill ${cFilt === 'SNIPER' ? 'active' : ''}" onclick="setGemsFilter('cluster', 'SNIPER')">🚀 Cecchini xG</button>
                    </div>

                    <div style="display:flex;align-items:center;gap:10px;margin-left:auto;flex-wrap:wrap;">
                        <!-- Selettore Vista Lista / Griglia -->
                        <div style="display:flex;align-items:center;background:rgba(0,0,0,0.45);padding:2px;border-radius:8px;border:1px solid rgba(255,255,255,0.12);">
                            <button class="gems-view-toggle ${vMode === 'LIST' ? 'active' : ''}" onclick="setGemsFilter('view', 'LIST')" title="Visualizza come Lista Tabellare">📋 Lista</button>
                            <button class="gems-view-toggle ${vMode === 'GRID' ? 'active' : ''}" onclick="setGemsFilter('view', 'GRID')" title="Visualizza come Schede">🃏 Schede</button>
                        </div>

                        <div style="display:flex;align-items:center;gap:6px;">
                            <label style="font-size:11px;font-weight:800;color:var(--text-muted);">ORDINA:</label>
                            <select class="tactical-select" style="width:160px;padding:4px 8px;font-size:11.5px;" onchange="setGemsFilter('sort', this.value)">
                                <option value="AI_SCORE" ${sFilt === 'AI_SCORE' ? 'selected' : ''}>🔮 Indice Predittivo AI</option>
                                <option value="PRICE_ASC" ${sFilt === 'PRICE_ASC' ? 'selected' : ''}>💰 Prezzo Crescente</option>
                                <option value="RATING_DESC" ${sFilt === 'RATING_DESC' ? 'selected' : ''}>⭐ Rating Statistico Decrescente</option>
                                <option value="BONUS_DESC" ${sFilt === 'BONUS_DESC' ? 'selected' : ''}>⚡ Somma xG + xA</option>
                            </select>
                        </div>
                        <input type="text" placeholder="🔍 Cerca nome o club..." value="${qFilt}" oninput="setGemsFilter('search', this.value)" style="background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.15);color:#fff;padding:5px 10px;border-radius:6px;font-size:12px;outline:none;width:170px;" />
                    </div>
                </div>
            </div>

            <!-- Contenuto Principale: Lista Tabellare o Griglia Schede -->
            ${mainContentHtml}
        </div>
    `;
}

function setGemsFilter(type, value) {
    if (type === 'role') window.gemsState.roleFilter = value;
    else if (type === 'cluster') window.gemsState.clusterFilter = value;
    else if (type === 'sort') window.gemsState.sortFilter = value;
    else if (type === 'search') window.gemsState.searchQuery = value;
    else if (type === 'view') window.gemsState.viewMode = value;
    renderGemsView();
}

// Alias: the dashboard HTML calls renderGemsTab(), state.js calls renderGemsView()
// Both are exposed so both naming conventions work
const renderGemsTab = renderGemsView;
window.renderGemsTab = renderGemsView;
window.renderGemsView = renderGemsView;
window.setGemsFilter = setGemsFilter;
